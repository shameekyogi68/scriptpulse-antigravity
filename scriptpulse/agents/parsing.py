"""Structural Parsing Agent - Format-Only Classification"""

import re


def run(input_data):
    """
    Classify screenplay lines by format only.
    
    Args:
        input_data: Raw screenplay text (string)
        
    Returns:
        List of dicts with line_index, text, and tag (S/A/D/C/M)
    """
    lines = input_data.split('\n')
    result = []
    
    for i, line in enumerate(lines):
        tag = classify_line(line, i, lines)
        result.append({
            'line_index': i,
            'text': line,
            'tag': tag
        })
    
    return result


def classify_line(line, index, all_lines):
    """
    Classify a single line by format cues only.
    
    Tags:
    - S: Scene heading (INT./EXT. lines)
    - A: Action/description
    - D: Dialogue
    - C: Character name
    - M: Metadata/transition (FADE, CUT, etc.)
    
    Args:
        line: The line to classify
        index: Line index in script
        all_lines: All lines for context
        
    Returns:
        Single character tag
    """
    stripped = line.strip()
    
    # Empty lines → action (conservative default)
    if not stripped:
        return 'A'
    
    # Scene headings: INT./EXT. at start
    if is_scene_heading(stripped):
        return 'S'
    
    # Metadata: transitions like FADE OUT, CUT TO:
    if is_metadata(stripped):
        return 'M'
    
    # Character names: ALL CAPS followed by dialogue
    if is_character_name(stripped, index, all_lines):
        return 'C'
    
    # Dialogue: indented text after character name
    if is_dialogue(stripped, index, all_lines):
        return 'D'
    
    # Default: action/description
    return 'A'


def is_scene_heading(line):
    """
    Check if line is a scene heading by format.
    
    IMPROVED: Added fallback patterns for non-standard formats.
    """
    # Standard patterns: INT./EXT.
    standard_pattern = r'^(INT\.?/EXT\.?|INT\.?|EXT\.?)\s+'
    if re.match(standard_pattern, line, re.IGNORECASE):
        return True
    
    # Fallback patterns for non-standard formats
    fallback_patterns = [
        r'^INTERIOR\s+',        # Full word "INTERIOR"
        r'^EXTERIOR\s+',        # Full word "EXTERIOR"
        r'^I\.\s+',             # Abbreviated "I."
        r'^E\.\s+',             # Abbreviated "E."
        r'^SCENE\s*:',          # "SCENE:" prefix
        r'^SCENE\s+\d+',        # "SCENE 1" format
        r'^\d+\s*(INT|EXT)',    # Scene number before INT/EXT
    ]
    
    for pattern in fallback_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    
    # Check for location markers without INT/EXT (risky, lower priority)
    # Must have a dash and time of day indicator
    time_pattern = r'^[A-Z][A-Z\s]+\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)'
    if re.match(time_pattern, line, re.IGNORECASE):
        return True
    
    return False


def is_metadata(line):
    """Check if line is metadata/transition by format"""
    # Common transition markers
    transitions = [
        'FADE IN',
        'FADE OUT',
        'FADE TO',
        'CUT TO',
        'DISSOLVE TO',
        'MATCH CUT',
        'SMASH CUT',
        'THE END',
        'CONTINUED'
    ]
    
    upper_line = line.upper().strip()
    
    for trans in transitions:
        if trans in upper_line or upper_line.startswith(trans):
            return True
    
    # Lines ending with colon are often transitions
    if upper_line.endswith(':'):
        return True
    
    return False


def is_character_name(line, index, all_lines):
    """Check if line is a character name by format"""
    # Must be ALL CAPS
    if not line.isupper():
        return False
    
    # Too long to be character name (likely action in caps)
    if len(line.split()) > 5:
        return False
    
    # Check if followed by dialogue-like text
    if index + 1 < len(all_lines):
        next_line = all_lines[index + 1].strip()
        # If next line is indented or not all caps, likely dialogue follows
        if next_line and not next_line.isupper():
            return True
    
    return False


def is_dialogue(line, index, all_lines):
    """Check if line is dialogue by format"""
    # Must not be all caps (that would be character or action)
    if line.isupper():
        return False
    
    # Check if previous line was character name
    if index > 0:
        prev_line = all_lines[index - 1].strip()
        if prev_line and prev_line.isupper() and len(prev_line.split()) <= 5:
            return True
    
    # Check for parentheticals (character extensions or wrylies)
    if line.startswith('(') and ')' in line:
        return True
    
    return False

