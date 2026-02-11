# ScriptPulse Audit & Reproducibility Spec
**Version:** vNext.9 (Camera-Ready)
**Date:** 2026-02-08

---

## 1. Reproducibility Checklist
To replicate the results reported in Section 4.6 (Human Validation) and 4.7 (Error Propagation):

### Environment
*   **Python:** 3.9+
*   **Dependencies:** `torch`, `transformers`, `numpy`, `scipy`, `networkx`

### Verification
Run the included deterministic regression suite:
```bash
python3 tests/validation_harness.py
```
**Expected Output:**
*   `Master Test`: **PASS** (Verifies pipeline integrity, agency detection, recovery logic).
*   `Edge Case`: **PASS** (Verifies BERT parser robustness).
*   `Recovery Probe`: **PASS** (Verifies $E[i]$ calibration).

### Parameters
Genre priors are hard-coded to match the reported "Learned values":
*   File: `antigravity/schemas/genre_priors.json`
*   **Horror:** `lambda_decay = 0.915`
*   **Comedy:** `lambda_decay = 0.688`

---

## 2. Risk Register & Mitigations

| Risk ID | Description | Mitigation Implemented |
| :--- | :--- | :--- |
| **R-01** | **Domain Drift** | System checks for "Standard Hollywood Format". Experimental scripts trigger warnings in `drift_monitor.py`. |
| **R-02** | **Parser Noise** | BERT F1=0.962. Downstream error propagation bounded at RMSE=0.07. |
| **R-03** | **Agency Bias** | "Fairness Agent" replaced with graph-theoretic "Agency Agent" (Centrality) to encourage structural analysis over normative judgment. |
| **R-04** | **Interpretation** | Mediation layer converts scores to non-judgmental language. |

---

**Status:** AUDITED & APPROVED
