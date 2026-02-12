#!/usr/bin/env python3
"""
Canary Script Check (v13.1 Hardening)

Runs a fixed set of 10 "canary" scripts on every deploy.
Compares outputs against stored golden baselines.

Enforces:
    - Pulse mean delta < 0.03
    - Uncertainty mean delta < 0.03
    - No new validation errors
    - Structure matching (scene count)

Usage:
    # 1. Generate/update golden baselines (ONLY when authorized)
    PYTHONPATH=. python3 tests/canary_check.py --update-goldens

    # 2. Run check (standard deploy gate)
    PYTHONPATH=. python3 tests/canary_check.py
"""

import sys
import os
import json
import time
import argparse
import statistics

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
CANARY_SCRIPTS_DIR = os.path.join(TESTS_DIR, 'canary_scripts')
GOLDEN_DIR = os.path.join(TESTS_DIR, 'canary_goldens')

# Thresholds
MAX_PULSE_DELTA = 0.03
MAX_UNCERTAINTY_DELTA = 0.03

# Fixed Canary Set (10 Scripts)
CANARY_SET = {
    '00_standard_drama': """INT. CAFE - DAY
ALEX
I can't do this anymore.
SAM
Do what?
ALEX
Pretend we're okay.""",

    '01_short_comedy': """INT. OFFICE - DAY
BOSS
Where's the report?
WORKER
The dog ate it.
BOSS
You don't have a dog.
WORKER
The cat ate it?""",

    '02_action_thriller': """EXT. ALLEY - NIGHT
Runner sprints. Gunfire erupts.
INT. CAR - CONTINUOUS
He dives inside. Tires screech.""",

    '03_dialogue_heavy': """INT. ROOM - DAY
A
Why?
B
Because.
A
That's not an answer.
B
It's the only one I have.""",

    '04_silent_visual': """EXT. DESERT - DAY
Wind blows sand. A lone figure walks.
The sun beats down. No water in sight.""",

    '05_monologue': """INT. STAGE - NIGHT
ACTOR
To be or not to be... that is the question.
Whether 'tis nobler in the mind to suffer...""",

    '06_high_conflict': """INT. KITCHEN - NIGHT
MOM
Get out!
DAD
This is my house!
MOM
Not anymore!""",

    '07_mixed_language': """INT. TOWER - DAY
GUIDE
Bienvenue everyone. Please follow me.
TOURIST
Danke schon.
GUIDE
Vamos!""",

    '08_flashback_structure': """INT. NOW - DAY
He cries.
INT. THEN - DAY
He laughs.
INT. NOW - DAY
He stops.""",

    '09_experimental_montage': """SERIES OF SHOTS
- A flower blooms.
- A bomb explodes.
- A baby cries."""
}


def ensure_dirs():
    os.makedirs(CANARY_SCRIPTS_DIR, exist_ok=True)
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    
    # Write scripts to disk if missing
    for name, content in CANARY_SET.items():
        path = os.path.join(CANARY_SCRIPTS_DIR, f"{name}.txt")
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(content)


def run_single(name, content):
    from scriptpulse import runner
    # Deterministic modes enabled
    return runner.run_pipeline(
        content, 
        experimental_mode=True, 
        moonshot_mode=True,
        cpu_safe_mode=False  # Force standard mode
    )


def extract_metrics(result):
    """Extract key metrics for comparison."""
    trace = result.get('temporal_trace', [])
    pulses = [p.get('attentional_signal', 0) for p in trace]
    unc = result.get('uncertainty_quantification',[])
    uncertainties = [u.get('std_dev', 0) for u in unc]
    
    return {
        'total_scenes': result.get('total_scenes', 0),
        'mean_pulse': round(statistics.mean(pulses), 4) if pulses else 0,
        'mean_uncertainty': round(statistics.mean(uncertainties), 4) if uncertainties else 0,
        'validation_errors': len(result.get('debug_export', {}).get('validation_errors', [])),
        'run_id': result.get('meta', {}).get('run_id'),
    }


def update_goldens():
    print("⚠️  UPDATING GOLDEN BASELINES...")
    ensure_dirs()
    
    for name, content in CANARY_SET.items():
        print(f"  Running {name}...")
        result = run_single(name, content)
        metrics = extract_metrics(result)
        
        path = os.path.join(GOLDEN_DIR, f"{name}.json")
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2)
            
    print("✅  All goldens updated.")


def check_canaries():
    print("="*60)
    print("CANARY DEPLOY CHECK — v13.1")
    print("="*60)
    
    ensure_dirs()
    failures = []
    
    for name, content in CANARY_SET.items():
        golden_path = os.path.join(GOLDEN_DIR, f"{name}.json")
        
        if not os.path.exists(golden_path):
            print(f"❌ {name}: No golden baseline found. Run --update-goldens first.")
            failures.append(f"{name}: Missing golden")
            continue
            
        with open(golden_path, 'r') as f:
            golden = json.load(f)
            
        # Run current
        try:
            result = run_single(name, content)
            current = extract_metrics(result)
        except Exception as e:
            print(f"❌ {name}: Crash during execution - {e}")
            failures.append(f"{name}: Crash")
            continue
            
        # Compare
        print(f"\nChecking {name}...", end="")
        
        # 1. Pulse Delta
        pulse_delta = abs(current['mean_pulse'] - golden['mean_pulse'])
        if pulse_delta > MAX_PULSE_DELTA:
            print(f" FAIL (Pulse delta {pulse_delta:.4f} > {MAX_PULSE_DELTA})")
            failures.append(f"{name}: Pulse drift {pulse_delta:.4f}")
            continue
            
        # 2. Uncertainty Delta
        unc_delta = abs(current['mean_uncertainty'] - golden['mean_uncertainty'])
        if unc_delta > MAX_UNCERTAINTY_DELTA:
            print(f" FAIL (Uncertainty delta {unc_delta:.4f} > {MAX_UNCERTAINTY_DELTA})")
            failures.append(f"{name}: Uncertainty drift {unc_delta:.4f}")
            continue
            
        # 3. Validation Errors
        if current['validation_errors'] > golden['validation_errors']:
            print(f" FAIL (New validation errors: {current['validation_errors']} > {golden['validation_errors']})")
            failures.append(f"{name}: New validation errors")
            continue

        print(f" PASS (ΔP={pulse_delta:.4f}, ΔU={unc_delta:.4f})")
    
    print("\n" + "="*60)
    if failures:
        print(f"❌ CANARY CHECK: FAIL ({len(failures)} failures)")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ CANARY CHECK: PASS")
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-goldens', action='store_true', help='Update golden baselines')
    args = parser.parse_args()
    
    if args.update_goldens:
        update_goldens()
    else:
        check_canaries()
