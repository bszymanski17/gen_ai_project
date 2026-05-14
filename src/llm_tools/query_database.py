from src.database.database_handler import get_engine
import pandas as pd
from sqlalchemy import text
from src.core.utilts import create_logger

logger = create_logger("Query database")

def query_database(query: str) -> str:
    """
    Executes a raw SQL query against the PostgreSQL database. 
    
    - For SELECT queries, it returns a formatted string of the first 10 rows to provide data context.
    - For data modification queries, it returns the number of affected rows to confirm execution.
    - If a SQL error occurs, it returns the specific error message so the query can be analyzed, corrected, and retried.

    Args:
        query: The executable PostgreSQL query string.

    Returns:
        str: A formatted string containing query results, success confirmation, or error details.
    """
    engine = get_engine()

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query))
            if result.returns_rows:
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                logger.info("Query executed successfully!")
                if df.empty:
                    return "SUCCESS: Query executed, but returned not results."
                else:
                    return f"SUCCESS: Query returned following data (firs 10 rows): {df.head(10).to_string(index=False)}."
            else:
                return f"SUCCESS: Operation completed. Affected rows: {result.rowcount}."

    except Exception as e:
        logger.info(f"Query executed failed! Error: {str(e)}")
        return f"SQL Execution failed. Error: {str(e)}"