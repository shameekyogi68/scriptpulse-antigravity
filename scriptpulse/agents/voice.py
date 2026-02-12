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
                pass 
    
    # Better Aggregation: State Machine
    current_char = None
    for scene in scenes:
        for line in scene['lines']:
            if line['tag'] == 'C':
                current_char = line['text'].split('(')[0].strip()
            elif line['tag'] == 'D' and current_char:
                char_text[current_char].append(line['text'])
    
    # v13.1: Also try to find character names from 'character' tags (new parser)
    current_char = None
    for scene in scenes:
        for line in scene.get('lines', []):
            tag = line.get('tag', '')
            if tag in ('C', 'character'):
                current_char = line['text'].split('(')[0].strip()
            elif tag in ('D', 'dialogue') and current_char:
                if current_char not in char_text or line['text'] not in char_text[current_char]:
                    char_text[current_char].append(line['text'])
                
    # 2. Analyze Metrics
    fingerprints = {}
    
    # Lexicons for Agency
    active_verbs = {'run', 'hit', 'take', 'jump', 'decide', 'make', 'fight', 'stop', 'go', 'grab'}
    passive_markers = {'was', 'by', 'is', 'are', 'were', 'had', 'been'}
    
    # v13.1: Process ALL characters (minimum 1 line), with confidence flag
    for char, texts in char_text.items():
        if not texts:
            continue
            
        full_text = " ".join(texts).lower()
        words = full_text.split()
        if not words: continue
        
        # Confidence based on sample size
        if len(texts) >= 10:
            confidence = 'high'
        elif len(texts) >= 5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # A. Complexity (Avg Words per Line + Unique Word Ratio)
        avg_len = sum(len(t.split()) for t in texts) / len(texts)
        unique_ratio = len(set(words)) / len(words) if len(words) > 0 else 0
        complexity = (min(1.0, avg_len/20.0) + min(1.0, unique_ratio/0.6)) / 2
        
        # B. Positivity
        pos_words = {'good', 'love', 'yes', 'great', 'happy', 'safe', 'hope'}
        neg_words = {'bad', 'no', 'hate', 'die', 'kill', 'fear', 'pain'}
        pos = sum(1 for w in words if w in pos_words)
        neg = sum(1 for w in words if w in neg_words)
        total_aff = pos + neg
        positivity = (pos - neg) / total_aff if total_aff > 0 else 0.0
        
        # C. Agency (Active Verbs Ratio)
        active = sum(1 for w in words if w in active_verbs)
        passive = sum(1 for w in words if w in passive_markers)
        total_verbs = active + passive
        agency = (active - passive) / max(1, total_verbs)
        
        # D. v13.1: Punctuation rate (useful even for 1 line)
        punct_count = sum(1 for c in full_text if c in '!?...,;:')
        punct_rate = round(punct_count / max(1, len(words)), 3)
        
        fingerprints[char] = {
            'complexity': round(complexity, 2),
            'positivity': round(positivity, 2),
            'agency': round(agency, 2),
            'line_count': len(texts),
            'fingerprint_confidence': confidence,
            'punctuation_rate': punct_rate
        }
        
    return fingerprints
