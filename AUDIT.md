# ScriptPulse Audit & Reproducibility Spec
**Version:** v14.0 (Consolidated Agent Architecture)
**Date:** 2026-02-21

> [!WARNING]
> This document describes the system's current validation status. All empirical claims are pending real-world validation with an annotated corpus.

---

## 1. Reproducibility Checklist
To replicate the system's analysis pipeline:

### Environment
*   **Python:** 3.9+
*   **Dependencies:** `torch`, `transformers`, `sentence-transformers`, `numpy`, `scipy`, `networkx`

### Verification
Run the included deterministic regression suite:
```bash
python3 -m pytest tests/ -v
```

### Parameters
Genre priors are configured in:
*   File: `config/genre_priors.json`
*   **Horror:** `lambda_decay = 0.915`
*   **Comedy:** `lambda_decay = 0.688`
*   These values are **hand-tuned heuristics**, not learned from data.

---

## 2. Risk Register & Mitigations

| Risk ID | Description | Mitigation Implemented | Validation Status |
| :--- | :--- | :--- | :--- |
| **R-01** | **Domain Drift** | System checks for "Standard Hollywood Format". Experimental scripts trigger warnings via `drift_monitor.py`. | ✅ Implemented |
| **R-02** | **Parser Noise** | Hybrid heuristic/ML parser with zero-shot fallback. | ⚠️ **F1 pending real benchmark** — no annotated corpus exists yet to measure parser accuracy. |
| **R-03** | **Agency Bias** | Graph-theoretic "Agency Agent" (Centrality) encourages structural analysis over normative judgment. | ✅ Implemented |
| **R-04** | **Interpretation** | Mediation layer converts scores to non-judgmental, question-first language. | ✅ Implemented |

---

## 3. Known Limitations
1.  **No Empirical Validation**: No annotated screenplay corpus exists. All metrics are theoretical until validated against human ground truth.
2.  **Keyword-Based NLP**: Emotion detection, stakes detection, and thematic resonance use lexical keyword matching, not semantic understanding.
3.  **Stub Modules**: `PolyglotValidator` and `MultimodalFusion` are placeholder stubs.
4.  **Hand-Tuned Priors**: Genre parameters (λ, β, θ) are expert-estimated, not learned from data.

---

**Status:** DRAFT — PENDING EMPIRICAL VALIDATION
