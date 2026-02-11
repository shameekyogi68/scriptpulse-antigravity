
import sys
import os
import json
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse import runner

def run_pipeline(script_path):
    print(f"\n--- Running Pipeline on {os.path.basename(script_path)} ---")
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Run pipeline
        # We need to simulate the args or call runner logic directly?
        # runner.main() expects args. Let's import the agents and run manually or modify runner to have a callable entry point that takes string/file
        # runner.run_pipeline() exists?
        # Let's check runner.py. It has a main() but also we can import run logic?
        # The runner.py viewed earlier suggests there is a flow.
        # But wait, to be safe, let's use subprocess to call the module as CLI, 
        # OR better: use the 'runner' module functions if exposed.
        # Let's assume we can call `runner.run_pipeline(script_content)` if it exists, or similar.
        # Looking at previous view_file of runner.py:
        # It has `def main():` and `if __name__ == "__main__":`.
        # It doesn't seem to expose a direct `run(text)` function easily without refactoring.
        # BUT, we can use `subprocess` to run `python -m scriptpulse.runner <file>` and capture stdout/json.
        # OR we can just import agents. 
        # Actually, let's try to import the runner's main logic if possible.
        # Ideally runner.py has `run_analysis(text)`.
        # If not, I will use subprocess for now to be safe and robust.
        
        pass 
    except Exception as e:
        print(f"Error: {e}")
        return None

def validate_master(output):
    print("Validating Master Test...")
    errors = []
    
    # Check 1: Scene Count
    if output['total_scenes'] != 4:
        errors.append(f"Scene count mismatch. Expected 4, got {output['total_scenes']}")
        
    # Check 2: Parser
    scenes = output['scene_info']
    if "INT. SAFE HOUSE" not in scenes[0]['heading']:
         errors.append("Scene 1 heading mismatch")
         
    # Check 3: Agency
    agency = output.get('agency_analysis', {}).get('agency_metrics', [])
    raj = next((c for c in agency if c['character'] == 'RAJ'), None)
    commander = next((c for c in agency if c['character'] == 'COMMANDER'), None)
    
    if not raj or not commander:
        errors.append("Agency Agent failed to detect key characters")
    
    # Check 4: Recovery
    trace = output['temporal_trace']
    last_scene = trace[-1]
    if last_scene['recovery_credit'] <= 0.1:
        errors.append(f"Recovery failed in Scene 4. R[i]={last_scene['recovery_credit']}")
        
    if not errors:
        print("[PASS] Master Test passed all checks.")
    else:
        print("[FAIL] Master Test errors:")
        for e in errors:
            print(f"  - {e}")

def validate_edge(output):
    print("Validating Edge Case...")
    # Just checking it didn't crash and found scenes
    if output['total_scenes'] < 1:
        print("[FAIL] Parser failed to find scenes in edge case.")
    else:
        print(f"[PASS] Edge Case handled. Found {output['total_scenes']} scenes.")

def validate_recovery(output):
    print("Validating Recovery Probe...")
    trace = output['temporal_trace'][0]
    if trace['instantaneous_effort'] > 0.3:
        print(f"[FAIL] High effort detected in silent field scene. E[i]={trace['instantaneous_effort']}")
    else:
        print(f"[PASS] Recovery Probe E[i]={trace['instantaneous_effort']} (Low).")

if __name__ == "__main__":
    # We will use subprocess to run the runner and caption JSON output
    import subprocess
    
    scripts = {
        'master': 'tests/scenarios/master_test.txt',
        'edge': 'tests/scenarios/edge_case.txt',
        'recovery': 'tests/scenarios/recovery.txt'
    }
    
    for name, path in scripts.items():
        if not os.path.exists(path):
            print(f"Skipping {name}: file not found.")
            continue
            
        cmd = [sys.executable, "-m", "scriptpulse.runner", path]
        try:
            # Run and capture output
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # The runner prints JSON to stdout? Or to a file?
            # Previous runs showed JSON output in stdout.
            # We need to extract the JSON part.
            output_str = result.stdout
            
            # Naive JSON extraction (find first { and last })
            try:
                start = output_str.find('{')
                end = output_str.rfind('}') + 1
                json_str = output_str[start:end]
                data = json.loads(json_str)
                
                if name == 'master':
                    validate_master(data)
                elif name == 'edge':
                    validate_edge(data)
                elif name == 'recovery':
                    validate_recovery(data)
                    
            except json.JSONDecodeError:
                print(f"[FAIL] Could not parse JSON output for {name}")
                # print(output_str) 
        except Exception as e:
             print(f"[FATAL] Wrapper failed: {e}")

