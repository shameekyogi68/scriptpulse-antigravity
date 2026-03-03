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
            "You are a master script consultant and clinical narrative analyst. Your job is to translate "
            "raw structural metrics into a cohesive, deeply insightful narrative for a screenwriter.\n"
            "INSTRUCTIONS:\n"
            "1. Synthesize all data fields into a holistic assessment of the script's 'heartbeat' and health.\n"
            "2. DO NOT just say 'let's talk' or provide an intro. Provide the full analysis immediately.\n"
            "3. Speak directly to the writer as a supportive but honest peer/collaborator.\n"
            "4. Explain WHAT the patterns mean for the reader's emotional journey.\n"
            "5. Keep it concise (2 paragraphs max) but dense with value. No bullet points."
        )
        
        # 3. Call the model
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=400,
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
