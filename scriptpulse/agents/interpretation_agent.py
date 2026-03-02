"""
Interpretation Agent - Logic, Reasoning, and Feedback
Consolidates: intent.py, ssf.py, uncertainty.py, ensemble_uncertainty.py, profiler.py, xai.py, scene_notes.py, suggestion.py
"""

import math
import statistics
import random

# =============================================================================
# MEDIATION CONSTANTS
# =============================================================================
WRITER_NATIVE_TRANSLATIONS = {
    'sustained_attentional_demand': (
        "This run of scenes stays intense without a release valve — "
        "the audience may feel pushed without a moment to recover."
    ),
    'limited_recovery': (
        "Fatigue accumulates here. "
        "Without a clear breather, the audience's capacity to track detail may drop."
    ),
    'repetition': (
        "This stretch risks feeling like more of the same — "
        "the audience may stop registering escalation."
    ),
    'surprise_cluster': (
        "The rhythm spikes sharply here. "
        "Without setup, this intensity risks feeling jarring rather than impactful."
    ),
    'constructive_strain': (
        "This section demands heavy lifting. "
        "The audience is working hard to keep up — ensure the payoff is worth the effort."
    ),
    # Fix 1 / Fix 9: Low engagement translation
    'low_engagement': (
        "The modeled attentional demand stays consistently low across these scenes. "
        "Is the audience's investment intentionally restrained here, or has forward momentum slowed?"
    ),
    'degenerative_fatigue': {
        'drift': (
            "The audience may start to drift here — "
            "this stretch risks losing grip unless something resets their focus."
        ),
        'collapse': (
            "The mental load here is becoming heavy. "
            "The audience may struggle to track new information effectively."
        )
    }
}

BANNED_WORDS = {
    'good', 'bad', 'fix', 'improve', 'optimize', 'too long', 'too short',
    'slow', 'fast', 'weak', 'strong', 'problem', 'issue', 'ideal', 'optimal',
    'tips', 'suggestions', 'advice', 'should', 'must', 'need to'
}

ADS_DISCLAIMERS = [
    "This reflects one modeled first-pass experience.",
    "Other readers may differ.",
    "This is not a statement about effectiveness.",
    "Attention varies by reader; this model tracks median structural load."
]

CREATIVE_BEAT_LABELS = {
    'high_strain_high_effort': "Action Climax / Intense Conflict",
    'high_strain_low_effort': "Suspenseful Build-Up",
    'low_strain_high_effort': "Dense Exposition / World-Building",
    'low_strain_low_effort': "Quiet Reflection / Breathing Room",
    'moderate_tension': "Steady Narrative Flow"
}

# =============================================================================
# INTENT LOGIC (formerly intent.py)
# =============================================================================

class InterpretationAgent:
    """Methods for interpreting analytical data into human-usable insight."""

    def __init__(self):
        self.ALLOWED_INTENTS = {
            'intentionally exhausting',
            'intentionally confusing',
            'should feel smooth',
            'should feel tense',
            'experimental / anti-narrative'
        }

    def apply_semantic_labels(self, temporal_trace, valence_trace=None):
        """Maps numeric signals to writer-safe story beat labels."""
        if not temporal_trace: return []
        
        labeled_trace = []
        for i, pt in enumerate(temporal_trace):
            strain = pt.get('attentional_signal', 0.5)
            effort = pt.get('instantaneous_effort', 0.5)
            val = valence_trace[i] if (valence_trace and i < len(valence_trace)) else 0.0
            
            label = CREATIVE_BEAT_LABELS['moderate_tension']
            
            if strain > 0.75:
                if effort > 0.6: label = CREATIVE_BEAT_LABELS['high_strain_high_effort']
                else: label = CREATIVE_BEAT_LABELS['high_strain_low_effort']
            elif strain < 0.35:
                if effort > 0.6: label = CREATIVE_BEAT_LABELS['low_strain_high_effort']
                else: label = CREATIVE_BEAT_LABELS['low_strain_low_effort']
            
            # Emotional modifiers
            sentiment = "Neutral"
            if val > 0.2: sentiment = "Positive / Hopeful"
            elif val < -0.2: sentiment = "Negative / Tragic"
            
            labeled_trace.append({
                'scene_index': pt['scene_index'],
                'primary_label': label,
                'emotional_undertone': sentiment,
                'composite_beat': f"{label} ({sentiment})"
            })
        return labeled_trace

    def map_to_structure(self, temporal_trace):
        """Detects Act boundaries and Key Beats (Inciting Incident, Midpoint, Climax)."""
        if not temporal_trace: return {}
        
        total = len(temporal_trace)
        if total < 5: return {'acts': [], 'beats': []}
        
        # 1. Traditional 3-Act Structure (Percentage based fallback)
        act_1_end = int(total * 0.25)
        act_2_end = int(total * 0.75)
        
        acts = [
            {'name': 'Act 1: Setup', 'range': [0, act_1_end]},
            {'name': 'Act 2: Confrontation', 'range': [act_1_end + 1, act_2_end]},
            {'name': 'Act 3: Resolution', 'range': [act_2_end + 1, total - 1]}
        ]
        
        # 2. Dynamic Beat Detection (Local peaks in strain)
        signals = [s.get('attentional_signal', 0) for s in temporal_trace]
        
        beats = []
        # Inciting Incident (Peak in first 20%)
        ii_window = signals[:int(total * 0.25)]
        if ii_window:
            ii_idx = ii_window.index(max(ii_window))
            beats.append({'name': 'Inciting Incident', 'scene_index': ii_idx})
            
        # Midpoint (Peak in middle 20%)
        m_start, m_end = int(total * 0.4), int(total * 0.6)
        mid_window = signals[m_start:m_end]
        if mid_window:
            mid_idx = m_start + mid_window.index(max(mid_window))
            beats.append({'name': 'Midpoint Turn', 'scene_index': mid_idx})
            
        # Climax (Max peak overall in last 25%)
        c_start = int(total * 0.75)
        cli_window = signals[c_start:]
        if cli_window:
            cli_idx = c_start + cli_window.index(max(cli_window))
            beats.append({'name': 'Narrative Climax', 'scene_index': cli_idx})
            
        return {'acts': acts, 'beats': beats}

    def map_archetypes(self, fingerprints):
        """Maps voice fingerprints to recognizable character archetypes."""
        if not fingerprints: return {}
        
        archetypes = {}
        for char, fp in fingerprints.items():
            agency = fp.get('agency', 0.0)
            complexity = fp.get('complexity', 0.5)
            positivity = fp.get('positivity', 0.0)
            punct = fp.get('punctuation_rate', 0.0)
            
            # Archetype Heuristics
            if agency > 0.4 and complexity < 0.4:
                arch = "The Stoic / Man of Action"
            elif agency > 0.4 and punct > 0.15:
                arch = "The Chaotic Rebel"
            elif complexity > 0.7 and positivity > 0.2:
                arch = "The Mentor / Guide"
            elif agency < -0.2 and complexity > 0.6:
                arch = "The Cerebral Observer"
            elif positivity < -0.3 and agency > 0.3:
                arch = "The Antagonist / Force of Nature"
            elif punct > 0.2 and complexity < 0.3:
                arch = "The Comic Relief"
            else:
                arch = "The Everyman"
                
            archetypes[char] = {
                'archetype': arch,
                'explanation': self._get_arch_explanation(arch, fp)
            }
        return archetypes

    def _get_arch_explanation(self, arch, fp):
        if "Stoic" in arch: return "Direct, high-agency dialogue with minimal fluff."
        if "Chaotic" in arch: return "High energy, fragmented, and assertive."
        if "Mentor" in arch: return "Complex, encouraging, and highly articulate."
        if "Cerebral" in arch: return "Introspective and sophisticated, but less physically active."
        if "Antagonist" in arch: return "Strong-willed, negative, and driving the conflict."
        if "Comic" in arch: return "High-punctuation, rapid, and playful."
        return "Balanced voice with standard narrative profile."

    def audit_subtext(self, scene_features, fingerprints):
        """Identifies characters who are 'speaking the plot' too literally."""
        if not scene_features: return []
        
        audits = []
        for feat in scene_features:
            otn = feat.get('on_the_nose', {}).get('on_the_nose_ratio', 0.0)
            scene_idx = feat.get('scene_index', 0)
            
            if otn > 0.4:
                audits.append({
                    'scene_index': scene_idx,
                    'severity': 'High' if otn > 0.6 else 'Moderate',
                    'issue': "Transparent Dialogue (On-the-Nose)",
                    'advice': "Character is stating their feelings/intent too directly. Try using subtext or physical action instead."
                })
        return audits

    def map_to_custom_framework(self, temporal_trace, framework_type='3_act'):
        """Maps the tension trace to alternative storytelling frameworks."""
        if not temporal_trace: return {}
        total = len(temporal_trace)
        if total < 5: return {'acts': [], 'beats': []}

        if framework_type == 'heros_journey':
            return self._map_heros_journey(total)
        elif framework_type == 'eight_sequences':
            return self._map_eight_sequences(total)
        
        # Fallback to standard 3-Act
        return self.map_to_structure(temporal_trace)

    def _map_heros_journey(self, total):
        """Standard 12-step Hero's Journey mapping."""
        steps = [
            ("Ordinary World", 0, 0.1),
            ("Call to Adventure", 0.1, 0.15),
            ("Refusal of the Call", 0.15, 0.2),
            ("Meeting the Mentor", 0.2, 0.25),
            ("Crossing the Threshold", 0.25, 0.3),
            ("Tests, Allies, Enemies", 0.3, 0.5),
            ("Approach to the Inmost Cave", 0.5, 0.6),
            ("The Ordeal", 0.6, 0.7),
            ("The Reward", 0.7, 0.75),
            ("The Road Back", 0.75, 0.85),
            ("Resurrection", 0.85, 0.95),
            ("Return with the Elixir", 0.95, 1.0)
        ]
        acts = []
        for name, start_p, end_p in steps:
            acts.append({'name': name, 'range': [int(total*start_p), int(total*end_p)]})
        return {'acts': acts, 'beats': []}

    def _map_eight_sequences(self, total):
        """The 8-Sequence Method (commonly used in TV/Feature writing)."""
        seqs = [
            ("Sequence 1: Setup", 0, 0.125),
            ("Sequence 2: Inciting Incident", 0.125, 0.25),
            ("Sequence 3: Rising Action", 0.25, 0.375),
            ("Sequence 4: First Culmination", 0.375, 0.5),
            ("Sequence 5: Midpoint", 0.5, 0.625),
            ("Sequence 6: Rising Tension", 0.625, 0.75),
            ("Sequence 7: Climax", 0.75, 0.875),
            ("Sequence 8: Resolution", 0.875, 1.0)
        ]
        acts = []
        for name, start_p, end_p in seqs:
            acts.append({'name': name, 'range': [int(total*start_p), int(total*end_p)]})
        return {'acts': acts, 'beats': []}

    def audit_narrative_intelligence(self, scenes, temporal_trace):
        """Detects high-level narrative issues like Dropped Threads or Thematic Drift."""
        if not scenes or not temporal_trace: return []
        
        audits = []
        
        # 1. Setup & Payoff (Item Tracking)
        loaded_items = ["gun", "weapon", "knife", "letter", "bag", "key", "secret", "poison", "bomb", "evidence"]
        item_usage = {} # item -> [scene_indices]
        
        for s in scenes:
            lines = s.get('lines', [])
            text_blocks = [l.get('text', '').lower() for l in lines]
            text_blocks.append(s.get('heading', '').lower())
            text_blocks.append(s.get('preview', '').lower())
            
            combined_text = " ".join(text_blocks)
            
            for item in loaded_items:
                if item in combined_text:
                    if item not in item_usage: item_usage[item] = []
                    item_usage[item].append(s['scene_index'])
        
        # 2. Logic: Identify Dropped Threads (Setup without Payoff)
        for item, indices in item_usage.items():
            if len(indices) == 1:
                # If item appears only once and it's in early part of script
                scene_idx = indices[0]
                if scene_idx < max(1, len(scenes) * 0.4): # More lenient 40% threshold
                    audits.append({
                        'type': 'Setup/Payoff',
                        'severity': 'Warning',
                        'issue': f"Dropped Thread: '{item.title()}'",
                        'advice': f"You introduced a {item} in Scene {scene_idx+1} but it never reappears."
                    })
        
        # 2. Thematic Consistency (Keyword Drift)
        # Check first 20% vs last 20% for major keyword overlap
        if len(scenes) > 10:
            start_text = " ".join([" ".join([l.get('text', '').lower() for l in s['lines']]) for s in scenes[:len(scenes)//5]])
            end_text = " ".join([" ".join([l.get('text', '').lower() for l in s['lines']]) for s in scenes[-len(scenes)//5:]])
            
            # Simple word sets (ignoring common stopwords)
            stopwords = {'the', 'and', 'was', 'were', 'that', 'with', 'from', 'this'}
            start_words = set(w for w in start_text.split() if len(w) > 4 and w not in stopwords)
            end_words = set(w for w in end_text.split() if len(w) > 4 and w not in stopwords)
            
            overlap = start_words.intersection(end_words)
            if len(overlap) < 3:
                audits.append({
                    'type': 'Thematic Consistency',
                    'severity': 'Info',
                    'issue': "Potential Thematic Drift",
                    'advice': "The vocabulary in your opening and closing acts is very different. Ensure your core themes (e.g. motifs) are woven throughout."
                })
                
        return audits

    def calculate_conflict_typology(self, scene_features, valence_trace=None):
        """Categorizes research-grade conflict types (External, Social, Internal)."""
        if not scene_features: return []
        
        typologies = []
        for i, feat in enumerate(scene_features):
            vis = feat.get('visual_abstraction', {})
            dial = feat.get('dialogue_dynamics', {})
            ling = feat.get('linguistic_load', {})
            
            # 1. External Conflict (Kinetic/Physical)
            # High action lines, low complexity (directness)
            action_score = (vis.get('action_lines', 0) / 10.0) + (vis.get('continuous_action_runs', 0) / 3.0)
            ext_score = min(1.0, action_score * 0.7 + (1.0 - ling.get('clarity_score', 0.5)) * 0.3)
            
            # 2. Social Conflict (Interpersonal/Dialogue)
            # High switches, high dialogue turns
            social_tension = (dial.get('speaker_switches', 0) / 5.0) + (dial.get('dialogue_turns', 0) / 10.0)
            v_val = valence_trace[i] if (valence_trace and i < len(valence_trace)) else 0.0
            v_stress = abs(v_val) * 0.4 
            soc_score = min(1.0, social_tension * 0.6 + v_stress)
            
            # 3. Internal Conflict (Psychological/Subtextual)
            # High linguistic complexity, low explicit action, high idea density
            int_score = min(1.0, ling.get('readability_grade', 0.0) / 15.0 * 0.5 + ling.get('idea_density', 0.5) * 0.5)
            
            typologies.append({
                'scene_index': i,
                'external': round(ext_score, 2),
                'social': round(soc_score, 2),
                'internal': round(int_score, 2),
                'dominant': max([('External', ext_score), ('Social', soc_score), ('Internal', int_score)], key=lambda x: x[1])[0]
            })
            
        return typologies

    def track_thematic_recurrence(self, scene_features):
        """Identifies semantic echoes and thematic mirrors using scene vocabulary clusters."""
        if not scene_features or len(scene_features) < 2: return []
        
        # Use scene_vocabulary clusters if available, else extract from lines
        scene_vocabs = []
        for feat in scene_features:
            vocab = feat.get('scene_vocabulary', set())
            if not vocab:
                # Fallback: extract keywords if vocabulary missing
                vocab = feat.get('thematic_clusters', set())
            scene_vocabs.append(vocab if isinstance(vocab, set) else set(vocab))
        
        echoes = []
        for i in range(len(scene_vocabs)):
            for j in range(i + 1, len(scene_vocabs)):
                v1, v2 = scene_vocabs[i], scene_vocabs[j]
                if not v1 or not v2: continue
                
                # Jaccard Similarity on vocabulary
                intersection = v1.intersection(v2)
                union = v1.union(v2)
                similarity = len(intersection) / len(union) if union else 0.0
                
                if similarity > 0.12: # Threshold for "Thematic Echo" in research contexts
                    echoes.append({
                        'scenes': [i, j],
                        'similarity': round(similarity, 3),
                        'shared_motifs': list(intersection)[:5],
                        'type': 'Structural Mirror' if (i < len(scene_vocabs)*0.25 and j > len(scene_vocabs)*0.75) else 'Thematic Echo'
                    })
                    
        echoes.sort(key=lambda x: x['similarity'], reverse=True)
        return echoes[:15] # Top 15 echoes for research analysis

    def map_interaction_networks(self, scenes, conflict_typology):
        """Maps inter-character tension networks and identifies conflict triangles."""
        if not scenes or not conflict_typology: return {'network': {}, 'triangles': []}
        
        # 1. Aggregate tension per character pair
        tension_map = {} # pair_tuple -> {tension_sum: float, scene_count: int}
        
        for i, scene in enumerate(scenes):
            chars = sorted(list(self._extract_chars_from_scene(scene)))
            if len(chars) < 2: continue
            
            # Use Social Conflict score from typology if available
            scene_social_tension = conflict_typology[i]['social'] if i < len(conflict_typology) else 0.0
            
            for k in range(len(chars)):
                for j in range(k + 1, len(chars)):
                    pair = (chars[k], chars[j])
                    if pair not in tension_map:
                        tension_map[pair] = {'tension_sum': 0.0, 'scene_count': 0}
                    tension_map[pair]['tension_sum'] += scene_social_tension
                    tension_map[pair]['scene_count'] += 1
                    
        # 2. Normalize and filter
        final_edges = []
        node_adj = {} # adjacency list for triangle detection
        
        for pair, data in tension_map.items():
            avg_tension = data['tension_sum'] / data['scene_count'] if data['scene_count'] > 0 else 0.0
            # Normalize intensity [0-1] based on total scene count or raw sum?
            # Research standard often uses weighted edges.
            final_edges.append({
                'source': pair[0],
                'target': pair[1],
                'weight': round(avg_tension, 3),
                'scenes': data['scene_count']
            })
            
            # Build adjacency for triangles (only high tension edges)
            if avg_tension > 0.3:
                if pair[0] not in node_adj: node_adj[pair[0]] = set()
                if pair[1] not in node_adj: node_adj[pair[1]] = set()
                node_adj[pair[0]].add(pair[1])
                node_adj[pair[1]].add(pair[0])
                
        # 3. Detect Triangles
        triangles = self._detect_conflict_triangles(node_adj)
        
        return {
            'edges': final_edges,
            'triangles': triangles
        }

    def _extract_chars_from_scene(self, scene):
        """Helper to get unique characters from scene lines."""
        chars = set()
        for line in scene.get('lines', []):
            if line.get('tag') == 'C':
                name = line.get('text', '').split('(')[0].strip()
                if name: chars.add(name)
        return chars

    def _detect_conflict_triangles(self, adj):
        """Finds cycles of length 3 in the character interaction graph."""
        triangles = []
        nodes = sorted(list(adj.keys()))
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                for k in range(j + 1, len(nodes)):
                    n1, n2, n3 = nodes[i], nodes[j], nodes[k]
                    if n2 in adj[n1] and n3 in adj[n2] and n1 in adj[n3]:
                        triangles.append([n1, n2, n3])
        return triangles

    def audit_timeline_continuity(self, scenes):
        """Audits time-of-day progression for logical consistency."""
        if not scenes: return []
        
        audits = []
        consecutive_nights = 0
        last_tod = None
        last_loc = None
        
        for idx, scene in enumerate(scenes):
            heading = scene.get('heading', '').upper()
            
            # Look for actual sluglines (INT/EXT) in the first 3 lines if heading is just "SCENE X"
            if "INT." not in heading and "EXT." not in heading:
                for line in scene.get('lines', [])[:3]:
                    text = line.get('text', '').upper()
                    if "INT." in text or "EXT." in text:
                        heading = text
                        break
            tod = None
            if " DAY" in heading: tod = "DAY"
            elif " NIGHT" in heading: tod = "NIGHT"
            elif " CONT" in heading: tod = "CONTINUOUS"
            elif " LATER" in heading: tod = "LATER"
            
            loc = heading.split('-')[0].strip() if '-' in heading else heading
            
            if tod == "NIGHT":
                consecutive_nights += 1
            else:
                if consecutive_nights >= 5:
                    audits.append({
                        'scene_index': idx,
                        'severity': 'Warning',
                        'issue': 'Timeline Bloat (Night)',
                        'advice': f"You have {consecutive_nights} consecutive NIGHT scenes. Ensure this much time actually passes or consider condensing."
                    })
                consecutive_nights = 0
            
            # Instantaneous Location Jump Checking
            if tod == "DAY" and last_tod == "DAY" and loc != last_loc and "CONTINUOUS" not in heading:
                # E.g., EXT. HOUSE - DAY immediately followed by INT. OFFICE - DAY
                # This is common in montages, but in a standard scene sequence, it can feel jarring
                if idx > 0: # Check if it's not the first scene
                    audits.append({
                        'scene_index': idx,
                        'severity': 'Info',
                        'issue': 'Abrupt Time/Location Jump',
                        'advice': f"Scene jumps abruptly from {last_loc} to {loc} on the same DAY. Consider an establishing shot or 'LATER/CONT' if it's the same sequence."
                    })
            
            if tod and tod != "CONTINUOUS":
                last_tod = tod
            last_loc = loc
            
        if consecutive_nights >= 5: # check tail
             audits.append({
                'scene_index': len(scenes)-1,
                'severity': 'Warning',
                'issue': 'Timeline Bloat (Night)',
                'advice': f"You have {consecutive_nights} consecutive NIGHT scenes. Ensure this much time actually passes."
            })
             
        return audits

    def audit_narrative_causality(self, encoded_scenes, scenes):
        """Tracks causal flow: setups must lead to complications or decisions."""
        if not encoded_scenes or not scenes: return []
        
        audits = []
        purposes = [enc.get('scene_purpose', {}).get('purpose', 'Transition') for enc in encoded_scenes]
        
        # Look for sequences of "Establishment" without "Complication" or "Decision"
        est_streak = 0
        for i, p in enumerate(purposes):
            if p == 'Establishment':
                est_streak += 1
            elif p in ['Complication', 'Decision', 'Confrontation', 'Revelation']:
                if est_streak >= 3:
                     audits.append({
                         'scene_index': i - 1,
                         'severity': 'Moderate',
                         'issue': 'Causal Flatline',
                         'advice': f"You spent {est_streak} scenes merely 'Establishing'. The plot stalled. This scene finally advances it, but consider cutting the preceding setup."
                     })
                est_streak = 0
            
            # A Revelation should usually be followed by a Decision or Complication, not just a Transition
            if i > 0 and purposes[i-1] == 'Revelation' and p == 'Transition':
                audits.append({
                     'scene_index': i,
                     'severity': 'Info',
                     'issue': 'Muted Revelation',
                     'advice': "The previous scene contained a Revelation, but this scene immediately transitions. Give the characters a moment to process or make a Decision."
                 })
                 
        if est_streak >= 3:
            audits.append({
                 'scene_index': len(purposes) - 1,
                 'severity': 'Moderate',
                 'issue': 'Causal Flatline',
                 'advice': f"The sequence ends with {est_streak} 'Establishing' scenes. The plot is drifting without consequence."
             })
             
        return audits

    def calculate_dialogue_authenticity(self, encoded_scenes):
        """Aggregates On-The-Nose, Generic, and Shoe-Leather for dialogue quality scoring."""
        if not encoded_scenes: return []
        
        scores = []
        for i, enc in enumerate(encoded_scenes):
            otn_dict = enc.get('on_the_nose', {})
            otn = otn_dict.get('on_the_nose_ratio', 0.0) if isinstance(otn_dict, dict) else 0.0
            
            gen_dict = enc.get('generic_dialogue', {})
            gen = gen_dict.get('generic_ratio', 0.0) if isinstance(gen_dict, dict) else 0.0
            
            sl_dict = enc.get('shoe_leather', {})
            if isinstance(sl_dict, dict):
                sl = (sl_dict.get('scene_start_filler', 0) + sl_dict.get('scene_end_filler', 0)) / 6.0
            else:
                sl = 0.0
            
            # Penalize high combination of cardinal sins
            penalty = (otn * 0.5) + (gen * 0.3) + (sl * 0.2)
            authenticity = max(0.0, 1.0 - penalty)
            
            complexity = enc.get('linguistic_load', {}).get('idea_density', 0.5)
            
            label = "Functional"
            if authenticity > 0.8 and complexity > 0.6:
                label = "Brilliant (Sorkin-esque)"
            elif authenticity < 0.4 and complexity > 0.6:
                label = "Wordy / Over-Written"
            elif authenticity < 0.4 and complexity < 0.4:
                label = "Generic / Soap-Opera"
            elif authenticity > 0.8 and complexity < 0.4:
                label = "Punchy / Hemingway"
                
            scores.append({
                'scene_index': i,
                'authenticity_score': round(authenticity, 2),
                'quality_label': label,
                'red_flags': {
                    'on_the_nose': round(otn, 2),
                    'generic': round(gen, 2),
                    'shoe_leather': round(sl, 2)
                }
            })
            
        return scores

    def apply_writer_intent(self, input_data):
        """Writer Intent Immunity (formerly intent.run)"""
        patterns = input_data.get('patterns', [])
        writer_intents = input_data.get('writer_intent', [])
        
        validated_intents = [i for i in writer_intents if i.get('intent') in self.ALLOWED_INTENTS]
        
        surfaced, suppressed, notes = [], [], []
        
        # Consistency Check
        if len(validated_intents) >= 2:
            for i in range(len(validated_intents)):
                for j in range(i+1, len(validated_intents)):
                    ia, ib = validated_intents[i], validated_intents[j]
                    start_over = max(ia['scene_range'][0], ib['scene_range'][0])
                    end_over = min(ia['scene_range'][1], ib['scene_range'][1])
                    if start_over <= end_over and ia['intent'] != ib['intent']:
                        notes.append({'warning_type': 'intent_conflict', 'message': 'Conflicting intents', 'scene_range': [start_over, end_over]})

        if not validated_intents:
            return {'surfaced_patterns': patterns, 'suppressed_patterns': [], 'intent_alignment_notes': notes}
            
        for pattern in patterns:
            p_start, p_end = pattern['scene_range']
            overlap = self._check_overlap(p_start, p_end, validated_intents)
            
            if overlap['full']:
                suppressed.append(pattern)
                notes.append({'pattern_type': pattern['pattern_type'], 'intent': overlap['intent'], 'action': 'suppressed', 'scene_range': pattern['scene_range']})
            elif overlap['partial']:
                # Suppress overlapping part
                suppr_p = pattern.copy()
                suppr_p['scene_range'] = overlap['overlap_range']
                suppressed.append(suppr_p)
                
                # Surface remaining
                if overlap['remain_range']:
                    rem_p = pattern.copy()
                    rem_p['scene_range'] = overlap['remain_range']
                    rem_p['confidence'] = 'low' # Downgrade
                    surfaced.append(rem_p)
                
                notes.append({'pattern_type': pattern['pattern_type'], 'intent': overlap['intent'], 'action': 'partial_suppression'})
            else:
                surfaced.append(pattern)
                
        return {'surfaced_patterns': surfaced, 'suppressed_patterns': suppressed, 'intent_alignment_notes': notes}

    def _check_overlap(self, p_start, p_end, intents):
        for intent in intents:
            i_start, i_end = intent['scene_range']
            o_start = max(p_start, i_start)
            o_end = min(p_end, i_end)
            
            if o_start <= o_end:
                if i_start <= p_start and i_end >= p_end:
                    return {'full': True, 'partial': False, 'intent': intent['intent'], 'overlap_range': None, 'remain_range': None}
                else:
                    rem = [p_start, i_start-1] if p_start < i_start else [i_end+1, p_end]
                    return {'full': False, 'partial': True, 'intent': intent['intent'], 'overlap_range': [o_start, o_end], 'remain_range': rem}
        return {'full': False, 'partial': False, 'intent': None}

    # =========================================================================
    # SSF LOGIC (formerly ssf.py)
    # =========================================================================

    def analyze_silence(self, input_data):
        """Silence-as-Signal Formalization (formerly ssf.run)"""
        ablation = input_data.get('ablation_config', {})
        if ablation.get('disable_ssf', False):
            return {'is_silent': False, 'silence_confidence': 0.0, 'explanation_key': 'ablation_disabled'}

        signals = input_data.get('temporal_signals', [])
        acd_states = input_data.get('acd_states', [])
        surfaced = input_data.get('surfaced_patterns', [])
        
        if surfaced:
            return {'is_silent': False, 'silence_confidence': None, 'explanation_key': None}
            
        if not signals:
            return {'is_silent': True, 'silence_confidence': 'low', 'explanation_key': 'no_data'}
            
        s_vals = [s['attentional_signal'] for s in signals]
        r_vals = [s['recovery_credit'] for s in signals]
        
        max_s, avg_s = max(s_vals), statistics.mean(s_vals)
        avg_r = statistics.mean(r_vals)
        max_c = max(a['collapse_likelihood'] for a in acd_states) if acd_states else 0.0
        max_d = max(a['drift_likelihood'] for a in acd_states) if acd_states else 0.0
        
        metrics = {'max_strain': round(max_s,3), 'avg_recovery': round(avg_r,3)}
        
        high_conf = (max_s < 0.6 and avg_r > 0.15 and max_c < 0.5)
        med_conf = (max_s < 0.8 and (avg_r > 0.1 or avg_s < 0.3))
        
        conf = 'low'
        key = 'marginal_strain'
        
        if high_conf: 
            conf, key = 'high', 'stable_continuity'
            if max_d > 0.7: key = 'stable_but_drifting'
        elif med_conf: 
            conf, key = 'medium', 'self_correcting'
            
        return {'is_silent': True, 'silence_confidence': conf, 'stability_metrics': metrics, 'explanation_key': key}

    # =========================================================================
    # UNCERTAINTY LOGIC (formerly uncertainty.py & ensemble_uncertainty.py)
    # =========================================================================

    def calculate_uncertainty(self, input_data):
        """Analytical Uncertainty (formerly uncertainty.run)"""
        signals = input_data.get('temporal_signals', [])
        features = input_data.get('features', [])
        if not signals: return []
        
        outputs = []
        for i, sig in enumerate(signals):
            s_val = sig['attentional_signal']
            feat = features[i]
            
            ent = feat.get('entropy_score', 0)
            u_ent = max(0.0, (ent - 3.0) * 0.05)
            
            micro = feat.get('micro_structure', [])
            u_micro = statistics.stdev([m['word_count'] for m in micro])/50.0 if len(micro) > 1 else 0.1
            
            u_vol = 0.0
            if i >= 3:
                vals = [x['attentional_signal'] for x in signals[i-3:i]]
                u_vol = statistics.stdev(vals) if len(vals) > 1 else 0.0
                
            sigma = min(0.25, 0.05 + 0.3*u_ent + 0.2*u_micro + 0.5*u_vol)
            
            outputs.append({
                'scene_index': sig['scene_index'],
                'sigma': round(sigma, 3),
                'ci_upper': round(s_val + 1.96*sigma, 3),
                'ci_lower': round(max(0, s_val - 1.96*sigma), 3)
            })
        return outputs

    def calculate_ensemble_uncertainty(self, input_data):
        """Ensemble uncertainty using bagging (formerly ensemble_uncertainty.run)"""
        iterations = input_data.get('iterations', 20)
        base_trace = input_data.get('base_trace', [])
        
        if not base_trace: return []
        
        ensemble_results = []
        # [GOVERNANCE] Enforce deterministic mathematical boundary for Monte Carlo
        import random
        # random.seed(42) # Removed hardcoded seed to respect global config
        
        for _ in range(iterations):
            trace = []
            for pt in base_trace:
                noise = random.gauss(0, 0.07)
                trace.append(max(0, min(1, pt['attentional_signal'] + noise)))
            ensemble_results.append(trace)
            
        output = []
        for i in range(len(base_trace)):
            vals = [run[i] for run in ensemble_results]
            mean = statistics.mean(vals)
            std = statistics.stdev(vals) if len(vals) > 1 else 0.0
            
            output.append({
                'scene_index': i,
                'mean': round(mean, 3),
                'lower_bound_95': round(max(0, mean - 2*std), 3),
                'upper_bound_95': round(min(1, mean + 2*std), 3)
            })
        return output

    # =========================================================================
    # PROFILER LOGIC (formerly profiler.py)
    # =========================================================================

    def get_cognitive_profile(self, profile_name="general"):
        """Returns cognitive physics parameters"""
        profiles = {
            'general': {'lambda_base': 0.85, 'beta_recovery': 0.3, 'fatigue_threshold': 1.0, 'coherence_weight': 0.15},
            'cinephile': {'lambda_base': 0.90, 'beta_recovery': 0.4, 'fatigue_threshold': 1.3, 'coherence_weight': 0.10},
            'distracted': {'lambda_base': 0.75, 'beta_recovery': 0.2, 'fatigue_threshold': 0.8, 'coherence_weight': 0.30},
            'child': {'lambda_base': 0.70, 'beta_recovery': 0.5, 'fatigue_threshold': 0.6, 'coherence_weight': 0.40}
        }
        return profiles.get(profile_name.lower(), profiles['general'])

    # =========================================================================
    # XAI LOGIC (formerly xai.py)
    # =========================================================================

    def generate_explanations(self, data):
        """Decompose effort signal into drivers (formerly xai.run)"""
        features = data.get('features', [])
        sem_scores = data.get('semantic_scores', [])
        syn_scores = data.get('syntax_scores', [])
        
        output = []
        # Weights (reflecting temporal defaults)
        w_cog, w_emo = 0.55, 0.45
        
        for i, scene in enumerate(features):
            sem = sem_scores[i] if i < len(sem_scores) else 0.0
            syn = syn_scores[i] if i < len(syn_scores) else 0.0
            
            # Raw Inputs
            ref = scene['referential_load']
            struct = scene['structural_change']
            dial = scene['dialogue_dynamics']
            vis = scene['visual_abstraction']
            ling = scene['linguistic_load']
            
            # Calculation
            raw_struct = ((ref['active_character_count']/10.0 + ref['character_reintroductions']/5.0)*0.3 + 
                          (ling['sentence_length_variance']/20.0)*0.3 + (struct['event_boundary_score']/100.0)*0.25 + 
                          (dial['speaker_switches']/20.0)*0.15)
            
            raw_motion = (vis['action_lines']/50.0 + vis['continuous_action_runs']/10.0)
            raw_dial = (dial['dialogue_turns']/50.0)*0.6 + (ling['sentence_count']/50.0)*0.4
            
            # Weighted Contributions
            c_struct = w_cog * 0.6 * raw_struct
            c_syn = w_cog * 0.2 * syn
            c_sem = w_cog * 0.2 * sem
            c_motion = w_emo * 0.3 * raw_motion
            c_dial = w_emo * 0.7 * raw_dial
            
            total = c_struct + c_syn + c_sem + c_motion + c_dial
            if total < 0.001: total = 1.0
            
            drivers = {
                'Structure': round(c_struct/total, 2),
                'Syntax': round(c_syn/total, 2),
                'Semantics': round(c_sem/total, 2),
                'Motion': round(c_motion/total, 2),
                'Dialogue': round(c_dial/total, 2)
            }
            
            output.append({
                'scene_index': scene['scene_index'],
                'drivers': drivers,
                'dominant_driver': max(drivers, key=drivers.get)
            })
        return output

    # =========================================================================
    # SCENE NOTES LOGIC (formerly scene_notes.py)
    # =========================================================================

    def generate_scene_notes(self, data):
        """Generate actionable feedback (formerly scene_notes.run)"""
        scenes = data.get('scenes', [])
        trace = data.get('temporal_trace', [])
        valence = data.get('valence_scores', [])
        syntax = data.get('syntax_scores', [])
        
        feedback = {}
        
        for i, scene in enumerate(scenes):
            notes = []
            tp = trace[i] if i < len(trace) else {}
            v = valence[i] if i < len(valence) else 0
            s = syntax[i] if i < len(syntax) else 0
            tsn = tp.get('attentional_signal', 0)
            
            if tsn < 0.3: 
                notes.append({'severity': 'info', 'insight': 'Frictionless Flow', 'reflection': 'The modeled attentional demand is low here. Is this intended as a moment of rest for the audience?'})
            if v < -0.2: 
                notes.append({'severity': 'info', 'insight': 'Sustained Gravity', 'reflection': 'The tonal signal is consistently heavy. How might a moment of levity impact this section?'})
            if s > 0.7: 
                notes.append({'severity': 'info', 'insight': 'Linguistic Density', 'reflection': 'The complexity of language is high. How does this affect the intended reading rhythm?'})
            
            d_lines = [l for l in scene['lines'] if l.get('tag') == 'D']
            if any(len(l['text'].split()) > 40 for l in d_lines):
                notes.append({'severity': 'info', 'insight': 'Extended Speech', 'reflection': 'A character has a particularly long monologue. How does this volume of information serve the scene?'})
            
            if not d_lines and len(scene['lines']) > 3:
                notes.append({'severity': 'info', 'insight': 'Silent Section', 'reflection': 'This scene relies entirely on action and visuals. Does this silence amplify or obscure the intent?'})
            
            if tsn > 0.7 and v > 0.2:
                notes.append({'severity': 'info', 'insight': 'Tonal Contrast', 'reflection': 'High attentional demand coincides with a positive tonal signal. Does this contrast align with the emotional goal?'})
            
            if notes: feedback[i] = notes
            
        return feedback

    # =========================================================================
    # SUGGESTION LOGIC (formerly suggestion.py)
    # =========================================================================

    def generate_suggestions(self, temporal_trace):
        """Generate structural strategies (formerly suggestion.run)"""
        suggestions = []
        if not temporal_trace: return {}
        
        for pt in temporal_trace:
            eff = pt.get('instantaneous_effort', 0.5)
            # state = pt.get('affective_state', 'Normal') # Assume state is calculated elsewhere or implied
            
            sugg = None
            if eff < 0.2:
                sugg = {
                    'scene': pt['scene_index'],
                    'diagnosis': "Risk of Boredom",
                    'strategy': "Inject Kinetic Energy",
                    'tactics': ["Cut sentence length", "Add visual words", "Interrupt dialogue"],
                    'priority': 0.2 - eff
                }
            elif eff > 0.85:
                sugg = {
                    'scene': pt['scene_index'],
                    'diagnosis': "Risk of Burnout",
                    'strategy': "Induce Recovery",
                    'tactics': ["Insert visual rest", "Simplify syntax", "Lower social tension"],
                    'priority': eff - 0.85
                }
            
            if sugg:
                suggestions.append(sugg)
                
        # [GOVERNANCE] Enforce deterministic selection based on mathematical priority
        suggestions.sort(key=lambda x: x.get('priority', 0), reverse=True)
        for s in suggestions:
            s.pop('priority', None)
            
        return {'structural_repair_strategies': suggestions[:3]}

    # =========================================================================
    # MEDIATION LOGIC (formerly mediation.py)
    # =========================================================================

    def mediate_experience(self, input_data):
        """
        Translate patterns into writer-safe, question-first reflections.
        (formerly mediation.run)
        """
        surfaced = input_data.get('surfaced_patterns', [])
        suppressed = input_data.get('suppressed_patterns', [])
        alignment_notes = input_data.get('intent_alignment_notes', [])
        acd_states = input_data.get('acd_states', []) 
        ssf_analysis = input_data.get('ssf_analysis', {}) 
        
        reflections = []
        
        # === AEKS: Alert Escalation Kill-Switch (Constraint) ===
        total_scenes = 100 
        if acd_states:
            total_scenes = len(acd_states)
            
        max_alerts = max(3, int(total_scenes / 12))
        
        # Deduplicate overlapping patterns
        surfaced = self._deduplicate_patterns(surfaced)
        
        if len(surfaced) > max_alerts:
            conf_map = {'high': 3, 'medium': 2, 'low': 1}
            surfaced.sort(key=lambda x: conf_map.get(x.get('confidence'), 0), reverse=True)
            surfaced = surfaced[:max_alerts]
        
        # Generate reflections
        for pattern in surfaced:
            reflection = self._generate_reflection(pattern, acd_states, total_scenes, input_data=input_data)
            reflections.append(reflection)
        
        # Handle silence
        silence_explanation = None
        if not surfaced:
            silence_explanation = self._generate_silence_explanation(suppressed, alignment_notes, ssf_analysis)
        
        # Generate intent acknowledgments
        intent_acknowledgments = []
        for note in alignment_notes:
            ack = self._generate_intent_acknowledgment(note)
            intent_acknowledgments.append(ack)
            
        return {
            'reflections': reflections,
            'silence_explanation': silence_explanation,
            'intent_acknowledgments': intent_acknowledgments,
            'total_surfaced': len(surfaced), 
            'total_suppressed': len(suppressed),
            'aeks_active': len(input_data.get('surfaced_patterns', [])) > max_alerts 
        }

    def _deduplicate_patterns(self, patterns):
        """Prioritize: Degenerative > Demand > Recovery > Repetition"""
        if not patterns: return []
        priority = {'degenerative_fatigue': 1, 'sustained_attentional_demand': 2, 
                   'limited_recovery': 3, 'surprise_cluster': 4, 'repetition': 5}
        patterns.sort(key=lambda p: priority.get(p.get('pattern_type'), 10))
        unique_patterns = []
        for p in patterns:
            is_redundant = False
            p_start, p_end = p.get('scene_range', [0, 0])
            p_len = p_end - p_start + 1
            for existing in unique_patterns:
                e_start, e_end = existing.get('scene_range', [0, 0])
                overlap_start = max(p_start, e_start)
                overlap_end = min(p_end, e_end)
                if overlap_start <= overlap_end:
                    overlap_len = overlap_end - overlap_start + 1
                    if overlap_len / p_len > 0.8:
                        is_redundant = True
                        break
            if not is_redundant: unique_patterns.append(p)
        return unique_patterns

    def _calculate_confidence(self, pattern, input_data):
        """
        Calculate a confidence score (0.0-1.0) for a specific pattern/insight.
        Based on:
        1. Signal Clarity (Signal-to-Noise Ratio in local window)
        2. Data Density (Number of data points in scene)
        3. Feature Congruence (Do multiple features agree?)
        """
        scene_range = pattern.get('scene_range', [0, 0])
        start, end = scene_range
        
        # 1. Data Density
        scenes = input_data.get('scenes', [])
        relevant_scenes = [s for s in scenes if start <= s['scene_index'] <= end]
        total_lines = sum(len(s.get('lines', [])) for s in relevant_scenes)
        
        density_score = min(1.0, total_lines / 10.0) # <10 lines = lower confidence
        
        # 2. Heuristic Congruence (Simplified)
        congruence_score = 0.8 # Default base
        if pattern.get('pattern_type') == 'high_tension':
            # Check if stakes detector also fired
            stakes = self._check_stakes(relevant_scenes)
            if stakes == 'High': congruence_score = 1.0
            
        return round(density_score * congruence_score, 2)

    def _check_stakes(self, scenes):
        # Placeholder for accessing pre-computed stakes if available
        return 'Low'

    def _generate_reflection(self, pattern, acd_states=None, total_scenes=100, input_data=None):
        pattern_type = pattern.get('pattern_type', 'unknown')
        scene_range = pattern.get('scene_range', [0, 0])
        
        # Calculate specialized confidence
        confidence_val = self._calculate_confidence(pattern, input_data) if input_data else 0.7
        
        # Map float to Label
        confidence_label = 'High'
        if confidence_val < 0.4: confidence_label = 'Low'
        elif confidence_val < 0.7: confidence_label = 'Medium'
        
        reflection_text = "This section creates a unique texture that may require specific audience tuning."
        
        if pattern_type == 'degenerative_fatigue' and acd_states:
            start, end = scene_range
            window_acd = [state for state in acd_states if start <= state['scene_index'] <= end]
            avg_drift = sum(s['drift_likelihood'] for s in window_acd) / len(window_acd) if window_acd else 0.5
            avg_collapse = sum(s['collapse_likelihood'] for s in window_acd) / len(window_acd) if window_acd else 0.5
            
            if avg_drift > avg_collapse:
                 reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['drift']
            else:
                 reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['collapse']
        elif pattern_type in WRITER_NATIVE_TRANSLATIONS:
            reflection_text = WRITER_NATIVE_TRANSLATIONS[pattern_type]
            
        # Fix 7: Add climax-zone context note to sustained demand reflections
        if pattern_type == 'sustained_attentional_demand' and pattern.get('in_climax_zone'):
            reflection_text += " Note: This section falls near the expected dramatic peak — high demand here may be structurally appropriate."
        elif total_scenes > 30:
            start, end = scene_range
            if end / max(1, total_scenes) > 0.8:
                reflection_text += " (Deep in the script, this requires even more energy to sustain.)"

        # Fix 6: Attach dominant XAI driver to reflection
        dominant_driver = None
        if input_data:
            xai_data = input_data.get('xai_explanations', [])
            start, end = scene_range
            window_xai = [x for x in xai_data if start <= x.get('scene_index', -1) <= end]
            if window_xai:
                driver_counts = {}
                for x in window_xai:
                    d = x.get('dominant_driver')
                    if d:
                        driver_counts[d] = driver_counts.get(d, 0) + 1
                if driver_counts:
                    dominant_driver = max(driver_counts, key=driver_counts.get)

        return {
            'scene_range': scene_range,
            'reflection': reflection_text,
            'confidence': confidence_label,
            'confidence_score': confidence_val,  # Numeric score for research purposes
            'dominant_driver': dominant_driver    # Fix 6: Why was this scene flagged?
        }

    def _generate_silence_explanation(self, suppressed, alignment_notes, ssf_analysis=None):
        if alignment_notes:
            return "Silence here means the system sees exactly what you intended. Your declared intent matches the audience load."
        
        if ssf_analysis and ssf_analysis.get('is_silent'):
            key = ssf_analysis.get('explanation_key')
            avg_effort = ssf_analysis.get('stability_metrics', {}).get('avg_effort', 0.5)
            
            # Fix 9: Distinguish balanced from low-engagement continuity
            if key == 'stable_continuity':
                if avg_effort < 0.3:
                    return (
                        "The modeled attentional demand remains very low throughout — no strain detected. "
                        "Is the audience investment intentionally restrained here, or has the script's forward pull softened?"
                    )
                return "The experience here is rock stable. Effort and recovery are balanced — the audience is breathing naturally."
            elif key == 'self_correcting':
                return "The flow feels self-correcting. Whenever tension rises, a release valve opens naturally."
            elif key == 'stable_but_drifting':
                return "The experience is stable, though the water is very still. No strain, but also low demand."
        
        if suppressed: return "Patterns were suppressed based on provided constraints."
        return "The attentional flow is stable. No red flags, no drag, no exhaustion. A clean reading."
        
    def _generate_intent_acknowledgment(self, note):
        intent = note.get('intent', 'your declared intent')
        start, end = note.get('scene_range', [0, 0])
        return f"You marked scenes {start}–{end} as '{intent}'. This matches the signal perfectly."

    def generate_silence_explanation(self, suppressed, alignment_notes, ssf_analysis=None):
        return self._generate_silence_explanation(suppressed, alignment_notes, ssf_analysis)

    def generate_intent_acknowledgments(self, alignment_notes):
        acks = []
        for note in alignment_notes:
            acks.append(self._generate_intent_acknowledgment(note))
        return acks

class CounterfactualExplainer:
    """Run 'What-If' Simulations to explain why a score is high/low"""
    
    def __init__(self):
        # Local import to avoid circular dependency
        from scriptpulse.agents.dynamics_agent import DynamicsAgent
        self.dynamics = DynamicsAgent()
        
    def run(self, input_data):
        """
        Compare actual signals against hypothetical variations.
        Returns: {
            'action_heavy_delta': float,
            'dialogue_heavy_delta': float,
            'suggestion': str
        }
        """
        import copy
        original_signals = input_data.get('temporal_signals', [])
        features = input_data.get('features', [])
        
        if not original_signals or not features: return {}
        
        avg_original = statistics.mean([s['instantaneous_effort'] for s in original_signals])
        
        # 1. Simulate "What if lighter structure?" (Simulating an edit)
        # We modify features in-place (deep copied)
        light_features = copy.deepcopy(features)
        for f in light_features:
            f['linguistic_load']['sentence_length_variance'] *= 0.8
            f['structural_change']['event_boundary_score'] *= 0.8
            
        light_input = copy.deepcopy(input_data)
        light_input['features'] = light_features
        
        light_signals = self.dynamics.run_simulation(light_input, iterations=1)
        if not light_signals: return {}
        
        avg_light = statistics.mean([s['instantaneous_effort'] for s in light_signals])
        delta_light = avg_original - avg_light
        
        # 2. Simulate "What if more visual?"
        vis_features = copy.deepcopy(features)
        for f in vis_features:
            f['visual_abstraction']['action_lines'] *= 1.5
            
        vis_input = copy.deepcopy(input_data)
        vis_input['features'] = vis_features
        
        vis_signals = self.dynamics.run_simulation(vis_input, iterations=1)
        avg_vis = statistics.mean([s['instantaneous_effort'] for s in vis_signals])
        delta_vis = avg_vis - avg_original
        
        insight = "Balanced."
        if delta_light > 0.1:
            insight = "Structural complexity is a major driver. Simplifying sentences would significantly reduce load."
        elif delta_vis < 0:
            insight = "Adding visual action would actually LOWER the cognitive load (by breaking up density)."
            
        return {
            'effort_reduction_if_simplified': round(delta_light, 3),
            'effort_change_if_visuals_doubled': round(delta_vis, 3),
            'counterfactual_insight': insight
        }
