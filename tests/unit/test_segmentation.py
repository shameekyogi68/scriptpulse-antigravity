#!/usr/bin/env python3
"""
Tests for SceneSegmentationAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import parsing, segmentation


# Test scripts (reusing from parsing tests)

CLEAN_PROFESSIONAL = """INT. OFFICE - DAY

JOHN, 30s, sits at his desk.

JOHN
I think we have a problem.

INT. HALLWAY - DAY

MARY walks down the corridor.

EXT. PARKING LOT - DAY

Cars everywhere."""


MESSY_DRAFT = """int office day

john sits

JOHN
hey there

some room

mary walks in

mary
what's up?"""


MINIMALIST = """INT. ROOM - NIGHT

A chair.

Silence."""


DIALOGUE_HEAVY = """INT. CAFE - DAY

ALICE
How are you?

BOB
I'm fine, thanks.

ALICE
That's good to hear.

BOB
You?

ALICE
Great!"""


ACTION_HEAVY = """EXT. BATTLEFIELD - DAY

Explosions everywhere. Soldiers run for cover.

Smoke fills the air. Chaos reigns.

A tank rolls forward. Gunfire erupts.

INT. COMMAND CENTER - DAY

Officers monitor screens."""


EXPERIMENTAL = """nowhere

words

MORE WORDS

(silence)

another place maybe

some text

END"""


def test_clean_professional():
    """Test clean professional script segmentation"""
    parsed = parsing.run(CLEAN_PROFESSIONAL)
    scenes = segmentation.run(parsed)
    
    # Should create multiple scenes (3 INT/EXT headings)
    assert len(scenes) >= 2, f"Expected multiple scenes, got {len(scenes)}"
    
    # Check scene structure
    for scene in scenes:
        assert 'scene_index' in scene
        assert 'start_line' in scene
        assert 'end_line' in scene
        assert 'boundary_confidence' in scene
    
    # Check no gaps/overlaps
    for i in range(len(scenes) - 1):
        assert scenes[i]['end_line'] + 1 == scenes[i + 1]['start_line'], \
            "Scenes must be adjacent"
    
    print(f"✓ Clean professional: {len(scenes)} scenes")


def test_messy_draft_conservative():
    """Test that messy drafts produce fewer scenes (conservative)"""
    parsed = parsing.run(MESSY_DRAFT)
    scenes = segmentation.run(parsed)
    
    # Should be conservative - likely 1-2 scenes max
    assert len(scenes) <= 3, f"Too many scenes ({len(scenes)}) for messy draft"
    
    print(f"✓ Messy draft: {len(scenes)} scenes (conservative)")


def test_minimalist():
    """Test minimalist script"""
    parsed = parsing.run(MINIMALIST)
    scenes = segmentation.run(parsed)
    
    # Should handle minimal structure
    assert len(scenes) >= 1
    
    print(f"✓ Minimalist: {len(scenes)} scene(s)")


def test_dialogue_heavy():
    """Test dialogue-heavy script doesn't over-segment"""
    parsed = parsing.run(DIALOGUE_HEAVY)
    scenes = segmentation.run(parsed)
    
    # Should remain as single scene (no scene headings mid-dialogue)
    assert len(scenes) <= 2, f"Dialogue should not cause over-segmentation: {len(scenes)} scenes"
    
    print(f"✓ Dialogue-heavy: {len(scenes)} scene(s)")


def test_action_heavy():
    """Test action-heavy script segments properly"""
    parsed = parsing.run(ACTION_HEAVY)
    scenes = segmentation.run(parsed)
    
    # Should detect 2 scenes (EXT + INT)
    assert len(scenes) >= 1
    
    print(f"✓ Action-heavy: {len(scenes)} scenes")


def test_experimental():
    """Test experimental formatting doesn't explode"""
    parsed = parsing.run(EXPERIMENTAL)
    scenes = segmentation.run(parsed)
    
    # Conservative behavior - should not over-segment
    assert len(scenes) <= 3, f"Experimental should remain conservative: {len(scenes)} scenes"
    
    print(f"✓ Experimental: {len(scenes)} scene(s)")


def test_no_orphaned_lines():
    """Test that all lines belong to exactly one scene"""
    parsed = parsing.run(CLEAN_PROFESSIONAL)
    scenes = segmentation.run(parsed)
    
    # Count total lines covered
    total_lines = len(parsed)
    covered_lines = set()
    
    for scene in scenes:
        for line_idx in range(scene['start_line'], scene['end_line'] + 1):
            assert line_idx not in covered_lines, f"Line {line_idx} appears in multiple scenes"
            covered_lines.add(line_idx)
    
    assert len(covered_lines) == total_lines, "Not all lines are covered by scenes"
    
    print("✓ No orphaned lines")


def test_determinism():
    """Test that same input produces identical output"""
    parsed = parsing.run(CLEAN_PROFESSIONAL)
    
    scenes1 = segmentation.run(parsed)
    scenes2 = segmentation.run(parsed)
    
    assert scenes1 == scenes2, "Segmentation should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all segmentation tests"""
    print("Running SceneSegmentationAgent tests...\n")
    
    test_clean_professional()
    test_messy_draft_conservative()
    test_minimalist()
    test_dialogue_heavy()
    test_action_heavy()
    test_experimental()
    test_no_orphaned_lines()
    test_determinism()
    
    print("\n✅ All segmentation tests passed!")


if __name__ == '__main__':
    run_all_tests()
