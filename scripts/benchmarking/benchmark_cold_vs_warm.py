#!/usr/bin/env python3
"""
ScriptPulse Before/After Benchmark
Measures warm-run performance improvement from agent singleton caching.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse.pipeline import runner

SCRIPT = ""
scenes = [
    ("INT. OFFICE - DAY", "SARAH\nWe need to close the deal today.\nTOM\nI know. The board won't wait.\n"),
    ("INT. BOARDROOM - NIGHT", "CEO\nNumbers are down.\nANALYST\nMarket conditions shifted.\n"),
    ("INT. CAFÉ - MORNING", "ANNA reads her phone.\nANNA\nHe's not coming back.\n"),
    ("EXT. ROOFTOP - SUNSET", "MARCUS stares at the skyline.\nMARCUS\nThis was never about the money.\n"),
    ("INT. HOSPITAL ROOM - NIGHT", "DR. CHEN checks the chart.\nDR. CHEN\nShe's stable for now.\n"),
]
for i in range(20):
    h, body = scenes[i % len(scenes)]
    SCRIPT += f"\n{h}\n\n{body}\n"

print(f"Script: {len(SCRIPT):,} chars, ~20 scenes")
print("="*50)

times = []
for run_num in range(3):
    t0 = time.perf_counter()
    runner.run_pipeline(SCRIPT, cpu_safe_mode=True, experimental_mode=False)
    elapsed = round(time.perf_counter() - t0, 2)
    times.append(elapsed)
    print(f"  Run {run_num+1}: {elapsed}s")

print("="*50)
print(f"  Run 1 (cold): {times[0]}s")
print(f"  Run 2 (warm): {times[1]}s")
print(f"  Run 3 (warm): {times[2]}s")
warm_avg = round((times[1] + times[2]) / 2, 2)
speedup = round(times[0] / warm_avg, 1) if warm_avg > 0 else 0
print(f"\n  Warm avg:     {warm_avg}s")
print(f"  Speedup:      {speedup}x (cold vs warm)")
print(f"  Time saved:   {round(times[0] - warm_avg, 2)}s per subsequent call")
