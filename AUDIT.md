# ScriptPulse Audit & Reproducibility Spec
**Version:** v15.0 Gold (Transformer-Enhanced Architecture)
**Date:** 2026-03-07

> [!IMPORTANT]
> This document describes the system's current validation status. The system has been upgraded from Heuristic-Lexical analysis to **Transformer-Augmented Behavioral Simulation** using Jina-v2 and DeBERTa-v3.

---

## 1. Reproducibility Checklist
To replicate the system's analysis pipeline and ensure research parity:

### Environment & Dependencies
*   **Python:** 3.9+ (Tested on 3.12)
*   **Core Logic:** `numpy`, `scipy`, `networkx`, `pandas`
*   **Transformer Stack:** `torch`, `transformers`, `sentence-transformers`
*   **Models:**
    *   `Jina-v2-small-en`: Sentence Embeddings (8k context window).
    *   `DeBERTa-v3-xsmall-mnli-alnli`: Zero-Shot Classification.
    *   `en_core_web_sm`: spaCy syntactic parsing.

### Verification Suite
Run the full stress-test and logic-verification script:
```bash
python3 final_validation.py
```
*Expected: "OK". Verifies genre sensitivity and pipeline end-to-end flow.*

### Parameters (Frozen for Research)
Genre priors are hardcoded in `DynamicsAgent` to ensure audit integrity:
*   **Drama:** `lambda=0.90, beta=0.25`
*   **Horror:** `lambda=0.70, beta=0.15`
*   **Action:** `lambda=0.78, beta=0.50`
*   These values follow the **v1.3 Genre Prior Specification** in `PAPER_METHODS.md`.

---

## 2. Risk Register & Mitigations

| Risk ID | Description | Mitigation Implemented | Status |
| :--- | :--- | :--- | :--- |
| **R-01** | **Domain Drift** | Slugline-based parsing guards against non-screenplay text. | ✅ Active |
| **R-02** | **Memory OOM** | Diagnostics toggle for "Memory Safe Mode" (disables Transformer stack). | ✅ Active |
| **R-03** | **Context Truncation** | Transitioned to Jina-v2 with **8,192-token horizon** to capture full scenes. | ✅ Upgraded |
| **R-04** | **Evaluative Bias** | System output suppresses "Good/Bad" judgment, focusing on "Attentional Signal." | ✅ Active |

---

## 3. System Capabilities (v15.0 Gold)
1.  **High-Fidelity Sentiment**: Emotional valence is now mapped via zero-shot classification (DeBERTa) rather than keyword counting.
2.  **Long-Range Dependency**: The 8k context window allows the system to perceive narrative connections across entire scenes.
3.  **Genre Calibration**: Pacing alerts (Structural Sag) now adjust dynamically based on the selected genre.

---

**Status:** PRODUCTION READY — RESEARCH SPEC ALIGNED
