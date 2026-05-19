from google import genai
from google.genai import types
from src.core.utilts import load_env
from src.core.utilts import create_logger, load_config
from src.llm_tools.talk_to_data_tools import execute_query, create_plot
import plotly.express as px


config = load_config()
DB_config, GCP_config = load_env()
client = genai.Client(vertexai=True, project=GCP_config.project_id)

logger = create_logger("Talk to your data")


def talk_to_data(system_instructions: str, user_instructions:str, temperature: float=0.7, max_tokens=65000)->dict:
    """
    Orchestrates the SQL query aporach to execute database operations based on user instructions.

    Args:
        ddl_schema: The structural blueprint (DDL) of the database.
        system_instructions: The persona and operational rules for the model.
        user_instructions: The specific task requested by the user.
        temperature: Creativity/randomness parameter for the LLM. 
        max_tokens: The maximum token limit for the model's output.

    Returns:
        
    """

    llm_config = types.GenerateContentConfig(
        system_instruction=system_instructions,
        temperature=temperature,
        max_output_tokens=max_tokens,
        tools=[execute_query, create_plot],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
    
    artifacts = {
        "sql_query": None,
        "df": None,
        "plot": None,
        "warning": None
    }

    try:
        logger.info("Invoking model...")
        response = client.models.generate_content(
            model=config['llm']['model'],
            config=llm_config,
            contents=[user_instructions]
        )

        plot_code_str = None

        if response.function_calls:
            for tool_call in response.function_calls:
                tool_name = tool_call.name
                tool_args= tool_call.args

                if tool_name == "execute_query":
                    query = tool_args.get("query", "")
                    artifacts['sql_query'] = query
                    _, artifacts['df'] = execute_query(query)
                elif tool_name == "create_plot":
                    plot_code_str = tool_args.get("python_code", "")

        elif response.text:
            if "WARNING:" in response.text:
                artifacts['warning'] = response.text.strip()

        if artifacts["df"] is not None and plot_code_str:
            try:
                local_context = {"df": artifacts["df"], "px": px, "fig": None}
                exec(plot_code_str, {}, local_context)
                artifacts['plot'] = local_context.get("fig")
            except Exception as plt_err:
                logger.error(f"Error during plot execution: {str(plt_err)}")
                artifacts["warning"] = f"WARNING: Failed to generate chart: {str(plt_err)}"


        logger.info(f"Analyzing proccess completed.")
        return artifacts

    except Exception as e:
        logger.error(f"Error during llm calling: {str(e)}")
        artifacts["warning"] = f"WARNING: Error: {str(e)}"
        return artifacts
    