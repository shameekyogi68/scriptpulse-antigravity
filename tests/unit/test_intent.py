#!/usr/bin/env python3
"""
Tests for WriterIntentImmunityAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import intent


# Mock patterns for testing
MOCK_PATTERNS = [
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


def test_no_intent_passthrough():
    """Test that patterns pass through unchanged if no intent declared"""
    result = intent.run({
        'patterns': MOCK_PATTERNS,
        'writer_intent': []
    })
    
    # All patterns should surface
    assert len(result['surfaced_patterns']) == len(MOCK_PATTERNS)
    assert len(result['suppressed_patterns']) == 0
    assert len(result['intent_alignment_notes']) == 0
    
    print("✓ No intent: patterns pass through unchanged")


def test_full_suppression_with_intent():
    """Test that explicit intent suppresses overlapping patterns"""
    result = intent.run({
        'patterns': MOCK_PATTERNS,
        'writer_intent': [
            {
                'scene_range': [0, 10],
                'intent': 'intentionally exhausting'
            }
        ]
    })
    
    # All patterns should be suppressed (intent covers entire range)
    assert len(result['surfaced_patterns']) == 0
    assert len(result['suppressed_patterns']) == len(MOCK_PATTERNS)
    
    # Alignment notes should be recorded
    assert len(result['intent_alignment_notes']) == len(MOCK_PATTERNS)
    for note in result['intent_alignment_notes']:
        assert note['intent'] == 'intentionally exhausting'
        assert note['action'] == 'suppressed'
    
    print("✓ Full suppression: explicit intent suppresses patterns")


def test_partial_overlap():
    """Test partial overlap handling"""
    result = intent.run({
        'patterns': [
            {
                'pattern_type': 'sustained_attentional_demand',
                'scene_range': [0, 10],
                'confidence': 'high',
                'supporting_signals': ['test']
            }
        ],
        'writer_intent': [
            {
                'scene_range': [5, 10],
                'intent': 'should feel tense'
            }
        ]
    })
    
    # Should have partial suppression
    assert len(result['suppressed_patterns']) == 1
    
    # Remaining portion should have downgraded confidence
    if result['surfaced_patterns']:
        assert result['surfaced_patterns'][0]['confidence'] in ['medium', 'low']
    
    # Alignment note should show partial_suppression
    assert result['intent_alignment_notes'][0]['action'] == 'partial_suppression'
    
    print("✓ Partial overlap: only overlapping range suppressed")


def test_invalid_intent_rejected():
    """Test that invalid intent labels are silently rejected"""
    result = intent.run({
        'patterns': MOCK_PATTERNS,
        'writer_intent': [
            {
                'scene_range': [0, 10],
                'intent': 'this is a great script'  # Not allowed!
            }
        ]
    })
    
    # Invalid intent should be rejected, patterns pass through
    assert len(result['surfaced_patterns']) == len(MOCK_PATTERNS)
    assert len(result['suppressed_patterns']) == 0
    
    print("✓ Invalid intent: silently rejected (no inference)")


def test_allowed_intents_only():
    """Test that only allowed intent labels are accepted"""
    allowed = [
        'intentionally exhausting',
        'intentionally confusing',
        'should feel smooth',
        'should feel tense',
        'experimental / anti-narrative'
    ]
    
    for allowed_intent in allowed:
        result = intent.run({
            'patterns': MOCK_PATTERNS,
            'writer_intent': [
                {
                    'scene_range': [0, 10],
                    'intent': allowed_intent
                }
            ]
        })
        
        # Should suppress with allowed intents
        assert len(result['suppressed_patterns']) > 0, f"Intent '{allowed_intent}' should work"
    
    print("✓ All 5 allowed intent labels work correctly")


def test_no_inference():
    """Test that intent is never inferred from patterns"""
    result = intent.run({
        'patterns': MOCK_PATTERNS,
        'writer_intent': None  # No intent
    })
    
    # Patterns should pass through, no suppression without explicit intent
    assert len(result['surfaced_patterns']) == len(MOCK_PATTERNS)
    assert len(result['suppressed_patterns']) == 0
    
    print("✓ No inference: patterns surface without explicit intent")


def test_determinism():
    """Test that same input produces identical output"""
    input_data = {
        'patterns': MOCK_PATTERNS,
        'writer_intent': [
            {
                'scene_range': [0, 5],
                'intent': 'intentionally exhausting'
            }
        ]
    }
    
    result1 = intent.run(input_data)
    result2 = intent.run(input_data)
    
    assert result1 == result2, "Intent processing should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all intent immunity tests"""
    print("Running WriterIntentImmunityAgent tests...\n")
    
    test_no_intent_passthrough()
    test_full_suppression_with_intent()
    test_partial_overlap()
    test_invalid_intent_rejected()
    test_allowed_intents_only()
    test_no_inference()
    test_determinism()
    
    print("\n✅ All intent immunity tests passed!")


if __name__ == '__main__':
    run_all_tests()
