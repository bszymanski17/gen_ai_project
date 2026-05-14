from google import genai
from google.genai import types
import pandas as pd
from src.core.load_env import load_env
from src.core.utilts import load_config, create_logger
from typing import Dict
from src.llm_tools.upload_data import upload_all_and_validate
from src.core.state import get_collected_dataframes, reset_collected_dataframes
from src.core.get_user_prompt import get_user_prompt


config = load_config()
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

    reset_collected_dataframes()

    
    model_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_tokens,
        tools=[upload_all_and_validate]
        )

    try:
        logger.info("Invoking model with function calling...")

        response = client.models.generate_content(
            model=config['llm']['model'],
            contents=[user_prompt],
            config=model_config
        )

        collected = get_collected_dataframes()

        if collected:
            logger.info(f"Data generation completed. Tables: {list(collected.keys())}")
        else:
            logger.error("No function calls found in model response.")

        return collected

    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}")
        return {}