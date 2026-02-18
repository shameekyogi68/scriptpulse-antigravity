# ScriptPulse Evaluation Protocol (v1.0-Frozen)

**Date Frozen**: 2026-02-17
**Version**: 1.2.0-research-grade

## 1. Metric Definitions

### Human Alignment
*   **Pearson r**: Linear correlation between System Mean Signal and Human Mean Rating.
*   **Spearman rho**: Rank correlation.
*   **MAE**: Mean Absolute Error (`mean(|system - human|)`).
*   **Acceptance Criteria**:
    *   Pearson r > 0.6 (Strong Correlation)
    *   MAE < 0.15 (on 0-1 scale)

### Inter-Rater Reliability
*   **Krippendorff's Alpha**: Measure of agreement among human raters.
*   **Usage**: Sets theoretical ceiling for potential system performance. (System cannot exceed Human-Human agreement).

### Calibration
*   **ECE (Expected Calibration Error)**: Weighted average of absolute difference between confidence and accuracy bins.
*   **Target**: ECE < 0.1.

## 2. Validation Run Steps

1.  **Lock Configuration**: Ensure `config/reproducibility.lock` matches the version under test.
2.  **Load Ground Truth**: Use `data/ground_truth/mock_human_ratings_multi_rater.csv`.
3.  **Execute Pipeline**: Run `reproduce_results.py`.
    *   *Note*: This script enforces the random seed=42.
4.  **Verify Hash**: The output report filename includes a hash of the configuration parameters.

## 3. Failure Auditing
Any scene with **Residual > 0.3** must be logged in `tests/failure_library/` with a root cause analysis:
*   **Type A**: Missing Perception (e.g., sarcasm not detected).
*   **Type B**: Model Limitation (e.g., non-linear timeline).
*   **Type C**: Ground Truth Noise (human raters disagreed significantly).
