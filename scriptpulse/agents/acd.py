"""
Attention Collapse vs Drift (ACD) Layer
vNext.5 Internal Upgrade - Invisible Intelligence

Differentiation of attentional failure modes:
1. Collapse: Overload-driven failure (High load, low recovery, stress)
2. Drift: Under-stimulation failure (Low variance, monotony, lack of novelty)
"""

def run(input_data):
    """
    Calculate latent Collapse and Drift states.
    
    Args:
        input_data: Dict containing:
            'temporal_signals': List from temporal agent (with E[i], R[i], S[i])
            'features': List from encoding agent (for structural change)
            
    Returns:
        List of ACD state dicts:
        {
            'scene_index': int,
            'collapse_likelihood': float (0-1),
            'drift_likelihood': float (0-1),
            'primary_state': str ('collapse', 'drift', 'stable')
        }
    """
    signals = input_data.get('temporal_signals', [])
    features = input_data.get('features', [])
    
    if not signals or not features:
        return []
    
    acd_states = []
    
    # Contextual running buffers
    prev_collapse = 0.0
    prev_drift = 0.0
    
    # Constants
    COLLAPSE_DECAY = 0.85 # Collapse is sticky
    DRIFT_DECAY = 0.6     # Drift clears faster on novelty
    
    for i, sig in enumerate(signals):
        feat = features[i]
        
        # Extract metrics
        effort = sig['instantaneous_effort']
        recovery = sig['recovery_credit']
        signal = sig['attentional_signal']
        struct_change = feat['structural_change']['event_boundary_score']
        
        # === COLLAPSE SIGNATURE ===
        # Driven by sustained high effort without recovery
        # Amplified by structural chaos (high event boundaries rapid-fire)
        
        collapse_pressure = 0.0
        if effort > 0.6:
            collapse_pressure += (effort - 0.6) * 2.0
        
        if recovery < 0.1:
            collapse_pressure += 0.2
            
        # Structural chaos multiplier
        if struct_change > 70: # High change
            collapse_pressure *= 1.2
            
        # Integration
        collapse = collapse_pressure + COLLAPSE_DECAY * prev_collapse
        collapse = min(1.0, collapse)
        prev_collapse = collapse
        
        # === DRIFT SIGNATURE ===
        # Driven by moderate/low effort with low variance/novelty
        # "Nothing demands attention strongly enough"
        
        drift_pressure = 0.0
        
        # Moderate zone (Goldilocks zone of boredom? Not high enough to grip, not low enough to rest?)
        # Actually drift happens when effort is flat.
        # We need variance context.
        
        effort_delta = 0.0
        if i > 0:
            effort_delta = abs(effort - signals[i-1]['instantaneous_effort'])
            
        if effort_delta < 0.1 and effort < 0.5:
             # Stagnation
             drift_pressure += 0.15
             
        if struct_change < 20:
            # Low structural novelty
            drift_pressure += 0.15
            
        # Integration
        drift = drift_pressure + DRIFT_DECAY * prev_drift
        drift = min(1.0, drift)
        
        # Novelty reset
        if struct_change > 60 or effort_delta > 0.3:
            drift *= 0.2 # Sharp drop on novelty
            
        prev_drift = drift
        
        # === CLASSIFICATION ===
        # Internal only
        primary = 'stable'
        if collapse > 0.6 and collapse > drift:
            primary = 'collapse'
        elif drift > 0.6 and drift > collapse:
            primary = 'drift'
            
        acd_states.append({
            'scene_index': sig['scene_index'],
            'collapse_likelihood': round(collapse, 3),
            'drift_likelihood': round(drift, 3),
            'primary_state': primary
        })
        
    return acd_states
