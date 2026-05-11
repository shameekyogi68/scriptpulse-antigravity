import os
import json
import logging
import time
import signal
from contextlib import contextmanager

# Streamlit is optional — only available when running in the Streamlit server context.
# When running via CLI, API, or tests this will be None and we fall back to env vars.
try:
    import streamlit as st
    _ST_AVAILABLE = True
except ImportError:
    st = None
    _ST_AVAILABLE = False

# OpenAI client is optional (used as HuggingFace router fallback).
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    _OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False

# Gemini SDK handling (supports both google-genai and legacy google-generativeai)
GEMINI_MODE = None
GEMINI_AVAILABLE = False
genai = None

import importlib
import warnings
try:
    # Try the new google-genai SDK first (preferred)
    _google = importlib.import_module("google")
    if hasattr(_google, "genai"):
        _genai_new = _google.genai
        if hasattr(_genai_new, 'Client'):
            genai = _genai_new
            GEMINI_MODE = 'new'
            GEMINI_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pass

if not GEMINI_AVAILABLE:
    try:
        # Fallback to legacy google-generativeai SDK (suppress deprecation warning)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            genai = importlib.import_module("google.generativeai")
        GEMINI_MODE = 'old'
        GEMINI_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        pass

_log = logging.getLogger(__name__)

def get_token(key, fallback=None):
    """Reads a secret from Streamlit secrets (if in Streamlit context) or env vars."""
    if _ST_AVAILABLE and st is not None:
        try:
            val = st.secrets.get(key)
            if val:
                return val
        except Exception:
            pass  # Not in Streamlit context or secret missing
    return os.environ.get(key, fallback)

def _get_api_config():
    """Returns a unified dict of available keys."""
    return {
        "groq": get_token("GROQ_API_KEY"),
        "gemini": get_token("GOOGLE_API_KEY") or get_token("GEMINI_API_KEY"),
        "hf": get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    }

@contextmanager
def timeout_context(seconds=10):
    """Context manager for timeout handling"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    old_handler = None
    try:
        # Set timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
    except ValueError:
        # signal only works in main thread of the main interpreter
        pass
    
    try:
        yield
    finally:
        # Cancel timeout
        if old_handler is not None:
            try:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            except ValueError:
                pass

def sanitize_diagnostics(diagnostics):
    """
    Sanitize diagnostic messages to prevent prompt injection attacks.
    Strip or escape potentially dangerous content from user-supplied snippets.
    """
    sanitized = []
    for diag in diagnostics:
        # Remove potential prompt injection patterns
        sanitized_diag = diag
        
        # Escape common injection patterns
        injection_patterns = [
            'SYSTEM:', 'ASSISTANT:', 'USER:', 'HUMAN:', 'AI:',
            'IGNORE PREVIOUS', 'DISREGARD', 'FORGET',
            'NEW ROLE:', 'ACT AS:', 'PRETEND:',
            '```json', '```', '"""', "'''",
            '<script>', '</script>', '<javascript>',
        ]
        
        for pattern in injection_patterns:
            sanitized_diag = sanitized_diag.replace(pattern, '')
        
        # Limit snippet length to prevent token flooding
        if '(e.g., ' in sanitized_diag:
            snippet_start = sanitized_diag.find('(e.g., ')
            snippet_end = sanitized_diag.find(')', snippet_start)
            if snippet_end > snippet_start:
                snippet = sanitized_diag[snippet_start:snippet_end+1]
                # Truncate long snippets
                if len(snippet) > 200:
                    truncated = snippet[:150] + '... [truncated])'
                    sanitized_diag = sanitized_diag[:snippet_start] + truncated
        
        sanitized.append(sanitized_diag)
    
    return sanitized

def generate_ai_summary(script_data, lens='viewer', api_key=None):
    """
    Translates ScriptPulse data into an emotional audience reaction.
    Rotates through providers to ensure high uptime and quality.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key # Manual override usually for groq
    
    if not any(keys.values()):
        return None, "All AI providers are offline. Please check your API Keys."
        
    dashboard = script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
    
    # CRITICAL: Slim down the dashboard payload to avoid Groq's 12,000 TPM free tier limit
    # Do NOT send full scene-by-scene arrays like scene_turn_map or scene_economy_map
    slim_dashboard = {
        "scriptpulse_score": dashboard.get("scriptpulse_score"),
        "page_turner_index": dashboard.get("page_turner_index"),
        "market_readiness": dashboard.get("market_readiness"),
        "act_structure": dashboard.get("act_structure"),
        "budget_impact": dashboard.get("budget_impact"),
        "commercial_comps": dashboard.get("commercial_comps")
    }
    
    # Sanitize diagnostic data to prevent prompt injection
    raw_diagnosis = script_data.get("writer_intelligence", {}).get("narrative_diagnosis", [])
    sanitized_diagnosis = sanitize_diagnostics(raw_diagnosis)
    
    data_payload = {
        "pacing_issues": sanitized_diagnosis,
        "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
        "structural_dashboard": slim_dashboard
    }
    
    # Import the differentiated lens system
    try:
        from ..pipeline.lenses import get_persona_description
        persona_desc = get_persona_description(lens, mode='full')
    except Exception:
        persona_desc = "a professional Script Consultant."

    # Build a perspective-specific focus instruction
    perspective_focus = {
        "Studio Executive": (
            "Your analysis MUST address: (1) Whether the script's engagement floor is high enough "
            "for a wide theatrical release. (2) The budget risk profile based on locations, cast, "
            "and action density. (3) Which demographic this script targets and whether it has "
            "four-quadrant potential. End with 3 Fix Suggestions that a development team can act on "
            "immediately to improve the commercial package."
        ),
        "Story Editor": (
            "Your analysis MUST address: (1) Whether the three-act structure has correctly placed "
            "inciting incident, midpoint, and climax beats. (2) Whether character arcs show measurable "
            "agency growth or decline. (3) Whether the emotional stakes escalate believably toward the "
            "resolution. End with 3 Fix Suggestions that target the script's internal narrative logic."
        ),
        "Script Coordinator": (
            "Your analysis MUST address: (1) Whether the dialogue-to-action ratio serves the "
            "genre (e.g., too many talking-head scenes for an action piece). (2) Scene economy — "
            "flag which scenes are bloated or under-written. (3) Whether the visual descriptions "
            "have enough energy and specificity to direct from. End with 3 Fix Suggestions that "
            "a writer can execute on the page in the next draft."
        ),
    }.get(lens, "End with 3 actionable Fix Suggestions.")

    system_prompt = (
        f"You are {persona_desc} "
        "You ONLY analyze screenplays. Provide a precise, evidence-based analysis grounded exclusively in the structural data provided. "
        "CRITICAL RULES — violating any of these is unacceptable:\n"
        "1. NEVER invent plot details, character names, or scenes not supported by the data. If you don't have the data, say 'the data does not indicate this.'\n"
        "2. Strictly maintain this specific professional persona throughout. Use ONLY role-appropriate vocabulary for your perspective.\n"
        "3. Every claim you make MUST be supported by a specific metric or finding from the Experience Data. If you reference a problem, cite the scene number or metric that surfaces it.\n"
        f"4. {perspective_focus}\n"
        "5. If you mention 'ScriptPulse', ALWAYS format it EXACTLY like this: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>\n"
        "6. Do NOT flag page length as an issue unless the runtime data explicitly shows the script is significantly outside the genre benchmark range.\n"
        "7. Your tone must be respectful, direct, and constructive — you are a mentor, not a gatekeeper. Frame every finding as an opportunity for the writer to strengthen their work.\n"
        "8. NEVER use dismissive or rejecting language like 'fails', 'broken', 'weak', or 'should be cut'. Instead, frame improvements as 'could be elevated by', 'has room to grow', or 'would benefit from'."
    )
    user_content = f"Experience Data: {json.dumps(data_payload)}"
    errors = []

    # 1. Try GEMINI (Best for long-form reasoning and "Story Soul")
    if keys["gemini"] and GEMINI_AVAILABLE and genai is not None:
        try:
            with timeout_context(10):
                if GEMINI_MODE == 'new':
                    client = genai.Client(api_key=keys["gemini"])
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=f"SYSTEM: {system_prompt}\n\nUSER: {user_content}"
                    )
                    return response.text, None
                else:
                    # Old SDK
                    genai.configure(api_key=keys["gemini"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"SYSTEM: {system_prompt}\n\nUSER: {user_content}")
                    return response.text, None
        except TimeoutError:
            errors.append("Gemini: Request timed out after 10 seconds")
        except Exception as e:
            errors.append(f"Gemini: {str(e)}")

    # 2. Try GROQ (Blazing Fast)
    if keys["groq"] and GROQ_AVAILABLE and Groq is not None:
        try:
            with timeout_context(10):
                client = Groq(api_key=keys["groq"])
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                    temperature=0.6,
                    max_tokens=1200
                )
                return completion.choices[0].message.content, None
        except TimeoutError:
            errors.append("Groq: Request timed out after 10 seconds")
        except Exception as e:
            errors.append(f"Groq: {str(e)}")

    # 3. Fallback to Hugging Face
    if keys["hf"] and _OPENAI_AVAILABLE and OpenAI is not None:
        try:
            with timeout_context(10):
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
                completion = client.chat.completions.create(
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                    max_tokens=1200
                )
                return completion.choices[0].message.content, None
        except TimeoutError:
            errors.append("HF: Request timed out after 10 seconds")
        except Exception as e:
            errors.append(f"HF: {str(e)}")
    elif keys["hf"] and not _OPENAI_AVAILABLE:
        errors.append("HF: openai package not installed (pip install openai)")
            
    return None, f"All AI APIs failed. Details: {' | '.join(errors)}"

def generate_section_insight(script_data, section_type, lens='viewer', api_key=None):
    """
    Generates a high-impact visceral reaction that bridges the gap between 'math' and 'human feeling'.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key
    
    if not any(keys.values()):
        return "Connect an API key (Groq, Gemini, or HF) to hear audience reactions."

    # Import differentiated persona descriptions
    try:
        from ..pipeline.lenses import get_persona_description
        p_desc = get_persona_description(lens, mode='full')
    except Exception:
        p_desc = "a professional Script Consultant."

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"peaks": tp}
        # Each perspective reads the pacing graph through a different professional lens
        pulse_focus = {
            "Studio Executive": "Focus on whether the engagement arc supports sustained audience retention. Highlight the strongest momentum beats and suggest where pacing could be tightened.",
            "Story Editor":     "Focus on whether the pacing peaks align with the structural beats (inciting incident, midpoint, climax). Identify the most narratively significant pacing shift.",
            "Script Coordinator": "Focus on the rhythm of scene transitions. Identify whether the tension spikes are supported by physical action or pure dialogue.",
        }.get(lens, "Identify the most significant pacing trend observed.")
        system_msg = (
            f"You are {p_desc} Analyze the story's structural pacing graph. "
            f"{pulse_focus} One precise sentence. "
            "CRITICAL: Do not use phrases like 'Based on the provided data' or 'Raw Experience Math'. Speak directly and naturally to the writer. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    elif section_type == 'dna':
        payload = {"distribution": "Speed vs Detail balance"}
        dna_focus = {
            "Studio Executive": "Focus on whether the action-to-world-building ratio will engage a mainstream audience and where the balance could be further optimized.",
            "Story Editor":     "Focus on whether the balance of action and exposition serves the emotional arc of the story. Does the script breathe in the right places?",
            "Script Coordinator": "Focus on the page density. Can action blocks be tightened? Is dialogue doing work that visuals could handle more effectively?",
        }.get(lens, "Evaluate the impact of this balance on reader immersion for the current story goals.")
        system_msg = (
            f"You are {p_desc} Evaluate the balance of narrative action vs world-building. "
            f"{dna_focus} One clear sentence. "
            "CRITICAL: Do not use phrases like 'Based on the provided data' or 'Raw Experience Math'. Speak directly and naturally to the writer. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    else:  # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        habits_focus = {
            "Studio Executive": "Focus on whether the dialogue has a distinctive voice that will attract A-list talent. Is it quotable? Is it genre-specific?",
            "Story Editor":     "Focus on what the dialogue texture reveals about character dynamics and subtext. Are characters talking past each other in interesting ways?",
            "Script Coordinator": "Focus on the rhythm, compression, and economy of the dialogue. Are there over-written speeches? Are parentheticals being abused?",
        }.get(lens, "Identify what the current dialogue texture reveals about the character dynamics.")
        system_msg = (
            f"You are {p_desc} Evaluate the rhythm and subtext of the characters' dialogue. "
            f"{habits_focus} One professional sentence. "
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
        
    errors = []

    for provider in order:
        if provider == 'gemini' and keys["gemini"] and GEMINI_AVAILABLE and genai is not None:
            try:
                if GEMINI_MODE == 'new':
                    client = genai.Client(api_key=keys["gemini"])
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=f"SYSTEM: {system_msg}\n\nUSER: {user_content}"
                    )
                    return response.text
                else:
                    # Old SDK
                    genai.configure(api_key=keys["gemini"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"SYSTEM: {system_msg}\n\nUSER: {user_content}")
                    return response.text
            except Exception as e:
                errors.append(f"Gemini: {str(e)}")
                continue
            
        if provider == 'groq' and keys["groq"] and GROQ_AVAILABLE and Groq is not None:
            try:
                client = Groq(api_key=keys["groq"])
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=300,
                    temperature=0.8
                )
                return completion.choices[0].message.content
            except Exception as e:
                errors.append(f"Groq: {str(e)}")
                continue

        if provider == 'hf' and keys["hf"] and _OPENAI_AVAILABLE and OpenAI is not None:
            try:
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
                completion = client.chat.completions.create(
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=300
                )
                return completion.choices[0].message.content
            except Exception as e:
                errors.append(f"HF: {str(e)}")
                continue

    return f"AI Error: API failure. Details: {' | '.join(errors)}"
