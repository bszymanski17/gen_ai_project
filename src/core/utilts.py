import yaml
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv
from typing import Tuple, Dict
from src.schemas.schemas import DatabaseConfig, GCPConfig, LFConfig
from pydantic import ValidationError
import streamlit as st
from google import genai
from google.genai import types

def create_logger(name: str)  -> logging.Logger:
    """
    Initializes a standarized logger.
    
    Args:
        name: name of the logger.
    Returns:
        logging.Logger: A configured logger instance with a console handler.
    """
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    return logger

logger = create_logger("Utils")

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load applictaion settings from a YAML configuration file.

    Args:
        config_paths: Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: A dictionary containging the configuration parameters. Return an empty dict if loading fails.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"YAML config loaded successfuly from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Error: File not found at: {config_path}")
    except Exception as e:
        logger.error(f"Error during YAML confih loading: {str(e)}")


def load_env() -> Tuple[DatabaseConfig, GCPConfig, LFConfig]:
    """
    Loads and validates environment variables for DB and GCP.

    Returns:
        Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]: A tuple containing tthree dictionaries:
            - DB_CONFIG: Database connection settings (dbname, user, password, host, port).
            - GCP_CONFIG: Google Cloud settings (project_id).
            - LANGFUSE_CONFIG: Lanfuse settings.
    """

    logger.info("Loading environment variables...")
    load_dotenv()

    try:
        db_conf = DatabaseConfig(
            dbname=os.getenv("DB_NAME"),
            user= os.getenv("DB_USER"),
            password= os.getenv("DB_PASS"),
            host= os.getenv("DB_HOST"),
            port= os.getenv("DB_PORT")
        )

        gcp_conf = GCPConfig(
            project_id= os.getenv("GCP_PROJECT_ID")
        )

        langfuse_conf = LFConfig(
            langfuse_secret_key= os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_public_key= os.getenv("LANGFUSE_PUBLIC_KEY"),
            langfuse_base_url =os.getenv("LANGFUSE_BASE_URL")
        )
 
    except ValidationError as v:
        logger.error(f"Error during validation enviroment variables: {str(v)}")
        raise RuntimeError(f"Error during validation enviroment variables. {str(v)}")
    except Exception as e:
        logger.error(f"Error during loading enviroment variables: {str(e)}")
        raise RuntimeError("Error during loading enviroment variables.")
    
    return db_conf, gcp_conf, langfuse_conf


@st.cache_data
def get_cached():
    """
    Loads and caches configuration files.

    Returns:
        tuple: (prompts_dict, main_config_dict)
    """
    return load_config("prompts/prompts.yaml"), load_config()

@st.cache_resource
def init_instrumentation():
    from langfuse import get_client
    from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
    
    # Inicjalizacja klienta i włączenie śledzenia (wykona się TYLKO RAZ)
    get_client()
    GoogleGenAIInstrumentor().instrument()
    return True

