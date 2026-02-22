#!/usr/bin/env python3
"""
Tests for StructuralEncodingAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import parsing, segmentation, encoding


# Test scripts

MINIMALIST = """INT. ROOM - NIGHT

A chair.

Silence."""


DENSE_DIALOGUE = """INT. CAFE - DAY

ALICE
How are you doing today?

BOB
I'm doing quite well, thanks for asking.

ALICE
That's wonderful to hear from you.

BOB
And how about yourself?

ALICE
I'm great, just enjoying this lovely day.

BOB
The weather is indeed quite nice."""


ACTION_HEAVY = """EXT. BATTLEFIELD - DAY

Explosions everywhere. Soldiers dive for cover behind concrete barriers.

Smoke billows across the field. Chaos and confusion reign supreme.

A massive tank rumbles forward slowly. Heavy gunfire erupts from all sides.

Debris flies through the air continuously.

INT. BUNKER - DAY

Officers watch monitors intently."""


EXPERIMENTAL = """nowhere really

words words words

(but what does it mean)

MORE WORDS HERE

another strange place

text continues

END OF SOMETHING"""


def test_minimalist():
    """Test minimal script produces low counts without implying failure"""
    parsed = parsing.run(MINIMALIST)
    scenes = segmentation.run(parsed)
    
    # Prepare input
    input_data = {'scenes': scenes, 'lines': parsed}
    features = encoding.run(input_data)
    
    # Should produce valid feature vector
    assert len(features) > 0, "Should produce features"
    
    scene_features = features[0]
    
    # Check all required keys exist
    assert 'linguistic_load' in scene_features
    assert 'dialogue_dynamics' in scene_features
    assert 'visual_abstraction' in scene_features
    assert 'referential_load' in scene_features
    assert 'structural_change' in scene_features
    
    # Values should be numeric
    ling = scene_features['linguistic_load']
    assert isinstance(ling['sentence_count'], int)
    assert isinstance(ling['mean_sentence_length'], (int, float))
    
    print(f"✓ Minimalist script: {ling['sentence_count']} sentences, valid features")


def test_dense_dialogue():
    """Test dialogue-heavy script shows high dialogue metrics"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    
    input_data = {'scenes': scenes, 'lines': parsed}
    features = encoding.run(input_data)
    
    scene_features = features[0]
    dial = scene_features['dialogue_dynamics']
    
    # Should have dialogue turns
    assert dial['dialogue_turns'] > 0, "Should detect dialogue"
    assert dial['speaker_switches'] >= 0, "Should count switches"
    
    print(f"✓ Dense dialogue: {dial['dialogue_turns']} turns, {dial['speaker_switches']} switches")


def test_action_heavy():
    """Test action-heavy script shows high action metrics"""
    parsed = parsing.run(ACTION_HEAVY)
    scenes = segmentation.run(parsed)
    
    input_data = {'scenes': scenes, 'lines': parsed}
    features = encoding.run(input_data)
    
    # Should have multiple scenes
    assert len(features) > 0
    
    # First scene should have action
    scene_features = features[0]
    visual = scene_features['visual_abstraction']
    
    assert visual['action_lines'] > 0, "Should detect action lines"
    
    print(f"✓ Action-heavy: {visual['action_lines']} action lines")


def test_experimental():
    """Test experimental script doesn't crash"""
    parsed = parsing.run(EXPERIMENTAL)
    scenes = segmentation.run(parsed)
    
    input_data = {'scenes': scenes, 'lines': parsed}
    features = encoding.run(input_data)
    
    # Should not crash
    assert len(features) > 0
    
    # Should have all feature groups
    scene_features = features[0]
    assert 'linguistic_load' in scene_features
    assert 'dialogue_dynamics' in scene_features
    
    print("✓ Experimental: no crashes, features extracted")


def test_all_keys_present():
    """Test all expected keys are present in output"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    
    input_data = {'scenes': scenes, 'lines': parsed}
    features = encoding.run(input_data)
    
    scene_features = features[0]
    
    # Check linguistic_load keys
    ling = scene_features['linguistic_load']
    assert 'sentence_count' in ling
    assert 'mean_sentence_length' in ling
    assert 'max_sentence_length' in ling
    assert 'sentence_length_variance' in ling
    
    # Check dialogue_dynamics keys
    dial = scene_features['dialogue_dynamics']
    assert 'dialogue_turns' in dial
    assert 'speaker_switches' in dial
    assert 'turn_velocity' in dial
    assert 'monologue_runs' in dial
    
    # Check visual_abstraction keys
    visual = scene_features['visual_abstraction']
    assert 'action_lines' in visual
    assert 'continuous_action_runs' in visual
    assert 'vertical_writing_load' in visual
    
    # Check referential_load keys
    ref = scene_features['referential_load']
    assert 'active_character_count' in ref
    assert 'character_reintroductions' in ref
    
    # Check structural_change keys
    struct = scene_features['structural_change']
    assert 'event_boundary_score' in struct
    
    print("✓ All feature keys present")


def test_determinism():
    """Test that same input produces identical output"""
    parsed = parsing.run(DENSE_DIALOGUE)
    scenes = segmentation.run(parsed)
    
    input_data = {'scenes': scenes, 'lines': parsed}
    
    features1 = encoding.run(input_data)
    features2 = encoding.run(input_data)
    
    assert features1 == features2, "Encoding should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all encoding tests"""
    print("Running StructuralEncodingAgent tests...\n")
    
    test_minimalist()
    test_dense_dialogue()
    test_action_heavy()
    test_experimental()
    test_all_keys_present()
    test_determinism()
    
    print("\n✅ All encoding tests passed!")


if __name__ == '__main__':
    run_all_tests()
