from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class TableData(BaseModel):
    """
    Represents generated data for a single table.

    Attributes:
        table_name: The name of the table
        table: A list of dictionares, where each dictionary represents a row with.
    """
    table_name: str = Field(description="Exact name of the table from DDL schema.")
    table: List[Dict[str, Any]] = Field(description="List of records. Each record is a dictionary mapping column names to generated values.")

class DataResponse(BaseModel):
    """
    Represent data for all parsed tabled (LLM output).

    Attributes:
        tables: A collection of TableData objects representing all generated tables.
    """
    tables: List[TableData] = Field(description="List of tables containing the generated synthetic rows.")
    warning: Optional[str] = None


class DatabaseConfig(BaseModel):
    """
    Configuration model for database connection .
    """
    dbname: str
    user: str
    password: str
    host: str
    port: int

class GCPConfig(BaseModel):
    """
    Configuration model for the Google Cloud Platform (GCP) environment.
    """
    project_id: str

