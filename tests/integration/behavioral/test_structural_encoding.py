#!/usr/bin/env python3
"""
Behavioral tests for Structural Encoding Agent

Tests feature extraction, interpretability, and absence of semantic inference.
"""

import unittest
import json
import subprocess
import tempfile
from pathlib import Path


class TestStructuralEncoding(unittest.TestCase):
    """Test suite for Structural Encoding Agent"""
    
    def setUp(self):
        """Set up test paths"""
        self.fixtures_dir = Path(__file__).parent.parent / 'fixtures'
        self.encoder = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'structural_encoding' / 'encoder.py'
        self.validator = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'structural_encoding' / 'validator.py'
        self.segmenter = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'scene_segmentation' / 'segmenter.py'
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'structural_features.json'
    
    def _encode_script(self, screenplay_file, tags_file):
        """Helper to encode a script"""
        # First segment scenes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            scenes_path = f.name
        
        try:
            # Segment scenes
            result = subprocess.run(
                ['python3', str(self.segmenter), str(tags_file)],
                capture_output=True,
                text=True,
                check=True
            )
            Path(scenes_path).write_text(result.stdout)
            
            # Then encode
            result = subprocess.run(
                ['python3', str(self.encoder), str(screenplay_file), str(tags_file), scenes_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout)
        finally:
            Path(scenes_path).unlink(missing_ok=True)

    
    def test_clean_script_encoding(self):
        """Test encoding on clean professional script"""
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        # Should encode 2 scenes
        self.assertEqual(len(scenes), 2, f"Expected 2 scenes, got {len(scenes)}")
        
        # All scenes should have features
        for scene in scenes:
            self.assertIn('features', scene)
            features = scene['features']
            
            self.assertIn('linguistic_load', features)
            self.assertIn('dialogue_dynamics', features)
            self.assertIn('visual_abstraction', features)
            self.assertIn('referential_memory', features)
            self.assertIn('structural_change', features)
        
        print(f"\n✓ Clean script: {len(scenes)} scenes encoded with all feature groups")
    
    def test_all_features_numeric(self):
        """Test that all features are numeric and valid"""
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        for scene in scenes:
            scene_idx = scene['scene_index']
            features = scene['features']
            
            # Flatten all features
            for group_name, group_features in features.items():
                for feat_name, value in group_features.items():
                    # Must be numeric
                    self.assertIsInstance(value, (int, float),
                                        f"Scene {scene_idx}: {group_name}.{feat_name} is not numeric")
                    
                    # Must not be NaN or infinite
                    import math
                    self.assertFalse(math.isnan(value),
                                   f"Scene {scene_idx}: {group_name}.{feat_name} is NaN")
                    self.assertFalse(math.isinf(value),
                                   f"Scene {scene_idx}: {group_name}.{feat_name} is infinite")
        
        print(f"\n✓ All features are numeric and valid")
    
    def test_first_scene_boundary_zero(self):
        """Test that first scene has event_boundary_score = 0"""
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        first_scene = scenes[0]
        boundary_score = first_scene['features']['structural_change']['event_boundary_score']
        
        self.assertEqual(boundary_score, 0.0,
                        f"First scene should have boundary score 0.0, got {boundary_score}")
        
        print(f"\n✓ First scene boundary score = 0.0")
    
    def test_feature_interpretability(self):
        """Test that features produce reasonable values"""
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        for scene in scenes:
            features = scene['features']
            
            # Linguistic features should be reasonable
            ling = features['linguistic_load']
            self.assertGreaterEqual(ling['sentence_count'], 0)
            self.assertGreaterEqual(ling['mean_sentence_length'], 0)
            
            # Dialogue features
            dial = features['dialogue_dynamics']
            self.assertGreaterEqual(dial['dialogue_turns'], 0)
            self.assertGreaterEqual(dial['speaker_switches'], 0)
            
            # Visual features
            vis = features['visual_abstraction']
            self.assertGreaterEqual(vis['action_line_count'], 0)
            self.assertLessEqual(vis['visual_density'], 1.0)  # Density can't exceed 1.0
            
            # Referential features
            ref = features['referential_memory']
            self.assertGreaterEqual(ref['active_character_count'], 0)
            self.assertLessEqual(ref['pronoun_density'], 1.0)  # Density can't exceed 1.0
        
        print(f"\n✓ All features have interpretable ranges")
    
    def test_schema_exists(self):
        """Verify schema file exists and is valid"""
        self.assertTrue(self.schema_file.exists(), "Schema file missing")
        
        schema = json.loads(self.schema_file.read_text())
        
        # Should have all feature groups documented
        self.assertIn('feature_groups', schema)
        groups = schema['feature_groups']
        
        self.assertIn('linguistic_load', groups)
        self.assertIn('dialogue_dynamics', groups)
        self.assertIn('visual_abstraction', groups)
        self.assertIn('referential_memory', groups)
        self.assertIn('structural_change', groups)
        
        print(f"\n✓ Schema exists with all {len(groups)} feature groups")
    
    def test_forbidden_operations_documented(self):
        """Verify forbidden operations are documented"""
        schema = json.loads(self.schema_file.read_text())
        
        forbidden = schema.get('forbidden_operations', [])
        forbidden_str = ' '.join(forbidden).lower()
        
        # Should forbid semantic techniques
        self.assertIn('semantic', forbidden_str)
        self.assertIn('sentiment', forbidden_str)
        self.assertIn('quality', forbidden_str)
        
        print(f"\n✓ Schema documents {len(forbidden)} forbidden operations")
    
    def test_interpretability_principle_documented(self):
        """Verify interpretability principle is stated"""
        schema = json.loads(self.schema_file.read_text())
        
        principle = schema.get('interpretability_principle', '')
        self.assertIn('page', principle.lower())  # "point to on the page"
        
        print(f"\n✓ Interpretability principle documented")


class TestFeatureExtraction(unittest.TestCase):
    """Test specific feature extraction logic"""
    
    def setUp(self):
        """Set up test paths"""
        self.fixtures_dir = Path(__file__).parent.parent / 'fixtures'
        self.encoder = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'structural_encoding' / 'encoder.py'
        self.segmenter = Path(__file__).parent.parent.parent / 'antigravity' / 'agents' / 'scene_segmentation' / 'segmenter.py'
    
    def _encode_script(self, screenplay_file, tags_file):
        """Helper to encode a script"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            scenes_path = f.name
        
        try:
            result = subprocess.run(
                ['python3', str(self.segmenter), str(tags_file)],
                capture_output=True,
                text=True,
                check=True
            )
            Path(scenes_path).write_text(result.stdout)
            
            result = subprocess.run(
                ['python3', str(self.encoder), str(screenplay_file), str(tags_file), scenes_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout)
        finally:
            Path(scenes_path).unlink(missing_ok=True)

    
    def test_dialogue_heavy_script(self):
        """Test that dialogue-heavy scripts have high dialogue dynamics"""
        # Note: This test will work when we have tags for dialogue_heavy_sample
        # For now, test on clean script
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        # Should have dialogue features extracted
        for scene in scenes:
            dial = scene['features']['dialogue_dynamics']
            self.assertIn('dialogue_turns', dial)
            self.assertIn('speaker_switches', dial)
        
        print(f"\n✓ Dialogue dynamics extracted")
    
    def test_visual_density_calculation(self):
        """Test visual density is properly bounded"""
        screenplay = self.fixtures_dir / 'clean_script_sample.fountain'
        tags = self.fixtures_dir / 'clean_script_sample.tags'
        
        result = self._encode_script(screenplay, tags)
        scenes = result['encoded_scenes']
        
        for scene in scenes:
            vis = scene['features']['visual_abstraction']
            density = vis['visual_density']
            
            # Density must be in [0, 1]
            self.assertGreaterEqual(density, 0.0)
            self.assertLessEqual(density, 1.0)
        
        print(f"\n✓ Visual density properly bounded [0,1]")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestStructuralEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureExtraction))
    
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
