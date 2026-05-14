import os
from dotenv import load_dotenv
from src.core.utilts import create_logger
from typing import Tuple
from src.schemas.schemas import DatabaseConfig, GCPConfig
from pydantic import ValidationError

logger = create_logger("Config loader")

def load_env() -> Tuple[DatabaseConfig, GCPConfig]:
    """
    Loads and validates environment variables for DB and GCP.

    Returns:
        Tuple[Dict[str, str], Dict[str, str]]: A tuple containing two dictionaries:
            - DB_CONFIG: Database connection settings (dbname, user, password, host, port).
            - GCP_CONFIG: Google Cloud settings (project_id).
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
 
    except ValidationError as v:
        logger.error(f"Error during validation enviroment variables: {str(v)}")
        raise RuntimeError(f"Error during validation enviroment variables. {str(v)}")
    except Exception as e:
        logger.error(f"Error during loading enviroment variables: {str(e)}")
        raise RuntimeError("Error during loading enviroment variables.")
    
    return db_conf, gcp_conf
