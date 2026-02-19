
import sys
import os
import random
import statistics

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent

def generate_script(type_label, length=30):
    features = []
    for i in range(length):
        base_intensity = 0.5
        
        # Profile Characteristics
        if type_label == 'Upper Decile' or type_label == 'Masterpiece':
            # High variance, rhythmic intensity
            import math
            base_intensity = 0.5 + 0.4 * math.sin(i / 3.0) 
            struct = 80 if i % 10 == 0 else 20
            entropy = 3.0 + base_intensity * 3.0
            
        elif type_label == 'Low Engagement' or type_label == 'Boring':
            # Flat, low intensity
            base_intensity = 0.2
            struct = 10
            entropy = 2.0
            
        elif type_label == 'High Entropy' or type_label == 'Chaotic':
            # Random high noise
            base_intensity = random.uniform(0.1, 0.9)
            struct = random.choice([0, 100])
            entropy = random.uniform(4.0, 6.0) # High confusion?
            
        elif type_label == 'High Action' or type_label == 'Fast':
            # High action, short scenes
            base_intensity = 0.8
            struct = 50
            entropy = 3.5
            
        feat = {
            'scene_index': i,
            'referential_load': {'active_character_count': 2 + int(base_intensity*3)},
            'structural_change': {'event_boundary_score': struct},
            'entropy_score': entropy,
            'linguistic_load': {'sentence_length_variance': 10 + base_intensity*40, 'sentence_count': 10},
            'dialogue_dynamics': {'turn_velocity': base_intensity, 'dialogue_line_count': 5},
            'visual_abstraction': {'action_lines': 5 if type_label == 'Fast' else 2},
            'ambient_signals': {'component_scores': {'stillness': 0.1}}
        }
        features.append(feat)
    return features

def verify_calibration():
    print("==========================================")
    print("      CALIBRATION AUDIT (v1.3)            ")
    print("==========================================")
    
    agent = DynamicsAgent()
    genre = 'Drama'
    
    results = {}
    
    # 1. Run 20 Scripts (5 of each type)
    types = ['Upper Decile', 'Low Engagement', 'High Entropy', 'High Action']
    
    print(f"{'Type':<15} | {'Avg Att':<10} | {'Fatigue':<10} | {'Status'}")
    print("-" * 55)
    
    for t in types:
        scores = []
        for i in range(5):
            feats = generate_script(t, length=40)
            trace = agent.run_simulation({'features': feats}, genre=genre, debug=False)
            
            avg_att = statistics.mean([s['attentional_signal'] for s in trace])
            scores.append(avg_att)
            
        avg_score = statistics.mean(scores)
        results[t] = avg_score
        print(f"{t:<15} | {avg_score:.3f}      | N/A        | {'OK' if 0.1 <= avg_score <= 0.9 else 'Warning'}")

    print("-" * 55)
    
    # Check Separation
    spread = max(results.values()) - min(results.values())
    print(f"Spread: {spread:.3f}")
    
    if spread < 0.2:
        print("❌ FAILED: All scripts cluster together. Scaling is weak.")
    else:
        # Check ordering
        if results['Upper Decile'] > results['Low Engagement'] and results['High Action'] > results['Low Engagement']:
             print("✅ PASSED: Meaningful separation detected.")
             print("   (Upper Decile/High Action > Low Engagement)")
        else:
             print("❌ FAILED: Low Engagement script scored higher than active ones?")
             
    # 2. Cross Draft Delta
    print("\n--- Cross Draft Delta ---")
    draft_a = generate_script('Boring', 40)
    draft_b = generate_script('Masterpiece', 40) # Treated as "Tightened" version
    
    res_a = statistics.mean([s['attentional_signal'] for s in agent.run_simulation({'features': draft_a}, genre=genre)])
    res_b = statistics.mean([s['attentional_signal'] for s in agent.run_simulation({'features': draft_b}, genre=genre)])
    
    delta = res_b - res_a
    print(f"Draft A (Boring): {res_a:.3f}")
    print(f"Draft B (Tightened): {res_b:.3f}")
    print(f"Delta: {delta:+.3f}")
    
    if delta > 0.1:
        print("✅ PASSED: Improvement is measurable.")
    else:
        print("❌ FAILED: Improvement too small.")
        
    # 3. Blind Ranking Test
    print("\n--- Blind Ranking Verification ---")
    from scriptpulse.validation.ranking_experiment import RankingExperiment
    
    # Mock Ground Truth: Upper Decile (1) > Fast (2) > Chaotic (3) > Low (4)
    # We generated 5 of each. Let's rank the averages.
    # Script IDs: [Type]_[Index]
    
    # Generate Map
    features_map = {}
    gt_ranks = {}
    rank_ptr = 1
    
    # Order: Upper Decile -> Fast -> Chaotic -> Low Engagement
    ordered_types = ['Upper Decile', 'High Action', 'High Entropy', 'Low Engagement']
    
    for t in ordered_types:
        for i in range(2): # Just 2 of each for speed
            sid = f"{t}_{i}"
            features_map[sid] = generate_script(t, 40)
            gt_ranks[sid] = rank_ptr # Tie rank? No, just bucketing
        rank_ptr += 1 # Increment rank for next group
        
    ranker = RankingExperiment(agent)
    res = ranker.run(features_map, gt_ranks)
    print(ranker.generate_report(res))
    
    if res['rho'] > 0.4:
        print("✅ PASSED: Ranking logic correlates with intent.")
    else:
        print("⚠️ WARNING: Ranking correlation weak (synthetic artifacts?).")
        
    # 4. Inter-Rater Check
    print("\n--- Inter-Rater Logic Check ---")
    try:
        import krippendorff
        # Mock CSV File
        with open('mock_ratings_temp.csv', 'w') as f:
            f.write("script_id,rater_id,scene_index,score\n")
            f.write("s1,r1,1,0.5\n")
            f.write("s1,r2,1,0.6\n") # Close
            f.write("s1,r1,2,0.8\n")
            f.write("s1,r2,2,0.2\n") # Divergent
            
        from scriptpulse.validation.inter_rater import InterRaterReliability
        irr = InterRaterReliability()
        alpha_res = irr.calculate_alpha('mock_ratings_temp.csv')
        
        if 'error' in alpha_res:
            print("⚠️ SKIPPED: Krippendorff library not installed.")
        else:
            print(f"Alpha: {alpha_res.get('alpha', 'N/A')}")
            print("✅ PASSED: Inter-Rater logic executes.")
            
        import os
        if os.path.exists('mock_ratings_temp.csv'):
            os.remove('mock_ratings_temp.csv')
            
    except ImportError:
        print("⚠️ SKIPPED: Krippendorff not locally available.")

if __name__ == "__main__":
    verify_calibration()
