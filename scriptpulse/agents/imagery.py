"""
ScriptPulse Imagery Agent (Multimodal Research Layer)
Gap Solved: "Visual Blindness"

Quantifies "Visual Density" (Cinematic Load) by detecting high-imagery lexicons.
Rationale: A scene with "red neon", "shattered glass", and "glimmering steel" 
requires more cognitive visualization effort than "a room".
"""

def run(data):
    """
    Calculate Visual Density Score for each scene.
    Returns list of floats 0.0-1.0.
    """
    scenes = data.get('scenes', [])
    
    # Lexicons of High-Visual-Impact words
    # Source: Cinematic descriptive norms
    
    colors = {
        'red', 'blue', 'green', 'black', 'white', 'yellow', 'crimson', 'azure', 
        'neon', 'dark', 'bright', 'shadow', 'light', 'grey', 'purple', 'silver', 'gold'
    }
    
    optics = {
        'fade', 'cut', 'dissolve', 'zoom', 'pan', 'tilt', 'focus', 'blur', 
        'glimpse', 'stare', 'look', 'watch', 'see', 'view', 'angle', 'shot', 'pov'
    }
    
    textures = {
        'rough', 'smooth', 'slick', 'wet', 'dry', 'dusty', 'dirty', 'clean', 
        'pristine', 'shattered', 'broken', 'rusty', 'metallic', 'glass', 'wood'
    }
    
    kinetics = {
        'run', 'jump', 'fall', 'crash', 'explode', 'shatter', 'sprint', 
        'crawl', 'fly', 'drive', 'spin', 'roll', 'slide', 'hit', 'punch'
    }
    
    scores = []
    
    for scene in scenes:
        text = " ".join([l['text'] for l in scene['lines']]).lower()
        words = text.replace('.', '').replace(',', '').split()
        
        if not words:
            scores.append(0.0)
            continue
            
        hits = 0
        for w in words:
            if w in colors or w in optics or w in textures or w in kinetics:
                hits += 1
                
        # Density = Hits / Total Words
        # Normalization: 10% imagery density is very high for a script.
        # Scale: 0.0 -> 0.15 maps to 0.0 -> 1.0
        
        density = hits / len(words)
        normalized = min(1.0, density / 0.15)
        
        scores.append(normalized)
        
    return scores
