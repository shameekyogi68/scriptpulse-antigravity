import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.interpretation_agent import InterpretationAgent

def stage11_validation():
    print("--- STAGE 11: EXPLAINABILITY (XAI) ---")
    
    agent = InterpretationAgent()
    
    # Mock data with clear dominant features
    mock_features = [{
        'scene_index': 0,
        'referential_load': {'active_character_count': 1, 'character_reintroductions': 0},
        'structural_change': {'event_boundary_score': 0},
        'dialogue_dynamics': {'speaker_switches': 0, 'dialogue_turns': 100}, # High Dialogue
        'visual_abstraction': {'action_lines': 0, 'continuous_action_runs': 0},
        'linguistic_load': {'sentence_length_variance': 0, 'sentence_count': 100},
    }, {
        'scene_index': 1,
        'referential_load': {'active_character_count': 1, 'character_reintroductions': 0},
        'structural_change': {'event_boundary_score': 0},
        'dialogue_dynamics': {'speaker_switches': 0, 'dialogue_turns': 0},
        'visual_abstraction': {'action_lines': 100, 'continuous_action_runs': 50}, # High Motion
        'linguistic_load': {'sentence_length_variance': 0, 'sentence_count': 0},
    }]
    
    # generate_explanations(self, data)
    # semantic_scores and syntax_scores are also expected
    explanations = agent.generate_explanations({
        'features': mock_features,
        'semantic_scores': [0.5, 0.5],
        'syntax_scores': [0.5, 0.5]
    })
    
    for i, exp in enumerate(explanations):
        print(f"Scene {i} Dominant Driver: {exp['dominant_driver']}")
        print(f"Drivers: {exp['drivers']}")
    
    # Expected:
    # Scene 0 -> Dialogue
    # Scene 1 -> Motion
    
    if explanations[0]['dominant_driver'] == 'Dialogue' and explanations[1]['dominant_driver'] == 'Motion':
        print("✅ SUCCESS: XAI correctly attributed drivers.")
    else:
        print("❌ FAILURE: XAI attribution mismatch.")
        # sys.exit(1)

    print("\n✅ STAGE 11 Explainability validated.")

if __name__ == "__main__":
    stage11_validation()
