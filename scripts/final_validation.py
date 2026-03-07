#!/usr/bin/env python3
"""
Final Functional Validation - full pipeline sanity check for v15.0 Gold
"""

import sys
import os
import unittest

# Ensure project root is in path
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scriptpulse.pipeline import runner

# Sample script for testing
TEST_SCRIPT = """INT. COFFEE SHOP - DAY
ALICE (20s) sits alone, staring at a coffee cup.
BOB (30s) enters, looking frantic.
BOB
We have to leave. Now.
ALICE
Why? What happened?
BOB
They found the prototype.
"""

class TestPipeline(unittest.TestCase):
    
    def test_pipeline_run(self):
        """Verify the pipeline completes without error and returns expected keys."""
        report = runner.run_pipeline(TEST_SCRIPT, genre='Thriller')
        
        # Verify structure
        self.assertIn('temporal_trace', report)
        self.assertIn('writer_intelligence', report)
        self.assertIn('meta', report)
        
        # Verify metadata
        self.assertEqual(report['meta']['genre'], 'Thriller')
        
        # Verify dynamics
        trace = report['temporal_trace']
        self.assertGreater(len(trace), 0)
        self.assertIn('attentional_signal', trace[0])
        
        # Verify writer intelligence
        wi = report['writer_intelligence']
        self.assertIn('narrative_diagnosis', wi)
        self.assertIn('rewrite_priorities', wi)
        
    def test_genre_sensitivity(self):
        """Verify the engine responds differently to different genre priors."""
        rep_thriller = runner.run_pipeline(TEST_SCRIPT, genre='Thriller')
        rep_drama = runner.run_pipeline(TEST_SCRIPT, genre='Drama')
        
        # The signals should differ based on lambda/beta priors
        sig_thriller = rep_thriller['temporal_trace'][0]['attentional_signal']
        sig_drama = rep_drama['temporal_trace'][0]['attentional_signal']
        
        # For a short script, they might be close, but let's check execution time or data keys
        self.assertNotEqual(str(rep_thriller['temporal_trace']), str(rep_drama['temporal_trace']))

if __name__ == '__main__':
    unittest.main()
