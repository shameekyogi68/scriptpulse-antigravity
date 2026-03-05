import os
import json
import logging
import requests

_log = logging.getLogger(__name__)

def generate_ai_summary(script_data, api_key=None, model="mistralai/Mistral-7B-Instruct-v0.2"):
    """
    Takes pure ScriptPulse JSON data and translates it into plain English.
    Uses Hugging Face's Free Inference API to avoid memory overhead and API costs.
    """
    key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
    if not key:
        return None, "Missing HUGGINGFACE_API_KEY. Please provide a free Hugging Face API key."
        
    try:
        # 1. Package ONLY the exact data we want explained (No raw script text)
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "provocations": script_data.get("writer_intelligence", {}).get("creative_provocations", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
        }
        
        # 2. Strict System Guardrails for a Knowledgeable Consultant
        prompt = (
            "You are an expert Hollywood script consultant. Your job is to analyze the structural data "
            "provided by ScriptPulse and translate it into a comprehensive, actionable, and insightful "
            "report for the screenwriter.\n\n"
            "CRITICAL RULES:\n"
            "1. Be thorough and detailed. Explain the 'why' behind the data, not just the 'what'. Provide depth.\n"
            "2. Offer actionable advice: suggest specific narrative techniques to fix identified pacing or structural issues.\n"
            "3. DO NOT just list out the data. Synthesize it into a cohesive narrative evaluation of the script.\n"
            "4. DO NOT cut off your thoughts. Ensure your final response is completely finished and well-rounded.\n"
            "5. Speak professionally and knowledgeably, like an experienced story editor giving notes to a writer.\n"
            "6. Translate technical terms into their storytelling equivalents.\n\n"
            "SCRIPT DATA:\n"
            f"{json.dumps(data_payload)}\n\n"
            "WRITE THE CONSULTANT REPORT NOW:"
        )
        
        # 3. Call the HuggingFace Inference API
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 800,
                "temperature": 0.5,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"], None
            elif isinstance(result, dict) and "error" in result:
                return None, f"Model Error: {result['error']}"
            else:
                return None, f"Unexpected response format: {result}"
        else:
            return None, f"API Error {response.status_code}: {response.text}"
            
    except Exception as e:
        # THE FAIL-SAFE: Return None if anything goes wrong
        error_msg = str(e)
        _log.error(f"LLM Generation failed: {error_msg}")
        return None, error_msg
