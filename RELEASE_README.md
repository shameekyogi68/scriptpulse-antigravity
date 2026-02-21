# ScriptPulse Research Artifact

This repository contains the official implementation, dataset (mock), and reproduction scripts for the paper:  
**"ScriptPulse: Computational Narrative Analysis via Multi-Agent Temporal Dynamics"**

## 📂 Contents
*   `scriptpulse/`: Core multi-agent system source code.
    *   `agents/`: The 6 Core Cognitive Agents.
    *   `validation/`: Validation logic (Temporal, Calibration, etc.).
    *   `utils/`: Shared utilities (Normalization, Runtime).
    *   `runner.py`: Unified execution pipeline.
*   `data/`:
    *   `ground_truth/`: Human-annotated scripts (N=50) for validation.
    *   `holdout/`: Unseen scripts (N=10) for blind evaluation.
    *   `real_study/`: Schema for participant data.
*   `config/`: Configuration files and `reproducibility.lock`.
*   `reproduce_results.py`: **Main entry point** to generate the full research report.
*   `PAPER_METHODS.md`: Detailed mathematical definitions and parameter tables.

## 🚀 Quick Start (Reproduction)

1.  **Install Dependencies** (Python 3.9+ required):
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Full Reproduction**:
    This command trains no models (inference only) but runs the full validation harness:
    *   Human Agreement (Krippendorff's Alpha)
    *   Baseline Comparisons vs. Readability
    *   Ablation Studies
    *   Significance Testing (Bootstrap CIs)
    ```bash
    python3 reproduce_results.py
    ```

3.  **Output**:
    A timestamped Markdown report will be generated in `output/research_run/`.

## 📊 Methods & Parameters
See `PAPER_METHODS.md` for exact formulas, constant values, and evaluation protocols used in this study.

### v1.3 Validation Audit (Phase 18)
*   **Sensitivity**: Stable elasticity (< 1.0) under $\lambda$ perturbation.
*   **Calibration**: Demonstrated signal separation (0.2-0.9) on synthetic corpus.
*   **Confidence**: Metrics penalized for low data density or variance.

### v2.0 Writer Intelligence Layer (Phase 19)
*   **Narrative Translation**: Converts math signals (Entropy, Strain) into story diagnosis ("Clarity Gap", "Plot Density Spike").
*   **Rewrite Prioritization**: Ranks structural edits by estimated leverage (High/Medium/Low).
*   **Executive Summary**: Clean, one-page report format for rapid writer assessment.

### Reproducibility Protocols
*   **Version Lock**: MD5 Hash of constants embedded in all reports.
*   **Deterministic Core**: Random seed fixed to `42` in `config.py`.
*   **Hard Bounds**: All outputs clamped to $[0,1]$ for numerical stability.

# ScriptPulse v1.3 + Writer Layer (Gold Master)

**Status**: Development Complete. Ready for Writer Stress Testing (Product Validation).
**Version**: 1.3.1 (Writer Interface Verified)
**Date**: 2026-02-20
*   **Validation Status**:
    *   Engineering: ✅ Complete (Deterministic)
    *   Science: ✅ Complete (Pre-registered, Power-analyzed)
    *   Product: 🟡 In Progress (Writer Stress Test)

## 📘 Writer's Guide
See `WRITER_GUIDE.md` for a comprehensive, non-technical explanation of the system's capabilities, architecture, and how to interpret the reports.

## 🔮 Future Work & Limitations
See `ROADMAP.md` for a detailed list of known limitations (e.g., genre blindness) and the v2.0 feature plan.

## ⚖️ License
MIT License.
