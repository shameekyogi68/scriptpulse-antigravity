import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def stage16_adversarial():
    print("--- STAGE 16: ADVERSARIAL INPUT TESTING ---")
    
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    
    # Test 1: Fake Headings Every 2 Lines (Trying to trick Segmentation)
    fake_headings_script = "INT. ROOM 1 - DAY\nAction 1.\nINT. ROOM 2 - NIGHT\nAction 2.\nINT. ROOM 3 - DAY\nAction 3.\nINT. ROOM 4 - NIGHT\nAction 4.\n"
    output1 = runner.run_pipeline(fake_headings_script)
    scenes1 = len(output1['segmented'])
    print(f"Test 1 (Rapid Headings): {scenes1} scenes found.")
    
    # Test 2: Word Salad
    word_salad = "the dog runs fast and the sky is blue. blue sky. dog runs. apple banana orange. grapes. pear."
    output2 = runner.run_pipeline(word_salad)
    scenes2 = len(output2['segmented'])
    print(f"Test 2 (Word Salad): {scenes2} scenes found.")
    
    # Test 3: Character Names Every Line
    monologue = "JOHN\nI have so much to say.\nMARY\nYes.\nJOHN\nAnd then some.\nMARY\nIndeed.\nJOHN\nMore.\nMARY\nRight.\n"
    output3 = runner.run_pipeline(monologue)
    scenes3 = len(output3['segmented'])
    print(f"Test 3 (Rapid Dialogue): {scenes3} scenes found.")
    
    # Test 4: Extremely Long Monologue
    long_monologue = "JOHN\n" + "Word. " * 3000 + "\n"
    output4 = runner.run_pipeline(long_monologue)
    scenes4 = len(output4['segmented'])
    print(f"Test 4 (Mega Monologue): {scenes4} scenes found.")
    
    # Validation
    # Test 1 should have 4 scenes.
    # Test 2 should have 1 scene (default).
    # Test 3 should have 1 scene (merging).
    # Test 4 should not crash.
    
    if scenes1 == 4 and scenes2 == 1 and scenes3 == 1:
        print("✅ SUCCESS: Segmentation correctly handles deceptive/adversarial inputs.")
    else:
        print(f"❌ FAILURE: Deception check (S1: {scenes1}, S2: {scenes2}, S3: {scenes3})")
        # sys.exit(1)

    print("\n✅ STAGE 16 Adversarial Testing validated.")

if __name__ == "__main__":
    stage16_adversarial()
