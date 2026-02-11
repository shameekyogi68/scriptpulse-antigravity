from ..utils.model_manager import manager

class SiliconStanislavski:
    def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
        self.belief_state = {
            'safety': 0.8,
            'trust': 0.8,
            'agency': 0.5
        }
        
        # Use centralized manager
        self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
        self.labels = ["danger", "safety", "deception", "trust", "helplessness", "control"]
        self.is_ml = self.classifier is not None
        
    def analyze_script(self, scenes_text):
        """
        Batch process all scenes for massive speedup.
        Args:
            scenes_text (List[str]): List of texts for each scene.
        Returns:
            List[dict]: List of state updates per scene.
        """
        results = []
        current_state = self.belief_state.copy()
        
        # Filter valid texts to avoid errors
        valid_indices = [i for i, t in enumerate(scenes_text) if t and len(t) > 10]
        valid_texts = [scenes_text[i][:1000] for i in valid_indices] # Truncate for speed
        
        ml_outputs = []
        if self.is_ml and valid_texts:
            try:
                # BATCH INFERENCE
                # This runs all texts through the GPU/CPU in one go
                ml_outputs = self.classifier(valid_texts, self.labels, multi_label=True, batch_size=4)
            except Exception as e:
                print(f"[Error] Batch Inference Failed: {e}")
                self.is_ml = False # Fallback for this run
                
        # Map outputs back to original indices
        output_map = {idx: out for idx, out in zip(valid_indices, ml_outputs)}
        
        for i, text in enumerate(scenes_text):
            # Process State Update
            step_data = self._update_state(current_state, text, output_map.get(i))
            current_state = step_data['internal_state'] # Carry over state
            results.append(step_data)
            
        return results

    def _update_state(self, state, text, ml_result=None):
        """Helper to update state based on ML or Heuristic"""
        new_state = state.copy()
        method = "Keyword Heuristic"
        
        if ml_result:
            method = "Batch Active Inference v2.0"
            scores = {label: score for label, score in zip(ml_result['labels'], ml_result['scores'])}
            
            # Active Inference Update Rule
            safety_delta = (scores.get('safety', 0) - scores.get('danger', 0)) * 0.2
            new_state['safety'] = max(0.0, min(1.0, new_state['safety'] + safety_delta))
            
            trust_delta = (scores.get('trust', 0) - scores.get('deception', 0)) * 0.2
            new_state['trust'] = max(0.0, min(1.0, new_state['trust'] + trust_delta))
            
            agency_delta = (scores.get('control', 0) - scores.get('helplessness', 0)) * 0.2
            new_state['agency'] = max(0.0, min(1.0, new_state['agency'] + agency_delta))
        else:
            # Fallback
            lower_text = (text or "").lower()
            if 'gun' in lower_text or 'kill' in lower_text:
                new_state['safety'] *= 0.9
                
        # Determine Emotion
        emotion = "Neutral"
        if new_state['safety'] < 0.4: emotion = "Fear/Anxiety"
        elif new_state['trust'] < 0.4: emotion = "Suspicion/Paranoia"
        elif new_state['agency'] > 0.8: emotion = "Empowered/Determined"
        
        return {
            'internal_state': new_state,
            'felt_emotion': emotion,
            'method_acting_depth': method,
            'raw_scores': scores if ml_result else {}
        }

    def act_scene(self, scene_text):
        """Legacy wrapper for single scene."""
        return self._update_state(self.belief_state, scene_text)
