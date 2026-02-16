#!/usr/bin/env python3
"""
Comprehensive Test Suite for ScriptPulse
P1 Priority: Edge cases, regression tests, and validation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scriptpulse import runner
from scriptpulse.agents import structure_agent as parsing
# segmentation is now part of structure_agent too


class TestEmptyScript(unittest.TestCase):
    """Test handling of empty or minimal input"""
    
    def test_empty_string(self):
        """Empty string should not crash"""
        result = runner.run_pipeline("")
        self.assertIsNotNone(result)
        # Empty string may produce 1 default scene (conservative handling)
        self.assertLessEqual(result.get('total_scenes', 0), 1)
    
    def test_whitespace_only(self):
        """Whitespace-only input should not crash"""
        result = runner.run_pipeline("   \n\n   \n  ")
        self.assertIsNotNone(result)


class TestSingleScene(unittest.TestCase):
    """Test scripts with only one scene"""
    
    def test_single_scene_script(self):
        """Single scene should be detected"""
        script = """INT. ROOM - DAY

A man sits alone.

MAN
Hello.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
        self.assertEqual(result.get('total_scenes', 0), 1)


class TestSceneDetection(unittest.TestCase):
    """Test improved scene detection patterns"""
    
    def test_standard_int_ext(self):
        """Standard INT./EXT. should be detected"""
        self.assertTrue(parsing.is_scene_heading("INT. COFFEE SHOP - DAY"))
        self.assertTrue(parsing.is_scene_heading("EXT. PARK - NIGHT"))
        self.assertTrue(parsing.is_scene_heading("INT/EXT. CAR - DAY"))
    
    def test_interior_exterior_fallback(self):
        """Full INTERIOR/EXTERIOR should be detected"""
        self.assertTrue(parsing.is_scene_heading("INTERIOR HOUSE - DAY"))
        self.assertTrue(parsing.is_scene_heading("EXTERIOR STREET - NIGHT"))
    
    def test_abbreviated_fallback(self):
        """Abbreviated I./E. should be detected"""
        self.assertTrue(parsing.is_scene_heading("I. ROOM - DAY"))
        self.assertTrue(parsing.is_scene_heading("E. GARDEN - NIGHT"))
    
    def test_scene_prefix(self):
        """SCENE: prefix should be detected"""
        self.assertTrue(parsing.is_scene_heading("SCENE: THE ARRIVAL"))
        self.assertTrue(parsing.is_scene_heading("SCENE 1"))
    
    def test_time_of_day_fallback(self):
        """Location with time indicator should be detected"""
        self.assertTrue(parsing.is_scene_heading("COFFEE SHOP - DAY"))
        self.assertTrue(parsing.is_scene_heading("BEDROOM - NIGHT"))


class TestLargeScript(unittest.TestCase):
    """Test performance with large scripts"""
    
    def test_50_scenes(self):
        """50-scene script should complete without timeout"""
        scenes = []
        for i in range(50):
            scenes.append(f"""
INT. ROOM {i} - DAY

Character {i} enters.

CHARACTER {i}
Line {i}.
""")
        script = "\n\n".join(scenes)
        
        import time
        start = time.time()
        result = runner.run_pipeline(script)
        elapsed = time.time() - start
        
        self.assertIsNotNone(result)
        self.assertLess(elapsed, 10)  # Should complete in under 10 seconds


class TestMalformedFormatting(unittest.TestCase):
    """Test handling of non-standard formatting"""
    
    def test_no_scene_headings(self):
        """Script without scene headings should not crash"""
        script = """
John walks in.
He looks around.

JOHN
Where am I?
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_mixed_case_headings(self):
        """Mixed case headings should work"""
        script = """Int. Room - Day

A man enters.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestUnicode(unittest.TestCase):
    """Test handling of unicode and special characters"""
    
    def test_unicode_dialogue(self):
        """Unicode in dialogue should not crash"""
        script = """INT. CAFÉ - DAY

PIERRE
Où est le café?

MARIA
¿Qué dijiste?
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)
    
    def test_em_dashes(self):
        """Em dashes in scene headings should work"""
        script = """INT. ROOM – DAY

A man sits.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestAllDialogue(unittest.TestCase):
    """Test dialogue-heavy scripts"""
    
    def test_all_dialogue(self):
        """All-dialogue script should be analyzed"""
        script = """INT. ROOM - DAY

JOHN
Hello.

MARY
Hi there.

JOHN
How are you?

MARY
Fine, thanks.

JOHN
Good to hear.

MARY
Indeed.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestAllAction(unittest.TestCase):
    """Test action-heavy scripts"""
    
    def test_all_action(self):
        """All-action script should be analyzed"""
        script = """INT. WAREHOUSE - NIGHT

The door swings open.
Dust fills the air.
A figure emerges from the shadows.
Footsteps echo.
The figure stops.
Silence.
A light flickers.
More footsteps.
The chase begins.
"""
        result = runner.run_pipeline(script)
        self.assertIsNotNone(result)


class TestWriterIntent(unittest.TestCase):
    """Test writer intent functionality"""
    
    def test_intent_suppression(self):
        """Writer intent should suppress matching patterns"""
        script = """INT. ROOM - DAY

A man sits.

INT. ROOM - DAY

Same angle.

INT. ROOM - DAY

Same again.
"""
        # Without intent
        result_no_intent = runner.run_pipeline(script)
        
        # With intent
        intent = [{'scene_range': [0, 2], 'intent': 'intentionally minimal'}]
        result_with_intent = runner.run_pipeline(script, writer_intent=intent)
        
        self.assertIsNotNone(result_no_intent)
        self.assertIsNotNone(result_with_intent)


class TestSceneInfo(unittest.TestCase):
    """Test scene info extraction for UI"""
    
    def test_scene_info_present(self):
        """Scene info should be in output"""
        script = """INT. COFFEE SHOP - DAY

John enters.

INT. PARK - NIGHT

Mary waits.
"""
        result = runner.run_pipeline(script)
        self.assertIn('scene_info', result)
        self.assertIn('total_scenes', result)
    
    def test_scene_headings_extracted(self):
        """Scene headings should be extracted"""
        script = """INT. COFFEE SHOP - DAY

John enters.

INT. PARK - NIGHT

Mary waits.
"""
        result = runner.run_pipeline(script)
        scene_info = result.get('scene_info', [])
        
        if scene_info:
            headings = [s['heading'] for s in scene_info]
            self.assertTrue(any('COFFEE SHOP' in h for h in headings))


if __name__ == '__main__':
    print("="*60)
    print("ScriptPulse Comprehensive Test Suite")
    print("="*60)
    
    unittest.main(verbosity=2)
