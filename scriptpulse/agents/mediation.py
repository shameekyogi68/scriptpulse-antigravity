"""Audience Experience Mediation Agent - Writer-Safe Language Translation"""


# Pattern-to-description mappings (experiential, non-prescriptive)
PATTERN_DESCRIPTIONS = {
    'sustained_attentional_demand': {
        'description': 'Sustained attentional demand observed',
        'experiential': 'This region asks the audience to stay focused over multiple scenes',
        'confidence_note': 'Based on signal persistence across scenes'
    },
    'limited_recovery': {
        'description': 'Limited recovery opportunities observed',
        'experiential': 'Few low-intensity moments appear in this stretch',
        'confidence_note': 'Based on recovery credit analysis'
    },
    'repetition': {
        'description': 'Repetitive pattern observed',
        'experiential': 'Similar experiential weight repeats across scenes',
        'confidence_note': 'Based on effort variance'
    },
    'surprise_cluster': {
        'description': 'Surprise cluster observed',
        'experiential': 'Multiple high-boundary scenes appear together',
        'confidence_note': 'Based on structural boundaries'
    },
    'constructive_strain': {
        'description': 'Constructive strain observed',
        'experiential': 'High demand with visible recovery maintains engagement',
        'confidence_note': 'Based on demand-recovery balance'
    },
    'degenerative_fatigue': {
        'description': 'Degenerative fatigue observed',
        'experiential': 'Accumulating demand without visible recovery',
        'confidence_note': 'Based on signal drift patterns'
    }
}


def run(input_data):
    """
    Translate patterns into writer-safe, experiential descriptions.
    
    No prescription. No judgment. No ranking.
    
    Args:
        input_data: Dict with 'surfaced_patterns' and 'suppressed_patterns' 
                   (from intent agent)
        
    Returns:
        Dict with mediated_output containing writer-safe descriptions
    """
    surfaced = input_data.get('surfaced_patterns', [])
    suppressed = input_data.get('suppressed_patterns', [])
    alignment_notes = input_data.get('intent_alignment_notes', [])
    
    mediated = []
    
    for pattern in surfaced:
        mediated_entry = mediate_pattern(pattern)
        mediated.append(mediated_entry)
    
    # Include suppression acknowledgments
    suppression_acknowledgments = []
    for note in alignment_notes:
        suppression_acknowledgments.append({
            'scene_range': note.get('scene_range', []),
            'acknowledgment': f"Writer intent acknowledged: {note.get('intent', 'unspecified')}",
            'action': note.get('action', 'noted')
        })
    
    return {
        'mediated_output': mediated,
        'suppression_acknowledgments': suppression_acknowledgments,
        'total_surfaced': len(surfaced),
        'total_suppressed': len(suppressed)
    }


def mediate_pattern(pattern):
    """
    Translate a single pattern into writer-safe language.
    
    Rules:
    - Describe experience, not quality
    - No "should", "could", "might help"
    - No ranking or prioritization
    - Include scene range for reference
    """
    pattern_type = pattern.get('pattern_type', 'unknown')
    scene_range = pattern.get('scene_range', [0, 0])
    confidence = pattern.get('confidence', 'low')
    
    # Get description template
    template = PATTERN_DESCRIPTIONS.get(pattern_type, {
        'description': f'{pattern_type} observed',
        'experiential': 'Pattern detected in this region',
        'confidence_note': 'Based on available signals'
    })
    
    return {
        'scene_range': scene_range,
        'description': template['description'],
        'experiential_note': template['experiential'],
        'confidence': confidence,
        'confidence_explanation': get_confidence_explanation(confidence),
        # Explicitly NO recommendation, NO action, NO judgment
    }


def get_confidence_explanation(confidence):
    """
    Explain confidence level in neutral terms.
    
    Never implies that low confidence is bad or high is good.
    """
    if confidence == 'high':
        return 'Pattern persisted clearly across multiple analysis windows'
    elif confidence == 'medium':
        return 'Pattern detected with some signal variance'
    else:
        return 'Pattern detected with high signal variance or limited persistence'


def format_for_display(mediated_output):
    """
    Format mediated output for display.
    
    Optional helper - not part of core pipeline.
    """
    lines = []
    
    for entry in mediated_output.get('mediated_output', []):
        start, end = entry['scene_range']
        lines.append(f"Scenes {start}-{end}: {entry['description']}")
        lines.append(f"  → {entry['experiential_note']}")
        lines.append(f"  Confidence: {entry['confidence']}")
        lines.append("")
    
    if mediated_output.get('suppression_acknowledgments'):
        lines.append("Intent Acknowledgments:")
        for ack in mediated_output['suppression_acknowledgments']:
            lines.append(f"  {ack['acknowledgment']}")
    
    return '\n'.join(lines)

