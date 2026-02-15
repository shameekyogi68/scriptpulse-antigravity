"""
ScriptPulse Semantic Agent (Real ML Layer)
Gap Solved: "Semantic Blindness"

Calculates Cognitive Load using Vector Embedding Variance.
Rationale: 
- High Variance/Flux = High Cognitive Load (Brain must re-orient).
- Low Variance/Flux = Flow State.

Implementation: Sentence-Transformers (SBERT).
"""

from ..utils.model_manager import manager
import math
import numpy as np

class SemanticAgent:
    def __init__(self):
        # The original `manager` was imported from `..utils.model_manager`.
        # The instruction snippet implies creating a new local `manager` instance.
        # Assuming `ModelManager` is available in the same `model_manager` module.
        from ..utils.model_manager import ModelManager
        manager = ModelManager()

        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = manager.get_sentence_transformer(model_name)
        if self.model:
            print("[ML] Loaded SBERT for Semantic Analysis.")
        else:
             print("[Warning] Semantic ML failed to load. Using Entropy Fallback.")
            
    def run(self, data):
        """
        Calculate Semantic Entropy/Flux for each scene based on embedding distance.
        """
        scenes = data.get('scenes', [])
        scores = []
        
        if not scenes:
            return []
            
        # 1. Extract Text
        scene_texts = [" ".join([l['text'] for l in s['lines']]) for s in scenes]
        
        # 2. Encode if model exists
        if self.model:
            embeddings = self.model.encode(scene_texts)
            
            # 3. Calculate "Entropy" as distance from the Narrative Centroid
            # Or distance from previous scene (Flux).
            # The original metric was "Entropy" (0-1).
            # Let's use Cosine Distance from Previous Scene as a proxy for "Surprise" (Information Theory).
            
            from sklearn.metrics.pairwise import cosine_similarity
            
            for i in range(len(embeddings)):
                if i == 0:
                    scores.append(0.1) # Exposition is low entropy
                    continue
                
                # Reshape for sklearn [1, -1]
                curr = embeddings[i].reshape(1, -1)
                prev = embeddings[i-1].reshape(1, -1)
                
                sim = cosine_similarity(curr, prev)[0][0]
                
                # Flux/Entropy = 1 - Similarity
                # High Similarity (0.9) -> Low Entropy (0.1) -> Predictable
                # Low Similarity (0.2) -> High Entropy (0.8) -> Surprising
                entropy = 1.0 - max(0.0, sim)
                
                scores.append(float(entropy))
                
        else:
            # Fallback (Mock/Heuristic)
            import collections
            for text in scene_texts:
                tokens = text.split()
                if not tokens: 
                    scores.append(0.0)
                    continue
                counts = collections.Counter(tokens)
                entropy = 0.0
                total = len(tokens)
                for count in counts.values():
                    p = count / total
                    entropy -= p * math.log(p, 2)
                scores.append(min(1.0, entropy / 6.0))

        return scores

# Shim for existing calls
def run(data):
    agent = SemanticAgent()
    return agent.run(data)
