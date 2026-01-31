"""
Temporal Attentional Microdynamics (TAM) Layer
vNext.5 Internal Upgrade - Invisible Intelligence

Models intra-scene attentional fluctuation to refine scene-level E[i] and R[i].
Operates on the normalized micro-time axis \u03c4 [0,1].
"""

import math

def run_micro_integration(scene_features, base_effort):
    """
    Refine Effort E[i] and Recovery R[i] using micro-dynamics.
    
    Args:
        scene_features: Encoded features including 'micro_structure'
        base_effort: The scalar E[i] calculated by the main Temporal agent
        
    Returns:
        Dict {
            'effort_modifier': float,  # Multiplier for E[i]
            'recovery_modifier': float, # Multiplier for R[i]
            'micro_fatigue_integral': float # Internal metric for debugging
        }
    """
    micro = scene_features.get('micro_structure', [])
    if not micro:
        return {'effort_modifier': 1.0, 'recovery_modifier': 1.0, 'micro_fatigue_integral': 0.0}
    
    # 1. Map Micro-Effort e(\u03c4)
    # We map line tags/lengths to instantaneous effort e_t
    # This is relative density, not absolute load
    e_tau = []
    
    for item in micro:
        tag = item['tag']
        words = item['word_count']
        
        # Base instantaneous load per line type
        if tag == 'A':  # Action
            # Dense text blocks are heaviest
            val = 0.5 + min(0.5, words / 20.0) 
        elif tag == 'D': # Dialogue
            # Dialogue is lighter but varies by length
            val = 0.3 + min(0.4, words / 15.0)
        elif tag == 'S': # Scene Heading
            val = 0.8 # Heading is a re-orientation spike
        elif tag == 'C': # Character
            val = 0.1 # Name is negligible, just tracking
        else:
            val = 0.2
            
        e_tau.append(val)
        
    if not e_tau:
        return {'effort_modifier': 1.0, 'recovery_modifier': 1.0}
        
    # 2. Compute Micro-Fatigue Accumulation \u03c3(\u03c4)
    # \u03c3_t = e_t + 0.9 * \u03c3_{t-1} (Micro-carryover)
    # This detects "surges" vs "oscillations"
    
    sigma = []
    prev_s = 0.0
    micro_lambda = 0.9 # High retention within scene
    
    for e in e_tau:
        s = e + micro_lambda * prev_s
        sigma.append(s)
        prev_s = s
        
    # 3. Derive Modifiers
    
    # PEAK FATIGUE PENALTY
    # If intra-scene fatigue hits a "wall" early, the scene feels heavier than its average
    peak_sigma = max(sigma) if sigma else 0
    avg_sigma = sum(sigma) / len(sigma) if sigma else 0
    
    # Normalize peak relative to length (longer scenes naturally have higher sigma sum)
    # We want density-independent peak
    # Ideally, e_t is 0-1. Sigma can grow to ~10. 
    # Use simple heuristic: if peak is very high relative to average, it's structured badly
    
    # EFFORT MODIFIER
    # If the distribution is bottom-heavy (end of scene), it feels heavier
    # We integrate weighted by time? No, stick to simple density.
    
    # Let's use the Ratio of Peak to Mean.
    # High Peak/Mean => Spiky/Uneven => Higher perceived effort
    
    uniformity = avg_sigma / peak_sigma if peak_sigma > 0 else 1.0
    
    # If uniformity is low (spiky), effort modifier increases slightly
    # If uniformity is high (constant load), effort modifier is neutral
    
    effort_mod = 1.0 + (1.0 - uniformity) * 0.2 # Max +20% for uneven surges
    
    
    # RECOVERY MODIFIER
    # Recovery requires CONTINUOUS low-load windows.
    # We define low-load as e(\u03c4) < 0.3
    
    low_load_run = 0
    max_low_load_run = 0
    
    for e in e_tau:
        if e < 0.35: # "Breathing room" threshold
            low_load_run += 1
        else:
            max_low_load_run = max(max_low_load_run, low_load_run)
            low_load_run = 0
    max_low_load_run = max(max_low_load_run, low_load_run)
    
    # Relative recovery window
    # If max run is < 10% of scene, no recovery is possible
    # regardless of average
    
    rel_window = max_low_load_run / len(e_tau)
    
    if rel_window < 0.15: 
        # Fragmented relief -> Penalty to recovery
        recovery_mod = 0.5 # Halve the recovery credit
    elif rel_window < 0.30:
        recovery_mod = 0.8
    else:
        recovery_mod = 1.0 # Full recovery credit
        
    # 4. Collapse to Scalar
    return {
        'effort_modifier': round(effort_mod, 3),
        'recovery_modifier': round(recovery_mod, 3),
        'micro_fatigue_integral': round(avg_sigma, 3)
    }
