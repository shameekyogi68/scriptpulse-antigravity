"""
ScriptPulse Syntactic Agent (IEEE SOTA Layer)
Gap Solved: "Bag of Words Fallacy"

Calculates Syntactic Complexity (Clause Density) as a proxy for Tree Depth.
Rationale: Deeply nested sentences (e.g., "The man who knew...") require more working memory
than flat sentences, even if entropy is identical.

Implementation: Heuristic Clause Detection (Regex-based).
Avoids heavy NLP dependencies (Spacy) for portability while maintaining high correlation.
"""

import re
import statistics

def run(data):
    """
    Calculate Syntactic Complexity for each scene.
    
    Returns:
        List of float (Complexity scores 0.0-1.0)
    """
    scenes = data.get('scenes', [])
    complexity_scores = []
    
    # Clause markers (Subordinating conjunctions & Relative pronouns)
    # These signal nesting/recursion in English syntax.
    patterns = [
        r'\bwhich\b', r'\bthat\b', r'\bwho\b', r'\bwhom\b', r'\bwhose\b', # Relative
        r'\bbecause\b', r'\balthough\b', r'\bif\b', r'\bwhile\b', r'\bwhen\b', # Subordinating
        r'\bunitl\b', r'\bunless\b', r'\bsince\b', r'\bwhereas\b',
        r'[,;]\s*and\b', r'[,;]\s*but\b' # Compound
    ]
    regex = re.compile('|'.join(patterns), re.IGNORECASE)
    
    for scene in scenes:
        lines = [l['text'] for l in scene['lines']]
        if not lines:
            complexity_scores.append(0.0)
            continue
            
        scene_scores = []
        for line in lines:
            # Count clause markers
            matches = len(regex.findall(line))
            
            # Count punctuation (commas often delimit clauses)
            commas = line.count(',')
            
            # Simple Proxy for Tree Depth:
            # Depth ≈ 1 + (Markers * 0.5) + (Commas * 0.2)
            depth_proxy = 1.0 + (matches * 0.8) + (commas * 0.2)
            
            # Penalize length (long sentences with no structure are hard too)
            words = len(line.split())
            if words > 20: 
                depth_proxy += (words - 20) * 0.05
                
            scene_scores.append(depth_proxy)
            
        # Scene score is the average depth of its sentences
        avg_depth = statistics.mean(scene_scores) if scene_scores else 1.0
        
        # Normalize: Typical depth range 1.0 - 4.0
        # Scale to 0.0 - 1.0
        norm_score = max(0.0, min(1.0, (avg_depth - 1.0) / 3.0))
        complexity_scores.append(norm_score)
        
    return complexity_scores
