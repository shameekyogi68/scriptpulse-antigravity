"""
Test Suite for ML Research Components
"""

import unittest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import features, ml_models, evaluation, ablation

class TestMLResearch(unittest.TestCase):
    
    def setUp(self):
        """Create dummy data for testing."""
        # Dummy scenes
        self.scenes = [
            {'lines': [
                {'tag': 'D', 'text': 'Hello world'},
                {'tag': 'A', 'text': 'He walks away'},
                {'tag': 'C', 'text': 'JOHN'}
            ]},
            {'lines': [
                {'tag': 'D', 'text': 'Goodbye cruel world'},
                {'tag': 'A', 'text': 'She sighs'},
                {'tag': 'C', 'text': 'MARY'}
            ]}
        ]
        
        # Dummy report data
        self.report_data = {
            'valence_scores': [0.5, -0.3],
            'temporal_trace': [
                {'attentional_signal': 0.6},
                {'attentional_signal': 0.8}
            ]
        }
    
    def test_feature_extraction(self):
        """Test that feature extraction returns correct shape."""
        X = features.extract_features(self.scenes, self.report_data)
        
        # Should have 2 scenes x 7 features
        self.assertEqual(X.shape, (2, 7))
        
        # Check feature names
        feat_names = features.get_feature_names()
        self.assertEqual(len(feat_names), 7)
        self.assertIn('dialogue_ratio', feat_names)
    
    def test_model_training(self):
        """Test that models can be trained."""
        X = np.random.rand(10, 7)
        y = np.random.rand(10)
        
        # Test random forest
        model = ml_models.train_model(X, y, model_type='random_forest')
        self.assertIsNotNone(model)
        
        # Test prediction
        y_pred = model.predict(X)
        self.assertEqual(len(y_pred), 10)
    
    def test_evaluation_metrics(self):
        """Test that evaluation metrics are computed."""
        y_true = np.array([0.5, 0.6, 0.7])
        y_pred = np.array([0.52, 0.58, 0.72])
        
        metrics = evaluation.evaluate_predictions(y_true, y_pred)
        
        self.assertIn('mae', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('r2', metrics)
        
        # MAE should be small for close predictions
        self.assertLess(metrics['mae'], 0.1)
    
    def test_cross_validation(self):
        """Test cross-validation runs without errors."""
        X = np.random.rand(20, 7)
        y = np.random.rand(20)
        
        cv_results = ml_models.cross_validate(X, y, model_type='random_forest', k_folds=3)
        
        self.assertIn('mae_mean', cv_results)
        self.assertIn('mae_std', cv_results)
        self.assertIn('r2_mean', cv_results)
    
    def test_ablation_study(self):
        """Test ablation study produces feature rankings."""
        X = np.random.rand(15, 7)
        y = np.random.rand(15)
        
        ablation_data = ablation.ablation_study(X, y, model_type='random_forest')
        
        self.assertIn('full_model_r2', ablation_data)
        self.assertIn('ablation_results', ablation_data)
        
        # Should have 7 feature results
        self.assertEqual(len(ablation_data['ablation_results']), 7)
        
        # Rankings should be 1-7
        ranks = [r['importance_rank'] for r in ablation_data['ablation_results']]
        self.assertEqual(sorted(ranks), list(range(1, 8)))

if __name__ == '__main__':
    print("Testing ML Research Components...")
    unittest.main()
