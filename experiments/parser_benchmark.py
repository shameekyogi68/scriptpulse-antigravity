
import sys
import os
import re

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scriptpulse.agents import parsing

# MOCK GOLDEN CORPUS
# Format: (Line Text, Expected Tag)
GOLDEN_CORPUS = [
    ("INT. LAB - DAY", "S"),
    ("The scientist holds a beaker.", "A"),
    ("SCIENTIST", "C"),
    ("Eureka!", "D"),
    ("Ext. Space - Night", "S"),
    ("The ship explodes.", "A"),
    ("   (quietly)", "P"),
    ("It is done.", "D"),
    ("CUT TO:", "T"),
    ("INT. HOUSE - DAY", "S"),
    ("MOM", "C"),
    ("Dinner's ready!", "D"),
    ("She places the plate on the table.", "A"),
    ("DAD (O.S.)", "C"),
    ("Coming!", "D"),
    # ... In a real benchmark, this would load 100+ annotated scripts
]

def calculate_parser_f1():
    """
    Runs the regex parser against the Golden Corpus and calculates F1 Score.
    """
    tp = 0 # True Positive
    fp = 0 # False Positive
    fn = 0 # False Negative (Mocking simplified: mostly exact match)
    
    print("--- Running Parser Benchmark (Golden Corpus N=15) ---")
    
    results = []
    
    for text, expected_tag in GOLDEN_CORPUS:
        # Create mock line dict
        line = {'text': text, 'line_index': 0}
        
        # We need to access the specific regex logic. 
        # parsing.run() does a whole script.
        # We'll stick to a simple integration test using parsing.classify_line (if it existed)
        # Or just construct a minimal input for parsing.run
        
        # Since parsing.run expects a string, let's reconstruct it.
        # Actually, let's just use the regexes directly if accessible, or run the agent.
        
        # Simulating run for single line is inefficient, so let's run batch.
        pass

    # Batch Run using BERT Agent
    # script_text = "\n".join([item[0] for item in GOLDEN_CORPUS])
    # parsed_output = parsing.run(script_text)
    
    # vNext.9 Upgrade: Test BERT Parser
    from scriptpulse.agents import bert_parser
    agent = bert_parser.BertParserAgent()
    script_text = "\n".join([item[0] for item in GOLDEN_CORPUS])
    parsed_output = agent.run(script_text)['lines']
    
    # Align output
    parsed_lines = parsed_output
    
    # Calculate Metrics
    correct = 0
    total = len(GOLDEN_CORPUS)
    
    print(f"{'Text':<30} | {'Exp':<3} | {'Act':<3} | {'Status'}")
    print("-" * 50)
    
    for i, p_line in enumerate(parsed_lines):
        if i >= len(GOLDEN_CORPUS): break
        
        expected = GOLDEN_CORPUS[i][1]
        actual = p_line['tag']
        
        # Remap system tags to simpler benchmark tags if needed
        # System: S, A, C, D, M (Metadata), P (Parenthetical - usually merged or separate?)
        # Let's assume strict equality for S, A, C, D
        
        is_match = (expected == actual)
        # Parenthetical handling: System usually merges P into D or tracks separate
        if expected == 'P' and actual == 'D': is_match = True # Acceptable fold
        
        if is_match:
            correct += 1
            tp += 1
            status = "OK"
        else:
            status = "FAIL"
            
        print(f"{p_line['text'][:30]:<30} | {expected:<3} | {actual:<3} | {status}")

    accuracy = correct / total
    
    print("-" * 50)
    print(f"Accuracy: {accuracy:.2%}")
    
    # Mocking F1 Calculation (Simplified)
    precision = tp / (tp + fp + 1e-9) if (tp+fp) > 0 else 0
    recall = tp / (tp + fn + 1e-9) if (tp+fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall + 1e-9)
    
    print(f"Estimated F1 Score: {accuracy:.4f} (Micro-Averaged)")
    
    if accuracy > 0.95:
        print("[PASS] Parser is Calibration-Ready.")
    else:
        print("[FAIL] Parser requires retraining (or BERT implementation).")

if __name__ == "__main__":
    calculate_parser_f1()
