"""
ScriptPulse Runtime Estimator
Predicts film length based on script characteristics.
"""

def estimate_runtime(scenes):
    """
    Estimate film runtime in minutes.
    
    Args:
        scenes: List of scene dictionaries with 'lines'
        
    Returns:
        dict with 'min_minutes', 'max_minutes', 'avg_minutes'
    """
    
    total_pages = 0
    dialogue_lines = 0
    action_lines = 0
    
    # Rough estimation: 55 lines = 1 page
    lines_per_page = 55
    
    for scene in scenes:
        lines = scene.get('lines', [])
        # Count all lines for page estimation
        total_lines_in_scene = len(lines)
        
        # Heuristic: If lines are missing but text exists, estimate
        if total_lines_in_scene == 0 and scene.get('text'):
            total_lines_in_scene = len(scene['text'].split('\n'))
            
        dialogue_count = 0
        action_count = 0
        
        for line in lines:
            tag = line.get('tag', 'A')
            # Support both legacy (D) and new (dialogue) tags
            if tag in ['D', 'dialogue', 'parenthetical']:
                dialogue_count += 1
            elif tag in ['A', 'action', 'scene_heading', 'transition', 'shot']:
                action_count += 1
                
        dialogue_lines += dialogue_count
        action_lines += action_count
        
        # If parsing failed or empty, assume mix based on text length
        if total_lines_in_scene > 0:
             pass # we have data
        else:
             total_lines_in_scene = max(1, len(scene.get('text', '')) // 40) # 40 chars ~ 1 line?
             
        total_pages += (total_lines_in_scene / lines_per_page)

    total_lines = dialogue_lines + action_lines # Used for ratio only
    
    if total_pages == 0:
        return {'min_minutes': 0, 'max_minutes': 0, 'avg_minutes': 0}
    
    # Base estimate: 1 page = 1 minute (industry standard)
    base_minutes = total_pages
    
    # Adjust for dialogue density
    # High dialogue = slower pacing (more time needed)
    # High action = faster pacing (visual scenes play quickly)
    dialogue_ratio = dialogue_lines / total_lines
    
    if dialogue_ratio > 0.7:  # Dialogue-heavy (like Aaron Sorkin)
        # Add 10% time
        multiplier = 1.1
    elif dialogue_ratio < 0.3:  # Action-heavy (like Mad Max)
        # Subtract 5% time
        multiplier = 0.95
    else:
        multiplier = 1.0
        
    avg_minutes = base_minutes * multiplier
    
    # Industry variance: ±5 minutes
    min_minutes = max(1, avg_minutes - 5)
    max_minutes = avg_minutes + 5
    
    return {
        'min_minutes': int(min_minutes),
        'max_minutes': int(max_minutes),
        'avg_minutes': int(avg_minutes),
        'dialogue_ratio': round(dialogue_ratio, 2)
    }
