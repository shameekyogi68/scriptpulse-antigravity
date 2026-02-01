#!/usr/bin/env python3
"""
Complete Streamlit Error Testing
Simulates real user interaction to catch ALL runtime errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse import runner

def test_all_report_accesses():
    """Test every single report access pattern"""
    
    test_script = """
INT. COFFEE SHOP - DAY

ALEX (30s, tired) sits alone, laptop open.

ALEX
(muttering)
This deadline is impossible.

BARISTA (20s, cheerful) approaches.

BARISTA
Another coffee?

ALEX
Please. Triple shot.

BARISTA
Rough day?

ALEX
You have no idea.

Alex's PHONE BUZZES. A text: "Where's the report?"

ALEX (CONT'D)
(sighs)
Make it a quadruple.
"""
    
    print("Running pipeline...")
    report = runner.run_pipeline(test_script, genre='drama', lens='viewer')
    
    print("\n=== Testing All Dictionary Accesses ===\n")
    
    # Test 1: XAI Attribution
    print("1. XAI Attribution Access:")
    xai_attribution = report.get('xai_attribution', [])
    print(f"   Type: {type(xai_attribution)}")
    print(f"   Length: {len(xai_attribution)}")
    if xai_attribution and len(xai_attribution) > 0:
        scene_idx = 0
        if isinstance(xai_attribution[scene_idx], dict):
            xai_data = xai_attribution[scene_idx]
            dominant = xai_data.get('dominant_driver', 'Unknown')
            print(f"   ✅ Dominant driver: {dominant}")
            drivers = xai_data.get('drivers', {})
            print(f"   ✅ Drivers: {drivers}")
        else:
            print(f"   ⚠️ Item not dict: {type(xai_attribution[scene_idx])}")
    
    # Test 2: Suggestions
    print("\n2. Suggestions Access:")
    suggestions = report.get('suggestions', {})
    print(f"   Type: {type(suggestions)}")
    if isinstance(suggestions, dict):
        strategies = suggestions.get('structural_repair_strategies', [])
        print(f"   ✅ Strategies: {len(strategies)} items")
        for s in strategies:
            if isinstance(s, dict):
                print(f"      - Scene {s.get('scene', '?')}: {s.get('diagnosis', 'N/A')}")
    
    # Test 3: Temporal Trace
    print("\n3. Temporal Trace Access:")
    temporal = report.get('temporal_trace', [])
    print(f"   Type: {type(temporal)}")
    print(f"   Length: {len(temporal)}")
    if temporal:
        print(f"   ✅ First scene tension: {temporal[0].get('attentional_signal', 0)}")
    
    # Test 4: Scene Feedback
    print("\n4. Scene Feedback Access:")
    scene_fb = report.get('scene_feedback', {})
    print(f"   Type: {type(scene_fb)}")
    print(f"   Keys: {list(scene_fb.keys())}")
    for idx, notes in scene_fb.items():
        if isinstance(notes, list):
            print(f"   ✅ Scene {idx}: {len(notes)} notes")
    
    # Test 5: Reflections
    print("\n5. Reflections Access:")
    reflections = report.get('reflections', [])
    print(f"   Type: {type(reflections)}")
    print(f"   Length: {len(reflections)}")
    
    # Test 6: Fairness Audit
    print("\n6. Fairness Audit Access:")
    fairness = report.get('fairness_audit', {})
    print(f"   Type: {type(fairness)}")
    print(f"   Keys: {list(fairness.keys())}")
    
    # Test 7: Voice Fingerprints
    print("\n7. Voice Fingerprints Access:")
    voice = report.get('voice_fingerprints', {})
    print(f"   Type: {type(voice)}")
    print(f"   Characters: {list(voice.keys())}")
    
    # Test 8: Interaction Map
    print("\n8. Interaction Map Access:")
    interactions = report.get('interaction_map', {})
    print(f"   Type: {type(interactions)}")
    print(f"   Pairs: {len(interactions)}")
    
    # Test 9: Runtime Estimate
    print("\n9. Runtime Estimate Access:")
    runtime = report.get('runtime_estimate', {})
    print(f"   Type: {type(runtime)}")
    if isinstance(runtime, dict):
        print(f"   ✅ Min: {runtime.get('min_minutes', '?')} Max: {runtime.get('max_minutes', '?')}")
    
    # Test 10: Meta
    print("\n10. Meta Access:")
    meta = report.get('meta', {})
    print(f"   Type: {type(meta)}")
    print(f"   Keys: {list(meta.keys())}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED - No AttributeErrors or TypeErrors")
    print("="*60)

if __name__ == '__main__':
    test_all_report_accesses()
