"""
ScriptPulse Social Agent (Network Theory Research Layer)
Gap Solved: "Social Physics"

Quantifies "Social Tension" using Dynamic Network Analysis.
Method:
1. Builds a 'Interaction Graph' for each scene based on turn-taking.
2. Calculates Degree Centrality for all characters.
3. Computes 'Centrality Entropy' (Chaos vs Order).
   - High Entropy = Flat hierarchy (The Mob / Argument) = High Load.
   - Low Entropy = Steep hierarchy (Lecture / Order) = Low Load.
"""

import math
import collections

def run(data):
    """
    Calculate Social Tension (Centrality Entropy) per scene.
    """
    scenes = data.get('scenes', [])
    scores = []
    
    for scene in scenes:
        lines = scene['lines']
        
        # 1. Build Turn-Taking Graph
        speakers = []
        for line in lines:
            if line['tag'] == 'C':
                # clean "(V.O.)" etc
                name = line['text'].split('(')[0].strip()
                if name:
                    speakers.append(name)
                    
        if len(speakers) < 2:
            scores.append(0.0) # No social interaction
            continue
            
        # Edges: Speaker A -> Speaker B
        # Undirected for simplicity of "Connection"
        degree_map = collections.defaultdict(int)
        
        for i in range(len(speakers) - 1):
            s1 = speakers[i]
            s2 = speakers[i+1]
            if s1 != s2:
                degree_map[s1] += 1
                degree_map[s2] += 1
                
        # 2. Calculate Centrality Distribution
        total_degrees = sum(degree_map.values())
        if total_degrees == 0:
            scores.append(0.0)
            continue
            
        proportions = [d / total_degrees for d in degree_map.values()]
        
        # 3. Calculate Shannon Entropy of Centrality
        entropy = 0.0
        for p in proportions:
            if p > 0:
                entropy -= p * math.log2(p)
                
        # 4. Normalize
        # Max entropy for N speakers is log2(N).
        # We want a 0-1 score where 1.0 = Max Chaos.
        unique_speakers = len(degree_map)
        if unique_speakers > 1:
            max_entropy = math.log2(unique_speakers)
            norm_entropy = entropy / max_entropy
        else:
            norm_entropy = 0.0
            
        scores.append(norm_entropy)
        
    return scores
