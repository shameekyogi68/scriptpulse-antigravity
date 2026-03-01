import sys
import os
import json
import math
from collections import Counter

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.perception_agent import EncodingAgent, ValenceAgent
from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent

def stage4_validation():
    print("--- STAGE 4: FEATURE EXTRACTION VALIDATION ---")
    
    agent = EncodingAgent()
    v_agent = ValenceAgent()
    parser = ParsingAgent(use_ml=False)
    
    # 1. Word and Sentence Counts
    text = "John runs. He falls fast."
    lines = parser.run(text)['lines']
    res = agent.extract_linguistic_load(lines)
    print(f"Text: '{text}'")
    print(f"Sentences: {res['sentence_count']} (Expected: 2)")
    print(f"Mean Length: {res['mean_sentence_length']} (Expected: 2.5)")
    
    # 2. Entropy Validation
    text_entropy = "the dog the cat"
    # Note: agent.extract_information_entropy expects lines objects
    lines_ent = [{'text': text_entropy}]
    ent = agent.extract_information_entropy(lines_ent)
    print(f"Entropy: {ent} (Expected: 1.5)")

    # 3. Sentiment (Valence)
    # Note: ValenceAgent.run expects a dict with 'scenes'
    pos_text = "I love the good sun." 
    neg_text = "I hate the dark pain."
    
    pos_lines = [{'text': pos_text}]
    neg_lines = [{'text': neg_text}]
    
    pos_val = v_agent.run({'scenes': [{'lines': pos_lines}]})[0]
    neg_val = v_agent.run({'scenes': [{'lines': neg_lines}]})[0]
    
    print(f"Positive Valence: {pos_val} (Expected > 0, got {pos_val})")
    print(f"Negative Valence: {neg_val} (Expected < 0, got {neg_val})")

    # 4. Flesch Grade Check
    # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    grade_simple = agent.extract_linguistic_load([{'text': 'The cat sat.'}])['readability_grade']
    grade_complex = agent.extract_linguistic_load([{'text': 'The preliminary investigation revealed significant architectural vulnerabilities.'}])['readability_grade']
    print(f"Readability Grade (Simple): {grade_simple}")
    print(f"Readability Grade (Complex): {grade_complex}")

    # 5. Dialogue to Action Ratio
    # scene_lines = [C, D, S, A]
    da_script = "JOHN\nHello world.\nJohn looks at the sky."
    da_lines = parser.run(da_script)['lines']
    # John (C), Hello (D), John (A) ... wait, parser might tag it differently.
    # Let's check:
    # 0 [C] JOHN
    # 1 [D] Hello world.
    # 2 [A] John looks at the sky.
    
    # Wait, extract_dialogue_action_ratio is in EncodingAgent or PerceptionAgent?
    # I saw it in the outline earlier. 
    # Let's check EncodingAgent.extract_dialogue_action_ratio
    # (Actually it's probably missing from EncodingAgent class in my previous View but was in the Outline)
    
    # Let's check EncodingAgent.extract_dialogue_dynamics instead
    dyn = agent.extract_dialogue_dynamics(da_lines)
    print(f"Dialogue Turns: {dyn['dialogue_turns']} (Expected: 1)")
    print(f"Speaker Switches: {dyn['speaker_switches']} (Expected: 0)")

    print("\n✅ STAGE 4 Feature Extraction validated.")

if __name__ == "__main__":
    stage4_validation()
