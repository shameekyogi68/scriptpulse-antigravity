"""Audience Experience Mediation Agent - Writer-Safe Language Translation"""

import random

# WRITER-NATIVE TRANSLATIONS
# Translates technical signal patterns into visceral, screenplay-native concepts:
# Grip, Breath, Rhythm, Escalation, Release.
WRITER_NATIVE_TRANSLATIONS = {
    'sustained_attentional_demand': (
        "This run of scenes stays intense without a release valve — "
        "the audience may feel pushed without a moment to recover."
    ),
    'limited_recovery': (
        "Fatigue accumulates here. "
        "Without a clear breather, the audience's capacity to track detail may drop."
    ),
    'repetition': (
        "This stretch risks feeling like more of the same — "
        "the audience may stop registering escalation."
    ),
    'surprise_cluster': (
        "The rhythm spikes sharply here. "
        "Without setup, this intensity risks feeling jarring rather than impactful."
    ),
    'constructive_strain': (
        "This section demands heavy lifting. "
        "The audience is working hard to keep up — ensure the payoff is worth the effort."
    ),
    'degenerative_fatigue': {
        # Split handled in logic: Drift vs. Collapse
        'drift': (
            "The audience may start to drift here — "
            "this stretch risks losing grip unless something resets their focus."
        ),
        'collapse': (
            "The mental load here is becoming heavy. "
            "The audience may struggle to track new information effectively."
        )
    }
}


# Banned words (automatic failure if present)
BANNED_WORDS = {
    'good', 'bad', 'fix', 'improve', 'optimize', 'too long', 'too short',
    'slow', 'fast', 'weak', 'strong', 'problem', 'issue', 'ideal', 'optimal',
    'tips', 'suggestions', 'advice', 'should', 'must', 'need to'
}

# ADS: Authority Diffusion Safeguard Disclaimers
ADS_DISCLAIMERS = [
    "This reflects one modeled first-pass experience.",
    "Other readers may differ.",
    "This is not a statement about effectiveness.",
    "Attention varies by reader; this model tracks median structural load."
]


def run(input_data):
    """
    Translate patterns into writer-safe, question-first reflections.
    """
    surfaced = input_data.get('surfaced_patterns', [])
    suppressed = input_data.get('suppressed_patterns', [])
    alignment_notes = input_data.get('intent_alignment_notes', [])
    acd_states = input_data.get('acd_states', []) 
    ssf_analysis = input_data.get('ssf_analysis', {}) 
    
    reflections = []
    
    # === AEKS: Alert Escalation Kill-Switch (Constraint) ===
    total_scenes = 100 
    if acd_states:
        total_scenes = len(acd_states)
        
    max_alerts = max(3, int(total_scenes / 12))
    
    if len(surfaced) > max_alerts:
        conf_map = {'high': 3, 'medium': 2, 'low': 1}
        surfaced.sort(key=lambda x: conf_map.get(x.get('confidence'), 0), reverse=True)
        surfaced = surfaced[:max_alerts]
    
    # Generate reflections
    for pattern in surfaced:
        reflection = generate_reflection(pattern, acd_states, total_scenes)
        reflections.append(reflection)
    
    # Handle silence
    silence_explanation = None
    if not surfaced:
        silence_explanation = generate_silence_explanation(suppressed, alignment_notes, ssf_analysis)
    
    # Generate intent acknowledgments
    intent_acknowledgments = []
    for note in alignment_notes:
        ack = generate_intent_acknowledgment(note)
        intent_acknowledgments.append(ack)
    
    return {
        'reflections': reflections,
        'silence_explanation': silence_explanation,
        'intent_acknowledgments': intent_acknowledgments,
        'total_surfaced': len(surfaced), 
        'total_suppressed': len(suppressed),
        'aeks_active': len(input_data.get('surfaced_patterns', [])) > max_alerts 
    }


def generate_reflection(pattern, acd_states=None, total_scenes=100):
    """
    Generate a writer-native reflection.
    
    Uses terms like: Grip, Breath, Rhythm, Escalation.
    Avoids system jargon.
    """
    pattern_type = pattern.get('pattern_type', 'unknown')
    scene_range = pattern.get('scene_range', [0, 0])
    confidence = pattern.get('confidence', 'low')
    
    # Default fallback
    reflection_text = "This section creates a unique texture that may require specific audience tuning."

    # Select Translation
    if pattern_type == 'degenerative_fatigue' and acd_states:
        # Nuance for Drift vs Collapse
        start, end = scene_range
        window_acd = [state for state in acd_states 
                     if start <= state['scene_index'] <= end]
        
        avg_drift = 0.5
        avg_collapse = 0.5
        if window_acd:
            avg_drift = sum(s['drift_likelihood'] for s in window_acd) / len(window_acd)
            avg_collapse = sum(s['collapse_likelihood'] for s in window_acd) / len(window_acd)
            
        if avg_drift > avg_collapse:
             reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['drift']
        else:
             reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['collapse']
    
    elif pattern_type in WRITER_NATIVE_TRANSLATIONS:
        reflection_text = WRITER_NATIVE_TRANSLATIONS[pattern_type]
    
    # === FPG: FALSE PRECISION GUARD (Writer-Friendly) ===
    # Instead of "uncertainty increases", frame it as "Late-Script Fatigue" context.
    start, end = scene_range
    relative_pos = end / max(1, total_scenes)
    
    if relative_pos > 0.8:
        # Append a context note about the "Third Act Effect"
        # "Late in the script, this risk compounds with accumulated fatigue."
        # Or simpler:
        reflection_text += " (Deep in the script, this requires even more energy to sustain.)"

    return {
        'scene_range': scene_range,
        'reflection': reflection_text,
        'confidence': confidence
    }


def generate_silence_explanation(suppressed, alignment_notes, ssf_analysis=None):
    """
    Explain silence using writer-native terms: Stability, Flow, Alignment.
    """
    if alignment_notes:
        return (
            "Silence here means the system sees exactly what you intended. "
            "Your declared intent matches the audience load."
        )
    
    if ssf_analysis and ssf_analysis.get('is_silent'):
        explanation_key = ssf_analysis.get('explanation_key')
        
        if explanation_key == 'stable_continuity':
             return (
                "The experience here is rock stable. "
                "Effort and recovery are balanced—the audience is breathing naturally."
             )
        elif explanation_key == 'self_correcting':
            return (
                "The flow feels self-correcting. "
                "Whenever tension rises, a release valve opens naturally."
            )
        elif explanation_key == 'stable_but_drifting':
             return (
                 "The experience is stable, though the water is very still. "
                 "No strain, but also low demand."
             )
    
    if suppressed:
        return "Patterns were suppressed based on provided constraints."
    else:
        return (
            "The attentional flow is stable. "
            "No red flags, no drag, no exhaustion. A clean reading."
        )


def generate_intent_acknowledgment(note):
    intent = note.get('intent', 'your declared intent')
    scene_range = note.get('scene_range', [0, 0])
    
    start, end = scene_range
    scene_text = f"scenes {start}–{end}"
    
    return (
        f"You marked {scene_text} as '{intent}'. "
        f"This matches the signal perfectly."
    )


def validate_no_banned_words(text):
    text_lower = text.lower()
    for banned in BANNED_WORDS:
        if banned in text_lower:
            return False, banned
    return True, None


def format_for_display(mediated_output):
    """
    Format mediated output for display.
    """
    lines = []
    
    for entry in mediated_output.get('reflections', []):
        lines.append(entry['reflection'])
        lines.append("")
    
    if mediated_output.get('silence_explanation'):
        lines.append("—")
        lines.append(mediated_output['silence_explanation'])
        lines.append("")
    
    if mediated_output.get('intent_acknowledgments'):
        lines.append("Intent Acknowledgments:")
        for ack in mediated_output['intent_acknowledgments']:
            lines.append(f"  {ack}")
            
    lines.append("")
    lines.append(f"({random.choice(ADS_DISCLAIMERS)})")
    
    return '\n'.join(lines)
