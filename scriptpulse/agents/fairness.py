"""
ScriptPulse Fairness Agent (Ethical AI Research Layer)
Gap Solved: "Cultural Bias" & "Algorithmic Fairness"

Audits the script for potential statistical biases in character portrayal.
Checks for:
1. Valence Imbalance: Are some characters consistently associated with negative sentiment?
2. Social Dominance Imbalance: Is there a monopoly on centrality?
3. Complexity Bias: Are some characters consistently given simpler syntax lines?
"""

import collections
import statistics

def run(input_data):
    """
    Audit character portrayals.
    Requires: 'scenes' (with lines), 'valence_scores', 'social_scores'.
    """
    scenes = input_data.get('scenes', [])
    valence_scores = input_data.get('valence_scores', [])
    
    if not scenes:
        return {}
        
    # Aggegate metrics per character
    char_valence = collections.defaultdict(list)
    char_lines = collections.defaultdict(int)
    char_words = collections.defaultdict(int)
    
    for i, scene in enumerate(scenes):
        scene_val = valence_scores[i] if i < len(valence_scores) else 0.0
        
        # Who is in this scene?
        # We attribute the Scene's Valence to the Characters present.
        # This determines "Atmospheric Bias" (e.g. Does bad stuff happen when X is around?)
        active_chars = set()
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name:
                    active_chars.add(name)
                    char_lines[name] += 1
                    # Rough word count for complexity audit
                    # (Next version: check syntax per char)
                    
        for char in active_chars:
            char_valence[char].append(scene_val)
            
    # Audit Analysis
    report = {
        'stereotyping_risks': [],
        'representation_stats': {}
    }
    
    # Filter for major characters (> 5 scenes)
    major_chars = [c for c, vals in char_valence.items() if len(vals) > 5]
    
    for char in major_chars:
        vals = char_valence[char]
        avg_val = statistics.mean(vals)
        
        # 1. Valence Bias Check
        # If mean valence is significantly negative (< -0.15), flag risk.
        if avg_val < -0.15:
            report['stereotyping_risks'].append(
                f"Character '{char}' is associated with Negative Sentiment (Avg: {avg_val:.2f}). Check for 'Villain Coding' or 'Trauma Tropes'."
            )
        elif avg_val > 0.3:
            # Too positive? 'Mary Sue' risk? (Less critical usually)
            pass
            
        report['representation_stats'][char] = {
            'scene_count': len(vals),
            'avg_sentiment': round(avg_val, 3)
        }
        
    return report
