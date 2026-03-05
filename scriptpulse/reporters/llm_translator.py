import os
import json
import logging
from openai import OpenAI

_log = logging.getLogger(__name__)

def generate_ai_summary(script_data, api_key=None, model="moonshotai/Kimi-K2-Instruct-0905"):
    """
    Takes pure ScriptPulse JSON data and translates it into professional coverage.
    Uses Hugging Face's OpenAI-compatible router for high-quality LLM notes.
    """
    # Accept either name for the token
    key = api_key or os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
    
    if not key:
        return None, "Missing HUGGINGFACE_API_KEY / HF_TOKEN. Please provide your Hugging Face API key."
        
    try:
        # 1. Package ONLY the exact data we want explained (No raw script text)
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "provocations": script_data.get("writer_intelligence", {}).get("creative_provocations", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
        }
        
        # 2. Setup OpenAI-compatible client for Hugging Face Router
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=key,
        )
        
        system_prompt = (
            "You are an expert Hollywood script consultant (Story Editor). "
            "Analyze the provided ScriptPulse structural data and write professional, "
            "actionable 'Studio Coverage' notes for the writer.\n\n"
            "RULES:\n"
            "1. Be thorough. Explain the psychological impact of pacing issues on the reader.\n"
            "2. Suggest specific narrative fixes (e.g., 'Combine these two scenes into one high-stakes interaction').\n"
            "3. Format your report like a professional industry memo.\n"
            "4. DO NOT reference the raw JSON numbers directly; translate them into terms like 'Slow Burn' or 'Highly Dynamic'.\n"
            "5. Ensure the tone is encouraging but firm on craft standards."
        )
        
        user_content = f"Here is the ScriptPulse analysis data for my draft:\n\n{json.dumps(data_payload, indent=2)}\n\nPlease provide your expert consultation report."
        
        # 3. Request Completion from the Kimi-K2 model (via HF Router)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        if completion.choices:
            return completion.choices[0].message.content, None
        else:
            return None, "Empty response from the AI model."
            
    except Exception as e:
        error_msg = str(e)
        _log.error(f"AI Consultant Generation failed: {error_msg}")
        # Check for specific HF errors like rate limiting or credits
        if "rate limit" in error_msg.lower():
            return None, "Hugging Face rate limit reached. Please try again in a few minutes."
        elif "insufficient" in error_msg.lower():
            return None, "Hugging Face account credits exhausted."
        return None, error_msg
