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

    def _get_snippet(self, scene_dict, preferred_tag=None):
        """Extracts a short text snippet from a scene using correct tags ('D', 'A')."""
        try:
            lines = scene_dict.get('lines', [])
            dialogue = [l['text'] for l in lines if l.get('tag') == 'D' and len(l['text']) > 10]
            action = [l['text'] for l in lines if l.get('tag') == 'A' and len(l['text']) > 10]
            
            if preferred_tag == 'A' and action:
                snip = action[len(action)//2]
                return f'"{snip[:60]}..."'
            if preferred_tag == 'D' and dialogue:
                snip = dialogue[len(dialogue)//2]
                return f'"{snip[:60]}..."'
                
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
        if not temporal_trace or not features or not scenes or len(features) != len(temporal_trace) or len(scenes) != len(temporal_trace): 
            return diagnosis
            
        signals = [s['attentional_signal'] for s in temporal_trace]
        
        # Pacing Threshold Adjustment by Genre
        sag_limit = 0.35 if genre.lower() == 'drama' else 0.45 
        sag_scenes = 3 if genre.lower() == 'drama' else 2 
            
        # 1. Overcrowded Narrative
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            if churn >= 3.5 and att_sig < 0.5:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Information Churn (Scene {i+1})**: Excessive name density. Suggest compressing introduction or embedding these details into an existing conflict. (e.g., {snippet})"
                )
                break

        # 2. Action Peak
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if action > 6 and att_sig > 0.8:
                snippet = self._get_snippet(scenes[i], preferred_tag='A')
                diagnosis.append(
                    f"✨ **Action Peak (Scene {i+1})**: Strong integration of physical action and tension. (e.g., {snippet})"
                )
                break
                
        # 3. Structural Sag
        high_runs = 0
        for i, s in enumerate(signals):
            if s < sag_limit: 
                high_runs += 1
            else: 
                high_runs = 0
            
            if high_runs >= sag_scenes:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Attentional Valley (Scene {i+1})**: Cumulative period of lower dramatic signals. (e.g., {snippet})"
                )
                break
                
        # 4. Exposition Heavy
        for i in range(len(temporal_trace)):
            if entropy > 4.5 and att_sig < 0.4:  # Raised significantly to filter anything but pure data-dumps
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"💡 **Informational Peak (Scene {i+1})**: Dry exposition. Convert this block into a dramatic confrontation or high-stakes discovery to restore narrative momentum. (e.g., {snippet})"
                )
                break

        # 5. Talking Heads (High Dialogue, Low Action, Mid Tension)
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            dial = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if dial > 15 and action < 2 and 0.4 < att_sig < 0.6:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🗣️ **Talking Heads (Scene {i+1})**: Physical passivity. Inject visual subtext or external environment shifts to avoid dialogue fatigue. (e.g., {snippet})"
                )
                break

        # 6. Tonal Whiplash (Task: Stabilize detection)
        whiplash_candidates = []
        for i in range(1, len(temporal_trace)):
            curr_sig = temporal_trace[i]['attentional_signal']
            prev_sig = temporal_trace[i-1]['attentional_signal']
            feat = features[i]
            purpose = feat.get('purpose', {}).get('purpose', '')
            has_death = feat.get('narrative_closure', False)
            is_anchor_scene = any(kw in purpose for kw in ['Revelation', 'Discovery', 'Action', 'Conflict']) or has_death
            
            delta = abs(curr_sig - prev_sig)
            if delta > 0.65 and is_anchor_scene:  # Raised threshold to reduce false positive spikes
                whiplash_candidates.append((i, delta))

        # 8. Cognitive Resonance (The 'Perfect' Scene)
        resonance_candidates = []
        for i in range(len(temporal_trace)):
            res = temporal_trace[i].get('cognitive_resonance', 0)
            if res > 0.85:
                resonance_candidates.append((i, res))

        # --- Task: Mutual Exclusion Rule (Re-implemented for stability) ---
        final_whiplash = []
        final_resonance = []
        
        # Track which scenes have already been 'claimed' by one signal
        claimed_scenes = {}
        
        # Group all signals by index
        all_signals = []
        for idx, val in whiplash_candidates:
            all_signals.append({'idx': idx, 'type': 'whiplash', 'val': val})
        for idx, val in resonance_candidates:
            all_signals.append({'idx': idx, 'type': 'resonance', 'val': val})
            
        # Sort by value descending so the strongest signal 'wins' the scene
        all_signals.sort(key=lambda x: x['val'], reverse=True)
        
        for sig in all_signals:
            idx = sig['idx']
            if idx not in claimed_scenes:
                claimed_scenes[idx] = sig['type']
                if sig['type'] == 'whiplash':
                    final_whiplash.append(idx)
                else:
                    final_resonance.append(idx)

        # Now add filtered diagnostics to result
        for idx in sorted(final_whiplash)[:1]: # Show only the primary whiplash
            snippet = self._get_snippet(scenes[idx])
            diagnosis.append(f"🎢 **Tonal Whiplash (Scene {idx+1})**: Extreme shift in tension anchored by a sharp narrative turn. (e.g., {snippet})")
            
        for idx in sorted(final_resonance)[:1]: # Show only the primary resonance
            snippet = self._get_snippet(scenes[idx])
            diagnosis.append(f"💎 **Cognitive Resonance (Scene {idx+1})**: High harmonization of narrative conflict and emotional impact. (e.g., {snippet})")

        # 7. Similar Name Confusion
        for i in range(len(features)):
            frustration = features[i].get('reader_frustration', {})
            similar_pairs = frustration.get('similar_name_pairs', [])
            if similar_pairs:
                diagnosis.append(
                    f"🧠 **Audience Confusion (Scene {i+1})**: Characters with similar names ({', '.join(similar_pairs)}) may confuse the reader."
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
