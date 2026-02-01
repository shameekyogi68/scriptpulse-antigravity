"""
ScriptPulse Biometric Lab (Empirical Research Layer)
Gap Solved: "The Synthetic Bubble"

Correlates simulated temporal traces with imported physiological data
(Heart Rate, Galvanic Skin Response, etc.) to calculate Pearson/Spearman validity.
"""

import math
import statistics

def correlate_biometrics(simulated_trace, real_data_points):
    """
    simulated_trace: List of dicts (the ScriptPulse output)
    real_data_points: List of floats (the CSV biometric data)
    
    Returns: Pearson Correlation Coefficient (-1.0 to 1.0)
    """
    if not simulated_trace or not real_data_points:
        return 0.0
        
    sim_values = [p['attentional_signal'] for p in simulated_trace]
    
    # 1. Resample Real Data to match Simulation Length
    # Assuming the real data covers the same total duration.
    # We downsample or upsample real data to match len(sim_values).
    
    resampled_real = resample_list(real_data_points, len(sim_values))
    
    # 2. Pearson Correlation
    return pearson_correlation(sim_values, resampled_real)


def resample_list(data, target_len):
    """Linear interpolation to match lengths."""
    if len(data) == target_len: return data
    if len(data) < 2: return [data[0]] * target_len
    
    resampled = []
    n = len(data)
    for i in range(target_len):
        # map i (0..target-1) to x (0..n-1)
        x = i * (n - 1) / (target_len - 1)
        k = int(x)
        t = x - k
        
        if k >= n - 1:
            val = data[-1]
        else:
            val = data[k] * (1 - t) + data[k+1] * t
            
        resampled.append(val)
    return resampled

def pearson_correlation(x, y):
    """Calculate Pearson r."""
    n = len(x)
    if n != len(y) or n < 2: return 0.0
    
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    num = 0.0
    denom_x = 0.0
    denom_y = 0.0
    
    for i in range(n):
        dx = x[i] - mean_x
        dy = y[i] - mean_y
        num += dx * dy
        denom_x += dx * dx
        denom_y += dy * dy
        
    if denom_x == 0 or denom_y == 0:
        return 0.0
        
    return num / math.sqrt(denom_x * denom_y)
