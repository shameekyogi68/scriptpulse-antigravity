#!/usr/bin/env python3
"""
Lens Stability Test (v13.1 Block 6)

Regression test: runs viewer/reader/narrator on fixed scripts
and verifies stability properties.

Assertions:
    1. Ordering differences exist between lenses (they should diverge)
    2. Variance stays within band
    3. No lens produces flat-line pulse
    
Stores lens variance baseline for regression tracking.

Usage:
    PYTHONPATH=. python3 tests/lens_stability.py
    PYTHONPATH=. python3 tests/lens_stability.py --baseline
"""

import sys
import os
import json
import argparse
import statistics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(TESTS_DIR, 'lens_variance_baseline.json')

LENSES = ['viewer', 'reader', 'narrator']

# Fixed test scripts (deterministic input)
TEST_SCRIPTS = {
    'drama_short': """INT. OFFICE - DAY

ALEX
(firmly)
We need to talk about the merger.

MARIA
I already know. The board rejected it.

ALEX
Then we go to plan B.

EXT. PARKING LOT - NIGHT

Rain pours down. ALEX walks to their car alone.""",

    'thriller_medium': """INT. BUNKER - NIGHT

AGENT CHEN
(whispering)
They're coming. Two minutes max.

OPERATIVE
The extraction point is compromised.

AGENT CHEN
Then we fight our way out.

INT. CORRIDOR - CONTINUOUS

Gunfire echoes. CHEN moves low through smoke.

EXT. ROOFTOP - NIGHT

A helicopter descends. CHEN reaches the ladder.

AGENT CHEN
(into radio)
Package secured. Coming home.

INT. SAFE HOUSE - DAY

DIRECTOR
Debrief in twenty. Get cleaned up.""",

    'dialogue_heavy': """INT. THERAPY ROOM - DAY

PATIENT
I keep having the same dream.

THERAPIST
Tell me about it.

PATIENT
I'm standing at the edge of a cliff. Below is water. I want to jump but I can't.

THERAPIST
What stops you?

PATIENT
Fear. Always fear. It paralyzes everything.

THERAPIST
And in waking life?

PATIENT
The same. I make plans but never act.

THERAPIST
What would happen if you acted?

PATIENT
I don't know. That's what scares me.""",
}

PASS = 0
FAIL = 0


def log(check, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
        print(f"  ✅ {check}: {detail[:80]}")
    else:
        FAIL += 1
        print(f"  ❌ {check}: {detail[:80]}")


def run_all_lenses():
    """Run each lens on each test script, collect pulse traces."""
    from scriptpulse import runner
    
    results = {}
    
    for script_name, script_text in TEST_SCRIPTS.items():
        results[script_name] = {}
        for lens in LENSES:
            print(f"  Running {script_name} / {lens}...")
            r = runner.run_pipeline(script_text, lens=lens, experimental_mode=True, moonshot_mode=True)
            trace = r.get('temporal_trace', [])
            pulses = [p.get('attentional_signal', 0) for p in trace]
            results[script_name][lens] = {
                'pulses': pulses,
                'mean': round(statistics.mean(pulses), 4) if pulses else 0,
                'std': round(statistics.stdev(pulses), 4) if len(pulses) > 1 else 0,
                'total_scenes': r.get('total_scenes', 0),
            }
    
    return results


def check_stability(results):
    """Run all stability assertions."""
    
    variance_record = {}
    
    for script_name, lens_data in results.items():
        print(f"\n--- {script_name} ---")
        
        means = {lens: lens_data[lens]['mean'] for lens in LENSES}
        stds = {lens: lens_data[lens]['std'] for lens in LENSES}
        
        # 1. Ordering differences exist (lenses should diverge)
        unique_means = set(round(m, 3) for m in means.values())
        has_differences = len(unique_means) > 1
        log("Ordering differences exist", has_differences,
            f"means={means}")
        
        # 2. Variance within band (no lens should have extreme variance)
        all_within_band = all(s < 0.5 for s in stds.values())
        log("Variance within band (<0.5)", all_within_band,
            f"stds={stds}")
        
        # 3. No flat-line pulse (std > 0 for scripts with >1 scene)
        for lens in LENSES:
            n_scenes = lens_data[lens]['total_scenes']
            is_flat = stds[lens] == 0 and n_scenes > 1
            log(f"{lens}: no flat pulse", not is_flat,
                f"std={stds[lens]:.4f}, scenes={n_scenes}")
        
        variance_record[script_name] = {
            'means': means,
            'stds': stds,
        }
    
    return variance_record


def save_baseline(variance_record):
    with open(BASELINE_PATH, 'w') as f:
        json.dump(variance_record, f, indent=2)
    print(f"\nBaseline saved to {BASELINE_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true', help='Save results as baseline')
    args = parser.parse_args()
    
    print("=" * 60)
    print("LENS STABILITY TEST — v13.1 Block 6")
    print("=" * 60)
    
    results = run_all_lenses()
    variance_record = check_stability(results)
    
    if args.baseline:
        save_baseline(variance_record)
    
    print("\n" + "=" * 60)
    print(f"LENS STABILITY: {'PASS' if FAIL == 0 else 'FAIL'}")
    print(f"  ✅ {PASS}  ❌ {FAIL}")
    print("=" * 60)
    
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == '__main__':
    main()
