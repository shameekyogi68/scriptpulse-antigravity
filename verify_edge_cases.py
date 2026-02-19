
import sys
import os
import time

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.perception_agent import EncodingAgent

def verify_edge_cases():
    print("Running Edge Case Verification...")
    
    # 1. Maximally Complex Content (Cognitive Overload)
    # To breach 0.9, we need:
    # - High Structural Load: Many Characters, Frequent Changes
    # - High Syntactic Load: Long sentences with high variance
    # - High Semantic Load: Low repetitiveness (High Entropy)
    high_octane = []
    for i in range(1, 11):
        lines = [
            {'tag': 'S', 'text': f'EXT. BATTLEFIELD {i} - DAY', 'line_index': i*10},
            {'tag': 'C', 'text': 'COMMANDER (V.O.)', 'line_index': i*10+1},
            {'tag': 'D', 'text': 'The synchronization of the multi-phasic targeting array, which requires precision beyond human capability, is failing because the sub-routines are corrupted by a virus that mimics organic neural patterns.', 'line_index': i*10+2},
            {'tag': 'A', 'text': 'Explosions rupture the hull. ALICE screams. BOB falls. CHARLIE runs. The data stream flickers—red, blue, green—as the system crashes.', 'line_index': i*10+3},
            {'tag': 'C', 'text': 'ALICE', 'line_index': i*10+4},
            {'tag': 'D', 'text': 'Reboot it! Now! Before the containment field collapses and exposes the reactor core to the vacuum!', 'line_index': i*10+5}
        ]
        high_octane.append({'scene_index': i, 'lines': lines, 'start_line': i*10, 'end_line': i*10+5})

    # 2. Slow Art Content
    slow_art = []
    for i in range(1, 11):
        lines = [{'tag': 'D', 'text': 'I suppose... in the end... it represents the futility of time itself. Does it not?', 'line_index': i}]
        slow_art.append({'scene_index': i, 'lines': lines, 'start_line': i, 'end_line': i})

    # 3. Extract Features
    encoder = EncodingAgent()
    feat_high = encoder.run({'scenes': high_octane})
    feat_slow = encoder.run({'scenes': slow_art})
    
    dynamics = DynamicsAgent()

    # Case A: High Action (Michael Bay) in Drama Mode (Slow Decay)
    # Expect: High Fatigue accumulation because Drama expects slow pacing but gets intensity.
    print("\n--- Test A: High Action in 'Drama' Mode ---")
    res_a = dynamics.run_simulation({'features': feat_high}, genre='Drama')
    
    # DEBUG: Print signal trace
    signals_a = [s['attentional_signal'] for s in res_a]
    print(f"Signals A: {[round(x, 2) for x in signals_a]}")
    
    avg_fatigue_a = sum(s.get('fatigue_state', 0) for s in res_a) / len(res_a)
    print(f"Avg Fatigue: {avg_fatigue_a:.3f}")

    # Case B: Slow Art (French Cinema) in Thriller Mode (Fast Decay)
    # Expect: Bottoming out (Sag) because Thriller expects activity but gets monologue.
    print("\n--- Test B: Slow Art in 'Thriller' Mode ---")
    res_b = dynamics.run_simulation({'features': feat_slow}, genre='Thriller')
    avg_att_b = sum(s['attentional_signal'] for s in res_b) / len(res_b)
    print(f"Avg Attention: {avg_att_b:.3f}")
    
    if avg_fatigue_a > 0.0 and avg_att_b < 0.5:
        print("\n✅ SUCCESS: Metric Logic holds. Action/Drama caused fatigue. Art/Thriller caused sag.")
    else:
        print("\n❌ FAILURE: Logic check failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify_edge_cases()
