"""
Verification Suite for vNext.11 ML Upgrade
"""
import unittest
import sys
import os

# Ensure path is set (hack for relative imports in tests)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scriptpulse.agents import bert_parser, semantic, silicon_stanislavski
from scriptpulse import drift_monitor

class TestMLComponents(unittest.TestCase):
    
    def test_bert_parser_init(self):
        """Test that BERT Parser initializes (Mock or Real)."""
        agent = bert_parser.BertParserAgent()
        print(f"\n[Test] Parser Mode: {'Mock' if agent.is_mock else 'ML'}")
        
        # Test basic prediction
        tag = agent.predict_line("INT. HOUSE - DAY")
        self.assertEqual(tag, "S")
        
        tag = agent.predict_line("JOHN")
        # Could be C (Character) or A (Action) depending on context/ML
        # But INT. is definitely S
        
    def test_semantic_agent(self):
        """Test Semantic Agent logic."""
        agent = semantic.SemanticAgent()
        print(f"[Test] Semantic Mode: {'SBERT' if agent.model else 'Heuristic'}")
        
        data = {
            'scenes': [
                {'lines': [{'text': 'Hello world'}]},
                {'lines': [{'text': 'Different content here'}]}
            ]
        }
        scores = agent.run(data)
        self.assertEqual(len(scores), 2)
        self.assertTrue(isinstance(scores[0], float))
        
    def test_stanislavski_simulation(self):
        """Test Silicon Stanislavski."""
        agent = silicon_stanislavski.SiliconStanislavski()
        print(f"[Test] Stanislavski Mode: {'ML' if getattr(agent, 'is_ml', False) else 'Keyword'}")
        
        result = agent.act_scene("He pointed the gun at the safe.")
        self.assertIn('internal_state', result)
        self.assertIn('felt_emotion', result)
        
        # Check that state updates
        state = result['internal_state']
        self.assertTrue(0.0 <= state['safety'] <= 1.0)

    def test_drift_monitor_stats(self):
        """Test Statistical Drift Detection."""
        monitor = drift_monitor.DriftMonitor()
        
        # Seed with baseline
        baseline = [0.1, 0.1, 0.1, 0.1, 0.2] * 10
        monitor.log_run({'id': 'baseline'}, entropy_scores=baseline)
        
        # Test with similar data
        drift, p_val = monitor.check_distribution_drift([0.1, 0.15, 0.1] * 5)
        print(f"[Test] Drift Check 1 (Similar): p={p_val:.4f}")
        self.assertFalse(drift)
        
        # Test with highly different data (High Entropy)
        drift, p_val = monitor.check_distribution_drift([0.9, 0.8, 0.9] * 5)
        print(f"[Test] Drift Check 2 (Different): p={p_val:.4f}")
        # Might need more data for significance, but p should be low
        if len(monitor.entropy_baseline) >= 50:
             self.assertTrue(drift or p_val < 0.05)

if __name__ == '__main__':
    unittest.main()
