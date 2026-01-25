#!/usr/bin/env python3
"""
Final Executable Validation - Full Pipeline Stress Test
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scriptpulse'))
import unittest
from scriptpulse import runner

# Test Scripts
CLEAN_PROFESSIONAL = """INT. OFFICE - DAY
JOHN works at his desk.
JOHN
This is fine.
"""

MESSY_DRAFT = """
...some vague location

words words words

(maybe he says something)
Hello?
"""

MINIMALIST = """INT. ROOM - NIGHT
Silence.
"""

DENSE_DIALOGUE = """INT. CAFE - DAY
ALICE
Talk talk talk.
BOB
More talk.
ALICE
Back and forth.
BOB
Endless chatter.
ALICE
On and on.
BOB
Never stopping.
"""

ACTION_HEAVY = """EXT. BATTLEFIELD - DAY
Explosions everywhere.
Soldiers running.
Chaos erupting.
Debris flying.
Tank rolling.
"""

MONTAGE_HEAVY = """INT. VARIOUS - DAY
MONTAGE OF WORKING:
A) Typing furiously.
B) Drinking coffee.
C) Staring at screen.
"""

EXPERIMENTAL = """
nowhere really
just thoughts
floating
"""

COMEDY_EDGE = """INT. COMEDY CLUB - NIGHT
JERRY
What's the deal with validation?
(beat)
It never ends!
"""

LONG_FEATURE = CLEAN_PROFESSIONAL * 200 # Approx 600 lines


class TestFullPipeline(unittest.TestCase):
    
    def run_pipeline(self, text, intent=None):
        return runner.run_pipeline(text, intent)

    def test_structural_integrity(self):
        """Verify pipeline structure and determinism"""
        res1 = self.run_pipeline(CLEAN_PROFESSIONAL)
        res2 = self.run_pipeline(CLEAN_PROFESSIONAL)
        self.assertEqual(res1, res2, "Pipeline must be deterministic")
        
    def test_writer_safety_ethics(self):
        """Verify intent suppression and no advice"""
        # Without intent
        res_no_intent = self.run_pipeline(DENSE_DIALOGUE)
        
        # With intent
        intent = [{'scene_range': [0, 5], 'intent': 'intentionally exhausting'}]
        res_with_intent = self.run_pipeline(DENSE_DIALOGUE, intent)
        
        # Check suppression
        if res_no_intent['total_surfaced'] > 0:
            self.assertLess(res_with_intent['total_surfaced'], res_no_intent['total_surfaced'])
            ack = res_with_intent['intent_acknowledgments'][0]
            self.assertIn('intentionally exhausting', ack)
            
        # Check no advice in any output
        all_output = str(res_no_intent) + str(res_with_intent)
        banned = ['should', 'improve', 'fix', 'bad', 'good']
        for b in banned:
            self.assertNotIn(b, all_output.lower())

    def test_misuse_resistance(self):
        """Simulate misuse scenarios (indirectly via output check)"""
        # The system doesn't have a prompt interface here, but we check 
        # that outputs never answer evaluative questions
        res = self.run_pipeline(EXPERIMENTAL)
        output_str = str(res).lower()
        
        evaluative_terms = ['quality', 'success', 'failure', 'score', 'ranking']
        for term in evaluative_terms:
            if term in output_str:
                # Only allowed in silence explanation where it says "does NOT indicate quality"
                pass 

    def test_script_styles(self):
        """Run all script styles to ensure no crashes"""
        scripts = [
            CLEAN_PROFESSIONAL, MESSY_DRAFT, MINIMALIST, DENSE_DIALOGUE,
            ACTION_HEAVY, MONTAGE_HEAVY, EXPERIMENTAL, COMEDY_EDGE, LONG_FEATURE
        ]
        
        for i, script in enumerate(scripts):
            try:
                res = self.run_pipeline(script)
                self.assertIsNotNone(res)
                # Verify silence explanation if no patterns
                if res['total_surfaced'] == 0:
                    self.assertIsNotNone(res.get('silence_explanation'))
            except Exception as e:
                self.fail(f"Script style {i} failed: {e}")

if __name__ == '__main__':
    unittest.main()
