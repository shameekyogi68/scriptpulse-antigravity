"""
ScriptPulse Hybrid NLP Agent (Modern Research Layer)
Gap Solved: "Antiquated NLP" vs "Modern Embeddings"

Calculates 'Semantic Flux' using Vector Embeddings.
- High Flux = Rapid thematic shifting (Disorientation)
- Low Flux = Thematic consistency (Focus)

Architecture:
1. Tries to load `sentence-transformers` (SBERT).
2. Fallback: Uses Jaccard Similarity on N-Grams (Pure Python Proxy).
"""

import math

def run(data):
    """
    Calculate Semantic Flux (1 - Similarity) between consecutive scenes.
    """
    scenes = data.get('scenes', [])
    scores = []
    
    # Try SBERT (Modern Standard via Manager)
    model = None
    try:
        from ..utils.model_manager import ModelManager
        from sentence_transformers import util
        manager = ModelManager()

        model = manager.get_sentence_transformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:

        pass

        
    for i in range(len(scenes)):
        if i == 0:
            scores.append(0.0) # No previous scene
            continue
            
        curr_text = " ".join([l['text'] for l in scenes[i]['lines']])
        prev_text = " ".join([l['text'] for l in scenes[i-1]['lines']])
        
        normalized_flux = 0.0
        
        if model:
            # SBERT Method (IEEE Gold Standard)
            emb1 = model.encode(curr_text, convert_to_tensor=True)
            emb2 = model.encode(prev_text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(emb1, emb2).item()
            # Flux = 1 - Similarity
            normalized_flux = 1.0 - max(0.0, similarity)
            
        else:
            # Fallback: N-Gram Jaccard (Robust Proxy)
            # Bag of bigrams
            def get_bigrams(text):
                words = text.lower().replace('.', '').split()
                return set(zip(words, words[1:]))
                
            b1 = get_bigrams(curr_text)
            b2 = get_bigrams(prev_text)
            
            if not b1 or not b2:
                normalized_flux = 1.0 # Max Change if empty
            else:
                intersection = len(b1.intersection(b2))
                union = len(b1.union(b2))
                jaccard = intersection / union if union > 0 else 0.0
                normalized_flux = 1.0 - jaccard
                
        scores.append(round(normalized_flux, 3))
        
    return scores
