# IEEE Experimental Validation & Ablation Protocol
## ScriptPulse vNext.5 (Advanced Temporal Realism)

This document defines the formal protocol for validating ScriptPulse's internal modeling layers against reader-experienced cognitive phenomena. It ensures publication readiness, system rigor, and ethical alignment.

---

### 1. Validation Philosophy

**ScriptPulse is NOT validated against:**
* "Good" or "Bad" writing
* Box office success or critical reception
* Screenplay "rules" or structural dogma

**ScriptPulse IS validated against:**
* **First-Pass Cognitive Experience:** Does the model identify strain where readers report strain?
* **Silence Validity:** Does the model remain silent where readers report stability?
* **Temporal Alignment:** Do the modeled fatigue curves match the timing of reader fatigue?

---

### 2. Ablation Methodology (Failure Mode Analysis)

To prove the necessity of each v5.0 internal layer, we conduct **Ablation Studies**. We remove one layer at a time and measure the resurgence of specific failure modes.

#### Layer 1: TAM (Temporal Attentional Microdynamics)
*   **Ablation:** Disable `tam.py` and `micro_structure` encoding.
*   **Hypothesis:** Without TAM, recovery timing will be inaccurate (`recovery_timing_error` increases). Short, dense scenes will be under-weighted.
*   **Target Metric:** Recovery Lag (ms/lines).

#### Layer 2: ACD (Attention Collapse vs Drift)
*   **Ablation:** Disable `acd.py` logic.
*   **Hypothesis:** High-strain signals will trigger generic alerts instead of nuanced "drift" warnings. "Boring" sections will trigger "Exhaustion" false positives.
*   **Target Metric:** False Positive Alert Rate on "Boring" Control Scripts.

#### Layer 3: SSF (Silence-as-Signal Formalization)
*   **Ablation:** Disable `ssf.py` confidence bands.
*   **Hypothesis:** The system will fail to distinguish "Lack of Data" from "Earned Stability", reducing writer trust.
*   **Target Metric:** Silence Confidence Precision.

#### Layer 4: LRF (Long-Range Fatigue)
*   **Ablation:** Disable `lrf.py` reserve tracking.
*   **Hypothesis:** Late-script strain will be invisible or attributed to the wrong specific scene.
*   **Target Metric:** Late-Act Strain Correlation.

---

### 3. Quantitative Metrics

#### 3.1 Temporal Alignment Score (TAS)
Overlap between modeled strain ($S(t) > 0.6$) and reader-reported difficulty windows ($W_{reader}$).

$$ TAS = \frac{|S_{high} \cap W_{reader}|}{|S_{high} \cup W_{reader}|} $$

*   **Goal:** $> 0.75$ (High alignment, but not perfect, allowing for subjective variance).

#### 3.2 False Positive Silence Rate (FPSR)
Frequency of alerts surfaced in windows where readers reported **zero difficulty**.

*   **Goal:** $< 0.10$ (Restraint is prioritized over sensitivity).

#### 3.3 Determinism Index
Percent of identical outputs across 100 runs on the same input.

*   **Requirement:** $1.0$ (100%). ScriptPulse must be strictly deterministic.

---

### 4. Control Experiments

#### 4.1 The "Entropy" Control (Random Structure)
*   **Input:** Randomly shuffled lines from a valid script.
*   **Expected Result:** High, chaotic $S(t)$, massive fatigue, immediate collapse. Use to verify system responsiveness to incoherence.

#### 4.2 The "Flat" Control (Repetitive Monotony)
*   **Input:** 50 identical scenes of "He sits. He waits."
*   **Expected Result:** 
    *   $E[i]$ remains low.
    *   **Drift (ACD)** spikes to 1.0.
    *   **Silence (SSF)** reports "Stable but Drifting".
    *   **Alerts** should be "Wandering", not "Tiring".

---

### 5. Ethical Guidelines for Validators

1.  **NO EVALUATION:** Validators must never judge the quality of the script ("good scene", "bad dialogue"). Only report experience ("felt long", "confusing").
2.  **SINGLE PASS:** Validation data must come from a single, uninterrupted read-through to simulate the audience.
3.  **NO AUTHORSHIP:** Validators cannot be the author of the work being tested.

---

### 6. Execution Instructions

1.  Run `tests/ablation_study.py` to generate signals for Full Stack vs Ablated versions.
2.  Compare output metrics against Ground Truth (if available) or Theoretical Bounds.
3.  Report results in standard IEEE ablation table format.
