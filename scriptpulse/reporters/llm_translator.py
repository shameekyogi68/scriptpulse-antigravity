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

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

_log = logging.getLogger(__name__)

def get_token(key, fallback=None):
    try: 
        val = st.secrets.get(key)
        if val: return val
    except: pass
    return os.environ.get(key, fallback)

def _get_api_config():
    """Returns a unified dict of available keys."""
    return {
        "groq": get_token("GROQ_API_KEY"),
        "gemini": get_token("GOOGLE_API_KEY") or get_token("GEMINI_API_KEY"),
        "hf": get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    }

def generate_ai_summary(script_data, api_key=None):
    """
    Translates ScriptPulse data into professional coverage.
    Rotates through providers to ensure high uptime and quality.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key # Manual override usually for groq
    
    if not any(keys.values()):
        return None, "All AI providers are offline. Please check your API Keys (GROQ, GEMINI, or HF)."
        
    data_payload = {
        "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
        "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
        "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
    }
    
    system_prompt = (
        "You are an expert Hollywood script consultant. Look past the numbers and focus on the story's soul. "
        "Summarize the script's health in a professional memo based on the data provided. "
        "CRITICAL RULES: NEVER give advice. NEVER suggest fixes. NEVER tell the writer what they 'need' to do. "
        "Your only job is to act as a mirror, reflecting the script's current structural and emotional condition with brutal honesty and high-level professionalism."
    )
    user_content = f"Data Analysis Packet: {json.dumps(data_payload)}"

    # 1. Try GEMINI (Best for long-form reasoning and "Story Soul")
    if keys["gemini"] and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=keys["gemini"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"SYSTEM: {system_prompt}\n\nUSER: {user_content}")
            return response.text, None
        except Exception as ge: pass

    # 2. Try GROQ (Blazing Fast)
    if keys["groq"] and GROQ_AVAILABLE:
        try:
            client = Groq(api_key=keys["groq"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                temperature=0.6,
                max_tokens=1000
            )
            return completion.choices[0].message.content, None
        except Exception: pass

    # 3. Fallback to Hugging Face
    if keys["hf"]:
        try:
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                max_tokens=1000
            )
            return completion.choices[0].message.content, None
        except Exception: pass
            
    return None, "Ran out of AI API calls. Please try again in 60 seconds."

def generate_section_insight(script_data, section_type, api_key=None):
    """
    Generates a high-impact AI insight that bridges the gap between 'math' and 'story'.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key
    
    if not any(keys.values()):
        return "Connect an API key (Groq, Gemini, or HF) to unlock AI story coaching."

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"turning_points": tp}
        system_msg = (
            "You are a master story analyzer sitting with the writer, looking at their 'Emotional Rollercoaster' graph. "
            "Explain exactly WHY the graph looks this way based on what they have ALREADY written. "
            "For example: 'You have a massive peak at scene 40 because your Midpoint climax has intense emotional stakes. "
            "The flatline after it shows a long period of low tension.' "
            "CRITICAL RULES: NEVER give advice. NEVER suggest how to fix it. NEVER tell the writer what they 'need' to do. "
            "Only act as a mirror reflecting their current narrative choices. Max 2 simple, punchy sentences. No jargon."
        )
    elif section_type == 'dna':
        payload = {"distribution": "The Speed vs Detail balance of the scenes."}
        system_msg = (
            "You are a cinematic analyzer looking at the 'Scene Pacing Map'. Explain WHY their script sits in its current quadrant. "
            "For example: 'Your script is sitting heavily in the World-Building corner because your scenes favor rich descriptions over rapid action.' "
            "CRITICAL RULES: NEVER give advice. NEVER tell them to 'try tightening' or 'pull it toward' another quadrant. "
            "Only reflect the current 'vibe' of their script as a statement of fact. One punchy, evocative sentence."
        )
    else: # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        system_msg = (
            "You are a vocal analyzer looking at the 'Writer's Voice' radar chart. Explain WHY the spikes look the way they do based on their text. "
            "For example: 'The massive spike in Dialogue Rhythm means you write rapid-fire, Sorkin-style exchanges, "
            "while your low Action Density shows scenes driven almost entirely by talking.' "
            "CRITICAL RULES: NEVER give advice. NEVER say they are 'neglecting' something or should change their style."
            "Make them understand the visual shape of their talent as it currently exists. One single sentence."
        )

    user_content = f"Narrative Telemetry: {json.dumps(payload)}\nConsultant Coaching:"

    user_content = f"Narrative Telemetry: {json.dumps(payload)}\nConsultant Coaching:"

    # PURPOSE-BASED DISTRIBUTION (To avoid free-tier rate limits)
    # Gemini: 'pulse' (Story/Emotion) | Groq: 'dna' and 'habits' (Structure/Pattern)
    
    order = []
    if section_type == 'pulse':
        order = ['gemini', 'groq', 'hf']
    else:
        order = ['groq', 'gemini', 'hf']

    for provider in order:
        if provider == 'gemini' and keys["gemini"] and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=keys["gemini"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"SYSTEM: {system_msg}\n\nUSER: {user_content}")
                return response.text
            except Exception: continue
            
        if provider == 'groq' and keys["groq"] and GROQ_AVAILABLE:
            try:
                client = Groq(api_key=keys["groq"])
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=100,
                    temperature=0.8
                )
                return completion.choices[0].message.content
            except Exception: continue

        if provider == 'hf' and keys["hf"]:
            try:
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
                completion = client.chat.completions.create(
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=100
                )
                return completion.choices[0].message.content
            except Exception: continue

    return "AI is gathering its thoughts... (Provider Busy)"
