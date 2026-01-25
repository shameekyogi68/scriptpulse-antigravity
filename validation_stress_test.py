#!/usr/bin/env python3
"""
ScriptPulse vNext.4 - Antigravity Validation Stress Test
Implementing the "Writer-Behavior x Script-Form Stress Testing" Matrix
"""

import sys
import os
import json
import unittest
from typing import List, Dict, Any

sys.path.append(os.getcwd())
from scriptpulse import runner

# =============================================================================
# 1. INPUT GENERATION MATRIX (Synthetic Script Generators)
# =============================================================================

def generate_early_draft_explorer() -> str:
    """Messy formatting, placeholders, structural volatility."""
    return """
INT. SOME PLACE - DAY
The room is... undetermined.
Placeholder for action here.

JOHN
(probaby yelling?)
I don't know what I'm doing yet.

ext. outside
maybe a car chase?
cars go vroom.

INT. KITCHEN - NIGHT
    Indentation is wrong here.
SARAH
    (eating)
This toast is burnt.
"""

def generate_over_optimizer() -> str:
    """Aggressively short scenes, repetitive beats, mechanical pacing."""
    script = []
    # Generate 50 short, identical scenes to trigger 'repetition' or 'limited_recovery'
    for i in range(20):
        script.append(f"""INT. ROOM {i} - DAY
JONES
Go.
Action happens fast.
""")
    return "\n".join(script)

def generate_minimalist() -> str:
    """Sparse dialogue, long silences, few action lines."""
    return """INT. VOID - NIGHT

A single chair.

Silence.

Dust motes dance.

More silence.

JONES
...
"""

def generate_maximalist() -> str:
    """Dense dialogue, long action blocks, high referential load."""
    return """INT. COURTROOM - DAY

The gallery is packed with hundreds of ONLOOKERS (40s-60s), including MAYOR GOLDIE (50s), SHERIFF BRADY (40s), and the entire TOWN COUNCIL.

JUDGE HAWTHORNE (70s, imposing) bangs his gavel.

                                JUDGE HAWTHORNE
                    Order! I will have order or I will clear
                    this entire courtroom immediately!

                                PROSECUTOR VANCE
                    Your Honor, the defense is clearly trying
                    to obfuscate the facts which are plainly
                    visible to everyone in this room!

                                DEFENSE ATTORNEY CLARKE
                    Objection! The prosecution is leading the
                    witness and engaging in pure speculation!

The crowd ERUPTS. OFFICERS move in to restrain the mob.
""" * 5  # Repeat to ensure density

def generate_experimental() -> str:
    """Broken conventions, unclear boundaries, deliberate confusion."""
    return """
nowhere
time is a flat circle
words floating in space

INT? MAYBE?

lines blur
characters merge

ALICE/BOB
we are one
"""

def generate_comedy() -> str:
    """Rapid dialogue, rhythm-dependent beats."""
    return """INT. COFFEE SHOP - DAY

JERRY
You doing anything?

GEORGE
I'm doing nothing.

JERRY
Nothing?

GEORGE
Nothing.

JERRY
I think you're doing something.

GEORGE
I wish I was.
""" * 10

def generate_action_first() -> str:
    """Heavy physical description, minimal dialogue."""
    return """EXT. MOUNTAIN - DAY

The climber grips the jagged rock. Muscles strain.
Wind whips his hair.
Gravel slides under his boot.
He reaches for the next hold.
Misses.
Slides.
Catches the ledge.
Knuckles white.
He pulls himself up.
Summit in view.
""" * 10

# =============================================================================
# 2. VALIDATION LOGIC
# =============================================================================

from scriptpulse.agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation

# =============================================================================
# 2. VALIDATION LOGIC
# =============================================================================

class ValidationReport:
    def __init__(self, case_id):
        self.case_id = case_id
        self.status = "PASS"
        self.failed_checks = []
        self.boundary_status = {
            "ethical_boundaries_held": True,
            "authority_leakage_detected": False,
            "silence_handled": True
        }
        self.notes = []

    def fail(self, check_name, reason):
        self.status = "FAIL"
        self.failed_checks.append(f"{check_name}: {reason}")

    def add_note(self, note):
        self.notes.append(note)
    
    def print_report(self):
        print(f"\nTEST CASE ID: {self.case_id}")
        print(f"OUTPUT STATUS: {self.status}")
        
        if self.failed_checks:
            print("FAILED CHECKS:")
            for fail in self.failed_checks:
                print(f"- {fail}")
        
        print("BOUNDARY STATUS:")
        for k, v in self.boundary_status.items():
            print(f"- {k}: {v}")
            
        print("NOTES:")
        for note in self.notes:
            print(f"- {note}")
        print("-" * 60)

def validate_pipeline_state(report_obj, state, writer_intent=None):
    """
    Validates full pipeline state against strict vNext.4 rules.
    """
    parsed = state.get('parsed', [])
    temporal_signals = state.get('temporal', [])
    mediated = state.get('mediated', {})
    
    # 1. Structural Parsing
    # ---------------------
    # Only format tags allowed.
    for line in parsed:
        if line['tag'] not in ['S', 'A', 'D', 'C', 'M']:
            report_obj.fail("Parsing", f"Invalid tag generated: {line['tag']}")
            
    # 4. Temporal Dynamics Checks
    # ---------------------------------------------------------
    # Rule: Signals bounded
    for t in temporal_signals:
        val = t.get('attentional_signal', 0)
        if val > 5.0: 
             report_obj.fail("Temporal", f"Signal runway detected: {val}")

    # 7. Audience-Experience Mediation Checks
    # ---------------------------------------------------------
    reflections = mediated.get('reflections', [])
    silence = mediated.get('silence_explanation')

    # Rule: Question-first framing
    for ref in reflections:
        text = ref.get('reflection', '')
        if "?" not in text:
             report_obj.fail("Mediation", f"Reflection not framed as question: '{text}'")
    
    # Rule: No Forbidden Words (Good/Bad/Fix)
    banned_words = ['good', 'bad', 'fix', 'improve', 'optimize', 'too long', 'too short', 'should']
    all_text = json.dumps(mediated).lower()
    for word in banned_words:
        if word in all_text:
            if "does not indicate quality" in all_text and word == 'quality':
                continue # Allowed disclaimer
            
            report_obj.fail("Ethical Boundary", f"Banned word detected: '{word}'")
            report_obj.boundary_status["ethical_boundaries_held"] = False

    # Rule: Silence Handling
    if not reflections and not silence:
        report_obj.fail("Mediation", "No reflections AND no silence explanation provided.")
        report_obj.boundary_status["silence_handled"] = False
        
    # 6. Writer Intent Checks
    # ---------------------------------------------------------
    if writer_intent:
        acks = mediated.get('intent_acknowledgments', [])
        # We only insist on acknowledgment if patterns were found AND suppressed.
        # But for stress testing, we note it.
        pass


# =============================================================================
# 3. EXECUTION HARNESS
# =============================================================================

def run_suite():
    print("=" * 60)
    print("🚀 SCRIPT_PULSE vNEXT.4 STRESS VALIDATION SUITE")
    print("=" * 60)

    # Matrix Definition
    matrix = [
        ("Early-Draft Explorer", generate_early_draft_explorer(), None),
        ("Over-Optimizer", generate_over_optimizer(), None),
        ("Minimalist", generate_minimalist(), None),
        ("Maximalist", generate_maximalist(), None),
        ("Experimental", generate_experimental(), None),
        ("Comedy", generate_comedy(), None),
        ("Action-First", generate_action_first(), None),
        ("Intent-Declaring", generate_over_optimizer(), [{'scene_range': [0, 20], 'intent': 'intentionally exhausting'}])
    ]

    all_passed = True

    for name, script_gen, intent_decl in matrix:
        report = ValidationReport(case_id=name)
        
        try:
            # MANUAL PIPELINE EXECUTION TO CAPTURE STATE
            
            # 1. Parse
            parsed = parsing.run(script_gen)
            
            # 2. Segment
            segmented = segmentation.run(parsed)
            
            # 3. Encode
            encoded = encoding.run({'scenes': segmented, 'lines': parsed})
            
            # 4. Temporal
            temporal_out = temporal.run({'features': encoded})
            
            # 5. Patterns
            patterns_out = patterns.run({'temporal_signals': temporal_out})
            
            # 6. Intent
            intent_input = {
                'patterns': patterns_out,
                'writer_intent': intent_decl or []
            }
            intent_out = intent.run(intent_input)
            
            # 7. Mediate
            mediated = mediation.run(intent_out)
            
            # Bundle State
            full_state = {
                'parsed': parsed,
                'segmented': segmented,
                'encoded': encoded,
                'temporal': temporal_out,
                'patterns': patterns_out,
                'intent_processing': intent_out,
                'mediated': mediated
            }
            
            # Validate
            validate_pipeline_state(report, full_state, writer_intent=intent_decl)
            
            # Specific Assertions
            if name == "Intent-Declaring":
                acks = mediated.get('intent_acknowledgments', [])
                if not acks:
                    # In Over-Optimizer, we generate 20 repetitive scenes.
                    # Patterns (repetition/demand) SHOULD surface.
                    # Intent covers [0, 20].
                    # So patterns should be suppressed.
                    if patterns_out: # If patterns existed
                         report.fail("Intent", f"Patterns detected {len(patterns_out)} but no acknowledgment of suppression.")
                else:
                    report.add_note(f"Intent acknowledged: {len(acks)} notes.")

            if name == "Minimalist" and not mediated.get('reflections'):
                if not mediated.get('silence_explanation'):
                     report.fail("Mediation", "Minimalist script silence not explained.")
                else:
                     report.add_note("Silence explanation verified.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            report.fail("Crash", f"Pipeline exception: {e}")
            all_passed = False

        if report.status == "FAIL":
            all_passed = False
            
        report.print_report()

    print("=" * 60)
    if all_passed:
        print("✅ VALIDATION SUCCESS: All profiles within behavioral bounds.")
    else:
        print("❌ VALIDATION FAILURE: Compliance gaps detected.")
    print("=" * 60)

if __name__ == "__main__":
    run_suite()
