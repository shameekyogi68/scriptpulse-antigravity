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

def get_token(key, fallback=None):
    try: 
        val = st.secrets.get(key)
        if val: return val
    except: pass
    return os.environ.get(key, fallback)

def generate_ai_summary(script_data, api_key=None):
    """
    Translates ScriptPulse data into professional coverage.
    Prioritizes Groq (Extreme Speed + High Free Limits) 
    Falls back to Hugging Face (Kimi-K2-Instruct).
    """
    groq_key = api_key or get_token("GROQ_API_KEY")
    hf_key = get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    
    if not groq_key and not hf_key:
        return None, "Missing API Keys. Please provide GROQ_API_KEY or HF_TOKEN in secrets."
        
    try:
        data_payload = {
            "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
            "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
            "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
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
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                        temperature=0.6,
                        max_tokens=1000
                    )
                    return completion.choices[0].message.content, None
                except Exception as ge:
                    last_error = f"Groq Error: {str(ge)}"
            else:
                last_error = "Groq Library not found"

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
            
        return None, f"All AI providers failed. Last reason: {last_error}"
            
    except Exception as e:
        return None, str(e)

def generate_section_insight(script_data, section_type, api_key=None):
    """
    Generates a concise, high-impact AI insight for a specific dashboard section.
    Types: 'pulse', 'dna', 'habits'
    """
    groq_key = api_key or get_token("GROQ_API_KEY")
    hf_key = get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    
    if not groq_key and not hf_key:
        return "Connect your API key to see AI insights here."

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"structural_points": tp}
        system_msg = "You are a story editor. Analyze the 'Story Pulse' graph data. Specifically mention the turning points (Inciting Incident, Midpoint, etc.) and if the rising action looks healthy. Keep it under 2 sentences. No numbers, just story wisdom."
    elif section_type == 'dna':
        payload = {"data": "Explain the Style DNA chart balance."}
        system_msg = "You are a story editor. Explain the 'Style DNA' balance. If most scenes are Action/Climax, tell them it's high-octane. If mostly Mystery/Breather, tell them it's a slow burn. One simple, punchy sentence."
    else: # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        system_msg = "You are a writing coach. Summarize the writer's 'voice' based on their sentence style and dialogue rhythm. Be encouraging but honest. One sentence maximum."

    user_content = f"Data snippet: {json.dumps(payload)}\nConsultant Insight:"

    try:
        if groq_key and GROQ_AVAILABLE:
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                max_tokens=150,
                temperature=0.7
            )
            return completion.choices[0].message.content
        
        if hf_key:
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=hf_key)
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                max_tokens=150
            )
            return completion.choices[0].message.content
            
        return "Insight generated (Connecting to AI...)"
    except Exception as e:
        return "AI is thinking... refresh to view insight."
