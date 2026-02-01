"""
ScriptPulse Semantic Agent (IEEE Research Layer)
Gap Solved: "Semantic Blindness"

Calculates Cognitive Load using Information Theoretic Entopy (Shannon Entropy).
Rationale: Higher entropy = higher unpredictability = higher cognitive processing cost.

Pure Python implementation. Zero ML dependencies.
"""

import math
import collections
import re

def run(data):
    """
    Calculate Semantic Entropy for each scene.
    
    Args:
        data: Dict containing 'scenes' (from segmentation)
        
    Returns:
        List of float (Entropy scores 0.0-1.0)
    """
    scenes = data.get('scenes', [])
    entropy_scores = []
    
    for scene in scenes:
        # 1. Extract Text
        lines = [l['text'] for l in scene['lines']]
        text = " ".join(lines).lower()
        
        # 2. Tokenize (Simple regex)
        tokens = re.findall(r'\b\w+\b', text)
        
        if not tokens:
            entropy_scores.append(0.0)
            continue
            
        # 3. Calculate Shannon Entropy
        # H = -sum(p(x) * log2(p(x)))
        total_tokens = len(tokens)
        counts = collections.Counter(tokens)
        
        entropy = 0.0
        for count in counts.values():
            p = count / total_tokens
            entropy -= p * math.log2(p)
            
        # 4. Normalize
        # Max entropy for N unique tokens is log2(N)
        # However, for text, we normalize against a theoretical max to keep it 0-1
        # A very dense scene might have entropy ~5-6 bits/word. 
        # We clamp/scale it.
        
        # Scale: 0.0 (Repetitive) -> 6.0 (High Density)
        # We normalize to 0.0 -> 1.0 range based on typical prose max ~6.0
        normalized_entropy = min(1.0, entropy / 6.0)
        
        entropy_scores.append(normalized_entropy)
        
    return entropy_scores
