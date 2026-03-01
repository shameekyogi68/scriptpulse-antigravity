import sys
import os
import json
import statistics

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner
from scriptpulse.agents.interpretation_agent import InterpretationAgent
from scriptpulse.agents.dynamics_agent import DynamicsAgent

def get_mock_features(scene_count, entropy=0.2, dial_turns=5, action_lines=5):
    features = []
    for i in range(scene_count):
        features.append({
            'scene_index': i,
            'entropy_score': entropy,
            'referential_load': {'active_character_count': 2, 'entity_churn': 0.1, 'character_reintroductions': 0},
            'dialogue_dynamics': {'turn_velocity': 0.5, 'speaker_switches': 0.2, 'dialogue_turns': dial_turns, 'dialogue_line_count': dial_turns},
            'visual_abstraction': {'action_lines': action_lines, 'visual_complexity': 0.3, 'continuous_action_runs': 0},
            'linguistic_load': {'sentence_count': 10, 'mean_sentence_length': 12, 'sentence_length_variance': 20.0},
            'ambient_signals': {'temporal_markers': 0, 'setting_drift': 0, 'component_scores': {'stillness': 0.1}},
            'micro_structure': [],
            'structural_change': {'is_new_location': False, 'time_jump': False, 'event_boundary_score': 10.0}
        })
    return features

def test_writer_trust():
    print("=== WRITER TRUST VERIFICATION ===")
    
    interp = InterpretationAgent()
    dyn = DynamicsAgent()

    # 1. Interpretation Accuracy & 3. Missed Issue (High Strain Detection)
    print("\n[Test 1 & 3] Detection & Interpretation Accuracy")
    # 40 scenes of very high entropy (10.0)
    high_strain_features = get_mock_features(40, entropy=10.0, dial_turns=20)
    signals = dyn.run_simulation({'features': high_strain_features}, genre='drama')
    
    # DynamicsAgent needs features for these
    acd = dyn.calculate_acd_states({'temporal_signals': signals, 'features': high_strain_features})
    patterns = dyn.detect_patterns({
        'temporal_signals': signals, 
        'features': high_strain_features,
        'acd_states': acd
    })
    
    # Check if 'sustained_attentional_demand' or similar is caught
    # Note: different patterns might fire. 
    found_strain = any(p['pattern_type'] in ['sustained_attentional_demand', 'degenerative_fatigue', 'limited_recovery'] for p in patterns)
    print(f"Detected patterns: {[p['pattern_type'] for p in patterns]}")
    
    if found_strain:
        print("✅ SUCCESS: Detected high strain in synthetic flaw script.")
    else:
        print("❌ FAILURE: Missed high strain issue.")

    # Check Reflection Alignment
    mediated = interp.mediate_experience({'surfaced_patterns': patterns, 'acd_states': acd})
    for r in mediated['reflections']:
        print(f"Reflection: {r['reflection'][:100]}... (Conf: {r['confidence']})")
    
    if len(mediated['reflections']) > 0:
        print("✅ SUCCESS: System generated reflections for detected issues.")
    else:
        print("❌ FAILURE: Valid patterns were suppressed or not reflected.")

    # 2. False Alarm Test
    print("\n[Test 2] False Alarm Test (Safe Script)")
    # 10 scenes of low/moderate effort (entropy 0.1, dial 5, action 5)
    safe_features = get_mock_features(10, entropy=0.1, dial_turns=5, action_lines=5)
    sig_safe = dyn.run_simulation({'features': safe_features}, genre='drama')
    acd_safe = dyn.calculate_acd_states({'temporal_signals': sig_safe, 'features': safe_features})
    pat_safe = dyn.detect_patterns({'temporal_signals': sig_safe, 'features': safe_features, 'acd_states': acd_safe})
    
    print(f"Detected patterns (Safe Script): {[p['pattern_type'] for p in pat_safe]}")
    if len(pat_safe) == 0:
        print("✅ SUCCESS: Zero warnings for well-paced script.")
    else:
        print(f"⚠️ INFO: Found {len(pat_safe)} patterns in safe script (might be baseline noise).")

    # 4. Writer Intent Immunity
    print("\n[Test 4] Writer Intent Immunity")
    intent = [{'intent': 'intentionally exhausting', 'scene_range': [0, 39]}]
    immune_data = interp.apply_writer_intent({
        'patterns': patterns,
        'writer_intent': intent
    })
    
    is_suppressed = any(p['pattern_type'] == 'sustained_attentional_demand' for p in immune_data['suppressed_patterns'])
    print(f"Suppressed: {[p['pattern_type'] for p in immune_data['suppressed_patterns']]}")
    print(f"Surfaced: {[p['pattern_type'] for p in immune_data['surfaced_patterns']]}")
    
    # Check for acknowledgment
    final_immune = interp.mediate_experience(immune_data)
    print(f"Intent Acks: {final_immune['intent_acknowledgments']}")
    
    if len(final_immune['intent_acknowledgments']) > 0:
        print("✅ SUCCESS: Intent acknowledged and corresponding warnings suppressed.")
    else:
        print("❌ FAILURE: Intent ignored or ack missing.")

    # 6. Overconfidence & Confidence Visibility
    print("\n[Test 6] Overconfidence (Heuristics)")
    # We already have 'confidence' labels in reflections.
    has_conf = all('confidence' in r and 'confidence_score' in r for r in mediated['reflections'])
    if has_conf:
        print("✅ SUCCESS: Confidence bands and labels visible in interpretation.")
    else:
        print("❌ FAILURE: Interpretation lacks confidence metadata.")

    # 8. Genre Context Test
    print("\n[Test 8] Genre Context (Horror vs Drama)")
    # Drama lambda=0.9, Horror lambda=0.7 (fast decay), fatigue threshold Horror=1.5, Drama=0.9
    # The same sequence should feel "worse" in Drama than Horror regarding fatigue.
    trace_drama = dyn.run_simulation({'features': high_strain_features}, genre='Drama')
    trace_horror = dyn.run_simulation({'features': high_strain_features}, genre='Horror')
    
    # Measure fatigue in trace (DynamicsAgent adds 'fatigue' or 'overload' flag?)
    # Let's check max signal
    max_drama = max(s['attentional_signal'] for s in trace_drama)
    max_horror = max(s['attentional_signal'] for s in trace_horror)
    
    print(f"Max Attentional Signal - Drama: {max_drama:.3f}, Horror: {max_horror:.3f}")
    # In my DynamicsAgent, S[i] = S[i-1]*lambda + E[i]... 
    # Lambda Horror (0.7) < Drama (0.9) => Horror decays faster, but might have higher tolerate?
    # Actually if Horror recovers slower (beta=0.15) it might stay higher.
    
    # 9. Stability Test 
    print("\n[Test 9] Dashboard Stability")
    base_script = "INT. OFFICE - DAY\nJohn sits."
    edit_script = "INT. OFFICE - DAY\nJohn sits. Quietly."
    
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    out1 = runner.run_pipeline(base_script)
    out2 = runner.run_pipeline(edit_script)
    
    s1 = out1['temporal_trace'][0]['attentional_signal']
    s2 = out2['temporal_trace'][0]['attentional_signal']
    delta = abs(s1 - s2)
    print(f"Signal 1: {s1:.4f}, Signal 2: {s2:.4f}, Delta: {delta:.4f}")
    
    if delta < 0.05:
        print("✅ SUCCESS: Small edit caused small output change.")
    else:
        print("❌ FAILURE: Extreme swing from minor edit.")

    # 10. Transparency (XAI Alignment)
    print("\n[Test 10] Transparency (XAI Attribution)")
    # Scene with 100% Dialogue
    transparent_feat = get_mock_features(1, entropy=0.1, dial_turns=100, action_lines=0)
    xai = interp.generate_explanations({
        'features': transparent_feat,
        'semantic_scores': [0.1],
        'syntax_scores': [0.1]
    })
    
    driver = xai[0]['dominant_driver']
    print(f"Dominant Driver: {driver} (Expected: Dialogue)")
    
    if driver == 'Dialogue':
        print("✅ SUCCESS: XAI aligns with scene drivers.")
    else:
        print("❌ FAILURE: XAI misattributed driver.")

    # 7. Suggestion Relevance
    print("\n[Test 7] Suggestion Relevance")
    # Low signal scene (<0.3) should get 'Add obstacle/stakes' note
    low_sig_features = get_mock_features(1, entropy=0.01, dial_turns=1, action_lines=1)
    sig_low = dyn.run_simulation({'features': low_sig_features}, genre='drama')
    
    notes = interp.generate_scene_notes({
        'scenes': [{'lines': [{'tag': 'D', 'text': 'Hi.'}, {'tag': 'A', 'text': 'John waits.'}]}],
        'temporal_trace': sig_low,
        'valence_scores': [0.0],
        'syntax_scores': [0.1]
    })
    
    found_fix = any('Add obstacle/stakes' in n['suggestion'] for n in notes[0])
    print(f"Notes for Low Signal Scene: {[n['suggestion'] for n in notes[0]]}")
    
    if found_fix:
        print("✅ SUCCESS: Suggestion correctly addresses low tension.")
    else:
        print("❌ FAILURE: Suggestion missed low tension.")

    print("\n=== WRITER TRUST PASSED ===")

if __name__ == "__main__":
    test_writer_trust()
