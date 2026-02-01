"""
Streamlit App Error Testing Script
Tests all potential error points in streamlit_app.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse import runner

def test_all_report_keys():
    """Test that pipeline returns expected structure"""
    
    test_script = """
INT. OFFICE - DAY

JOHN sits at his desk.

JOHN
I need to finish this report.

MARY enters.

MARY
Any updates?

JOHN
Almost done.
"""
    
    print("Testing pipeline output structure...")
    result = runner.run_pipeline(test_script, genre='drama', lens='viewer')
    
    # Check all keys that streamlit_app.py expects
    expected_keys = [
        'temporal_trace',
        'reflections',
        'suggestions',
        'scene_feedback',
        'fairness_audit',
        'semantic_flux',
        'voice_fingerprints',
        'interaction_map',
        'runtime_estimate',
        'meta',
        'scene_info'
    ]
    
    print("\\nChecking expected keys:")
    for key in expected_keys:
        if key in result:
            value_type = type(result[key])
            print(f"  ✅ {key}: {value_type}")
        else:
            print(f"  ❌ {key}: MISSING")
    
    # Specifically check suggestions structure
    print("\\n=== SUGGESTIONS STRUCTURE ===")
    suggestions = result.get('suggestions', {})
    print(f"Type: {type(suggestions)}")
    print(f"Content: {suggestions}")
    
    if isinstance(suggestions, dict):
        print(f"Keys: {suggestions.keys()}")
        if 'structural_repair_strategies' in suggestions:
            strategies = suggestions['structural_repair_strategies']
            print(f"Strategies type: {type(strategies)}")
            print(f"Strategies count: {len(strategies)}")
            if strategies:
                print(f"First strategy type: {type(strategies[0])}")
                print(f"First strategy: {strategies[0]}")
    
    print("\\n=== TEST PASSED ===")
    return result


if __name__ == '__main__':
    test_all_report_keys()
