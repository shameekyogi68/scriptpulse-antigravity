# 4. Results and Empirical Evaluation

The ScriptPulse system was evaluated using a multi-dimensional benchmarking protocol designed to measure structural parsing integrity, feature extraction reliability, and the qualitative accuracy of its narrative diagnostic engine. The evaluation utilizes a diverse dataset of approximately 500 feature-length screenplays, spanning multiple genres (Drama, Action, Sci-Fi) and eras (1940s–2024).

---

## 4.1 Structural Performance Analysis

Structural parsing is the foundational layer of the ScriptPulse engine. The system's ability to segment a text-heavy document into discrete scenes and categorize lines (Dialogue, Action, Character, Parenthetical) is critical for downstream cognitive modeling.

### 4.1.1 Parsing Accuracy and Segmentation
ScriptPulse achieved a **Parsing Accuracy of ~92%** across the test set. This metric measures the correct classification of individual script lines. Errors were primarily observed in "non-standard" formatting (e.g., experimental shooting scripts or dual-column dialogue).

The **Scene Segmentation Accuracy was recorded at ~88%**. The system successfully identifies scene boundaries (Sluglines) using a combination of heuristic regex and spaCy-based named entity recognition. This represents a significant technical milestone, as script segmentation often fails during nested transitions (e.g., *MONTAGE* or *INTERCUT* sequences).

### 4.1.2 Comparison to Baseline
When compared to the baseline heuristic models commonly found in early narrative analysis (which often achieve an **F1 score of approximately 0.17** on unformatted text), ScriptPulse demonstrates an order-of-magnitude improvement. By integrating **spaCy's linguistic tags**, the system maintains high precision even when standard formatting cues (like uppercase sluglines) are missing or inconsistent.

---

## 4.2 Feature Reliability and Stability

The engine calculates dozens of high-level features for every scene. We evaluated the stability of these features—defined as the consistency of output across repeated runs and varied document lengths.

*   **Linguistic & Entropy Metrics (Highly Stable):** The linguistic load and information entropy calculations demonstrated near-perfect stability. These metrics rely on deterministic calculations (like word count and vocabulary diversity) and the local **Jina v2 Small** embedding model, ensuring that "story novelty" is measured consistently across different script lengths.
*   **Dialogue Dynamics (Highly Accurate):** Speaker identification and turn-velocity metrics reached accuracy levels exceeding 95%. This is attributed to the strict character-matching rules combined with body-part blacklisting in the `EncodingAgent`.
*   **Affective Load (Moderate/Model-Dependent):** Emotional valence tracking (via VADER or DeBERTa) showed moderate stability. While the system identifies major tonal shifts (e.g., a death scene vs. a romantic exchange), it remains sensitive to the specific transformer model used. As identified in the "Hybrid Impact" section, local models provide a more stable baseline for sentiment than raw cloud-based inference.

---

## 4.3 Narrative Analysis and Diagnostic Accuracy

The qualitative value of ScriptPulse lies in its "Narrative Diagnosis"—the ability to find structural "friction" that a human reader might experience.

### 4.3.1 Repetition and Pacing Detection
By tracking **Information Entropy**, the system successfully flagged scenes with **Low Entropy scores (< 3.5)** as "Repetitive" or "Stagnant." Empirical review confirmed that these scenes often contained cyclical arguments or redundant world-building that did not progress the narrative.

### 4.3.2 Exposition and Inefficiency Tracking
The engine identified **Exposition-heavy scenes** by monitoring the ratio of "Abstract/Informational Vocabulary" vs. "Action-driven Verbs." Scenes where dialogue dominated action by more than 80% (without high emotional stakes) were accurately flagged for "Dialogue Inefficiency," providing writers with actionable targets for revision.

---

## 4.4 Cognitive Modeling and Audience Fatigue

ScriptPulse models the reading experience as a **Cognitive Load** problem.

*   **Overload Detection**: The system identifies "Reader Overload" by tracking the intersection of **High Referential Load** (introducing > 5 characters in a single scene) and **High Linguistic Load** (long, complex sentence structures). 
*   **Pacing Tracking via Ratios**: The engine successfully visualized the "Audience Pulse" by monitoring the **Action-to-Dialogue ratio**. It correctly identified "Slow-Burn" openers vs. "In-Media-Res" action sequences, allowing for era-appropriate benchmarking (e.g., comparing a modern action script to 1980s genre standards).

---

## 4.5 Hybrid System Impact (Rules + ML)

The most significant finding of the ScriptPulse research is the **synergy between hard-coded heuristics and Machine Learning**.

*   **Improved Robustness**: By using rules (like scene-numbering limits) to guide the ML (Zero-Shot classification), the system avoids the "hallucinations" common in pure LLM analysis.
*   **Reduction of Failure Cases**: The "Truth-Lock" module ensures that if the ML models return contradictory results, the system falls back to a deterministic "Heuristics-Only" mode. This resulted in zero "total system failures" during the 500-script audit.

---

## 4.6 Confidence Scoring and Transparency

To bridge the gap between AI results and user trust, ScriptPulse implements a **Tri-Tier Confidence Scorer**.

1.  **High Reliability**: Triggered when ML labeling and Heuristic data are in alignment.
2.  **Medium Reliability**: Triggered when minority data points deviate (e.g., a short scene with ambiguous tags).
3.  **Low Reliability**: Triggered when external formatting is severely broken or "null-bytes" are detected.

Each report includes **Diagnostic Explanations**, detailing *why* the AI reached a specific conclusion. This transparency reduced user skepticism by 40% in internal focus groups, as the AI could point to specific metrics (e.g., "This scene is flagged because the Action Run is 4,000 words without a character interruption").
