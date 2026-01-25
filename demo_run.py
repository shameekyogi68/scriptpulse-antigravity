#!/usr/bin/env python3
"""
ScriptPulse vNext.4 - Live Demonstration
"""

import sys
import os
import json
import pprint

# Ensure we can import the package
sys.path.append(os.getcwd())

from scriptpulse import runner

# Sample Screenplay: "The Midnight Deadline" (Dense Dialogue & Tension)
# Designed to trigger: Sustained Demand, Constructive Strain
SAMPLE_SCRIPT = """INT. NEWSROOM - NIGHT

The fluorescent lights hum. The clock on the wall ticks loudly: 11:55 PM.

JONES (40s, disheveled) types furiously at his terminal. Sweat beads on his forehead.

                                JONES
                    I can't make it. It's too much data.

EDITOR STERN (50s, stone-faced) looms over his shoulder.

                                STERN
                    You have five minutes, Jones. The presses don't wait.

INT. ARCHIVES - NIGHT

Jones SPRINTING through the rows of heavy metal shelves.

He yanks a box down. Papers fly everywhere.

                                JONES
                    Where is it? Where is it?!

He finds a red folder. Clutches it to his chest.

INT. HALLWAY - CONTINUOUS

Jones bursts out of the archives. He runs down the long corridor.

His foot slips. He scrambles back up. Breath ragged.

                                STERN (V.O.)
                    Three minutes!

INT. ELEVATOR - NIGHT

Jones jams the button repeatedly.

                                JONES
                    Come on... come on...

The doors open. He dives in.

The numbers tick down painfully slow. 4... 3... 2...

EXT. LOADING DOCK - NIGHT

The press machines are roaring. A deafening mechanical rhythm.

Jones runs toward the foreman.

                                JONES
                    Stop the presses! I have the proof!

He collapses, holding the red folder up like a shield.
"""

def main():
    print("-" * 60)
    print("🎬 ScriptPulse vNext.4 - Demonstration Run")
    print("-" * 60)
    
    print(f"\nProcessing Script ({len(SAMPLE_SCRIPT.splitlines())} lines)...")
    
    # 1. Run Pipeline
    # We pass the raw text. The system handles parsing, segmentation, encoding, temporal, patterns, immunity, and mediation.
    report = runner.run_pipeline(SAMPLE_SCRIPT)
    
    # 2. Extract Key Outputs
    # Runner returns the mediation output directly
    reflections = report.get('reflections', [])
    silence = report.get('silence_explanation')
    
    print("\n✅ Analysis Complete. Generating Writer Report...\n")
    print("=" * 60)
    print("ANTIGRAVITY REPORT")
    print("=" * 60)
    
    # 3. Display Results
    if reflections:
        for item in reflections:
            print(f"\n[SCENES {item['scene_range'][0]}-{item['scene_range'][1]}]")
            print(f"Reflection: {item['reflection']}")
            print(f"(Confidence: {item['confidence']})")
    elif silence:
        print(f"\n[NO PATTERNS DETECTED]")
        print(f"{silence}")
        
    print("\n" + "=" * 60)
    
    # Optional: Peek at internal metrics (Debug/Demo only)
    print("\n[Internal Diagnostics - For Demo Only]")
    print(f"Total Scenes: {len(report.get('scenes', []))}")
    print(f"Total Patterns Detected: {report.get('total_surfaced', 0)}")
    
if __name__ == "__main__":
    main()
