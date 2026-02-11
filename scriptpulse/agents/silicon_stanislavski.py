"""
ScriptPulse vNext.11 - "Silicon Stanislavski" Agent (Real ML)
Objective: Simulate internal emotional state using Zero-Shot Classification (Active Inference).
"""

try:
    from transformers import pipeline
    import torch
except ImportError:
    pipeline = None
    torch = None

class SiliconStanislavski:
    def __init__(self):
        # Internal Belief State
        self.belief_state = {
            'safety': 0.8,
            'trust': 0.8,
            'agency': 0.5
        }
        
        try:
            device = -1
            if torch and torch.cuda.is_available():
                device = 0
                
            # Using a fast zero-shot model
            self.classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3", device=device)
            self.labels = ["danger", "safety", "deception", "trust", "helplessness", "control"]
            self.is_ml = True
            print("[ML] Silicon Stanislavski initialized (Zero-Shot).")
        except Exception as e:
            print(f"[Warning] Failed to load Stanislavski ML: {e}")
            self.is_ml = False
        
    def act_scene(self, scene_text):
        """
        Simulate the agent 'living' through the scene using ML.
        """
        if not scene_text or len(scene_text) < 10:
             return {'internal_state': self.belief_state.copy(), 'felt_emotion': "Neutral"}

        # ML Update
        if self.is_ml:
            try:
                # Truncate for speed/memory if needed
                text_sample = scene_text[:1000] 
                result = self.classifier(text_sample, self.labels, multi_label=True)
                
                scores = {label: score for label, score in zip(result['labels'], result['scores'])}
                
                # Active Inference Update Rule (Bayesian-ish)
                # Safety: Decrease by Danger, Increase by Safety
                safety_delta = (scores.get('safety', 0) - scores.get('danger', 0)) * 0.2
                self.belief_state['safety'] = max(0.0, min(1.0, self.belief_state['safety'] + safety_delta))
                
                # Trust: Decrease by Deception, Increase by Trust
                trust_delta = (scores.get('trust', 0) - scores.get('deception', 0)) * 0.2
                self.belief_state['trust'] = max(0.0, min(1.0, self.belief_state['trust'] + trust_delta))
                
                # Agency: Decrease by Helplessness, Increase by Control
                agency_delta = (scores.get('control', 0) - scores.get('helplessness', 0)) * 0.2
                self.belief_state['agency'] = max(0.0, min(1.0, self.belief_state['agency'] + agency_delta))
                
            except Exception as e:
                print(f"[Error] Stanislavski Inference Failed: {e}")
        
        # Fallback Logic (if ML failed or didn't run)
        else:
            lower_text = scene_text.lower()
            if 'gun' in lower_text or 'kill' in lower_text:
                self.belief_state['safety'] *= 0.9
        
        # Determine Felt Emotion
        emotion = "Neutral"
        if self.belief_state['safety'] < 0.4:
            emotion = "Fear/Anxiety"
        elif self.belief_state['trust'] < 0.4:
            emotion = "Suspicion/Paranoia"
        elif self.belief_state['agency'] > 0.8:
            emotion = "Empowered/Determined"
            
        return {
            'internal_state': self.belief_state.copy(),
            'felt_emotion': emotion,
            'method_acting_depth': "Zero-Shot Active Inference v1.0"
        }
