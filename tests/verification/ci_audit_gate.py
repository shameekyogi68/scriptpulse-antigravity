#!/usr/bin/env python3
"""
CI Audit Gate — Wraps structured_audit.py for automated CI/CD.

Exit codes:
    0 = PASS (all thresholds met)
    1 = FAIL (score below minimum or critical failure)
    2 = WARN (score below warning threshold but above minimum)

Usage:
    python tests/ci_audit_gate.py
"""

import json
import os
import sys
import subprocess
import math

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
THRESHOLDS_DIR = os.path.join(TESTS_DIR, 'thresholds')
REPORT_PATH = os.path.join(TESTS_DIR, 'audit_report.json')


def load_threshold(name):
    path = os.path.join(THRESHOLDS_DIR, name)
    with open(path, 'r') as f:
        return json.load(f)


def run_audit():
    """Run the structured audit and return the report."""
    print("=" * 60)
    print("CI AUDIT GATE — Running structured_audit.py")
    print("=" * 60)

    audit_script = os.path.join(TESTS_DIR, 'structured_audit.py')
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT

    result = subprocess.run(
        [sys.executable, audit_script],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=False
    )

    if result.returncode != 0:
        print(f"\n❌ Audit script exited with code {result.returncode}")
        return None

    if not os.path.exists(REPORT_PATH):
        print(f"\n❌ Audit report not found at {REPORT_PATH}")
        return None

    with open(REPORT_PATH, 'r') as f:
        return json.load(f)


def check_thresholds(report):
    """Check the audit report against all threshold files."""
    failures = []
    warnings = []

    # --- Score Threshold ---
    score_thresholds = load_threshold('min_score.json')
    total_passed = report['summary']['passed']
    total_checks = report['summary']['total']
    min_pass = score_thresholds['min_pass']
    min_warn = score_thresholds['min_warn']

    if total_passed < min_pass:
        failures.append(f"Score {total_passed}/{total_checks} below minimum {min_pass}")
    elif total_passed < min_warn:
        warnings.append(f"Score {total_passed}/{total_checks} below warning {min_warn}")

    # --- Critical Section Failures ---
    critical_sections = score_thresholds.get('critical_sections', ['S2', 'S14'])
    for check in report.get('checks', []):
        if check['status'] == 'FAIL' and check.get('section') in critical_sections:
            failures.append(
                f"Critical section {check['section']}/{check['prompt']} FAILED: {check['check']}"
            )

    # --- Determinism Check ---
    for check in report.get('checks', []):
        if check.get('section') == 'S2' and check['status'] == 'FAIL':
            failures.append(f"Determinism failure: {check['check']} — {check['detail']}")

    # --- NaN/None Check ---
    for check in report.get('checks', []):
        detail = check.get('detail', '')
        if 'NaN' in str(detail) or 'None' in str(detail):
            if check['status'] == 'FAIL':
                failures.append(f"NaN/None detected: {check['check']} — {detail}")

    # --- Runtime Threshold ---
    runtime_thresholds = load_threshold('max_runtime_cpu.json')
    total_time = report['summary'].get('total_time_s', 0)
    if total_time > runtime_thresholds['max_total_s']:
        failures.append(
            f"Total runtime {total_time:.0f}s exceeds max {runtime_thresholds['max_total_s']}s"
        )
    elif total_time > runtime_thresholds.get('warn_total_s', 900):
        warnings.append(
            f"Total runtime {total_time:.0f}s exceeds warning threshold {runtime_thresholds['warn_total_s']}s"
        )

    return failures, warnings


def main():
    # Run the audit
    report = run_audit()
    if report is None:
        print("\n❌ CI GATE: FAIL — Could not generate audit report")
        sys.exit(1)

    # Check thresholds
    failures, warnings = check_thresholds(report)

    # Print results
    print("\n" + "=" * 60)
    print("CI GATE RESULTS")
    print("=" * 60)

    score = report['summary']['passed']
    total = report['summary']['total']
    print(f"\n  Score: {score}/{total} ({score/total*100:.1f}%)")
    print(f"  Time:  {report['summary'].get('total_time_s', 0):.1f}s")

    if warnings:
        print(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")

    if failures:
        print(f"\n  ❌ FAILURES ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
        print(f"\n❌ CI GATE: FAIL")
        sys.exit(1)
    elif warnings:
        print(f"\n⚠️  CI GATE: WARN (passing with warnings)")
        sys.exit(2)
    else:
        print(f"\n✅ CI GATE: PASS")
        sys.exit(0)


if __name__ == '__main__':
    main()
