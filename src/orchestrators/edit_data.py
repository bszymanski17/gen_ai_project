from src.orchestrators.apporaches.engine_direct import generating_data_loop
from src.orchestrators.apporaches.engine_fc import fc_generator
from src.orchestrators.apporaches.engine_query import query_engine, update_tables

def edit_data(prompts: dict, ddl_schema: str, user_instructions: str, approach:str, data: str,temperature: float=0.7, max_tokens: int=65000, max_retries: int=3):
    if approach == "direct": 
        system_prompt = prompts['system_prompts']['edit_main_prompt']
        starting_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
        return generating_data_loop(prompts, system_prompt, starting_prompt, temperature, max_tokens, max_retries)
    elif approach == "function_calling":
        system_prompt = prompts['system_prompts']['edit_main_prompt']
        user_prompt = prompts['user_prompts']['edit_main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions,data=data)
        return fc_generator(system_instruction=system_prompt, user_prompt=user_prompt, temperature=temperature, max_tokens=max_tokens)
    elif approach == "query":
        system_prompt = prompts['system_prompts']['edit_query_main_promt']
        user_prompt = prompts['user_prompts']['edit_query_user_prompt'].format(ddl_schema=ddl_schema, user_instructions=user_instructions)
        query_engine(ddl_schema,system_instructions=system_prompt, user_instructions=user_prompt,temperature=temperature, max_tokens=max_tokens)
        success, warning_msg = query_engine(ddl_schema, system_instructions=system_prompt, user_instructions=user_prompt, temperature=temperature, max_tokens=max_tokens)
        
        if not success:
            return None, warning_msg
        else:
            updated_data = update_tables(data)
            return updated_data, None
            
    return None, "WARNING: Unknown approach type."