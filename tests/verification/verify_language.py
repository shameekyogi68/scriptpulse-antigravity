"""
ScriptPulse Language Compliance Verification
"""

import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse.agents import mediation

class TestLanguageCompliance(unittest.TestCase):
    
    def test_writer_native_framing(self):
        """Ensure reflections use writer-native vocabulary (Grip, Breath, Rhythm)."""
        
        # Test 1: Sustained Demand
        pattern_demand = {'pattern_type': 'sustained_attentional_demand', 'confidence': 'high', 'scene_range': [1, 5]}
        res_demand = mediation.generate_reflection(pattern_demand)
        print("\nDemand Output:", res_demand['reflection'])
        self.assertIn("release valve", res_demand['reflection'])
        self.assertIn("moment to recover", res_demand['reflection'])
        
        # Test 2: Repetition
        pattern_rep = {'pattern_type': 'repetition', 'confidence': 'medium', 'scene_range': [10, 15]}
        res_rep = mediation.generate_reflection(pattern_rep)
        print("\nRepetition Output:", res_rep['reflection'])
        self.assertIn("escalation", res_rep['reflection'])
        
        # Ensure NO banned words
        valid, word = mediation.validate_no_banned_words(res_demand['reflection'])
        self.assertTrue(valid, f"Reflection contained banned word: {word}")
        
    def test_silence_language(self):
        """Ensure Silence uses 'Stability' and 'Flow'"""
        ssf = {'is_silent': True, 'explanation_key': 'stable_continuity'}
        
        # Test Silence
        res = mediation.generate_silence_explanation([], [], ssf)
        print("\nSilence Output:", res)
        # Check for natural language
        self.assertIn("breathing naturally", res.lower())
        self.assertNotIn("success", res.lower())

if __name__ == '__main__':
    print("=== Running Language Compliance Check ===")
    unittest.main()
