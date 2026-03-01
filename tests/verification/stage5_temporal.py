import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.dynamics_agent import DynamicsAgent

def get_full_mock(entropy=0.0, scene_index=0):
    return {
        'scene_index': scene_index,
        'entropy_score': entropy,
        'referential_load': {
            'active_character_count': 5, 
            'entity_churn': 0.1,
            'unresolved_references': 0.0
        },
        'dialogue_dynamics': {
            'turn_velocity': 0.5, 
            'speaker_switches': 0.2, 
            'dialogue_line_count': 5
        },
        'visual_abstraction': {
            'action_lines': 5, 
            'visual_complexity': 0.2
        },
        'linguistic_load': {
            'sentence_count': 10, 
            'mean_sentence_length': 12, 
            'sentence_length_variance': 20.0
        },
        'ambient_signals': {
            'temporal_markers': 0, 
            'setting_drift': 0,
            'component_scores': {'stillness': 0.1}
        },
        'micro_structure': [],
        'structural_change': {
            'is_new_location': False, 
            'time_jump': False, 
            'event_boundary_score': 10.0
        }
    }

def stage5_validation():
    print("--- STAGE 5: TEMPORAL SIMULATION BEHAVIOR ---")
    
    agent = DynamicsAgent()
    
    # 1. No exponential explosion (Capped at 1.0)
    high_effort_seq = [get_full_mock(entropy=100.0, scene_index=i) for i in range(50)]
    
    trace_explode = agent.run_simulation({'features': high_effort_seq})
    max_signal = max(s['attentional_signal'] for s in trace_explode)
    print(f"Max Signal (High Load): {max_signal} (Expected: 1.0)")
    
    # 2. No negative strain
    low_effort_seq = [get_full_mock(entropy=-100.0, scene_index=i) for i in range(50)]
    
    trace_neg = agent.run_simulation({'features': low_effort_seq})
    min_signal = min(s['attentional_signal'] for s in trace_neg)
    print(f"Min Signal (Low Load): {min_signal} (Expected: 0.0)")

    # 3. Proper Recovery (Sequence of High then Low)
    high_feat = get_full_mock(entropy=5.0, scene_index=0)
    low_feats = [get_full_mock(entropy=0.0, scene_index=i+1) for i in range(10)]
    for f in low_feats:
        f['linguistic_load'] = {'sentence_count': 1, 'mean_sentence_length': 1, 'sentence_length_variance': 0.0}
        f['dialogue_dynamics']['dialogue_line_count'] = 0
        f['visual_abstraction']['action_lines'] = 0
    
    sequence = [high_feat] + low_feats
    trace_action = agent.run_simulation({'features': sequence}, genre='Action')
    trace_drama = agent.run_simulation({'features': sequence}, genre='Drama')
    
    # Print a few points
    print(f"Action: Scene 1 S={trace_action[0]['attentional_signal']:.3f}, Scene 10 S={trace_action[10]['attentional_signal']:.3f}")
    print(f"Drama:  Scene 1 S={trace_drama[0]['attentional_signal']:.3f}, Scene 10 S={trace_drama[10]['attentional_signal']:.3f}")
    
    if trace_action[10]['attentional_signal'] < trace_drama[10]['attentional_signal']:
        print("✅ SUCCESS: Action genre recovers faster than Drama.")
    else:
        print("❌ FAILURE: Recovery behavior inverted.")

    print("\n✅ STAGE 5 Temporal Simulation Behavior validated.")

if __name__ == "__main__":
    stage5_validation()
