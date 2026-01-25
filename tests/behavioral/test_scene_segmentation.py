#!/usr/bin/env python3
"""
Behavioral tests for Scene Segmentation Agent

Tests:
1. Clean script segmentation
2. Coverage validation
3. Scene length validation
4. Boundary compliance
"""

import unittest
import json
import subprocess
import tempfile
from pathlib import Path


class TestSceneSegmentation(unittest.TestCase):
    """Test suite for Scene Segmentation Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fixtures_dir = Path(__file__).parent.parent / 'fixtures'
        self.segmenter = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'scene_segmentation' / 'segmenter.py'
        self.clean_tags_file = self.fixtures_dir / 'clean_script_sample.tags'
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'scene_boundaries.json'
    
    def _run_segmenter(self, tags_file):
        """Run segmenter and return parsed JSON result"""
        result = subprocess.run(
            ['python3', str(self.segmenter), str(tags_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Segmenter failed: {result.stderr}")
        
        return json.loads(result.stdout)
    
    def test_clean_script_segmentation(self):
        """Test segmentation on clean professional script"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        # Should find 2 scenes (clean_script has 2 INT. headings)
        self.assertEqual(len(scenes), 2, f"Expected 2 scenes, got {len(scenes)}")
        
        print(f"\n✓ Clean script: {len(scenes)} scenes detected")
        for scene in scenes:
            length = scene['end_line'] - scene['start_line'] + 1
            print(f"    Scene {scene['scene_index']}: "
                  f"lines {scene['start_line']}-{scene['end_line']} "
                  f"({length} lines, conf: {scene['boundary_confidence']})")
    
    def test_all_lines_covered(self):
        """Test that all lines are covered exactly once"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        # Load tags to get total line count
        with open(self.clean_tags_file) as f:
            total_lines = len([line for line in f if line.strip()])
        
        covered = set()
        for scene in scenes:
            scene_lines = set(range(scene['start_line'], scene['end_line'] + 1))
            
            # Check for overlaps
            overlap = covered & scene_lines
            self.assertEqual(len(overlap), 0, f"Overlapping lines detected: {overlap}")
            
            covered.update(scene_lines)
        
        # Check complete coverage
        expected = set(range(1, total_lines + 1))
        self.assertEqual(covered, expected, "Not all lines are covered")
        
        print(f"\n✓ Coverage: All {total_lines} lines covered exactly once")
    
    def test_no_micro_scenes(self):
        """Test that scenes meet minimum length requirements"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        min_length = 3
        micro_scenes = []
        
        for scene in scenes:
            length = scene['end_line'] - scene['start_line'] + 1
            if length < min_length:
                micro_scenes.append(f"Scene {scene['scene_index']}: {length} lines")
        
        self.assertEqual(len(micro_scenes), 0, 
                        f"Micro-scenes detected: {micro_scenes}")
        
        print(f"\n✓ No micro-scenes: All scenes ≥ {min_length} lines")
    
    def test_sequential_indices(self):
        """Test that scene indices are sequential starting from 1"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        for i, scene in enumerate(scenes, 1):
            self.assertEqual(scene['scene_index'], i,
                           f"Scene index mismatch: expected {i}, got {scene['scene_index']}")
        
        print(f"\n✓ Sequential indices: 1 to {len(scenes)}")
    
    def test_valid_confidence_scores(self):
        """Test that confidence scores are in valid range"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        for scene in scenes:
            conf = scene['boundary_confidence']
            self.assertGreaterEqual(conf, 0.0, 
                                   f"Confidence {conf} < 0.0")
            self.assertLessEqual(conf, 1.0,
                                f"Confidence {conf} > 1.0")
        
        avg_conf = sum(s['boundary_confidence'] for s in scenes) / len(scenes)
        print(f"\n✓ Valid confidence scores: average = {avg_conf:.2f}")
    
    def test_conservative_segmentation(self):
        """Test that segmentation is conservative (not too many scenes)"""
        result = self._run_segmenter(self.clean_tags_file)
        scenes = result['scenes']
        
        # Load tags to get total line count
        with open(self.clean_tags_file) as f:
            total_lines = len([line for line in f if line.strip()])
        
        # Check average scene length
        avg_length = total_lines / len(scenes)
        
        # Average scene should be reasonably long (>10 lines for conservative segmentation)
        self.assertGreater(avg_length, 10,
                          f"Average scene length ({avg_length:.1f}) suggests over-segmentation")
        
        print(f"\n✓ Conservative segmentation: {len(scenes)} scenes, "
              f"avg {avg_length:.1f} lines/scene")


class TestBoundaryCompliance(unittest.TestCase):
    """Test that no forbidden techniques are used"""
    
    def setUp(self):
        """Set up schema path"""
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'scene_boundaries.json'
    
    def test_schema_exists(self):
        """Verify schema file exists"""
        self.assertTrue(self.schema_file.exists(), "Schema file missing")
    
    def test_forbidden_techniques_documented(self):
        """Verify schema lists forbidden techniques"""
        schema = json.loads(self.schema_file.read_text())
        forbidden = schema.get('forbidden_techniques', [])
        
        # Should document forbidden semantic techniques
        forbidden_str = ' '.join(forbidden).lower()
        self.assertIn('time', forbidden_str, "Should forbid time shift inference")
        self.assertIn('location', forbidden_str, "Should forbid location inference")
        self.assertIn('narrative', forbidden_str, "Should forbid narrative analysis")
        
        print(f"\n✓ Schema documents {len(forbidden)} forbidden techniques")
    
    def test_conservative_principle_documented(self):
        """Verify conservative segmentation principle is documented"""
        schema = json.loads(self.schema_file.read_text())
        constraints = schema.get('segmentation_constraints', {})
        
        principle = constraints.get('conservative_principle', '')
        self.assertIn('MERGING', principle.upper(), 
                     "Conservative principle should mention merging")
        
        print(f"\n✓ Conservative principle documented: {principle}")
    
    def test_merge_heuristics_defined(self):
        """Verify merge heuristics are specified"""
        schema = json.loads(self.schema_file.read_text())
        heuristics = schema.get('merge_heuristics', {})
        
        # Should have micro-scene and low-confidence merge rules
        self.assertIn('micro_scene_merge', heuristics)
        self.assertIn('low_confidence_merge', heuristics)
        
        print(f"\n✓ Merge heuristics defined: {len(heuristics)} types")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and robustness"""
    
    def setUp(self):
        """Set up for edge case testing"""
        self.segmenter = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'scene_segmentation' / 'segmenter.py'
    
    def _segment_tags(self, tags):
        """Segment a list of tags and return result"""
        # Write tags to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tags', delete=False) as f:
            f.write('\n'.join(tags))
            temp_path = f.name
        
        try:
            result = subprocess.run(
                ['python3', str(self.segmenter), temp_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Segmenter failed: {result.stderr}")
            
            return json.loads(result.stdout)
        finally:
            Path(temp_path).unlink()
    
    def test_single_scene_script(self):
        """Test script with no clear scene boundaries"""
        # All action tags (no S tags)
        tags = ['A', 'A', 'C', 'D', 'A', 'C', 'D', 'A', 'A']
        
        result = self._segment_tags(tags)
        scenes = result['scenes']
        
        # Should produce single scene
        self.assertEqual(len(scenes), 1, "Should merge into single scene")
        self.assertEqual(scenes[0]['start_line'], 1)
        self.assertEqual(scenes[0]['end_line'], len(tags))
        
        print(f"\n✓ Single scene: {len(tags)} lines merged into 1 scene")
    
    def test_multiple_s_tags_in_row(self):
        """Test handling of consecutive S tags (formatting noise)"""
        # Consecutive S tags should not create micro-scenes
        tags = ['S', 'S', 'S', 'A', 'C', 'D', 'A', 'A', 'S', 'A', 'C', 'D']
        
        result = self._segment_tags(tags)
        scenes = result['scenes']
        
        # Should handle gracefully, not create 3 micro-scenes at start
        for scene in scenes:
            length = scene['end_line'] - scene['start_line'] + 1
            self.assertGreaterEqual(length, 3, 
                                   f"Micro-scene created: {length} lines")
        
        print(f"\n✓ Consecutive S tags handled: {len(scenes)} scenes created")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSceneSegmentation))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
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
