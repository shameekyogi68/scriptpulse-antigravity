# Methods

## 1. Computational Architecture

The ScriptPulse system utilizes a **Multi-Agent Cognitive Simulation** architecture designed to model the temporal dynamics of narrative consumption. The system is composed of six specialized agents: Structure, Perception, Dynamics, Interpretation, Experimental, and Ethics.

### 1.1 Structural Parsing & Segmentation
Raw screenplays are processed into a structured stream of *Scenes* and *Beats*. Features are extracted at the Scene level ($S_i$) using a hybrid heuristic/ML parser.
*   **Scene Segmentation**: Defined by standard sluglines (INT/EXT).
*   **Beat Segmentation**: Sub-scene units defined by narrative shifts (Transition, Angle On).

---

## 2. Mathematical Model (Dynamics Agent)

The core contribution is the **Attentional State Model**, a linear dynamical system that tracks reader engagement ($A_t$) over time $t$.

### 2.1 State Equations
The instantaneous attentional state for scene $t$ is defined as:

$$ A_t = A_{t-1} \cdot \lambda + E_t - R_t $$

Where:
*   $A_t$: Attentional Engagement (Scalar, 0-1).
*   $\lambda$: **Decay Rate** (Memory Persistence).
*   $E_t$: **Instantaneous Complexity ("Effort")**.
*   $R_t$: **Recovery Potential**.

### 2.2 Feature Definitions

**Effort ($E_t$)** is a weighted sum of cognitive and emotional load:
$$ E_t = w_1 \cdot L_{ling} + w_2 \cdot D_{vis} + w_3 \cdot C_{soc} $$
*   $L_{ling}$: Linguistic Load (Syntactic complexity, idea density).
*   $D_{vis}$: Visual Density (Action lines/page, special FX).
*   $C_{soc}$: Social Complexity (Number of active speaking characters).

**Recovery ($R_t$)** is derived from pacing and resolution:
$$ R_t = P_{still} + \Delta S_{entropy} $$
*   $P_{still}$: Stillness moments (absence of dialogue/action).
*   $\Delta S_{entropy}$: Reduction in semantic entropy (clarity/resolution).

### 2.3 Reader Profiles & Parameter Adaptation
The system adapts parameters ($\lambda, w_i$) based on a **Reader Profile** vector $P = [F, S, T]$:
*   **Familiarity ($F$)**: Domain knowledge.
*   **Speed ($S$)**: Reading speed (WPM).
*   **Tolerance ($T$)**: Tolerance for ambiguity.

**Parameter Derivation**:
*   **Decay Rate ($\lambda$)**: $\lambda = 0.80 + (0.15 \cdot T)$
*   **Recovery Base ($\beta$)**: $\beta = 0.20 + (0.30 \cdot F)$
*   **Fatigue Threshold ($\theta$)**: $\theta = 0.80 + (0.40 \cdot T)$

---

## 3. Evaluation Protocol

### 3.1 Datasets
*   **Ground Truth ($D_{GT}$)**: $N=50$ screenplays with human-annotated "Interest" and "Confusion" scores.
    *   **Selection Criteria**: Award-winning or commercially successful scripts from 2000-2023.
    *   **Annotation**: 3 raters per script.
*   **Holdout Set ($D_{Holdout}$)**: $N=10$ scripts, strictly unseen during development.
*   **Real Reader Study ($D_{Real}$)**: *[PLACEHOLDER: N participants, Age Range, Demographics]*

### 3.2 Metrics
*   **Human Alignment**: Pearson correlation ($r$) between Model $A_t$ series and Human Interest $H_t$.
*   **Inter-Rater Reliability**: Krippendorff's $\alpha$ for human raters.
    *   *Reported $\alpha$*: *[PLACEHOLDER]*
*   **Calibration Error (ECE)**: Expected Calibration Error for confidence scores.
    *   $ECE = \sum_{m=1}^M \frac{|B_m|}{n} |acc(B_m) - conf(B_m)|$

### 3.3 Significance Testing
*   **Bootstrap Resampling**: 1000 iterations to generate 95% Confidence Intervals.
*   **p-values**: Calculated against a null hypothesis of random signal correlation.

---

## 4. Reproducibility

### 4.1 Environment
*   **Python**: 3.9+
*   **Dependencies**: Locked via `config/reproducibility.lock`.
*   **Seed**: Fixed at `42` for all deterministic runs.

### 4.2 Parameter Table (Fixed)

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `lambda_base` | 0.85 | Default memory decay |
| `max_memory` | 5 | Max sliding window (scenes) |
| `w_readability` | 1.0 | Weight for Flesch-Kincaid |
| `w_density` | 1.0 | Weight for Idea Density |
| `bias_thresh_neg` | -0.3 | Ethics negative bias flag |
| `bias_thresh_pos` | 0.2 | Ethics positive bias flag |

### 4.3 Validation Thresholds
Alert thresholds are derived from the 95th percentile of the simulated reader population:
*   **Fatigue Alert**: $> 0.85$
*   **Confusion Alert**: $> 0.75$ (Sustained for 3 scenes)
