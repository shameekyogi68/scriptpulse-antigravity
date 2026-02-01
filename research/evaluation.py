"""
ScriptPulse Evaluation Module
Quantitative metrics and baseline comparisons.
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def baseline_heuristic(features):
    """
    Simple baseline: predict tension from dialogue ratio only.
    Higher dialogue = lower tension (inverse relationship).
    
    Args:
        features: numpy array [N x 7]
        
    Returns:
        predictions [N]
    """
    dialogue_ratio = features[:, 0]  # First feature
    # Inverse relationship: more dialogue = less tension
    predictions = 1.0 - dialogue_ratio
    return predictions


def evaluate_predictions(y_true, y_pred, model_name="Model"):
    """
    Compute and print regression metrics.
    
    Args:
        y_true: ground truth scores
        y_pred: predicted scores
        model_name: name for display
        
    Returns:
        dict of metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        'model': model_name,
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    }
    
    return metrics


def compare_models(y_true, baseline_pred, ml_pred):
    """
    Compare ML model against baseline.
    
    Returns:
        Comparison report as dict
    """
    baseline_metrics = evaluate_predictions(y_true, baseline_pred, "Heuristic Baseline")
    ml_metrics = evaluate_predictions(y_true, ml_pred, "ML Model")
    
    improvement = {
        'mae_improvement': (baseline_metrics['mae'] - ml_metrics['mae']) / baseline_metrics['mae'] * 100,
        'rmse_improvement': (baseline_metrics['rmse'] - ml_metrics['rmse']) / baseline_metrics['rmse'] * 100,
        'r2_improvement': (ml_metrics['r2'] - baseline_metrics['r2']) / abs(baseline_metrics['r2']) * 100 if baseline_metrics['r2'] != 0 else 0
    }
    
    return {
        'baseline': baseline_metrics,
        'ml_model': ml_metrics,
        'improvement': improvement
    }


def generate_evaluation_report(comparison, cv_results=None):
    """
    Generate formatted text report for research paper.
    
    Args:
        comparison: output from compare_models()
        cv_results: optional cross-validation results
        
    Returns:
        markdown formatted string
    """
    report = "# Model Evaluation Report\n\n"
    
    report += "## Performance Comparison\n\n"
    report += "| Metric | Baseline | ML Model | Improvement |\n"
    report += "|--------|----------|----------|-------------|\n"
    
    baseline = comparison['baseline']
    ml = comparison['ml_model']
    imp = comparison['improvement']
    
    report += f"| MAE    | {baseline['mae']:.4f} | {ml['mae']:.4f} | {imp['mae_improvement']:.1f}% |\n"
    report += f"| RMSE   | {baseline['rmse']:.4f} | {ml['rmse']:.4f} | {imp['rmse_improvement']:.1f}% |\n"
    report += f"| R²     | {baseline['r2']:.4f} | {ml['r2']:.4f} | +{imp['r2_improvement']:.1f}% |\n\n"
    
    if cv_results:
        report += "## Cross-Validation Results\n\n"
        report += f"- **MAE**: {cv_results['mae_mean']:.4f} ± {cv_results['mae_std']:.4f}\n"
        report += f"- **RMSE**: {cv_results['rmse_mean']:.4f} ± {cv_results['rmse_std']:.4f}\n"
        report += f"- **R²**: {cv_results['r2_mean']:.4f} ± {cv_results['r2_std']:.4f}\n\n"
    
    report += "## Interpretation\n\n"
    if ml['mae'] < baseline['mae']:
        report += f"The ML model achieves **{imp['mae_improvement']:.1f}% lower error** than the heuristic baseline, "
        report += f"demonstrating that learned features generalize better than simple dialogue ratio.\n"
    
    return report
