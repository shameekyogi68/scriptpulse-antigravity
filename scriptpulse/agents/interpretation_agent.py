# MODULE: interpretation_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Interpretation Agent - Text-Grounded Cognitive Version
Translates mathematical signals into true human "First Reader" experiences.
Focuses on: Confusion, Boredom, Visceral Reaction, and Textual Proof.
"""

import statistics
import random
import re
from ..utils.model_manager import manager

class InterpretationAgent:
    """AI-Enhanced Cognitive Translation Layer - From Data to Human Experience"""

    def __init__(self):
        # Human Experience Labels for UI
        self.LABELS = {
            'High': "Gripping / Intense",
            'Medium': "Engaging / Steady",
            'Low': "Slow / Breather"
        }
        self.model_manager = manager
        self.zero_shot_classifier = None
        self._init_ai_models()

    def _init_ai_models(self):
        """Initialize AI models for enhanced analysis"""
        try:
            self.zero_shot_classifier = self.model_manager.get_zero_shot()
        except:
            self.zero_shot_classifier = None

    def detect_genre(self, temporal_trace, features=None):
        """
        Advanced genre detection using ALL available signals:
        - Content analysis (themes, dialogue patterns)
        - Sentiment analysis (emotional tone)
        - Semantic patterns (scene types, transitions)
        - Structural analysis (pacing, tension)
        - AI-powered classification when available
        """
        if not temporal_trace:
            return 'drama'  # Default fallback
        
        # Initialize enhanced analysis variables
        dialogue_heavy = 0
        action_heavy = 0
        crime_keywords = 0
        family_themes = 0
        horror_sentiment = 0  # Track negative sentiment for horror
        comedy_sentiment = 0  # Track positive sentiment for comedy
        semantic_patterns = 0  # Track genre-specific patterns
        structural_signals = 0  # Track pacing/tension patterns
        
        for scene in temporal_trace:
            # Check dialogue vs action balance
            dialogue_ratio = scene.get('dialogue_action_ratio', {}).get('scene_dialogue_ratio', 0.5)
            if dialogue_ratio > 0.6:
                dialogue_heavy += 1
            elif dialogue_ratio < 0.4:
                action_heavy += 1
            
            # Check for crime/family themes in text
            text_content = " ".join([str(v) for v in scene.values()]).lower()
            if any(word in text_content for word in ['mafia', 'crime', 'murder', 'investigation', 'gang', 'mob']):
                crime_keywords += 1
            if any(word in text_content for word in ['family', 'father', 'son', 'mother', 'corleone']):
                family_themes += 1
            
            # Analyze sentiment patterns for genre detection
            sentiment = scene.get('sentiment', 0)
            if sentiment < -0.3:  # Negative sentiment
                horror_sentiment += 1
            elif sentiment > 0.2:  # Positive sentiment
                comedy_sentiment += 1
            
            # Enhanced semantic pattern analysis
            scene_type = scene.get('scene_type', '').lower()
            if 'investigation' in scene_type or 'interrogation' in scene_type:
                crime_keywords += 1
            if 'romantic' in scene_type or 'date' in scene_type:
                family_themes += 1
            if 'chase' in scene_type or 'explosion' in scene_type:
                action_heavy += 1
            if 'laugh' in scene_type or 'joke' in scene_type:
                comedy_sentiment += 1
            
            # Structural signal analysis
            attention = scene.get('attentional_signal', 0)
            if attention > 0.8:  # High tension
                structural_signals += 1
            elif attention < 0.3:  # Low tension
                structural_signals += 1
        
        # AI-enhanced genre detection
        ai_genre = self._ai_genre_detection(temporal_trace, features)
        if ai_genre:
            return ai_genre
            
        # Enhanced heuristic detection as fallback
        heuristic_genre = self._heuristic_genre_detection(
            crime_keywords, family_themes, dialogue_heavy, action_heavy,
            comedy_sentiment, horror_sentiment, temporal_trace
        )
        return heuristic_genre or 'drama'  # Default fallback

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
        
        def _find_act_boundary(signals, search_range):
            """Find the lowest attentional signal in a range = likely act break."""
            segment = signals[search_range[0]:search_range[1]]
            if not segment:
                return search_range[0]
            min_idx = segment.index(min(segment, key=lambda s: s['attentional_signal']))
            return search_range[0] + min_idx
        
        # Dynamic act boundaries using attentional signal valleys
        # Act 1 boundary between 20%–30%
        a1_search_start = int(total * 0.20)
        a1_search_end = int(total * 0.30)
        a1_end = _find_act_boundary(temporal_trace, [a1_search_start, a1_search_end])
        
        # Act 2 boundary between 60%–80%
        a2_search_start = int(total * 0.60)
        a2_search_end = int(total * 0.80)
        a2_end = _find_act_boundary(temporal_trace, [a2_search_start, a2_search_end])
        
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
            
        # Minimum scene thresholds per diagnostic type
        MIN_SCENES_FOR_SAG = 8         # Need 8 scenes before a sag is meaningful
        MIN_SCENES_FOR_OVERCROWD = 5   # Need 5 scenes to flag character churn
        
        signals = [s['attentional_signal'] for s in temporal_trace]
        
        # Pacing Threshold Adjustment by Genre
        sag_limit = 0.35 if genre.lower() == 'drama' else 0.45 
        sag_scenes = 3 if genre.lower() == 'drama' else 2 
            
        # 1. Overcrowded Narrative
        if len(temporal_trace) >= MIN_SCENES_FOR_OVERCROWD:
            for i in range(len(temporal_trace)):
                feat = features[i]
                att_sig = temporal_trace[i]['attentional_signal']
                churn = feat.get('referential_load', {}).get('character_churn', 0.0)
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
        if len(temporal_trace) >= MIN_SCENES_FOR_SAG:
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
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            entropy = feat.get('entropy_score', 0)
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

    def _ai_genre_detection(self, temporal_trace, features):
        """
        AI-powered genre detection using DeBERTa zero-shot classification.
        Stratified sampling: takes up to 15 scenes across Act 1, Act 2, Act 3
        for a representative full-script read rather than just the opening 5 scenes.
        Falls back gracefully if models are unavailable.
        """
        if not self.zero_shot_classifier or not temporal_trace:
            return None
            
        try:
            # Stratified sampling: pick scenes from beginning, middle, and end of script
            n = len(temporal_trace)
            indices = set()
            # 5 from Act 1 (first 30%)
            a1_end = max(1, int(n * 0.30))
            indices.update(range(0, a1_end, max(1, a1_end // 5)))
            # 5 from Act 2 (30%-70%)
            a2_start, a2_end = a1_end, max(a1_end + 1, int(n * 0.70))
            step = max(1, (a2_end - a2_start) // 5)
            indices.update(range(a2_start, a2_end, step))
            # 5 from Act 3 (last 30%)
            a3_start = int(n * 0.70)
            step = max(1, (n - a3_start) // 5)
            indices.update(range(a3_start, n, step))
            indices = sorted(indices)[:15]  # Cap at 15

            text_samples = []
            for i in indices:
                if features and i < len(features):
                    feat = features[i]
                    dialogue_text = " ".join([
                        l.get('text', '') for l in feat.get('micro_structure', [])
                        if l.get('tag') == 'D'
                    ])
                    action_text = " ".join([
                        l.get('text', '') for l in feat.get('micro_structure', [])
                        if l.get('tag') == 'A'
                    ])
                    combined = f"{dialogue_text} {action_text}".strip()
                    if len(combined) > 50:
                        text_samples.append(combined[:400])
            
            if not text_samples:
                return None
                
            candidate_labels = [
                'drama', 'comedy', 'action', 'horror', 'thriller', 
                'crime drama', 'sci-fi', 'fantasy', 'romance', 'western'
            ]
            
            combined_text = " ".join(text_samples)
            if len(combined_text) < 100:
                return None
                
            result = self.zero_shot_classifier(
                combined_text[:1024],
                candidate_labels,
                multi_label=False
            )
            
            if result and result.get('labels'):
                top_genre = result['labels'][0]
                confidence = result['scores'][0] if result.get('scores') else 0
                
                # Require higher confidence since we have better coverage now
                if confidence > 0.35:
                    return top_genre
                    
        except Exception:
            pass
            
        return None

    def _heuristic_genre_detection(self, crime_keywords, family_themes, dialogue_heavy, 
                                action_heavy, comedy_sentiment, horror_sentiment, temporal_trace):
        """
        Sophisticated genre detection with weighted scoring system
        """
        total_scenes = len(temporal_trace)
        if total_scenes < 3:
            return 'drama'
            
        # Calculate content ratios
        dialogue_ratio = dialogue_heavy / max(1, dialogue_heavy + action_heavy)
        action_ratio = action_heavy / max(1, dialogue_heavy + action_heavy)
        
        # Analyze tension patterns
        tension_peaks = sum(1 for s in temporal_trace if s.get('attentional_signal', 0) > 0.7)
        avg_tension = sum(s.get('attentional_signal', 0) for s in temporal_trace) / total_scenes
        
        # Enhanced keyword analysis
        romance_keywords = 0
        psychological_keywords = 0
        for scene in temporal_trace:
            text_content = " ".join([str(v) for v in scene.values()]).lower()
            if any(word in text_content for word in ['love', 'romance', 'relationship', 'dating', 'marriage']):
                romance_keywords += 1
            if any(word in text_content for word in ['mind', 'psychological', 'mental', 'therapy', 'trauma']):
                psychological_keywords += 1
        
        # Genre scoring system
        genre_scores = {}
        
        # Crime Thriller: crime + family/drama elements
        if crime_keywords >= 2:
            crime_score = (crime_keywords * 2) + (family_themes * 1.5) + (tension_peaks * 0.5)
            genre_scores['crime_thriller'] = crime_score
        
        # Horror: negative sentiment + high tension peaks + low dialogue
        if horror_sentiment >= 2 or tension_peaks >= 5:
            horror_score = (horror_sentiment * 2) + (tension_peaks * 1.2) + ((1 - dialogue_ratio) * 3)
            genre_scores['horror'] = horror_score
        
        # Action: high action ratio + tension peaks
        if action_ratio > 0.5 and tension_peaks >= 3:
            action_score = (action_ratio * 3) + (tension_peaks * 1.5)
            genre_scores['action'] = action_score
        
        # Thriller: moderate action + tension + crime elements
        thriller_score = (action_ratio * 2) + (tension_peaks * 1) + (crime_keywords * 1.5)
        genre_scores['thriller'] = thriller_score
        
        # Comedy: high positive sentiment + dialogue-heavy
        if comedy_sentiment >= 2 or dialogue_ratio > 0.7:
            comedy_score = (comedy_sentiment * 2) + (dialogue_ratio * 2) + (avg_tension * 0.5)
            genre_scores['comedy'] = comedy_score
        
        # Romance: romance keywords + positive sentiment
        if romance_keywords >= 2:
            romance_score = (romance_keywords * 2) + (comedy_sentiment * 1) + (dialogue_ratio * 1.5)
            genre_scores['romance'] = romance_score
        
        # Psychological: psychological keywords + complex themes
        if psychological_keywords >= 2:
            psych_score = (psychological_keywords * 2) + (dialogue_ratio * 1) + (avg_tension * 1)
            genre_scores['psychological_thriller'] = psych_score
        
        # Sci-Fi: technology/science keywords + intellectual content
        scifi_keywords = 0
        for scene in temporal_trace:
            text_content = " ".join([str(v) for v in scene.values()]).lower()
            if any(word in text_content for word in ['technology', 'science', 'future', 'space', 'robot', 'alien', 'computer', 'system', 'digital', 'virtual']):
                scifi_keywords += 1
        
        if scifi_keywords >= 2:
            scifi_score = (scifi_keywords * 2) + (psychological_keywords * 1) + (avg_tension * 1.2)
            genre_scores['sci-fi'] = scifi_score
        
        # Drama: balanced content with dialogue/emotional elements
        drama_score = (dialogue_ratio * 1.5) + (family_themes * 1) + (avg_tension * 0.8)
        genre_scores['drama'] = drama_score
        
        # Return highest scoring genre
        if genre_scores:
            best_genre = max(genre_scores.items(), key=lambda x: x[1])
            return best_genre[0] if best_genre[1] > 2.0 else 'drama'
        
        return 'drama'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
