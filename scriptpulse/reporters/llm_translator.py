import os
import json
import logging

_log = logging.getLogger(__name__)

def generate_ai_summary(script_data, model="gemini-1.5-flash", api_key=None):
    """
    Takes pure ScriptPulse JSON data and translates it into plain English.
    Requires GEMINI_API_KEY environment variable or explicitly passed api_key.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
        
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=key)
        
        # 1. Package ONLY the exact data we want explained (No raw script text)
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
        }
        
        # 2. Strict System Guardrails
        system_prompt = (
            "You are a clinical narrative analyst. Your job is to translate "
            "structural metrics into plain language for a screenwriter.\n"
            "RULES:\n"
            "1. Do NOT invent narrative causes.\n"
            "2. Do NOT judge the quality of the script.\n"
            "3. Use strictly the data provided in the JSON.\n"
            "4. Keep it concise, professional, and directly actionable.\n"
            "5. Speak directly to the writer in simple, supportive language. Do not use complex math jargon."
        )
        
        # 3. Call the model
        response = client.models.generate_content(
            model=model,
            contents=json.dumps(data_payload),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                max_output_tokens=400,
            )
        )
        
        return response.text
        
    except Exception as e:
        # THE FAIL-SAFE: Return None if anything goes wrong, 
        # allowing the app to fall back to the hardcoded summary entirely invisibly to the user.
        _log.error(f"LLM Generation failed: {e}")
        return None
