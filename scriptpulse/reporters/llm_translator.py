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
    groq_key = api_key or st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
    
    if not groq_key and not hf_key:
        return None, "Missing API Keys. Please set GROQ_API_KEY or HF_TOKEN in .streamlit/secrets.toml"
        
    try:
        # Prepare content
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
        }
        
        system_prompt = (
            "You are an expert Hollywood script consultant. "
            "Write a professional 'Studio Excellence' memo based on the script analyzer data provided.\n"
            "RULES:\n"
            "1. Focus on the 'why'—explain why a scene is fatuating or why pacing is working.\n"
            "2. Offer 3 concrete narrative fixes.\n"
            "3. Format as a clean industry memo. Do NOT include raw numbers or technical jargon."
        )
        user_content = f"Script Data:\n{json.dumps(data_payload, indent=2)}\n\nGenerate Memo:"

        # 2. Try GROQ first (Fastest / Generous Free Tier)
        if groq_key and GROQ_AVAILABLE:
            try:
                client = Groq(api_key=groq_key)
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.6,
                    max_tokens=1000
                )
                return completion.choices[0].message.content, None
            except Exception as ge:
                _log.warning(f"Groq failed, trying HF fallback: {ge}")

        # 3. Fallback to Hugging Face (Router)
        if hf_key:
            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=hf_key,
            )
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=1000
            )
            return completion.choices[0].message.content, None
            
        return None, "All AI providers failed. Check your keys."
            
    except Exception as e:
        error_msg = str(e)
        _log.error(f"AI Consultant error: {error_msg}")
        return None, error_msg
