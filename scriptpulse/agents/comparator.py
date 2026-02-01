"""
ScriptPulse Comparator Agent (HCI Research Layer)
Gap Solved: "Normative Bias" & "Longitudinal Intervention"

Capabilities:
1. Reference Mode: Compare User Script vs Target Script (e.g. "Pulp Fiction").
   Uses Dynamic Time Warping (DTW) to calculate "Stylistic Distance" independent of length.
2. Longitudinal Delta: Compare Run A vs Run B to measure "Optimization Gain".
"""

import math

def compare_to_reference(user_trace, reference_trace):
    """
    Compare user's pulse line against a reference script's pulse line.
    Returns Stylistic Distance (DTW Score).
    """
    if not user_trace or not reference_trace:
        return {'distance': 0.0, 'similarity': 0.0}
        
    # Extract just the signal values (Attentional Signal or Effort)
    # user_trace is list of dicts from runner result
    u_sig = [frame['attentional_signal'] for frame in user_trace]
    r_sig = [frame['attentional_signal'] for frame in reference_trace]
    
    # Calculate DTW Distance
    distance = dtw_distance(u_sig, r_sig)
    
    # Normalize Distance by length to get "Average Error per Scene"
    # This allows comparing long scripts vs short scripts approx.
    norm_distance = distance / max(len(u_sig), len(r_sig))
    
    # Invert for Similarity (0.0 to 1.0)
    # Heuristic: Dist > 1.0 per scene is very different. Dist 0.1 is very close.
    similarity = max(0.0, 1.0 - norm_distance)
    
    return {
        'stylistic_distance': round(norm_distance, 4),
        'stylistic_similarity': round(similarity, 4),
        'interpretation': interpret_distance(norm_distance)
    }

def compare_longitudinal(current_run, benefits_run):
    """
    Compare Current Run vs Previous Run (Delta).
    Returns change metrics.
    """
    curr = current_run.get('temporal_trace', [])
    prev = benefits_run.get('temporal_trace', [])
    
    if not curr or not prev:
        return {}
    
    # 1. Total Load Change (Sum of Strain)
    curr_load = sum(f['attentional_signal'] for f in curr)
    prev_load = sum(f['attentional_signal'] for f in prev)
    
    delta_load = curr_load - prev_load
    pct_change = (delta_load / prev_load) * 100 if prev_load > 0 else 0.0
    
    # 2. Peak Strain Change
    curr_peak = max(f['attentional_signal'] for f in curr) if curr else 0
    prev_peak = max(f['attentional_signal'] for f in prev) if prev else 0
    
    # 3. Fatigue Event Count
    curr_fatigue = sum(1 for f in curr if f['fatigue_state'] in ['high', 'extreme'])
    prev_fatigue = sum(1 for f in prev if f['fatigue_state'] in ['high', 'extreme'])
    
    return {
        'load_change_pct': round(pct_change, 1),
        'peak_strain_delta': round(curr_peak - prev_peak, 2),
        'fatigue_events_delta': curr_fatigue - prev_fatigue,
        'improved': delta_load < 0 # Assuming reduction is "improvement" for typical use
    }

def dtw_distance(s1, s2):
    """
    Compute Dynamic Time Warping distance between two sequences.
    Pure Python implementation of O(NM) matrix.
    Using Euclidean distance as local cost.
    """
    n, m = len(s1), len(s2)
    dtw = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    dtw[0][0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(s1[i-1] - s2[j-1])
            # Take minimum of insertion, deletion, match
            dtw[i][j] = cost + min(dtw[i-1][j],    # Insertion
                                   dtw[i][j-1],    # Deletion
                                   dtw[i-1][j-1])  # Match
                                   
    return dtw[n][m]

def interpret_distance(d):
    if d < 0.1: return "Stylistic Twin (Very Close)"
    if d < 0.25: return "Similar Rhythm"
    if d < 0.5: return "Distinct Variance"
    return "Completely Different Style"
