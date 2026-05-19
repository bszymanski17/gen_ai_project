from src.core.utilts import load_env, create_logger, get_cached
from google import genai
from google.genai import types
from src.schemas.schemas import DataResponse
import pandas as pd
from src.database.database_handler import upload_to_postgres
from pydantic import ValidationError
from typing import Dict
from langfuse import observe

prompts, config = get_cached()
DB_CONF, GCP_CONF, _ = load_env()

logger = create_logger("Data generator")

client = genai.Client(vertexai=True, project=GCP_CONF.project_id)

@observe()
def generating_data_loop(prompts:dict, system_instructions: str, starting_prompt: str, temperature: float, max_tokens: int, max_retries: int = 3) -> Dict[str, pd.DataFrame]:
    """
    Data generation process with an integrated error-correction retry loop.

    Args:
        prompts: A dictionary containing prompt templates, specifically for formatting error messages.
        system_instructions: The core behavioral instructions for the LLM.
        starting_prompt: The initial prompt containing the DDL schema and user instructions.
        temperature: Controls the randomness of the LLM output.
        max_tokens: Maximum number of tokens the LLM is allowed to generate.
        max_retries: Maximum number of attempts to generate and upload valid data.

    Returns:
        A dictionary where keys are table names and values are the generated Pandas DataFrames.
        Returns an empty dictionary if max_retries are reached without success.
    """
    logger.info("Starting data generation process...")

    config_llm = types.GenerateContentConfig(
        system_instruction=system_instructions,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
        response_schema=DataResponse
    )

    current_prompt = starting_prompt

    logger.debug(f"Temperature={temperature}, max tokens={max_tokens}, model=\"{config['llm']['model']}\", user_prompt={starting_prompt}")

    for iter in range(max_retries):
        try:
            logger.info("Invoking model...")
            response = client.models.generate_content(
                model = config['llm']['model'],
                contents=[current_prompt],
                config=config_llm
            )

            logger.info("Respone recived. Starting validation...")
            valid_data = DataResponse.model_validate_json(response.text)

            if valid_data.warning:
                logger.warning(f"Guardrail triggered by model: {valid_data.warning}")
                return {}, valid_data.warning

            dataframes = {tab.table_name: pd.DataFrame(tab.table) for tab in valid_data.tables}
            upload_success, error_msg = upload_to_postgres(dataframes)
            if upload_success:
                logger.info("Data generated successfully.")
                return dataframes, None
            else:
                raise RuntimeError(error_msg)
        except RuntimeError as r:
            logger.warning(f"Error on iter {iter+1} during uploading to PostgreSQL: {str(r)}")
            current_prompt += prompts['error_prompts']['runtime_error_prompt'].format(r=str(r))
        except ValidationError as v:
            logger.warning(f"Validation error on iter {iter+1}: {str(v)}. Feeding back to LLM...")
            current_prompt += prompts['error_prompts']['validation_error_prompt'].format(v=str(v))
        except Exception as e:
            logger.error(f"Error druing data generation: {str(e)}")
            continue


    logger.error("Max retries reached. Returning empty data.")
    return {}
