from src.database.database_handler import get_engine
import pandas as pd
from sqlalchemy import text
from src.core.utilts import create_logger
from typing import Optional, Tuple

logger = create_logger("Execute query")

def execute_query(query: str):
    """
    Executes a SELECT SQL query on the PostgreSQL database and returns the results.
    Model should use this FIRST to get data before drawing any charts.

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
                    return "SUCCESS: Query executed, but returned not results.", df
                else:
                    return f"SUCCESS: Query returned following data (firs 10 rows): {df.head(10).to_string(index=False)}.", df
            else:
                return f"SUCCESS: Operation completed. Affected rows: {result.rowcount}.", None

    except Exception as e:
        logger.info(f"Query executed failed! Error: {str(e)}")
        return f"SQL Execution failed. Error: {str(e)}", None
    


def create_plot(python_code: str):
    """
    Generates Python code using plotly. Express to create a chart based on the database results.
    The code MUST assume that the data is already loaded into a pandas DataFrame named 'df'.

    Args:
        python_code: The executable Python code string using plotly.express and st.plotly_chart.
    """
    return python_code