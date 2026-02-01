"""
ScriptPulse Suggestion Agent (Co-Creativity Research Layer)
Gap Solved: "Passive Observer" / "So What?"

Generates actionable structural strategies to repair identified issues.
Does NOT write text. Writes "Constraints" to spark writer creativity.
Mixed-Initiative Co-Creativity.
"""

import random

def run(temporal_trace):
    """
    Generate suggestions based on Affective States.
    """
    suggestions = []
    
    if not temporal_trace:
        return []
        
    # Analyze blocks
    # Looking for contiguous blocks of "Melancholy" (Boredom) or "Extreme High" (Fatigue)
    
    for i, point in enumerate(temporal_trace):
        state = point.get('affective_state', 'Normal')
        effort = point.get('instantaneous_effort', 0.5)
        scene_idx = point['scene_index']
        
        # Strategy Generator
        suggestion = None
        
        # CASE 1: Melancholy (Low Energy, Negative/Neutral) -> Boring?
        if state == "Melancholy" or (effort < 0.2):
            suggestion = {
                'scene': scene_idx,
                'diagnosis': "Low Arousal (Risk of Boredom)",
                'strategy': "Inject Kinetic Energy",
                'tactics': [
                    "Cut sentence length by 20% to increase tempo.",
                    "Add 3 'Visual' words (Colors/Motion) to spike Imagery Load.",
                    "Have a character interrupt another."
                ]
            }
            
        # CASE 2: Extreme Anxiety (Too High, Too Long)
        # We need state history to know "Too Long", but looking at single point extreme:
        elif effort > 0.85:
            suggestion = {
                'scene': scene_idx,
                'diagnosis': "Extreme Cognitive Load (Risk of Burnout)",
                'strategy': "Induce Recovery",
                'tactics': [
                    "Insert a 'Visual Rest' moment (Looking at a view).",
                    "Simplify syntax: Unpack nested clauses.",
                    "Switch to 'Monologue' mode (Lower Social Tension)."
                ]
            }
            
        # Random sampling to avoid spamming suggestions for every scene
        if suggestion and random.random() < 0.3:
            suggestions.append(suggestion)
            
    # Sort by urgency (extreme efforts first)
    # Return top 3
    return {
        'structural_repair_strategies': suggestions[:3]
    }
