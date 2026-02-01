"""
ScriptPulse Valence Agent (Affective Research Layer)
Gap Solved: "Emotional Blindness" (Arousal vs Valence)

Determines the emotional polarity (Positive/Negative) of each scene.
Used in conjunction with Temporal Effort (Arousal) to map scenes to
Russell's Circumplex Model of Affect:
- High Effort + Neg = Anxiety (Terror/Stress)
- High Effort + Pos = Excitement (Joy/Victory)
- Low Effort + Neg = Depression (Boredom)
- Low Effort + Pos = Relaxation (Flow)
"""

def run(data):
    """
    Calculate Valence Score (-1.0 to +1.0) for each scene.
    """
    scenes = data.get('scenes', [])
    scores = []
    
    # Lexicons (Simplified ANEW / VADER style)
    # Positive: Success, Love, Joy, Safety, Light
    positive_words = {
        'love', 'good', 'great', 'happy', 'joy', 'smile', 'laugh', 'light', 
        'sun', 'win', 'success', 'safe', 'calm', 'peace', 'hope', 'kiss', 
        'hug', 'beautiful', 'bright', 'yes', 'victory', 'friend', 'warm', 
        'soft', 'sweet', 'free', 'glory', 'alive', 'proud', 'brave', 'trust', 
        'rich', 'fun', 'party', 'dance', 'music', 'sing', 'heal', 'kiss'
    }
    
    # Negative: Danger, Pain, Fear, Loss, Dark
    negative_words = {
        'bad', 'dark', 'dead', 'death', 'kill', 'gun', 'blood', 'pain', 
        'hurt', 'cry', 'scream', 'fear', 'afraid', 'run', 'break', 'shatter', 
        'crash', 'fight', 'hate', 'enemy', 'trap', 'lose', 'fail', 'cold', 
        'sick', 'ill', 'sad', 'empty', 'alone', 'lost', 'danger', 'risk', 
        'hell', 'murder', 'corpse', 'evil', 'cruel', 'ugly', 'no', 'stop', 
        'lie', 'betray', 'monster', 'ghost', 'shadow'
    }
    
    for scene in scenes:
        text = " ".join([l['text'] for l in scene['lines']]).lower()
        words = text.replace('.', '').replace(',', '').split()
        
        if not words:
            scores.append(0.0)
            continue
            
        pos_hits = 0
        neg_hits = 0
        
        for w in words:
            if w in positive_words: pos_hits += 1
            if w in negative_words: neg_hits += 1
            
        total_hits = pos_hits + neg_hits
        
        if total_hits == 0:
            scores.append(0.0) # Neutral
            continue
            
        # Valence Ratio (-1.0 to 1.0)
        # If all pos: 1.0
        # If all neg: -1.0
        # Mixed: somewhere in between
        
        raw_valence = (pos_hits - neg_hits) / total_hits
        
        # Scaling by density? 
        # A scene with 1 pos word and 0 neg is 1.0, but weak.
        # A scene with 10 pos words and 0 neg is 1.0, and strong.
        # We should weight by density slightly.
        
        density = total_hits / len(words)
        # Boost confidence if density is high
        confidence = min(1.0, density / 0.05) # 5% emotional words is high
        
        final_valence = raw_valence * confidence
        
        scores.append(round(final_valence, 3))
        
    return scores
