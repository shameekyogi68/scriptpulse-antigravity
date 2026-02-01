"""
ScriptPulse Advanced Analysis Module
Error analysis, learning curves, and statistical tests.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import learning_curve

def analyze_errors(y_true, y_pred, X, feature_names, threshold=0.2):
    """
    Analyze prediction errors to identify patterns.
    
    Args:
        y_true: ground truth
        y_pred: predictions
        X: feature matrix
        feature_names: list of feature names
        threshold: error threshold for "large error"
        
    Returns:
        dict with error analysis results
    """
    errors = np.abs(y_true - y_pred)
    
    # Identify large errors
    large_error_indices = np.where(errors > threshold)[0]
    small_error_indices = np.where(errors <= threshold)[0]
    
    # Analyze feature distributions for large vs small errors
    feature_analysis = {}
    for i, feat_name in enumerate(feature_names):
        large_error_vals = X[large_error_indices, i] if len(large_error_indices) > 0 else []
        small_error_vals = X[small_error_indices, i] if len(small_error_indices) > 0 else []
        
        feature_analysis[feat_name] = {
            'large_error_mean': np.mean(large_error_vals) if len(large_error_vals) > 0 else 0,
            'small_error_mean': np.mean(small_error_vals) if len(small_error_vals) > 0 else 0,
            'difference': np.mean(large_error_vals) - np.mean(small_error_vals) if len(large_error_vals) > 0 and len(small_error_vals) > 0 else 0
        }
    
    return {
        'mean_error': np.mean(errors),
        'std_error': np.std(errors),
        'large_error_count': len(large_error_indices),
        'large_error_percentage': len(large_error_indices) / len(errors) * 100,
        'feature_analysis': feature_analysis,
        'worst_predictions': {
            'indices': np.argsort(errors)[-5:],  # Top 5 worst
            'errors': errors[np.argsort(errors)[-5:]]
        }
    }


def plot_learning_curve(model, X, y, cv=5, scoring='r2'):
    """
    Generate learning curve to show model performance vs training size.
    
    Args:
        model: sklearn model
        X: features
        y: labels
        cv: cross-validation folds
        scoring: metric to plot
        
    Returns:
        matplotlib figure
    """
    train_sizes = np.linspace(0.1, 1.0, 10)
    
    train_sizes_abs, train_scores, val_scores = learning_curve(
        model, X, y,
        cv=cv,
        train_sizes=train_sizes,
        scoring=scoring,
        n_jobs=-1
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(train_sizes_abs, train_mean, 'o-', color='r', label='Training score')
    ax.fill_between(train_sizes_abs, train_mean - train_std, train_mean + train_std, alpha=0.1, color='r')
    
    ax.plot(train_sizes_abs, val_mean, 'o-', color='g', label='Validation score')
    ax.fill_between(train_sizes_abs, val_mean - val_std, val_mean + val_std, alpha=0.1, color='g')
    
    ax.set_xlabel('Training Set Size')
    ax.set_ylabel(f'{scoring.upper()} Score')
    ax.set_title('Learning Curve')
    ax.legend(loc='best')
    ax.grid(True)
    
    return fig


def plot_predictions(y_true, y_pred, title="Predicted vs Actual"):
    """
    Scatter plot of predictions vs ground truth.
    
    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.scatter(y_true, y_pred, alpha=0.5)
    
    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
    
    ax.set_xlabel('Actual Tension Score')
    ax.set_ylabel('Predicted Tension Score')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    
    return fig


def plot_feature_correlation(X, feature_names):
    """
    Heatmap of feature correlations.
    
    Returns:
        matplotlib figure
    """
    corr_matrix = np.corrcoef(X.T)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    
    ax.set_xticks(np.arange(len(feature_names)))
    ax.set_yticks(np.arange(len(feature_names)))
    ax.set_xticklabels(feature_names, rotation=45, ha='right')
    ax.set_yticklabels(feature_names)
    
    # Add correlation values
    for i in range(len(feature_names)):
        for j in range(len(feature_names)):
            text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Feature Correlation Matrix')
    fig.colorbar(im)
    
    return fig


def statistical_significance_test(baseline_errors, ml_errors):
    """
    Test if ML model is significantly better than baseline.
    
    Args:
        baseline_errors: array of baseline prediction errors
        ml_errors: array of ML prediction errors
        
    Returns:
        dict with test results
    """
    # Wilcoxon signed-rank test (paired, non-parametric)
    statistic, p_value = stats.wilcoxon(baseline_errors, ml_errors)
    
    # Also compute effect size (Cohen's d)
    mean_diff = np.mean(baseline_errors) - np.mean(ml_errors)
    pooled_std = np.sqrt((np.std(baseline_errors)**2 + np.std(ml_errors)**2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
    
    return {
        'test': 'Wilcoxon signed-rank',
        'statistic': statistic,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'cohens_d': cohens_d,
        'effect_size': 'small' if abs(cohens_d) < 0.5 else 'medium' if abs(cohens_d) < 0.8 else 'large'
    }
