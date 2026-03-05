import os
import json
import logging
import streamlit as st
from openai import OpenAI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

_log = logging.getLogger(__name__)

def generate_ai_summary(script_data, api_key=None):
    """
    Translates ScriptPulse data into professional coverage.
    Prioritizes Groq (Extreme Speed + High Free Limits) 
    Falls back to Hugging Face (Kimi-K2-Instruct).
    """
    
    # 1. Gather Keys (Streamlit Secrets or Env Vars)
    # We use .get() Safely as Streamlit Secrets might raise an error if accessed directly as dict
    def get_token(key, fallback=None):
        try: return st.secrets.get(key)
        except: return os.environ.get(key, fallback)

    groq_key = api_key or get_token("GROQ_API_KEY")
    hf_key = get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    
    # Debug info for logs (Never log the actual key!)
    _log.info(f"AI Check: GroqKey={bool(groq_key)}, HFKey={bool(hf_key)}, GroqLib={GROQ_AVAILABLE}")

    if not groq_key and not hf_key:
        return None, "Missing API Keys. Please provide GROQ_API_KEY or HF_TOKEN in secrets."
        
    try:
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "structural":"dashboard_data"
        }
        
        system_prompt = (
            "You are an expert Hollywood script consultant. Summarize the script diagnostics into a professional memo. "
            "Suggest 3 concrete fixes. Be professional and high-level."
        )
        user_content = f"Data: {json.dumps(data_payload)}"

        # 2. Try GROQ first
        last_error = "None"
        if groq_key:
            if GROQ_AVAILABLE:
                try:
                    client = Groq(api_key=groq_key)
                    completion = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                        temperature=0.6,
                        max_tokens=1000
                    )
                    return completion.choices[0].message.content, None
                except Exception as ge:
                    last_error = f"Groq Error: {str(ge)}"
                    _log.warning(last_error)
            else:
                last_error = "Groq Library not found (Is 'groq' in requirements.txt?)"
                _log.error(last_error)

        # 3. Fallback to Hugging Face
        if hf_key:
            try:
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=hf_key)
                completion = client.chat.completions.create(
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                    max_tokens=1000
                )
                return completion.choices[0].message.content, None
            except Exception as he:
                last_error = f"HF Fallback Error: {str(he)}"
                _log.warning(last_error)
            
        return None, f"All AI providers failed. Last reason: {last_error}"
            
    except Exception as e:
        error_msg = f"Critical Pipeline Error: {str(e)}"
        _log.error(error_msg)
        return None, error_msg
