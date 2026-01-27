"""Pattern Detection Agent - Non-Evaluative Pattern Detection"""


# Configuration
MIN_PERSISTENCE_SCENES = 3  # Patterns must span at least 3 scenes
HIGH_CONFIDENCE_THRESHOLD = 0.8
MEDIUM_CONFIDENCE_THRESHOLD = 0.5


def run(input_data):
    """
    Detect persistent experiential patterns (non-evaluative).
    
    Args:
        input_data: Dict with 'temporal_signals' (list from temporal agent)
                    and 'features' (list from encoding agent)
        
    Returns:
        List of pattern descriptors (pattern_type, scene_range, confidence)
    """
    signals = input_data.get('temporal_signals', [])
    features = input_data.get('features', [])  # NEW: needed for functional differentiation
    
    if len(signals) < MIN_PERSISTENCE_SCENES:
        return []  # Cannot detect patterns with insufficient data
    
    # Calculate script-level context for calibration
    total_scenes = len(signals)
    length_factor = compute_length_factor(total_scenes)
    script_contrast = compute_script_contrast(signals)
    
    patterns = []
    
    # Detect each pattern type (pass context for calibration)
    patterns.extend(detect_sustained_demand(signals, length_factor, script_contrast))
    patterns.extend(detect_limited_recovery(signals, script_contrast))
    patterns.extend(detect_repetition(signals, features, script_contrast))  # Now with features
    patterns.extend(detect_surprise_cluster(signals))
    patterns.extend(detect_constructive_strain(signals, script_contrast))
    patterns.extend(detect_degenerative_fatigue(signals, script_contrast))
    
    return patterns


def compute_length_factor(total_scenes):
    """
    Compute threshold scaling based on script length.
    Same as temporal agent for consistency.
    """
    if total_scenes >= 50:
        return 1.0
    elif total_scenes >= 20:
        return 1.0 + (50 - total_scenes) / (50 - 20) * 0.5
    else:
        return 2.0


def compute_script_contrast(signals):
    """
    Calculate overall dynamic range of the script.
    
    Low-contrast scripts (minimal tonal variation) warrant lower confidence
    for detected patterns, as patterns in stable environments are less
    diagnostically meaningful.
    """
    all_signal_values = [s['attentional_signal'] for s in signals]
    
    contrast_score = max(all_signal_values) - min(all_signal_values)
    
    # Normalize to 0-1 range
    normalized_contrast = min(1.0, contrast_score / 2.0)
    
    return {
        'contrast_score': contrast_score,
        'normalized_contrast': normalized_contrast,
        'is_low_contrast': contrast_score < 0.8,  # More lenient (was 0.5)
        'is_high_contrast': contrast_score > 2.0  # More strict (was 1.5)
    }


def compute_feature_diversity(window_features):
    """
    Calculate how much narrative function changes across scenes.
    
    Returns: Diversity score (0.0 = identical, 1.0 = highly varied)
    
    Used to distinguish perceptual similarity (same tone/location)
    from structural redundancy (same narrative purpose).
    """
    if len(window_features) < 2:
        return 0.0
    
    # 1. Character Set Changes
    character_counts = [
        f['referential_load']['active_character_count']
        for f in window_features
    ]
    # Normalize by max expected change
    char_variance = sum(
        abs(character_counts[i] - character_counts[i+1])
        for i in range(len(character_counts) - 1)
    ) / (len(window_features) * 5.0)
    
    # 2. Dialogue vs Action Balance Shift
    dialogue_ratios = [
        f['dialogue_dynamics']['turn_velocity']
        for f in window_features
    ]
    ratio_changes = sum(
        abs(dialogue_ratios[i] - dialogue_ratios[i+1])
        for i in range(len(dialogue_ratios) - 1)
    ) / len(dialogue_ratios)
    
    # 3. Structural Boundary Presence
    boundary_scores = [
        f['structural_change']['event_boundary_score']
        for f in window_features
    ]
    boundary_diversity = (max(boundary_scores) - min(boundary_scores)) / 100.0
    
    # 4. Information Density Change (sentence count variation)
    sentence_counts = [
        f['linguistic_load']['sentence_count']
        for f in window_features
    ]
    if len(sentence_counts) > 1:
        mean_sentences = sum(sentence_counts) / len(sentence_counts)
        density_variance = sum(
            abs(s - mean_sentences) for s in sentence_counts
        ) / (len(sentence_counts) * max(1, mean_sentences))
    else:
        density_variance = 0.0
    
    # Aggregate (weighted)
    diversity_score = (
        0.3 * char_variance +
        0.25 * ratio_changes +
        0.25 * boundary_diversity +
        0.2 * density_variance
    )
    
    return min(1.0, diversity_score)


def detect_sustained_demand(signals, length_factor=1.0, script_contrast=None):
    """Detect sustained high attentional demand across multiple scenes"""
    patterns = []
    
    # Scale threshold by script length (short scripts get higher tolerance)
    # Increased base from 0.4 to 0.6 for more conservative detection
    DEMAND_THRESHOLD = 0.6 * length_factor
    
    in_pattern = False
    pattern_start = None
    
    for i, sig in enumerate(signals):
        if sig['attentional_signal'] > DEMAND_THRESHOLD:
            if not in_pattern:
                pattern_start = i
                in_pattern = True
        else:
            if in_pattern:
                # End of pattern
                pattern_end = i - 1
                if pattern_end - pattern_start + 1 >= MIN_PERSISTENCE_SCENES:
                    confidence = compute_confidence(
                        signals[pattern_start:pattern_end+1], 
                        'sustained',
                        script_contrast
                    )
                    patterns.append({
                        'pattern_type': 'sustained_attentional_demand',
                        'scene_range': [pattern_start, pattern_end],
                        'confidence': confidence,
                        'supporting_signals': ['high_signal_persistence']
                    })
                in_pattern = False
    
    # Handle pattern extending to end
    if in_pattern and len(signals) - pattern_start >= MIN_PERSISTENCE_SCENES:
        confidence = compute_confidence(
            signals[pattern_start:], 
            'sustained',
            script_contrast
        )
        patterns.append({
            'pattern_type': 'sustained_attentional_demand',
            'scene_range': [pattern_start, len(signals) - 1],
            'confidence': confidence,
            'supporting_signals': ['high_signal_persistence']
        })
    
    return patterns


def detect_limited_recovery(signals, script_contrast=None):
    """Detect periods with limited recovery opportunities"""
    patterns = []
    
    # Look for low recovery credits over multiple scenes
    # Reduced threshold from 0.1 to 0.05 for more conservative detection
    LOW_RECOVERY_THRESHOLD = 0.05
    
    low_recovery_count = 0
    pattern_start = None
    
    for i, sig in enumerate(signals):
        if sig['recovery_credit'] < LOW_RECOVERY_THRESHOLD:
            if low_recovery_count == 0:
                pattern_start = i
            low_recovery_count += 1
        else:
            if low_recovery_count >= MIN_PERSISTENCE_SCENES:
                confidence = compute_confidence(
                    signals[pattern_start:i], 
                    'limited_recovery',
                    script_contrast
                )
                patterns.append({
                    'pattern_type': 'limited_recovery',
                    'scene_range': [pattern_start, i - 1],
                    'confidence': confidence,
                    'supporting_signals': ['low_recovery_credits']
                })
            low_recovery_count = 0
    
    return patterns


def detect_repetition(signals, features=None, script_contrast=None):
    """
    Detect repetitive STRUCTURE, not just similar tone.
    
    Requires both effort similarity AND functional similarity.
    """
    patterns = []
    
    # Look for runs of similar instantaneous effort
    if len(signals) < MIN_PERSISTENCE_SCENES:
        return patterns
    
    # Check for runs of similar instantaneous effort
    EFFORT_SIMILARITY_THRESHOLD = 0.1
    DIVERSITY_THRESHOLD = 0.2  # Below this = truly repetitive
    
    for start in range(len(signals) - MIN_PERSISTENCE_SCENES + 1):
        window_signals = signals[start:start + MIN_PERSISTENCE_SCENES]
        efforts = [s['instantaneous_effort'] for s in window_signals]
        
        # Check if efforts are similar
        mean_effort = sum(efforts) / len(efforts)
        effort_variance = sum((e - mean_effort) ** 2 for e in efforts) / len(efforts)
        
        # NEW: Also check functional diversity if features available
        diversity = 1.0  # Default: assume diverse (no false positive)
        if features and len(features) > start + MIN_PERSISTENCE_SCENES:
            window_features = features[start:start + MIN_PERSISTENCE_SCENES]
            diversity = compute_feature_diversity(window_features)
        
        # Only flag if BOTH effort AND function are similar
        if effort_variance < EFFORT_SIMILARITY_THRESHOLD and diversity < DIVERSITY_THRESHOLD:
            # NEW: Calculate repetition density for confidence escalation
            repetition_density = {
                'is_early': start == 0,  # Repetition from scene 0
                'effort_variance': effort_variance,
                'diversity_score': diversity,
                'is_extreme': effort_variance < 0.05 and diversity < 0.1  # Very tight repetition
            }
            
            confidence = compute_confidence(
                window_signals, 
                'repetition',
                script_contrast,
                repetition_density=repetition_density  # NEW
            )
            patterns.append({
                'pattern_type': 'repetition',
                'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                'confidence': confidence,
                'supporting_signals': [
                    'low_effort_variance',
                    'low_functional_diversity'  # NEW
                ]
            })
            break  # Only report first instance
    
    return patterns


def detect_surprise_cluster(signals):
    """Detect clusters of high-boundary scenes"""
    patterns = []
    
    # This would require structural_change data from features
    # For now, stub (would need to pass features through)
    
    return patterns


def detect_constructive_strain(signals, script_contrast=None):
    """Detect high demand WITH recovery and stability (descriptive only)"""
    patterns = []
    
    # Look for high signal with recovery present
    HIGH_SIGNAL = 0.6
    MIN_RECOVERY = 0.2
    
    for start in range(len(signals) - MIN_PERSISTENCE_SCENES + 1):
        window = signals[start:start + MIN_PERSISTENCE_SCENES]
        
        avg_signal = sum(s['attentional_signal'] for s in window) / len(window)
        avg_recovery = sum(s['recovery_credit'] for s in window) / len(window)
        
        if avg_signal > HIGH_SIGNAL and avg_recovery > MIN_RECOVERY:
            confidence = compute_confidence(
                window, 
                'constructive',
                script_contrast
            )
            patterns.append({
                'pattern_type': 'constructive_strain',
                'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                'confidence': confidence,
                'supporting_signals': ['high_demand_with_recovery']
            })
            break
    
    return patterns


def detect_degenerative_fatigue(signals, script_contrast=None):
    """Detect drift/collapse patterns (descriptive only)"""
    patterns = []
    
    # Look for upward drift in signal without recovery
    if len(signals) < MIN_PERSISTENCE_SCENES:
        return patterns
    
    for start in range(len(signals) - MIN_PERSISTENCE_SCENES + 1):
        window = signals[start:start + MIN_PERSISTENCE_SCENES]
        
        # Check for monotonic increase
        is_increasing = all(
            window[i+1]['attentional_signal'] >= window[i]['attentional_signal']
            for i in range(len(window) - 1)
        )
        
        if is_increasing:
            avg_recovery = sum(s['recovery_credit'] for s in window) / len(window)
            if avg_recovery < 0.1:  # Very low recovery
                confidence = compute_confidence(
                    window, 
                    'degenerative',
                    script_contrast
                )
                patterns.append({
                    'pattern_type': 'degenerative_fatigue',
                    'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                    'confidence': confidence,
                    'supporting_signals': ['monotonic_increase_low_recovery']
                })
                break
    
    return patterns


def compute_confidence(window_signals, pattern_context, script_contrast=None, repetition_density=None):
    """
    Compute confidence conservatively.
    
    Confidence can only DECREASE, never increase.
    Based on signal variance, recovery noise, script-level contrast, and repetition density.
    """
    # Base confidence - reduced from 0.8 to 0.7 for more conservative starting point
    base_confidence = 0.7
    
    # === REPETITION DENSITY ESCALATION ===
    # NEW: Boost confidence for truly repetitive patterns (early + extreme similarity)
    if repetition_density:
        if repetition_density['is_extreme']:
            # Extreme repetition (variance < 0.05, diversity < 0.1)
            base_confidence += 0.25  # Escalate to high confidence
        elif repetition_density['is_early'] and repetition_density['diversity_score'] < 0.15:
            # Early-script repetition with very low diversity
            base_confidence += 0.15  # Escalate to medium-high
    
    # Reduce confidence for low-contrast scripts
    # Patterns in stable environments are less diagnostically meaningful
    # BUT: Don't penalize if repetition density is high (genuine redundancy)
    if script_contrast and not (repetition_density and repetition_density['is_extreme']):
        if script_contrast['is_low_contrast']:
            base_confidence -= 0.2  # Reduced penalty from 0.3
        elif script_contrast['normalized_contrast'] < 0.7:
            base_confidence -= 0.15  # Reduced penalty from 0.2
    
    # Decrease based on variance
    signals_values = [s['attentional_signal'] for s in window_signals]
    mean_signal = sum(signals_values) / len(signals_values)
    variance = sum((s - mean_signal) ** 2 for s in signals_values) / len(signals_values)
    
    # High variance reduces confidence
    # UNLESS it's repetition (variance already checked separately)
    if not repetition_density:
        if variance > 0.2:
            base_confidence -= 0.3
        elif variance > 0.1:
            base_confidence -= 0.2
    
    # Small window reduces confidence
    if len(window_signals) < MIN_PERSISTENCE_SCENES + 2:
        base_confidence -= 0.15  # Increased penalty from 0.1
    
    # Map to discrete bands
    if base_confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return 'high'
    elif base_confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
        return 'medium'
    else:
        return 'low'

