"""
Experimental Agent - Advanced Research & Experimental Modules
Consolidates: silicon_stanislavski.py, resonance.py, insight.py, polyglot_validator.py, multimodal.py
"""

import logging

from ..utils.model_manager import manager

logger = logging.getLogger('scriptpulse.experimental')

# =============================================================================
# SILICON STANISLAVSKI LOGIC (formerly silicon_stanislavski.py)
# =============================================================================

class SiliconStanislavskiAgent:
    """Methods for Believability & Actor Theory (Method Acting Simulation)"""
    
    def __init__(self):
        self.belief_state = {'safety': 0.8, 'trust': 0.8, 'agency': 0.5}
        self.classifier = manager.get_zero_shot()
        self.labels = ["danger", "safety", "deception", "trust", "helplessness", "control"]
        self.is_ml = self.classifier is not None
        
    def analyze_script(self, scenes_text):
        """
        Batch process all scenes using full-scene chunked inference.
        
        Previous approach truncated every scene to 1000 chars, missing 60-80%
        of scene content in long dialogue-heavy scenes. Now we:
        1. Split long scenes into 512-char chunks with 64-char overlap
        2. Run DeBERTa on each chunk
        3. Average the scores across chunks (ensemble-style aggregation)
        This gives accurate belief-state readings regardless of scene length.
        """
        results = []
        current_state = self.belief_state.copy()
        
        if not self.is_ml:
            for text in scenes_text:
                step_data = self._update_state(current_state, text, None)
                current_state = step_data['internal_state']
                results.append(step_data)
            return results

        # Build chunk lists per scene
        scene_chunks = []  # list of (scene_idx, [chunk_texts])
        for i, text in enumerate(scenes_text):
            if text and len(text) > 10:
                chunks = self._chunk_text(text, chunk_size=512, overlap=64)
                scene_chunks.append((i, chunks))

        # Flatten all chunks for a single batch call (fastest approach)
        flat_chunks = []
        flat_scene_ids = []  # which scene each chunk belongs to
        for scene_idx, chunks in scene_chunks:
            for chunk in chunks:
                flat_chunks.append(chunk)
                flat_scene_ids.append(scene_idx)

        # Single batched inference call
        flat_results = []
        if flat_chunks and self.classifier:
            try:
                flat_results = self.classifier(
                    flat_chunks, self.labels, multi_label=True, batch_size=8
                )
            except Exception as e:
                logger.error("Chunked batch inference failed: %s", e)
                self.is_ml = False
                for text in scenes_text:
                    step_data = self._update_state(current_state, text, None)
                    current_state = step_data['internal_state']
                    results.append(step_data)
                return results

        # Aggregate chunk results per scene (mean ensemble)
        from collections import defaultdict
        scene_label_scores = defaultdict(lambda: defaultdict(list))
        for chunk_result, scene_idx in zip(flat_results, flat_scene_ids):
            for label, score in zip(chunk_result['labels'], chunk_result['scores']):
                scene_label_scores[scene_idx][label].append(score)

        output_map = {}
        for scene_idx, label_score_lists in scene_label_scores.items():
            # Average scores across all chunks for this scene
            avg_scores = {label: sum(scores) / len(scores)
                          for label, scores in label_score_lists.items()}
            # Reconstruct the same format the classifier returns
            labels_sorted = sorted(avg_scores.keys(), key=lambda l: avg_scores[l], reverse=True)
            output_map[scene_idx] = {
                'labels': labels_sorted,
                'scores': [avg_scores[l] for l in labels_sorted]
            }

        # Build result list in order
        for i, text in enumerate(scenes_text):
            step_data = self._update_state(current_state, text, output_map.get(i))
            current_state = step_data['internal_state']
            results.append(step_data)
        return results

    @staticmethod
    def _chunk_text(text, chunk_size=512, overlap=64):
        """
        Split text into overlapping character chunks.
        Overlap ensures boundary context is not lost between chunks.
        """
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks

    def _update_state(self, state, text, ml_result=None):
        new_state = state.copy()
        method = "Keyword Heuristic (Fallback)"
        scores = {}
        confidence = 0.5  # Default confidence for heuristic
        
        if ml_result:
            method = "Zero-Shot Classification (DeBERTa-v3)"
            scores = {label: score for label, score in zip(ml_result['labels'], ml_result['scores'])}
            # Use top score as a confidence proxy
            confidence = max(scores.values()) if scores else 0.5
            
            new_state['safety'] = max(0.0, min(1.0, new_state['safety'] + (scores.get('safety', 0) - scores.get('danger', 0)) * 0.2))
            new_state['trust'] = max(0.0, min(1.0, new_state['trust'] + (scores.get('trust', 0) - scores.get('deception', 0)) * 0.2))
            new_state['agency'] = max(0.0, min(1.0, new_state['agency'] + (scores.get('control', 0) - scores.get('helplessness', 0)) * 0.2))
        else:
            logger.warning("ML model unavailable — falling back to keyword heuristics")
            lower_text = (text or "").lower()
            if 'gun' in lower_text or 'kill' in lower_text:
                new_state['safety'] *= 0.9
                
        emotion = "Neutral"
        if new_state['safety'] < 0.4: emotion = "Fear/Anxiety"
        elif new_state['trust'] < 0.4: emotion = "Suspicion/Paranoia"
        elif new_state['agency'] > 0.8: emotion = "Empowered/Determined"
        
        return {
            'internal_state': new_state,
            'felt_emotion': emotion,
            'method_acting_depth': method,
            'raw_scores': scores,
            'confidence': round(confidence, 3)  # Trust signal for writers
        }


# =============================================================================
# RESONANCE LOGIC (formerly resonance.py)
# =============================================================================

class ResonanceAgent:
    """Thematic Resonance Agent - Alignment of Effort & Theme.
    Uses SBERT cosine similarity when available, keyword fallback otherwise.
    """
    
    # Expanded theme descriptions for high-fidelity SBERT semantic matching
    # 12 themes covering core human dramatic archetypes
    THEME_DESCRIPTIONS = {
        'Redemption':    'finding forgiveness, making amends, being saved, earning a second chance, absolution',
        'Betrayal':      'breaking trust, deception, backstabbing, double-cross, treachery, unmasking a traitor',
        'Sacrifice':     'giving up something precious, self-sacrifice, noble loss, martyrdom, paying the ultimate price',
        'Identity':      'who am I, self-discovery, transformation, belonging, otherness, feeling like an outsider',
        'Love':          'romantic connection, deep affection, heartbreak, longing, devotion, unrequited love',
        'Death':         'mortality, loss of life, grief, finality, legacy, facing the end, survival guilt',
        'Power':         'ambition, control, dominance, political maneuvering, corruption, the cost of authority',
        'Family':        'loyalty to blood, generational conflict, parental responsibility, inheritance, sibling rivalry',
        'Truth':         'uncovering secrets, confession, confronting lies, speaking the unspeakable, the burden of knowledge',
        'Freedom':       'escaping oppression, breaking chains, fleeing the past, the right to choose, liberation',
        'Justice':       'revenge, moral reckoning, punishment, making it right, the law versus the soul',
        'Isolation':     'loneliness, abandonment, being the last survivor, the outsider, disconnection from others',
    }
    
    def __init__(self):
        self.themes = list(self.THEME_DESCRIPTIONS.keys())
        self.sbert_model = manager.get_sentence_transformer('jinaai/jina-embeddings-v2-small-en')
        self.theme_embeddings = None
        self.is_ml = (self.sbert_model is not None)
        
        if self.is_ml and self.sbert_model is not None:
            try:
                theme_texts = list(self.THEME_DESCRIPTIONS.values())
                self.theme_embeddings = self.sbert_model.encode(theme_texts, convert_to_tensor=False)
                logger.info("ResonanceAgent: SBERT theme embeddings loaded")
            except Exception as e:
                logger.error("ResonanceAgent: Failed to encode themes: %s", e)
                self.is_ml = False
        
    def analyze_scene(self, scene_text, structural_effort):
        if not self.is_ml or self.sbert_model is None:
            detected_themes, thematic_weight = self._keyword_fallback(scene_text)
            return {
                'resonance_score': structural_effort * (1.0 + thematic_weight),
                'detected_themes': detected_themes,
                'thematic_weight': round(thematic_weight, 3),
                'method': "Keyword Fallback"
            }

        detected_themes = []
        thematic_weight = 0.0
        method = "Keyword Fallback"
        
        if self.is_ml and self.theme_embeddings is not None and scene_text and len(scene_text.strip()) > 10:
            try:
                import numpy as np
                # Chunk encode the full scene text (not just first 1000 chars)
                # Then average chunk embeddings for a full-scene representation
                chunks = SiliconStanislavskiAgent._chunk_text(scene_text, chunk_size=800, overlap=100)
                chunk_embs = self.sbert_model.encode(chunks, convert_to_tensor=False, show_progress_bar=False)
                # Mean pooling across chunks = full-scene embedding
                scene_vec = chunk_embs.mean(axis=0)
                scene_norm = np.linalg.norm(scene_vec)
                theme_scores = []
                if scene_norm > 0:
                    for i, theme_name in enumerate(self.themes):
                        theme_vec = self.theme_embeddings[i]
                        theme_norm = np.linalg.norm(theme_vec)
                        if theme_norm > 0:
                            cosine_sim = np.dot(scene_vec, theme_vec) / (scene_norm * theme_norm)
                            theme_scores.append((theme_name, float(cosine_sim)))

                    # Sort by similarity, pick top themes above threshold 0.25
                    theme_scores.sort(key=lambda x: x[1], reverse=True)
                    for theme_name, sim in theme_scores:
                        if sim > 0.25:  # Lowered from 0.35 — SBERT cosines for descriptions are lower
                            detected_themes.append(theme_name)
                            thematic_weight += min(float(sim), 0.5)

                method = "SBERT Cosine Similarity (Jina v2)"
            except Exception as e:
                logger.warning("ResonanceAgent: SBERT inference failed, falling back to keywords: %s", e)
                detected_themes, thematic_weight = self._keyword_fallback(scene_text)
                method = "Keyword Fallback (after SBERT error)"
        else:
            if not self.is_ml:
                logger.warning("ResonanceAgent: SBERT unavailable — using keyword fallback")
            detected_themes, thematic_weight = self._keyword_fallback(scene_text)
        
        resonance_score = structural_effort * (1.0 + thematic_weight)
        
        return {
            'resonance_score': min(resonance_score, 2.0),
            'detected_themes': detected_themes,
            'thematic_weight': round(thematic_weight, 3),
            'method': method
        }
    
    def _keyword_fallback(self, scene_text):
        """Original keyword-based theme detection as fallback."""
        detected = []
        weight = 0.0
        lower_text = (scene_text or '').lower()
        for theme in self.themes:
            if theme.lower() in lower_text:
                detected.append(theme)
                weight += 0.2
        return detected, weight


# =============================================================================
# INSIGHT LOGIC (formerly insight.py)
# =============================================================================

class InsightAgent:
    """Insight Cascade Agent - Detecting Aha Moments"""
    
    def __init__(self):
        self.prev_entropy = 0.5 
        
    def detect_cascade(self, current_entropy):
        delta = self.prev_entropy - current_entropy
        is_insight = False
        label = "Stable"
        
        if delta > 0.2:
            is_insight = True
            label = "Insight Cascade (Aha!)"
        elif delta < -0.2:
            label = "Confusion Spike"
            
        self.prev_entropy = current_entropy
        return {'entropy_delta': delta, 'is_insight': is_insight, 'label': label}


# =============================================================================
# POLYGLOT VALIDATOR LOGIC (formerly polyglot_validator.py)
# =============================================================================

class PolyglotValidatorAgent:
    """Pacing Distribution Profiler.
    (Reframed from 'Polyglot Validator' to ensure scientific accuracy; 
    avoids mapping simple line counts to complex cultural structural paradigms).
    """
    
    def __init__(self):
        self.supported_structures = ['Balanced', 'Frontloaded', 'Backloaded', 'Mid-heavy']
        
    def detect_structure(self, scene_list):
        if not scene_list or len(scene_list) < 4:
            return "Unknown Pacing"
            
        scene_lengths = [max(1, s.get('end_line', 0) - s.get('start_line', 0)) for s in scene_list]
        total_length = sum(scene_lengths)
        
        q_size = len(scene_lengths) // 4
        q1 = sum(scene_lengths[:q_size]) / total_length
        q2 = sum(scene_lengths[q_size:q_size*2]) / total_length
        q3 = sum(scene_lengths[q_size*2:q_size*3]) / total_length
        q4 = sum(scene_lengths[q_size*3:]) / total_length
        
        # Honest pacing metrics based on length distributions
        if max([q1, q2, q3, q4]) - min([q1, q2, q3, q4]) < 0.10:
            return "Balanced Pacing (Even distribution)"
        elif q3 > q1 + 0.1 and q3 > q4 + 0.1:
            return "Mid-Heavy (Focus on development/complications)"
        elif q1 > q3 and q1 > q4:
            return "Frontloaded (Heavy setup/worldbuilding)"
        elif q4 > q1 and q4 > q2:
            return "Backloaded (Extended climax/resolution)"
            
        return "Variable Pacing"
    
    def run(self, input_data):
        structure = self.detect_structure(input_data.get('scenes', []))
        return {
            'detected_structure': structure,
            'cultural_bias_check': 'DEPRECATED - Replaced with empirical pacing profiling to maintain research validity.'
        }


# =============================================================================
# MULTI-LABEL EMOTION LOGIC
# =============================================================================

class MultiLabelEmotionAgent:
    """Detects Plutchik's 8 Emotions + Compound States.
    Uses zero-shot classification when ML is available, keyword fallback otherwise.
    """
    
    EMOTION_LABELS = ['joy', 'sadness', 'anger', 'fear', 'trust', 'disgust', 'surprise', 'anticipation']
    
    # Keyword sets for fallback mode
    KEYWORD_SETS = {
        'joy': {'joy', 'happy', 'smile', 'laugh', 'win', 'good', 'love', 'success'},
        'sadness': {'sad', 'cry', 'tears', 'grief', 'loss', 'die', 'dead', 'pain', 'fail'},
        'anger': {'angry', 'hate', 'rage', 'kill', 'fight', 'attack', 'enemy', 'fury'},
        'fear': {'scared', 'fear', 'afraid', 'run', 'hide', 'terror', 'panic', 'danger'},
        'trust': {'trust', 'friend', 'help', 'safe', 'believe', 'team', 'agree'},
        'disgust': {'gross', 'ugly', 'sick', 'rot', 'dirty', 'vile', 'nasty'},
        'surprise': {'shock', 'swhat', 'gasp', 'sudden', 'unexpected', 'stunned'},
        'anticipation': {'wait', 'hope', 'plan', 'ready', 'soon', 'look forward'}
    }
    
    def __init__(self):
        self.classifier = manager.get_zero_shot()
        self.is_ml = self.classifier is not None
        if not self.is_ml:
            logger.warning("MultiLabelEmotionAgent: ML unavailable — using keyword fallback")
        
    def run(self, scene_text):
        if not scene_text:
            return {}
        
        if self.is_ml and self.classifier is not None:
            return self._ml_classify(scene_text)
        else:
            return self._keyword_classify(scene_text)
    
    def _ml_classify(self, scene_text):
        """Use zero-shot classification for emotion detection."""
        if self.classifier is None:
            return self._keyword_classify(scene_text)
        try:
            result = self.classifier(
                scene_text[:1000],
                self.EMOTION_LABELS,
                multi_label=True
            )
            normalized = {label: round(score, 3) 
                         for label, score in zip(result['labels'], result['scores'])}
            
            # Detect Compounds from ML scores
            compounds = []
            joy   = normalized.get('joy',   0)
            trust = normalized.get('trust', 0)
            fear  = normalized.get('fear',  0)
            surp  = normalized.get('surprise', 0)
            anger = normalized.get('anger', 0)
            disg  = normalized.get('disgust', 0)
            
            # Tighter compound thresholds (0.45) to eliminate false positives
            # Compounds should only fire when BOTH emotions are clearly dominant
            if joy > 0.45 and trust > 0.45:
                compounds.append('Love')
            if fear > 0.45 and surp > 0.45:
                compounds.append('Awe')
            if anger > 0.45 and disg > 0.45:
                compounds.append('Contempt')
            if fear > 0.45 and trust > 0.45:
                compounds.append('Submission')  # New: fear + trust = subjugation
            if joy > 0.45 and surp > 0.45:
                compounds.append('Delight')     # New: joy + surprise = delight
            
            return {'emotions': normalized, 'compounds': compounds, 'method': 'Zero-Shot Classification'}
        except Exception as e:
            logger.warning("MultiLabelEmotionAgent: ML inference failed: %s. Falling back.", e)
            return self._keyword_classify(scene_text)
    
    def _keyword_classify(self, scene_text):
        """Original keyword-based emotion detection as fallback."""
        words = scene_text.lower().split()
        scores = {k: 0.0 for k in self.KEYWORD_SETS}
        total_hits = 0
        
        for w in words:
            for emo, keywords in self.KEYWORD_SETS.items():
                if w in keywords:
                    scores[emo] += 1.0
                    total_hits += 1
                    
        if total_hits == 0:
            return {k: 0.0 for k in scores}
        
        normalized = {k: round(v / total_hits, 2) for k, v in scores.items()}
        
        # Detect Compounds
        compounds = []
        if normalized['joy'] > 0.2 and normalized['trust'] > 0.2:
            compounds.append('Love')
        if normalized['fear'] > 0.2 and normalized['surprise'] > 0.2:
            compounds.append('Awe')
        if normalized['anger'] > 0.2 and normalized['disgust'] > 0.2:
            compounds.append('Contempt')
        
        return {'emotions': normalized, 'compounds': compounds, 'method': 'Keyword Fallback'}


# =============================================================================
# STAKES DETECTOR LOGIC
# =============================================================================

class StakesDetector:
    """Detects High Stakes and Time Pressure using Lexical Markers"""
    
    def __init__(self):
        self.is_ml = True
        
    def run(self, scene_text, ablation_config=None):
        if not scene_text: return {'stakes': 'Low', 'time_pressure': False}
        
        ablation_config = ablation_config or {}
        if not ablation_config.get('use_sbert', True):
            self.is_ml = False
            
        if self.is_ml:
            try:
                from ..utils.model_manager import manager as global_manager
                classifier = global_manager.get_zero_shot()
                if classifier is None:
                    return self._lexical_fallback(scene_text)
                    
                if len(scene_text.split()) < 5:
                    return {'stakes': 'Low', 'time_pressure': False, 'method': 'Length Fallback'}
                    
                # Detect High Stakes
                stakes_labels = ['high stakes life or death', 'medium stakes conflict', 'low stakes casual']
                # Use first 512 chars (model context window) — prioritise dialogue over description
                # by finding the first dialogue block if present
                text_for_ml = scene_text
                if len(scene_text) > 512:
                    # Try to find dialogue-heavy first 512 chars
                    lines = scene_text.split('\n')
                    dialogue_lines = [l for l in lines if l.strip() and not l.isupper()]
                    text_for_ml = ' '.join(dialogue_lines)[:512] if dialogue_lines else scene_text[:512]
                    
                stakes_result = classifier(text_for_ml, stakes_labels, multi_label=False)
                top_stakes = stakes_result['labels'][0]
                
                if 'high' in top_stakes: stakes_level = 'High'
                elif 'medium' in top_stakes: stakes_level = 'Medium'
                else: stakes_level = 'Low'
                
                # Detect Time Pressure
                time_labels = [' urgent time pressure deadline', 'relaxed pace no hurry']
                time_result = classifier(scene_text, time_labels, multi_label=False)
                time_pressure = 'urgent' in time_result['labels'][0] and time_result['scores'][0] > 0.6
                
                return {
                    'stakes': stakes_level,
                    'time_pressure': time_pressure,
                    'method': 'Zero-Shot ML'
                }
            except Exception as e:
                import logging
                logger = logging.getLogger('scriptpulse.mlops')
                logger.warning("StakesDetector ML failed, falling back to lexical: %s", e)
        
        return self._lexical_fallback(scene_text)

    def _lexical_fallback(self, scene_text):
        """Heuristic analysis of stakes based on keyword intensity."""
        high_stakes_markers = {
            'die', 'kill', 'save', 'bomb', 'gun', 'blood', 'forever', 'last chance', 'escape', 'destroy',
            'ruin', 'love', 'marry', 'pregnant', 'truth', 'secret', 'confess', 'explode', 'life', 'lives', 'death'
        }
        time_pressure_markers = {
            'hurry', 'run', 'fast', 'quick', 'seconds', 'minutes', 'too late', 'now', 'move', 'go go'
        }
        
        lower_text = scene_text.lower()
        
        stakes_hits = sum(1 for m in high_stakes_markers if m in lower_text)
        time_hits = sum(1 for m in time_pressure_markers if m in lower_text)
        
        stakes_level = 'Low'
        if stakes_hits >= 2: 
            stakes_level = 'High' if (stakes_hits >= 3 or time_hits >= 1) else 'Medium'
        elif stakes_hits == 1 and time_hits >= 2:
            stakes_level = 'Medium'
        
        return {
            'stakes': stakes_level,
            'time_pressure': time_hits > 0, 
            'method': 'Lexical Fallback'
        }

# =============================================================================
# MULTIMODAL LOGIC (formerly multimodal.py)
# =============================================================================

class MultimodalFusionAgent:
    """Multimodal Fusion Agent - Combining Text & Pseudo-Vision/Acoustics.
    Since raw video/audio is unavailable at the script stage, this agent
    extrapolates hypothetical visual and acoustic intensity from screenplay format.
    """
    
    def __init__(self):
        self.visual_layer_enabled = True
        
    def run(self, input_data):
        text_effort = input_data.get('effort_score', 0.5)
        
        # Extrapolate visual density proxy (Action verbs, uppercase nouns)
        action_density = input_data.get('action_density', 0.5)
        # Extrapolate acoustic density proxy (Dialogue velocity, punctuation marks)
        dialogue_velocity = input_data.get('dialogue_velocity', 0.5)
        
        # Calculate cross-modal interference (Does loud sound conflict with dense text?)
        interference = 0.0
        if text_effort > 0.7 and dialogue_velocity > 0.7:
            interference = 0.2  # Cognitive overload from dual complex information
        elif action_density > 0.8 and text_effort < 0.3:
            # High action, low text -> visual dominance, reduced reading effort
            interference = -0.15 
            
        fused_effort = text_effort + (action_density * 0.15) + (dialogue_velocity * 0.1) + interference
        
        return {
            'fused_effort': max(0.0, min(fused_effort, 1.0)),
            'visual_proxy': round(action_density, 3),
            'acoustic_proxy': round(dialogue_velocity, 3),
            'source': 'Multimodal Fusion (Action/Dialogue Proxy Extrapolation)'
        }


# =============================================================================
# CHARACTER VOICE DISTINCTION AGENT (Unique Competitive Feature)
# =============================================================================

class CharacterVoiceDistinctionAgent:
    """
    Measures how semantically DISTINCT each character's voice is from every other.

    This is a unique differentiator: most script analysis tools flag 'Same Voice
    Syndrome' via surface statistics (sentence length, vocabulary overlap). We use
    Jina SBERT to embed each character's full dialogue corpus into a semantic vector,
    then compute pairwise cosine distances between characters.

    Output:
      - voice_distinction_scores: {(CharA, CharB): similarity} — lower is MORE distinct
      - voice_diversity_index: global 0-1 score (1.0 = all characters sound unique)
      - flagged_pairs: pairs with cosine similarity > 0.80 (dangerously similar voices)
      - standout_character: the character whose voice is most distinct from all others
    """

    SIMILARITY_THRESHOLD = 0.80  # Above this = voices are suspiciously similar

    def __init__(self):
        self.sbert_model = manager.get_sentence_transformer()
        self.is_ml = (self.sbert_model is not None)
        if not self.is_ml:
            logger.warning("CharacterVoiceDistinctionAgent: SBERT unavailable — skipping voice analysis")

    def analyze(self, voice_fingerprints: dict) -> dict:
        """
            voice_fingerprints: dict from WriterAgent — {char_name: {dialogue_samples: [...], line_count: int}}
        Returns:
            Full voice distinction report.
        """
        if not self.is_ml or self.sbert_model is None or not voice_fingerprints:
            return {'method': 'Unavailable', 'voice_diversity_index': None}

        # Filter: only characters with enough dialogue to meaningfully fingerprint
        eligible = {
            name: data for name, data in voice_fingerprints.items()
            if data.get('line_count', 0) >= 8
        }

        if len(eligible) < 2:
            return {
                'method': 'Insufficient Data',
                'note': 'Need at least 2 characters with 8+ dialogue lines for voice comparison.',
                'voice_diversity_index': None
            }

        # Build a text corpus per character (up to 30 dialogue lines, joined)
        char_corpora = {}
        for name, data in eligible.items():
            samples = data.get('dialogue_samples', [])
            if not samples:
                continue
            # Join samples into one representative text block
            corpus = ' '.join(str(s) for s in samples[:30])[:2000]
            if len(corpus) > 30:
                char_corpora[name] = corpus

        if len(char_corpora) < 2:
            return {'method': 'Insufficient Data', 'voice_diversity_index': None}

        # Encode all character corpora in one batch (fast)
        char_names = list(char_corpora.keys())
        corpora_list = [char_corpora[n] for n in char_names]

        try:
            import numpy as np
            embeddings = self.sbert_model.encode(
                corpora_list, convert_to_tensor=False, show_progress_bar=False
            )

            # Normalise embeddings for cosine via dot product
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            normed = embeddings / norms

            # Compute full pairwise similarity matrix
            sim_matrix = np.dot(normed, normed.T)  # shape: (N, N)

            # Extract upper triangle (unique pairs only)
            n = len(char_names)
            pair_similarities = {}
            flagged_pairs = []
            all_similarities = []

            for i in range(n):
                for j in range(i + 1, n):
                    sim = float(sim_matrix[i, j])
                    pair_key = f"{char_names[i]} ↔ {char_names[j]}"
                    pair_similarities[pair_key] = round(sim, 3)
                    all_similarities.append(sim)
                    if sim > self.SIMILARITY_THRESHOLD:
                        flagged_pairs.append({
                            'pair': pair_key,
                            'similarity': round(sim, 3),
                            'severity': '🔴 Critical' if sim > 0.92 else '🟠 High',
                            'advice': (
                                f"{char_names[i]} and {char_names[j]} share {round(sim*100)}% "
                                f"semantic voice similarity. Give one character a unique verbal tic, "
                                f"a distinct sentence rhythm, or a recurring idiomatic phrase the other never uses."
                            )
                        })

            # Voice Diversity Index: 1 - mean_similarity across all pairs
            # 1.0 = all characters sound completely different (ideal)
            # 0.0 = all characters are semantically identical
            mean_sim = float(np.mean(all_similarities)) if all_similarities else 0.0
            diversity_index = round(1.0 - mean_sim, 3)

            # Standout character: lowest mean similarity to all others = most distinct voice
            char_distinctiveness = {}
            for i, name in enumerate(char_names):
                row_sims = [float(sim_matrix[i, j]) for j in range(n) if j != i]
                char_distinctiveness[name] = round(1.0 - (sum(row_sims) / len(row_sims)), 3) if row_sims else 0.5

            standout = max(char_distinctiveness, key=lambda k: char_distinctiveness[k])

            # Diversity label
            if diversity_index >= 0.25:
                diversity_label = "🟢 Excellent — Characters sound genuinely distinct"
            elif diversity_index >= 0.15:
                diversity_label = "🟡 Moderate — Some characters may blend together"
            else:
                diversity_label = "🔴 Weak — Most characters share similar voice patterns"

            return {
                'method': 'SBERT Semantic Voice Embedding (Jina v2)',
                'voice_diversity_index': diversity_index,
                'diversity_label': diversity_label,
                'pair_similarities': pair_similarities,
                'flagged_pairs': flagged_pairs,
                'char_distinctiveness': char_distinctiveness,
                'standout_character': standout,
                'standout_note': f"{standout} has the most distinctive dialogue voice in the script.",
                'characters_analyzed': char_names
            }

        except Exception as e:
            logger.error("CharacterVoiceDistinctionAgent: SBERT inference failed: %s", e)
            return {'method': 'Error', 'voice_diversity_index': None, 'error': str(e)}
