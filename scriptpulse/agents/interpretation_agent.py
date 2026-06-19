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
        # FIX: Horror requires STRONGLY negative sentiment (< -0.6) NOT just any negative scene.
        # Drama scripts routinely have negative scenes; using -0.3 causes huge false positive rate.
        horror_sentiment = 0  # Track STRONGLY negative sentiment for horror
        comedy_sentiment = 0  # Track positive sentiment for comedy
        semantic_patterns = 0  # Track genre-specific patterns
        structural_signals = 0  # Track pacing/tension patterns
        
        # FIX: Count explicit genre-specific keywords at scene text level
        horror_explicit = 0   # Tracks actual horror keywords in scene text
        fantasy_explicit = 0  # Tracks actual fantasy keywords in scene text
        
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
            
            # FIX: Only count horror_sentiment if sentiment is VERY strongly negative
            # Drama scripts regularly score -0.3 to -0.5 during conflict/tragedy — this is NOT horror.
            sentiment = scene.get('sentiment', 0)
            if sentiment < -0.6:  # Only extreme negativity signals horror
                horror_sentiment += 1
            elif sentiment > 0.2:  # Positive sentiment
                comedy_sentiment += 1
            
            # FIX: Count explicit horror/fantasy keywords directly in scene text
            if any(word in text_content for word in ['ghost', 'demon', 'haunt', 'monster', 'possess', 'curse', 'scream', 'nightmare', 'zombie', 'vampire', 'undead']):
                horror_explicit += 1
            if any(word in text_content for word in ['magic', 'wizard', 'witch', 'dragon', 'kingdom', 'spell', 'prophecy', 'elf', 'enchant', 'sorcerer', 'realm']):
                fantasy_explicit += 1
            
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
        
        total_scenes = max(1, len(temporal_trace))
        
        # FIX: EXPLICIT KEYWORD GATE — Horror and Fantasy must have ACTUAL keywords,
        # not just inferred from sentiment or tension. A drama with sad scenes is NOT horror.
        # Require at least 10% of scenes to contain explicit genre markers.
        horror_threshold = max(3, total_scenes * 0.10)
        fantasy_threshold = max(3, total_scenes * 0.10)
        
        # AI-enhanced genre detection — only trust if we have explicit content evidence
        ai_genre = self._ai_genre_detection(temporal_trace, features)
        if ai_genre:
            # FIX: Validate AI genre predictions against explicit keyword evidence
            # before accepting them. AI zero-shot can hallucinate on ambiguous drama.
            if ai_genre == 'horror' and horror_explicit < horror_threshold:
                ai_genre = None  # Reject — no explicit horror markers
            elif ai_genre == 'fantasy' and fantasy_explicit < fantasy_threshold:
                ai_genre = None  # Reject — no explicit fantasy markers
        if ai_genre:
            return ai_genre
            
        # Enhanced heuristic detection as fallback
        heuristic_genre = self._heuristic_genre_detection(
            crime_keywords, family_themes, dialogue_heavy, action_heavy,
            comedy_sentiment, horror_sentiment, temporal_trace,
            horror_explicit=horror_explicit, fantasy_explicit=fantasy_explicit
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
                        f"🟠 **Dense Introduction (Scene {i+1})**: This scene introduces many names quickly — consider spacing character introductions across scenes for clarity. (e.g., {snippet})"
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
                        f"🟠 **Pacing Opportunity (Scene {i+1})**: This section has a quieter rhythm — consider adding a small dramatic beat or reveal to sustain forward momentum. (e.g., {snippet})"
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
                    f"💡 **Exposition Opportunity (Scene {i+1})**: Dense information here — consider weaving key facts into dialogue or a dramatic discovery to keep momentum high. (e.g., {snippet})"
                )
                break

        # 5. Visual Opportunity (High Dialogue, Low Action, Mid Tension)
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            dial = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if dial > 15 and action < 2 and 0.4 < att_sig < 0.6:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🗣️ **Visual Opportunity (Scene {i+1})**: Dialogue-rich scene — consider adding physical movement or environmental detail to create visual contrast. (e.g., {snippet})"
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
                    f"🧠 **Clarity Note (Scene {i+1})**: Characters with similar names ({', '.join(similar_pairs)}) — consider differentiating to help readers track them effortlessly."
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
    def map_to_custom_framework(self, trace, framework_type='3_act'):
        if framework_type == 'heros_journey':
            total = len(trace)
            if total < 4:
                return {
                    'acts': [
                        {'name': 'Ordinary World & Call to Adventure', 'range': [0, max(0, total-1)]}
                    ],
                    'beats': []
                }
            ordinary_world_end = max(0, int(total * 0.15))
            crossing_threshold = max(ordinary_world_end + 1, int(total * 0.35))
            ordeal = max(crossing_threshold + 1, int(total * 0.70))
            
            acts = [
                {'name': 'Ordinary World', 'range': [0, ordinary_world_end]},
                {'name': 'Crossing the Threshold', 'range': [ordinary_world_end + 1, crossing_threshold]},
                {'name': 'The Ordeal', 'range': [crossing_threshold + 1, ordeal]},
                {'name': 'Return with the Elixir', 'range': [ordeal + 1, total - 1]}
            ]
            beats = [
                {'name': 'Call to Adventure', 'scene_index': max(0, ordinary_world_end - 1)},
                {'name': 'Supreme Ordeal', 'scene_index': int(total / 2)}
            ]
            return {'acts': acts, 'beats': beats}
        
        return self.map_to_structure(trace)

    def audit_narrative_intelligence(self, scenes, trace):
        import collections
        motifs = ['gun', 'weapon', 'bomb', 'knife', 'letter', 'secret']
        scene_motifs = collections.defaultdict(list)
        
        for i, scene in enumerate(scenes):
            scene_text = " ".join([l.get('text', '') for l in scene.get('lines', [])]).lower()
            for motif in motifs:
                if motif in scene_text:
                    scene_motifs[motif].append(i)
                    
        intelligence = []
        for motif, scene_indices in scene_motifs.items():
            if len(scene_indices) == 1:
                idx = scene_indices[0]
                intelligence.append({
                    'type': 'Dropped Thread',
                    'issue': f"Dropped Thread: '{motif.capitalize()}' was set up in Scene {idx+1} but never paid off in later scenes.",
                    'advice': f"Consider resolving the setup of the '{motif}' in subsequent scenes, or remove the setup if it does not serve the plot."
                })
        return intelligence

    def calculate_conflict_typology(self, encoded, valence):
        typology = []
        
        external_keywords = {'runs', 'leaps', 'rolls', 'fires', 'bullets', 'rooftop', 'gunfight', 'chase', 'combat', 'jump', 'fall', 'hit', 'shot'}
        social_keywords = {'where', 'busy', 'why', 'what', 'you', 'me', 'who', 'say', 'tell', 'hear', 'conversation', 'talk', 'argue', 'angry'}
        internal_keywords = {'letter', 'ponder', 'regret', 'dread', 'feels', 'thinks', 'wonder', 'mind', 'memory', 'clock', 'solitude', 'lonely'}
        
        for i, feat in enumerate(encoded):
            text = " ".join([line.get('text', '') for line in feat.get('micro_structure', [])]).lower()
            
            ext_score = sum(1 for w in external_keywords if w in text)
            soc_score = sum(1 for w in social_keywords if w in text)
            int_score = sum(1 for w in internal_keywords if w in text)
            
            dial_dynamics = feat.get('dialogue_dynamics', {})
            vis_dynamics = feat.get('visual_abstraction', {})
            
            ext_score += vis_dynamics.get('visual_intensity', 0.0) * 5.0
            ext_score += vis_dynamics.get('action_lines', 0) * 0.5
            
            soc_score += dial_dynamics.get('turn_velocity', 0.0) * 5.0
            soc_score += dial_dynamics.get('speaker_switches', 0) * 0.5
            
            ling = feat.get('linguistic_load', {})
            int_score += ling.get('idea_density', 0.0) * 3.0
            if ling.get('mean_sentence_length', 0) > 15:
                int_score += 2.0
                
            ext_score = max(0.1, ext_score)
            soc_score = max(0.1, soc_score)
            int_score = max(0.1, int_score)
            
            total = ext_score + soc_score + int_score
            ext_norm = round(ext_score / total, 2)
            soc_norm = round(soc_score / total, 2)
            int_norm = round(int_score / total, 2)
            
            scores = {'External': ext_norm, 'Social': soc_norm, 'Internal': int_norm}
            dominant = max(scores, key=lambda k: scores[k])
            
            typology.append({
                'scene_index': feat.get('scene_index', i),
                'dominant': dominant,
                'external': ext_norm,
                'social': soc_norm,
                'internal': int_norm
            })
        return typology

    def track_thematic_recurrence(self, encoded):
        echoes = []
        n = len(encoded)
        if n < 3: return echoes
        
        thematic_motifs = {'rose', 'crimson', 'petal', 'gun', 'blood', 'family', 'gold', 'ring', 'shadow', 'clock'}
        
        for i in range(n):
            vocab_i = set(encoded[i].get('scene_vocabulary', []))
            motifs_i = vocab_i.intersection(thematic_motifs)
            if not motifs_i:
                continue
                
            for j in range(i + 2, n):
                vocab_j = set(encoded[j].get('scene_vocabulary', []))
                motifs_j = vocab_j.intersection(thematic_motifs)
                
                shared = motifs_i.intersection(motifs_j)
                if shared:
                    sim = len(shared) / max(1, min(len(motifs_i), len(motifs_j)))
                    echoes.append({
                        'scenes': [i, j],
                        'similarity': round(sim, 2),
                        'shared_motifs': sorted(list(shared))
                    })
        return echoes

    def map_interaction_networks(self, scenes, typologies=None):
        import collections
        scene_speakers = []
        all_chars = set()
        for scene in scenes:
            speakers = set()
            for line in scene.get('lines', []):
                if line.get('tag') == 'C':
                    name = line.get('text', '').split('(')[0].strip().upper()
                    from scriptpulse.agents.perception_agent import normalize_character_name
                    norm_name = normalize_character_name(name)
                    if norm_name:
                        speakers.add(norm_name)
                        all_chars.add(norm_name)
            scene_speakers.append(speakers)

        edge_weights = collections.defaultdict(int)
        for speakers in scene_speakers:
            sorted_spk = sorted(list(speakers))
            for i in range(len(sorted_spk)):
                for j in range(i + 1, len(sorted_spk)):
                    pair = (sorted_spk[i], sorted_spk[j])
                    edge_weights[pair] += 1

        edges = []
        adjacency = collections.defaultdict(set)
        for (src, dst), weight in edge_weights.items():
            if weight >= 1:
                edges.append({'source': src, 'target': dst, 'weight': weight})
                adjacency[src].add(dst)
                adjacency[dst].add(src)

        triangles = []
        sorted_nodes = sorted(list(all_chars))
        for i in range(len(sorted_nodes)):
            for j in range(i + 1, len(sorted_nodes)):
                for k in range(j + 1, len(sorted_nodes)):
                    n1, n2, n3 = sorted_nodes[i], sorted_nodes[j], sorted_nodes[k]
                    if n2 in adjacency[n1] and n3 in adjacency[n1] and n3 in adjacency[n2]:
                        triangles.append([n1, n2, n3])

        return {
            'edges': edges,
            'triangles': triangles
        }
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
                                action_heavy, comedy_sentiment, horror_sentiment, temporal_trace,
                                horror_explicit=0, fantasy_explicit=0):
        """
        UNIVERSAL genre detection — every genre must have its own POSITIVE EVIDENCE.
        
        Design principles:
        1. Drama is the safe default. ALL other genres must earn the label.
        2. Sentiment & tension alone NEVER classify a genre. They are shared across all genres.
        3. Every genre has a dedicated keyword vocabulary. Overlap is minimised.
        4. A genre must beat drama's score by a MEANINGFUL MARGIN (40%) to win.
        5. Keyword thresholds scale with script length (% of scenes, not fixed counts).
        """
        total_scenes = len(temporal_trace)
        if total_scenes < 3:
            return 'drama'

        # ── Structural signals (shared, not genre-defining alone) ────────────
        dialogue_ratio = dialogue_heavy / max(1, dialogue_heavy + action_heavy)
        action_ratio   = action_heavy   / max(1, dialogue_heavy + action_heavy)
        tension_peaks  = sum(1 for s in temporal_trace if s.get('attentional_signal', 0) > 0.7)
        avg_tension    = sum(s.get('attentional_signal', 0) for s in temporal_trace) / total_scenes

        # ── Per-scene keyword counting (single pass) ─────────────────────────
        # Each vocabulary is EXCLUSIVE to its genre — no shared terms.
        # Generic words that appear in many genres are intentionally excluded.
        kw = {
            'crime_strong': 0,
            'crime_weak':   0,
            'horror':    0,
            'fantasy':   0,
            'scifi':     0,
            'action':    0,
            'comedy':    0,
            'romance':   0,
            'psych':     0,
            'western':   0,
        }

        CRIME_STRONG  = {'mafia', 'mob', 'gang', 'cartel', 'don', 'corleone', 'hitman',
                         'assassin', 'heist', 'smugg', 'racket', 'narco'}
        CRIME_WEAK    = {'detective', 'investigat', 'interrogat', 'forensic', 'suspect',
                         'evidence', 'witness', 'alibi', 'arrest', 'prison', 'jail',
                         'cop', 'police', 'fbi', 'cia', 'interpol', 'criminal', 'convict'}
        HORROR_KW     = {'ghost', 'demon', 'haunt', 'monster', 'possess', 'curse',
                         'scream', 'nightmare', 'zombie', 'vampire', 'undead', 'apparit',
                         'poltergeist', 'exorcis', 'supernatural', 'satanic', 'wraith',
                         'specter', 'spectre', 'eldritch', 'entity'}
        FANTASY_KW    = {'magic', 'wizard', 'witch', 'dragon', 'sorcerer', 'enchant',
                         'prophecy', 'elf', 'elves', 'dwarf', 'realm', 'kingdom',
                         'quest', 'rune', 'alchemy', 'warlock', 'mage', 'paladin',
                         'orc', 'goblin', 'fairy', 'faerie', 'mythic', 'spellcast'}
        SCIFI_KW      = {'spaceship', 'starship', 'alien', 'robot', 'android', 'cyborg',
                         'hologram', 'warp', 'galactic', 'interstellar', 'extraterrest',
                         'quantum', 'nanotech', 'cryogen', 'terraform', 'lightyear',
                         'wormhole', 'dystopia', 'utopia', 'cyberpunk', 'biopunk',
                         'clone', 'mutant', 'ai overlord', 'neural implant'}
        ACTION_KW     = {'chase', 'gunfight', 'shootout', 'explosion', 'ambush',
                         'brawl', 'martial art', 'sniper', 'detonate', 'firefight',
                         'combat', 'mission', 'infiltrat', 'mercenary', 'spec ops',
                         'airstrike', 'squad', 'platoon', 'commando'}
        COMEDY_KW     = {'joke', 'laugh', 'hilarious', 'comedic', 'punchline',
                         'slapstick', 'wisecrack', 'banter', 'farce', 'absurd',
                         'sitcom', 'parody', 'satire', 'quip', 'witty', 'snarky',
                         'comedians', 'stand-up', 'gag', 'spoof', 'zany'}
        ROMANCE_KW    = {'romance', 'romantic', 'kissing', 'kisses', 'flirt', 'serenade',
                         'courtship', 'sweetheart', 'beloved', 'darling', 'lover', 'dating',
                         'propose', 'engagement', 'honeymoon', 'infatuat', 'enamored',
                         'rendezvous', 'admirer', 'valentine', 'courtship'}
        PSYCH_KW      = {'manipulat', 'gaslighting', 'delusion', 'hallucin',
                         'paranoia', 'dissociat', 'alter ego', 'split personality',
                         'unreliable', 'mind control', 'brainwash', 'obsession',
                         'stalker', 'psychopath', 'sociopath', 'narcissist'}
        WESTERN_KW    = {'sheriff', 'outlaw', 'cowboy', 'saloon', 'frontier',
                         'gunslinger', 'bandit', 'ranch', 'posse', 'bounty hunter',
                         'lawman', 'duel', 'wild west', 'horseback', 'stagecoach'}

        # Count SCENES that have at least one hit (not total hits across all scenes)
        # This makes pct_scenes() correctly measure "what fraction of scenes mention this genre"
        scene_kw_hits = {
            'crime_strong': 0, 'crime_weak': 0, 'horror': 0, 'fantasy': 0,
            'scifi': 0, 'action': 0, 'comedy': 0, 'romance': 0, 'psych': 0, 'western': 0
        }

        for scene in temporal_trace:
            raw_vals = " ".join(str(v) for v in scene.values()).lower()
            # Crime
            if any(w in raw_vals for w in CRIME_STRONG): scene_kw_hits['crime_strong'] += 1
            if any(w in raw_vals for w in CRIME_WEAK):   scene_kw_hits['crime_weak']   += 1
            # Genre-specific
            if any(w in raw_vals for w in HORROR_KW):    scene_kw_hits['horror']        += 1
            if any(w in raw_vals for w in FANTASY_KW):   scene_kw_hits['fantasy']       += 1
            if any(w in raw_vals for w in SCIFI_KW):     scene_kw_hits['scifi']         += 1
            if any(w in raw_vals for w in ACTION_KW):    scene_kw_hits['action']        += 1
            if any(w in raw_vals for w in COMEDY_KW):    scene_kw_hits['comedy']        += 1
            if any(w in raw_vals for w in ROMANCE_KW):   scene_kw_hits['romance']       += 1
            if any(w in raw_vals for w in PSYCH_KW):     scene_kw_hits['psych']         += 1
            if any(w in raw_vals for w in WESTERN_KW):   scene_kw_hits['western']       += 1
            # Legacy kw counts (kept for score weighting, not thresholding)
            kw['crime_strong'] += sum(1 for w in CRIME_STRONG if w in raw_vals)
            kw['crime_weak']   += sum(1 for w in CRIME_WEAK   if w in raw_vals)
            kw['horror']       += sum(1 for w in HORROR_KW    if w in raw_vals)
            kw['fantasy']      += sum(1 for w in FANTASY_KW   if w in raw_vals)
            kw['scifi']        += sum(1 for w in SCIFI_KW     if w in raw_vals)
            kw['action']       += sum(1 for w in ACTION_KW    if w in raw_vals)
            kw['comedy']       += sum(1 for w in COMEDY_KW    if w in raw_vals)
            kw['romance']      += sum(1 for w in ROMANCE_KW   if w in raw_vals)
            kw['psych']        += sum(1 for w in PSYCH_KW     if w in raw_vals)
            kw['western']      += sum(1 for w in WESTERN_KW   if w in raw_vals)

        family_marker_count = 0
        for scene in temporal_trace:
            raw_vals = " ".join(str(v) for v in scene.values()).lower()
            if any(w in raw_vals for w in ['family', 'father', 'mother', 'son', 'daughter',
                                            'husband', 'wife', 'sibling', 'grief', 'funeral',
                                            'divorce', 'custody', 'inheritance']):
                family_marker_count += 1

        def pct_scenes(genre_key, pct=0.10):
            """Returns True if at least pct% of scenes mention this genre's keywords."""
            return scene_kw_hits[genre_key] >= max(2, total_scenes * pct)

        genre_scores = {}
        drama_score = (
            (dialogue_ratio * 3.0) +
            (family_marker_count * 0.15) +
            (avg_tension * 0.5)
        )
        genre_scores['drama'] = max(1.0, drama_score)

        crime_strong_hit = scene_kw_hits['crime_strong'] >= max(2, total_scenes * 0.06)
        crime_weak_hit   = scene_kw_hits['crime_weak']   >= max(3, total_scenes * 0.12)
        if crime_strong_hit:
            crime_score = (
                (kw['crime_strong'] * 2.5) +
                (kw['crime_weak'] * 0.8) +
                (tension_peaks * 0.4)
            )
            genre_scores['crime drama'] = crime_score
            if tension_peaks >= max(3, total_scenes * 0.12) and avg_tension > 0.45:
                genre_scores['crime thriller'] = crime_score * 1.2
        elif crime_weak_hit and tension_peaks >= max(3, total_scenes * 0.12):
            crime_score = (kw['crime_weak'] * 1.0) + (tension_peaks * 0.5)
            if crime_score > drama_score * 1.4:
                genre_scores['thriller'] = crime_score

        if pct_scenes('horror', pct=0.10):
            horror_score = (
                (kw['horror'] * 4.0) +
                (horror_sentiment * 1.0) +
                (tension_peaks * 0.3)
            )
            genre_scores['horror'] = horror_score

        if pct_scenes('fantasy', pct=0.10):
            fantasy_score = (
                (kw['fantasy'] * 4.0) +
                (avg_tension * 0.5)
            )
            genre_scores['fantasy'] = fantasy_score

        if pct_scenes('scifi', pct=0.08):
            scifi_score = (
                (kw['scifi'] * 3.5) +
                (avg_tension * 0.5)
            )
            genre_scores['sci-fi'] = scifi_score

        # ACTION: requires explicit combat/tactical vocabulary AND either action-dominant
        # scene structure OR a clear keyword density. The action_ratio param is from
        # detect_genre's loop; if called standalone, fall back to pure keyword density.
        action_density_ok = (action_ratio > 0.40) or pct_scenes('action', pct=0.15)
        if pct_scenes('action', pct=0.08) and action_density_ok:
            action_score = (
                (kw['action'] * 2.5) +
                (action_ratio * 3.0) +
                (tension_peaks * 0.4)
            )
            genre_scores['action'] = action_score

        if pct_scenes('comedy', pct=0.08):
            comedy_score = (
                (kw['comedy'] * 3.0) +
                (comedy_sentiment * 1.0) +
                (dialogue_ratio * 1.0)
            )
            genre_scores['comedy'] = comedy_score

        if pct_scenes('romance', pct=0.12):
            romance_score = (
                (kw['romance'] * 3.0) +
                (comedy_sentiment * 0.8) +
                (dialogue_ratio * 1.0)
            )
            genre_scores['romance'] = romance_score

        if pct_scenes('psych', pct=0.08) and (tension_peaks >= max(2, total_scenes * 0.10) or avg_tension >= 0.55):

            psych_score = (
                (kw['psych'] * 3.5) +
                (avg_tension * 1.0) +
                (tension_peaks * 0.3)
            )
            genre_scores['psychological thriller'] = psych_score

        if pct_scenes('western', pct=0.08):
            western_score = (
                (kw['western'] * 4.0) +
                (action_ratio * 1.5)
            )
            genre_scores['western'] = western_score

        # THRILLER (generic fallback) — must have both crime/investigative signals AND
        # meaningful tension. Tension alone (even very high) is NOT a thriller signal —
        # dramas, horror, and action all have high tension.
        # Gate: requires crime_weak keywords PLUS tension, not either alone.
        thriller_raw = (kw['crime_weak'] * 1.2) + (action_ratio * 1.5)
        has_crime_signal = scene_kw_hits['crime_weak'] >= max(2, total_scenes * 0.08)
        has_tension_signal = tension_peaks >= max(3, total_scenes * 0.12)
        if thriller_raw > 4.0 and has_crime_signal and has_tension_signal and 'crime drama' not in genre_scores and 'action' not in genre_scores:
            genre_scores['thriller'] = thriller_raw

        if genre_scores:
            drama_s = genre_scores.get('drama', 1.0)
            ranked = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
            winner_genre, winner_score = ranked[0]
            if winner_genre == 'drama':
                return 'drama'
            if winner_score > drama_s * 1.40 and winner_score >= 3.0:
                return winner_genre

        return 'drama'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
