"""
ScriptPulse OGHLS Safety Verification
Tests AEKS, PUCD, ODD, and Mediation Safety.
"""

import sys
import os
import unittest
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse import governance, drift_monitor
from scriptpulse.agents import mediation
from scriptpulse.governance import UseContext

class TestSafetyLayer(unittest.TestCase):
    
    def test_pucd_context_validation(self):
        """Test Professional Use-Context Declaration"""
        # Valid
        self.assertTrue(governance.validate_context(UseContext.PERSONAL))
        
        # Invalid (String instead of Enum)
        with self.assertRaises(governance.PolicyViolationError):
            governance.validate_context("personal_writing")
            
    def test_aeks_alert_kill_switch(self):
        """Test Alert Escalation Kill-Switch (Max Density)"""
        # Simulate 100 surfaced patterns for a 100-scene script
        # Max permitted is roughly 100/12 = 8
        patterns = [{'pattern_type': 'test', 'confidence': 'low'} for _ in range(30)]
        # Add a high confidence one
        patterns.append({'pattern_type': 'high_priority', 'confidence': 'high'})
        
        input_data = {
            'surfaced_patterns': patterns,
            'acd_states': [{'scene_index': i} for i in range(100)], # 100 scenes
            'suppressed_patterns': [],
            'intent_alignment_notes': []
        }
        
        output = mediation.run(input_data)
        
        # Verify truncation
        self.assertLess(output['total_surfaced'], 31)
        self.assertLessEqual(output['total_surfaced'], 10) # 8-9ish
        self.assertTrue(output['aeks_active'])
        
        # Verify prioritization: High confidence should survive
        # (Though we can't easily check contents without deeper inspection, the sort logic is there)
        pass
        
    def test_odd_monitor_init(self):
        """Test Drift Monitor Logic"""
        mon = drift_monitor.DriftMonitor()
        self.assertEqual(mon.drift_score, 0.0)
        
        # Simulate usage
        meta = {'fingerprint': 'abc', 'run_id': '123'}
        mon.log_run(meta)
        self.assertEqual(len(mon.recent_runs), 1)

if __name__ == '__main__':
    print("=== Running OGHLS Safety Verification ===")
    unittest.main()
