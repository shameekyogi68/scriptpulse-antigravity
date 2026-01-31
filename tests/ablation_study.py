"""
ScriptPulse v5.0 Ablation Study Harness

This script runs the analysis pipeline multiple times on the same input,
systematically disabling ("ablating") specific internal layers to measure
their contribution to the final signal.
"""

import sys
import os
import json
import copy

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse import runner, lenses
from scriptpulse.agents import temporal, tam, acd, ssf, lrf

def run_ablation_study():
    print("=== ScriptPulse v5.0 Ablation Study ===\n")
    
    # Load test script
    script_path = "test_17_scenes.fountain"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        return

    with open(script_path, 'r') as f:
        text = f.read()

    # Define Configurations
    studies = {
        "Baseline (Full v5)": {}, 
        "No TAM (Microdynamics)": {"disable_tam": True},
        "No ACD (Collapse/Drift)": {"disable_acd": True},
        "No SSF (Silence)": {"disable_ssf": True},
        "No LRF (Fatigue Reserve)": {"disable_lrf": True}
    }
    
    results = {}
    
    for name, config in studies.items():
        print(f"-> Running: {name}")
        
        # Monkey-patching / Mocking for ablation
        # Note: In a real production environment, we'd use dependency injection.
        # Here, we use a modified runner or we can rely on the fact that these
        # layers are sequential. Ideally, we'd pass an 'ablation_config' to runner.
        # Since runner doesn't support that yet, we simulate the effects by
        # manually running the pipeline parts here.
        
        # 1. Standard Pre-processing
        from scriptpulse.agents import parsing, segmentation, encoding
        parsed = parsing.run(text)
        segmented = segmentation.run(parsed)
        encoded = encoding.run({'scenes': segmented, 'lines': parsed})
        
        # Modify encoding if TAM disabled (remove micro_structure)
        if config.get("disable_tam"):
            for scene in encoded:
                if 'micro_structure' in scene:
                    del scene['micro_structure']
        
        # 2. Temporal (Supports TAM internally via passed features)
        # If TAM is disabled, we need to ensure temporal.py doesn't use it.
        # The easiest way is to mock tam.run_micro_integration to return 1.0 modifiers.
        
        original_tam_run = tam.run_micro_integration
        if config.get("disable_tam"):
            tam.run_micro_integration = lambda features, effort: {
                'effort_modifier': 1.0, 
                'recovery_modifier': 1.0, 
                'micro_fatigue_integral': 0.0
            }
            
        temporal_output = temporal.run({'features': encoded}, lens_config=lenses.get_lens('viewer'))
        
        # Restore TAM
        if config.get("disable_tam"):
            tam.run_micro_integration = original_tam_run
            
        # 3. LRF
        if not config.get("disable_lrf"):
            temporal_output = lrf.run({'temporal_signals': temporal_output, 'features': encoded})
            
        # 4. ACD
        acd_output = []
        if not config.get("disable_acd"):
             acd_output = acd.run({'temporal_signals': temporal_output, 'features': encoded})
        else:
            # Emulate empty/neutral ACD
            for s in temporal_output:
                acd_output.append({
                    'scene_index': s['scene_index'], 
                    'collapse_likelihood': 0.0, 
                    'drift_likelihood': 0.0, 
                    'primary_state': 'stable'
                })
                
        # 5. Patterns
        from scriptpulse.agents import patterns
        patterns_output = patterns.run({
            'temporal_signals': temporal_output,
            'features': encoded,
            'acd_states': acd_output
        })
        
        # 6. Intent
        from scriptpulse.agents import intent
        filtered = intent.run({'patterns': patterns_output, 'writer_intent': []})
        
        # 7. SSF
        ssf_output = {}
        if not config.get("disable_ssf"):
             ssf_output = ssf.run({
                'temporal_signals': temporal_output,
                'acd_states': acd_output,
                'surfaced_patterns': filtered['surfaced_patterns']
            })
        
        # Capture Metrics
        avg_effort = sum(s['instantaneous_effort'] for s in temporal_output) / len(temporal_output)
        avg_signal = sum(s['attentional_signal'] for s in temporal_output) / len(temporal_output)
        alert_count = len(filtered['surfaced_patterns'])
        
        results[name] = {
            'avg_effort': avg_effort,
            'avg_signal': avg_signal,
            'alert_count': alert_count,
            'silence_conf': ssf_output.get('silence_confidence', 'N/A')
        }
    
    # === REPORT ===
    print("\n=== Ablation Results ===")
    print(f"{'Configuration':<30} | {'Avg E[i]':<10} | {'Avg S[t]':<10} | {'Alerts':<8} | {'Silence'}")
    print("-" * 80)
    for name, metrics in results.items():
        print(f"{name:<30} | {metrics['avg_effort']:.4f}     | {metrics['avg_signal']:.4f}     | {metrics['alert_count']:<8} | {metrics['silence_conf']}")

    print("\nDone.")

if __name__ == "__main__":
    run_ablation_study()
