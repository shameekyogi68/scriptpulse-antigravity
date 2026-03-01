import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent

def run_test_case(name, text, expected_scenes):
    print(f"Testing: {name}")
    parser = ParsingAgent(use_ml=False) # Use heuristics for baseline consistency
    segmenter = SegmentationAgent()
    
    parsed = parser.run(text.strip())['lines']
    segmented = segmenter.run(parsed)
    
    actual_scenes = len(segmented)
    if actual_scenes == expected_scenes:
        print(f"✅ SUCCESS: Found {actual_scenes} scenes.")
    else:
        print(f"❌ FAILURE: Expected {expected_scenes}, found {actual_scenes}.")
        for i, s in enumerate(segmented):
            print(f"  Scene {i}: {s['heading']} (Lines {s['start_line']}-{s['end_line']})")
            for li in range(s['start_line'], s['end_line'] + 1):
                print(f"    [{parsed[li]['tag']}] {parsed[li]['text']}")
    print("-" * 20)
    return actual_scenes == expected_scenes

def stage3_validation():
    print("--- STAGE 3: STRUCTURAL PARSING ACCURACY ---")
    
    success = True
    
    # 1. Clean Hollywood
    hollywood = """
INT. COFFEE SHOP - DAY
JOHN sits alone. He checks his watch.
MARY enters.
MARY
Sorry I'm late.
JOHN
It's fine.

EXT. PARKING LOT - LATER
They walk to a car.
    """
    success &= run_test_case("Clean Hollywood", hollywood, 2)
    
    # 2. Messy Indie (Implicit Headings)
    indie = """
KITCHEN - DAY
Steam rises from a kettle.
MOM
Did you finish your homework?

LIVING ROOM - CONTINUOUS
TIMMY ignores her. He plays video games.
    """
    success &= run_test_case("Messy Indie", indie, 2)
    
    # 3. Mixed INT/EXT
    mixed = """
INT/EXT. TOYOTA - MOVING - NIGHT
Rain lashes the windshield.
    """
    success &= run_test_case("Mixed INT/EXT", mixed, 1)

    # 4. Merging Rules (Headless fragment)
    merging = """
INT. HOUSE - DAY
John is here.

More action happens here.
This is another paragraph.
    """
    success &= run_test_case("Merging Rules (No heading)", merging, 1)

    # 5. Missing Headings (Dialogue Only)
    headless = """
JOHN
Where are we?
MARY
In the void.
    """
    success &= run_test_case("Missing Headings", headless, 1)

    if success:
        print("\n🏆 STAGE 3 PASSED: All structural parsing cases validated.")
    else:
        print("\n⚠️ STAGE 3 FAILED: Some structural cases did not parse as expected.")
        sys.exit(1)

if __name__ == "__main__":
    stage3_validation()
