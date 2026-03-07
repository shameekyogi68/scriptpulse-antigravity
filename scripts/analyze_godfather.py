#!/usr/bin/env python3
"""
Research Grade Showcase: Analyzing 'The Godfather' using ScriptPulse v15.0 Gold
"""

import os
import sys
from datetime import datetime

# Ensure project root is in path
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scriptpulse.pipeline import runner
from scriptpulse.reporters import writer_report

def main():
    print("==============================================================")
    print("🎬  SCRIPTPULSE v15.0 GOLD MASTER — RESEARCH SHOWCASE")
    print("    Project: THE GODFATHER (Crime/Drama)")
    print("==============================================================")

    filepath = os.path.join(ROOT_DIR, "data", "samples", "Godfather, The.txt")
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} not found.")
        return

    # 1. READ
    print(f"\n[1/3] Reading screenplay source...")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 2. RUN PIPELINE
    print(f"[2/3] Running Cognitive Simulation (Genre: Drama)...")
    _t_start = datetime.now()
    
    # We use 'Drama' genre to trigger the lambda=0.90, beta=0.25 priors
    report = runner.run_pipeline(text, genre='Drama')
    
    _t_end = datetime.now()
    duration = (_t_end - _t_start).total_seconds()
    
    # 3. GENERATE REPORT
    print(f"[3/3] Generating Intelligence Report ({duration:.2f}s)...")
    
    md_report = writer_report.generate_writer_report(
        report, 
        title="The Godfather", 
        genre="Drama"
    )
    
    # 4. OUTPUT
    output_file = "GODFATHER_INSIGHT_v15.md"
    with open(output_file, "w") as f:
        f.write(md_report)

    print(f"\n✅ SUCCESS: Research Report generated at: {output_file}")
    print("\n[PREVIEW OF NARRATIVE DIAGNOSIS]")
    print("-" * 30)
    diagnosis = report.get('writer_intelligence', {}).get('narrative_diagnosis', [])
    for d in diagnosis[:5]:
        print(f" • {d}")
    print("-" * 30)

if __name__ == "__main__":
    main()
