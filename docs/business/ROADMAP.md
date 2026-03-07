# ScriptPulse v2.0 Roadmap

**Current Status**: v1.2 (Research Grade)
**Focus**: Moving from "Objective Metrics" to "Nuanced Understanding"

---

## 🚧 Known Limitations (The "Cons")
*   **Surface-Level Analysis**: Model relies on text signals, missing subtext/irony.
*   **Genre Blindness**: "Slow Burn" dramas currently get penalized for low pacing relative to Action norms.
*   **Agency Proxy**: Agency is calculated via verb counts, not decision weight.
*   **Entropy Ambiguity**: High entropy can mean "Pleasant Surprise" OR "Confusing Chaos".
*   ** Rigid Decay**: Fatigue decay ($\lambda$) is fixed and doesn't adapt to "Festival" vs "Blockbuster" audiences.

---

## 🚀 Planned Features (The "Improvements")

### 1. Genre & Audience Profiling
*   [x] **Genre Profile Layer**:
    *   Define distinct pacing targets for *Thriller, Drama, Comedy, Art House*.
    *   *Implementation*: Load genre-specific $\lambda$ (decay) and $E_t$ thresholds from config.

### 2. Semantic & Agency Upgrades
*   [ ] **Intent Tagging**:
    *   Allow writers to tag scenes (e.g., `[INTENT: CALM]`) to override global pacing alerts.
*   [ ] **Agency Graph**:
    *   Transition from "Verb Counting" to "State Change Tracking".
    *   Did the character's action change the *Plot State*?
*   [x] **Entropy Split**:
    *   Differentiate **Novelty** (Good) vs. **Clarity** (Bad).
    *   Reward Novelty + Clarity -> "Twist".
    *   Penalize Novelty + Confusion -> "WTF?"

### 3. Usability & Guidance
*   [ ] **Rewrite Guidance Blocks**:
    *   Instead of just "Error", provide "Fix Patterns" (e.g., "Split this scene or cut description").
*   [ ] **Character Arc Tracker**:
    *   Measure shifts in Goal/Belief across Acts.
*   [ ] **Calibration Dashboard**:
    *   Expose constants ($\lambda, w_i$) to the user via a UI to tune sensitivity.

### 4. Comparison Tools
*   [ ] **Multi-Draft Comparison**:
    *   Calculate $\Delta$ metrics between Version A and Version B.
    *   Highlight specific edits that raised/lowered the score.

### 5. Reporting Nuance
*   [ ] **Confidence Bands**:
    *   Replace absolute "Pass/Fail" with probability distributions ($P > 80\%$).
*   [ ] **False Positive Control**:
    *   Add writer intent flags (e.g., `[INTENT: SLOW CINEMA]`) to avoid penalizing artistic choices.

### Phase 2: Scientific Validation (Immediate Next Steps)
### 2.1 Internal Validation (Completed v1.3)
- [x] Synthetic Calibration Audit (Spread 0.2-0.9)
- [x] Sensitivity Analysis (Elasticity < 1.0)
- [x] Cross-Draft Delta Verification

### 2.2 External Validation (Required for v2.0)
- [ ] **Blind Ranking Experiment**: Rank holdout scripts by Mean Attention vs Human Interest (Report Spearman $\rho$).
- [ ] **Real World Corpus Study**: Validate distribution on 50+ produced scripts.
- [ ] **Inter-Rater Agreement**: Establish $\alpha > 0.7$ for grounded truth annotations.

### Phase 3: Writer Intelligence Layer (The Interface)
Moves from "Engineer Tool" (10/10) to "Writer Collaborator" (10/10).
*   [ ] **Narrative Language Translation**:
    *   Convert "High Entropy" $\rightarrow$ "Three new plot facts introduced without reaction."
    *   Convert "Valence Oscillation" $\rightarrow$ "Emotional tone remains negative for 27 minutes."
*   [ ] **Rewrite Priority Ranking**:
    *   Rank fixes by leverage (e.g., "Priority 1: Reduce exposition in Scene 12 -> +0.2 Attention").
*   [ ] **Scene-Specific Rewrite Strategies**:
    *   Suggest pattern fixes: "Insert recovery beat," "Clarify goal," "Split confrontation."
*   [ ] **Deep Character Drive**:
    *   Track *Decisions* vs *Events*.
    *   Flag "Protagonist Inactive" sequences.
*   [ ] **Structural Health Dashboard**:
    *   Midpoint Energy Dip detection.
    *   "Thread Load" tracking per scene.

### 6. Deep Narrative Structures (New)
*   [ ] **Dialogue Function Analysis**:
    *   Classify speech intent: Conflict, Exposition, Persuasion, Bonding.
    *   Move beyond "density" to "purpose".
*   [ ] **Theme Progression**:
    *   Track recurring motifs and thematic reinforcement across acts.
    *   Measure "Thematic Resonance" (frequency consistency).
*   [ ] **Character Arc Modeling**:
    *   Beyond agency: Measure belief shifts and power dynamics over time.

### 7. Scale Validation
*   [ ] **Large Scale Benchmark**:
    *   Test across 300+ scripts to establish definitive genre norms.
    *   Publish variance tables for public reference.
