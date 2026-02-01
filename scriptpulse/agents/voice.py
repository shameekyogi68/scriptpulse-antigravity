"""
ScriptPulse Voice Agent (Market Professional Layer)
Gap Solved: "The Same-Sounding Character Problem"

Quantifies character linguistic distinctiveness using a 3D Vector:
1. Complexity (X): Vocabulary richness and sentence structure.
2. Positivity (Y): Emotional Valence.
3. Agency (Z): Active vs Passive verb usage.

Output is used to plot a "Voice Map" to see if characters overlap (Bad) or separate (Good).
"""

import collections
import statistics

def run(data):
    """
    Generate Voice Fingerprints for top characters.
    Requires: 'scenes' (with hydrated lines).
    """
    scenes = data.get('scenes', [])
    
    # 1. Aggregate Text per Character
    char_text = collections.defaultdict(list)
    char_lines = collections.defaultdict(int)
    
    for scene in scenes:
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name:
                    char_lines[name] += 1
            elif line['tag'] == 'D':
                # Attribute dialogue to the LAST seen character
                # (Simple heuristic, strictly relies on C-tag preceding D-tag)
                # Ideally 'parsing.py' would link them, but we scan backwards here or keep state
                pass 
    
    # Better Aggregation: State Machine
    current_char = None
    for scene in scenes:
        for line in scene['lines']:
            if line['tag'] == 'C':
                current_char = line['text'].split('(')[0].strip()
            elif line['tag'] == 'D' and current_char:
                char_text[current_char].append(line['text'])
                
    # 2. Analyze Metrics
    fingerprints = {}
    
    # Lexicons for Agency
    active_verbs = {'run', 'hit', 'take', 'jump', 'decide', 'make', 'fight', 'stop', 'go', 'grab'}
    passive_markers = {'was', 'by', 'is', 'are', 'were', 'had', 'been'}
    
    # Filter for characters with > 10 lines
    for char, texts in char_text.items():
        if len(texts) < 10:
            continue
            
        full_text = " ".join(texts).lower()
        words = full_text.split()
        if not words: continue
        
        # A. Complexity (Avg Words per Line + Unique Word Ratio)
        avg_len = sum(len(t.split()) for t in texts) / len(texts)
        unique_ratio = len(set(words)) / len(words)
        # Normalize: AvgLen 20 is high, Unique 0.5 is high
        complexity = (min(1.0, avg_len/20.0) + min(1.0, unique_ratio/0.6)) / 2
        
        # B. Positivity (Valence - Simple keyword match)
        # Re-using simplified valance lexicon for speed
        pos_words = {'good', 'love', 'yes', 'great', 'happy', 'safe', 'hope'}
        neg_words = {'bad', 'no', 'hate', 'die', 'kill', 'fear', 'pain'}
        pos = sum(1 for w in words if w in pos_words)
        neg = sum(1 for w in words if w in neg_words)
        total_aff = pos + neg
        # Scale -1 to 1
        positivity = (pos - neg) / total_aff if total_aff > 0 else 0.0
        
        # C. Agency (Active Verbs Ratio)
        active = sum(1 for w in words if w in active_verbs)
        passive = sum(1 for w in words if w in passive_markers)
        total_verbs = active + passive
        agency = (active - passive) / max(1, total_verbs) # -1 to 1
        
        fingerprints[char] = {
            'complexity': round(complexity, 2), # 0-1
            'positivity': round(positivity, 2), # -1 to 1
            'agency': round(agency, 2),         # -1 to 1
            'line_count': len(texts)
        }
        
    return fingerprints
