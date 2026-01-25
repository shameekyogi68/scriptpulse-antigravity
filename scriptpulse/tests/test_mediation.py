#!/usr/bin/env python3
"""
Tests for ExperienceMediationAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import mediation


# Mock patterns for testing
MOCK_SURFACED = [
    {
        'pattern_type': 'sustained_attentional_demand',
        'scene_range': [0, 5],
        'confidence': 'high',
        'supporting_signals': ['test']
    },
    {
        'pattern_type': 'limited_recovery',
        'scene_range': [3, 8],
        'confidence': 'medium',
        'supporting_signals': ['test']
    }
]

MOCK_SUPPRESSED = [
    {
        'pattern_type': 'degenerative_fatigue',
        'scene_range': [10, 15],
        'confidence': 'low',
        'supporting_signals': ['test']
    }
]

MOCK_ALIGNMENT_NOTES = [
    {
        'pattern_type': 'degenerative_fatigue',
        'scene_range': [10, 15],
        'intent': 'intentionally exhausting',
        'action': 'suppressed'
    }
]


def test_experiential_language():
    """Test that output uses experiential, not prescriptive language"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    for entry in result['mediated_output']:
        # Check no prescriptive language
        desc = entry['description'].lower()
        exp = entry['experiential_note'].lower()
        
        assert 'should' not in desc and 'should' not in exp, "No 'should' allowed"
        assert 'must' not in desc and 'must' not in exp, "No 'must' allowed"
        assert 'fix' not in desc and 'fix' not in exp, "No 'fix' allowed"
        assert 'problem' not in desc and 'problem' not in exp, "No 'problem' allowed"
    
    print("✓ Experiential language only (no prescription)")


def test_no_ranking():
    """Test that patterns are not ranked or prioritized"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    for entry in result['mediated_output']:
        assert 'priority' not in entry
        assert 'importance' not in entry
        assert 'severity' not in entry
        assert 'rank' not in entry
    
    print("✓ No ranking or prioritization")


def test_suppression_acknowledgment():
    """Test that suppressed patterns are acknowledged"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': MOCK_SUPPRESSED,
        'intent_alignment_notes': MOCK_ALIGNMENT_NOTES
    })
    
    assert len(result['suppression_acknowledgments']) > 0
    assert result['total_suppressed'] == len(MOCK_SUPPRESSED)
    
    # Check acknowledgment mentions writer intent
    ack = result['suppression_acknowledgments'][0]
    assert 'Writer intent acknowledged' in ack['acknowledgment']
    
    print("✓ Suppression acknowledged with writer intent")


def test_confidence_explanation():
    """Test confidence is explained neutrally"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    for entry in result['mediated_output']:
        assert 'confidence' in entry
        assert 'confidence_explanation' in entry
        
        # Explanation should not imply good/bad
        exp = entry['confidence_explanation'].lower()
        assert 'bad' not in exp and 'good' not in exp and 'better' not in exp
    
    print("✓ Confidence explained neutrally")


def test_all_pattern_types_handled():
    """Test that all 6 pattern types have descriptions"""
    pattern_types = [
        'sustained_attentional_demand',
        'limited_recovery',
        'repetition',
        'surprise_cluster',
        'constructive_strain',
        'degenerative_fatigue'
    ]
    
    for ptype in pattern_types:
        result = mediation.run({
            'surfaced_patterns': [{'pattern_type': ptype, 'scene_range': [0, 5], 'confidence': 'high'}],
            'suppressed_patterns': [],
            'intent_alignment_notes': []
        })
        
        assert len(result['mediated_output']) == 1
        assert result['mediated_output'][0]['description'] != ''
    
    print("✓ All 6 pattern types have descriptions")


def test_empty_input():
    """Test handling of empty input"""
    result = mediation.run({
        'surfaced_patterns': [],
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    assert result['mediated_output'] == []
    assert result['total_surfaced'] == 0
    assert result['total_suppressed'] == 0
    
    print("✓ Empty input handled correctly")


def test_determinism():
    """Test that same input produces identical output"""
    input_data = {
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': MOCK_SUPPRESSED,
        'intent_alignment_notes': MOCK_ALIGNMENT_NOTES
    }
    
    result1 = mediation.run(input_data)
    result2 = mediation.run(input_data)
    
    assert result1 == result2, "Mediation should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all mediation tests"""
    print("Running ExperienceMediationAgent tests...\n")
    
    test_experiential_language()
    test_no_ranking()
    test_suppression_acknowledgment()
    test_confidence_explanation()
    test_all_pattern_types_handled()
    test_empty_input()
    test_determinism()
    
    print("\n✅ All experience mediation tests passed!")


if __name__ == '__main__':
    run_all_tests()
