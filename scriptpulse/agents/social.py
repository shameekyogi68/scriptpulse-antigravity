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
   
v11.0 Update: Calculates Interaction Map (Pairwise Co-occurrence) for Chemistry Heatmap.
"""

import math
import collections

def get_chars(scene):
    chars = set()
    for line in scene['lines']:
        if line['tag'] == 'C':
            name = line['text'].split('(')[0].strip()
            if name:
                chars.add(name)
    return chars

def run(data):
    """
    Calculate Social Tension (Centrality Entropy) per scene.
    Returns dict: {'centrality_entropy': [], 'interaction_map': {}}
    """
    scenes = data.get('scenes', [])
    entropy_trace = []
    
    # v11.0: Interaction Heatmap (Chemistry Matrix)
    # Map: "CharA|CharB" -> [scene_index, scene_index, ...]
    interaction_map = collections.defaultdict(list) 
    
    for i, scene in enumerate(scenes):
        lines = scene['lines']
        
        # 0. Chemistry: Who is in this scene?
        chars_in_scene = sorted(list(get_chars(scene)))
        if len(chars_in_scene) >= 2:
            for k in range(len(chars_in_scene)):
                for j in range(k+1, len(chars_in_scene)):
                    c1 = chars_in_scene[k]
                    c2 = chars_in_scene[j]
                    pair = f"{c1}|{c2}"
                    interaction_map[pair].append(scene['scene_index'])
        
        # 1. Build Turn-Taking Graph (for Entropy)
        speakers = []
        for line in lines:
            if line['tag'] == 'C':
                # clean "(V.O.)" etc
                name = line['text'].split('(')[0].strip()
                if name:
                    speakers.append(name)
                    
        if len(speakers) < 2:
            entropy_trace.append(0.0) # No social interaction
            continue
            
        # Edges: Speaker A -> Speaker B
        # Undirected for simplicity of "Connection"
        degree_map = collections.defaultdict(int)
        
        for k in range(len(speakers) - 1):
            s1 = speakers[k]
            s2 = speakers[k+1]
            if s1 != s2:
                degree_map[s1] += 1
                degree_map[s2] += 1
                
        # 2. Calculate Centrality Distribution
        total_degrees = sum(degree_map.values())
        if total_degrees == 0:
            entropy_trace.append(0.0)
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
            
        entropy_trace.append(norm_entropy)
        
    return {
        'centrality_entropy': entropy_trace,
        'interaction_map': dict(interaction_map)
    }
