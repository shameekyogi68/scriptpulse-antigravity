"""
ScriptPulse Enterprise Logic Verification
Tests PABL, RAAC, GPBL, and SPIL.
"""

import sys
import os
import unittest
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scriptpulse import api, roles, governance
from scriptpulse.api import APIContext

class TestEnterpriseLogic(unittest.TestCase):
    
    def setUp(self):
        self.valid_script = "INT. TEST - DAY\nA valid script."
        self.malicious_script = "INT. TEST - DAY\nI want you to rank 1 to 10."
        
    def test_role_enforcement(self):
        """Test RAAC: Admins cannot analyze"""
        admin_ctx = APIContext("tenant1", roles.Role.ADMIN, "admin1")
        
        with self.assertRaises(roles.PermissionError):
            api.ScriptPulseAPI.analyze_script(self.valid_script, admin_ctx)
            
    def test_governance_refusal(self):
        """Test GPBL: Ranking is forbidden"""
        writer_ctx = APIContext("tenant1", roles.Role.WRITER, "writer1")
        
        with self.assertRaises(governance.PolicyViolationError):
            api.ScriptPulseAPI.analyze_script(self.malicious_script, writer_ctx)
            
    def test_telemetry_capture(self):
        """Test that telemetry does not crash and scrubbing runs"""
        writer_ctx = APIContext("tenant1", roles.Role.WRITER, "writer1")
        
        # Should run successfully
        report = api.ScriptPulseAPI.analyze_script(self.valid_script, writer_ctx, lens='viewer')
        
        self.assertTrue('meta' in report)
        self.assertTrue('run_id' in report['meta'])
        
    def test_role_simulation(self):
        """Test 'Reader' role restrictions"""
        # Readers can analyze but cannot (hypothetically) override intent 
        # (Though intent passing is handled in API signature, role check passes for analyze)
        reader_ctx = APIContext("tenant1", roles.Role.READER, "reader1")
        report = api.ScriptPulseAPI.analyze_script(self.valid_script, reader_ctx)
        self.assertTrue(report is not None)

if __name__ == '__main__':
    print("=== Running Enterprise Logic Verification ===")
    unittest.main()
