from google import genai
from google.genai import types
import pandas as pd
from src.core.utilts import load_config, create_logger, load_env, get_cached
from typing import Dict
from src.llm_tools.upload_data import upload_data_tool
from src.database.database_handler import get_engine

prompts, config = get_cached()

DB_CONFIG, GCP_CONFIG = load_env()

logger = create_logger("Generating data")
client = genai.Client(vertexai=True, project=GCP_CONFIG.project_id)

def fc_generator(system_instruction:str, user_prompt:str,temperature: float = 0.7,max_tokens: int = 65000,) -> Dict[str, pd.DataFrame]:
    """
    Generates synthetic data using Gemini automatic function calling.

    Args:
        ddl_schema: The SQL DDL content to be interpreted.
        user_instructions: Custom prompt to guide generation.
        temperature: LLM temperature parameter.
        max_tokens: Max output tokens.

    Returns:
        A dictionary mapping table names to Pandas DataFrames.
    """

    logger.info("Starting data generation process...")


    
    model_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_tokens,
        tools=[upload_data_tool]
        )

    try:
        logger.info("Invoking model with function calling...")

        response = client.models.generate_content(
            model=config['llm']['model'],
            contents=[user_prompt],
            config=model_config
        )
        
        if response.text and "WARNING:" in response.text:
            warning_msg = response.text.strip()
            logger.warning(f"Model rejected the prompt: {warning_msg}")
            return {}, warning_msg

        logger.info("Model finished execution. Fetching fresh data from PostgreSQL...")

        collected_dataframes: Dict[str, pd.DataFrame] = {}

        engine = get_engine()
        
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        table_names = pd.read_sql(query, engine)['table_name'].tolist()
        
        for table in table_names:
            collected_dataframes[table] = pd.read_sql_table(table, con=engine)

        if collected_dataframes:
            logger.info(f"Data generation completed.")
        else:
            logger.error("Database is empty after generation. Model might have failed to use the tool.")

        return collected_dataframes, None


    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}")
        return {}, f"WARNING: Internal error occurred: {str(e)}"