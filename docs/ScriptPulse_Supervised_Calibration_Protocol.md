ScriptPulse vNext.4
Supervised Learning, Calibration & ML Governance Protocol
(Authoritative · IEEE-Defensible · Non-Extensible)

1. Purpose of This Document
This document defines exactly how supervised learning and ML are allowed to exist inside ScriptPulse.
It exists to ensure that:
ML improves accuracy without increasing authority
calibration remains human-grounded
no semantic or evaluative drift occurs over time
Any ML use outside this protocol invalidates the system.

2. Core Principle (Non-Negotiable)
ML in ScriptPulse is used to calibrate perception — never to interpret meaning.
ML may decide:
when to speak
how confident to be
ML must never decide:
what matters
what is good
what should change

3. Where Supervised Learning Is Allowed
Supervised learning may be used only in the following components:
3.1 Threshold Calibration
Purpose
Align alert thresholds with real human experience
Inputs
Numeric structural signals only (Eᵢ, S(t), recovery metrics)
Outputs
Threshold adjustments
Sensitivity scaling
Explicitly Forbidden
Feature creation
Feature weighting beyond bounded adjustment
Any direct mapping to quality

3.2 Confidence & Uncertainty Estimation
Purpose
Prevent false authority
Inputs
Parsing certainty
Boundary stability
Window agreement
Draft volatility
Outputs
High / Medium / Low confidence bands
ML may downgrade certainty — never inflate it.

3.3 Draft-State Detection (Meta-Diagnostic)
Purpose
Protect writers from early-draft misuse
Inputs
Structural volatility patterns
Boundary instability
Effort variance
Outputs
Draft labels:
exploratory
structural
polish
Important
Draft state never alters analysis
Only alters framing and confidence

3.4 Parsing & Segmentation Support (Optional)
Purpose
Improve robustness to formatting noise
Inputs
Line-level text features (non-semantic)
Layout cues
Outputs
Improved structural tagging
Boundary confidence

4. Human Label Policy (Critical)
4.1 Allowed Labels (Only These)
Supervised learning may use only experiential labels, such as:
felt tiring
had to reread
lost orientation
These labels describe human processing difficulty, not value.

4.2 Forbidden Labels (Never Allowed)
The following labels must never appear in training data:
good / bad
engaging / boring
emotional / flat
effective / ineffective
clear / unclear (as judgment)
strong / weak writing
Using any of these corrupts the system.

5. Training Data Collection Rules
Labels must be collected from first-pass readers only
Readers must not discuss meaning, emotion, or quality
Labels are binary or ordinal (never scalar scores)
Reader identity is anonymized
No writer or producer labels allowed

6. Model Requirements
6.1 Model Types (Allowed)
logistic regression
shallow decision trees
calibrated linear models
6.2 Model Types (Forbidden)
deep neural networks deciding outputs
transformers inferring meaning
end-to-end black-box models
Interpretability is mandatory.

7. Feature Governance
7.1 Allowed Feature Inputs
scene effort Eᵢ
accumulated load S(t)
recovery metrics
volatility measures
boundary confidence
7.2 Forbidden Feature Inputs
absolute lexical sentiment quality
semantic embeddings (except for bounded thematic resonance mapping)
prescriptive topic vectors
character importance
narrative role indicators

8. Training & Validation Protocol
8.1 Cross-Validation
cross-script validation required
no script may appear in both train and test sets
8.2 Evaluation Criteria
Models are evaluated on:
false positive reduction
false negative reduction
confidence calibration accuracy
Never on:
agreement with taste
predictive success
alignment with coverage notes

9. Update & Drift Control
Models are version-locked
No online learning in production
Any retraining requires full regression testing
Threshold changes must be logged and reviewable

10. Explainability Requirement
For any ML-influenced decision, the system must be able to state:
“This alert was surfaced because sustained load exceeded the calibrated sensitivity range observed in human first-pass readers.”
If this cannot be explained, the model must not be used.

11. Failure & Rollback Rules
ML components must be rolled back if they:
increase alert frequency without justification
reduce silence validity
increase writer confusion
introduce evaluative language
Rollback is mandatory, not optional.

12. Ethical Guardrail
If ML makes the system sound smarter than a careful human reader, it has failed.
Accuracy without humility is corruption.

13. Final Lock Statement
Supervised learning in ScriptPulse exists to improve calibration, not authority.
Any ML use that:
infers meaning,
evaluates quality,
or pressures writers
…violates this protocol and must be removed.

