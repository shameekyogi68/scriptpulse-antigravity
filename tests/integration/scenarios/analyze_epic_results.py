import json
import numpy as np

def analyze_results():
    # 1. Load Data (Robust-ish)
    with open('tests/scenarios/epic_output.json', 'r') as f:
        content = f.read()
        json_start = content.find('{')
        data = json.loads(content[json_start:])
        
    scenes = data['temporal_trace']
    count = len(scenes)
    print(f"Total Scenes Analyzed: {count}")
    
    efforts = [s.get('instantaneous_effort', 0) for s in scenes]
    
    idx_25 = int(count * 0.25)
    idx_75 = int(count * 0.75)
    idx_90 = int(count * 0.90)
    
    setup_avg = np.mean(efforts[:idx_25])
    conflict_avg = np.mean(efforts[idx_25:idx_75])
    climax_avg = np.mean(efforts[idx_75:idx_90])
    res_avg = np.mean(efforts[idx_90:])
    
    print("-" * 30)
    print("NARRATIVE ARC VALIDATION")
    print("-" * 30)
    print(f"Setup Avg Effort:      {setup_avg:.3f}")
    print(f"Conflict Avg Effort:   {conflict_avg:.3f}")
    print(f"Climax Avg Effort:     {climax_avg:.3f}")
    print(f"Resolution Avg Effort: {res_avg:.3f}")
    
    # Checks
    print("-" * 30)
    print("LOGIC CHECKS")
    if conflict_avg > setup_avg:
        print("[PASS] Conflict > Setup")
    else:
        print("[FAIL] Conflict <= Setup")
        
    if climax_avg > setup_avg:
        print("[PASS] Climax > Setup")
    else:
        print("[FAIL] Climax <= Setup")

    # Check Execution Mode
    meta = data.get('meta', {})
    print("-" * 30)
    print(f"Execution Mode: {meta.get('execution_mode')}")
    print(f"Version: {meta.get('version')}")

if __name__ == "__main__":
    analyze_results()
