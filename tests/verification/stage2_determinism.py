import os
import sys
import json
import hashlib
import time

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def get_hash(data):
    # Standardize JSON for consistent hashing (sort keys, no extra whitespace)
    # We remove 'agent_timings' and 'wall_time_s' since they are inherently non-deterministic (timing-based)
    clean_data = json.loads(json.dumps(data))
    
    if 'meta' in clean_data:
        if 'agent_timings' in clean_data['meta']:
            del clean_data['meta']['agent_timings']
        if 'wall_time_s' in clean_data['meta']:
            del clean_data['meta']['wall_time_s']
    if 'runtime_ms' in clean_data:
        del clean_data['runtime_ms']
        
    json_str = json.dumps(clean_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def run_determinism_test():
    print("--- STAGE 2: DETERMINISM VALIDATION ---")
    
    script_path = "tests/integration/scenarios/master_test.txt"
    if not os.path.exists(script_path):
        script_text = "INT. ROOM - DAY\nJohn enters. He is angry.\nJOHN\nWhere is it?\nMARY\nI don't know."
    else:
        with open(script_path, 'r') as f:
            script_text = f.read()

    hashes = []
    iterations = 50
    print(f"Running {iterations} iterations with seed=42...")
    
    start_time = time.time()
    for i in range(iterations):
        # Clear model cache or ensure it doesn't affect state
        output = runner.run_pipeline(script_text, ablation_config={'seed': 42})
        h = get_hash(output)
        hashes.append(h)
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"Completed {i+1}/{iterations}... (Elapsed: {elapsed:.1f}s)")

    unique_hashes = set(hashes)
    print(f"\nUnique Hashes: {len(unique_hashes)}")
    
    if len(unique_hashes) == 1:
        print("✅ SUCCESS: Zero drift across 50 runs.")
    else:
        print(f"❌ FAILURE: Detected {len(unique_hashes)} different outputs.")
        # Find where it differs
        # (We could print diffs here if needed)

    # Verify seed works
    print("\nVerifying seed effect (Monte Carlo Ensemble)...")
    output_a = runner.run_pipeline(script_text, ablation_config={'seed': 42})
    output_b = runner.run_pipeline(script_text, ablation_config={'seed': 999})
    
    hash_a = get_hash(output_a)
    hash_b = get_hash(output_b)
    
    if hash_a != hash_b:
        print("✅ SUCCESS: Different seeds produce different outputs.")
    else:
        # Check if ensemble uncertainty is actually producing noise
        if 'uncertainty_quantification' in output_a and output_a['uncertainty_quantification']:
             print("❌ FAILURE: Monte Carlo ensemble results were identical for different seeds.")
        else:
             print("⚠️ INFO: Output identical, but possibly because random components were inactive.")

    # Validate reproducibility.lock against active params
    print("\nValidating reproducibility.lock vs active constants...")
    lock_path = "config/reproducibility.lock"
    if os.path.exists(lock_path):
        with open(lock_path, 'r') as f:
            lock = json.load(f)
        
        # Check seed
        if lock.get('seed') == 42:
            print("✅ lock seed matches.")
        else:
            print(f"⚠️ lock seed mismatch: {lock.get('seed')}")
    else:
        print("❌ reproducibility.lock missing.")

if __name__ == "__main__":
    run_determinism_test()
