from sqlalchemy import create_engine, text
import pandas as pd
from typing import Dict
from src.core.utilts import load_env
from src.core.utilts import create_logger
import re

logger = create_logger("Database handler")
DB_CONFIG, GCP_CONFIG, _ = load_env()

def preprocess_ddl(ddl_schema: str) -> str:
    return re.sub(r'(?i)(REFERENCES\s+\w+\s*\([^)]+\))(?!\s+DEFERRABLE)', r'\1 DEFERRABLE INITIALLY IMMEDIATE', ddl_schema)

def get_engine():
    """
    Create a SQLAlchemy engine for PostgreSQL connectivity.

    Returns:
        sqlalchemy.engine.Engine: An initialized engine ready for database operations.
    """
    uri = f"postgresql+psycopg2://{DB_CONFIG.user}:{DB_CONFIG.password}@{DB_CONFIG.host}:{DB_CONFIG.port}/{DB_CONFIG.dbname}"
    logger.debug(f"Connecting to database: {DB_CONFIG.dbname} at {DB_CONFIG.host}.")
    return create_engine(uri)

def truncate_all_tables() -> None:
    """
    Truncate all tables in public schema before data generation.
    """
    try:
        engine = get_engine()
        with engine.begin() as conn:
            result = conn.execute(text("""SELECT tablename FROM pg_tables WHERE schemaname = 'public'"""))
            tables = [row[0] for row in result]
            for table in tables:
                logger.info(f"Truncating table {table}")
                conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
    except Exception as e:
        logger.error(f"Error truncating tables: {str(e)}")

def init_tables(ddl_schema: str) -> bool:
    """
    Reset the database schema and appiles the DDML structure.

    Args:
        ddl_schema: A string containging the DDL schema to set up tables, columns and data types.

    Returns:
        bool: True if the schema was successfully intialized, False otherwise.
    """
    try:
        logger.info("Initializing database tables...")
        engine = get_engine()
        with engine.connect() as conn:
            logger.warning("Dropping and recreating public schema...")
            conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
            logger.info("Executing DDL schema...")
            conn.execute(text(ddl_schema))
            conn.commit()

        logger.info("Database schema initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Error during initializing tables: {str(e)}")
        return False

def upload_to_postgres(dataframes: Dict[str, pd.DataFrame]) -> bool:
    """
    Upload the generated data into PostgreSQL tables.

    Args:
        dataframes: A dictionary where keys are table names and values are pandas DataFrames.

    Returns:
        bool: True if all data was successfully uploaded, False if eny error occurred.
    """
    try:
        logger.info("Starting data upload to PostgreSQL...")
        engine = get_engine()

        with engine.begin() as conn:
            for table_name in dataframes.keys():
                logger.info(f"Clening table {table_name} before update.")
                conn.execute(text(f'TRUNCATE TABLE "{table_name.lower()}" RESTART IDENTITY CASCADE'))

            
            conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            for table_name, table in dataframes.items():
                logger.info(f"Uploading {len(table)} rows to table: {table_name}.")
                table.to_sql(name=table_name.lower(), con=conn, if_exists='append', index=False)

        logger.info("Data uploaded successfully.")
        return True, None

    except Exception as e:
        return False, str(e)