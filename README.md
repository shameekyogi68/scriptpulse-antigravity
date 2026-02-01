# ScriptPulse v8.0 (Research Edition)

**"From Toy to Instrument"**

A deterministic, empirical, and ethical computational cinematography engine for analyzing screenplay rhythm, cognitive load, and affective dynamics.

---

## 🚀 Research Capabilities (v8.0)

ScriptPulse v8.0 integrates **11 Specialized Research Agents** to model the complete human reading experience:
1.  **Temporal Dynamics** (`temporal.py`): Models biological attention decay and recovery.
2.  **Semantic Entropy** (`semantic.py`): Measures information density (Shannon Entropy).
3.  **Syntactic Depth** (`syntax.py`): Estimates processing load via clause structure.
4.  **Explainability (XAI)** (`xai.py`): Attributes strain to specific factors (Visual vs Verbal).
5.  **Macro-Structure** (`templates.py`): Maps narrative arcs against canonical shapes (Vonnegut).
6.  **Comparative Analysis** (`comparator.py`): Longitudinal tracking and normative baselining (DTW).
7.  **Cinematic/Social** (`imagery.py`, `social.py`): Multimodal analysis of Visual Load and Social Tension.
8.  **Affective Computing** (`valence.py`): Emotion classification (Excitement vs Anxiety) via Russell's Circumplex.
9.  **Cognitive Profiling** (`profiler.py`): Simulates diverse audiences (Critic, Child, Distracted).
10. **Empirical Lab** (`beat.py`, `biometrics.py`): High-Res Micro-Pacing and Physiological Ground Truth validation.
11. **Ethical Co-Creativity** (`fairness.py`, `suggestion.py`): Audits algorithmic bias and generates structural repair tactics.
12. **Comparative Baselines** (`baselines.py`): Control group comparison against standard VADER sentiment.
13. **Hybrid NLP** (`embeddings.py`): Uses Vector Embeddings (SBERT) for semantic flux.
14. **Voice Fingerprinting** (`voice.py`): Linguistic scatter plot to detect "Same Voice" issues.
15. **Studio Reporting** (`reporters/studio_report.py`): Professional HTML/PDF coverage generation with user notes.
16. **FDX Native Support** (`importers.py`): Final Draft XML Parsing.
17. **Chemistry HeatMap** (`social.py`): Pairwise character valence interaction matrix.
18. **Exposition Alarm** (`syntax.py`): Detection of high-density info-dump monologues.
19. **Hall of Fame Benchmarks** (`research/imprints.py`): Compare your script to classic narrative structures.
20. **Visual Beat Board** (UI): Index Card visualization with color-coded tension.
21. **Genre Calibration** (`fairness.py`): Genre-aware thresholds for Horror, Comedy, Thriller.
22. **Runtime Estimator** (`utils/runtime.py`): Predict film length based on dialogue/action density.
23. **Character Arc Tracking** (UI): Visualize character growth across acts (Act 1 → 3).
24. **Simplified UI** (v13.0): Plain language, emoji labels, tooltips for non-technical users.
25. **Scene-Level Feedback** (`agents/scene_notes.py`): Actionable notes for each scene (e.g., "Add conflict").
26. **Print Summary** (`reporters/print_summary.py`): 1-page printable summary (Top 5 problems + strengths).
27. **Save/Load Analysis** (Backend): Export/import analysis as JSON to resume later.
28. **ML Feature Engineering** (`research/features.py`): 7-feature vector extraction (dialogue_ratio, sentiment_variance, etc.).
29. **ML Model Training** (`research/ml_models.py`): Random Forest/Gradient Boosting for tension prediction.
30. **Quantitative Evaluation** (`research/evaluation.py`): MAE, RMSE, R² metrics with baseline comparison.
31. **Cross-Validation** (`research/ml_models.py`): 5-fold validation with mean±std reporting.
32. **Ablation Study** (`research/ablation.py`): Feature importance analysis via systematic removal.

---

## 🚦 Usage

### 1. The Research Lab (Streamlit UI)
The primary interface for interaction and visualization.
```bash
streamlit run streamlit_app.py
```
**Features:**
*   **Pulse Line**: Real-time visualization of attentional strain.
*   **Affective Signals**: Purple (Excitement) vs Red (Anxiety) indicators.
*   **Co-Creativity Engine**: Generative strategies for repairing weak scenes.
*   **Fairness Audit**: Checks for stereotyping risks.
*   **Biometric Lab**: Import real heart-rate CSVs to validate the model.

### 2. Python API
```python
from scriptpulse import runner

report = runner.run_pipeline(
    script_text, 
    lens='viewer',
    genre='thriller',
    audience_profile='cinephile', # v6.6
    high_res_mode=True            # v7.0
)

# Access deep metrics
print(report['fairness_audit'])
print(report['suggestions'])
```

---

## ⚖️ Ethics & Limitations

### 1. Deterministic Heuristics
This system uses distinct, explainable heuristics rather than "Black Box" LLMs. This ensures **Scientific Reproducibility** but means the system calculates *Structure*, not *Subtext*. It may miss sarcasm.

### 2. Algorithmic Fairness
The `fairness_audit` module (v8.0) actively monitors for bias. However, the system relies on English-language lexicons and Western narrative templates.

### 3. Writer Authority
The system is a **Surrogate**, not a Critic. It predicts *Cost*, not *Quality*.

---

## 📂 Project Structure
*   `scriptpulse/`
    *   `agents/` - The 11 Research Agents.
    *   `rubrics/` - Interpretation logic.
    *   `runner.py` - Orchestrator.
*   `research/`
    *   `biometrics.py` - Physiological correlation.
    *   `calibrate.py` - Hill-climbing optimizer.
    *   `validate.py` - K-Fold cross-validation.

*Audit Date: 2026-02-01 (v8.0 Release)*
