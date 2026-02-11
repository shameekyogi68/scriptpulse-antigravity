
import math
import statistics

def run(input_data):
    """
    Calculates the 95% Confidence Interval for the Attentional Signal.
    
    Uncertainty Sources:
    1. Parse Confidence (Regex mismatches)
    2. Entropy (Information density ambiguity)
    3. Structural Volatility (Rapid changes in features)
    
    Returns:
        List of dicts with 'sigma' (standard deviation) and 'confidence_interval'.
    """
    temporal_signals = input_data.get('temporal_signals', [])
    features = input_data.get('features', [])
    
    if not temporal_signals or not features:
        return []
        
    uncertainty_outputs = []
    
    # Rolling window for volatility
    window_size = 3
    
    for i, signal_data in enumerate(temporal_signals):
        s_val = signal_data['attentional_signal']
        feat = features[i]
        
        # --- Source 1: Entropy (Ambiguity) ---
        # High entropy is good for quality, but bad for predictive certainty.
        # If entropy > 4.5 (very dense), uncertainty increases.
        entropy = feat.get('entropy_score', 0.0)
        u_entropy = max(0.0, (entropy - 3.0) * 0.05) 
        
        # --- Source 2: Micro-Structure Variance (Parse Noise) ---
        # If line lengths vary wildly, regex might be missing beats.
        micro = feat.get('micro_structure', [])
        if micro:
            lengths = [m['word_count'] for m in micro]
            if len(lengths) > 1:
                u_micro = statistics.stdev(lengths) / 50.0  # Normalize
            else:
                u_micro = 0.1
        else:
            u_micro = 0.2 # High uncertainty if no micro data
            
        # --- Source 3: Volatility (Temporal Instability) ---
        # If the signal is jumping significantly, our confidence in the specific scalar drops
        if i >= window_size:
            recent_vals = [t['attentional_signal'] for t in temporal_signals[i-window_size:i]]
            u_volatility = statistics.stdev(recent_vals) if len(recent_vals) > 1 else 0.0
        else:
            u_volatility = 0.0
            
        # Composite Uncertainty (Sigma)
        # Baseline uncertainty = 0.05
        sigma = 0.05 + (0.3 * u_entropy) + (0.2 * u_micro) + (0.5 * u_volatility)
        
        # Cap sigma to reasonable bounds
        sigma = min(sigma, 0.25)
        
        uncertainty_outputs.append({
            'scene_index': signal_data['scene_index'],
            'signal_mean': s_val,
            'sigma': round(sigma, 3),
            'ci_upper': round(s_val + 1.96 * sigma, 3),
            'ci_lower': round(max(0, s_val - 1.96 * sigma), 3),
            'confidence_score': round(1.0 - (sigma * 2), 2) # 0.0 - 1.0 confidence
        })
        
    return uncertainty_outputs
