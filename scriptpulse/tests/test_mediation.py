#!/usr/bin/env python3
"""
Tests for AudienceExperienceMediationAgent
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


def test_question_first_framing():
    """Test that output uses question-first framing"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    for entry in result['reflections']:
        reflection = entry['reflection']
        # Check for question mark in high/medium confidence
        if entry['confidence'] in ['high', 'medium']:
            assert '?' in reflection, f"Expected question in: {reflection}"
    
    print("✓ Question-first framing verified")


def test_explicit_uncertainty():
    """Test that output contains uncertainty language"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    uncertainty_words = {'may', 'might', 'could', 'possibility', 'uncertain', 'confidence'}
    
    for entry in result['reflections']:
        reflection = entry['reflection'].lower()
        has_uncertainty = any(word in reflection for word in uncertainty_words)
        assert has_uncertainty, f"No uncertainty in: {entry['reflection']}"
    
    print("✓ Explicit uncertainty present")


def test_no_banned_words():
    """Test that output contains no banned words"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    for entry in result['reflections']:
        is_valid, banned = mediation.validate_no_banned_words(entry['reflection'])
        assert is_valid, f"Banned word '{banned}' found in: {entry['reflection']}"
    
    print("✓ No banned words in output")


def test_silence_explanation():
    """Test that silence is explained when no patterns"""
    result = mediation.run({
        'surfaced_patterns': [],
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    assert result['silence_explanation'] is not None, "Silence must be explained"
    assert len(result['silence_explanation']) > 0, "Silence explanation cannot be empty"
    
    # Check silence does not imply quality
    explanation = result['silence_explanation'].lower()
    assert 'quality' not in explanation or 'not indicate quality' in explanation
    
    print("✓ Silence explained without implying quality")


def test_intent_acknowledgment():
    """Test that suppressed patterns acknowledge intent"""
    result = mediation.run({
        'surfaced_patterns': [],
        'suppressed_patterns': MOCK_SUPPRESSED,
        'intent_alignment_notes': MOCK_ALIGNMENT_NOTES
    })
    
    assert len(result['intent_acknowledgments']) > 0, "Intent must be acknowledged"
    
    # Check acknowledgment mentions the intent
    ack = result['intent_acknowledgments'][0]
    assert 'intentionally exhausting' in ack, "Intent label must be mentioned"
    
    print("✓ Intent acknowledged explicitly")


def test_experiential_translations():
    """Test that only allowed translations are used"""
    allowed_phrases = [
        'may feel mentally demanding',
        'there may be little chance to catch their breath',
        'may feel similar to what came just before',
        'the shift may feel sudden on first exposure',
        'may feel effortful but held together',
        'may begin to feel tiring over time'
    ]
    
    for pattern_type in mediation.EXPERIENTIAL_TRANSLATIONS.keys():
        result = mediation.run({
            'surfaced_patterns': [{'pattern_type': pattern_type, 'scene_range': [0, 5], 'confidence': 'high'}],
            'suppressed_patterns': [],
            'intent_alignment_notes': []
        })
        
        reflection = result['reflections'][0]['reflection']
        has_allowed = any(phrase in reflection for phrase in allowed_phrases)
        assert has_allowed, f"Non-allowed translation in: {reflection}"
    
    print("✓ All translations use allowed phrases")


def test_no_advice_or_recommendations():
    """Test that output never gives advice"""
    result = mediation.run({
        'surfaced_patterns': MOCK_SURFACED,
        'suppressed_patterns': [],
        'intent_alignment_notes': []
    })
    
    advice_indicators = ['you should', 'consider', 'try', 'recommend', 'suggest']
    
    for entry in result['reflections']:
        reflection = entry['reflection'].lower()
        for indicator in advice_indicators:
            assert indicator not in reflection, f"Advice '{indicator}' found in: {entry['reflection']}"
    
    print("✓ No advice or recommendations given")


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
    print("Running AudienceExperienceMediationAgent tests...\n")
    
    test_question_first_framing()
    test_explicit_uncertainty()
    test_no_banned_words()
    test_silence_explanation()
    test_intent_acknowledgment()
    test_experiential_translations()
    test_no_advice_or_recommendations()
    test_determinism()
    
    print("\n✅ All experience mediation tests passed!")


if __name__ == '__main__':
    run_all_tests()
