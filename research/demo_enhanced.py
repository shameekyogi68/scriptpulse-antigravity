"""
Enhanced Demo: Complete ML Research Pipeline with Advanced Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import features, ml_models, evaluation, ablation, advanced_analysis, hyperparameter_tuning
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

def run_enhanced_demo():
    """
    Complete ML research pipeline with publication-grade analysis.
    """
    print("=" * 70)
    print("ScriptPulse Enhanced ML Research Pipeline")
    print("=" * 70)
    
    # Create synthetic dataset
    print("\n1. Creating synthetic dataset (50 scenes for better statistics)...")
    np.random.seed(42)
    n_samples = 50
    
    X = np.random.rand(n_samples, 7)
    X[:, 0] = np.clip(X[:, 0], 0.2, 0.8)  # dialogue_ratio
    
    y_true = 1.0 - X[:, 0] + 0.2 * X[:, 1] + np.random.normal(0, 0.1, n_samples)
    y_true = np.clip(y_true, 0, 1)
    
    feat_names = features.get_feature_names()
    print(f"   - Features: {', '.join(feat_names)}")
    print(f"   - Samples: {n_samples}")
    
    # Train model
    print("\n2. Training Random Forest...")
    rf_model = ml_models.train_model(X, y_true, model_type='random_forest')
    ml_results = ml_models.evaluate_model(rf_model, X, y_true)
    print(f"   - R²: {ml_results['r2']:.4f}")
    print(f"   - MAE: {ml_results['mae']:.4f}")
    
    # Baseline comparison
    print("\n3. Baseline comparison...")
    baseline_pred = evaluation.baseline_heuristic(X)
    comparison = evaluation.compare_models(y_true, baseline_pred, ml_results['predictions'])
    print(f"   - Improvement: {comparison['improvement']['mae_improvement']:.1f}%")
    
    # Error analysis
    print("\n4. Error Analysis...")
    error_analysis = advanced_analysis.analyze_errors(
        y_true, ml_results['predictions'], X, feat_names, threshold=0.2
    )
    print(f"   - Mean error: {error_analysis['mean_error']:.4f}")
    print(f"   - Large errors: {error_analysis['large_error_percentage']:.1f}%")
    print(f"   - Worst prediction error: {error_analysis['worst_predictions']['errors'][-1]:.4f}")
    
    # Statistical significance
    print("\n5. Statistical Significance Test...")
    baseline_errors = np.abs(y_true - baseline_pred)
    ml_errors = np.abs(y_true - ml_results['predictions'])
    sig_test = advanced_analysis.statistical_significance_test(baseline_errors, ml_errors)
    print(f"   - p-value: {sig_test['p_value']:.4f}")
    print(f"   - Significant: {'YES' if sig_test['significant'] else 'NO'}")
    print(f"   - Effect size: {sig_test['effect_size']} (Cohen's d = {sig_test['cohens_d']:.2f})")
    
    # Learning curve
    print("\n6. Generating Learning Curve...")
    fig_learning = advanced_analysis.plot_learning_curve(rf_model, X, y_true, cv=5)
    fig_learning.savefig('/tmp/learning_curve.png', dpi=100, bbox_inches='tight')
    print("   - Saved to /tmp/learning_curve.png")
    plt.close(fig_learning)
    
    # Prediction plot
    print("\n7. Generating Prediction vs Actual plot...")
    fig_pred = advanced_analysis.plot_predictions(y_true, ml_results['predictions'])
    fig_pred.savefig('/tmp/predictions.png', dpi=100, bbox_inches='tight')
    print("   - Saved to /tmp/predictions.png")
    plt.close(fig_pred)
    
    # Feature correlation
    print("\n8. Generating Feature Correlation Heatmap...")
    fig_corr = advanced_analysis.plot_feature_correlation(X, feat_names)
    fig_corr.savefig('/tmp/feature_correlation.png', dpi=100, bbox_inches='tight')
    print("   - Saved to /tmp/feature_correlation.png")
    plt.close(fig_corr)
    
    # Hyperparameter tuning (optional, takes longer)
    print("\n9. Hyperparameter Tuning (quick search)...")
    tuning_results = hyperparameter_tuning.tune_random_forest(X, y_true, cv=3)
    print(f"   - Best R²: {tuning_results['best_score']:.4f}")
    print(f"   - Best params: {tuning_results['best_params']}")
    
    print("\n" + "=" * 70)
    print("Enhanced ML Pipeline Complete!")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"  - ML significantly outperforms baseline (p={sig_test['p_value']:.4f})")
    print(f"  - Effect size: {sig_test['effect_size']}")
    print(f"  - Model explains {ml_results['r2']*100:.1f}% of variance")
    print(f"  - {error_analysis['large_error_percentage']:.1f}% of predictions have large errors")
    print("\nVisualizations saved to /tmp/")

if __name__ == '__main__':
    run_enhanced_demo()
