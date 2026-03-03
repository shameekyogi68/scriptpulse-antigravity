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
            "1. Synthesize ALL data fields (pacing, priorities, and provocations) into a holistic assessment.\n"
            "2. DO NOT waste characters on introductions like 'Alright, let's dive in'. Start with the analysis immediately.\n"
            "3. Speak directly to the writer with a supportive but honest and expert voice.\n"
            "4. Focus on 'What this pattern means for the reader's experience'.\n"
            "5. KEEP IT COMPACT: 2-3 dense paragraphs. Do NOT cut off mid-sentence."
        )
        
        # 3. Call the model
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
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
