"""Writer Intent Immunity Agent - Ethical Override Layer"""


# Allowed intent labels (ONLY these, no synonyms)
ALLOWED_INTENTS = {
    'intentionally exhausting',
    'intentionally confusing',
    'should feel smooth',
    'should feel tense',
    'experimental / anti-narrative'
}


def run(input_data):
    """
    Apply writer intent to suppress patterns where intent applies.
    
    Writer intent ALWAYS overrides system patterns.
    No inference. No judgment.
    
    Includes WSICC (Writer Self-Intent Consistency Check).
    """
    patterns = input_data.get('patterns', [])
    writer_intents = input_data.get('writer_intent', [])
    
    # Validate intents
    validated_intents = validate_intents(writer_intents)
    
    # WSICC: Check internal consistency
    consistency_warnings = check_internal_consistency(validated_intents)
    
    # If no intent declared, pass all patterns through unchanged
    if not validated_intents:
        return {
            'surfaced_patterns': patterns,
            'suppressed_patterns': [],
            'intent_alignment_notes': []
        }
    
    surfaced = []
    suppressed = []
    alignment_notes = []
    
    # Add consistency warnings to alignment notes
    alignment_notes.extend(consistency_warnings)
    
    for pattern in patterns:
        pattern_start, pattern_end = pattern['scene_range']
        
        # Check overlap with any intent
        overlap_result = check_intent_overlap(pattern_start, pattern_end, validated_intents)
        
        if overlap_result['full_overlap']:
            # Full suppression
            suppressed.append(pattern)
            alignment_notes.append({
                'pattern_type': pattern['pattern_type'],
                'scene_range': pattern['scene_range'],
                'intent': overlap_result['matching_intent'],
                'action': 'suppressed',
                'reason': 'Writer intent applies to entire pattern range'
            })
        elif overlap_result['partial_overlap']:
            # Partial suppression: split the pattern
            # Suppressed portion
            suppressed_pattern = pattern.copy()
            suppressed_pattern['scene_range'] = overlap_result['overlapping_range']
            suppressed.append(suppressed_pattern)
            
            # Remaining portion surfaces with downgraded confidence
            if overlap_result['remaining_range']:
                remaining_pattern = pattern.copy()
                remaining_pattern['scene_range'] = overlap_result['remaining_range']
                remaining_pattern['confidence'] = downgrade_confidence(pattern.get('confidence', 'high'))
                surfaced.append(remaining_pattern)
            
            alignment_notes.append({
                'pattern_type': pattern['pattern_type'],
                'scene_range': pattern['scene_range'],
                'intent': overlap_result['matching_intent'],
                'action': 'partial_suppression',
                'overlapping_range': overlap_result['overlapping_range'],
                'remaining_range': overlap_result['remaining_range']
            })
        else:
            # No overlap, surface unchanged
            surfaced.append(pattern)
    
    return {
        'surfaced_patterns': surfaced,
        'suppressed_patterns': suppressed,
        'intent_alignment_notes': alignment_notes
    }


def validate_intents(writer_intents):
    """
    Validate that intents use allowed labels only.
    
    Rejects any intent not in ALLOWED_INTENTS.
    No synonyms accepted.
    """
    if not writer_intents:
        return []
    
    validated = []
    
    for intent in writer_intents:
        if 'intent' not in intent or 'scene_range' not in intent:
            continue
        
        if intent['intent'] in ALLOWED_INTENTS:
            validated.append(intent)
        # Silently reject invalid intents (no inference/reinterpretation)
    
    return validated


def check_internal_consistency(intents):
    """
    WSICC: Check for conflicting intent declarations.
    e.g. "should feel smooth" overlapping with "intentionally exhausting"
    """
    warnings = []
    if len(intents) < 2:
        return warnings
        
    for i in range(len(intents)):
        for j in range(i + 1, len(intents)):
            intent_a = intents[i]
            intent_b = intents[j]
            
            # Check overlap
            start_a, end_a = intent_a['scene_range']
            start_b, end_b = intent_b['scene_range']
            
            overlap_start = max(start_a, start_b)
            overlap_end = min(end_a, end_b)
            
            if overlap_start <= overlap_end:
                # Overlap detected
                if intent_a['intent'] != intent_b['intent']:
                     warnings.append({
                         'warning_type': 'intent_conflict',
                         'message': f"Conflicting intents declared for scenes {overlap_start}-{overlap_end}: '{intent_a['intent']}' vs '{intent_b['intent']}'",
                         'scene_range': [overlap_start, overlap_end]
                     })
    return warnings


def check_intent_overlap(pattern_start, pattern_end, intents):
    """
    Check if pattern range overlaps with any intent range.
    
    Returns overlap details for precise handling.
    """
    for intent in intents:
        intent_start, intent_end = intent['scene_range']
        
        # Check for any overlap
        overlap_start = max(pattern_start, intent_start)
        overlap_end = min(pattern_end, intent_end)
        
        if overlap_start <= overlap_end:
            # There is overlap
            if intent_start <= pattern_start and intent_end >= pattern_end:
                # Full overlap (intent covers entire pattern)
                return {
                    'full_overlap': True,
                    'partial_overlap': False,
                    'matching_intent': intent['intent'],
                    'overlapping_range': None,
                    'remaining_range': None
                }
            else:
                # Partial overlap
                remaining_range = None
                if pattern_start < intent_start:
                    remaining_range = [pattern_start, intent_start - 1]
                elif pattern_end > intent_end:
                    remaining_range = [intent_end + 1, pattern_end]
                
                return {
                    'full_overlap': False,
                    'partial_overlap': True,
                    'matching_intent': intent['intent'],
                    'overlapping_range': [overlap_start, overlap_end],
                    'remaining_range': remaining_range
                }
    
    # No overlap
    return {
        'full_overlap': False,
        'partial_overlap': False,
        'matching_intent': None,
        'overlapping_range': None,
        'remaining_range': None
    }


def downgrade_confidence(current_confidence):
    """
    Downgrade confidence for partial overlap cases.
    
    Confidence can only decrease, never increase.
    """
    if current_confidence == 'high':
        return 'medium'
    elif current_confidence == 'medium':
        return 'low'
    else:
        return 'low'
