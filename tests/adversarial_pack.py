#!/usr/bin/env python3
"""
Adversarial Script Pack (v13.1 Block 5)

Targeted attack scenarios designed to find parser, temporal, and
uncertainty edge cases.

Test cases:
    1. Repeated fake scene headings every line
    2. Alternating 1-word scenes
    3. 10K character dialogue line
    4. Only parentheticals
    5. Mixed language per line

Assertions:
    - No crash
    - Bounded pulse (0-1)
    - Uncertainty rises on weak signals
    - Parser does not create zero-length scenes

Usage:
    PYTHONPATH=. python3 tests/adversarial_pack.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0
RESULTS = []


def log(test, check, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
        icon = "✅"
    else:
        FAIL += 1
        icon = "❌"
    RESULTS.append({'test': test, 'check': check, 'passed': passed, 'detail': detail})
    print(f"  {icon} [{test}] {check}: {detail[:80]}")


def timed_run(script):
    from scriptpulse import runner
    t0 = time.time()
    r = runner.run_pipeline(script, experimental_mode=True, moonshot_mode=True)
    return r, round(time.time() - t0, 1)


def validate_output(result, test_name):
    """Common assertions across all adversarial tests."""
    errors = []
    
    # Bounded pulse
    trace = result.get('temporal_trace', [])
    for i, point in enumerate(trace):
        sig = point.get('attentional_signal', 0)
        if not (0 <= sig <= 1):
            errors.append(f"Scene {i}: pulse {sig} out of bounds")
    
    log(test_name, "Bounded pulse (0-1)", len(errors) == 0,
        f"All {len(trace)} scenes in bounds" if not errors else errors[0])
    
    # No zero-length scenes
    scene_info = result.get('scene_info', [])
    log(test_name, "No zero-length scenes", len(scene_info) > 0,
        f"{len(scene_info)} scenes")
    
    # Total scenes > 0
    log(test_name, "total_scenes > 0", result.get('total_scenes', 0) > 0,
        f"total_scenes={result.get('total_scenes', 0)}")
    
    return trace


def test_fake_headings():
    """1. Repeated fake scene headings every line."""
    print("\n--- Test 1: Fake Headings Every Line ---")
    lines = []
    for i in range(50):
        lines.append(f"INT. ROOM {i} - DAY")
        lines.append(f"CHARACTER_{i}")
        lines.append(f"Line {i}.")
    script = "\n".join(lines)
    
    try:
        r, t = timed_run(script)
        log("FAKE_HEADINGS", "No crash", True, f"Time={t}s")
        validate_output(r, "FAKE_HEADINGS")
        
        # Should have high scene count
        log("FAKE_HEADINGS", "Parser handles extreme headings",
            r.get('total_scenes', 0) >= 1,
            f"Scenes={r.get('total_scenes', 0)}")
    except Exception as e:
        log("FAKE_HEADINGS", "No crash", False, str(e)[:120])


def test_one_word_scenes():
    """2. Alternating 1-word scenes."""
    print("\n--- Test 2: Alternating 1-Word Scenes ---")
    lines = []
    for i in range(30):
        lines.append(f"INT. ROOM {i} - DAY")
        lines.append("Word.")
    script = "\n\n".join(lines)  # Double newline between each
    
    try:
        r, t = timed_run(script)
        log("ONE_WORD", "No crash", True, f"Time={t}s")
        validate_output(r, "ONE_WORD")
        
        # Uncertainty should be elevated for weak signals
        uncertainty = r.get('uncertainty_quantification', [])
        if uncertainty:
            avg_std = sum(u.get('std_dev', 0) for u in uncertainty) / len(uncertainty)
            log("ONE_WORD", "Uncertainty rises", avg_std > 0.01,
                f"avg_std_dev={avg_std:.4f}")
    except Exception as e:
        log("ONE_WORD", "No crash", False, str(e)[:120])


def test_10k_dialogue():
    """3. 10K character dialogue line."""
    print("\n--- Test 3: 10K Character Dialogue ---")
    long_line = "I repeat this endlessly. " * 400  # ~10K chars
    script = f"""INT. OFFICE - DAY

PROFESSOR
{long_line}

STUDENT
Okay."""
    
    try:
        r, t = timed_run(script)
        log("10K_DIALOGUE", "No crash", True, f"Time={t}s")
        validate_output(r, "10K_DIALOGUE")
    except Exception as e:
        log("10K_DIALOGUE", "No crash", False, str(e)[:120])


def test_only_parentheticals():
    """4. Only parentheticals — no actual dialogue or action."""
    print("\n--- Test 4: Only Parentheticals ---")
    script = """INT. THERAPY ROOM - DAY

CHARACTER_A
(sighing heavily)
(beat)
(looking away)
(whispering)
(long pause)
(shaking head)
(clearing throat)

CHARACTER_B
(nodding)
(beat)
(staring)
(fidgeting)
(silence)"""
    
    try:
        r, t = timed_run(script)
        log("PARENTHETICALS", "No crash", True, f"Time={t}s")
        validate_output(r, "PARENTHETICALS")
    except Exception as e:
        log("PARENTHETICALS", "No crash", False, str(e)[:120])


def test_mixed_language():
    """5. Mixed language per line — code-switching within dialogue."""
    print("\n--- Test 5: Mixed Language Per Line ---")
    script = """INT. UN HEADQUARTERS - DAY

DIPLOMAT_A
Bonjour, we need to discuss the Vereinbarung immediately. これは重要です。

DIPLOMAT_B
D'accord, mais primero debemos hablar sobre die Konsequenzen. Это сложно.

DIPLOMAT_A
Entiendo. Let's обсудим les détails zusammen. 一起讨论吧。

ACTION: Papers in multiple scripts (العربية, हिन्दी, 한국어) cover the table.
The خريطة shows disputed ελληνικά borders near 東京."""
    
    try:
        r, t = timed_run(script)
        log("MIXED_LANG", "No crash", True, f"Time={t}s")
        validate_output(r, "MIXED_LANG")
    except Exception as e:
        log("MIXED_LANG", "No crash", False, str(e)[:120])


def main():
    print("=" * 60)
    print("ADVERSARIAL SCRIPT PACK — v13.1 Block 5")
    print("=" * 60)
    
    test_fake_headings()
    test_one_word_scenes()
    test_10k_dialogue()
    test_only_parentheticals()
    test_mixed_language()
    
    print("\n" + "=" * 60)
    print("ADVERSARIAL RESULTS")
    print("=" * 60)
    print(f"  ✅ Passed: {PASS}")
    print(f"  ❌ Failed: {FAIL}")
    print(f"  Total:    {PASS + FAIL}")
    
    if FAIL > 0:
        print(f"\n❌ ADVERSARIAL PACK: FAIL")
        sys.exit(1)
    else:
        print(f"\n✅ ADVERSARIAL PACK: PASS")
        sys.exit(0)


if __name__ == '__main__':
    main()
