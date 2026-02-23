#!/usr/bin/env python3
"""
ScriptPulse Acceptance Test Suite (v1.0)

Validates deterministic, exact-match pipeline outputs across all genres.

Usage:
    python tests/integration/calibration/acceptance_test.py --generate   # Create golden baselines
    python tests/integration/calibration/acceptance_test.py              # Run acceptance suite

Validates:
    - Scene segmentation (exact count, heading text)
    - temporal_trace per-scene values (effort, recovery, strain, attentional_signal, confidence)
    - valence_scores (per-scene float)
    - structure_map (acts + beats)
    - semantic_beats (per-scene labels)
    - narrative_intelligence (issues + advice)
    - writer_intelligence (diagnoses, dashboard)
    - voice_fingerprints (per-character)
    - agency_analysis (per-character scores)
    - fairness_audit (bias metrics)
    - Aggregate metrics: total_scenes, run_id, version
"""

import json
import os
import sys
import argparse
import math
import time
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

BENCHMARK_DIR = os.path.join(SCRIPT_DIR, 'benchmark_scripts')
GOLDEN_PATH = os.path.join(SCRIPT_DIR, 'golden_baselines.json')

# ── Precision ──────────────────────────────────────────────────────────────────
FLOAT_TOLERANCE = 1e-4  # ±0.0001

# ── Selected benchmark scripts (2 per genre: 1 short + 1 medium) ──────────────
ACCEPTANCE_SCRIPTS = [
    # Drama
    'short_022_drama.txt',
    'medium_053_drama.txt',
    # Thriller
    'short_003_thriller.txt',
    'medium_050_thriller.txt',
    # Comedy
    'short_005_comedy.txt',
    'medium_051_comedy.txt',
    # Horror
    'short_000_horror.txt',
    'medium_057_horror.txt',
    # Romance
    'short_002_romance.txt',
    'medium_054_romance.txt',
]

# ── Top-level output keys to validate ─────────────────────────────────────────
VALIDATED_KEYS = [
    'temporal_trace',
    'valence_scores',
    'structure_map',
    'semantic_beats',
    'suggestions',
    'narrative_intelligence',
    'writer_intelligence',
    'voice_fingerprints',
    'agency_analysis',
    'fairness_audit',
    'total_scenes',
    'run_id',
    'version',
]


# =============================================================================
# HELPERS
# =============================================================================

def floats_equal(a, b, tol=FLOAT_TOLERANCE):
    """Compare two floats within tolerance, handling NaN."""
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return abs(a - b) <= tol
    return a == b


def deep_compare(expected, actual, path="root"):
    """
    Recursively compare two objects.
    Returns a list of deviation strings.
    """
    deviations = []

    if type(expected) != type(actual):
        deviations.append(
            f"  TYPE MISMATCH at {path}: expected {type(expected).__name__}, got {type(actual).__name__}"
        )
        return deviations

    if isinstance(expected, dict):
        # Key presence check
        missing = set(expected.keys()) - set(actual.keys())
        extra = set(actual.keys()) - set(expected.keys())
        if missing:
            deviations.append(f"  MISSING KEYS at {path}: {missing}")
        if extra:
            deviations.append(f"  EXTRA KEYS at {path}: {extra}")
        # Recurse into shared keys
        for key in expected:
            if key in actual:
                deviations.extend(deep_compare(expected[key], actual[key], f"{path}.{key}"))

    elif isinstance(expected, list):
        if len(expected) != len(actual):
            deviations.append(
                f"  LENGTH MISMATCH at {path}: expected {len(expected)}, got {len(actual)}"
            )
        for i in range(min(len(expected), len(actual))):
            deviations.extend(deep_compare(expected[i], actual[i], f"{path}[{i}]"))

    elif isinstance(expected, float):
        if not floats_equal(expected, actual):
            deviations.append(
                f"  NUMERIC DRIFT at {path}: expected {expected:.6f}, got {actual:.6f}, "
                f"delta={abs(expected - actual):.6f}"
            )

    elif isinstance(expected, (int, str, bool, type(None))):
        if expected != actual:
            exp_str = repr(expected)[:80]
            act_str = repr(actual)[:80]
            deviations.append(
                f"  VALUE MISMATCH at {path}: expected {exp_str}, got {act_str}"
            )

    return deviations


def extract_genre(filename):
    """Extract genre from filename like 'short_022_drama.txt'."""
    parts = filename.replace('.txt', '').split('_')
    return parts[-1] if len(parts) >= 3 else 'unknown'


def run_single_script(filepath, genre):
    """Run the pipeline on a single script and return the full output dict."""
    from scriptpulse.pipeline import runner

    with open(filepath, 'r') as f:
        content = f.read()

    result = runner.run_pipeline(
        content,
        genre=genre,
        experimental_mode=True,
        moonshot_mode=True,
        cpu_safe_mode=True,
    )
    return result


def serialize_output(result):
    """
    Extract only the validated fields from the pipeline output.
    Converts to JSON-safe types for storage and comparison.
    """
    subset = {}
    for key in VALIDATED_KEYS:
        val = result.get(key)
        if val is not None:
            subset[key] = val

    # Round-trip through JSON to normalize types (e.g., numpy → Python)
    return json.loads(json.dumps(subset, default=str))


# =============================================================================
# PHASE 1: GENERATE GOLDEN BASELINES
# =============================================================================

def generate_baselines():
    """Run all acceptance scripts and save golden baselines."""
    print("=" * 70)
    print("PHASE 1: GENERATING GOLDEN BASELINES")
    print("=" * 70)

    baselines = {}
    errors = []

    for filename in ACCEPTANCE_SCRIPTS:
        filepath = os.path.join(BENCHMARK_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP {filename} — file not found")
            continue

        genre = extract_genre(filename)
        print(f"  Running {filename} (genre={genre})...", end=" ", flush=True)

        t0 = time.time()
        try:
            result = run_single_script(filepath, genre)
            serialized = serialize_output(result)
            baselines[filename] = serialized
            elapsed = time.time() - t0
            n_scenes = serialized.get('total_scenes', '?')
            print(f"OK ({n_scenes} scenes, {elapsed:.1f}s)")
        except Exception as e:
            print(f"FAIL ({e})")
            errors.append(f"{filename}: {e}")

    with open(GOLDEN_PATH, 'w') as f:
        json.dump(baselines, f, indent=2, default=str)

    print(f"\nGolden baselines saved to {GOLDEN_PATH}")
    print(f"  Scripts processed: {len(baselines)}/{len(ACCEPTANCE_SCRIPTS)}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e}")

    return len(errors) == 0


# =============================================================================
# PHASE 2: ACCEPTANCE VALIDATION
# =============================================================================

def run_acceptance():
    """Run all scripts and compare against golden baselines."""
    if not os.path.exists(GOLDEN_PATH):
        print("ERROR: No golden baselines found. Run with --generate first.")
        sys.exit(1)

    with open(GOLDEN_PATH, 'r') as f:
        baselines = json.load(f)

    print("=" * 70)
    print("ACCEPTANCE TEST SUITE — ScriptPulse v14.0")
    print("=" * 70)
    print(f"Golden baselines: {len(baselines)} scripts")
    print(f"Float tolerance: {FLOAT_TOLERANCE}")
    print()

    results = {}
    total_deviations = 0
    pass_count = 0
    fail_count = 0

    for filename in ACCEPTANCE_SCRIPTS:
        if filename not in baselines:
            print(f"  SKIP {filename} — no golden baseline")
            continue

        filepath = os.path.join(BENCHMARK_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP {filename} — file not found")
            continue

        genre = extract_genre(filename)
        print(f"  Testing {filename} (genre={genre})...", end=" ", flush=True)

        try:
            result = run_single_script(filepath, genre)
            current = serialize_output(result)
        except Exception as e:
            print(f"PIPELINE ERROR: {e}")
            results[filename] = {'status': 'ERROR', 'error': str(e)}
            fail_count += 1
            continue

        # Deep compare against golden baseline
        golden = baselines[filename]
        deviations = deep_compare(golden, current)

        if deviations:
            print(f"FAIL ({len(deviations)} deviations)")
            results[filename] = {
                'status': 'FAIL',
                'deviations': deviations,
                'count': len(deviations),
            }
            total_deviations += len(deviations)
            fail_count += 1
        else:
            print("PASS")
            results[filename] = {'status': 'PASS'}
            pass_count += 1

    # ── Summary Report ─────────────────────────────────────────────────────
    total = pass_count + fail_count
    accuracy = round((pass_count / total) * 100) if total > 0 else 0

    print()
    print("=" * 70)
    print("ACCEPTANCE TEST RESULTS")
    print("=" * 70)

    # Per-genre breakdown
    genre_results = {}
    for filename, res in results.items():
        g = extract_genre(filename)
        genre_results.setdefault(g, []).append(res['status'])

    print("\nPer-Genre Breakdown:")
    for g in sorted(genre_results.keys()):
        statuses = genre_results[g]
        passed = statuses.count('PASS')
        total_g = len(statuses)
        icon = "PASS" if passed == total_g else "FAIL"
        print(f"  {g.title():12s}: {icon} ({passed}/{total_g})")

    # Deviation details
    if total_deviations > 0:
        print(f"\nDetailed Deviation Report ({total_deviations} total):")
        print("-" * 60)
        for filename, res in results.items():
            if res.get('deviations'):
                print(f"\n  {filename}:")
                for d in res['deviations'][:20]:  # Cap at 20 per script
                    print(f"    {d}")
                if len(res['deviations']) > 20:
                    print(f"    ... and {len(res['deviations']) - 20} more")

    print()
    print(f"  Total scripts:    {total}")
    print(f"  Passed:           {pass_count}")
    print(f"  Failed:           {fail_count}")
    print(f"  Total deviations: {total_deviations}")
    print(f"  Accuracy:         {accuracy}/100")
    print()

    if fail_count == 0:
        print("ACCEPTANCE TEST: PASS")
        print(f"All {total} scripts match golden baselines with zero deviations.")
    else:
        print("ACCEPTANCE TEST: FAIL")
        print(f"{fail_count}/{total} scripts deviated from golden baselines.")

    return fail_count == 0


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='ScriptPulse Acceptance Test Suite')
    parser.add_argument('--generate', action='store_true',
                        help='Generate golden baselines from current pipeline output')
    args = parser.parse_args()

    if args.generate:
        success = generate_baselines()
        sys.exit(0 if success else 1)
    else:
        passed = run_acceptance()
        sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
