"""
ScriptPulse Language Compliance Verification
"""

import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse.agents import mediation

class TestLanguageCompliance(unittest.TestCase):
    
    def test_asl_presence(self):
        """Ensure Audience Scope Lock is present in reflections"""
        pattern = {'pattern_type': 'sustained_attentional_demand', 'confidence': 'high', 'scene_range': [1, 5]}
        
        # Test Reflection
        res = mediation.generate_reflection(pattern)
        print("\nReflection Output:", res['reflection'])
        self.assertIn("screenplay-literate first-pass reader", res['reflection'])
        self.assertNotIn("first-time audience", res['reflection'])
        
    def test_silence_language(self):
        """Ensure Silence supports ASL and avoids 'Success'"""
        ssf = {'is_silent': True, 'explanation_key': 'stable_continuity'}
        
        # Test Silence
        res = mediation.generate_silence_explanation([], [], ssf)
        print("\nSilence Output:", res)
        self.assertIn("screenplay-literate first-pass reader", res)
        self.assertNotIn("success", res.lower())
        self.assertNotIn("good job", res.lower())

if __name__ == '__main__':
    print("=== Running Language Compliance Check ===")
    unittest.main()
