"""
ScriptPulse Hyperparameter Tuning Module
Grid search for optimal model parameters.
"""

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

def tune_random_forest(X, y, cv=5):
    """
    Hyperparameter tuning for Random Forest.
    
    Returns:
        best model and parameters
    """
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    
    rf = RandomForestRegressor(random_state=42)
    
    grid_search = GridSearchCV(
        rf, param_grid,
        cv=cv,
        scoring='r2',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X, y)
    
    return {
        'best_model': grid_search.best_estimator_,
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'all_results': grid_search.cv_results_
    }


def tune_gradient_boosting(X, y, cv=5):
    """
    Hyperparameter tuning for Gradient Boosting.
    
    Returns:
        best model and parameters
    """
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.3]
    }
    
    gb = GradientBoostingRegressor(random_state=42)
    
    grid_search = GridSearchCV(
        gb, param_grid,
        cv=cv,
        scoring='r2',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X, y)
    
    return {
        'best_model': grid_search.best_estimator_,
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'all_results': grid_search.cv_results_
    }


def generate_tuning_report(tuning_results, model_name="Model"):
    """
    Generate formatted hyperparameter tuning report.
    
    Args:
        tuning_results: output from tune_* functions
        model_name: name for display
        
    Returns:
        markdown string
    """
    report = f"# Hyperparameter Tuning: {model_name}\n\n"
    
    report += "## Best Parameters\n\n"
    for param, value in tuning_results['best_params'].items():
        report += f"- **{param}**: {value}\n"
    
    report += f"\n**Best CV Score (R²)**: {tuning_results['best_score']:.4f}\n\n"
    
    report += "## Interpretation\n\n"
    report += f"Grid search identified optimal hyperparameters with R² of {tuning_results['best_score']:.4f}. "
    report += "These parameters balance model complexity and generalization.\n"
    
    return report
