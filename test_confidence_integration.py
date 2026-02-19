
import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.validation.confidence import ConfidenceScorer

class TestConfidence(unittest.TestCase):
    def test_short_script(self):
        # 5 scenes, flat
        trace = [{'attentional_signal': 0.5, 'fatigue_state': 0.0} for _ in range(5)]
        res = ConfidenceScorer().calculate(trace)
        self.assertEqual(res['level'], 'LOW')
        self.assertIn('Insufficient Length', str(res['reasons']))
        
    def test_flatline(self):
        # 50 scenes, exact same signal (variance = 0)
        trace = [{'attentional_signal': 0.5, 'fatigue_state': 0.0} for _ in range(50)]
        res = ConfidenceScorer().calculate(trace)
        self.assertIn('Signal Flatline', str(res['reasons']))
        
    def test_healthy(self):
        # 50 scenes, good variance
        import random
        trace = [{'attentional_signal': random.uniform(0.1, 0.9), 'fatigue_state': 0.0} for _ in range(50)]
        res = ConfidenceScorer().calculate(trace)
        self.assertEqual(res['level'], 'HIGH')
        self.assertEqual(res['reasons'], [])

if __name__ == '__main__':
    unittest.main()
