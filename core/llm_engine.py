import os
import google.generativeai as genai

def setup_llm():
    """Configures the Gemini API key from the environment."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    return api_key

def get_best_model():
    """Identifies and returns the best available Gemini model based on preferences."""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferences = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for p in preferences:
            if p in available_models:
                return genai.GenerativeModel(p), p
        return genai.GenerativeModel(available_models[0]), available_models[0]
    except Exception as e:
        return None, f"Error Connecting: {str(e)}"

def generate_audit_report(model, client_type: str, review_mode: str, source_text: str, chunk_text: str, current_part: int, total_parts: int) -> str:
    """Generates a comparison deviation report for a specific chunk of text."""
    
    # Prioritizing substantive legal changes over formatting/typos
    prompt_task = (
        "STRICT SUBSTANTIVE COMPARISON. Ignore all whitespace, punctuation, "
        "typos, or formatting changes. Only flag changes to legal meaning."
        if "Literal" in review_mode else 
        "CONCEPTUAL PLAYBOOK COMPLIANCE. Flag deviations from mandatory standards."
    )
    
    prompt = f"""
    You are a senior attorney's high-precision comparison tool. 
    Representing: {client_type}
    Task: {prompt_task}

    [SOURCE OF TRUTH / PLAYBOOK]
    {source_text}

    [INCOMING DRAFT FOR REVIEW - PART {current_part} OF {total_parts}]
    {chunk_text}

    CRITICAL INSTRUCTIONS:
    1. IGNORE ALL TYPOS AND SPACING: Do not flag 't he' vs 'the' or missing spaces.
    2. IGNORE PUNCTUATION: Do not flag commas or periods unless they change liability.
    3. FOCUS: Only list changes that alter the legal rights or obligations of the {client_type}.
    4. FORMAT: Create a Markdown table with 3 columns:
       - Clause Reference
       - Our Standard
       - Their Substantive Change
    5. Do NOT provide summaries. If no substantive changes exist, return "No substantive deviations found."
    """

    # Generation configuration with a deterministic temperature for code evaluation
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 8192,  # Prevent high cutoff bounds
            "temperature": 0.1
        }
    )
    
    return response.text
