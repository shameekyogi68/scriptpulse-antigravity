#!/usr/bin/env python3
"""
Behavioral tests for Writer Intent & Immunity Agent
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'antigravity' / 'agents' / 'intent_immunity'))
from intent_processor import IntentProcessor, ALLOWED_INTENT_LABELS

class TestIntentImmunity(unittest.TestCase):
    
    def test_no_intent_passes_through(self):
        """Test patterns pass through when no intent declared"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [10, 25], 'confidence_band': 'high'}]
        processor = IntentProcessor([])
        result = processor.apply_intent(patterns)
        
        self.assertEqual(len(result['surfaced_patterns']), 1)
        self.assertEqual(len(result['suppressed_patterns']), 0)
        print("\n✓ No intent → patterns pass through unchanged")
    
    def test_full_coverage_suppresses(self):
        """Test full intent coverage suppresses pattern"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 40]}]
        intents = [{'scene_range': [15, 45], 'intent_label': 'intentionally_exhausting'}]
        
        processor = IntentProcessor(intents)
        result = processor.apply_intent(patterns)
        
        self.assertEqual(len(result['surfaced_patterns']), 0)
        self.assertEqual(len(result['suppressed_patterns']), 1)
        
        suppressed = result['suppressed_patterns'][0]
        self.assertEqual(suppressed['suppressed_reason'], 'writer_intent')
        self.assertTrue(suppressed['internal_analysis_preserved'])
        self.assertIn('alignment_note', suppressed)
        print("\n✓ Full coverage → pattern suppressed with alignment note")
    
    def test_alignment_note_present(self):
        """Test alignment acknowledgment is mandatory"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 40]}]
        intents = [{'scene_range': [15, 45], 'intent_label': 'intentionally_exhausting'}]
        
        processor = IntentProcessor(intents)
        result = processor.apply_intent(patterns)
        
        alignment = result['suppressed_patterns'][0]['alignment_note']
        self.assertIn('Writer marked', alignment)
        self.assertIn('aligns with declared intent', alignment)
        print("\n✓ Alignment acknowledgment present and formatted correctly")
    
    def test_analysis_preserved(self):
        """Test internal analysis is preserved in suppressed patterns"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 40], 'supporting_metrics': {'avg': 1.8}}]
        intents = [{'scene_range': [15, 45], 'intent_label': 'intentionally_exhausting'}]
        
        processor = IntentProcessor(intents)
        result = processor.apply_intent(patterns)
        
        suppressed = result['suppressed_patterns'][0]
        self.assertTrue(suppressed['internal_analysis_preserved'])
        self.assertIn('original_pattern', suppressed)
        print("\n✓ Analysis preserved in suppressed pattern")
    
    def test_invalid_label_rejected(self):
        """Test invalid intent labels are rejected"""
        with self.assertRaises(ValueError):
            IntentProcessor([{'scene_range': [10, 20], 'intent_label': 'invalid_label'}])
        print("\n✓ Invalid intent label rejected")
    
    def test_allowed_labels(self):
        """Test all allowed labels work"""
        for label in ALLOWED_INTENT_LABELS:
            processor = IntentProcessor([{'scene_range': [10, 20], 'intent_label': label}])
            self.assertIsNotNone(processor)
        print(f"\n✓ All {len(ALLOWED_INTENT_LABELS)} allowed labels validated")

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIntentImmunity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✅ ALL TESTS PASSED ({result.testsRun} tests)")
    else:
        print(f"❌ FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
    print("="*70)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
