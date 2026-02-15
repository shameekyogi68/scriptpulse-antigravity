"""
ScriptPulse Universal Format Normalizer
Preprocessing middleware to standardize messy or creative script formats.
"""
import re

def normalize_script(text):
    """
    Normalize script text to standard Screenplay format (mostly).
    
    Transformations:
    1. Headings: INT, EXT, INTERIOR, I/E -> INT. / EXT. (Uppercase)
    2. Dialogue: "NAME: Text" -> "NAME\nText"
    3. Formatting: Standardizes dashes, newlines.
    4. Characters: Attempts to uppercase mixed-case character names.
    """
    if not text:
        return ""
        
    # 1. Basic cleaning
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Split lines
    lines = text.split('\n')
    output_lines = []
    
    # Pre-compile regex
    # Headings: INT, EXT, I/E, etc. at start of line
    # Matches: "int. room", "Interior Room", "i/e car", "ext garden", "interior: house"
    re_heading = re.compile(r'^(INT|EXT|I\/E|INT\/EXT|EXT\/INT|INTERIOR|EXTERIOR)([:\.\s]|$)', re.IGNORECASE)

    
    # Transitions ending in TO:
    re_transition = re.compile(r'.* TO:$', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            output_lines.append("")
            continue
            
        # A. Detect Scene Headings
        match = re_heading.match(stripped)
        if match:
            # Found heading. Standardize.
            raw_prefix = match.group(1).upper()
            slug = stripped[len(match.group(0)):].strip()
            
            # Map variations
            if raw_prefix in ['INTERIOR']: prefix = 'INT.'
            elif raw_prefix in ['EXTERIOR']: prefix = 'EXT.'
            elif raw_prefix in ['INT', 'EXT']: prefix = raw_prefix + '.'
            elif raw_prefix in ['I/E']: prefix = 'I/E.'
            else: prefix = raw_prefix + '.' # Fallback
            
            # Ensure nice spacing
            # Force upper slug
            normalized = f"{prefix} {slug.upper()}"
            
            # Ensure double newline before headers (helps segmentation)
            if output_lines and output_lines[-1] != "":
                output_lines.append("")
                
            output_lines.append(normalized)
            continue
            
        # B. Detect "CHARACTER: Dialogue"
        # Logic: Starts with name, has colon, text follows.
        # Exclude "CUT TO:" (Transition)
        if re_transition.match(stripped):
            output_lines.append(stripped.upper())
            continue
            
        if ':' in stripped:
            parts = stripped.split(':', 1)
            char_part = parts[0].strip()
            dial_part = parts[1].strip()
            
            # Name heuristic: Shortish, mostly letters/spaces
            # (Allows "MR. SMITH" or "John")
            if 0 < len(char_part) < 30 and dial_part:
                # Treat as dialogue
                output_lines.append(char_part.upper())
                output_lines.append(dial_part)
                continue
                
        # C. Detect Mixed Case Character Cues
        # Heuristic: Short line without end punctuation, followed by text?
        # This is risky for "He runs" followed by "He jumps".
        # But critical for "John" followed by "Hello".
        
        # Check constraints:
        # 1. Not a heading (checked)
        # 2. Not a transition (checked)
        # 3. Short length (< 25 chars)
        # 4. No sentence-ending punctuation (., ?, !) unless it's an initial (J.T.)
        # 5. Looks name-y?
        
        is_upper = stripped.isupper()
        no_punct = not stripped.endswith(('.', '!', '?')) or stripped.endswith('.') and len(stripped)<5 # Allow "DR."
        
        if not is_upper and len(stripped) < 25 and no_punct:
             # It *mostly* looks like a name.
             # DANGER: "He runs" fits this.
             # Check for common action verbs? No, too complex.
             # Check if next line exists and is non-empty?
             # If next line is dialogue, this is character.
             
             # Lookahead
             has_dialogue_after = False
             if i + 1 < len(lines):
                 next_l = lines[i+1].strip()
                 if next_l:
                     has_dialogue_after = True
             
             if has_dialogue_after:
                 # We assume it's a character.
                 # "John" -> "JOHN"
                 # "He runs" -> "HE RUNS" (This becomes Character in parser... bad)
                 # But risk is acceptable for "Universal Tolerance".
                 # Better to capture characters than miss them and treat dialogue as action.
                 output_lines.append(stripped.upper())
                 continue
        
        # Default: Pass through
        output_lines.append(stripped)
        
    return "\n".join(output_lines)
