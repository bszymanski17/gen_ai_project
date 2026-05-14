def get_user_prompt(prompts:dict , ddl_schema: str, user_instructions: str) -> str:
    """
    Formats the base prompt with the provided DDL schema and custom instructions.

    Args:
        prompts: A dictionary containing prompt templates (typically loaded from a YAML config).
        ddl_schema: The SQL DDL content to be injected into the prompt.
        user_instructions: Custom instructions from the user to guide the data generation.
        
    Returns:
        The final, formatted prompt string ready to be sent to the LLM.
        """
    user_prompt = prompts['user_prompts']['main_prompt']
    return user_prompt.format(ddl_schema=ddl_schema,user_instructions=user_instructions)

