"""
Test Suite for Universal Screenplay Format Support.
Verifies normalizer + parser pipeline on messy scripts.
"""
import pytest
import sys
import os

# Ensure import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scriptpulse import runner

def test_mixed_case_headings():
    print("\nTesting Mixed Case Headings...")
    script = """
    int. room - day
    A man walks in.
    exterior garden - night
    He leaves.
    """
    # Explicitly disable resource/safety logic to ensure pure logic test
    # But runner defaults are fine. cpu_safe_mode=True for speed.
    output = runner.run_pipeline(script, cpu_safe_mode=True, experimental_mode=False)
    
    scenes = output['scene_info']
    print(f"Scenes Detected: {len(scenes)}")
    for s in scenes:
        print(f"  - {s['heading']}")
        
    assert len(scenes) >= 2
    assert "INT. ROOM" in scenes[0]['heading']
    assert "EXT. GARDEN" in scenes[1]['heading']

def test_inline_dialogue():
    print("\nTesting Inline Dialogue (NAME: Text)...")
    script = """
    INT. CAFE - DAY
    JOHN: Hello there.
    mary: Hi John.
    """
    output = runner.run_pipeline(script, cpu_safe_mode=True)
    # We can't easily inspect internal structure, but we can verify it runs
    # and maybe check if 'dialogue' count in metrics (if exposed) is > 0?
    # runner output has 'metrics'? 
    # scene_info has preview.
    scenes = output['scene_info']
    assert len(scenes) == 1
    print(f"Preview: {scenes[0]['preview']}")
    # Preview should ideally show the dialogue
    
def test_loose_indentation():
    print("\nTesting Loose Indentation...")
    script = """
INT. OFFICE - DAY
No indentation at all.
BOSS
You're fired.
    """
    output = runner.run_pipeline(script, cpu_safe_mode=True)
    assert len(output['scene_info']) == 1

def test_prose_style():
    print("\nTesting Prose Style (No Format)...")
    script = """
    Just a bunch of text.
    No clear format.
    Is it a scene?
    Maybe.
    """
    output = runner.run_pipeline(script, cpu_safe_mode=True)
    # Should produce at least 1 scene (Scene 1 default)
    assert len(output['scene_info']) >= 1
    print(f"Heading: {output['scene_info'][0]['heading']}")

def test_messy_mixed_bag():
    print("\nTesting Messy Mixed Bag...")
    script = """
    interior: spaceship
    alien: take me to your leader.
    ext. space - continuous
    Ships fly.
    """
    output = runner.run_pipeline(script, cpu_safe_mode=True)
    scenes = output['scene_info']
    assert len(scenes) >= 2
    # Check normalized header
    print(f"Heading: {scenes[0]['heading']}")
    assert "INT. SPACESHIP" in scenes[0]['heading']
    
if __name__ == "__main__":
    # Manual run if executed directly
    try:
        test_mixed_case_headings()
        test_inline_dialogue()
        test_loose_indentation()
        test_prose_style()
        test_messy_mixed_bag()
        print("\n✅ ALL TESTS PASSED")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
