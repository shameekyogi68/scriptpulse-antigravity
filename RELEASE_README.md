# ScriptPulse Research Artifact

This repository contains the official implementation, dataset (mock), and reproduction scripts for the paper:  
**"ScriptPulse: Computational Narrative Analysis via Multi-Agent Temporal Dynamics"**

## 📂 Contents
*   `scriptpulse/`: Core multi-agent system source code.
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

## ⚖️ License
MIT License.
