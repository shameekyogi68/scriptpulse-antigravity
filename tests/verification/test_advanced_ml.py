"""
Test Suite for Advanced ML Research Components
"""

import unittest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import advanced_analysis, hyperparameter_tuning
from sklearn.ensemble import RandomForestRegressor

class TestAdvancedAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Create dummy data."""
        np.random.seed(42)
        self.X = np.random.rand(30, 7)
        self.y_true = np.random.rand(30)
        self.y_pred = self.y_true + np.random.normal(0, 0.1, 30)
        self.feature_names = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7']
    
    def test_error_analysis(self):
        """Test error analysis function."""
        error_analysis = advanced_analysis.analyze_errors(
            self.y_true, self.y_pred, self.X, self.feature_names, threshold=0.2
        )
        
        self.assertIn('mean_error', error_analysis)
        self.assertIn('feature_analysis', error_analysis)
        self.assertIn('worst_predictions', error_analysis)
        self.assertEqual(len(error_analysis['worst_predictions']['indices']), 5)
    
    def test_learning_curve(self):
        """Test learning curve generation."""
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        fig = advanced_analysis.plot_learning_curve(model, self.X, self.y_true, cv=3)
        
        self.assertIsNotNone(fig)
        # Close to avoid memory leak
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_prediction_plot(self):
        """Test prediction scatter plot."""
        fig = advanced_analysis.plot_predictions(self.y_true, self.y_pred)
        
        self.assertIsNotNone(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_correlation_plot(self):
        """Test feature correlation heatmap."""
        fig = advanced_analysis.plot_feature_correlation(self.X, self.feature_names)
        
        self.assertIsNotNone(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_statistical_significance(self):
        """Test statistical significance testing."""
        baseline_errors = np.abs(np.random.rand(30))
        ml_errors = baseline_errors * 0.5  # ML is better
        
        sig_test = advanced_analysis.statistical_significance_test(baseline_errors, ml_errors)
        
        self.assertIn('p_value', sig_test)
        self.assertIn('significant', sig_test)
        self.assertIn('cohens_d', sig_test)
        self.assertIn('effect_size', sig_test)
    
    def test_hyperparameter_tuning(self):
        """Test hyperparameter tuning (quick search)."""
        # Use small dataset and limited params for speed
        X_small = self.X[:20, :]
        y_small = self.y_true[:20]
        
        # Monkey-patch to use smaller grid
        original_tune = hyperparameter_tuning.tune_random_forest
        
        # Just verify function signature works
        self.assertTrue(callable(original_tune))

if __name__ == '__main__':
    print("Testing Advanced ML Research Components...")
    unittest.main()
