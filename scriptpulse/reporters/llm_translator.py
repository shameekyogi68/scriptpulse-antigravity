import os
import json
import logging

_log = logging.getLogger(__name__)

def generate_ai_summary(script_data, model="gemini-2.5-flash", api_key=None):
    """
    Takes pure ScriptPulse JSON data and translates it into plain English.
    Requires GEMINI_API_KEY environment variable or explicitly passed api_key.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None, "Missing GEMINI_API_KEY environment variable."
        
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=key)
        
        # 1. Package ONLY the exact data we want explained (No raw script text)
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "provocations": script_data.get("writer_intelligence", {}).get("creative_provocations", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
        }
        
        # 2. Strict System Guardrails
        system_prompt = (
            "You are a friendly, straightforward script mentor. Your job is to explain "
            "the 'feeling' of a script's structure using very simple, non-technical English.\n"
            "CRITICAL RULES:\n"
            "1. DO NOT use technical labels like 'Too Complex', 'Attentional Demand', or 'Narrative Entropy'.\n"
            "2. DO NOT reproduce the JSON keys. Explain what they MEAN in plain words.\n"
            "3. Use short, punchy sentences. Be direct and to the point.\n"
            "4. Speak like you are talking to a friend who doesn't know anything about data or math.\n"
            "5. ENSURE the message is complete. Do not stop mid-sentence or mid-thought.\n"
            "6. If the data shows complexity issues, say something like 'The story gets a bit crowded here' or 'There's a lot happening at once'."
        )
        
        # 3. Call the model
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        response = model_instance.generate_content(json.dumps(data_payload))
        
        return response.text, None
        
    except Exception as e:
        # THE FAIL-SAFE: Return None if anything goes wrong, 
        # allowing the app to fall back to the hardcoded summary entirely invisibly to the user.
        error_msg = str(e)
        _log.error(f"LLM Generation failed: {error_msg}")
        return None, error_msg
