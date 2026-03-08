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
    from google import genai
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

def generate_ai_summary(script_data, lens='viewer', api_key=None):
    """
    Translates ScriptPulse data into an emotional audience reaction.
    Rotates through providers to ensure high uptime and quality.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key # Manual override usually for groq
    
    if not any(keys.values()):
        return None, "All AI providers are offline. Please check your API Keys."
        
    data_payload = {
        "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
        "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
        "structural_dashboard": script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
    }
    
    # Customize the persona based on the lens
    persona_map = {
        "Studio Executive": "a sharp-eyed Development Executive at a major studio. Focus on commercial viability, audience demographic expansion, budget risks, and market positioning.",
        "Story Editor": "a master Story Editor for major film and television productions. Focus on internal character logic, causality, emotional stakes, and structural beats.",
        "Script Coordinator": "a technical Script Analyst and Pacing Consultant. Focus on dialogue economy, visual description energy, scene-to-scene transitions, and stylistic consistency."
    }
    persona_desc = persona_map.get(lens, "a professional Script Consultant.")

    system_prompt = (
        f"You are {persona_desc} "
        "Provide a comprehensive, actionable narrative analysis based on the structural and emotional data provided. "
        "CRITICAL RULES: \n"
        "1. Strictly maintain this specific professional persona. Use role-appropriate vocabulary (e.g., Executive uses 'ROI', 'Comp', 'Demographic'; Editor uses 'Beat', 'Arc', 'Causality'; Coordinator uses 'White Space', 'Rhythm', 'Flow').\n"
        "2. Prioritize your specific areas of expertise in the report.\n"
        "3. ALWAYS provide 3 concrete 'Fix Suggestions' at the end of the report to elevate the script for production.\n"
        "4. If you mention 'ScriptPulse', ALWAYS format it EXACTLY like this: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>\n"
        "5. Avoid archaic or overly rigid length rules. Prestige features often exceed 120 minutes; only flag length if it meaningfully drags the pacing or structural integrity."
    )
    user_content = f"Experience Data: {json.dumps(data_payload)}"

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

def generate_section_insight(script_data, section_type, lens='viewer', api_key=None):
    """
    Generates a high-impact visceral reaction that bridges the gap between 'math' and 'human feeling'.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key
    
    if not any(keys.values()):
        return "Connect an API key (Groq, Gemini, or HF) to hear audience reactions."

    # Persona definitions for sections
    persona_map = {
        "Studio Executive": "a Development Executive focused on commercial pacing and audience retention.",
        "Story Editor": "a Story Editor focused on structural beats and emotional momentum.",
        "Script Coordinator": "a Script Coordinator focused on the physical read and visual energy."
    }
    p_desc = persona_map.get(lens, "a professional Script Consultant.")

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"peaks": tp}
        system_msg = (
            f"You are {p_desc} Analyze the story's structural pacing graph. "
            "Explain how this sequence affects the audience's attention from your professional perspective. "
            "Identify the most significant pacing trend observed. One precise sentence. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    elif section_type == 'dna':
        payload = {"distribution": "Speed vs Detail balance"}
        system_msg = (
            f"You are {p_desc} Evaluate the balance of narrative action vs world-building. "
            "Evaluate the impact of this balance on reader immersion for the current story goals. One clear sentence. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    else: # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        system_msg = (
            f"You are {p_desc} Evaluate the rhythm and subtext of the characters' dialogue. "
            "Identify what the current dialogue texture reveals about the character dynamics. One professional sentence. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )

    user_content = f"Raw Experience Math: {json.dumps(payload)}\nAudience Reaction:"

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
                client = genai.Client(api_key=keys["gemini"])
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"SYSTEM: {system_msg}\n\nUSER: {user_content}"
                )
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
