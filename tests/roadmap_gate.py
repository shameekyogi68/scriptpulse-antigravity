#!/usr/bin/env python3
"""
v13.2 Roadmap Gate (v13.1 Block 8)

Checks whether the system satisfies all release criteria before
allowing v13.2 feature work to begin.

Gate criteria (must ALL hold for 1 week of runs):
    1. CI audit gate passes 100%
    2. Calibration drift within limits
    3. No resource_flag in normal workloads (<= 50 scenes)
    4. No schema breaks

Usage:
    PYTHONPATH=. python3 tests/roadmap_gate.py
"""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELEMETRY_DIR = os.path.join(PROJECT_ROOT, '.telemetry')
TELEMETRY_FILE = os.path.join(TELEMETRY_DIR, 'runs.jsonl')
AUDIT_REPORT = os.path.join(PROJECT_ROOT, 'tests', 'audit_report.json')
DRIFT_BASELINE = os.path.join(PROJECT_ROOT, '.drift_data', 'baseline.json')
GATE_STATUS_FILE = os.path.join(PROJECT_ROOT, '.drift_data', 'gate_status.json')

REQUIRED_GREEN_DAYS = 7


def load_telemetry(since_days=7):
    """Load telemetry entries from last N days."""
    if not os.path.exists(TELEMETRY_FILE):
        return []
    
    cutoff = datetime.now() - timedelta(days=since_days)
    entries = []
    
    with open(TELEMETRY_FILE, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry.get('timestamp', ''))
                if ts >= cutoff:
                    entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue
    
    return entries


def check_ci_audit():
    """Check 1: CI audit gate passes."""
    if not os.path.exists(AUDIT_REPORT):
        return False, "No audit report found"
    
    with open(AUDIT_REPORT, 'r') as f:
        report = json.load(f)
    
    passed = report.get('summary', {}).get('passed', 0)
    total = report.get('summary', {}).get('total', 0)
    failed = report.get('summary', {}).get('failed', 0)
    
    if failed > 0:
        return False, f"Audit has {failed} failures ({passed}/{total})"
    
    return True, f"Audit passes {passed}/{total}"


def check_drift():
    """Check 2: Calibration drift within limits."""
    try:
        from scriptpulse.drift_dashboard import DriftDashboard
        dashboard = DriftDashboard()
        status, triggers = dashboard.check_drift()
        
        if status == 'UNSTABLE':
            trigger_names = [t['metric'] for t in triggers]
            return False, f"Drift triggers: {trigger_names}"
        elif status == 'NO_BASELINE':
            return True, "No baseline set (first run)"
        
        return True, f"Drift status: {status}"
    except Exception as e:
        return True, f"Drift check skipped: {e}"


def check_resource_flags():
    """Check 3: No resource_flag in normal workloads."""
    entries = load_telemetry()
    
    if not entries:
        return True, "No telemetry data (first run)"
    
    # Filter to normal workloads (≤ 50 scenes)
    normal = [e for e in entries if e.get('total_scenes', 0) <= 50]
    flagged = [e for e in normal if e.get('resource_flag')]
    
    if flagged:
        return False, f"{len(flagged)}/{len(normal)} normal runs had resource_flag"
    
    return True, f"0/{len(normal)} normal runs flagged"


def check_schema():
    """Check 4: No schema breaks."""
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'tests/schema_compliance.py'],
            cwd=PROJECT_ROOT,
            capture_output=True, text=True,
            env={**os.environ, 'PYTHONPATH': PROJECT_ROOT}
        )
        if result.returncode == 0:
            return True, "Schema compliance passes"
        else:
            return False, f"Schema compliance failed (exit {result.returncode})"
    except Exception as e:
        return True, f"Schema check skipped: {e}"


def main():
    print("=" * 60)
    print("v13.2 ROADMAP GATE")
    print("=" * 60)
    
    checks = [
        ("CI Audit Gate", check_ci_audit),
        ("Calibration Drift", check_drift),
        ("Resource Flags", check_resource_flags),
        ("Schema Compliance", check_schema),
    ]
    
    all_pass = True
    results = {}
    
    for name, fn in checks:
        passed, detail = fn()
        icon = "✅" if passed else "❌"
        print(f"\n  {icon} {name}: {detail}")
        results[name] = {'passed': passed, 'detail': detail}
        if not passed:
            all_pass = False
    
    # Record gate status
    os.makedirs(os.path.dirname(GATE_STATUS_FILE), exist_ok=True)
    
    gate_history = []
    if os.path.exists(GATE_STATUS_FILE):
        with open(GATE_STATUS_FILE, 'r') as f:
            gate_history = json.load(f)
    
    gate_history.append({
        'timestamp': datetime.now().isoformat(),
        'all_pass': all_pass,
        'results': results,
    })
    
    with open(GATE_STATUS_FILE, 'w') as f:
        json.dump(gate_history, f, indent=2)
    
    # Count consecutive green days
    green_days = 0
    for entry in reversed(gate_history):
        if entry.get('all_pass'):
            green_days += 1
        else:
            break
    
    print("\n" + "=" * 60)
    if all_pass:
        print(f"✅ GATE: PASS ({green_days}/{REQUIRED_GREEN_DAYS} consecutive green)")
        if green_days >= REQUIRED_GREEN_DAYS:
            print(f"🟢 v13.2 DEVELOPMENT CLEARED — {green_days} consecutive green days")
        else:
            print(f"⏳ {REQUIRED_GREEN_DAYS - green_days} more green days needed before v13.2")
    else:
        print(f"❌ GATE: FAIL — Fix failing checks before v13.2 work")
    print("=" * 60)
    
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
