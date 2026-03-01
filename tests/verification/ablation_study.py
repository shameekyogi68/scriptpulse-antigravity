"""
ScriptPulse v14.0 Ablation Study Harness
(Consolidated Agent Architecture)
"""

import sys
import os
import json
import statistics

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def run_ablation_study():
    print("=== ScriptPulse v14.0 Ablation Study ===\n")
    
    # Create synthetic test script if not exists
    script_text = """
INT. OFFICE - DAY
JOHN is working.
MARY arrives.
MARY
Where is the report?
JOHN
I'm working on it.

INT. OFFICE - NIGHT
John is still working. He looks exhausted.
MARY
Go home John.
JOHN
I can't.
""" * 8 # 16 scenes

    # Define Configurations
    studies = {
        "Baseline (Full v14)": {}, 
        "No TAM (Microdynamics)": {"disable_tam": True},
        "No ACD (Collapse/Drift)": {"disable_acd": True},
        "No SSF (Silence)": {"disable_ssf": True},
        "No LRF (Fatigue Reserve)": {"disable_lrf": True}
    }
    
    results = {}
    
    # Ensure Heuristics Mode for consistency in ablation (determinism)
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    
    for name, config in studies.items():
        print(f"-> Running: {name}")
        
        output = runner.run_pipeline(script_text, ablation_config=config)
        
        temporal_trace = output.get('temporal_trace', [])
        reflections = output.get('reflections', [])
        
        if not temporal_trace:
             print(f"   ❌ ERROR: No temporal trace returned.")
             continue
             
        avg_effort = statistics.mean([s['instantaneous_effort'] for s in temporal_trace])
        avg_signal = statistics.mean([s['attentional_signal'] for s in temporal_trace])
        alert_count = len(reflections)
        
        # Check if SSF was active (silence explanation)
        silence_exp = output.get('silence_explanation', 'N/A')
        
        results[name] = {
            'avg_effort': avg_effort,
            'avg_signal': avg_signal,
            'alert_count': alert_count,
            'silence_exp': silence_exp if silence_exp else 'None'
        }
    
    # === REPORT ===
    print("\n=== Ablation Results ===")
    print(f"{'Configuration':<30} | {'Avg E[i]':<10} | {'Avg S[t]':<10} | {'Alerts':<8} | {'Silence Status'}")
    print("-" * 100)
    for name, metrics in results.items():
        print(f"{name:<30} | {metrics['avg_effort']:.4f}     | {metrics['avg_signal']:.4f}     | {metrics['alert_count']:<8} | {metrics['silence_exp'][:40]}...")

    # Validation Logic
    # 1. No TAM should change effort (TAM adds modifiers)
    # 2. No LRF should change signal (LRF adds discharge)
    # 3. No ACD should change alert count if it was relevant, or at least be processed differently.
    
    # === IEEE CONTROL EXPERIMENTS ===
    print("\n--- IEEE CONTROL EXPERIMENTS ---")
    controls = {
        "Control 4.1: Entropy (Random)": "INT. OFFICE - DAY\n" + "Blue sky dog runs apple banana.\n" * 50,
        "Control 4.2: Flat (Monotony)": "INT. OFFICE - DAY\n" + "He sits. He waits. Nothing happens.\n" * 50
    }
    
    for name, text in controls.items():
        print(f"-> Running: {name}")
        output = runner.run_pipeline(text)
        temporal_trace = output.get('temporal_trace', [])
        avg_signal = statistics.mean([s['attentional_signal'] for s in temporal_trace])
        
        # Check ACD states
        acd_states = [s.get('primary_state', 'stable') for s in output.get('temporal_trace', [])]
        drift_count = acd_states.count('drift')
        collapse_count = acd_states.count('collapse')
        
        print(f"   Avg Signal: {avg_signal:.4f} | Drift/Collapse: {drift_count}/{collapse_count}")
        
    print("\nAblation Study Done.")

if __name__ == "__main__":
    run_ablation_study()
