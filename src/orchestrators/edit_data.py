from src.orchestrators.apporaches.engine_direct import generating_data_loop
from src.orchestrators.apporaches.engine_fc import fc_generator
from src.orchestrators.apporaches.engine_query import query_engine, update_tables

def edit_data(prompts: dict, ddl_schema: str, user_instructions: str, approach:str, data: str,temperature: float=0.7, max_tokens: int=65000, max_retries: int=3):
    """
    Routes the data modification request to the specified execution engine. Formats the prompts based on the chosen approach ('direct', 'function_calling', 
    or 'query') and triggers the appropriate editing logic.

    Args:
        prompts: Dictionary containing system and user prompt templates.
        ddl_schema: The structural blueprint (DDL) of the database.
        user_instructions: The specific data editing task requested by the user.
        approach: The execution engine to use ('direct', 'function_calling', or 'query').
        data: The current state of the database data (formatted as a string/JSON).
        temperature: Creativity/randomness parameter for the LLM.
        max_tokens: The maximum token limit for the model's output.
        max_retries: Maximum number of validation retry attempts (used in the 'direct' approach).

    Returns:
        tuple: (updated_tables_dict or None, warning_message or None)
    """
    
    if approach == "direct": 
        system_prompt = prompts['system_prompts']['edit_main_prompt_fc_direct']
        starting_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
        return generating_data_loop(prompts, system_prompt, starting_prompt, temperature, max_tokens, max_retries)
    
    elif approach == "function_calling":
        system_prompt = prompts['system_prompts']['edit_main_prompt_fc_direct']
        user_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
        return fc_generator(system_instruction=system_prompt, user_prompt=user_prompt, temperature=temperature, max_tokens=max_tokens)
    
    elif approach == "query":
        system_prompt = prompts['system_prompts']['edit_main_prompt_query']
        user_prompt = prompts['user_prompts']['edit_main_prompt_query'].format(ddl_schema=ddl_schema, user_instructions=user_instructions)
        success, warning_msg = query_engine(system_instructions=system_prompt, user_instructions=user_prompt, temperature=temperature, max_tokens=max_tokens)
        
        if not success:
            return None, warning_msg
        else:
            updated_data = update_tables(data)
            return updated_data, None
            
    return None, "WARNING: Unknown approach type."