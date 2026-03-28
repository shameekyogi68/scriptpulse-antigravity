"""
Verification Script: 8 Universal Logic Rules
Tests the ScriptPulse diagnostic engine deterministically using isolated mock data.
"""
import os
import sys
import statistics

# Ensure scriptpulse is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scriptpulse.agents.writer_agent import WriterAgent
from scriptpulse.agents.interpretation_agent import InterpretationAgent

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def make_scene(idx, att_sig=0.5, conflict=0.1, visual_int=0.1, otn=0.1,
               dialogue="", chars=None, era_heading=None):
    """
    Factory for a fully-populated mock temporal trace scene.
    Includes every field accessed by _diagnose_health and related methods.
    """
    return {
        'scene_index': idx,
        'attentional_signal': att_sig,
        'fatigue_state': 0.0,
        'expectation_strain': 0.0,
        'conflict': conflict,
        'stakes': 0.2,
        'exposition_score': 0.0,
        'pacing_volatility': 0.0,
        'sentiment': 0.0,
        'visual_intensity': visual_int,
        'on_the_nose': {'on_the_nose_ratio': otn},
        'representative_dialogue': dialogue,
        'character_scene_vectors': chars or {},
        'motifs': [],
        'semantic_motifs': [],
        'tell_vs_show': {'tell_ratio': 0.0, 'literal_emotions': 0},
        'stakes_taxonomy': {'dominant': 'Emotional'},
        'stichomythia': {'has_stichomythia': False},
        'shoe_leather': {'has_shoe_leather': False},
        'narrative_closure': False,
        'reader_frustration': {'internal_state_hits': [], 'name_crowding': False, 'similar_name_pairs': []},
        'visual_abstraction': {'action_lines': 2},
        'location_data': {
            'raw_heading': era_heading or 'INT. OFFICE - DAY',
            'location': 'OFFICE',
            'int_ext': 'INT'
        }
    }


def test_universal_rules():
    print("=" * 60)
    print("  ScriptPulse Logic Engine — Universal Rules Verification")
    print("=" * 60)

    os.environ['SCRIPTPULSE_HEURISTICS_ONLY'] = '1'

    writer = WriterAgent()

    trace = []

    # ─────────────────────────────────────────────────────────────
    # Rule 1: Era Benchmarking
    # The engine scans location_data.raw_heading per scene for
    # markers like 'castle', 'kingdom', 'century', 'historical'.
    # If detected → script_era set to 'classic' → scoring adjusts.
    # We seed scene 0 with a period indicator.
    # ─────────────────────────────────────────────────────────────
    CLASSIC_HEADING = "INT. MEDIEVAL CASTLE GREAT HALL - DAY"

    # ─────────────────────────────────────────────────────────────
    # Rule 2: Same Voice Syndrome
    # Requires ≥2 chars with ≥10 lines, same register, WPT stdev
    # < 10% of avg WPT, agency stdev < 0.15.
    # We give ALICE & BOB identical fingerprints.
    # ─────────────────────────────────────────────────────────────
    VOICE_CHARS = {
        'ALICE': {'agency': 0.50, 'positivity': 0.5, 'words_per_turn': 8,
                  'register': 'formal', 'decisions': 0, 'initiations': 0,
                  'commands': 0, 'consequences': 0, 'presence_ratio': 0.50,
                  'moral_sentiment': 0.5},
        'BOB':   {'agency': 0.50, 'positivity': 0.5, 'words_per_turn': 8,
                  'register': 'formal', 'decisions': 0, 'initiations': 0,
                  'commands': 0, 'consequences': 0, 'presence_ratio': 0.50,
                  'moral_sentiment': 0.5},
    }

    # Scenes 0–14 (15 scenes): Same-Voice block with castle era marker
    for i in range(15):
        trace.append(make_scene(
            i,
            era_heading=CLASSIC_HEADING,
            chars=VOICE_CHARS
        ))

    # ─────────────────────────────────────────────────────────────
    # Rule 3: Scene Number Transparency
    # Verified via _format_scene_ref — output must include "Scene N"
    # format. This is structural and implicit; assert on output shape.
    # ─────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────
    # Rule 5: Contradiction Check (On-The-Nose)
    # on_the_nose_ratio > 0.25 AND conflict ≤ 0.4 AND visual_int ≤ 0.4
    # → triggers 🗣️ On-The-Nose Dialogue warning.
    # ─────────────────────────────────────────────────────────────
    trace.append(make_scene(
        15,
        att_sig=0.3, conflict=0.05, visual_int=0.05,
        otn=0.90,   # Strongly on-the-nose
        dialogue="I am telling you exactly how angry I feel about what you have done to me."
    ))

    # ─────────────────────────────────────────────────────────────
    # Rule 4 & 7: Agency Metrics + Character Arc Classification
    # CHARLIE goes from low presence/agency (Act 1) to high (Act 3).
    # Expected: Heroic Transformation 🌔 (Agency UP, Moral UP)
    # ─────────────────────────────────────────────────────────────
    for i in range(11):
        act_progress = i / 10.0                    # 0.0 → 1.0
        trace.append(make_scene(
            16 + i,
            att_sig=0.6,
            chars={
                'CHARLIE': {
                    'agency':         0.10 + act_progress * 0.80,
                    'presence_ratio': 0.20 + act_progress * 0.70,
                    'decisions':      0 if i < 5 else 3,
                    'initiations':    0 if i < 6 else 2,
                    'commands':       0 if i < 8 else 2,
                    'consequences':   0 if i < 9 else 2,
                    'moral_sentiment': 0.30 + act_progress * 0.60,   # UP
                }
            }
        ))

    # ─────────────────────────────────────────────────────────────
    # Voice fingerprints (top-level, not per-scene)
    # These are the aggregated stats the WriterAgent receives from
    # the parser for the _diagnose_voice() method.
    # ─────────────────────────────────────────────────────────────
    voice_fingerprints = {
        'ALICE': {
            'line_count': 15, 'complexity': 0.5, 'positivity': 0.5,
            'punctuation_rate': 0.10, 'words_per_turn': 8,
            'register': 'formal', 'agency': 0.50
        },
        'BOB': {
            'line_count': 15, 'complexity': 0.5, 'positivity': 0.5,
            'punctuation_rate': 0.10, 'words_per_turn': 8,
            'register': 'formal', 'agency': 0.50
        },
        'CHARLIE': {
            'line_count': 9, 'complexity': 0.7, 'positivity': 0.7,    # <10 → excluded from voice analysis
            'punctuation_rate': 0.05, 'words_per_turn': 12,
            'register': 'casual', 'agency': 0.90
        },
    }

    mock_report = {
        'temporal_trace': trace,
        'voice_fingerprints': voice_fingerprints,
        'narrative_diagnosis': [],   # InterpretationAgent output (empty for isolation)
        'fairness_audit': {},
        'scene_info': [],
        'suggestions': {},
    }

    # ─────────────────────────────────────────────────────────────
    # Execute Analysis
    # ─────────────────────────────────────────────────────────────
    analysis = writer.analyze(mock_report, genre='drama', script_era='auto')

    # ─── Extract outputs ─────────────────────────────────────────
    wi         = analysis.get('writer_intelligence', {})
    warnings   = wi.get('narrative_diagnosis', [])
    dashboard  = wi.get('structural_dashboard', {})
    arcs       = dashboard.get('character_arcs', {})
    score      = dashboard.get('scriptpulse_score')
    script_era = wi.get('script_era', 'unknown')

    print(f"\n  ScriptPulse Score : {score}")
    print(f"  Script Era Detected: {script_era}")
    print(f"  Diagnostics ({len(warnings)}):")
    for w in warnings:
        print(f"    • {w[:100]}")

    # ─────────────────────────────────────────────────────────────
    # RULE ASSERTIONS
    # ─────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    results = {}

    # Rule 1: Era Benchmarking
    # Verify the output reports 'classic' script_era.
    r1 = (script_era == 'classic')
    results['Rule 1 — Era Benchmarking'] = r1
    print(f"  Rule 1 (Era Benchmarking):     {PASS if r1 else FAIL}  [era={script_era}]")

    # Rule 2: Sub-scores & Contradiction Flagging
    pacing = dashboard.get('pacing_score')
    integrity = dashboard.get('structural_integrity')
    arc_depth = dashboard.get('character_arc_depth')
    pti = dashboard.get('page_turner_index')
    
    r2_presence = all(isinstance(s, (int, float)) for s in [pacing, integrity, arc_depth, pti])
    results['Rule 2 — Sub-score Availability'] = r2_presence
    print(f"  Rule 2 (Sub-scores):           {PASS if r2_presence else FAIL}")

    # Rule 2: Master Score Absence
    r2_score = ('scriptpulse_score' not in dashboard)
    results['Rule 2 — Master Score Absence'] = r2_score
    print(f"  Rule 2 (Master Score Absence): {PASS if r2_score else FAIL}")

    # Rule 2: Contradiction Flagging
    r2_flag = any("Metric Contradiction" in w for w in warnings)
    results['Rule 2 — Contradiction Flagging'] = r2_flag
    print(f"  Rule 2 (Contradiction Flag):  {PASS if r2_flag else FAIL}")

    # Rule 3: Scene Ref Transparency
    r3 = any("Scene" in w and "[p." in w for w in warnings)
    results['Rule 3 — Scene Ref Transparency'] = r3
    print(f"  Rule 3 (Scene Ref Transparency): {PASS if r3 else FAIL}")

    # Rule 4: Agency Metrics (Signals)
    charlie = arcs.get('CHARLIE', {})
    r4_signals = ('agency_act1' in charlie and 'agency_act3' in charlie)
    results['Rule 4 — Agency Signals'] = r4_signals
    print(f"  Rule 4 (Agency Signals):       {PASS if r4_signals else FAIL}  [Act1={charlie.get('agency_act1')}, Act3={charlie.get('agency_act3')}]")

    # Rule 5: Contradiction Check — On-The-Nose
    r5 = any("On-The-Nose Dialogue" in w for w in warnings)
    results['Rule 5 — Contradiction Check'] = r5
    print(f"  Rule 5 (Contradiction Check):  {PASS if r5 else FAIL}")

    # Rule 6: Location Profile
    r6 = 'location_profile' in dashboard
    results['Rule 6 — Location Profile Present'] = r6
    print(f"  Rule 6 (Location Profile):     {PASS if r6 else FAIL}")

    # Rule 7: Character Arc Classification (Rule 4 result)
    r7 = charlie.get('arc_type') == "Aspirational Rise 🌔"
    results['Rule 7 — Character Arc'] = r7
    print(f"  Rule 7 (Character Arc):        {PASS if r7 else FAIL}  [{charlie.get('arc_type')}]")

    # Rule 9: Comparable Films ( بالضبط 3 )
    comps = dashboard.get('commercial_comps', [])
    r9_count = len(comps) == 3
    r9_match = any("Blue Valentine" in c or "Ex Machina" in c for c in comps) # Expected matches for Relationship/Contained
    results['Rule 9 — 3 Comps Match'] = r9_count and r9_match
    print(f"  Rule 9 (3 Comps):              {PASS if r9_count and r9_match else FAIL}  [comps={comps}]")

    # ─────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    passed = sum(1 for v in results.values() if v)
    total  = len(results)
    print(f"  Result: {passed}/{total} rules passed")

    if passed == total:
        print("  🏆  ALL UNIVERSAL LOGIC RULES OPERATIONAL.")
        sys.exit(0)
    else:
        print("  ⚠️   SOME RULES FAILED — see above.")
        for name, ok in results.items():
            if not ok:
                print(f"       ↳ {name}")
        sys.exit(1)


if __name__ == "__main__":
    test_universal_rules()
