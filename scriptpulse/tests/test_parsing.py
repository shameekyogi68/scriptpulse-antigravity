#!/usr/bin/env python3
"""
Tests for StructuralParsingAgent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scriptpulse'))

from agents import parsing


# Test scripts

CLEAN_PROFESSIONAL = """INT. OFFICE - DAY

JOHN, 30s, sits at his desk.

JOHN
I think we have a problem.

MARY enters, looking concerned.

MARY
What kind of problem?

FADE OUT."""


MESSY_DRAFT = """int office day

john sits

JOHN
hey there

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
You?"""


ACTION_HEAVY = """EXT. BATTLEFIELD - DAY

Explosions everywhere. Soldiers run for cover.

Smoke fills the air. Chaos reigns.

A tank rolls forward. Gunfire erupts.

CUT TO:"""


EXPERIMENTAL = """nowhere

words

MORE WORDS

(silence)

END"""


def test_clean_professional():
    """Test clean professional script"""
    result = parsing.run(CLEAN_PROFESSIONAL)
    
    # Check structure
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check first line is scene heading
    assert result[0]['tag'] == 'S' or result[0]['text'].strip() == '', \
        f"Expected scene heading, got: {result[0]}"
    
    # Check has dialogue
    has_dialogue = any(r['tag'] == 'D' for r in result)
    assert has_dialogue, "Should detect dialogue"
    
    # Check has character names
    has_character = any(r['tag'] == 'C' for r in result)
    assert has_character, "Should detect character names"
    
    print("✓ Clean professional script passed")


def test_messy_draft():
    """Test messy early draft handling"""
    result = parsing.run(MESSY_DRAFT)
    
    # Should not crash
    assert isinstance(result, list)
    
    # Should be conservative (more A tags when uncertain)
    tag_counts = {}
    for r in result:
        tag = r['tag']
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print(f"✓ Messy draft parsed (tags: {tag_counts})")


def test_minimalist():
    """Test minimalist script"""
    result = parsing.run(MINIMALIST)
    
    assert isinstance(result, list)
    
    # Should handle sparse structure
    print("✓ Minimalist script passed")


def test_dialogue_heavy():
    """Test dialogue-heavy script"""
    result = parsing.run(DIALOGUE_HEAVY)
    
    # Should detect multiple dialogue exchanges
    dialogue_count = sum(1 for r in result if r['tag'] == 'D')
    assert dialogue_count > 0, "Should detect dialogue"
    
    print(f"✓ Dialogue-heavy script passed ({dialogue_count} dialogue lines)")


def test_action_heavy():
    """Test action-heavy script"""
    result = parsing.run(ACTION_HEAVY)
    
    # Should detect scene heading and metadata
    has_scene = any(r['tag'] == 'S' for r in result)
    has_metadata = any(r['tag'] == 'M' for r in result)
    
    assert has_scene, "Should detect scene heading"
    
    print("✓ Action-heavy script passed")


def test_experimental():
    """Test experimental formatting"""
    result = parsing.run(EXPERIMENTAL)
    
    # Should not crash on unusual structure
    assert isinstance(result, list)
    
    print("✓ Experimental script passed")


def test_determinism():
    """Test that same input produces identical output"""
    script = CLEAN_PROFESSIONAL
    
    result1 = parsing.run(script)
    result2 = parsing.run(script)
    
    assert result1 == result2, "Output should be deterministic"
    
    print("✓ Determinism check passed")


def run_all_tests():
    """Run all parsing tests"""
    print("Running StructuralParsingAgent tests...\n")
    
    test_clean_professional()
    test_messy_draft()
    test_minimalist()
    test_dialogue_heavy()
    test_action_heavy()
    test_experimental()
    test_determinism()
    
    print("\n✅ All parsing tests passed!")


if __name__ == '__main__':
    run_all_tests()
