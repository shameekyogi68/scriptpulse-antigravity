"""
ScriptPulse Research Smoke Test
Verifies that the v6-v8 Research Layers execute without crashing.
"""

import sys
import unittest

# Ensure we can import scriptpulse
sys.path.append('.')

from scriptpulse import runner

class TestResearchLayers(unittest.TestCase):
    
    def setUp(self):
        import textwrap
        self.script_sample = textwrap.dedent("""
        INT. LAB - DAY
        
        A SCIENTIST (30s) stares at a glowing screen.
        
        SCIENTIST
        It's working. The pulse is stable.
        
        He types furiously. Red lights flash.
        
        SCIENTIST (CONT'D)
        Wait. What is that?
        
        EXT. SPACE - NIGHT
        
        The void is silent. A star explodes.
        """).strip()
        
    def test_full_pipeline_v8(self):
        """Test the full pipeline with all research agents enabled."""
        print("\nTesting v8.0 Research Pipeline...")
        report = runner.run_pipeline(
            self.script_sample,
            lens='viewer',
            genre='sci-fi',
            audience_profile='cinephile', # v6.6
            high_res_mode=True            # v7.0
        )
        
        print("\nDEBUG REPORT METADATA:", report.get('meta'))
        if 'temporal_trace' in report:
            print("DEBUG TRACE LENGTH:", len(report['temporal_trace']))
        else:
            print("DEBUG: No temporal_trace found")
            
        # Check v6.4 (Imagery/Social)
        self.assertIn('temporal_trace', report)
        trace = report['temporal_trace']
        self.assertGreater(len(trace), 0)
        
        # Check v6.5 (Affective)
        first_point = trace[0]
        self.assertIn('affective_state', first_point)
        self.assertIn('valence_score', first_point)
        print(f"  > Affective Checking: {first_point.get('affective_state')} (Valence: {first_point.get('valence_score')})")
        
        # Check v6.6 (Cognitive/Coherence)
        self.assertIn('coherence_penalty', first_point)
        
        # Check v8.0 (Fairness)
        self.assertIn('fairness_audit', report)
        fairness = report['fairness_audit']
        self.assertIn('representation_stats', fairness)
        print("  > Fairness Audit: OK")
        
        # Check v8.0 (Suggestions)
        self.assertIn('suggestions', report)
        print("  > Suggestions: OK")
        
        # Check v9.0 (Research Hardening)
        self.assertIn('baseline_trace', report)
        self.assertIn('semantic_flux', report)
        print(f"  > Baselines: {len(report['baseline_trace'])} points")
        print(f"  > Semantic Flux: {len(report['semantic_flux'])} points")
        
        print("v8.0/v9.0 Pipeline Success.")

if __name__ == '__main__':
    unittest.main()
