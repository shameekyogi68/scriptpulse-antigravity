"""Scene Segmentation Agent - Conservative Boundary Detection"""


# Configuration
MIN_SCENE_LENGTH = 3  # Minimum lines per scene to prevent micro-scenes
LOW_CONFIDENCE_THRESHOLD = 0.6  # Threshold for merging adjacent scenes


def run(input_data):
    """
    Segment parsed lines into scenes conservatively.
    
    Args:
        input_data: List of dicts from parsing agent with line_index, text, tag
        
    Returns:
        List of scene dicts with scene_index, start_line, end_line, boundary_confidence
    """
    if not input_data:
        return []
    
    # Step 1: Detect potential boundaries
    boundaries = detect_boundaries(input_data)
    
    # Step 2: Create initial scenes
    scenes = create_scenes(input_data, boundaries)
    
    # Step 3: Apply minimum scene length constraint
    scenes = enforce_minimum_length(scenes, input_data)
    
    # Step 4: Merge low-confidence adjacent scenes
    scenes = merge_low_confidence(scenes)
    
    # Step 5: Re-index scenes
    scenes = reindex_scenes(scenes)
    
    return scenes


def detect_boundaries(parsed_lines):
    """
    Detect potential scene boundaries based on structural cues.
    
    Returns list of (line_index, confidence) tuples.
    """
    boundaries = [(0, 1.0)]  # First line always starts a scene
    
    for i, line_data in enumerate(parsed_lines):
        if i == 0:
            continue
        
        tag = line_data['tag']
        text = line_data['text'].strip()
        
        confidence = 0.0
        
        # Strong signal: Scene heading (S tag)
        if tag == 'S':
            confidence = 0.9
        
        # Weak signal: Metadata/transitions
        elif tag == 'M':
            confidence = 0.4
        
        # Only add if confidence is above threshold
        if confidence > 0.3:
            boundaries.append((i, confidence))
    
    return boundaries


def create_scenes(parsed_lines, boundaries):
    """
    Create initial scene objects from boundaries.
    """
    scenes = []
    
    for i in range(len(boundaries)):
        start_line = boundaries[i][0]
        start_confidence = boundaries[i][1]
        
        # Determine end line
        if i + 1 < len(boundaries):
            end_line = boundaries[i + 1][0] - 1
        else:
            end_line = len(parsed_lines) - 1
        
        scenes.append({
            'scene_index': i,
            'start_line': start_line,
            'end_line': end_line,
            'boundary_confidence': start_confidence
        })
    
    return scenes


def enforce_minimum_length(scenes, parsed_lines):
    """
    Merge scenes that are below minimum length.
    
    Conservative approach: when uncertain, prefer fewer scenes.
    """
    if not scenes:
        return scenes
    
    merged = []
    skip_next = False
    
    for i in range(len(scenes)):
        if skip_next:
            skip_next = False
            continue
        
        scene = scenes[i]
        scene_length = scene['end_line'] - scene['start_line'] + 1
        
        # If scene is too short, try to merge with next
        if scene_length < MIN_SCENE_LENGTH and i + 1 < len(scenes):
            # Merge with next scene
            next_scene = scenes[i + 1]
            merged_scene = {
                'scene_index': scene['scene_index'],
                'start_line': scene['start_line'],
                'end_line': next_scene['end_line'],
                'boundary_confidence': min(scene['boundary_confidence'], 
                                          next_scene['boundary_confidence'])
            }
            merged.append(merged_scene)
            skip_next = True
        else:
            merged.append(scene)
    
    return merged


def merge_low_confidence(scenes):
    """
    Merge adjacent scenes with low boundary confidence.
    
    This is the critical anti-over-segmentation step.
    """
    if len(scenes) <= 1:
        return scenes
    
    merged = []
    current = scenes[0]
    
    for i in range(1, len(scenes)):
        next_scene = scenes[i]
        
        # If current ends with low confidence, merge with next
        if current['boundary_confidence'] < LOW_CONFIDENCE_THRESHOLD:
            # Merge
            current = {
                'scene_index': current['scene_index'],
                'start_line': current['start_line'],
                'end_line': next_scene['end_line'],
                'boundary_confidence': max(current['boundary_confidence'],
                                          next_scene['boundary_confidence'])
            }
        else:
            # Keep current, move to next
            merged.append(current)
            current = next_scene
    
    # Don't forget the last scene
    merged.append(current)
    
    return merged


def reindex_scenes(scenes):
    """Re-index scenes sequentially after merging."""
    for i, scene in enumerate(scenes):
        scene['scene_index'] = i
    return scenes

