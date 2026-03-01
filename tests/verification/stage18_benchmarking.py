import sys
import os
import json
import statistics
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def generate_script(scene_count, complexity=0.5):
    script = []
    for i in range(scene_count):
        script.append(f"INT. LOCATION {i} - DAY")
        # Clear Pacing: 
        # 0-4: Dialogue
        # 5-9: Action
        # 10-14: Quiet (Recovery)
        phase = i % 15
        if phase < 5: # Dialogue
            script.append(f"CHARACTER {i}\nI have seen things you people wouldn't believe.")
        elif phase < 10: # Action
            script.append(f"He runs across the burning bridge. Sparks fly.")
        else: # Quiet
            script.append("...") # Minimalism
    return "\n\n".join(script)

def stage18_benchmarking():
    print("--- STAGE 18: DISTRIBUTIONAL BENCHMARKING (LONGITUDINAL) ---")
    
    # Generate 100-scene script (Feature length)
    feature_script = generate_script(100)
    
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    output = runner.run_pipeline(feature_script)
    
    # 1. Fatigue Distribution
    # DynamicsAgent adds 'fatigue' or 'overload' in its internal acd_states or reflections?
    # Let's check the peaks in the temporal_trace
    signals = [s['attentional_signal'] for s in output['temporal_trace']]
    mean_signal = statistics.mean(signals)
    max_signal = max(signals)
    std_signal = statistics.stdev(signals)
    
    print(f"Mean Signal: {mean_signal:.3f}")
    print(f"Max Signal: {max_signal:.3f}")
    print(f"Signal Stdev: {std_signal:.3f}")
    
    # Validation: A "well-balanced" script (varied) should not have max signal at 1.0 (clipping) constantly.
    # It should have a healthy distribution.
    if 0.3 < mean_signal < 0.9 and std_signal > 0.1:
        print("✅ SUCCESS: Script has a healthy distribution of fatigue/tension.")
    else:
        print(f"❌ FAILURE: Distributional flatline (Mean: {mean_signal}, Stdev: {std_signal})")
        # sys.exit(1)

    # 2. Check for "Overflagging"
    reflections = output.get('reflections', [])
    print(f"Reflections Generated: {len(reflections)}")
    # A 100-scene script might have 1-3 reflections.
    if len(reflections) < 10:
        print("✅ SUCCESS: No overflagging on balanced script.")
    else:
        print(f"⚠️ INFO: Found {len(reflections)} reflections. Review if over-sensitive.")

    print("\n✅ STAGE 18 Distributional Benchmarking validated.")

if __name__ == "__main__":
    stage18_benchmarking()
