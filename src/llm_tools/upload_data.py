from src.schemas.schemas import DataResponse
import pandas as pd
from src.database.database_handler import upload_to_postgres
from pydantic import ValidationError

    
def upload_data_tool(database_data_json: str) -> str:
    """
    Upload generated rows for all tables to PostgreSQL in a single transaction.
    Call this ONCE after generating data for the entire database.
    If an error is returned, fix the data and call again.

    Args:
        database_data_json: JSON object matching the DataResponse schema. 
                            Example: '{"tables": [{"table_name": "Authors", "table": [{"id": 1, "name": "John"}]}]}'
    """

    try:
        validated_data = DataResponse.model_validate_json(database_data_json)
        
        dataframes = {
            table_data.table_name: pd.DataFrame(table_data.table) 
            for table_data in validated_data.tables
        }
        
        success, error_msg = upload_to_postgres(dataframes)
        
        if success:
            return "SUCCESS: All tables uploaded successfully."
        else:
            return f"ERROR: {error_msg}. Fix the data and try again."
            
    except ValidationError as ve:
        return f"VALIDATION ERROR: Incorrect JSON structure. Details: {ve.json()}. Fix the data structure to match the schema and try again."
    except Exception as e:
        return f"ERROR: {str(e)}"
