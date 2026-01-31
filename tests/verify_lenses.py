
import sys
import os

# Ensure we can import scriptpulse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse.agents import parsing, segmentation, encoding, temporal
from scriptpulse import lenses

def run_verification():
    print("=== SciprPulse v5: Multi-Modal Lens Verification ===")
    
    # Load script
    script_path = "test_17_scenes.fountain"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        return

    with open(script_path, 'r') as f:
        text = f.read()

    # Pre-calculate common features
    print("-> Parsing and Encoding...")
    parsed = parsing.run(text)
    segmented = segmentation.run(parsed)
    encoded = encoding.run({'scenes': segmented, 'lines': parsed})
    
    print(f"-> Encoded {len(encoded)} scenes.")
    
    results = {}
    
    # Run for each lens
    lens_ids = ["viewer", "reader", "narrator"]
    
    for lens_id in lens_ids:
        print(f"\n[Testing Lens: {lens_id.upper()}]")
        config = lenses.get_lens(lens_id)
        
        # Run Temporal Agent
        signals = temporal.run({'features': encoded}, lens_config=config)
        
        # Test ACD (Internal integration check)
        # Note: In real pipeline, runner calls this. We emulate here.
        from scriptpulse.agents import acd
        acd_states = acd.run({'temporal_signals': signals, 'features': encoded})
        
        # Calculate stats
        total_effort = sum(s['instantaneous_effort'] for s in signals)
        avg_effort = total_effort / len(signals)
        max_effort = max(s['instantaneous_effort'] for s in signals)
        
        # Capture ACD stats
        avg_collapse = sum(a['collapse_likelihood'] for a in acd_states) / len(acd_states) if acd_states else 0
        avg_drift = sum(a['drift_likelihood'] for a in acd_states) / len(acd_states) if acd_states else 0
        
        results[lens_id] = {
            'avg_effort': avg_effort,
            'max_effort': max_effort,
            'avg_acd_collapse': avg_collapse,
            'avg_acd_drift': avg_drift,
            'first_5_efforts': [s['instantaneous_effort'] for s in signals[:5]]
        }
        
        print(f"  Avg Effort: {avg_effort:.4f}")
        print(f"  Max Effort: {max_effort:.4f}")
        print(f"  Avg Collapse: {avg_collapse:.4f} | Avg Drift: {avg_drift:.4f}")
        print(f"  First 5 E[i]: {results[lens_id]['first_5_efforts']}")

    # === VERIFY MEDIATION PHRASING LOGIC ===
    print("\n=== Mediation Phrasing Verification (ACD Bias) ===")
    from scriptpulse.agents import mediation
    
    # Test Case 1: Drift Dominant
    pattern_drift = {'pattern_type': 'degenerative_fatigue', 'scene_range': [1, 5], 'confidence': 'medium'}
    acd_drift = [{'scene_index': i, 'drift_likelihood': 0.8, 'collapse_likelihood': 0.2} for i in range(1, 6)]
    
    reflection_drift = mediation.generate_reflection(pattern_drift, acd_drift)
    print(f"[Drift Case] Output: \"{reflection_drift['reflection']}\"")
    
    if "wandering" in reflection_drift['reflection'] or "wander" in reflection_drift['reflection']:
        print("PASS: Correctly identified 'wandering' phrasing for Drift state.")
    else:
        print("FAIL: Did not use 'wandering' phrasing for Drift state.")
        
    # Test Case 2: Collapse Dominant
    pattern_collapse = {'pattern_type': 'degenerative_fatigue', 'scene_range': [1, 5], 'confidence': 'medium'}
    acd_collapse = [{'scene_index': i, 'drift_likelihood': 0.2, 'collapse_likelihood': 0.8} for i in range(1, 6)]
    
    reflection_collapse = mediation.generate_reflection(pattern_collapse, acd_collapse)
    print(f"[Collapse Case] Output: \"{reflection_collapse['reflection']}\"")
    
    if "tiring" in reflection_collapse['reflection']:
        print("PASS: Correctly identified 'tiring' phrasing for Collapse state.")
    else:
        print("FAIL: Did not use 'tiring' phrasing for Collapse state.")

    # === VERIFY SILENCE-AS-SIGNAL (SSF) LOGIC ===
    print("\n=== Silence-as-Signal Verification ===")
    
    # Test Case: High Confidence Silence
    ssf_high = {
        'is_silent': True,
        'explanation_key': 'stable_continuity'
    }
    
    explanation_high = mediation.generate_silence_explanation([], [], ssf_high)
    print(f"[High Conf Silence]: \"{explanation_high}\"")
    
    if "relatively stable" in explanation_high and "natural effort" in explanation_high:
         print("PASS: High confidence silence explanation generated correctly.")
    else:
         print("FAIL: Incorrect silence explanation.")

    # Verification Logic
    print("\n=== Comparative Analysis ===")
    viewer = results['viewer']
    reader = results['reader']
    narrator = results['narrator']
    
    # Assert differentiation
    if viewer['avg_effort'] == reader['avg_effort']:
        print("FAIL: Viewer and Reader produced identical efforts.")
    else:
        print("PASS: Viewer vs Reader differentiation detected.")
        
    if viewer['avg_effort'] == narrator['avg_effort']:
        print("FAIL: Viewer and Narrator produced identical efforts.")
    else:
        print("PASS: Viewer vs Narrator differentiation detected.")
        
    # Check specific tendencies (Narrator should likely be lower effort for this script as it has little dialogue)
    # The script 'test_17_scenes.fountain' is sparse.
    # Narrator emphasizes DialEngagement (turns). This script has very short dialogue.
    # So Narrator effort might be lower or higher depending on how pauses (action) are treated.
    # Actually Narrator weights VisualScore low (0.10). Viewer weights it 0.30.
    # Reader weights VisualScore high (0.45).
    # Since this script has a lot of action lines ("The phone vibrates", "Dark", etc), Reader should likely have higher effort.
    
    if reader['avg_effort'] > narrator['avg_effort']:
         print("OBSERVATION: Reader effort > Narrator effort (Expected for sparse, action-heavy script).")
    else:
         print("OBSERVATION: Narrator effort > Reader effort.")

if __name__ == "__main__":
    run_verification()
