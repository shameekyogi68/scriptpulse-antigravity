"""
ScriptPulse Ablation Study
Feature importance analysis via systematic feature removal.
"""

import numpy as np
from . import ml_models, features

def ablation_study(X, y, model_type='random_forest'):
    """
    Perform ablation study: measure performance drop when removing each feature.
    
    Args:
        X: feature matrix [N x 7]
        y: target labels [N]
        model_type: type of ML model to use
        
    Returns:
        dict with feature importance results
    """
    feature_names = features.get_feature_names()
    
    # Train full model
    full_model = ml_models.train_model(X, y, model_type=model_type)
    full_results = ml_models.evaluate_model(full_model, X, y)
    full_r2 = full_results['r2']
    
    ablation_results = []
    
    # For each feature, remove it and retrain
    for i, feat_name in enumerate(feature_names):
        # Create ablated feature matrix (remove column i)
        X_ablated = np.delete(X, i, axis=1)
        
        # Train model without this feature
        ablated_model = ml_models.train_model(X_ablated, y, model_type=model_type)
        ablated_results = ml_models.evaluate_model(ablated_model, X_ablated, y)
        ablated_r2 = ablated_results['r2']
        
        # Measure performance drop
        delta_r2 = full_r2 - ablated_r2
        
        ablation_results.append({
            'feature': feat_name,
            'r2_full': full_r2,
            'r2_ablated': ablated_r2,
            'delta': delta_r2,
            'importance_rank': 0  # Will be filled after sorting
        })
    
    # Sort by importance (largest delta = most important)
    ablation_results.sort(key=lambda x: x['delta'], reverse=True)
    
    # Assign ranks
    for rank, result in enumerate(ablation_results, 1):
        result['importance_rank'] = rank
    
    return {
        'full_model_r2': full_r2,
        'ablation_results': ablation_results
    }


def generate_ablation_report(ablation_data):
    """
    Generate formatted ablation study report.
    
    Args:
        ablation_data: output from ablation_study()
        
    Returns:
        markdown string
    """
    report = "# Ablation Study: Feature Importance\n\n"
    
    full_r2 = ablation_data['full_model_r2']
    results = ablation_data['ablation_results']
    
    report += f"**Full Model R²:** {full_r2:.4f}\n\n"
    
    report += "## Feature Importance Ranking\n\n"
    report += "| Rank | Feature | R² (full) | R² (ablated) | Delta | \n"
    report += "|------|---------|-----------|--------------|-------|\n"
    
    for r in results:
        star = " ⭐" if r['importance_rank'] == 1 else ""
        report += f"| {r['importance_rank']} | {r['feature']}{star} | "
        report += f"{r['r2_full']:.4f} | {r['r2_ablated']:.4f} | "
        report += f"{r['delta']:.4f} |\n"
    
    report += "\n## Interpretation\n\n"
    
    most_important = results[0]
    report += f"**Most Important Feature:** `{most_important['feature']}` (Δ R² = {most_important['delta']:.4f})\n\n"
    report += f"Removing this feature causes a **{most_important['delta']*100:.1f}% drop** in explained variance, "
    report += "indicating it is the strongest predictor of scene tension.\n\n"
    
    least_important = results[-1]
    report += f"**Least Important Feature:** `{least_important['feature']}` (Δ R² = {least_important['delta']:.4f})\n\n"
    
    return report
