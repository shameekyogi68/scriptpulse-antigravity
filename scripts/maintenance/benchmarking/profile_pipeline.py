#!/usr/bin/env python3
"""
ScriptPulse Lightweight Performance Profiler
---------------------------------------------
Runs a SINGLE pass on a tiny 3-scene script with cpu_safe_mode=True.
Reports wall time + peak RSS memory (no tracemalloc overhead).
Designed to complete in under 60 seconds on 8GB machines.
"""
import time
import os
import sys
import signal
import resource  # macOS/Linux only — gives peak RSS without tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hard 120-second timeout — never hang the machine
def _timeout_handler(signum, frame):
    print("\n[TIMEOUT] Pipeline exceeded 120s. Aborting safely.")
    sys.exit(1)

signal.signal(signal.SIGALRM, _timeout_handler)
signal.alarm(120)

from scriptpulse.pipeline import runner

# ---- Minimal 3-scene script (keeps model load fast) ----
SCRIPT = """
INT. OFFICE - DAY

SARAH
We need to close the deal today.

TOM
I know. The board won't wait.

INT. BOARDROOM - NIGHT

CEO
Numbers are down. Someone explain.

ANALYST
Market conditions shifted.

EXT. ROOFTOP - SUNSET

MARCUS stares at the city skyline.

MARCUS
This was never about the money.
"""

print("=" * 50)
print("SCRIPTPULSE LIGHTWEIGHT PROFILER")
print("=" * 50)
print(f"Script size: {len(SCRIPT):,} chars | ~3 scenes")
print(f"Mode: cpu_safe_mode=True, experimental=False\n")

# ---- Memory before ----
mem_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # bytes on macOS

# ---- Single timed pass ----
print("[1/1] Running pipeline...")
t0 = time.time()
try:
    result = runner.run_pipeline(SCRIPT, cpu_safe_mode=True, experimental_mode=False)
    wall_time = round(time.time() - t0, 2)
    print(f"[OK] Completed in {wall_time}s")
except Exception as e:
    wall_time = round(time.time() - t0, 2)
    print(f"[ERROR] Pipeline failed after {wall_time}s: {e}")
    result = None

# ---- Memory after ----
mem_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # bytes on macOS
# macOS reports in bytes, Linux in KB
is_mac = sys.platform == 'darwin'
peak_mb = mem_after / (1024 * 1024) if is_mac else mem_after / 1024

print(f"\n--- RESULTS ---")
print(f"Wall time       : {wall_time}s")
print(f"Peak RSS        : {peak_mb:.1f} MB")
print(f"Scenes analyzed : {result.get('total_scenes', '?') if result else 'N/A'}")

if result:
    timings = result.get('meta', {}).get('agent_timings', {})
    if timings:
        print(f"\n--- AGENT TIMINGS (ms) ---")
        for agent, ms in sorted(timings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent:25s} : {ms:>6} ms")

    meta = result.get('meta', {})
    print(f"\nExecution mode  : {meta.get('execution_mode', '?')}")
    print(f"Total wall (meta): {meta.get('wall_time_s', '?')}s")

signal.alarm(0)  # cancel timeout
print("\n[DONE] Profiler finished cleanly.")
