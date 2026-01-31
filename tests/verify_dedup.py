"""
ScriptPulse Deduplication & Short Script Verification
"""

import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse.agents import mediation

class TestMediationLogic(unittest.TestCase):
    
    def test_deduplication(self):
        """Ensure overlapping redundant patterns are suppressed."""
        patterns = [
            # High Priority
            {'pattern_type': 'sustained_attentional_demand', 'confidence': 'high', 'scene_range': [0, 10]},
            # Low Priority, Same Range (Should be removed)
            {'pattern_type': 'limited_recovery', 'confidence': 'high', 'scene_range': [0, 10]},
            # Different Range (Should keep)
            {'pattern_type': 'repetition', 'confidence': 'medium', 'scene_range': [15, 20]}
        ]
        
        deduped = mediation.deduplicate_patterns(patterns)
        
        self.assertEqual(len(deduped), 2)
        types = [p['pattern_type'] for p in deduped]
        self.assertIn('sustained_attentional_demand', types)
        self.assertNotIn('limited_recovery', types)
        self.assertIn('repetition', types)
        print("\nDeduplication Verified: redundant patterns suppressed.")

    def test_short_script_fpg(self):
        """Ensure FPG logic ignores short scripts."""
        pattern = {'pattern_type': 'test', 'confidence': 'high', 'scene_range': [10, 10]}
        
        # Case 1: Short Script (11 scenes). Should NOT have "Deep in script" warning.
        res_short = mediation.generate_reflection(pattern, total_scenes=11)
        self.assertNotIn("Deep in the script", res_short['reflection'])
        
        # Case 2: Long Script (100 scenes). Should HAVE warning for late scene.
        pattern_late = {'pattern_type': 'test', 'confidence': 'high', 'scene_range': [90, 95]}
        res_long = mediation.generate_reflection(pattern_late, total_scenes=100)
        self.assertIn("Deep in the script", res_long['reflection'])
        print("\nShort Script FPG Verified.")

if __name__ == '__main__':
    print("=== Running Mediation Deduplication Logic Check ===")
    unittest.main()
