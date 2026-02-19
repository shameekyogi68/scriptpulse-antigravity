
import sys
import os
import copy
import statistics

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent

def generate_synthetic_script(length=50):
    features = []
    # Create a sine-wave like intensity pattern
    import math
    for i in range(length):
        intensity = 0.5 + 0.4 * math.sin(i / 5.0) # Oscillates between 0.1 and 0.9
        
        feat = {
            'scene_index': i,
            'referential_load': {'active_character_count': 2 + int(intensity*4)},
            'structural_change': {'event_boundary_score': int(intensity*100)},
            'entropy_score': 3.0 + intensity*4.0,
            'linguistic_load': {'sentence_length_variance': 20 + intensity*50, 'sentence_count': 10},
            'dialogue_dynamics': {'turn_velocity': intensity, 'dialogue_line_count': 10},
            'visual_abstraction': {'action_lines': 2},
            'ambient_signals': {'component_scores': {'stillness': 1.0 - intensity}}
        }
        features.append(feat)
    return features

def run_test(name, agent, features, genre, override_params=None):
    # We need to manually inject overrides because run_simulation derives from genre
    # But run_simulation accepts profile_params if passed!
    
    # Baseline run to get default params
    base_params = agent.get_genre_config(genre)
    params = {
        'lambda_base': base_params['lambda_decay'],
        'beta_recovery': base_params['beta_recovery'],
        'fatigue_threshold': base_params['fatigue_threshold'],
        'coherence_weight': 0.15
    }
    
    if override_params:
        params.update(override_params)
        
    # Inject into input_data because we modified run_simulation to check there
    input_data = {'features': features, 'profile_params': params}
    
    trace = agent.run_simulation(input_data, genre=genre, debug=False)
    
    avg_att = statistics.mean([s['attentional_signal'] for s in trace])
    fatigue_scenes = sum(1 for s in trace if s['fatigue_state'] > 0)
    
    return avg_att, fatigue_scenes, params

def verify_sensitivity():
    print("==========================================")
    print("      SENSITIVITY ANALYSIS (v1.3)         ")
    print("==========================================")
    
    agent = DynamicsAgent()
    features = generate_synthetic_script(50)
    genre = 'Drama'
    
    # 1. Baseline
    base_att, base_fat, base_p = run_test("Baseline", agent, features, genre)
    print(f"Baseline ({genre}): Lambda={base_p['lambda_base']:.2f}, Thresh={base_p['fatigue_threshold']:.2f}")
    print(f"  -> Avg Att: {base_att:.3f}")
    print(f"  -> Fatigue Scenes: {base_fat}")
    print("-" * 40)
    
    # 2. Lambda Sensitivity
    for delta in [-0.05, 0.05]:
        new_val = base_p['lambda_base'] * (1.0 + delta)
        curr_att, curr_fat, _ = run_test(f"Lambda {delta:+%}", agent, features, genre, {'lambda_base': new_val})
        
        pct_change_att = (curr_att - base_att) / base_att * 100
        elasticity = abs(pct_change_att / (delta * 100))
        
        print(f"Lambda {delta:+.0%}: {new_val:.3f}")
        print(f"  -> Avg Att: {curr_att:.3f} (Delta: {pct_change_att:+.1f}%)")
        print(f"  -> Elasticity: {elasticity:.2f} (Target < 2.0)")
        
        if elasticity > 3.0:
            print("  ❌ UNSTABLE: Tiny input change caused massive output swing.")
        else:
            print("  ✅ STABLE")
            
    print("-" * 40)

    # 3. Fatigue Threshold Sensitivity
    # Impact on Fatigue Count
    for delta in [-0.10, 0.10]:
        new_val = base_p['fatigue_threshold'] * (1.0 + delta)
        curr_att, curr_fat, _ = run_test(f"Thresh {delta:+%}", agent, features, genre, {'fatigue_threshold': new_val})
        
        # Avoid div by zero
        denom = base_fat if base_fat > 0 else 1
        diff = curr_fat - base_fat
        pct_change_fat = (diff / denom) * 100
        
        print(f"Fatigue Thresh {delta:+.0%}: {new_val:.3f}")
        print(f"  -> Fatigue Scenes: {curr_fat} (Base: {base_fat})")
        
        # High elasticity is expected for thresholds near the signal peak
        # But should not be chaotic.
        print(f"  -> Delta Scenes: {diff:+d}")


if __name__ == "__main__":
    verify_sensitivity()
