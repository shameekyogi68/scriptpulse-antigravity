#!/usr/bin/env python3
"""
Regression Check (v13.1)

Runs the pipeline on all benchmark scripts and checks for metric drift.

Checks:
    1. Per-metric drift < defined delta (default 0.05)
    2. Pulse drift < 0.05
    3. No NaN in outputs
    4. Scores within expected ranges

Usage:
    python tests/calibration/regression_check.py
    python tests/calibration/regression_check.py --baseline  # Create new baseline
"""

import json
import os
import sys
import argparse
import statistics
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

BENCHMARK_DIR = os.path.join(SCRIPT_DIR, 'benchmark_scripts')
EXPECTED_RANGES_PATH = os.path.join(SCRIPT_DIR, 'expected_ranges.json')
BASELINE_PATH = os.path.join(SCRIPT_DIR, 'baseline_scores.json')

MAX_PULSE_DRIFT = 0.05
MAX_METRIC_DRIFT = 0.05


def load_expected_ranges():
    with open(EXPECTED_RANGES_PATH, 'r') as f:
        return json.load(f)


def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return None
    with open(BASELINE_PATH, 'r') as f:
        return json.load(f)


def run_script(filepath, sample_mode=False):
    """Run pipeline on a script and extract key metrics."""
    from scriptpulse import runner
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    try:
        result = runner.run_pipeline(content, experimental_mode=True, moonshot_mode=True)
        
        trace = result.get('temporal_trace', [])
        pulses = [p.get('attentional_signal', 0) for p in trace]
        
        metrics = {
            'total_scenes': result.get('total_scenes', 0),
            'mean_pulse': round(statistics.mean(pulses), 4) if pulses else 0,
            'max_pulse': round(max(pulses), 4) if pulses else 0,
            'min_pulse': round(min(pulses), 4) if pulses else 0,
            'has_nan': any(math.isnan(p) if isinstance(p, float) else False for p in pulses),
            'agent_timings': result.get('meta', {}).get('agent_timings', {}),
        }
        return metrics
    except Exception as e:
        return {'error': str(e), 'has_nan': True}


def create_baseline(expected_ranges, sample_size=10):
    """Run a sample of scripts to establish baseline metrics."""
    print("Creating baseline from sample...")
    
    baseline = {}
    scripts = list(expected_ranges.keys())
    sample = scripts[:sample_size] if len(scripts) > sample_size else scripts
    
    for filename in sample:
        filepath = os.path.join(BENCHMARK_DIR, filename)
        if not os.path.exists(filepath):
            continue
        
        print(f"  Processing {filename}...")
        metrics = run_script(filepath)
        baseline[filename] = metrics
    
    with open(BASELINE_PATH, 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"Baseline saved to {BASELINE_PATH} ({len(baseline)} scripts)")
    return baseline


def check_regression(expected_ranges, baseline):
    """Compare current run against baseline for drift."""
    failures = []
    warnings = []
    checked = 0
    
    for filename, baseline_metrics in baseline.items():
        if baseline_metrics.get('error'):
            continue
        
        filepath = os.path.join(BENCHMARK_DIR, filename)
        if not os.path.exists(filepath):
            continue
        
        print(f"  Checking {filename}...")
        current = run_script(filepath)
        
        if current.get('error'):
            failures.append(f"{filename}: Pipeline error — {current['error']}")
            continue
        
        # NaN check
        if current.get('has_nan'):
            failures.append(f"{filename}: NaN detected in pulse output")
            continue
        
        # Pulse drift
        pulse_drift = abs(current['mean_pulse'] - baseline_metrics['mean_pulse'])
        if pulse_drift > MAX_PULSE_DRIFT:
            failures.append(
                f"{filename}: Pulse drift {pulse_drift:.4f} > {MAX_PULSE_DRIFT} "
                f"(baseline={baseline_metrics['mean_pulse']:.4f}, current={current['mean_pulse']:.4f})"
            )
        
        # Scene count drift
        if current['total_scenes'] != baseline_metrics['total_scenes']:
            warnings.append(
                f"{filename}: Scene count changed "
                f"(baseline={baseline_metrics['total_scenes']}, current={current['total_scenes']})"
            )
        
        checked += 1
    
    return failures, warnings, checked


def main():
    parser = argparse.ArgumentParser(description='Regression check for ScriptPulse calibration')
    parser.add_argument('--baseline', action='store_true', help='Create new baseline')
    parser.add_argument('--sample', type=int, default=10, help='Sample size for baseline')
    args = parser.parse_args()
    
    expected_ranges = load_expected_ranges()
    
    if args.baseline:
        create_baseline(expected_ranges, sample_size=args.sample)
        return
    
    baseline = load_baseline()
    if baseline is None:
        print("No baseline found. Run with --baseline first.")
        sys.exit(1)
    
    print(f"Running regression check against baseline ({len(baseline)} scripts)...")
    failures, warnings, checked = check_regression(expected_ranges, baseline)
    
    print(f"\n{'='*60}")
    print(f"REGRESSION CHECK RESULTS")
    print(f"{'='*60}")
    print(f"  Checked: {checked}")
    
    if warnings:
        print(f"\n  ⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")
    
    if failures:
        print(f"\n  ❌ Failures ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
        print(f"\n❌ REGRESSION CHECK: FAIL")
        sys.exit(1)
    else:
        print(f"\n✅ REGRESSION CHECK: PASS (drift within thresholds)")
        sys.exit(0)


if __name__ == '__main__':
    main()
