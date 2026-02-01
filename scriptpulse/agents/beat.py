"""
ScriptPulse Beat Agent (High-Resolution Research Layer)
Gap Solved: "Low Resolution" / Pixelation

Sub-segments scenes into "Beats" (micro-units of ~100-150 words) 
to generate a High-Definition temporal trace.
"""

import math

BEAT_WORD_TARGET = 120  # Approx 45-60 seconds of screen time

def subdivide_into_beats(scenes):
    """
    Explode a list of Scene objects into a larger list of Beat objects.
    Preserves scene_index, adds beat_index.
    """
    beats = []
    
    for scene in scenes:
        lines = scene.get('lines', [])
        current_beat_lines = []
        current_word_count = 0
        beat_in_scene = 1
        
        # Heuristic: Break on Boundaries or Size
        # Strong Boundaries: Scene Headings (handled by parent), Transitions (CUT TO:)
        # Weak Boundaries: Character change? Maybe too frequent.
        # Length-based chunking is the most robust proxy for "Time".
        
        for line in lines:
            text = line.get('text', "")
            words = len(text.split())
            
            # Check for explicit transition line
            is_transition = line.get('type') == 'TRANSITION'
            
            # If adding this line exceeds target, push beat (unless it's the only line)
            if current_word_count + words > BEAT_WORD_TARGET and current_beat_lines:
                # Flush current beat
                beat_obj = create_beat(scene, current_beat_lines, beat_in_scene)
                beats.append(beat_obj)
                
                # Reset
                current_beat_lines = []
                current_word_count = 0
                beat_in_scene += 1
            
            current_beat_lines.append(line)
            current_word_count += words
            
            # If transition, force break after this line
            if is_transition:
                beat_obj = create_beat(scene, current_beat_lines, beat_in_scene)
                beats.append(beat_obj)
                current_beat_lines = []
                current_word_count = 0
                beat_in_scene += 1
                
        # Flush remaining
        if current_beat_lines:
             beat_obj = create_beat(scene, current_beat_lines, beat_in_scene)
             beats.append(beat_obj)
             
    return beats

def create_beat(parent_scene, lines, beat_idx):
    """Create a beat object that mimics a scene object for downstream agents."""
    return {
        'scene_index': parent_scene['scene_index'],
        'beat_index': beat_idx,
        'heading': f"{parent_scene['heading']} (Beat {beat_idx})",
        'lines': lines,
        'start_line': lines[0]['line_index'] if lines else 0,
        'end_line': lines[-1]['line_index'] if lines else 0,
        # Preserve parent metadata
        'location': parent_scene.get('location', 'UNKNOWN'),
        'time': parent_scene.get('time', 'UNKNOWN')
    }
