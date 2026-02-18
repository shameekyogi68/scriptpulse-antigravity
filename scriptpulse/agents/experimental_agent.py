"""
Experimental Agent - Advanced Research & Experimental Modules
Consolidates: silicon_stanislavski.py, resonance.py, insight.py, polyglot_validator.py, multimodal.py
"""

from ..utils.model_manager import manager

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
                print(f"[Error] Batch Inference Failed: {e}")
                self.is_ml = False 
                
        output_map = {idx: out for idx, out in zip(valid_indices, ml_outputs)}
        
        for i, text in enumerate(scenes_text):
            step_data = self._update_state(current_state, text, output_map.get(i))
            current_state = step_data['internal_state'] 
            results.append(step_data)
        return results

    def _update_state(self, state, text, ml_result=None):
        new_state = state.copy()
        method = "Keyword Heuristic"
        scores = {}
        
        if ml_result:
            method = "Batch Active Inference v2.0"
            scores = {label: score for label, score in zip(ml_result['labels'], ml_result['scores'])}
            
            new_state['safety'] = max(0.0, min(1.0, new_state['safety'] + (scores.get('safety', 0) - scores.get('danger', 0)) * 0.2))
            new_state['trust'] = max(0.0, min(1.0, new_state['trust'] + (scores.get('trust', 0) - scores.get('deception', 0)) * 0.2))
            new_state['agency'] = max(0.0, min(1.0, new_state['agency'] + (scores.get('control', 0) - scores.get('helplessness', 0)) * 0.2))
        else:
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
    """Thematic Resonance Agent - Alignment of Effort & Theme"""
    
    def __init__(self):
        self.themes = ['Redemption', 'Betrayal', 'Sacrifice', 'Identity', 'Love', 'Death']
        
    def analyze_scene(self, scene_text, structural_effort):
        detected_themes = []
        thematic_weight = 0.0
        lower_text = scene_text.lower()
        
        for theme in self.themes:
            if theme.lower() in lower_text:
                detected_themes.append(theme)
                thematic_weight += 0.2
        
        resonance_score = structural_effort * (1.0 + thematic_weight)
        
        return {
            'resonance_score': min(resonance_score, 2.0),
            'detected_themes': detected_themes,
            'thematic_weight': thematic_weight
        }


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
    """Cross-Cultural Validator Agent"""
    
    def __init__(self):
        self.supported_structures = ['3-Act', 'Kishotenketsu', 'Masala']
        
    def detect_structure(self, scene_list):
        # Placeholder logic
        return "3-Act (Western Standard)" if scene_list else "Unknown"
    
    def run(self, input_data):
        structure = self.detect_structure(input_data.get('scenes', []))
        return {
            'detected_structure': structure,
            'cultural_bias_check': 'PASSED' if structure == '3-Act' else 'WARNING: Non-Standard'
        }


# =============================================================================
# MULTI-LABEL EMOTION LOGIC
# =============================================================================

class MultiLabelEmotionAgent:
    """Detects Plutchik's 8 Emotions + Compound States"""
    
    def __init__(self):
        self.emotions = {
            'joy': {'joy', 'happy', 'smile', 'laugh', 'win', 'good', 'love', 'success'},
            'sadness': {'sad', 'cry', 'tears', 'grief', 'loss', 'die', 'dead', 'pain', 'fail'},
            'anger': {'angry', 'hate', 'rage', 'kill', 'fight', 'attack', 'enemy', 'fury'},
            'fear': {'scared', 'fear', 'afraid', 'run', 'hide', 'terror', 'panic', 'danger'},
            'trust': {'trust', 'friend', 'help', 'safe', 'believe', 'team', 'agree'},
            'disgust': {'gross', 'ugly', 'sick', 'rot', 'dirty', 'vile', 'nasty'},
            'surprise': {'shock', 'swhat', 'gasp', 'sudden', 'unexpected', 'stunned'},
            'anticipation': {'wait', 'hope', 'plan', 'ready', 'soon', 'look forward'}
        }
        
    def run(self, scene_text):
        if not scene_text: return {}
        words = scene_text.lower().split()
        scores = {k: 0.0 for k in self.emotions.keys()}
        total_hits = 0
        
        for w in words:
            for emo, keywords in self.emotions.items():
                if w in keywords:
                    scores[emo] += 1.0
                    total_hits += 1
                    
        if total_hits == 0: return {k: 0.0 for k in scores}
        
        # Normalize
        normalized = {k: round(v / total_hits, 2) for k, v in scores.items()}
        
        # Detect Compounds
        compounds = []
        if normalized['joy'] > 0.2 and normalized['trust'] > 0.2: compounds.append('Love')
        if normalized['fear'] > 0.2 and normalized['surprise'] > 0.2: compounds.append('Awe')
        if normalized['anger'] > 0.2 and normalized['disgust'] > 0.2: compounds.append('Contempt')
        
        return {'emotions': normalized, 'compounds': compounds}


# =============================================================================
# STAKES DETECTOR LOGIC
# =============================================================================

class StakesDetector:
    """Detects High Stakes and Time Pressure using Lexical Markers"""
    
    def __init__(self):
        self.high_stakes_markers = {
            'die', 'kill', 'save', 'bomb', 'gun', 'blood', 'forever', 'last chance', 'escape', 'destroy',
            'ruin', 'love', 'marry', 'pregnant', 'truth', 'secret', 'confess', 'explode', 'life', 'lives', 'death'
        }
        self.time_pressure_markers = {
            'hurry', 'run', 'fast', 'quick', 'seconds', 'minutes', 'too late', 'now', 'move', 'go go'
        }
        
    def run(self, scene_text):
        if not scene_text: return {'stakes': 'Low', 'time_pressure': False}
        
        lower_text = scene_text.lower()
        
        stakes_hits = sum(1 for m in self.high_stakes_markers if m in lower_text)
        time_hits = sum(1 for m in self.time_pressure_markers if m in lower_text)
        
        stakes_level = 'Low'
        if stakes_hits >= 2: 
            stakes_level = 'High' if (stakes_hits >= 3 or time_hits >= 1) else 'Medium'
        elif stakes_hits == 1 and time_hits >= 2:
            stakes_level = 'Medium'
        
        return {
            'stakes': stakes_level,
            'time_pressure': time_hits > 0, # Strict check for boolean
            'markers_found': stakes_hits + time_hits
        }

# =============================================================================
# MULTIMODAL LOGIC (formerly multimodal.py)
# =============================================================================

class MultimodalFusionAgent:
    """Multimodal Fusion Agent - Combining Text & Vision"""
    
    def __init__(self):
        self.visual_layer_enabled = False
        
    def run(self, input_data):
        text_effort = input_data.get('effort_score', 0.5)
        visual_density = input_data.get('visual_density', 0.0) 
        fused_effort = text_effort + (visual_density * 0.3)
        return {
            'fused_effort': min(fused_effort, 1.0),
            'source': 'Multimodal (Text + Vision Stub)'
        }
