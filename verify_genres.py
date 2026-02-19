
import sys
import os
import time

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.perception_agent import EncodingAgent

def verify_genre_separation():
    print("Running Genre Separation Verification...")
    
    # 1. Create Dummy Content (20 scenes of moderate activity)
    # We want a signal that decays if not "fed" enough.
    scenes = []
    for i in range(1, 21):
        lines = [
            {'tag': 'S', 'text': f'EXT. SCENE {i} - DAY', 'line_index': i*10},
            {'tag': 'A', 'text': 'He runs down the street, pursued by the shadow monster. Explosions rock the pavement.', 'line_index': i*10+1},
            {'tag': 'D', 'text': 'We have to keep moving! Does this never end?', 'line_index': i*10+2}
        ]
        scenes.append({'scene_index': i, 'lines': lines, 'start_line': i*10, 'end_line': i*10+2})
        
    # 2. Extract Features (Constant)
    encoder = EncodingAgent()
    features = encoder.run({'scenes': scenes})
    
    # 3. Run Dynamics for Thriller vs Drama
    dynamics = DynamicsAgent()
    
    # Thriller: Fast decay (0.75). Should drop lower.
    print(f"Testing Thriller Mode...")
    thriller_sigs = dynamics.run_simulation({'features': features}, genre='Thriller')
    thriller_avg = sum(s['attentional_signal'] for s in thriller_sigs) / len(thriller_sigs)
    
    # Drama: Slow decay (0.90). Should stay higher.
    print(f"Testing Drama Mode...")
    drama_sigs = dynamics.run_simulation({'features': features}, genre='Drama')
    drama_avg = sum(s['attentional_signal'] for s in drama_sigs) / len(drama_sigs)
    
    print(f"\nResults:")
    print(f"Thriller Avg Signal: {thriller_avg:.3f}")
    print(f"Drama Avg Signal:    {drama_avg:.3f}")
    
    delta = drama_avg - thriller_avg
    print(f"Delta: {delta:.3f}")
    
    if delta > 0.05:
        print("✅ SUCCESS: Drama maintains significantly higher attention for the same input (Slower Decay).")
        sys.exit(0)
    else:
        print("❌ FAILURE: Profiles are not distinct enough.")
        sys.exit(1)

if __name__ == "__main__":
    verify_genre_separation()
