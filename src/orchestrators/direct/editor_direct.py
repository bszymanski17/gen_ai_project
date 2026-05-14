from src.orchestrators.direct.engine_direct import generating_data_loop

def edit_data(data: str, prompts: dict, ddl_schema: str, user_instructions: str, temperature: float=0.7, max_tokens: int=65000, max_retries: int=3):
    """
    Facade function for editing existing data using the Direct retry-loop approach.
    This function acts as a wrapper that extracts the necessary templates,

    Args:
        data: The current database content in JSON format that needs to be modified.
        prompts: A dictionary containing 'system_prompts' and 'user_prompts' templates.
        ddl_schema: The SQL DDL string defining the target database structure.
        user_instructions: Custom requirements or context for the data to be generated.
        temperature: Controls randomness in LLM responses. 
        max_tokens: The maximum token limit for the model's output. 

    Returns:
        Dict[str, pd.DataFrame]: A dictionary mapping table names to their generated Pandas DataFrames, 
                                 retrieved from the global state after tool execution.
    """
    system_prompt = prompts['system_prompts']['edit_main_prompt']
    starting_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
    return generating_data_loop(prompts, system_prompt, starting_prompt, temperature, max_tokens, max_retries)
