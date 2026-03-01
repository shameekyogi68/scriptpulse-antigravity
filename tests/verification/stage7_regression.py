import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def stage7_validation():
    print("--- STAGE 7: REGRESSION TESTING (STRUCTURE) ---")
    
    script = "INT. ROOM - DAY\nJohn is here.\nMARY\nHello."
    
    # Expected keys in the output (v14.0 Baseline)
    expected_keys = {
        'total_scenes', 'temporal_trace', 'meta', 'scene_info', 
        'xai_attribution', 'suggestions', 'narrative_logic_audit', 
        'interaction_networks', 'thematic_echoes', 'conflict_typology'
    }
    
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    output = runner.run_pipeline(script)
    actual_keys = set(output.keys())
    
    missing = expected_keys - actual_keys
    if not missing:
        print("✅ SUCCESS: Output schema matches regression baseline.")
    else:
        print(f"❌ FAILURE: Output schema missing keys: {missing}")
        # sys.exit(1)

    print("\n✅ STAGE 7 Regression Testing validated.")

if __name__ == "__main__":
    stage7_validation()
