"""
ScriptPulse Feature Engineering Module
Formal feature extraction for ML models.
"""

import numpy as np
from collections import Counter

def extract_features(scenes, report_data):
    """
    Extract formal feature vector for each scene.
    
    Args:
        scenes: List of scene dicts with 'lines'
        report_data: Full analysis report with temporal, valence, etc.
        
    Returns:
        numpy array of shape [N_scenes, 7] where each row is:
        [dialogue_ratio, sentiment_variance, lexical_diversity, 
         character_count, semantic_coherence, syntactic_complexity, action_density]
    """
    
    features = []
    
    for i, scene in enumerate(scenes):
        # X1: Dialogue ratio
        total_lines = len(scene['lines'])
        dialogue_lines = sum(1 for l in scene['lines'] if l.get('tag') == 'D')
        dialogue_ratio = dialogue_lines / total_lines if total_lines > 0 else 0
        
        # X2: Sentiment variance (from valence scores)
        valence_scores = report_data.get('valence_scores', [])
        if i < len(valence_scores) and i > 0:
            # Variance of valence in this scene and neighbors
            window = valence_scores[max(0, i-1):min(len(valence_scores), i+2)]
            sentiment_variance = np.var(window) if window else 0
        else:
            sentiment_variance = 0
        
        # X3: Lexical diversity
        all_words = []
        for line in scene['lines']:
            if line.get('tag') in ['D', 'A']:
                all_words.extend(line.get('text', '').lower().split())
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        lexical_diversity = unique_words / total_words if total_words > 0 else 0
        
        # X4: Character count
        characters = set()
        for line in scene['lines']:
            if line.get('tag') == 'C':
                characters.add(line.get('text', ''))
        character_count = len(characters)
        
        # X5: Semantic coherence (simplified: word overlap with previous scene)
        if i > 0:
            prev_words = set()
            for line in scenes[i-1]['lines']:
                if line.get('tag') in ['D', 'A']:
                    prev_words.update(line.get('text', '').lower().split())
            
            curr_words = set(all_words)
            if prev_words and curr_words:
                overlap = len(prev_words & curr_words)
                union = len(prev_words | curr_words)
                semantic_coherence = overlap / union if union > 0 else 0
            else:
                semantic_coherence = 0
        else:
            semantic_coherence = 1.0  # First scene has perfect coherence
        
        # X6: Syntactic complexity (avg sentence length)
        sentence_lengths = []
        for line in scene['lines']:
            if line.get('tag') == 'D':
                text = line.get('text', '')
                words = text.split()
                sentence_lengths.append(len(words))
        
        syntactic_complexity = np.mean(sentence_lengths) if sentence_lengths else 0
        
        # X7: Action density
        action_lines = sum(1 for l in scene['lines'] if l.get('tag') == 'A')
        action_density = action_lines / total_lines if total_lines > 0 else 0
        
        # Combine into feature vector
        feature_vector = [
            dialogue_ratio,
            sentiment_variance,
            lexical_diversity,
            character_count,
            semantic_coherence,
            syntactic_complexity,
            action_density
        ]
        
        features.append(feature_vector)
    
    return np.array(features)


def get_feature_names():
    """Return list of feature names for documentation."""
    return [
        'dialogue_ratio',
        'sentiment_variance',
        'lexical_diversity',
        'character_count',
        'semantic_coherence',
        'syntactic_complexity',
        'action_density'
    ]
