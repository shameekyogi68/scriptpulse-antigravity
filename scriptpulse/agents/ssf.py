"""
Silence-as-Signal Formalization (SSF) Layer
vNext.5 Internal Upgrade - Trust & Mediation

The absence of alerts must be earned, explainable, and defensible.
This agent analyzes stability to license "Silence" as a valid signal.
"""

def run(input_data):
    """
    Analyze stability to determine silence validity and confidence.
    
    Args:
        input_data: Dict containing:
            'temporal_signals': List from temporal agent
            'acd_states': List from ACD agent
            'surfaced_patterns': List of patterns that WILL be shown
            
    Returns:
        Dict: {
            'is_silent': bool,
            'silence_confidence': 'high' | 'medium' | 'low',
            'stability_metrics': dict,
            'explanation_key': str
        }
    """
    signals = input_data.get('temporal_signals', [])
    acd_states = input_data.get('acd_states', [])
    surfaced = input_data.get('surfaced_patterns', [])
    
    # If patterns are surfaced, we are NOT in a silence state
    if surfaced:
        return {
            'is_silent': False,
            'silence_confidence': None,
            'stability_metrics': {},
            'explanation_key': None
        }
        
    if not signals:
         return {
            'is_silent': True,
            'silence_confidence': 'low', # No data = low confidence
            'stability_metrics': {},
            'explanation_key': 'no_data'
        }

    # === METRIC CALCULATION ===
    
    # 1. Strain Stability
    s_values = [s['attentional_signal'] for s in signals]
    max_s = max(s_values)
    avg_s = sum(s_values) / len(s_values)
    
    # 2. Recovery Availability
    r_values = [s['recovery_credit'] for s in signals]
    avg_r = sum(r_values) / len(r_values)
    
    # 3. ACD Stability
    c_values = [a['collapse_likelihood'] for a in acd_states] if acd_states else [0.0]
    max_c = max(c_values)
    d_values = [a['drift_likelihood'] for a in acd_states] if acd_states else [0.0]
    max_d = max(d_values)
    
    metrics = {
        'max_strain': round(max_s, 3),
        'avg_strain': round(avg_s, 3),
        'avg_recovery': round(avg_r, 3),
        'max_collapse': round(max_c, 3),
        'max_drift': round(max_d, 3)
    }
    
    # === CONFIDENCE BANDS ===
    
    # HIGH CONFIDENCE SILENCE
    # - Low max strain (< 0.6)
    # - Good recovery (> 0.15 avg)
    # - No latent collapse danger (< 0.5)
    high_conf = (
        max_s < 0.6 and
        avg_r > 0.15 and
        max_c < 0.5
    )
    
    # MEDIUM CONFIDENCE SILENCE
    # - Moderate strain (< 0.8)
    # - Decent recovery OR low average strain
    medium_conf = (
        max_s < 0.8 and
        (avg_r > 0.1 or avg_s < 0.3)
    )
    
    confidence = 'low'
    explanation_key = 'marginal_strain' # Default
    
    if high_conf:
        confidence = 'high'
        explanation_key = 'stable_continuity'
    elif medium_conf:
        confidence = 'medium'
        explanation_key = 'self_correcting'
        
    # Check for specific "Drift" silence (boring but stable)
    if confidence == 'high' and max_d > 0.7:
        explanation_key = 'stable_but_drifting'
        
    return {
        'is_silent': True,
        'silence_confidence': confidence,
        'stability_metrics': metrics,
        'explanation_key': explanation_key
    }
