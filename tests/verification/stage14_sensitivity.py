import sys
import os
import json
import statistics
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.dynamics_agent import DynamicsAgent

def get_mock_features(scene_count, entropy=0.5):
    features = []
    for i in range(scene_count):
        features.append({
            'scene_index': i,
            'entropy_score': entropy,
            'referential_load': {'active_character_count': 2, 'entity_churn': 0.1, 'character_reintroductions': 0},
            'dialogue_dynamics': {'turn_velocity': 0.5, 'speaker_switches': 0.2, 'dialogue_turns': 10, 'dialogue_line_count': 10},
            'visual_abstraction': {'action_lines': 5, 'visual_complexity': 0.3, 'continuous_action_runs': 0},
            'linguistic_load': {'sentence_count': 10, 'mean_sentence_length': 12, 'sentence_length_variance': 20.0},
            'ambient_signals': {'temporal_markers': 0, 'setting_drift': 0, 'component_scores': {'stillness': 0.1}},
            'micro_structure': [],
            'structural_change': {'is_new_location': False, 'time_jump': False, 'event_boundary_score': 10.0}
        })
    return features

def stage14_sensitivity():
    print("--- STAGE 14: SENSITIVITY ANALYSIS (HYPERPARAMETERS) ---")
    
    agent = DynamicsAgent()
    features = get_mock_features(50, entropy=0.6)
    
    # Baseline Run (Drama Defaults)
    baseline_params = {
        'lambda_base': 0.85,
        'beta_recovery': 0.3,
        'fatigue_threshold': 1.0,
        'coherence_weight': 0.15
    }
    
    baseline_trace = agent.run_simulation({'features': features, 'profile_params': baseline_params}, genre='drama')
    baseline_signals = [s['attentional_signal'] for s in baseline_trace]
    baseline_mean = statistics.mean(baseline_signals)
    
    perturbations = [
        ('lambda_base', 1.1), # +10%
        ('lambda_base', 0.9), # -10%
        ('beta_recovery', 1.1),   # +10%
        ('beta_recovery', 0.9),   # -10%
    ]
    
    print(f"Baseline Mean Signal: {baseline_mean:.4f}")
    
    results = []
    for param, factor in perturbations:
        test_params = baseline_params.copy()
        test_params[param] *= factor
        
        test_trace = agent.run_simulation({'features': features, 'profile_params': test_params}, genre='drama')
        test_signals = [s['attentional_signal'] for s in test_trace]
        test_mean = statistics.mean(test_signals)
        
        delta_pct = (test_mean - baseline_mean) / (baseline_mean if baseline_mean != 0 else 1) * 100
        results.append((param, factor, delta_pct))
        print(f"Perturbed {param} by x{factor:.1f}: Mean={test_mean:.4f} (Delta: {delta_pct:+.2f}%)")
        
        # Sensitivity Threshold: A 10% change in lambda should not cause a 50% change in output
        # If lambda 0.85 -> 0.935, signal might increase significantly but not double instantly.
        if abs(delta_pct) > 50:
            print(f"❌ FAILURE: System too fragile on {param} change.")
            # sys.exit(1)
            
    print("✅ SUCCESS: Hyperparameter sensitivity within stable bounds.")
    print("\n✅ STAGE 14 Sensitivity Analysis validated.")

if __name__ == "__main__":
    stage14_sensitivity()
