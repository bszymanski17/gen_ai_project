from google import genai
from google.genai import types
from src.core.load_env import load_env
from src.core.utilts import create_logger, load_config
from src.llm_tools.query_database import query_database
from src.database.database_handler import get_engine
import pandas as pd

config = load_config()
DB_config, GCP_config = load_env()
client = genai.Client(vertexai=True, project=GCP_config.project_id)
prompts = load_config("prompts/prompts.yaml")

logger = create_logger("Query database")


def query_engine(ddl_schema: str, system_instructions: str, user_instructions:str, temperature: float=0.7, max_tokens=65000) -> bool:
    """
    Orchestrates the SQL query aporach to execute database operations based on user instructions.

    Args:
        ddl_schema: The structural blueprint (DDL) of the database.
        system_instructions: The persona and operational rules for the model.
        user_instructions: The specific task requested by the user.
        temperature: Creativity/randomness parameter for the LLM. 
        max_tokens: The maximum token limit for the model's output.

    Returns:
        bool: True if the model successfully completed the execution flow, False if an exception occurred.
    """

    llm_config = types.GenerateContentConfig(
        system_instruction=system_instructions,
        temperature=temperature,
        max_output_tokens=max_tokens,
        tools=[query_database]
    )
    try:
        logger.info("Invoking model...")
        response = client.models.generate_content(
            model=config['llm']['model'],
            config=llm_config,
            contents=[user_instructions.format(ddl_schema=ddl_schema, user_instructions=user_instructions)]
        )
        logger.info(f"Data edition completed.")
        return True
    except Exception as e:
        logger.error(f"Error during llm calling: {str(e)}")
        return False
    



def update_tables(generated_data):
    engine = get_engine()
    updated_tables = {}
    
    for table_name in generated_data.keys():
        updated_tables[table_name] = pd.read_sql_table(table_name.lower(), con=engine)
    return updated_tables