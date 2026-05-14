from src.orchestrators.function_calling.engine_fc import fc_generator

def edit_data_fc(data: str, prompts: dict, ddl_schema: str, user_instructions:str, temperature: float=0.7, max_tokens: int=65000):
    """
    Function for editing existing data using the Function Calling approach.
    This function acts as a wrapper that extracts the necessary templates,

    Args:
        data: 
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
    user_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
    return fc_generator(system_instruction=system_prompt, user_prompt=user_prompt, temperature=temperature, max_tokens=max_tokens)
