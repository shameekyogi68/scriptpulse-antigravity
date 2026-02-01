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
        for line in scene['lines']:
            tag = line.get('tag', 'A')
            
            if tag == 'D':  # Dialogue
                dialogue_lines += 1
            elif tag == 'A':  # Action
                action_lines += 1
                
    total_lines = dialogue_lines + action_lines
    if total_lines == 0:
        return {'min_minutes': 0, 'max_minutes': 0, 'avg_minutes': 0}
    
    # Calculate pages
    total_pages = total_lines / lines_per_page
    
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
