"""
Long-Range Fatigue & Delayed Recovery Modeling (LRF) Layer
vNext.5 Internal Upgrade - Temporal Realism

Models latent "Fatigue Reserve" (F_res) that accumulates during
sub-threshold strain and discharges later, creating realistic
delayed fatigue effects.
"""

def run(input_data):
    """
    Apply long-range fatigue dynamics to refine attentional signals.
    
    Args:
        input_data: Dict containing:
            'temporal_signals': List from temporal agent (with E[i], R[i], S[i])
            'features': List from encoding agent (for micro-structure check)
            
    Returns:
        List of refined temporal signals (S[i] updated)
        Includes internal 'fatigue_reserve' metric for debugging.
    """
    signals = input_data.get('temporal_signals', [])
    features = input_data.get('features', [])
    
    if not signals:
        return []
        
    refined_signals = []
    
    # Latent Fatigue Reserve F_res
    fatigue_reserve = 0.0
    
    # Constants
    ACCUMULATION_RATE = 0.15
    DISCHARGE_RATE = 0.4
    DECAY_RATE = 0.05 # Reserve dissipates slowly on its own
    
    for i, sig in enumerate(signals):
        # working copy
        new_sig = sig.copy()
        
        # Extract base metrics
        e_i = sig['instantaneous_effort']
        r_i = sig['recovery_credit']
        s_i = sig['attentional_signal']
        
        # === 1. ACCUMULATION PHASE ===
        # F_res accumulates when audience is "coping but not recovering"
        # Criteria: 
        # - Moderate Effort (0.3 < E < 0.6)
        # - Low Recovery (R < 0.2)
        
        accumulation = 0.0
        if 0.3 < e_i < 0.6 and r_i < 0.2:
            # Sub-threshold strain
            accumulation = (e_i - 0.3) * ACCUMULATION_RATE
            
        fatigue_reserve += accumulation
        
        # === 2. DISCHARGE PHASE ===
        # F_res discharges into S[i] when recovery is attempted OR overload occurs
        # If R > 0.3 (Strong Recovery attempt), the "crash" happens
        # Or if S > 0.8 (Overload), reserve dumps to exacerbate it
        
        discharge = 0.0
        
        if r_i > 0.3:
            # Recovery moment -> Latent fatigue surfaces ("now I feel it")
            discharge = fatigue_reserve * DISCHARGE_RATE
        elif s_i > 0.7:
             # Crisis moment -> Reserve adds weight
             discharge = fatigue_reserve * 0.2
             
        # Apply discharge to Signal
        # We increase S[i] but do NOT decrease R[i] (recovery credit remains valid)
        # The discharge represents the *cost* of that recovery or the *weight* of the crash.
        
        new_s_i = s_i + discharge
        fatigue_reserve -= discharge
        
        # === 3. PASSIVE DECAY ===
        # Unexpressed fatigue eventually fades (forgetting)
        fatigue_reserve *= (1.0 - DECAY_RATE)
        
        # Update signal
        new_sig['attentional_signal'] = round(new_s_i, 3)
        new_sig['fatigue_reserve'] = round(fatigue_reserve, 3) # Internal metric
        
        refined_signals.append(new_sig)
        
    return refined_signals
