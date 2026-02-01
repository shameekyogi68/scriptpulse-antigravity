"""
ScriptPulse Scene Notes Agent (Writer's Tool)
Generates specific, actionable feedback for each scene.
"""

def analyze_scene(scene, scene_index, temporal_point, valence_score, syntax_score):
    """
    Generate actionable notes for a single scene.
    
    Returns:
        list of dicts with 'severity', 'issue', 'suggestion'
    """
    notes = []
    
    # Check 1: Low Tension (Flat Scene)
    tension = temporal_point.get('attentional_signal', 0)
    if tension < 0.3:
        notes.append({
            'severity': 'warning',
            'issue': '⚠️ Low Conflict',
            'suggestion': 'Add an obstacle, argument, or decision point to raise stakes.'
        })
    
    # Check 2: Negative Emotion (unless intentional)
    if valence_score < -0.2:
        notes.append({
            'severity': 'info',
            'issue': '😐 Heavy Tone',
            'suggestion': 'Scene feels dark. If intentional, ignore. Otherwise, add a moment of relief or hope.'
        })
    
    # Check 3: High Complexity (Confusing)
    if syntax_score > 0.7:
        notes.append({
            'severity': 'warning',
            'issue': '🔴 Complex Language',
            'suggestion': 'Dialogue is dense. Simplify sentences or add visual action to break it up.'
        })
    
    # Check 4: Long Dialogue Blocks (Exposition Risk)
    dialogue_lines = [l for l in scene['lines'] if l.get('tag') == 'D']
    long_blocks = [l for l in dialogue_lines if len(l['text'].split()) > 40]
    if long_blocks:
        notes.append({
            'severity': 'warning',
            'issue': '💬 Long Monologue',
            'suggestion': f'Break up this {len(long_blocks[0]["text"].split())}-word speech. Add interruptions or reactions.'
        })
    
    # Check 5: No Dialogue (Silent Scene)
    if len(dialogue_lines) == 0 and len(scene['lines']) > 3:
        notes.append({
            'severity': 'info',
            'issue': '🔇 Silent Scene',
            'suggestion': 'Pure visual scene. If intentional, great! Otherwise, add dialogue for clarity.'
        })
    
    # Check 6: High Tension + Positive Valence (Weird combo)
    if tension > 0.7 and valence_score > 0.2:
        notes.append({
            'severity': 'info',
            'issue': '🎢 Tonal Mismatch?',
            'suggestion': 'High tension but positive tone. Check if emotions match the conflict.'
        })
    
    return notes

def run(data):
    """
    Generate scene-level feedback for all scenes.
    
    Args:
        data: dict with 'scenes', 'temporal_trace', 'valence_scores', 'syntax_scores'
        
    Returns:
        dict: {scene_index: [notes]}
    """
    scenes = data.get('scenes', [])
    trace = data.get('temporal_trace', [])
    valence = data.get('valence_scores', [])
    syntax = data.get('syntax_scores', [])
    
    scene_feedback = {}
    
    for i, scene in enumerate(scenes):
        t_point = trace[i] if i < len(trace) else {}
        v_score = valence[i] if i < len(valence) else 0
        s_score = syntax[i] if i < len(syntax) else 0
        
        notes = analyze_scene(scene, i, t_point, v_score, s_score)
        if notes:
            scene_feedback[i] = notes
    
    return scene_feedback
