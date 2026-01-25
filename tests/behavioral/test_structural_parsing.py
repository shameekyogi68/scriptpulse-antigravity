#!/usr/bin/env python3
"""
Behavioral tests for Structural Parsing Agent

Tests:
1. Clean script classification accuracy
2. Output format validation
3. Boundary compliance
"""

import unittest
import json
from pathlib import Path


VALID_TAGS = {'S', 'A', 'D', 'C', 'M'}


class TestStructuralParsing(unittest.TestCase):
    """Test suite for Structural Parsing Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fixtures_dir = Path(__file__).parent.parent / 'fixtures'
        self.clean_script = self.fixtures_dir / 'clean_script_sample.fountain'
        self.messy_draft = self.fixtures_dir / 'messy_draft_sample.txt'
        self.clean_tags = self.fixtures_dir / 'clean_script_sample.tags'
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'structural_tags.json'
    
    def test_fixtures_exist(self):
        """Verify test fixtures exist"""
        self.assertTrue(self.clean_script.exists(), "Clean script fixture missing")
        self.assertTrue(self.messy_draft.exists(), "Messy draft fixture missing")
        self.assertTrue(self.clean_tags.exists(), "Clean tags fixture missing")
    
    def test_valid_tag_format(self):
        """Test that tags are in valid format"""
        tags_content = self.clean_tags.read_text()
        tags = [line.strip() for line in tags_content.split('\n') if line.strip()]
        
        for tag in tags:
            self.assertIn(tag, VALID_TAGS, f"Invalid tag: {tag}")
            self.assertEqual(len(tag), 1, f"Tag must be single character: {tag}")
    
    def test_line_count_match(self):
        """Test that tag count matches input line count"""
        script_lines = self.clean_script.read_text().split('\n')
        tags = [line.strip() for line in self.clean_tags.read_text().split('\n') if line.strip()]
        
        self.assertEqual(
            len(tags),
            len(script_lines),
            f"Tag count ({len(tags)}) doesn't match script lines ({len(script_lines)})"
        )
    
    def test_no_prose_in_output(self):
        """Test that output contains no prose or explanations"""
        tags_content = self.clean_tags.read_text()
        lines = tags_content.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for single character tags only
            self.assertEqual(
                len(stripped), 
                1, 
                f"Line {i}: Multiple characters detected '{stripped}' - only single tags allowed"
            )
            
            # Check for forbidden patterns
            forbidden_patterns = ['%', '(', 'because', 'note', 'confidence']
            for pattern in forbidden_patterns:
                self.assertNotIn(
                    pattern.lower(),
                    line.lower(),
                    f"Line {i}: Forbidden pattern '{pattern}' detected"
                )
    
    def test_tag_distribution_reasonable(self):
        """Test that tag distribution is reasonable for clean script"""
        tags = [line.strip() for line in self.clean_tags.read_text().split('\n') if line.strip()]
        
        tag_counts = {tag: tags.count(tag) for tag in VALID_TAGS}
        
        # Should have at least some of each major tag type
        self.assertGreater(tag_counts['S'], 0, "Should have scene headings")
        self.assertGreater(tag_counts['A'], 0, "Should have action lines")
        self.assertGreater(tag_counts['D'], 0, "Should have dialogue")
        self.assertGreater(tag_counts['C'], 0, "Should have character names")
        
        print("\n✓ Tag distribution:")
        for tag, count in sorted(tag_counts.items()):
            if count > 0:
                percentage = (count / len(tags)) * 100
                print(f"    {tag}: {count:3d} ({percentage:5.1f}%)")
    
    def test_scene_headings_present(self):
        """Test that scene headings are correctly identified"""
        script_lines = self.clean_script.read_text().split('\n')
        tags = [line.strip() for line in self.clean_tags.read_text().split('\n') if line.strip()]
        
        # Find lines tagged as scene headings
        scene_heading_lines = [script_lines[i] for i, tag in enumerate(tags) if tag == 'S']
        
        # Verify they look like scene headings (INT./EXT., all caps, etc.)
        for line in scene_heading_lines:
            line_upper = line.upper()
            self.assertTrue(
                'INT.' in line_upper or 'EXT.' in line_upper or 'INT./EXT.' in line_upper,
                f"Scene heading '{line}' should contain INT. or EXT."
            )


class TestBoundaryCompliance(unittest.TestCase):
    """Test that no forbidden techniques are used"""
    
    def setUp(self):
        """Set up schema path"""
        self.schema_file = Path(__file__).parent.parent.parent / 'antigravity' / 'schemas' / 'structural_tags.json'
    
    def test_schema_exists(self):
        """Verify schema file exists"""
        self.assertTrue(self.schema_file.exists(), "Schema file missing")
    
    def test_no_semantic_features_in_schema(self):
        """Verify schema lists no semantic features as allowed"""
        schema = json.loads(self.schema_file.read_text())
        forbidden = schema['boundary_compliance']['forbidden_features']
        
        # Verify forbidden list includes semantic features
        semantic_keywords = ['semantic', 'sentiment', 'quality', 'relationship']
        
        for keyword in semantic_keywords:
            has_keyword = any(keyword.lower() in feat.lower() for feat in forbidden)
            self.assertTrue(
                has_keyword,
                f"Schema should forbid '{keyword}'-related features"
            )
    
    def test_allowed_features_format_only(self):
        """Verify allowed features are format-only"""
        schema = json.loads(self.schema_file.read_text())
        allowed = schema['boundary_compliance']['allowed_features']
        
        # All allowed features should be format-based
        format_keywords = ['capitalization', 'indentation', 'punctuation', 'structural']
        
        for feature in allowed:
            has_format_keyword = any(keyword.lower() in feature.lower() for keyword in format_keywords)
            self.assertTrue(
                has_format_keyword,
                f"Feature '{feature}' may not be format-only"
            )
    
    def test_validation_rules_strict(self):
        """Verify validation rules are strict"""
        schema = json.loads(self.schema_file.read_text())
        forbidden = schema['validation_rules']['forbidden']
        
        # Should forbid confidence scores and commentary
        forbidden_str = ' '.join(forbidden).lower()
        self.assertIn('confidence', forbidden_str, "Should forbid confidence scores")
        self.assertIn('comment', forbidden_str, "Should forbid commentary")


class TestMessyDraftHandling(unittest.TestCase):
    """Test robustness with messy formatting"""
    
    def setUp(self):
        """Set up messy draft fixture"""
        self.messy_draft = Path(__file__).parent.parent / 'fixtures' / 'messy_draft_sample.txt'
    
    def test_messy_draft_exists(self):
        """Test that messy draft fixture exists"""
        self.assertTrue(self.messy_draft.exists(), "Messy draft fixture missing")
    
    def test_messy_draft_has_inconsistent_formatting(self):
        """Verify messy draft has inconsistent formatting (this is the point)"""
        content = self.messy_draft.read_text()
        lines = [l for l in content.split('\n') if l.strip()]
        
        # Should have lowercase starts (inconsistent capitalization)
        has_lowercase = any(line[0].islower() for line in lines if line)
        
        # Should have mixed spacing
        has_mixed_spacing = any('  ' in line for line in lines)
        
        print("\n✓ Messy draft validation:")
        print(f"    Has inconsistent capitalization: {has_lowercase}")
        print(f"    Has mixed spacing: {has_mixed_spacing}")
        
        # At least one should be true to verify it's actually messy
        self.assertTrue(
            has_lowercase or has_mixed_spacing,
            "Messy draft should have formatting inconsistencies"
        )


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStructuralParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestMessyDraftHandling))
    
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
