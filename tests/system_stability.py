"""
ScriptPulse v5.0 Stability & Determinism Check

Verifies that the system produces bitwise identical outputs for identical inputs,
a requirement for IEEE reproducibility.
"""

import sys
import os
import hashlib
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse import runner

def run_stability_check():
    print("=== ScriptPulse v5.0 Determinism Check ===\n")
    
    script_path = "test_17_scenes.fountain"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        return

    with open(script_path, 'r') as f:
        text = f.read()

    iterations = 10
    hashes = []
    
    print(f"Running {iterations} iterations...")
    
    for i in range(iterations):
        # Run full pipeline
        # Use default lens (Viewer)
        output = runner.run_pipeline(text, lens='viewer')
        
        # Serialize to JSON string with sort_keys=True
        # This converts the complex dict to a canonical string representation
        # We exclude 'timestamp' or similar volatile fields if they existed (none in v5 core)
        output_str = json.dumps(output, sort_keys=True)
        
        # Compute Hash
        run_hash = hashlib.sha256(output_str.encode('utf-8')).hexdigest()
        hashes.append(run_hash)
        
        print(f"Run {i+1}: {run_hash[:8]}...")
        
    # Verification
    first_hash = hashes[0]
    all_match = all(h == first_hash for h in hashes)
    
    if all_match:
        print("\nPASS: System is strictly deterministic.")
        print(f"Determinism Index: 1.0 (100%)")
    else:
         print("\nFAIL: Non-deterministic behavior detected.")
         mismatches = sum(1 for h in hashes if h != first_hash)
         print(f"Mismatches: {mismatches}/{iterations}")

if __name__ == "__main__":
    run_stability_check()
