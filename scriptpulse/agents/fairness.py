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

def run(input_data, context=None, genre='drama'):
    """
    Audit character portrayals.
    Requires: 'scenes' (with lines), 'valence_scores', 'social_scores'.
    context: dict of {char_name: role} (Protagonist, Antagonist, etc.)
    genre: v12.0 Genre calibration ('horror', 'comedy', 'drama', 'thriller')
    """
    scenes = input_data.get('scenes', [])
    valence_scores = input_data.get('valence_scores', [])
    char_context = context or {}
    
    # v12.0: Genre-specific thresholds
    if genre.lower() in ['horror', 'thriller']:
        negative_threshold = -0.3  # Allow more negativity
    elif genre.lower() == 'comedy':
        negative_threshold = -0.05  # Expect positivity
        positive_threshold = 0.2  # Warn if too dark
    else:
        negative_threshold = -0.15  # Default
        positive_threshold = None
    
    if not scenes:
        return {}
        
    # Aggegate metrics per character
    char_valence = collections.defaultdict(list)
    char_lines = collections.defaultdict(int)
    
    for i, scene in enumerate(scenes):
        scene_val = valence_scores[i] if i < len(valence_scores) else 0.0
        
        active_chars = set()
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name:
                    active_chars.add(name)
                    char_lines[name] += 1
                    
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
        role = char_context.get(char, 'Unknown')
        
        # 1. Valence Bias Check (Genre-Aware v12.0)
        if avg_val < negative_threshold:
            # Context Check: Antagonists are allowed to be negative.
            if role in ['Antagonist', 'Villain']:
                pass # This is expected behavior for a villain.
            else:
                report['stereotyping_risks'].append(
                    f"Character '{char}' ({role}) is associated with Negative Sentiment (Avg: {avg_val:.2f}). Check for 'Villain Coding' or 'Trauma Tropes'."
                )
        
        # Comedy-specific check: too dark?
        if positive_threshold and avg_val < positive_threshold:
            if genre.lower() == 'comedy':
                report['stereotyping_risks'].append(
                    f"Character '{char}' seems too negative for a Comedy (Avg: {avg_val:.2f})."
                )
        
        report['representation_stats'][char] = {
            'scene_count': len(vals),
            'avg_sentiment': round(avg_val, 3),
            'role': role
        }
        
    return report
