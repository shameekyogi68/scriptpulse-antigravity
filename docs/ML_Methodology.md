# Machine Learning Methodology

## Overview

ScriptPulse implements a supervised learning approach to predict scene-level tension scores from extracted linguistic and structural features.

## Feature Space

We define a 7-dimensional feature vector for each scene:

| Feature | Symbol | Definition | Range |
|---------|--------|------------|-------|
| Dialogue Ratio | X₁ | dialogue_lines / total_lines | [0, 1] |
| Sentiment Variance | X₂ | stddev(valence_scores) | [0, ∞) |
| Lexical Diversity | X₃ | unique_words / total_words | [0, 1] |
| Character Count | X₄ | number of speaking characters | [1, ∞) |
| Semantic Coherence | X₅ | word_overlap with previous scene | [0, 1] |
| Syntactic Complexity | X₆ | average sentence length (words) | [1, ∞) |
| Action Density | X₇ | action_lines / total_lines | [0, 1] |

## Model Architecture

We train three regression models and compare performance:

1. **Random Forest Regressor** (Primary)
   - n_estimators=100
   - max_depth=10
   - Ensemble of decision trees
   
2. **Gradient Boosting Regressor** (Comparison)
   - n_estimators=100
   - max_depth=5
   - learning_rate=0.1
   
3. **Multi-Layer Perceptron** (Deep Learning Baseline)
   - hidden_layers=[32, 16]
   - activation='relu'
   - max_iter=500

## Training Data

**Strategy:** Bootstrapped Synthetic Labels

Since human-annotated tension scores are unavailable, we use the existing heuristic-based tension scores as ground truth with added Gaussian noise (σ=0.1) to simulate annotation variance.

**Justification:** This approach tests whether ML models can learn and generalize the heuristic patterns, which is valid for a methods paper focused on the pipeline rather than absolute accuracy.

## Evaluation Protocol

### 1. Train/Test Split
- 80% training, 20% testing (random split)

### 2. Metrics
- **MAE** (Mean Absolute Error): Average prediction error
- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **R²** (Coefficient of Determination): Proportion of variance explained

### 3. Baseline Comparison
**Simple Heuristic:** tension = 1 - dialogue_ratio

We compare ML models against this baseline to demonstrate that multi-feature learning outperforms single-feature rules.

### 4. Cross-Validation
5-fold cross-validation with mean ± std reporting for robustness.

## Ablation Study

To determine feature importance, we systematically remove each feature and measure performance drop:

1. Train full model with all 7 features → R²_full
2. For each feature Xᵢ:
   - Remove Xᵢ
   - Retrain model → R²_ablated
   - Compute Δ R² = R²_full - R²_ablated
3. Rank features by Δ R² (larger = more important)

## Expected Results

**Hypothesis:** Dialogue ratio and sentiment variance will be the most important features, as they directly correlate with narrative intensity.

**Performance Target:** ML model should achieve R² > 0.65 and MAE < 0.15 on test set, outperforming the simple baseline.

## Code Implementation

```python
from research import features, ml_models, evaluation, ablation

# Extract features
X = features.extract_features(scenes, report_data)
y = tension_scores

# Train model
model = ml_models.train_model(X, y, model_type='random_forest')

# Evaluate
results = ml_models.evaluate_model(model, X_test, y_test)
print(f"MAE: {results['mae']:.4f}")
print(f"R²: {results['r2']:.4f}")

# Cross-validate
cv_results = ml_models.cross_validate(X, y, k_folds=5)

# Ablation study
ablation_data = ablation.ablation_study(X, y)
```

## References

- Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32.
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of Statistics*, 1189-1232.
