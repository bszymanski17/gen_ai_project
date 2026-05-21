import google.genai as genai
from langfuse import observe
from src.core.utilts import load_env, get_cached

_, gcp_project, _ = load_env()
prompts, config = get_cached()
client = genai.Client(vertexai=True, project=gcp_project.project_id)

@observe()
def security_check(user_input: str, action_type: str) -> dict:
    """
    Checks the query and logs the result directly to Langfuse.
    """
    if not user_input:
        return {"status": "empty_input"}

    judge_prompt = prompts['jailbreak_prompts']['main_prompt'].format(user_input=user_input)
    try:
        response = client.models.generate_content(
            model=config['llm']['jailbreak_model'],
            contents=judge_prompt
        )
        result = response.text.strip()
        
        return {
            "action_checked": action_type,
            "is_jailbreak_attempt": result == "1",
            "security_verdict": "FLAGGED" if result == "1" else "SAFE"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}