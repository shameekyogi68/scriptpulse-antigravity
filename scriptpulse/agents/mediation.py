"""Audience Experience Mediation Agent - Writer-Safe Language Translation"""


# Allowed experiential translations (ONLY these mappings)
EXPERIENTIAL_TRANSLATIONS = {
    'sustained_attentional_demand': 'may feel mentally demanding',
    'limited_recovery': 'there may be little chance to catch their breath',
    'repetition': 'may feel similar to what came just before',
    'surprise_cluster': 'the shift may feel sudden on first exposure',
    'constructive_strain': 'may feel effortful but held together',
    'degenerative_fatigue': 'may begin to feel tiring over time'
}


# Banned words (automatic failure if present)
BANNED_WORDS = {
    'good', 'bad', 'fix', 'improve', 'optimize', 'too long', 'too short',
    'slow', 'fast', 'weak', 'strong', 'problem', 'issue', 'ideal', 'optimal',
    'tips', 'suggestions', 'advice', 'should', 'must', 'need to'
}


def run(input_data):
    """
    Translate patterns into writer-safe, question-first reflections.
    
    No judgment. No advice. No authority.
    
    Args:
        input_data: Dict with 'surfaced_patterns', 'suppressed_patterns', 
                   'intent_alignment_notes' (from intent agent)
        
    Returns:
        Dict with reflections and acknowledgments
    """
    surfaced = input_data.get('surfaced_patterns', [])
    suppressed = input_data.get('suppressed_patterns', [])
    alignment_notes = input_data.get('intent_alignment_notes', [])
    acd_states = input_data.get('acd_states', []) 
    ssf_analysis = input_data.get('ssf_analysis', {}) # NEW
    
    reflections = []
    
    # === AEKS: Alert Escalation Kill-Switch (Constraint) ===
    # Hard limit on alert density to prevent alarm fatigue.
    # Max 1 alert per 12 scenes, minimum 3 allowed.
    total_scenes = 100 # Default if unknown
    if acd_states:
        total_scenes = len(acd_states)
        
    max_alerts = max(3, int(total_scenes / 12))
    
    # If too many alerts, prioritize high confidence and truncate
    if len(surfaced) > max_alerts:
        # Sort key: High=3, Medium=2, Low=1
        conf_map = {'high': 3, 'medium': 2, 'low': 1}
        surfaced.sort(key=lambda x: conf_map.get(x.get('confidence'), 0), reverse=True)
        
        # Truncate
        surfaced = surfaced[:max_alerts]
    
    # Generate reflections for surfaced patterns
    for pattern in surfaced:
        reflection = generate_reflection(pattern, acd_states)
        reflections.append(reflection)
    
    # Handle silence (no patterns to surface)
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
        'total_surfaced': len(surfaced), # Reported post-AEKS
        'total_suppressed': len(suppressed),
        'aeks_active': len(input_data.get('surfaced_patterns', [])) > max_alerts # Telemetry flag
    }


def generate_reflection(pattern, acd_states=None):
    """
    Generate a question-first, experiential reflection.
    
    Rules:
    - Default to questions
    - Include explicit uncertainty (may/might/could)
    - Use only allowed translations
    - NEW: Use ACD states to nuance 'tiring' vs 'wandering'
    """
    pattern_type = pattern.get('pattern_type', 'unknown')
    scene_range = pattern.get('scene_range', [0, 0])
    confidence = pattern.get('confidence', 'low')
    
    # Get allowed translation
    experience = EXPERIENTIAL_TRANSLATIONS.get(
        pattern_type, 
        'may have some experiential texture'
    )
    
    # === ACD PHRASING BIAS ===
    # For fatigue/demand patterns, check if it's Collapse (tiring) or Drift (wandering)
    if pattern_type in ['sustained_attentional_demand', 'degenerative_fatigue'] and acd_states:
        start, end = scene_range
        # Check average drift/collapse in this window
        window_acd = [state for state in acd_states 
                     if start <= state['scene_index'] <= end]
        
        if window_acd:
            avg_drift = sum(s['drift_likelihood'] for s in window_acd) / len(window_acd)
            avg_collapse = sum(s['collapse_likelihood'] for s in window_acd) / len(window_acd)
            
            # Bias Phrasing
            if avg_drift > 0.6 and avg_drift > avg_collapse:
                # DRIFT DOMINANT -> "attention may begin to wander"
                experience = "attention may begin to wander"
            elif avg_collapse > 0.6:
                # COLLAPSE DOMINANT -> "may feel mentally tiring"
                experience = "may feel mentally tiring"
    
    # Format scene range
    start, end = scene_range
    scene_text = f"scenes {start} through {end}" if start != end else f"scene {start}"
    
    # Generate question-first framing with uncertainty
    if confidence == 'high':
        reflection = (
            f"With moderate confidence, a first-time audience watching {scene_text} "
            f"{experience}. Is that the level of attention you want here?"
        )
    elif confidence == 'medium':
        reflection = (
            f"There's a possibility that {scene_text} {experience} for a first-time viewer. "
            f"Does that match your intention?"
        )
    else:  # low confidence
        reflection = (
            f"With low confidence, {scene_text} might {experience.replace('may ', '')}. "
            f"This signal is uncertain."
        )
    
    return {
        'scene_range': scene_range,
        'reflection': reflection,
        'confidence': confidence
    }


def generate_silence_explanation(suppressed, alignment_notes, ssf_analysis=None):
    """
    Explain why no patterns surfaced.
    
    Silence must NEVER imply quality or success.
    NEW: Use SSF analysis to explain stability.
    """
    if alignment_notes:
        # Patterns exist but were suppressed due to intent
        return (
            "No patterns are surfaced here because they align with your declared intent. "
            "The signals observed are consistent with what you indicated."
        )
    
    # Check SSF Analysis first for "Earned Silence"
    if ssf_analysis and ssf_analysis.get('is_silent'):
        explanation_key = ssf_analysis.get('explanation_key')
        
        if explanation_key == 'stable_continuity':
             return (
                "Across this run, the audience experience remains relatively stable, "
                "with natural effort and recovery balancing out. "
                "No moments stood out as likely to strain first-pass attention."
             )
        elif explanation_key == 'self_correcting':
            return (
                "While individual moments may require focus, they tend to resolve without "
                "accumulating fatigue. The attentional flow appears self-correcting."
            )
        elif explanation_key == 'stable_but_drifting':
             return (
                 "The experience is stable, though low-variance. "
                 "Attention is not strained, though it may not be heavily demanded."
             )
    
    if suppressed:
        # Should not happen (suppressed without notes), but handle gracefully
        return "Patterns were suppressed based on provided constraints."
    else:
        # No patterns detected at all (Low confidence fallback)
        return (
            "The attentional flow appears stable with regular recovery, "
            "or signals are low confidence due to draft variability. "
            "This does not indicate quality — only that no persistent patterns were detected."
        )


def generate_intent_acknowledgment(note):
    """
    Acknowledge writer intent explicitly.
    
    This is mandatory when patterns are suppressed due to intent.
    """
    intent = note.get('intent', 'your declared intent')
    scene_range = note.get('scene_range', [0, 0])
    
    start, end = scene_range
    scene_text = f"scenes {start} through {end}" if start != end else f"scene {start}"
    
    return (
        f"You marked {scene_text} as '{intent}'. "
        f"The signals here are consistent with that intent."
    )


def validate_no_banned_words(text):
    """
    Check that text contains no banned words.
    
    Used for testing compliance.
    """
    text_lower = text.lower()
    for banned in BANNED_WORDS:
        if banned in text_lower:
            return False, banned
    return True, None


def format_for_display(mediated_output):
    """
    Format mediated output for display.
    
    Optional helper - not part of core pipeline.
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
    
    return '\n'.join(lines)


