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
        
    Returns:
        List of pattern descriptors (pattern_type, scene_range, confidence)
    """
    signals = input_data.get('temporal_signals', [])
    
    if len(signals) < MIN_PERSISTENCE_SCENES:
        return []  # Cannot detect patterns with insufficient data
    
    patterns = []
    
    # Detect each pattern type
    patterns.extend(detect_sustained_demand(signals))
    patterns.extend(detect_limited_recovery(signals))
    patterns.extend(detect_repetition(signals))
    patterns.extend(detect_surprise_cluster(signals))
    patterns.extend(detect_constructive_strain(signals))
    patterns.extend(detect_degenerative_fatigue(signals))
    
    return patterns


def detect_sustained_demand(signals):
    """Detect sustained high attentional demand across multiple scenes"""
    patterns = []
    
    # Look for windows where signal remains elevated
    DEMAND_THRESHOLD = 0.4
    
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
                    confidence = compute_confidence(signals[pattern_start:pattern_end+1], 'sustained')
                    patterns.append({
                        'pattern_type': 'sustained_attentional_demand',
                        'scene_range': [pattern_start, pattern_end],
                        'confidence': confidence,
                        'supporting_signals': ['high_signal_persistence']
                    })
                in_pattern = False
    
    # Handle pattern extending to end
    if in_pattern and len(signals) - pattern_start >= MIN_PERSISTENCE_SCENES:
        confidence = compute_confidence(signals[pattern_start:], 'sustained')
        patterns.append({
            'pattern_type': 'sustained_attentional_demand',
            'scene_range': [pattern_start, len(signals) - 1],
            'confidence': confidence,
            'supporting_signals': ['high_signal_persistence']
        })
    
    return patterns


def detect_limited_recovery(signals):
    """Detect periods with limited recovery opportunities"""
    patterns = []
    
    # Look for low recovery credits over multiple scenes
    LOW_RECOVERY_THRESHOLD = 0.1
    
    low_recovery_count = 0
    pattern_start = None
    
    for i, sig in enumerate(signals):
        if sig['recovery_credit'] < LOW_RECOVERY_THRESHOLD:
            if low_recovery_count == 0:
                pattern_start = i
            low_recovery_count += 1
        else:
            if low_recovery_count >= MIN_PERSISTENCE_SCENES:
                confidence = compute_confidence(signals[pattern_start:i], 'limited_recovery')
                patterns.append({
                    'pattern_type': 'limited_recovery',
                    'scene_range': [pattern_start, i - 1],
                    'confidence': confidence,
                    'supporting_signals': ['low_recovery_credits']
                })
            low_recovery_count = 0
    
    return patterns


def detect_repetition(signals):
    """Detect repetitive effort patterns"""
    patterns = []
    
    # Look for similar effort values repeating
    if len(signals) < MIN_PERSISTENCE_SCENES:
        return patterns
    
    # Check for runs of similar instantaneous effort
    SIMILARITY_THRESHOLD = 0.1
    
    for start in range(len(signals) - MIN_PERSISTENCE_SCENES + 1):
        window = signals[start:start + MIN_PERSISTENCE_SCENES]
        efforts = [s['instantaneous_effort'] for s in window]
        
        # Check if efforts are similar
        mean_effort = sum(efforts) / len(efforts)
        variance = sum((e - mean_effort) ** 2 for e in efforts) / len(efforts)
        
        if variance < SIMILARITY_THRESHOLD:
            confidence = compute_confidence(window, 'repetition')
            patterns.append({
                'pattern_type': 'repetition',
                'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                'confidence': confidence,
                'supporting_signals': ['low_effort_variance']
            })
            break  # Only report first instance
    
    return patterns


def detect_surprise_cluster(signals):
    """Detect clusters of high-boundary scenes"""
    patterns = []
    
    # This would require structural_change data from features
    # For now, stub (would need to pass features through)
    
    return patterns


def detect_constructive_strain(signals):
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
            confidence = compute_confidence(window, 'constructive')
            patterns.append({
                'pattern_type': 'constructive_strain',
                'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                'confidence': confidence,
                'supporting_signals': ['high_demand_with_recovery']
            })
            break
    
    return patterns


def detect_degenerative_fatigue(signals):
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
                confidence = compute_confidence(window, 'degenerative')
                patterns.append({
                    'pattern_type': 'degenerative_fatigue',
                    'scene_range': [start, start + MIN_PERSISTENCE_SCENES - 1],
                    'confidence': confidence,
                    'supporting_signals': ['monotonic_increase_low_recovery']
                })
                break
    
    return patterns


def compute_confidence(window_signals, pattern_context):
    """
    Compute confidence conservatively.
    
    Confidence can only DECREASE, never increase.
    Based on signal variance and recovery noise.
    """
    # Base confidence
    confidence_score = 0.8
    
    # Decrease based on variance
    signals_values = [s['attentional_signal'] for s in window_signals]
    mean_signal = sum(signals_values) / len(signals_values)
    variance = sum((s - mean_signal) ** 2 for s in signals_values) / len(signals_values)
    
    # High variance reduces confidence
    if variance > 0.2:
        confidence_score -= 0.3
    elif variance > 0.1:
        confidence_score -= 0.2
    
    # Small window reduces confidence
    if len(window_signals) < MIN_PERSISTENCE_SCENES + 2:
        confidence_score -= 0.1
    
    # Map to discrete bands
    if confidence_score >= HIGH_CONFIDENCE_THRESHOLD:
        return 'high'
    elif confidence_score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return 'medium'
    else:
        return 'low'

