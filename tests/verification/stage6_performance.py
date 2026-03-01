import sys
import os
import time
import json
import gc

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def stage6_validation():
    print("--- STAGE 6: PERFORMANCE SCALABILITY ---")
    
    # 300 scenes script (~3000 lines)
    scene_template = "SCENE {i}\nEXT. LOCATION {i} - DAY\nAction {i} happens here. John and Mary talk for a while. They discuss the weather and the plot. It is very detailed for a synthetic script.\nJOHN\nLine {i} is important.\nMARY\nResponse {i} is even more important.\n"
    script_text = "".join(scene_template.format(i=i) for i in range(300))
    
    print(f"Testing with 300 scenes script (~3000 lines)...")
    
    # Ensure heuristics only for speed
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    
    start_time = time.time()
    
    # Perform analysis
    output = runner.run_pipeline(script_text)
    
    elapsed = time.time() - start_time
    print(f"Elapsed Time: {elapsed:.2f}s (Budget: 10.0s)")
    
    # Check scene count in output
    scenes = output.get('segmented', [])
    print(f"Processed {len(scenes)} scenes.")
    
    if elapsed < 10.0 and len(scenes) >= 300:
        print("✅ SUCCESS: Performance within budget and all scenes processed.")
    else:
        if elapsed >= 10.0:
            print("❌ FAILURE: Performance exceeded 10s budget.")
        if len(scenes) < 300:
            print(f"❌ FAILURE: Only processed {len(scenes)}/300 scenes.")
        sys.exit(1)

if __name__ == "__main__":
    stage6_validation()
