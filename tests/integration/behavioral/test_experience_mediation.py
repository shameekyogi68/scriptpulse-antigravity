#!/usr/bin/env python3
"""
Behavioral tests for Audience-Experience Mediation Agent
"""

import unittest
import json
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'antigravity' / 'agents' / 'experience_mediation'))
from mediator import ExperienceMediator, validate_no_forbidden_language, FORBIDDEN_WORDS

class TestExperienceMediation(unittest.TestCase):
    
    def test_patterns_translated(self):
        """Test patterns are translated to experiential language"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 35], 'confidence_band': 'high'}]
        
        mediator = ExperienceMediator()
        result = mediator.mediate(patterns, [])
        
        self.assertEqual(len(result['reflections']), 1)
        ref = result['reflections'][0]
        self.assertIn('audience', ref['experience'].lower())
        print("\n✓ Pattern translated to experiential language")
    
    def test_question_framing(self):
        """Test all reflections have question framing"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 35], 'confidence_band': 'high'}]
        
        mediator = ExperienceMediator()
        result = mediator.mediate(patterns, [])
        
        for ref in result['reflections']:
            self.assertTrue(ref['question'].endswith('?'))
        print("\n✓ Question-first framing present")
    
    def test_uncertainty_markers(self):
        """Test uncertainty markers are present"""
        patterns = [
            {'pattern_type': 'sustained_demand', 'scene_range': [10, 20], 'confidence_band': 'high'},
            {'pattern_type': 'limited_recovery', 'scene_range': [30, 40], 'confidence_band': 'medium'},
        ]
        
        mediator = ExperienceMediator()
        result = mediator.mediate(patterns, [])
        
        for ref in result['reflections']:
            self.assertIn(ref['uncertainty'], ['may', 'might', 'could'])
        print("\n✓ Uncertainty markers present")
    
    def test_silence_explanation(self):
        """Test silence explanation when no patterns"""
        mediator = ExperienceMediator()
        result = mediator.mediate([], [])
        
        self.assertEqual(len(result['reflections']), 0)
        self.assertIsNotNone(result['silence_explanation'])
        self.assertNotIn('good', result['silence_explanation'].lower())
        print(f"\n✓ Silence explanation: '{result['silence_explanation'][:40]}...'")
    
    def test_intent_acknowledgment(self):
        """Test intent acknowledgment for suppressed patterns"""
        suppressed = [{
            'pattern_type': 'sustained_demand',
            'scene_range': [20, 40],
            'suppressed_reason': 'writer_intent',
            'intent_reference': {
                'label': 'intentionally_exhausting',
                'scene_range': [15, 45]
            }
        }]
        
        mediator = ExperienceMediator()
        result = mediator.mediate([], suppressed)
        
        self.assertEqual(len(result['intent_acknowledgments']), 1)
        ack = result['intent_acknowledgments'][0]
        self.assertIn('consistent with that intent', ack['acknowledgment'])
        print("\n✓ Intent acknowledgment present")
    
    def test_no_forbidden_language(self):
        """Test no forbidden language in output"""
        patterns = [{'pattern_type': 'sustained_demand', 'scene_range': [20, 35], 'confidence_band': 'high'}]
        
        mediator = ExperienceMediator()
        result = mediator.mediate(patterns, [])
        
        self.assertTrue(validate_no_forbidden_language(result))
        print(f"\n✓ No forbidden language (checked {len(FORBIDDEN_WORDS)} terms)")

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExperienceMediation)
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
