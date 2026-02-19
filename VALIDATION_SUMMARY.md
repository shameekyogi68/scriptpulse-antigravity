# ScriptPulse External Validation Report
**Date**: 2026-02-19 15:16
**Status**: PRE-REGISTRATION / MOCK DATA

## 1. Blind Ranking Experiment
> **Protocol**: Spearman Rank Correlation ($ho$) on N scripts.
> **Pre-Registered Criteria**: $ho > 0.5$ and $p < 0.05$.

*(Awaiting Real Corpus Data)*

## 2. Inter-Rater Reliability
> **Protocol**: Krippendorff's $lpha$ on Human Annotations.
> **Pre-Registered Criteria**: $lpha > 0.7$.

⚠️ Tooling: `krippendorff` library MISSING.

## 3. Error Analysis Protocol
The following failure cases will be reported for every validation run:
1.  **Top 3 Disagreements**: Scripts with highest $|Rank_{sys} - Rank_{human}|$.
2.  **Mean Absolute Rank Error (MARE)**: Global accuracy metric.
3.  **CI Reporting**: 95% Bootstrap Confidence Intervals for all metrics.
