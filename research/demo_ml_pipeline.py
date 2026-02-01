"""
Demo: ML Research Pipeline
Train and evaluate ML models on sample scripts.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse import runner
from research import features, ml_models, evaluation, ablation
import numpy as np

def run_ml_demo():
    """
    Complete ML research pipeline demonstration using synthetic data.
    """
    print("=" * 70)
    print("ScriptPulse ML Research Pipeline Demo")
    print("=" * 70)
    
    # Create synthetic dataset (simulating 20 scenes)
    print("\n1. Creating synthetic dataset (20 scenes)...")
    np.random.seed(42)
    n_samples = 20
    
    # Synthetic feature matrix [dialogue_ratio, sentiment_var, etc.]
    X = np.random.rand(n_samples, 7)
    X[:, 0] = np.clip(X[:, 0], 0.2, 0.8)  # dialogue_ratio: [0.2, 0.8]
    
    # Synthetic tension scores (ground truth)
    # Higher dialogue_ratio = lower tension (inverse relationship)
    y_true = 1.0 - X[:, 0] + 0.2 * X[:, 1] + np.random.normal(0, 0.1, n_samples)
    y_true = np.clip(y_true, 0, 1)
    
    feat_names = features.get_feature_names()
    print(f"   - Feature matrix shape: {X.shape}")
    print(f"   - Features: {', '.join(feat_names)}")
    print(f"   - Target values (tension): mean={y_true.mean():.3f}, std={y_true.std():.3f}")
    
    # Train ML model
    print("\n2. Training Random Forest model...")
    rf_model = ml_models.train_model(X, y_true, model_type='random_forest')
    print("   - Model trained successfully")
    
    # Evaluate
    print("\n3. Evaluating model performance...\n")
    ml_results = ml_models.evaluate_model(rf_model, X, y_true)
    
    # Baseline comparison
    baseline_pred = evaluation.baseline_heuristic(X)
    comparison = evaluation.compare_models(y_true, baseline_pred, ml_results['predictions'])
    
    print(evaluation.generate_evaluation_report(comparison))
    
    # Cross-validation
    print("\n4. Running 5-fold cross-validation...")
    cv_results = ml_models.cross_validate(X, y_true, model_type='random_forest', k_folds=5)
    print(f"   - MAE: {cv_results['mae_mean']:.4f} ± {cv_results['mae_std']:.4f}")
    print(f"   - RMSE: {cv_results['rmse_mean']:.4f} ± {cv_results['rmse_std']:.4f}")
    print(f"   - R²: {cv_results['r2_mean']:.4f} ± {cv_results['r2_std']:.4f}")
    
    # Ablation study
    print("\n5. Performing ablation study...")
    ablation_data = ablation.ablation_study(X, y_true, model_type='random_forest')
    print(ablation.generate_ablation_report(ablation_data))
    
    print("\n" + "=" * 70)
    print("ML Research Pipeline Complete!")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"  - ML model outperforms baseline by {comparison['improvement']['mae_improvement']:.1f}%")
    print(f"  - Most important feature: {ablation_data['ablation_results'][0]['feature']}")

if __name__ == '__main__':
    run_ml_demo()

    print("=" * 70)
    print("ScriptPulse ML Research Pipeline Demo")
    print("=" * 70)
    
    # Sample script
    sample_script = """
INT. OFFICE - DAY

JOHN sits at his desk, nervous.

JOHN
I can't do this anymore.

MARY enters, angry.

MARY
You have to! We need you.

John stands, defiant.

JOHN
No. I'm done.

Mary slams the door and leaves.
"""
    
    print("\n1. Running ScriptPulse analysis...")
    report = runner.run_pipeline(sample_script, genre='drama')
    
    # Get scenes from segmented data
    scenes = report.get('segmented', [])
    if not scenes:
        # Fallback: create dummy scenes for demo
        scenes = [{'lines': [{'tag': 'D', 'text': 'Sample dialogue'}]}] * 3
    
    print(f"   - Analyzed {len(scenes)} scenes")
    print(f"   - Tension trace: {len(report['temporal_trace'])} points")
    
    # Extract features
    print("\n2. Extracting ML features...")
    X = features.extract_features(scenes, report)
    feat_names = features.get_feature_names()
    
    print(f"   - Feature matrix shape: {X.shape}")
    print(f"   - Features: {', '.join(feat_names)}")
    
    # Get ground truth (heuristic tension scores)
    y_true = np.array([p['attentional_signal'] for p in report['temporal_trace']])
    
    # Create synthetic dataset
    print("\n3. Creating synthetic training data...")
    X_train, y_train = ml_models.create_synthetic_dataset(X, y_true, noise_level=0.1)
    print(f"   - Training samples: {len(y_train)}")
    
    # Train ML model
    print("\n4. Training Random Forest model...")
    rf_model = ml_models.train_model(X_train, y_train, model_type='random_forest')
    print("   - Model trained successfully")
    
    # Evaluate
    print("\n5. Evaluating model performance...\n")
    ml_results = ml_models.evaluate_model(rf_model, X, y_true)
    
    # Baseline comparison
    baseline_pred = evaluation.baseline_heuristic(X)
    comparison = evaluation.compare_models(y_true, baseline_pred, ml_results['predictions'])
    
    print(evaluation.generate_evaluation_report(comparison))
    
    # Cross-validation
    print("\n6. Running 5-fold cross-validation...")
    cv_results = ml_models.cross_validate(X_train, y_train, model_type='random_forest', k_folds=5)
    print(f"   - MAE: {cv_results['mae_mean']:.4f} ± {cv_results['mae_std']:.4f}")
    print(f"   - RMSE: {cv_results['rmse_mean']:.4f} ± {cv_results['rmse_std']:.4f}")
    print(f"   - R²: {cv_results['r2_mean']:.4f} ± {cv_results['r2_std']:.4f}")
    
    # Ablation study
    print("\n7. Performing ablation study...")
    ablation_data = ablation.ablation_study(X_train, y_train, model_type='random_forest')
    print(ablation.generate_ablation_report(ablation_data))
    
    print("\n" + "=" * 70)
    print("ML Research Pipeline Complete!")
    print("=" * 70)

if __name__ == '__main__':
    run_ml_demo()
