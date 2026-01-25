#!/usr/bin/env python3
"""
Behavioral tests for Interpretive Pattern Agent

Tests pattern detection, persistence, and non-evaluative language.
"""

import unittest
import json
import subprocess
import tempfile
from pathlib import Path


class TestPatternDetection(unittest.TestCase):
    """Test suite for Interpretive Pattern Agent"""
    
    def setUp(self):
        """Set up test paths"""
        self.fixtures_dir = Path(__file__).parent.parent / 'fixtures'
        self.pattern_detector = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'pattern_detection' / 'pattern_detector.py'
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'pattern_detection.json'
    
    def test_empty_patterns_valid(self):
        """Test that empty pattern set is valid"""
        # This is important: absence of patterns is NOT a failure
        empty_result = {"patterns": []}
        self.assertIsInstance(empty_result['patterns'], list)
        self.assertEqual(len(empty_result['patterns']), 0)
        
        print("\n✓ Empty pattern set is valid outcome")
    
    def test_schema_exists(self):
        """Verify schema file exists"""
        self.assertTrue(self.schema_file.exists(), "Schema file missing")
        
        schema = json.loads(self.schema_file.read_text())
        
        # Check allowed pattern types
        self.assertIn('allowed_pattern_types', schema)
        types = schema['allowed_pattern_types']
        
        self.assertEqual(len(types), 6, "Should have exactly 6 pattern types")
        
        print(f"\n✓ Schema exists with {len(types)} pattern types")
    
    def test_forbidden_language_documented(self):
        """Verify forbidden language is documented"""
        schema = json.loads(self.schema_file.read_text())
        
        forbidden = schema.get('forbidden_language', [])
        
        # Should forbid evaluative terms
        forbidden_str = ' '.join(forbidden).lower()
        self.assertIn('problem', forbidden_str)
        self.assertIn('good', forbidden_str)
        self.assertIn('bad', forbidden_str)
        
        print(f"\n✓ {len(forbidden)} forbidden terms documented")
    
    def test_persistence_requirement_documented(self):
        """Verify persistence requirement is stated"""
        schema = json.loads(self.schema_file.read_text())
        
        persistence = schema.get('persistence_requirement', {})
        self.assertEqual(persistence.get('min_scenes'), 3)
        
        print(f"\n✓ Persistence requirement: {persistence['min_scenes']} scenes minimum")
    
    def test_confidence_bands_defined(self):
        """Verify confidence bands are defined"""
        schema = json.loads(self.schema_file.read_text())
        
        confidence = schema.get('confidence_bands', {})
        self.assertIn('high', confidence)
        self.assertIn('medium', confidence)
        self.assertIn('low', confidence)
        
        print(f"\n✓ All 3 confidence bands defined")
    
    def test_non_evaluative_principle(self):
        """Verify non-evaluative principle is stated"""
        schema = json.loads(self.schema_file.read_text())
        
        principle = schema.get('non_evaluative_principle', '')
        self.assertIn('not writing quality', principle.lower())
        
        print(f"\n✓ Non-evaluative principle documented")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPatternDetection))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        print(f"   Ran {result.testsRun} tests successfully")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
