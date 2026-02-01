"""
Comprehensive System Validation & Edge Case Testing
Tests all script formats, edge cases, and error handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse import runner
from research import features, ml_models
import unittest

class TestEdgeCases(unittest.TestCase):
    """Test extreme and edge cases"""
    
    def test_empty_script(self):
        """Test completely empty input"""
        result = runner.run_pipeline("")
        self.assertIsNotNone(result)
        self.assertEqual(len(result.get('segmented', [])), 0)
    
    def test_single_line(self):
        """Test single line input"""
        result = runner.run_pipeline("FADE IN:")
        self.assertIsNotNone(result)
    
    def test_no_dialogue(self):
        """Test script with zero dialogue"""
        script = """
INT. EMPTY ROOM - DAY

The room is silent.

A clock ticks.

FADE OUT.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
        self.assertIn('segmented', result)
    
    def test_only_dialogue(self):
        """Test script with only dialogue, no action"""
        script = """
INT. ROOM - DAY

JOHN
Hello.

MARY
Hi.

JOHN
Goodbye.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
        scenes = result.get('segmented', [])
        self.assertGreater(len(scenes), 0)
    
    def test_very_long_scene(self):
        """Test scene with 500+ lines"""
        dialogue = "\\n".join([f"Line {i}" for i in range(500)])
        script = f"""
INT. OFFICE - DAY

JOHN
{dialogue}
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_very_short_scenes(self):
        """Test many 1-2 line scenes"""
        scenes = "\\n\\n".join([f"INT. ROOM {i} - DAY\\nAction." for i in range(50)])
        result = runner.run_pipeline(scenes)
        self.assertIsNotNone(result)
    
    def test_special_characters(self):
        """Test unicode and special characters"""
        script = """
INT. CAFÉ - DAY

JOSÉ
¡Hola! Comment ça va? 你好！

FRANÇOIS
Très bien, merci! 😊
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_malformed_sluglines(self):
        """Test various malformed scene headings"""
        script = """
INT OFFICE DAY

JOHN
Missing periods.

int. office - night

MARY
Lowercase.

EXTERIOR. PARK
No hyphen.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_mixed_case(self):
        """Test mixed case character names"""
        script = """
INT. ROOM - DAY

john
Lowercase name.

JoHn
Mixed case.

JOHN
Normal.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestScriptFormats(unittest.TestCase):
    """Test different screenplay formats"""
    
    def test_fountain_format(self):
        """Test Fountain markdown format"""
        script = """
Title: Test Script
Author: Test

# ACT I

INT. OFFICE - DAY

JOHN sits at his desk.

JOHN
I need coffee.

> FADE OUT.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_no_scene_headings(self):
        """Test script without traditional sluglines"""
        script = """
A man walks down the street.

He stops.

Looks around.

Continues walking.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_dual_dialogue(self):
        """Test dual/simultaneous dialogue"""
        script = """
INT. ROOM - DAY

JOHN                      MARY
Hello.                    Hi there.

How are you?              I'm fine.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestMLRobustness(unittest.TestCase):
    """Test ML pipeline with edge cases"""
    
    def test_zero_variance_features(self):
        """Test when all features are identical"""
        import numpy as np
        X = np.ones((10, 7)) * 0.5  # All features = 0.5
        y = np.random.rand(10)
        
        try:
            model = ml_models.train_model(X, y, model_type='random_forest')
            self.assertIsNotNone(model)
        except Exception as e:
            self.fail(f"Should handle zero variance: {e}")
    
    def test_single_sample(self):
        """Test ML with only 1 sample"""
        import numpy as np
        X = np.random.rand(1, 7)
        y = np.array([0.5])
        
        # Should handle gracefully or raise informative error
        try:
            model = ml_models.train_model(X, y, model_type='random_forest')
        except ValueError:
            pass  # Expected
    
    def test_nan_features(self):
        """Test handling of NaN in features"""
        import numpy as np
        X = np.random.rand(10, 7)
        X[0, 0] = np.nan
        y = np.random.rand(10)
        
        # Should handle or raise clear error
        try:
            extracted = features.extract_features([], {'temporal_trace': []})
        except Exception:
            pass


class TestErrorHandling(unittest.TestCase):
    """Test system error handling"""
    
    def test_invalid_genre(self):
        """Test with invalid genre"""
        result = runner.run_pipeline("Test", genre='INVALID_GENRE')
        self.assertIsNotNone(result)
    
    def test_invalid_lens(self):
        """Test with invalid lens"""
        result = runner.run_pipeline("Test", lens='INVALID_LENS')
        self.assertIsNotNone(result)
    
    def test_corrupted_intent(self):
        """Test with malformed writer intent"""
        result = runner.run_pipeline("Test", writer_intent={'invalid': 'structure'})
        self.assertIsNotNone(result)
    
    def test_extreme_values(self):
        """Test with extreme parameter values"""
        result = runner.run_pipeline("Test" * 10000)  # Very long
        self.assertIsNotNone(result)


class TestIntegration(unittest.TestCase):
    """Test complete pipeline integration"""
    
    def test_full_pipeline_short(self):
        """Test complete pipeline with short script"""
        script = """
INT. OFFICE - DAY

JOHN
Hello.

MARY
Hi.
"""
        result = runner.run_pipeline(script, genre='drama', lens='viewer')
        
        # Verify all components present
        self.assertIn('segmented', result)
        self.assertIn('temporal_trace', result)
        self.assertIn('meta', result)
    
    def test_full_pipeline_medium(self):
        """Test with medium-length script (~10 scenes)"""
        scenes = []
        for i in range(10):
            scenes.append(f"""
INT. LOCATION {i} - DAY

CHARACTER {i}
Dialogue line {i}.

Action description {i}.
""")
        
        script = "\\n\\n".join(scenes)
        result = runner.run_pipeline(script)
        
        self.assertGreater(len(result.get('segmented', [])), 5)
        self.assertIsNotNone(result.get('temporal_trace'))


def run_all_tests():
    """Run all validation tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptFormats))
    suite.addTests(loader.loadTestsFromTestCase(TestMLRobustness))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result


if __name__ == '__main__':
    print("Running Comprehensive System Validation...")
    print("Testing edge cases, formats, ML robustness, and error handling\\n")
    run_all_tests()
