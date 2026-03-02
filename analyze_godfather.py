import os
import sys
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scriptpulse.pipeline import runner

filepath = "Godfather, The.txt"
if not os.path.exists(filepath):
    print(f"File {filepath} not found.")
    sys.exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Run pipeline
report = runner.run_pipeline(text, experimental_mode=True, moonshot_mode=True)

if not report:
    print("Pipeline returned None.")
else:
    print("REFLECTIONS:")
    for ref in report.get('reflections', []):
        print(f"Scenes {ref['scene_range'][0]}–{ref['scene_range'][1]}")
        print(ref['reflection'])
    if not report.get('reflections'):
        print(report.get('silence_explanation', "Attentional flow appears stable with regular recovery."))
