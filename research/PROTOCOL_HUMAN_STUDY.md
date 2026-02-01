# ScriptPulse Experimental Protocol: Human Ground Truth Validation
**Target Venue:** IEEE Transactions on Affective Computing / ACM CHI

To validate the ScriptPulse measurements of "Attentional Strain" and "Drift," we must correlate system outputs with empirically observed human reading behavior.

## 1. Study Design

**Objective:** Determine the correlation coefficient ($r$) between ScriptPulse `strain` predictions and human-reported cognitive load.

**Subjects:** 
- **N=50** participants.
- **Criteria:** Script-literate (must pass a basic formatting quiz). Mixed experience levels (Novice to Pro).

**Stimuli:**
- **10 Short Scripts** (5-10 pages each).
- **Selection:** Scripts must vary in density (some action-heavy, some dialogue-heavy, some experimental).

## 2. Methodology options

### Option A: The "Click-Through" Method (Low Cost)
*   **Setup:** Subjects read the script on a digital reader.
*   **Task:** They interpret the script as if they were a producer.
*   **Response:** They must click a "Flag" button whenever they feel:
    1.  **Confused** (Drift)
    2.  **Bored** (Recovery/Low Engagement)
    3.  **Overwhelmed** (High Strain)
*   **Data:** Timestamps of clicks mapped to Scene Numbers.

### Option B: Eye-Tracking (High Rigor - IEEE Gold Standard)
*   **Setup:** Use a Tobii Eye Tracker (or webcam-based AI tracker).
*   **Metric 1:** **Fixation Duration** (Longer fixation = High Processing Load).
    *   *Hypothesis:* Fixation Duration should correlate positively with ScriptPulse `Effort`.
*   **Metric 2:** **Regression Rate** (Eyes jumping back to re-read).
    *   *Hypothesis:* High Regression Rate should correlate with ScriptPulse `Drift` or `Complexity`.

## 3. Data Processing

1.  **Running the System:**
    Run ScriptPulse on all 10 scripts. Export the `temporal_trace` for each.
    
2.  **Aligning Data:**
    Bin human data into Scene Buckets (e.g., "Avg Fixation Time for Scene 1").
    
3.  **Correlation Analysis:**
    Calculate Pearson correlation ($r$) and Spearman rank correlation ($\rho$) between:
    - Independent Variable: `ScriptPulse_Effort` (System)
    - Dependent Variable: `Human_Fixation_Time` (Human)

## 4. Success Criteria

*   **$r > 0.4$**: **Valid Structural Proxy.** (Publishable). Shows the system captures a meaningful part of the signal.
*   **$r > 0.7$**: **High Fidelity Model.** (Breakthrough). The system effectively mimics human processing.

## 5. Ethical Considerations
*   **Non-Evaluative:** Ensure subjects are told they are testing the *software*, not grading the *writer*.
*   **Privacy:** Anonymize all human subject data.

---

### Ready-to-use Data Format (`human_data.csv`)

If you perform this study, format your data as follows for the `research/correlation.py` script:

```csv
script_id, scene_index, human_avg_fixation_ms, human_reported_confusion_flag
001, 1, 450, 0
001, 2, 800, 1
...
```
