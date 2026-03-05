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
        
        # 2. Strict System Guardrails for a Knowledgeable Consultant
        system_prompt = (
            "You are an expert Hollywood script consultant. Your job is to analyze the structural data "
            "provided by ScriptPulse and translate it into a comprehensive, actionable, and insightful "
            "report for the screenwriter.\n\n"
            "CRITICAL RULES:\n"
            "1. Be thorough and detailed. Explain the 'why' behind the data, not just the 'what'. Provide depth.\n"
            "2. Offer actionable advice: suggest specific narrative techniques to fix identified pacing or structural issues.\n"
            "3. DO NOT just list out the data. Synthesize it into a cohesive narrative evaluation of the script.\n"
            "4. DO NOT cut off your thoughts. Ensure your final response is completely finished and well-rounded.\n"
            "5. Speak professionally and knowledgeably, like an experienced story editor giving notes to a writer.\n"
            "6. Translate technical terms (like 'Attentional Demand' or 'Narrative Entropy') into their storytelling equivalents (e.g., 'Cognitive load on the reader', 'Overwhelming complexity').\n"
            "7. Ensure your output is structured with clear headings or paragraphs for readability."
        )
        
        # 3. Call the model
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=8192,
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
