"""
ScriptPulse v5.2 Deep-Maturity Verification
Tests CBN, AOI, FPG, ADS.
"""

import sys
import os
import unittest
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse.agents import mediation, temporal
from scriptpulse import drift_monitor

class TestV5_2_Safeguards(unittest.TestCase):
    
    def test_cbn_normalization(self):
        """Test Cognitive Baseline Normalization"""
        # Case 1: High Load Script (Median > 0.5)
        # Thresholds should be raised (harder to trigger High)
        high_baseline = 1.5
        state = temporal.classify_fatigue_state(0.8, baseline_factor=high_baseline)
        # 0.8 is usually 'elevated' or 'high' (default threshold_high=1.0)
        # With factor 1.5, threshold_high=1.5. So 0.8 is likely 'elevated' or 'normal' depending on elevated threshold (0.5*1.5=0.75).
        # 0.8 > 0.75 -> Elevated. (If it was factor 1.0, 0.8 is High? No, default high is 1.0. Elevated is 0.5. 0.8 is already elevated.)
        # Let's check a signal that WOULD be High without CBN.
        # Signal 1.2. Default High > 1.0.
        # With CBN 1.5: High > 1.5. So 1.2 is ELEVATED.
        
        state_norm = temporal.classify_fatigue_state(1.2, baseline_factor=1.0)
        self.assertEqual(state_norm, "high") # 1.2 > 1.0
        
        state_cbn = temporal.classify_fatigue_state(1.2, baseline_factor=1.5)
        self.assertNotEqual(state_cbn, "high") # Should be lower (elevated)
        self.assertEqual(state_cbn, "elevated") # 1.2 < 1.5
        print(f"\nCBN Verified: 1.2 signal is '{state_norm}' normally, but '{state_cbn}' with high baseline.")

    def test_aoi_anti_optimization(self):
        """Test Drift Monitor detects optimization loop"""
        dm = drift_monitor.DriftMonitor()
        meta = {'fingerprint': 'aabbcc'}
        
        # Log 10 identical runs
        for _ in range(10):
            dm.log_run(meta)
            
        self.assertTrue(dm.aoi_active)
        factor = dm.get_dampening_factor()
        self.assertLess(factor, 1.0)
        print(f"\nAOI Active. Dampening Factor: {factor}")
        
    def test_fpg_late_uncertainty(self):
        """Test False Precision Guard for late scenes"""
        pattern = {'pattern_type': 'test', 'confidence': 'high', 'scene_range': [90, 95]}
        # Total scenes 100. Range 90-95 is > 0.8 relative.
        res = mediation.generate_reflection(pattern, total_scenes=100)
        self.assertIn("uncertainty increases late", res['reflection'])
        print("\nFPG Verified: Late script uncertainty added.")
        
    def test_ads_disclaimer(self):
        """Test Authority Diffusion Safeguard"""
        output = {'reflections': []}
        text = mediation.format_for_display(output)
        self.assertTrue(any(d in text for d in mediation.ADS_DISCLAIMERS))
        print("\nADS Verified: Disclaimer present.")

if __name__ == '__main__':
    print("=== Running v5.2 Safeguards Verification ===")
    unittest.main()
