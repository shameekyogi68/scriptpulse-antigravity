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
    
    v13.1 Upgrade: Nonlinear fatigue growth for sustained high-effort sequences.
    
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
    
    # Constants (v13.1 Tuning)
    ACCUMULATION_RATE = 0.15
    DISCHARGE_RATE = 0.4
    DECAY_RATE = 0.05
    
    # v13.1: Sustained Load Fatigue Constants
    SUSTAINED_EFFORT_THRESHOLD = 0.4   # Scenes above this count as "high load"
    SUSTAINED_ONSET = 3                 # Fatigue kicks in after this many consecutive high scenes
    K1 = 0.025                          # Linear fatigue per scene index
    K2 = 0.008                          # Quadratic fatigue growth
    
    consecutive_high = 0  # Track consecutive high-effort scenes
    
    for i, sig in enumerate(signals):
        new_sig = sig.copy()
        
        e_i = sig['instantaneous_effort']
        r_i = sig['recovery_credit']
        s_i = sig['attentional_signal']
        
        # === v13.1: SUSTAINED LOAD TRACKING ===
        if e_i >= SUSTAINED_EFFORT_THRESHOLD:
            consecutive_high += 1
        else:
            consecutive_high = max(0, consecutive_high - 2)  # Slow cooldown
        
        # === 1. ACCUMULATION PHASE ===
        accumulation = 0.0
        if 0.3 < e_i < 0.6 and r_i < 0.2:
            accumulation = (e_i - 0.3) * ACCUMULATION_RATE
        
        # v13.1: Also accumulate during sustained high effort (above 0.6)
        if e_i >= 0.6:
            accumulation += e_i * ACCUMULATION_RATE * 0.5
            
        fatigue_reserve += accumulation
        
        # === 2. DISCHARGE PHASE ===
        discharge = 0.0
        
        if r_i > 0.3:
            discharge = fatigue_reserve * DISCHARGE_RATE
        elif s_i > 0.7:
             discharge = fatigue_reserve * 0.2
             
        new_s_i = s_i + discharge
        fatigue_reserve -= discharge
        
        # === 3. v13.1: SUSTAINED FATIGUE PENALTY ===
        # After SUSTAINED_ONSET consecutive high scenes, apply growing penalty
        sustained_penalty = 0.0
        if consecutive_high > SUSTAINED_ONSET:
            excess = consecutive_high - SUSTAINED_ONSET
            sustained_penalty = K1 * excess + K2 * (excess ** 2)
            sustained_penalty = min(sustained_penalty, 0.4)  # Cap at 40% reduction
        
        # Apply penalty: REDUCE signal (audience tunes out)
        new_s_i = new_s_i * (1.0 - sustained_penalty)
        
        # === 4. PASSIVE DECAY ===
        fatigue_reserve *= (1.0 - DECAY_RATE)
        
        # Update signal
        new_sig['attentional_signal'] = round(new_s_i, 3)
        new_sig['fatigue_reserve'] = round(fatigue_reserve, 3)
        new_sig['sustained_fatigue_penalty'] = round(sustained_penalty, 3)
        
        refined_signals.append(new_sig)
        
    return refined_signals
