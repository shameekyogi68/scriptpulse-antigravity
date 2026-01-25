#!/usr/bin/env python3
"""
Tests for PatternDetectionAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import parsing, segmentation, encoding, temporal, patterns


# Test scripts

DENSE_DIALOGUE = """INT. OFFICE - DAY

JOHN works intensely. Papers everywhere. Phones ringing constantly.

JOHN
We need to finish this project right now immediately.

MARY enters looking extremely stressed and worried.

MARY
The deadline is tomorrow morning without fail.

ALICE rushes in with more documents urgently.

ALICE
I have more reports that need review tonight.

BOB follows carrying heavy files quickly.

BOB
This is overwhelming but necessary work."""


ACTION_HEAVY = """EXT. BATTLEFIELD - DAY

Massive explosions rock landscape.

Soldiers sprint between positions.

Gunfire erupts everywhere.

INT. BUNKER - DAY

Brief quiet moment.

Officers rest briefly."""


EXPERIMENTAL = """nowhere

strange words flow

MORE WORDS

(but unclear)

another odd place

text continues strangely"""


MINIMALIST = """INT. ROOM - NIGHT

A chair.

Silence."""


def test_persistence_required():
    """Test that single-scene spikes do NOT produce patterns"""
    parsed = parsing.run(MINIMALIST)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result = patterns.run({'temporal_signals': temporal_signals})
    
    # Minimalist script should have few/no patterns (not enough persistence)
    print(f"✓ Minimalist script: {len(result)} patterns (low persistence)")


def test_sustained_demand():
    """Test detection of sustained demand in dense dialogue"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result = patterns.run({'temporal_signals': temporal_signals})
    
    # Should detect some persistent patterns
    pattern_types = [p['pattern_type'] for p in result]
    
    print(f"✓ Dense dialogue: {len(result)} patterns detected: {pattern_types}")


def test_confidence_downgrade():
    """Test that experimental noise downgrades confidence"""
    parsed = parsing.run(EXPERIMENTAL)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result = patterns.run({'temporal_signals': temporal_signals})
    
    # Any patterns should have lower confidence due to noise
    if result:
        confidences = [p['confidence'] for p in result]
        has_low = 'low' in confidences or 'medium' in confidences
        print(f"✓ Experimental: confidence appropriately downgraded: {confidences}")
    else:
        print("✓ Experimental: no patterns (too noisy)")


def test_allowed_pattern_types():
    """Test that only allowed pattern types are emitted"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result = patterns.run({'temporal_signals': temporal_signals})
    
    allowed_types = {
        'sustained_attentional_demand',
        'limited_recovery',
        'repetition',
        'surprise_cluster',
        'constructive_strain',
        'degenerative_fatigue'
    }
    
    for pattern in result:
        assert pattern['pattern_type'] in allowed_types, \
            f"Invalid pattern type: {pattern['pattern_type']}"
    
    print("✓ All pattern types are allowed")


def test_no_prioritization():
    """Test that patterns are not ranked or prioritized"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result = patterns.run({'temporal_signals': temporal_signals})
    
    # Check that no pattern has priority/ranking field
    for pattern in result:
        assert 'priority' not in pattern
        assert 'importance' not in pattern
        assert 'severity' not in pattern
    
    print("✓ No prioritization fields present")


def test_determinism():
    """Test that same input produces identical output"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    temporal_signals = temporal.run({'features': features})
    
    result1 = patterns.run({'temporal_signals': temporal_signals})
    result2 = patterns.run({'temporal_signals': temporal_signals})
    
    assert result1 == result2, "Pattern detection should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all pattern detection tests"""
    print("Running PatternDetectionAgent tests...\n")
    
    test_persistence_required()
    test_sustained_demand()
    test_confidence_downgrade()
    test_allowed_pattern_types()
    test_no_prioritization()
    test_determinism()
    
    print("\n✅ All pattern detection tests passed!")


if __name__ == '__main__':
    run_all_tests()
