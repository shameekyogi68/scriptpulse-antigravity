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

$$ A_t = \min(1.0, \max(0.0, A_{t-1} \cdot \lambda + E_t - R_t)) $$

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
*   $\Delta S_{entropy}$: Reduction in lexical entropy (clarity/resolution).

### 2.3 Reader Profiles & Parameter Adaptation
The system adapts parameters ($\lambda, w_i$) based on a **Reader Profile** vector $P = [F, S, T]$:
*   **Familiarity ($F$)**: Domain knowledge.
*   **Speed ($S$)**: Reading speed (WPM).
*   **Tolerance ($T$)**: Tolerance for ambiguity.

**Parameter Derivation**:
*   **Decay Rate ($\lambda$)**: $\lambda = 0.80 + (0.15 \cdot T)$
*   **Recovery Base ($\beta$)**: $\beta = 0.20 + (0.30 \cdot F)$
*   **Fatigue Threshold ($\theta$)**: $\theta = 0.80 + (0.40 \cdot T)$

### 2.4 Genre Priors (v1.3)
To account for genre norms, base parameters are adjusted per narrative mode. **These values are hand-tuned heuristics based on domain expertise, not learned from data.**

| Genre | $\lambda$ (Decay) | $\beta$ (Recovery) | $\theta$ (Fatigue) | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Drama** | 0.90 | 0.25 | 0.90 | Slow decay, focuses on sustained emotional arcs. |
| **Thriller** | 0.75 | 0.40 | 1.20 | Fast decay, high recovery needs, higher tolerance. |
| **Action** | 0.78 | 0.50 | 1.30 | High tolerance for sustained intensity. |
| **Comedy** | 0.80 | 0.60 | 0.80 | Jokes reset tension rapidly. |
| **Horror** | 0.70 | 0.15 | 1.50 | Very fast decay (jump scares), very slow recovery. |

---

## 2.5 Pre-Registered Validation Criteria (v2.0)

> [!IMPORTANT]
> The following are **pre-registered targets** for future validation. They have NOT yet been achieved. No annotated corpus currently exists.

| Metric | Target Threshold | Statistical Significance | Definition |
| :--- | :--- | :--- | :--- |
| **Spearman $\rho$** | $> 0.5$ | $p < 0.05$ | Correlation between Mean Attention and Human Rank. |
| **Inter-Rater $\alpha$** | $> 0.7$ | 95% CI > 0.6 | Agreement level of ground truth annotators. |
| **Rank Error (MARE)** | $< 2.0$ | N/A | Mean Absolute Rank Error per script (N=10). |

**Error Analysis Requirement**:
All validation reports must include:
1.  **Top 3 Disagreement Cases** (Outliers).
2.  **95% Bootstrap Confidence Intervals** for $\rho$ and $\alpha$.
3.  **Effect Size Interpretation** (Weak < 0.4, Moderate < 0.7, Strong > 0.7).

## 3. Evaluation Protocol

### 3.1 Datasets

> [!WARNING]
> All datasets below are **planned but not yet collected**. Current data files in `data/ground_truth/` are mock templates for development only.

*   **Ground Truth ($D_{GT}$)**: *[PLANNED]* $N=50$ screenplays with human-annotated "Interest" and "Confusion" scores.
    *   **Selection Criteria**: Award-winning or commercially successful scripts from 2000-2023.
    *   **Annotation**: 3 raters per script.
*   **Holdout Set ($D_{Holdout}$)**: *[PLANNED]* $N=10$ scripts, strictly unseen during development.
*   **Real Reader Study ($D_{Real}$)**: *[PLANNED: N participants, Age Range, Demographics]*

### 3.2 Power Analysis (Sample Size Estimation)
To detect a moderate correlation ($\rho=0.5$) with $\alpha=0.05$ and Power ($1-\beta$) $= 0.80$, the minimum required sample size is **N=29**.
*   **Study Target**: $N=50$ scripts (Ground Truth).
*   **Holdout Target**: $N=10$ scripts (Pilot).

### 3.3 Data Leakage Safeguards
To ensure epistemic integrity:
1.  **No Training**: The engine uses fixed priors derived from domain expertise, not optimization on any test set.
2.  **Parameter Freeze**: Constants ($\lambda, \beta, \theta$) are locked (MD5 Hash) prior to ingesting validation data.
3.  **Physical Separation**: The "Holdout Set" is stored in a separate directory from the "Dev Set".

### 3.4 Metrics
*   **Human Alignment**: Spearman rank correlation ($\rho$) between Model $A_t$ series and Human Interest $H_t$.
*   **Inter-Rater Reliability**: Krippendorff's $\alpha$ for human raters.
*   **Mean Absolute Rank Error (MARE)**: $|Rank_{sys} - Rank_{human}|$.

### 3.5 Significance Testing
*   **Bootstrap Resampling**: 1000 iterations to generate 95% Confidence Intervals.
*   **p-values**: Calculated via `scipy.stats.t.sf()` against a null hypothesis of zero correlation.

---

## 4. Reproducibility

### 4.1 Environment
*   **Python**: 3.9+
*   **Dependencies**: Locked via `requirements.txt` with pinned versions.
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
Alert thresholds are derived from the 95th percentile of a simulated reader population:
*   **Fatigue Alert**: $> 0.85$
*   **Confusion Alert**: $> 0.75$ (Sustained for 3 scenes)

---

## 5. Limitations

1.  **No Empirical Validation**: All metrics (correlation, F1, R²) are pre-registered targets, not achieved results. No annotated corpus exists.
2.  **Lexical NLP**: Feature extraction relies on word-frequency counting and keyword matching, not semantic embeddings or contextual language models.
3.  **Hand-Tuned Priors**: All genre parameters (λ, β, θ) are set by domain expertise. They have not been learned or validated against human data.
4.  **Stub Modules**: `PolyglotValidator` and `MultimodalFusion` are development placeholders with no real functionality.
5.  **Effort Model**: The cognitive effort function is a linear weighted sum of heuristic features, not based on information-theoretic Surprisal or psycholinguistic grounding.
