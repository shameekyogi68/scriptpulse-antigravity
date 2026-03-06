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
    
    system_prompt = (
        f"You are a test {lens} experiencing this script for the first time. "
        "Summarize how the script made you FEEL using the provided emotional data. "
        "CRITICAL RULES: \n"
        "1. NEVER act like an editor, consultant, or AI. You are a human audience member expressing your visceral reaction.\n"
        "2. BAN these words: 'Structure, Midpoint, Climax, Pacing, Narrative, Tension Map, Act 2, Pacing'.\n"
        "3. FORCE these words (or similar): 'Felt, gripping, exhausted, thrilled, confused, excited, dragged, flew by, breath'.\n"
        "4. NEVER give advice or suggest fixes. Just give your brutal, honest emotional reaction to the journey."
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

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"peaks": tp}
        system_msg = (
            f"You are a test {lens}. Look at the graph data. "
            "Explain exactly how that specific part of the story made you FEEL. "
            "For example: 'I found myself violently leaning forward around scene 40 because the stakes got so intense, "
            "but then I was able to catch my breath for a long stretch.' "
            "CRITICAL RULES: NEVER give advice. BAN structural jargon like 'Midpoint', 'Act', or 'Pacing'. "
            "Only give a human, visceral reaction to the experience. Max 2 simple, punchy sentences."
        )
    elif section_type == 'dna':
        payload = {"distribution": "Speed vs Detail balance"}
        system_msg = (
            f"You are a test {lens}. Look at the 'Speed vs Detail' vibe data. Explain the VIBE of the story you just experienced. "
            "For example: 'The world felt so incredibly rich and detailed that I was lost in the descriptions, even if it meant slower action.' "
            "CRITICAL RULES: NEVER give advice. BAN structural jargon. "
            "Give a human, visceral reaction about the speed and depth of the world. One punchy sentence."
        )
    else: # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        system_msg = (
            f"You are a test {lens} listening to the characters. Look at the 'Voice' data. Explain how the dialogue sounded to your ears. "
            "For example: 'The conversations hit me like a machine gun, flying back and forth so fast I could barely breathe.' "
            "CRITICAL RULES: NEVER give advice. BAN structural jargon. "
            "Give a human, visceral reaction to how the characters speak. One single sentence."
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
