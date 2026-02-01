"""
ScriptPulse Coherence Agent (Cognitive Modeling Layer)
Gap Solved: "Context Switch Blindness"

Calculates the "Switching Cost" (Orientation Load) between scenes.
Based on Event Indexing Model (Zwaan et al.):
- Space (Location Change)
- Time (Day/Night Change)
- Entity (Character Set Change)
"""

def run(data):
    """
    Calculate Disorientation Penalty (0.0 to 1.0) for each scene transition.
    Scene[0] is always 0.0 (Establishment).
    """
    scenes = data.get('scenes', [])
    scores = []
    
    if not scenes:
        return []
    
    # Init first scene
    scores.append(0.0) 
    
    for i in range(1, len(scenes)):
        prev = scenes[i-1]
        curr = scenes[i]
        
        penalty = 0.0
        
        # 1. Spatial Discontinuity (Location Change)
        # Check Heading (INT. KITCHEN vs INT. BEDROOM)
        # Simple string compare of the 'location' part
        prev_loc = get_loc(prev['heading'])
        curr_loc = get_loc(curr['heading'])
        
        if prev_loc != curr_loc:
            penalty += 0.4 # Major cost
            
        # 2. Temporal Discontinuity
        # Check Time (DAY vs NIGHT)
        prev_time = get_time(prev['heading'])
        curr_time = get_time(curr['heading'])
        
        if prev_time and curr_time and prev_time != curr_time:
            penalty += 0.2 # Minor cost
            
        # 3. Entity Discontinuity (Cast Change)
        # Determine active characters in scene
        # We need a robust way to get chars. 'lines' -> CHARACTER type
        prev_chars = get_chars(prev)
        curr_chars = get_chars(curr)
        
        if not prev_chars or not curr_chars:
            # If explicit empty scene (landscape), low cost? Or high?
            # Assume strict change if empty.
            pass 
        else:
            # Jaccard Similarity: Intersection / Union
            intersection = prev_chars.intersection(curr_chars)
            union = prev_chars.union(curr_chars)
            
            jaccard = len(intersection) / len(union)
            
            # Cost is inverse of similarity
            # If Jaccard is 1.0 (Same people), Cost 0.0
            # If Jaccard is 0.0 (Total stranger), Cost 0.4
            
            char_cost = (1.0 - jaccard) * 0.4
            penalty += char_cost
            
        scores.append(round(min(1.0, penalty), 3))
        
    return scores

def get_loc(heading):
    # Strip INT/EXT and TIME
    # "INT. HOUSE - DAY" -> "HOUSE"
    parts = heading.upper().replace('INT.', '').replace('EXT.', '').split('-')[0]
    return parts.strip()

def get_time(heading):
    h = heading.upper()
    if 'DAY' in h: return 'DAY'
    if 'NIGHT' in h: return 'NIGHT'
    return None

def get_chars(scene):
    chars = set()
    for line in scene['lines']:
        if line['tag'] == 'C':
            name = line['text'].split('(')[0].strip()
            if name:
                chars.add(name)
    return chars
