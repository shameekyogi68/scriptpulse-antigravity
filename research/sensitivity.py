"""
ScriptPulse Research - Parameter Sensitivity Analysis
Gap Solved: "Are these magic numbers?"

This script proves system robustness (stability) by adding noise
to the core constants and measuring output variance.

IEEE Requirement: The system should be STABLE under small parameter perturbations.
"""

import sys
import os
import json
import statistics
import random
import copy

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scriptpulse import runner
from scriptpulse.agents import temporal

def run_sensitivity_sweep(script_file, iterations=20, perturbation=0.1):
    """
    Run the pipeline multiple times with jittered constants.
    
    Args:
        iterations: Number of runs
        perturbation: +/- fraction to jitter constants (e.g. 0.1 = 10%)
    """
    with open(script_file, 'r') as f:
        text = f.read()
    
    print(f"Analyzing {os.path.basename(script_file)}...")
    print(f"Running {iterations} iterations with +/- {perturbation*100}% parameter noise...")
    
    # Store standard constants
    STD_RECOVERY = temporal.BASE_RECOVERY_RATE
    STD_FATIGUE = temporal.FATIGUE_THRESHOLD
    
    results = []
    
    for i in range(iterations):
        # Monkey-Patch Constants with Noise
        noise_r = 1.0 + random.uniform(-perturbation, perturbation)
        noise_f = 1.0 + random.uniform(-perturbation, perturbation)
        
        temporal.BASE_RECOVERY_RATE = STD_RECOVERY * noise_r
        temporal.FATIGUE_THRESHOLD = STD_FATIGUE * noise_f
        
        # Run Pipeline
        # Note: We must disable MRCS caching or ensure we get fresh run
        # Since MRCS uses random seeds, we expect some jitter anyway.
        # But here we are forcing parameter jitter.
        
        output = runner.run_pipeline(text)
        trace = output['temporal_trace']
        
        # Metric: Average "Net Tension" (S) across script
        avg_strain = statistics.mean([t['strain'] for t in trace])
        results.append(avg_strain)
        
        # Progress dot
        print(".", end="", flush=True)
        
    print("\n")
    
    # Restore Constants
    temporal.BASE_RECOVERY_RATE = STD_RECOVERY
    temporal.FATIGUE_THRESHOLD = STD_FATIGUE
    
    # Analyze Variance
    mean_s = statistics.mean(results)
    stdev_s = statistics.stdev(results)
    cv = stdev_s / mean_s # Coefficient of Variation
    
    print("--- RESULTS ---")
    print(f"Mean Strain: {mean_s:.4f}")
    print(f"Std Dev:     {stdev_s:.4f}")
    print(f"Coeff Var:   {cv:.4f}")
    
    if cv < 0.2:
        print("✅ SUCCESS: System is Robust (Stable).")
        print("Interpretation: Small parameter changes do not break the model.")
    elif cv > 0.5:
        print("❌ FAILURE: System is Chaotic.")
        print("Interpretation: The model is too sensitive to magic numbers.")
    else:
        print("⚠️ NOTE: Moderate sensitivity.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research/sensitivity.py <script_file>")
        sys.exit(1)
    run_sensitivity_sweep(sys.argv[1])
