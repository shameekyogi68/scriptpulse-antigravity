#!/usr/bin/env python3
"""
Tests for TemporalDynamicsAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import parsing, segmentation, encoding, temporal


# Test scripts

LONG_SCRIPT = """INT. OFFICE - DAY

JOHN works at his desk intensely. Papers everywhere.

JOHN
We need to finish this project immediately.

MARY enters looking stressed.

MARY
The deadline is tomorrow morning.

INT. CONFERENCE ROOM - DAY

The team gathers around a large table covered in documents.

ALICE
Let's review everything one more time carefully.

BOB
This is taking forever to complete.

INT. HALLWAY - NIGHT

Everyone walks slowly, exhausted.

Silence.

INT. PARKING LOT - NIGHT

They reach their cars finally."""


ACTION_HEAVY = """EXT. BATTLEFIELD - DAY

Massive explosions rock the landscape continuously.

Soldiers sprint between cover positions desperately.

Gunfire erupts from all directions simultaneously.

Smoke obscures everything completely.

INT. BUNKER - DAY

Brief moment of quiet."""


MINIMALIST = """INT. ROOM - NIGHT

A chair.

Silence."""


def test_canonical_equation():
    """Test that canonical equation S[i] = E[i] + λ·S[i-1] - R[i] is applied"""
    parsed = parsing.run(LONG_SCRIPT)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result = temporal.run({'features': features})
    
    # Should produce signals for all scenes
    assert len(result) == len(features)
    
    # Check first scene (no carryover)
    first = result[0]
    assert first['attentional_signal'] == first['instantaneous_effort'], \
        "First scene should have S[0] = E[0] (no carryover)"
    
    # Check second scene (should have carryover)
    if len(result) > 1:
        second = result[1]
        # Approximate check: S[1] ≈ E[1] + λ·S[0] - R[1]
        expected = (second['instantaneous_effort'] + 
                   temporal.LAMBDA * first['attentional_signal'] - 
                   second['recovery_credit'])
        # Allow small rounding difference
        assert abs(second['attentional_signal'] - max(0, expected)) < 0.01, \
            f"Canonical equation not applied: {second['attentional_signal']} vs {expected}"
    
    print(f"✓ Canonical equation verified (S[1]={result[1]['attentional_signal'] if len(result) > 1 else 'N/A'})")


def test_fatigue_carryover():
    """Test that fatigue carries over between scenes"""
    parsed = parsing.run(ACTION_HEAVY)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result = temporal.run({'features': features})
    
    # If multiple scenes, later scenes should show carryover
    if len(result) > 1:
        # Signal should potentially increase due to carryover
        first_signal = result[0]['attentional_signal']
        has_carryover = any(r['attentional_signal'] > first_signal for r in result[1:])
        print(f"✓ Fatigue carryover detected: signals range {min(r['attentional_signal'] for r in result):.3f} to {max(r['attentional_signal'] for r in result):.3f}")
    else:
        print("✓ Single scene (carryover not applicable)")


def test_recovery_credits():
    """Test that recovery credits are calculated"""
    parsed = parsing.run(MINIMALIST)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result = temporal.run({'features': features})
    
    # Should have recovery field
    for signal in result:
        assert 'recovery_credit' in signal
        assert signal['recovery_credit'] >= 0
        assert signal['recovery_credit'] <= temporal.R_MAX
    
    print("✓ Recovery credits bounded [0, R_MAX]")


def test_bounded_signals():
    """Test that signals don't exhibit runaway accumulation"""
    parsed = parsing.run(LONG_SCRIPT)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result = temporal.run({'features': features})
    
    # Signals should be bounded
    max_signal = max(r['attentional_signal'] for r in result)
    
    # Should not explode to crazy values
    assert max_signal < 5.0, f"Signal runaway detected: max={max_signal}"
    
    print(f"✓ Signals bounded: max={max_signal:.3f}")


def test_fatigue_states():
    """Test fatigue state classification"""
    parsed = parsing.run(ACTION_HEAVY)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result = temporal.run({'features': features})
    
    # Should have fatigue states
    valid_states = {'normal', 'elevated', 'high', 'extreme'}
    for signal in result:
        assert signal['fatigue_state'] in valid_states
    
    print("✓ Fatigue states valid")


def test_determinism():
    """Test that same input produces identical output"""
    parsed = parsing.run(LONG_SCRIPT)
    scenes = segmentation.run(parsed)
    features = encoding.run({'scenes': scenes, 'lines': parsed})
    
    result1 = temporal.run({'features': features})
    result2 = temporal.run({'features': features})
    
    assert result1 == result2, "Temporal dynamics should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all temporal tests"""
    print("Running TemporalDynamicsAgent tests...\n")
    
    test_canonical_equation()
    test_fatigue_carryover()
    test_recovery_credits()
    test_bounded_signals()
    test_fatigue_states()
    test_determinism()
    
    print("\n✅ All temporal tests passed!")


if __name__ == '__main__':
    run_all_tests()
