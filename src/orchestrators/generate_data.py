from src.orchestrators.apporaches.engine_direct import generating_data_loop
from src.orchestrators.apporaches.engine_fc import fc_generator

def generate_data(prompts: dict, ddl_schema: str, user_instructions: str, approach:str,temperature: float=0.7, max_tokens: int=65000, max_retries: int=3):
    if approach == "direct": 
        system_prompt = prompts['system_prompts']['main_prompt']
        starting_prompt = prompts['user_prompts']['main_prompt'].format(ddl_schema=ddl_schema,user_instructions=user_instructions)
        return generating_data_loop(prompts, system_prompt, starting_prompt, temperature, max_tokens, max_retries)
    elif approach == "function_calling":
        system_prompt = prompts['system_prompts']['main_prompt']
        user_prompt = prompts['user_prompts']['main_prompt'].format(ddl_schema=ddl_schema, user_instructions=user_instructions)
        return fc_generator(system_instruction=system_prompt, user_prompt=user_prompt,temperature=temperature, max_tokens=max_tokens)