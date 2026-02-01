"""
ScriptPulse Research - Structural Template Matching
Gap Solved: "Macro-Structure Narrative Gap"

Compares the script's tension curve against canonical narrative arcs:
1. Freytag's Pyramid (Classic Tragedy/Drama)
2. Man in Hole (Vonnegut - Fall, Rise)
3. Cinderella (Rise, Fall, Rise)
4. Icarus (Rise, Fall)

Uses simplified Dynamic Time Warping (DTW) logic (Resampling Comparison) 
to output a "Structural Fidelity Score".
"""

import sys
import math
import statistics

# Canonical Templates (Normalized 0.0 to 1.0 Time, 0.0 to 1.0 Tension)
TEMPLATES = {
    'Freytag': [
        (0.0, 0.2), (0.2, 0.4), # Exposition -> Rising Action
        (0.5, 0.9), # Climax
        (0.7, 0.5), # Falling Action
        (1.0, 0.3)  # Resolution
    ],
    'Man_in_Hole': [
        (0.0, 0.5), (0.2, 0.5), # Normal
        (0.4, 0.1), (0.6, 0.1), # The Hole (Tragedy/Load) - Wait, in ScriptPulse, High Strain = Load/Trouble?
        # Actually, in Vonnegut "Good Fortune" = High Y. 
        # But in ScriptPulse "High Strain" = Trouble/Effort.
        # So "Man in Hole" (Trouble) = Spike in Strain.
        
        # ScriptPulse Mapping:
        # High Strain = Conflict/Action/Trouble.
        # Low Strain = Peace/Good Fortune.
        
        # Man in Hole (Good -> Bad -> Good)
        # Strain: Low -> High -> Low
        (0.0, 0.2), 
        (0.5, 0.8), # The Trouble
        (1.0, 0.2)
    ],
    'Cinderella': [
        (0.0, 0.8), # High Strain (Bad life)
        (0.4, 0.2), # Low Strain (Ball/Prince - Good fortune)
        (0.7, 0.8), # High Strain (Midnight/Loss)
        (1.0, 0.2)  # Low Strain (Resolution)
    ],
    'Thriller_Escalation': [
        (0.0, 0.2),
        (0.3, 0.4),
        (0.6, 0.7),
        (0.9, 1.0), # Constant Rise
        (1.0, 0.5)
    ]
}

def analyze_fidelity(pulse_trace):
    """
    Compare pulse trace (list of floats) against templates.
    Returns best match and score.
    """
    if not pulse_trace:
        return {'best_match': 'None', 'score': 0.0}
        
    scores = {}
    
    # Normalize trace to [0,1] value and [0,1] time steps
    n = len(pulse_trace)
    
    # 1. Resample templates to match trace length N to allow direct vector comparison
    # (Simple Euclidean, not full DTW for speed/dependency reasons)
    
    for name, points in TEMPLATES.items():
        template_signal = resample_template(points, n)
        
        # 2. Calculate Distance (RMSE)
        # Lower means better match
        error_sum = 0.0
        for i in range(n):
            actual = pulse_trace[i]
            target = template_signal[i]
            error_sum += (actual - target) ** 2
            
        rmse = math.sqrt(error_sum / n)
        
        # Invert to Fidelity Score (1.0 = Perfect, 0.0 = terrible)
        # RMSE of 0.5 is very bad. 0.1 is very good.
        fidelity = max(0.0, 1.0 - (rmse * 2.0))
        scores[name] = round(fidelity, 3)
        
    best = max(scores, key=scores.get)
    return {
        'best_match': best,
        'fidelity_score': scores[best],
        'all_scores': scores
    }

def resample_template(points, target_len):
    """Interpolate template definition into N points"""
    signal = []
    
    # Points is list of (time, val). Time 0..1
    # We iterate i from 0 to N-1. t = i / (N-1)
    
    for i in range(target_len):
        t = i / max(1, target_len - 1)
        
        # Find bracketing points
        # Assuming points are sorted by time
        p1 = points[0]
        p2 = points[-1]
        
        for k in range(len(points) - 1):
            if points[k][0] <= t <= points[k+1][0]:
                p1 = points[k]
                p2 = points[k+1]
                break
                
        # Linear Interpolate
        # val = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
        t1, v1 = p1
        t2, v2 = p2
        
        if t2 == t1:
            val = v1
        else:
            val = v1 + (t - t1) * (v2 - v1) / (t2 - t1)
            
        signal.append(val)
        
    return signal
