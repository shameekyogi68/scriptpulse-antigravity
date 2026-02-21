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
    
    def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
        self.belief_state = {'safety': 0.8, 'trust': 0.8, 'agency': 0.5}
        self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
        self.labels = ["danger", "safety", "deception", "trust", "helplessness", "control"]
        self.is_ml = self.classifier is not None
        
    def analyze_script(self, scenes_text):
        """Batch process all scenes for massive speedup."""
        results = []
        current_state = self.belief_state.copy()
        
        valid_indices = [i for i, t in enumerate(scenes_text) if t and len(t) > 10]
        valid_texts = [scenes_text[i][:1000] for i in valid_indices] 
        
        ml_outputs = []
        if self.is_ml and valid_texts:
            try:
                ml_outputs = self.classifier(valid_texts, self.labels, multi_label=True, batch_size=4)
            except Exception as e:
                logger.error("Batch Inference Failed: %s", e)
                self.is_ml = False 
                
        output_map = {idx: out for idx, out in zip(valid_indices, ml_outputs)}
        
        for i, text in enumerate(scenes_text):
            step_data = self._update_state(current_state, text, output_map.get(i))
            current_state = step_data['internal_state'] 
            results.append(step_data)
        return results

    def _update_state(self, state, text, ml_result=None):
        new_state = state.copy()
        method = "Keyword Heuristic (Fallback)"
        scores = {}
        
        if ml_result:
            method = "Zero-Shot Classification"
            scores = {label: score for label, score in zip(ml_result['labels'], ml_result['scores'])}
            
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
            'raw_scores': scores
        }


# =============================================================================
# RESONANCE LOGIC (formerly resonance.py)
# =============================================================================

class ResonanceAgent:
    """Thematic Resonance Agent - Alignment of Effort & Theme.
    Uses SBERT cosine similarity when available, keyword fallback otherwise.
    """
    
    # Theme descriptions for embedding-based matching
    THEME_DESCRIPTIONS = {
        'Redemption': 'finding forgiveness, making amends, being saved, second chance',
        'Betrayal': 'breaking trust, deception, backstabbing, double-cross, treachery',
        'Sacrifice': 'giving up something precious, self-sacrifice, noble loss, martyrdom',
        'Identity': 'who am I, self-discovery, transformation, belonging, otherness',
        'Love': 'romantic connection, deep affection, heartbreak, longing, devotion',
        'Death': 'mortality, loss of life, grief, finality, legacy, afterlife'
    }
    
    def __init__(self):
        self.themes = list(self.THEME_DESCRIPTIONS.keys())
        self.sbert_model = manager.get_sentence_transformer('sentence-transformers/all-MiniLM-L6-v2')
        self.theme_embeddings = None
        self.is_ml = self.sbert_model is not None
        
        if self.is_ml:
            try:
                theme_texts = list(self.THEME_DESCRIPTIONS.values())
                self.theme_embeddings = self.sbert_model.encode(theme_texts, convert_to_tensor=False)
                logger.info("ResonanceAgent: SBERT theme embeddings loaded")
            except Exception as e:
                logger.error("ResonanceAgent: Failed to encode themes: %s", e)
                self.is_ml = False
        
    def analyze_scene(self, scene_text, structural_effort):
        detected_themes = []
        thematic_weight = 0.0
        method = "Keyword Fallback"
        
        if self.is_ml and self.theme_embeddings is not None and scene_text and len(scene_text.strip()) > 10:
            try:
                scene_emb = self.sbert_model.encode([scene_text[:1000]], convert_to_tensor=False)
                # Compute cosine similarity with each theme
                import numpy as np
                scene_vec = scene_emb[0]
                scene_norm = np.linalg.norm(scene_vec)
                if scene_norm > 0:
                    for i, theme_name in enumerate(self.themes):
                        theme_vec = self.theme_embeddings[i]
                        theme_norm = np.linalg.norm(theme_vec)
                        if theme_norm > 0:
                            cosine_sim = np.dot(scene_vec, theme_vec) / (scene_norm * theme_norm)
                            if cosine_sim > 0.35:  # Threshold for thematic relevance
                                detected_themes.append(theme_name)
                                thematic_weight += min(float(cosine_sim), 0.5)
                method = "SBERT Cosine Similarity"
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
    """Cross-Cultural Validator Agent.
    Detects narrative structure based on scene segmentation and pacing.
    """
    
    def __init__(self):
        self.supported_structures = ['3-Act', 'Kishotenketsu', 'Episodic', 'Unknown']
        
    def detect_structure(self, scene_list):
        if not scene_list or len(scene_list) < 4:
            return "Unknown"
            
        scene_lengths = [max(1, s.get('end_line', 0) - s.get('start_line', 0)) for s in scene_list]
        total_length = sum(scene_lengths)
        
        # Split into quartiles to analyze pacing
        q_size = len(scene_lengths) // 4
        q1 = sum(scene_lengths[:q_size]) / total_length
        q2 = sum(scene_lengths[q_size:q_size*2]) / total_length
        q3 = sum(scene_lengths[q_size*2:q_size*3]) / total_length
        q4 = sum(scene_lengths[q_size*3:]) / total_length
        
        # Heuristic rules for structural rhythms
        if q3 > q1 and q3 > q2 and q3 > q4:
            # Climax in third quarter is classic 3-Act
            return "3-Act (Western Standard)"
        elif q3 > q2 and q4 > q1 and abs(q1 - q2) < 0.1:
            # Kishotenketsu: Intro, Development, Twist (high activity), Conclusion (wrap up longer than intro)
            return "Kishotenketsu (East Asian)"
        elif max([q1, q2, q3, q4]) - min([q1, q2, q3, q4]) < 0.15:
            # Even distribution of pacing
            return "Episodic (Flat)"
            
        return "Unknown"
    
    def run(self, input_data):
        structure = self.detect_structure(input_data.get('scenes', []))
        return {
            'detected_structure': structure,
            'cultural_bias_check': 'PASSED' if '3-Act' in structure else 'NOTE: Non-Standard Paradigm Detected'
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
    
    def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
        self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
        self.is_ml = self.classifier is not None
        if not self.is_ml:
            logger.warning("MultiLabelEmotionAgent: ML unavailable — using keyword fallback")
        
    def run(self, scene_text):
        if not scene_text:
            return {}
        
        if self.is_ml:
            return self._ml_classify(scene_text)
        else:
            return self._keyword_classify(scene_text)
    
    def _ml_classify(self, scene_text):
        """Use zero-shot classification for emotion detection."""
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
            if normalized.get('joy', 0) > 0.3 and normalized.get('trust', 0) > 0.3:
                compounds.append('Love')
            if normalized.get('fear', 0) > 0.3 and normalized.get('surprise', 0) > 0.3:
                compounds.append('Awe')
            if normalized.get('anger', 0) > 0.3 and normalized.get('disgust', 0) > 0.3:
                compounds.append('Contempt')
            
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
        if not ablation_config.get('use_sbert', True) and not ablation_config.get('use_gpt2', True):
            self.is_ml = False
            
        if self.is_ml:
            try:
                from ..utils.model_manager import manager as global_manager
                classifier = global_manager.get_zero_shot()
                if len(scene_text.split()) < 5:
                    return {'stakes': 'Low', 'time_pressure': False, 'method': 'Length Fallback'}
                    
                # Detect High Stakes
                stakes_labels = ['high stakes life or death', 'medium stakes conflict', 'low stakes casual']
                stakes_result = classifier(scene_text, stakes_labels, multi_label=False)
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
        
        # Lexical Fallback
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
            'time_pressure': time_hits > 0, # Strict check for boolean
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
