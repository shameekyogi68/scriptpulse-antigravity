#!/usr/bin/env python3
"""
ScriptPulse Performance Profiler
Runs cProfile + tracemalloc on a 20-scene synthetic script.
Output: timing per function + peak memory.
"""
import cProfile
import pstats
import tracemalloc
import io
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse.pipeline import runner

# ---- Synthetic 20-scene script (moderate complexity) ----
SCRIPT = ""
scenes = [
    ("INT. OFFICE - DAY", "SARAH\nWe need to close the deal today.\nTOM\nI know. The board won't wait.\n"),
    ("INT. BOARDROOM - NIGHT", "CEO\nNumbers are down. Someone explain.\nANALYST\nMarket conditions shifted.\n"),
    ("INT. CAFÉ - MORNING", "ANNA reads her phone. She looks pale.\nANNA\nHe's not coming back.\n"),
    ("EXT. ROOFTOP - SUNSET", "MARCUS stares at the city skyline.\nMARCUS\nThis was never about the money.\n"),
    ("INT. HOSPITAL ROOM - NIGHT", "The machines beep. DR. CHEN checks the chart.\nDR. CHEN\nShe's stable for now.\n"),
]
for i in range(20):
    h, body = scenes[i % len(scenes)]
    SCRIPT += f"\n{h}\n\n{body}\n"

print("=" * 60)
print("SCRIPTPULSE PERFORMANCE PROFILER")
print("=" * 60)
print(f"Script size: {len(SCRIPT):,} chars | ~{SCRIPT.count('INT.') + SCRIPT.count('EXT.')} scenes\n")

# ---- PASS 1: Wall time baseline ----
t0 = time.time()
runner.run_pipeline(SCRIPT, cpu_safe_mode=True, experimental_mode=False)
wall_time_baseline = round(time.time() - t0, 2)
print(f"[Baseline] Wall time (cpu_safe=True): {wall_time_baseline}s")

# ---- PASS 2: cProfile ----
pr = cProfile.Profile()
tracemalloc.start()

pr.enable()
runner.run_pipeline(SCRIPT, cpu_safe_mode=True, experimental_mode=False)
pr.disable()

mem_snapshot = tracemalloc.take_snapshot()
tracemalloc.stop()

# Top 10 memory consumers
top_stats = mem_snapshot.statistics('lineno')
print("\n--- TOP 10 MEMORY CONSUMERS ---")
for stat in top_stats[:10]:
    print(stat)

# Top 20 CPU hogs by cumulative time
print("\n--- TOP 20 CPU HOTSPOTS (cumtime) ---")
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)
print(s.getvalue())
