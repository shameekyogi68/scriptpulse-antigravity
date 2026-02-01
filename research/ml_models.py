"""
ScriptPulse ML Models Module
Train and evaluate machine learning models for tension prediction.
"""

import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def create_synthetic_dataset(features, heuristic_tension_scores, noise_level=0.1):
    """
    Create synthetic training data using heuristic scores as ground truth.
    Add noise to simulate human annotation variance.
    
    Args:
        features: numpy array [N x 7]
        heuristic_tension_scores: list of tension scores from current system
        noise_level: std of Gaussian noise to add
        
    Returns:
        X, y for training
    """
    X = features
    y = np.array(heuristic_tension_scores)
    
    # Add noise to simulate annotation variance
    noise = np.random.normal(0, noise_level, size=y.shape)
    y_noisy = np.clip(y + noise, 0, 1)  # Keep in [0, 1] range
    
    return X, y_noisy


def train_model(X, y, model_type='random_forest'):
    """
    Train a regression model to predict tension scores.
    
    Args:
        X: feature matrix [N x 7]
        y: target tension scores [N]
        model_type: 'random_forest', 'gradient_boosting', or 'mlp'
        
    Returns:
        trained model
    """
    if model_type == 'random_forest':
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    elif model_type == 'mlp':
        model = MLPRegressor(
            hidden_layer_sizes=(32, 16),
            activation='relu',
            max_iter=500,
            random_state=42
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X, y)
    return model


def evaluate_model(model, X, y):
    """
    Compute regression metrics.
    
    Returns:
        dict with MAE, RMSE, R2
    """
    y_pred = model.predict(X)
    
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'predictions': y_pred
    }


def cross_validate(X, y, model_type='random_forest', k_folds=5):
    """
    Perform k-fold cross-validation.
    
    Returns:
        dict with mean and std of metrics
    """
    if model_type == 'random_forest':
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    else:
        model = MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)
    
    # Cross-validation for R2
    r2_scores = cross_val_score(model, X, y, cv=k_folds, scoring='r2')
    
    # Cross-validation for MAE
    mae_scores = -cross_val_score(model, X, y, cv=k_folds, scoring='neg_mean_absolute_error')
    
    # Cross-validation for RMSE
    rmse_scores = np.sqrt(-cross_val_score(model, X, y, cv=k_folds, scoring='neg_mean_squared_error'))
    
    return {
        'mae_mean': np.mean(mae_scores),
        'mae_std': np.std(mae_scores),
        'rmse_mean': np.mean(rmse_scores),
        'rmse_std': np.std(rmse_scores),
        'r2_mean': np.mean(r2_scores),
        'r2_std': np.std(r2_scores)
    }


def save_model(model, filepath):
    """Save trained model to disk."""
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)


def load_model(filepath):
    """Load trained model from disk."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)
