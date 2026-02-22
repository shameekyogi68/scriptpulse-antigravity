#!/usr/bin/env python3
"""
Calibration Benchmark Generator (v13.1)

Generates 120 labeled benchmark scripts for regression testing:
  - 50 short  (1-3 scenes, ~20-60 lines)
  - 50 medium (4-10 scenes, ~60-200 lines)
  - 20 long   (15-30 scenes, ~300-600 lines)

Labels per script:
  - boredom_risk:     [low_bound, high_bound]  (0-1)
  - confusion_risk:   [low_bound, high_bound]  (0-1)
  - fatigue_perception: [low_bound, high_bound] (0-1)
"""

import json
import os
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_DIR = os.path.join(SCRIPT_DIR, 'benchmark_scripts')
EXPECTED_RANGES_PATH = os.path.join(SCRIPT_DIR, 'expected_ranges.json')

# --- Genre Templates ---
GENRES = ['drama', 'thriller', 'comedy', 'horror', 'romance']

LOCATIONS = [
    "INT. OFFICE - DAY", "EXT. STREET - NIGHT", "INT. KITCHEN - MORNING",
    "EXT. ROOFTOP - SUNSET", "INT. HOSPITAL - NIGHT", "INT. CLASSROOM - DAY",
    "EXT. PARK - AFTERNOON", "INT. BAR - NIGHT", "INT. COURTROOM - DAY",
    "EXT. BEACH - DAWN", "INT. BUNKER - NIGHT", "INT. LIBRARY - DAY",
    "EXT. FOREST - DUSK", "INT. SUBWAY - NIGHT", "EXT. HIGHWAY - DAY",
]

CHARACTERS = [
    "ALEX", "MARIA", "DAVID", "SARAH", "JAMES", "LILY", "OMAR", "CHEN",
    "KATE", "RAVI", "ELENA", "MICHAEL", "SOFIA", "JOHN", "PRIYA",
]

ACTION_TEMPLATES = [
    "The room is silent. {char} paces back and forth, hands behind their back.",
    "{char} slams the door, rattling the windows. Dust falls from the ceiling.",
    "Rain hammers the glass. {char} stares out, jaw tight.",
    "{char} sits alone, staring at the empty chair across the table.",
    "Footsteps echo in the corridor. {char} freezes, listening.",
    "Papers scatter across the desk as {char} searches frantically.",
    "{char} picks up the phone, dials, hangs up. Dials again.",
    "The clock ticks. {char} watches the second hand crawl.",
    "A siren wails outside. {char} pulls the curtain aside carefully.",
    "Fluorescent lights buzz overhead. {char} rubs tired eyes.",
    "{char} enters slowly, scanning the room for threats.",
    "The candle flickers. Shadows dance across {char}'s face.",
]

DIALOGUE_TEMPLATES = [
    "I told you this would happen. You never listen.",
    "We don't have much time. Where is it?",
    "That's not what I meant and you know it.",
    "Look at me. Tell me the truth.",
    "I'm leaving. Don't try to stop me.",
    "How long have you known? Days? Weeks?",
    "This changes everything.",
    "You think this is easy? Try living my life.",
    "I can't do this anymore.",
    "One chance. That's all we get.",
    "Who sent you?",
    "The results came back. It's confirmed.",
    "We need to talk about what happened.",
    "Promise me you won't tell anyone.",
    "It's over. Accept it.",
]

PARENTHETICALS = ["(quietly)", "(shouting)", "(whispering)", "(angry)", "(beat)", "(sighs)", "(laughing)", ""]


def generate_scene(chars, genre='drama'):
    """Generate one scene block."""
    loc = random.choice(LOCATIONS)
    lines = [loc, ""]
    
    # 2-5 action + dialogue beats
    beats = random.randint(2, 5)
    used_chars = random.sample(chars, min(random.randint(1, 3), len(chars)))
    
    for _ in range(beats):
        # Action line
        char = random.choice(used_chars)
        action = random.choice(ACTION_TEMPLATES).format(char=char)
        lines.append(action)
        lines.append("")
        
        # Dialogue
        speaker = random.choice(used_chars)
        paren = random.choice(PARENTHETICALS)
        dialogue = random.choice(DIALOGUE_TEMPLATES)
        lines.append(speaker)
        if paren:
            lines.append(paren)
        lines.append(dialogue)
        lines.append("")
    
    return "\n".join(lines)


def generate_script(num_scenes, genre='drama'):
    """Generate a full screenplay with N scenes."""
    chars = random.sample(CHARACTERS, min(random.randint(2, 6), len(CHARACTERS)))
    scenes = [generate_scene(chars, genre) for _ in range(num_scenes)]
    return "\n\n".join(scenes)


def estimate_labels(num_scenes, genre):
    """
    Estimate expected score ranges based on script structure.
    These are NOT exact predictions — they're calibration anchors.
    """
    if num_scenes <= 3:
        # Short scripts: low boredom risk, low fatigue, moderate confusion
        boredom = [0.1, 0.4]
        confusion = [0.2, 0.5]
        fatigue = [0.05, 0.3]
    elif num_scenes <= 10:
        # Medium: moderate across the board
        boredom = [0.2, 0.6]
        confusion = [0.15, 0.5]
        fatigue = [0.2, 0.6]
    else:
        # Long: higher fatigue, moderate boredom, moderate confusion
        boredom = [0.3, 0.7]
        confusion = [0.2, 0.6]
        fatigue = [0.4, 0.8]
    
    # Genre adjustments
    if genre == 'thriller':
        boredom = [max(0, b - 0.1) for b in boredom]
    elif genre == 'comedy':
        fatigue = [max(0, f - 0.1) for f in fatigue]
    
    return {
        'boredom_risk': [round(b, 2) for b in boredom],
        'confusion_risk': [round(c, 2) for c in confusion],
        'fatigue_perception': [round(f, 2) for f in fatigue]
    }


def main():
    os.makedirs(BENCHMARK_DIR, exist_ok=True)
    
    expected_ranges = {}
    script_id = 0
    
    configs = [
        # (count, scene_range, category)
        (50, (1, 3), 'short'),
        (50, (4, 10), 'medium'),
        (20, (15, 30), 'long'),
    ]
    
    for count, (min_scenes, max_scenes), category in configs:
        for i in range(count):
            num_scenes = random.randint(min_scenes, max_scenes)
            genre = random.choice(GENRES)
            
            script = generate_script(num_scenes, genre)
            
            filename = f"{category}_{script_id:03d}_{genre}.txt"
            filepath = os.path.join(BENCHMARK_DIR, filename)
            
            with open(filepath, 'w') as f:
                f.write(script)
            
            expected_ranges[filename] = {
                'category': category,
                'genre': genre,
                'num_scenes': num_scenes,
                'line_count': len(script.splitlines()),
                'labels': estimate_labels(num_scenes, genre)
            }
            
            script_id += 1
    
    # Write expected ranges
    with open(EXPECTED_RANGES_PATH, 'w') as f:
        json.dump(expected_ranges, f, indent=2)
    
    print(f"Generated {script_id} benchmark scripts in {BENCHMARK_DIR}")
    print(f"Expected ranges saved to {EXPECTED_RANGES_PATH}")
    
    # Summary
    for category in ['short', 'medium', 'long']:
        count = sum(1 for v in expected_ranges.values() if v['category'] == category)
        avg_lines = sum(v['line_count'] for v in expected_ranges.values() if v['category'] == category) / count
        print(f"  {category}: {count} scripts, avg {avg_lines:.0f} lines")


if __name__ == '__main__':
    main()
