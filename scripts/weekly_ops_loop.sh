#!/bin/bash
# v13.1 Weekly Operations Loop
# Usage: ./scripts/weekly_ops_loop.sh

set -e

DATE_STR=$(date +%F)
REPORT_DIR="reports/weekly/$DATE_STR"

echo "=================================================="
echo "  WEEKLY OPS LOOP - v13.1 ($DATE_STR)"
echo "  Reports: $REPORT_DIR"
echo "=================================================="

mkdir -p "$REPORT_DIR"

# 1. Schema Compliance
echo "[1/8] Schema Compliance..."
PYTHONPATH=. python3 tests/schema_compliance.py > "$REPORT_DIR/1_schema.log" 2>&1 || echo "❌ Schema Check Failed"

# 2. CI Audit Gate
echo "[2/8] CI Audit Gate..."
PYTHONPATH=. python3 tests/ci_audit_gate.py > "$REPORT_DIR/2_ci_gate.log" 2>&1 || echo "❌ CI Gate Failed"

# 3. Full Structured Audit
echo "[3/8] Structured Audit..."
PYTHONPATH=. python3 tests/structured_audit.py > "$REPORT_DIR/3_audit.log" 2>&1 || echo "❌ Audit Failed"
cp tests/audit_report.json "$REPORT_DIR/audit_report.json" || true

# 4. Adversarial Pack
echo "[4/8] Adversarial Stress..."
PYTHONPATH=. python3 tests/adversarial_pack.py > "$REPORT_DIR/4_adversarial.log" 2>&1 || echo "❌ Adversarial Failed"

# 5. Lens Stability
echo "[5/8] Lens Stability..."
PYTHONPATH=. python3 tests/lens_stability.py > "$REPORT_DIR/5_lens.log" 2>&1 || echo "❌ Lens Stability Failed"

# 6. Regression Check
echo "[6/8] Regression Check..."
# Assuming regression_check.py is run against the benchmark scripts
PYTHONPATH=. python3 tests/calibration/regression_check.py > "$REPORT_DIR/6_regression.log" 2>&1 || echo "❌ Regression Failed"

# 7. Drift Dashboard
echo "[7/8] Drift Dashboard..."
PYTHONPATH=. python3 scriptpulse/drift_dashboard.py > "$REPORT_DIR/7_drift.log" 2>&1 || echo "❌ Drift Check Failed"

# 8. Product Readiness
echo "[8/8] Product Readiness..."
PYTHONPATH=. python3 tests/product_readiness.py > "$REPORT_DIR/8_readiness.log" 2>&1 || echo "❌ Readiness Failed"
cp tests/readiness_report.json "$REPORT_DIR/readiness_report.json" || true

echo "=================================================="
echo "  Loop Complete. Artifacts archived in $REPORT_DIR"
echo "=================================================="


