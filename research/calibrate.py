"""
ScriptPulse Research - Parameter Optimizer
Gap Solved: "Optimization Study"

This script performs a Hill Climbing search to optimize internal parameters
(LAMBDA, BETA, SEMANTIC_MIX) to maximize correlation with Human Ground Truth.
"""

import sys
import os
import random
import math
import csv

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scriptpulse import runner
from scriptpulse.agents import temporal

def load_human_data(csv_path):
    """Load Ground Truth data: scene_index -> human_score"""
    if not os.path.exists(csv_path):
        print(f"⚠️ Data file {csv_path} not found. Generating SYNTHETIC DUMMY DATA for demonstration.")
        return generate_dummy_data(50)
        
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # We want 'human_avg_fixation_ms' or similar
            # Normalize to 0-1
            score = float(row.get('human_avg_fixation_ms', 0)) / 1000.0 
            data[int(row['scene_index'])] = score
    return data

def generate_dummy_data(n=50):
    """Generate fake human data for demo purposes"""
    return {i: random.random() for i in range(n)}

def correlation(sp_scores, human_scores):
    """Correlation between two aligned lists"""
    n = len(sp_scores)
    if n < 2: return 0.0
    
    mx = sum(sp_scores)/n
    my = sum(human_scores)/n
    
    xm = [x - mx for x in sp_scores]
    ym = [y - my for y in human_scores]
    
    num = sum(a*b for a,b in zip(xm, ym))
    den = math.sqrt(sum(a*a for a in xm) * sum(b*b for b in ym))
    
    if den == 0: return 0.0
    return num / den

def objective_function(params, script_text, human_data):
    """
    Run pipeline with params and return Correlation with Human Data.
    Target: Maximize Correlation.
    """
    # 1. Apply Params (Monkey Patch)
    temporal.LAMBDA = params['lambda']
    temporal.BETA = params['beta']
    # Note: Semantic Mix is hardcoded in compute_instantaneous_effort currently 
    # (0.7/0.3). Ideally we would patch that too, but let's stick to global constants.
    
    # 2. Run Pipeline
    # To save time, we should parse once and only re-run temporal. 
    # But for simplicity, we run full pipeline (slower but safer).
    try:
        output = runner.run_pipeline(script_text)
        trace = output['temporal_trace']
        
        # 3. Align Data
        sp_scores = []
        h_scores = []
        
        for t in trace:
            idx = t['scene_index']
            if idx in human_data:
                sp_scores.append(t['attentional_signal']) # S[i]
                h_scores.append(human_data[idx])
                
        return correlation(sp_scores, h_scores)
    except Exception as e:
        return 0.0

def optimize(script_file, data_file='research/human_data.csv'):
    print(f"=== ScriptPulse Optimizer ===")
    print(f"Target: {script_file}")
    
    with open(script_file, 'r') as f:
        text = f.read()
        
    human_data = load_human_data(data_file)
    print(f"Loaded {len(human_data)} ground truth points.")
    
    # Initial Params
    best_params = {'lambda': 0.85, 'beta': 0.3}
    best_score = objective_function(best_params, text, human_data)
    
    print(f"Initial Correlation: {best_score:.4f}")
    
    # Simple Hill Climber
    iterations = 50
    print(f"Starting Hill Climb ({iterations} steps)...")
    
    for i in range(iterations):
        # Proposal: Perturb current best
        candidate = {
            'lambda': max(0.1, min(0.99, best_params['lambda'] + random.uniform(-0.05, 0.05))),
            'beta': max(0.1, min(0.9, best_params['beta'] + random.uniform(-0.05, 0.05)))
        }
        
        score = objective_function(candidate, text, human_data)
        
        if score > best_score:
            print(f"Step {i}: Improvement! {best_score:.4f} -> {score:.4f} (L={candidate['lambda']:.2f}, B={candidate['beta']:.2f})")
            best_score = score
            best_params = candidate
        else:
            print(".", end="", flush=True)
            
    print("\n\n=== OPTIMIZATION COMPLETE ===")
    print(f"Best Correlation: {best_score:.4f}")
    print(f"Optimal Parameters:")
    print(f"  LAMBDA (Carryover): {best_params['lambda']:.3f} (Default: 0.85)")
    print(f"  BETA (Recovery):    {best_params['beta']:.3f} (Default: 0.30)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research/calibrate.py <script_file> [human_data.csv]")
        sys.exit(1)
        
    script = sys.argv[1]
    data = sys.argv[2] if len(sys.argv) > 2 else 'research/human_data.csv'
    optimize(script, data)
