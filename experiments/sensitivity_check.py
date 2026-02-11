
import sys
import os
import random
import numpy as np
import pandas as pd

# Add parent directory to path to import scriptpulse modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse.agents import temporal
from scriptpulse.agents import encoding
# Mock input data generator for sensitivity testing
def generate_mock_scene(index, intensity=0.5):
    """Generates a synthetic scene feature vector."""
    return {
        'scene_index': index,
        'linguistic_load': {'sentence_length_variance': random.gauss(10, 2) * intensity, 'sentence_count': int(random.gauss(20, 5))},
        'dialogue_dynamics': {'speaker_switches': int(random.gauss(5, 2) * intensity), 'dialogue_turns': int(random.gauss(10, 3)), 'turn_velocity': 0.5, 'monologue_runs': 0},
        'visual_abstraction': {'action_lines': int(random.gauss(5, 2) * (1-intensity)), 'continuous_action_runs': int(random.gauss(1, 0.5))},
        'referential_load': {'active_character_count': int(random.gauss(3, 1)), 'character_reintroductions': int(random.gauss(1, 0.5))},
        'structural_change': {'event_boundary_score': random.random() * 100},
        'ambient_signals': {'ambient_score': random.random(), 'is_ambient': False},
        'micro_structure': [] # Simplified
    }

def run_sensitivity_analysis(iterations=1000, genre='Horror', baseline_lambda=0.92):
    """
    Perturbs lambda by +/- 10% and measures divergence in the final Attentional Signal.
    """
    print(f"--- Sensitivity Analysis: {genre} (Lambda={baseline_lambda}) ---")
    
    # 1. Generate a fixed "Control Script" (50 scenes)
    script_features = [generate_mock_scene(i, intensity=(0.8 if i % 10 == 0 else 0.4)) for i in range(50)]
    
    # 2. Run Control (Baseline)
    # We need to mock the full input structure for temporal.run
    control_input = {
        'features': script_features,
        'semantic_scores': [0.5]*50, 'syntax_scores': [0.5]*50, 
        'visual_scores': [0.5]*50, 'social_scores': [0.5]*50, 
        'valence_scores': [0.1]*50, 'coherence_scores': [0.0]*50
    }
    
    # Run with fixed baseline lambda
    control_profile = {'lambda_base': baseline_lambda, 'beta_recovery': 0.3, 'fatigue_threshold': 1.0, 'coherence_weight': 0.15}
    control_output = temporal.run(control_input, genre=genre, profile_params=control_profile)
    control_signals = np.array([s['attentional_signal'] for s in control_output])
    
    divergences = []
    
    # 3. Monte Carlo Loop
    for _ in range(iterations):
        # Perturb Lambda (+/- 10%)
        perturbation = random.uniform(0.9, 1.1)
        test_lambda = baseline_lambda * perturbation
        
        test_profile = control_profile.copy()
        test_profile['lambda_base'] = test_lambda
        
        test_output = temporal.run(control_input, genre=genre, profile_params=test_profile)
        test_signals = np.array([s['attentional_signal'] for s in test_output])
        
        # Calculate Mean Absolute Divergence (MAD) from Control
        mad = np.mean(np.abs(control_signals - test_signals))
        divergences.append(mad)
        
    # 4. Statistics
    avg_divergence = np.mean(divergences)
    max_divergence = np.max(divergences)
    stability_score = 1.0 - (avg_divergence / np.mean(control_signals))
    
    print(f"Perturbation Range: +/- 10%")
    print(f"Mean Divergence: {avg_divergence:.4f}")
    print(f"Stability Score: {stability_score:.4f} (Target > 0.85)")
    
    if stability_score > 0.85:
        print("[PASS] System is Robust to Parameter Uncertainty.")
    else:
        print("[FAIL] System is Fragile. Parameter estimation is critical.")
        
    return stability_score

if __name__ == "__main__":
    # Test Horror (High Lambda) vs Comedy (Low Lambda)
    run_sensitivity_analysis(genre='Horror', baseline_lambda=0.92)
    print("\n")
    run_sensitivity_analysis(genre='Comedy', baseline_lambda=0.70)
