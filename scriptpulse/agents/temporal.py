"""Temporal Dynamics Agent - Fatigue Carryover and Recovery Modeling"""


# Fixed parameters (not learned)
LAMBDA = 0.85  # Fatigue carryover coefficient
BETA = 0.3     # Recovery rate from low effort
GAMMA = 0.2    # Recovery from structural boundaries
R_MAX = 0.5    # Maximum recovery per scene
E_THRESHOLD = 0.4  # Low-effort threshold for recovery


def run(input_data):
    """
    Compute temporal dynamics with fatigue carryover.
    
    Canonical equation: S[i] = E[i] + λ·S[i-1] - R[i]
    
    Args:
        input_data: Dict with 'features' (list of feature vectors from encoding)
        
    Returns:
        List of temporal signal dicts with scene_index, effort, signal, recovery
    """
    features = input_data.get('features', [])
    
    if not features:
        return []
    
    signals = []
    prev_signal = 0.0
    
    for i, scene_features in enumerate(features):
        scene_idx = scene_features['scene_index']
        
        # Compute instantaneous effort E[i]
        effort = compute_instantaneous_effort(scene_features)
        
        # Compute recovery credit R[i]
        recovery = compute_recovery(scene_features, effort)
        
        # Apply canonical equation: S[i] = E[i] + λ·S[i-1] - R[i]
        if i == 0:
            signal = effort  # First scene has no carryover
        else:
            signal = effort + LAMBDA * prev_signal - recovery
        
        # Ensure non-negative
        signal = max(0.0, signal)
        
        # Classify fatigue state (descriptive only)
        fatigue_state = classify_fatigue_state(signal)
        
        # Store signal
        signals.append({
            'scene_index': scene_idx,
            'instantaneous_effort': round(effort, 3),
            'attentional_signal': round(signal, 3),
            'recovery_credit': round(recovery, 3),
            'fatigue_state': fatigue_state
        })
        
        prev_signal = signal
    
    return signals


def compute_instantaneous_effort(scene_features):
    """
    Compute instantaneous effort E[i] from feature vector.
    
    Uses fixed weights for observable features only.
    """
    # Extract normalized feature groups
    ling = scene_features['linguistic_load']
    dial = scene_features['dialogue_dynamics']
    visual = scene_features['visual_abstraction']
    ref = scene_features['referential_load']
    struct = scene_features['structural_change']
    
    # Normalize and aggregate each group
    ling_score = (
        ling['sentence_count'] / 50.0 +
        ling['mean_sentence_length'] / 20.0
    )
    
    dial_score = (
        dial['dialogue_turns'] / 50.0 +
        dial['speaker_switches'] / 20.0 +
        dial['turn_velocity']
    )
    
    visual_score = (
        visual['action_lines'] / 50.0 +
        visual['continuous_action_runs'] / 10.0
    )
    
    ref_score = (
        ref['active_character_count'] / 10.0 +
        ref['character_reintroductions'] / 5.0
    )
    
    struct_score = struct['event_boundary_score'] / 100.0
    
    # Fixed weights
    W_LINGUISTIC = 0.25
    W_DIALOGUE = 0.20
    W_VISUAL = 0.30
    W_REFERENTIAL = 0.15
    W_STRUCTURAL = 0.10
    
    effort = (
        W_LINGUISTIC * ling_score +
        W_DIALOGUE * dial_score +
        W_VISUAL * visual_score +
        W_REFERENTIAL * ref_score +
        W_STRUCTURAL * struct_score
    )
    
    return effort


def compute_recovery(scene_features, effort):
    """
    Compute recovery credit R[i].
    
    Recovery comes from:
    1. Low-effort scenes
    2. Structural boundaries
    """
    recovery = 0.0
    
    # 1. Low-effort recovery
    if effort < E_THRESHOLD:
        recovery += BETA * (E_THRESHOLD - effort)
    
    # 2. Structural boundary recovery
    boundary_score = scene_features['structural_change']['event_boundary_score']
    if boundary_score > 0.5:
        recovery += GAMMA * (boundary_score / 100.0)
    
    # Cap recovery
    recovery = min(recovery, R_MAX)
    
    return recovery


def classify_fatigue_state(signal):
    """Classify fatigue state (descriptive, not evaluative)"""
    if signal < 0.5:
        return "normal"
    elif signal < 1.0:
        return "elevated"
    elif signal < 1.5:
        return "high"
    else:
        return "extreme"

