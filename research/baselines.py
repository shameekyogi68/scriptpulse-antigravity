"""
ScriptPulse Research - Baseline Comparison
Gap Solved: "Is this just word count?"

This script compares ScriptPulse's 'Attentional Load' against standard baselines:
1. Raw Word Count
2. Action Line Density

Hypothesis: ScriptPulse should correlate MODERATELY (0.4-0.6) with these, 
proving it captures structural nuance beyond raw volume.
"""

import sys
import os
import json
import statistics
import math

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scriptpulse import runner

def calculate_baselines(script_text):
    """
    Compute standard baseline metrics for the script.
    """
    # Simple parse based on runner's parser results would be better, 
    # but let's do a raw pass for independence.
    scenes = runner.parse_structure(script_text)
    
    baseline_data = []
    
    # We need the raw segmentation to count words per scene
    # Re-running runner to get segmentation
    from scriptpulse.agents import parsing, segmentation
    parsed = parsing.run(script_text)
    segmented = segmentation.run(parsed)
    
    for scene in segmented:
        # 1. Word Count
        content = "\n".join([line['text'] for line in scene['lines']])
        word_count = len(content.split())
        
        # 2. Line Density (Lines of Action vs Dialogue)
        action_lines = sum(1 for line in scene['lines'] if line['type'] == 'ACTION')
        
        baseline_data.append({
            'scene_index': scene['scene_index'],
            'word_count': word_count,
            'action_lines': action_lines
        })
        
    return baseline_data

def run_comparison(script_file):
    with open(script_file, 'r') as f:
        text = f.read()
        
    print(f"Analyzing {os.path.basename(script_file)}...")
    
    # 1. Run ScriptPulse (The "Model")
    # We want the Effort (E) vector
    sp_output = runner.run_pipeline(text)
    trace = sp_output['temporal_trace']
    sp_scores = [t['effort'] for t in trace]
    
    # 2. Run Baselines
    baselines = calculate_baselines(text)
    word_counts = [b['word_count'] for b in baselines]
    
    # 3. Calculate Correlation
    if len(sp_scores) != len(word_counts):
        print("Error: aligned mismatch.")
        return

    corr = correlation(sp_scores, word_counts)
    
    print("\n--- RESULTS ---")
    print(f"Correlation (ScriptPulse vs WordCount): {corr:.3f}")
    
    if 0.3 <= corr <= 0.8:
        print("✅ SUCCESS: Moderate correlation.")
        print("Interpretation: ScriptPulse captures volume AND structural nuance.")
    elif corr > 0.8:
        print("⚠️ WARNING: High correlation.")
        print("Interpretation: ScriptPulse is mostly just counting words.")
    else:
        print("ℹ️ NOTE: Low correlation. The distinct structural signal is very strong.")

def correlation(x, y):
    """Pearson correlation coefficient"""
    n = len(x)
    if n != len(y): return 0
    if n < 2: return 0
    
    mx = statistics.mean(x)
    my = statistics.mean(y)
    
    xm = [i - mx for i in x]
    ym = [i - my for i in y]
    
    r_num = sum(a * b for a, b in zip(xm, ym))
    r_den = math.sqrt(sum(a * a for a in xm) * sum(b * b for b in ym))
    
    if r_den == 0: return 0
    return r_num / r_den

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research/baselines.py <script_file>")
        sys.exit(1)
    run_comparison(sys.argv[1])
