import pandas as pd
from typing import Dict

_collected_dataframes: Dict[str, pd.DataFrame] = {}

def reset_collected_dataframes() -> None:
    """
    Resets the globally stored dataframes to an empty state.
    
    This function should be called before starting a new data generation 
    process to ensure no leftover data from previous runs is retained.
    """
    global _collected_dataframes
    _collected_dataframes = {}

def get_collected_dataframes() -> Dict[str, pd.DataFrame]:
    """
    Retrieves the currently stored generated dataframes.
    
    Returns:
        A dictionary mapping table names to their corresponding Pandas DataFrames.
    """
    return _collected_dataframes

def set_collected_dataframes(dfs: Dict[str, pd.DataFrame]) -> None:
    """
    Updates the globally stored dataframes with new data.
    
    Args:
        dfs: A dictionary mapping table names to Pandas DataFrames to be stored 
             in the global state.
    """
    global _collected_dataframes
    _collected_dataframes = dfs