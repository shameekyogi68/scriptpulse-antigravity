"""Temporal Dynamics Agent - Fatigue Carryover and Recovery Modeling"""


# Fixed parameters (not learned)
LAMBDA = 0.85  # Fatigue carryover coefficient
BETA = 0.3     # Recovery rate from low effort
GAMMA = 0.2    # Recovery from structural boundaries
DELTA = 0.25   # Recovery from ambient/observational scenes
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
    
    # Calculate script length for duration normalization
    total_scenes = len(features)
    length_factor = compute_length_factor(total_scenes)
    
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
        
        # Classify fatigue state with duration normalization
        fatigue_state = classify_fatigue_state(signal, length_factor)
        
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
    
    NEW: Splits into cognitive load and emotional attention channels.
    
    Uses fixed weights for observable features only.
    """
    # Extract normalized feature groups
    ling = scene_features['linguistic_load']
    dial = scene_features['dialogue_dynamics']
    visual = scene_features['visual_abstraction']
    ref = scene_features['referential_load']
    struct = scene_features['structural_change']
    ambient = scene_features.get('ambient_signals', {})
    
    # === COGNITIVE LOAD ===
    # Tracking, memory, parsing complexity, inference
    
    # Linguistic complexity (variance = parsing difficulty)
    ling_complexity = ling['sentence_length_variance'] / 20.0
    
    # Referential tracking (character count, reintroductions)
    ref_score = (
        ref['active_character_count'] / 10.0 +
        ref['character_reintroductions'] / 5.0
    )
    
    # Structural discontinuity (boundaries = inference load)
    struct_score = struct['event_boundary_score'] / 100.0
    
    # Dialogue tracking (speaker switches)
    dial_tracking = dial['speaker_switches'] / 20.0
    
    # Aggregate cognitive load
    cognitive_effort = (
        0.30 * ref_score +           # Character tracking
        0.30 * ling_complexity +     # Parsing difficulty
        0.25 * struct_score +        # Discontinuity inference
        0.15 * dial_tracking         # Turn-taking tracking
    )
    
    # === EMOTIONAL ATTENTION ===
    # Sustained engagement, empathetic presence
    
    # Dialogue continuity (turns = sustained engagement)
    dial_engagement = dial['dialogue_turns'] / 50.0
    
    # Visual continuity (action density)
    visual_score = (
        visual['action_lines'] / 50.0 +
        visual['continuous_action_runs'] / 10.0
    )
    
    # Linguistic volume (sentence count = information flow)
    ling_volume = ling['sentence_count'] / 50.0
    
    # Stillness factor (low ambient = higher emotional focus needed)
    stillness_factor = 1.0 - ambient.get('ambient_score', 0.5)
    
    # Aggregate emotional attention
    emotional_attention = (
        0.35 * dial_engagement +     # Sustained dialogue
        0.30 * visual_score +        # Visual density
        0.20 * ling_volume +         # Information flow
        0.15 * stillness_factor      # Non-ambient intensity
    )
    
    # === TOTAL EFFORT ===
    # Combine both channels (weighted toward cognitive for conservative estimates)
    total_effort = (
        0.55 * cognitive_effort +
        0.45 * emotional_attention
    )
    
    return total_effort


def compute_recovery(scene_features, effort):
    """
    Compute recovery credit R[i].
    
    Recovery comes from:
    1. Low-effort scenes
    2. Structural boundaries
    3. Ambient/observational scenes (NEW)
    """
    recovery = 0.0
    
    # 1. Low-effort recovery
    if effort < E_THRESHOLD:
        recovery += BETA * (E_THRESHOLD - effort)
    
    # 2. Structural boundary recovery
    boundary_score = scene_features['structural_change']['event_boundary_score']
    if boundary_score > 0.5:
        recovery += GAMMA * (boundary_score / 100.0)
    
    # 3. Ambient scene recovery (NEW)
    ambient = scene_features.get('ambient_signals', {})
    ambient_score = ambient.get('ambient_score', 0.0)
    is_ambient = ambient.get('is_ambient', False)
    
    if is_ambient:  # High ambient quality
        # Bonus recovery for reflective/observational space
        recovery += DELTA * ambient_score
    
    # Cap recovery
    recovery = min(recovery, R_MAX)
    
    return recovery


def compute_length_factor(total_scenes):
    """
    Compute threshold scaling based on script length.
    
    Returns multiplier for thresholds:
    - 1.0 = standard (50+ scenes)
    - 1.5 = relaxed (20-50 scenes)
    - 2.0 = very relaxed (<20 scenes)
    
    Rationale: Short films have higher acceptable attention density.
    Fatigue is duration-dependent.
    """
    if total_scenes >= 50:
        return 1.0  # Standard (feature-length)
    elif total_scenes >= 20:
        # Linear interpolation: 20 scenes → 1.5x, 50 scenes → 1.0x
        return 1.0 + (50 - total_scenes) / (50 - 20) * 0.5
    else:
        # Very short: 2x threshold (double tolerance)
        return 2.0


def classify_fatigue_state(signal, length_factor=1.0):
    """
    Classify fatigue state (descriptive, not evaluative).
    
    Scales thresholds by script length to account for duration-dependent fatigue.
    """
    # Base thresholds (for standard-length scripts)
    threshold_elevated = 0.5 * length_factor
    threshold_high = 1.0 * length_factor
    threshold_extreme = 1.5 * length_factor
    
    if signal < threshold_elevated:
        return "normal"
    elif signal < threshold_high:
        return "elevated"
    elif signal < threshold_extreme:
        return "high"
    else:
        return "extreme"

