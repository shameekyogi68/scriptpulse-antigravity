
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent

def verify_trace():
    print("--- Verifying Debug Trace ---")
    agent = DynamicsAgent()
    
    # Mock Features
    features = []
    for i in range(3):
        features.append({
            'scene_index': i,
            'referential_load': {'active_character_count': 2},
            'structural_change': {'event_boundary_score': 50},
            'entropy_score': 4.0,
            'linguistic_load': {'sentence_length_variance': 20, 'sentence_count': 5},
            'dialogue_dynamics': {'turn_velocity': 0.5, 'dialogue_line_count': 10},
            'visual_abstraction': {'action_lines': 2},
            'ambient_signals': {'component_scores': {'stillness': 0}}
        })
        
    print("Running with debug=True...")
    # This should print [TRACE] lines to stdout
    agent.run_simulation({'features': features}, genre='drama', debug=True)
    
    print("\nRunning with debug=False...")
    # This should NOT print [TRACE] lines
    agent.run_simulation({'features': features}, genre='drama', debug=False)
    
    print("\nDone.")

if __name__ == "__main__":
    verify_trace()
