"""
Interpretation Agent - Text-Grounded Cognitive Version
Translates mathematical signals into true human "First Reader" experiences.
Focuses on: Confusion, Boredom, Visceral Reaction, and Textual Proof.
"""

import statistics
import random

class InterpretationAgent:
    """Cognitive Translation Layer - From Data to Human Experience"""

    def __init__(self):
        # Human Experience Labels for UI
        self.LABELS = {
            'High': "Gripping / Intense",
            'Medium': "Engaging / Steady",
            'Low': "Slow / Breather"
        }

    def run(self, temporal_trace, features=None, scenes=None, genre='drama'):
        """Main entry point for cognitive interpretation"""
        if not temporal_trace: return {}
        
        # 1. Structure Analysis (Text-Grounded)
        structure = self.map_to_structure(temporal_trace, features)
        
        # 2. Cognitive Heuristics Diagnosis
        diagnosis = self.diagnose_patterns(temporal_trace, features, scenes, genre=genre)
        
        return {
            'structure': structure,
            'diagnosis': diagnosis,
            'suggestions': [] # Deprecated: We don't give advice to writers anymore.
        }

    def map_to_structure(self, temporal_trace, features=None):
        """Identifies True Narrative Shifts based on intense emotional flux, not just math percentages."""
        total = len(temporal_trace)
        if total < 5: return {'acts': [], 'beats': []}
        
        # ACT 1 ends around 25%
        a1_end = int(total * 0.25)
        # ACT 2 ends around 75%
        a2_end = int(total * 0.75)
        
        acts = [
            {'name': 'Act 1: Setup', 'range': [0, a1_end]},
            {'name': 'Act 2: Confrontation', 'range': [a1_end + 1, a2_end]},
            {'name': 'Act 3: Resolution', 'range': [a2_end + 1, total - 1]}
        ]
        
        beats = []
        
        # Find True Inciting Incident: The earliest spike in pure emotional tension
        ii_idx = 0
        for i, t in enumerate(temporal_trace[:a1_end+1]):
            if t['attentional_signal'] > 0.6:
                ii_idx = i
                break
        
        # Find True Midpoint: The absolute peak of tension AND entropy (A major complication)
        mid_idx = a1_end
        highest_combo = 0
        if features and len(features) == len(temporal_trace):
            for i in range(a1_end, a2_end):
                combo = temporal_trace[i]['attentional_signal'] + (features[i].get('entropy_score', 0) / 10)
                if combo > highest_combo:
                    highest_combo = combo
                    mid_idx = i
        else:
            mid_idx = int(total/2) # Fallback

        climax_idx = total - 1
        highest_tension = 0
        for i in range(a2_end, total):
            if temporal_trace[i]['attentional_signal'] > highest_tension:
                highest_tension = temporal_trace[i]['attentional_signal']
                climax_idx = i
        
        beats = [
            {'name': 'Inciting Incident', 'scene_index': ii_idx},
            {'name': 'Midpoint', 'scene_index': mid_idx},
            {'name': 'Climax', 'scene_index': climax_idx}
        ]
        
        return {'acts': acts, 'beats': beats}

    def _get_snippet(self, scene_dict):
        """Extracts a short text snippet from a scene using correct tags ('D', 'A')."""
        try:
            lines = scene_dict.get('lines', [])
            dialogue = [l['text'] for l in lines if l.get('tag') == 'D' and len(l['text']) > 10]
            action = [l['text'] for l in lines if l.get('tag') == 'A' and len(l['text']) > 10]
            
            if dialogue: 
                snip = dialogue[len(dialogue)//2]
                return f'"{snip[:60]}..."'
            if action:
                snip = action[len(action)//2]
                return f'"{snip[:60]}..."'
            return ""
        except:
            return ""

    def diagnose_patterns(self, temporal_trace, features=None, scenes=None, genre='drama'):
        """Identifies Cognitive Experiences: Boredom, Confusion, Visceral Reaction."""
        diagnosis = []
        signals = [s['attentional_signal'] for s in temporal_trace]
        if not signals or not features or not scenes or len(features) != len(temporal_trace) or len(scenes) != len(temporal_trace): 
            return diagnosis
            
        # Pacing Threshold Adjustment by Genre
        sag_limit = 0.35 if genre.lower() == 'drama' else 0.45 # Action/Thriller drift earlier
        sag_scenes = 3 if genre.lower() == 'drama' else 2 
            
        # 1. Overcrowded Narrative (High entity churn + Low Tension)
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            churn = feat.get('referential_load', {}).get('entity_churn', 0)
            
            if churn >= 3.0 and att_sig < 0.5:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Overcrowded Scene (Scene {i+1})**: Too many new elements or characters are introduced without a strong driving dramatic question. (e.g., {snippet})"
                )
                break # Just find one to avoid spam

        # 2. High-Octane Sequence (High Action and High Tension)
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if action > 6 and att_sig > 0.8:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"✨ **Action Peak (Scene {i+1})**: Strong integration of physical action and narrative tension. Major anchor for pacing. (e.g., {snippet})"
                )
                break
                
        # 3. Pacing Drag / Structural Sag
        high_runs = 0
        for i, s in enumerate(signals):
            if s < sag_limit: 
                high_runs += 1
            else: 
                high_runs = 0
            
            if high_runs >= sag_scenes:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Structural Sag (Scene {i+1})**: Consecutive scenes of low tension for a {genre}. (e.g., {snippet})"
                )
                break
                
        # 4. Exposition Dump / Narrative Density
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            entropy = feat.get('entropy_score', 0)
            
            if entropy > 3.0 and att_sig < 0.4:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"💡 **Exposition Heavy (Scene {i+1})**: The scene is text-dense but low on dramatic conflict. (e.g., {snippet})"
                )
                break

        return diagnosis

    def generate_suggestions(self, temporal_trace):
        return {}

    def generate_scene_notes(self, input_data):
        return {}

    def apply_semantic_labels(self, temporal_trace, valence_trace=None):
        labels = []
        for pt in temporal_trace:
            s = pt['attentional_signal']
            label = "Steady Flow"
            if s > 0.7: label = "High Conflict"
            elif s < 0.3: label = "Quiet Moment"
            labels.append({'scene_index': pt['scene_index'], 'primary_label': label, 'composite_beat': label})
        return labels

    def map_archetypes(self, voice_map): return {}
    def audit_subtext(self, encoded, voice_map): return []
    def map_to_custom_framework(self, trace, framework_type='3_act'): return self.map_to_structure(trace)
    def audit_narrative_intelligence(self, scenes, trace): return []
    def calculate_conflict_typology(self, encoded, valence): return []
    def track_thematic_recurrence(self, encoded): return []
    def map_interaction_networks(self, scenes, typologies): return {'edges': [], 'triangles': []}
    def audit_timeline_continuity(self, scenes): return []
    def audit_narrative_causality(self, encoded, scenes): return []
    def calculate_dialogue_authenticity(self, encoded): return []
