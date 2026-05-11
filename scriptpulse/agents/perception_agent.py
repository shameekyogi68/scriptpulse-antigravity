# MODULE: perception_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Perception Agent - Simplified & MCA-Defensible Version
Focuses on 5 Core Cognitive Pillars:
1. Linguistic Load (Complexity)
2. Dialogue Dynamics (Rhythm)
3. Visual Abstraction (Action)
4. Referential Load (Characters)
5. Information Entropy (Novelty)
"""

import re
import math
import statistics
from collections import Counter
from ..utils.model_manager import manager

def normalize_character_name(name):
    """Utility for consistent character matching with body-part blacklist."""
    if not name: return "UNKNOWN"
    # Stem names: Remove (O.S.), (V.O.), (CONT'D) etc. 
    stemmed = re.sub(r'\(.*?\)', '', name).upper()
    # Handle suffixes without parentheses (e.g. CHARACTER-O.S.)
    stemmed = re.sub(r'[-\s](O\.?S\.?|V\.?O\.?|ALT|OFF-SCREEN|DASHES|FILTERED)$', '', stemmed)
    
    # Strip prefixes like MR., MS., DR., MRS., PROF.
    prefix_pattern = r'^(MR\.?|MS\.?|DR\.?|MRS\.?|PROF\.?)\s+'
    stemmed = re.sub(prefix_pattern, '', stemmed).strip()
    
    # Preserve hyphens as word separators, then collapse
    clean = re.sub(r'[^A-Z0-9\s\-]', '', stemmed).strip()
    clean = re.sub(r'-+', ' ', clean).strip()  # normalize hyphens to spaces
    
    # Body Part & Structural Blacklist
    # We only filter the 'garbage' items that are definitely action fragments misparsed.
    blacklist = {
        'EXT', 'INT', 'OFF-SCREEN', 'O.S.', 'V.O.', 'VOICE',
        'HIS HAND', 'HER FACE', 'HIS FACE', 'HER HAND', 'THE GUN', 'THE DOOR', 'THE CAR',
        'HIS HANDS', 'HER EYES', 'HIS EYES', 'CLOSE ON', 'CLOSE-UP'
    }
    if clean in blacklist:
        return None
    return clean

class EncodingAgent:
    """AI-Enhanced Encoding Agent - Flexible, Context-Aware Analysis"""
    
    def __init__(self):
        self.classifier = manager.get_zero_shot()
        self.sentence_transformer = manager.get_sentence_transformer()
        self.spacy_model = manager.get_spacy()
        self.stakes_labels = ['Physical Survival', 'Emotional Connection', 'Social Status', 'Moral Dilemma', 'Existential Dread']
        self.sentiment_labels = ['High Tension / Conflict', 'Positive Connection', 'Despair / Loss', 'Neutral / Calm']
        self.scene_type_labels = ['Action Sequence', 'Dialogue Scene', 'Transition', 'Revelation', 'Escalation', 'Resolution']

    def run(self, input_data):
        scenes = input_data.get('scenes', [])
        lines = input_data.get('lines', [])
        
        if not scenes: return []
        
        feature_vectors = []
        prev_characters = set()
        
        for i, scene in enumerate(scenes):
            scene_lines = [l for l in lines if scene['start_line'] <= l['line_index'] <= scene['end_line']]
            
            # 1. Linguistic Analysis (Syntactic Load)
            linguistic = self._extract_linguistic(scene_lines)
            
            # 2. Dialogue & Rhythm (Tempo)
            dialogue = self._extract_dialogue(scene_lines)
            
            # 3. Action & Visuals (Cinematic Weight)
            visual = self._extract_visual(scene_lines)
            
            # 4. Character Tracking (Cognitive Load)
            referential = self._extract_referential(scene_lines, prev_characters)
            prev_characters = referential['current_character_set']
            
            # 5. Information Theory (Entropy/Surprisal)
            entropy = self._extract_entropy(scene_lines)
            
            # 6. Affective Load (VADER Emotional Valence/Sentiment)
            affective = self._extract_affective_load(scene_lines)
            
            # 7. Narrative Metadata (For Charts/UI)
            metadata = self._extract_narrative_metadata(scene_lines)
            
            features = {
                'scene_index': scene['scene_index'],
                'linguistic_load': linguistic,
                'dialogue_dynamics': dialogue,
                'visual_abstraction': visual,
                'referential_load': {k:v for k,v in referential.items() if k != 'current_character_set'},
                'structural_change': self._extract_structural(scene, scenes, i),
                'entropy_score': entropy,
                'affective_load': affective,
                'ambient_signals': self._extract_ambient(linguistic, dialogue, visual),
                'micro_structure': self._extract_micro(scene_lines),
                'runtime_contribution': self._extract_runtime_contribution(scene_lines),
                # Supporting metrics for UI consistency
                'character_scene_vectors': metadata['character_scene_vectors'],
                'stakes_taxonomy': metadata['stakes'],
                'scene_purpose': metadata['purpose'],
                'payoff_density': metadata['payoff'],
                'on_the_nose': metadata['on_the_nose'],
                'shoe_leather': metadata['shoe_leather'],
                'tell_vs_show': metadata['tell_vs_show'],
                'is_exposition': metadata['purpose']['purpose'] == 'Exposition',
                'scene_vocabulary': metadata['scene_vocabulary'],
                'reader_frustration': self._extract_reader_frustration(scene_lines, referential['active_character_count']),
                'stichomythia': metadata['stichomythia'],
                'monologue_data': metadata['monologue_data'],
                'passive_voice': metadata['passive_voice'],
                'scene_economy': metadata['scene_economy'],
                'opening_hook': metadata['opening_hook'],
                'narrative_closure': metadata['narrative_closure'],
                'research_telemetry': metadata.get('research_telemetry', {})
            }
            feature_vectors.append(features)
            
        return feature_vectors

    def _extract_linguistic(self, lines):
        text = " ".join([l['text'] for l in lines])
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s]
        
        if not words: return {'mean_sentence_length': 0, 'sentence_length_variance': 0, 'sentence_count': 0, 'idea_density': 0, 'word_count': 0, 'clarity_score': 0.8}
        
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths)/len(lengths) if lengths else 0
        var = sum((x-avg)**2 for x in lengths)/len(lengths) if lengths else 0
        
        if getattr(self, 'spacy_model', None):
            try:
                doc = self.spacy_model(text[:10000])  # Cap for performance & stability
                lemmas = [t.lemma_ for t in doc if not t.is_stop and not t.is_punct]
                uniq = len(set(lemmas))
                idea_density = uniq / max(1, len(lemmas))
            except Exception:
                uniq = len(set(words))
                idea_density = uniq/len(words) if words else 0
        else:
            uniq = len(set(words))
            idea_density = uniq/len(words) if words else 0
        
        return {
            'mean_sentence_length': round(avg, 2),
            'sentence_length_variance': round(var, 2),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'idea_density': round(idea_density, 3),
            'clarity_score': 0.8 # Placeholder
        }

    def _extract_runtime_contribution(self, lines):
        """
        Calculates estimated runtime for the scene in seconds.
        Uses industry standard Word-to-Minute heuristics instead of crude block counts.
        """
        action_words = sum([len(l['text'].split()) for l in lines if l['tag'] == 'A'])
        dialogue_words = sum([len(l['text'].split()) for l in lines if l['tag'] == 'D'])
        
        # Calculate seconds (60 seconds per minute)
        # Industry standard: ~200 WPM spoken dialogue, but action descriptions
        # represent screen time at roughly 2-3x the reading rate
        action_seconds = action_words * 0.38   # ~158 words/min of screen time
        
        # Dialogue is spoken quickly
        dialogue_seconds = dialogue_words * 0.33  # ~180 WPM spoken
        
        total_seconds = action_seconds + dialogue_seconds
        
        # Minor buffer for transition instead of 5s
        total_seconds += 1.0 
        
        return {'estimated_seconds': round(total_seconds)}

    def _extract_dialogue(self, lines):
        d_lines = [l for l in lines if l['tag'] == 'D']
        c_lines = [l for l in lines if l['tag'] == 'C']
        
        switches = 0
        for i in range(1, len(c_lines)):
            if c_lines[i]['text'] != c_lines[i-1]['text']: switches += 1
            
        non_blank_d = [l for l in d_lines if l['text'].strip()]
        non_blank_total = [l for l in lines if l['text'].strip()]
        return {
            'dialogue_line_count': len(non_blank_d),
            'turn_velocity': round(len(non_blank_d) / max(1, len(non_blank_total)), 3),
            'speaker_switches': switches
        }

    def _extract_visual(self, lines):
        a_lines = [l for l in lines if l['tag'] == 'A']
        
        runs = 0
        in_run = False
        for l in lines:
            if l['tag'] == 'A':
                if not in_run:
                    runs += 1
                    in_run = True
            else:
                in_run = False
                
        non_blank_a = [l for l in a_lines if l['text'].strip()]
        non_blank_total = [l for l in lines if l['text'].strip()]
        return {
            'action_lines': len(non_blank_a),
            'visual_intensity': round(len(non_blank_a) / max(1, len(non_blank_total)), 3),
            'continuous_action_runs': runs
        }

    def _extract_referential(self, lines, prev_chars):
        chars = set(l['text'].strip() for l in lines if l['tag'] == 'C')
        added = len(chars - prev_chars)
        removed = len(prev_chars - chars)
        total = len(chars.union(prev_chars))
        churn = (added + removed) / max(1, total)
        
        return {
            'active_character_count': len(chars),
            'entity_churn': round(churn, 2),
            'current_character_set': chars
        }

    def _extract_entropy(self, lines):
        text = " ".join([l['text'] for l in lines]).lower()
        if getattr(self, 'sentence_transformer', None):
            try:
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if len(s.split()) > 3]
                if len(sentences) > 1:
                    import numpy as np
                    embeddings = self.sentence_transformer.encode(sentences, convert_to_tensor=False)
                    centroid = np.mean(embeddings, axis=0)
                    centroid_norm = np.linalg.norm(centroid)
                    if centroid_norm > 0:
                        centroid = centroid / centroid_norm
                    distances = []
                    for emb in embeddings:
                        norm = np.linalg.norm(emb)
                        if norm > 0:
                            sim = np.dot(emb / norm, centroid)
                            distances.append(1.0 - sim)
                    semantic_entropy = float(np.mean(distances)) * 2.0
                    return round(min(1.0, max(0.0, semantic_entropy)), 3)
            except Exception:
                pass

        words = re.findall(r'\b\w+\b', text)
        if len(words) < 5:
            return 0.0
        counts = Counter(words)
        total = len(words)
        raw_entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
        # Normalize: divide by log2(unique_words) so max entropy = 1.0
        max_possible = math.log2(len(counts)) if len(counts) > 1 else 1.0
        return round(raw_entropy / max_possible, 3)

    def _extract_affective_load(self, lines):
        # 1. Prepare text for analysis (Action 'A' and Dialogue 'D')
        text = " ".join([l['text'] for l in lines if l['tag'] in ['D', 'A']])
        all_text = " ".join([l['text'] for l in lines]).lower()
        if not text.strip():
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}

        # 2. High-Priority Narrative Override: Violence & Death (Task 1)
        violence_triggers_hard = ['killed', 'murdered', 'shot dead', 'execution', 'massacre', 'slaughter']
        violence_triggers_soft = ['shot', 'blood', 'body', 'weapon', 'knife', 'grenade', 'trigger']
        
        # Check for character presence via tags OR capitalized names in Action lines
        has_character = any(l['tag'] == 'C' for l in lines)
        if not has_character:
            has_character = any(re.search(r'\b[A-Z]{3,}\b', l['text']) for l in lines if l['tag'] == 'A')

        hard_match = any(w in all_text for w in violence_triggers_hard)
        soft_count = sum(1 for w in violence_triggers_soft if w in all_text)
        
        if has_character and (hard_match or soft_count >= 3):
            penalty = -0.99 if hard_match else -0.65
            return {'pos': 0.00, 'neg': abs(penalty), 'neu': 1 - abs(penalty), 'compound': penalty}

        # AI-enhanced sentiment analysis
        ai_result = self._ai_sentiment_analysis(text)
        if ai_result:
            return ai_result
                
        # Enhanced semantic fallback with contextual awareness
        return self._contextual_sentiment_fallback(text, all_text)

    def _extract_structural(self, scene, all_scenes, idx):
        prev_heading = all_scenes[idx-1].get('heading', '') if idx > 0 else ''
        curr_heading = scene.get('heading', '')
        # Extract location (text before ' - DAY/NIGHT') from heading
        def extract_loc(h): return re.sub(r'\s*-\s*(DAY|NIGHT|.*?)$', '', h).strip()
        location_change = extract_loc(prev_heading) != extract_loc(curr_heading) if idx > 0 else False
        return {'location_change': location_change, 'event_boundary_score': 1.0 if location_change else 0.0}

    def _extract_ambient(self, ling, dial, vis):
        score = ( (1 - dial['turn_velocity']) + (1 - min(1.0, vis['action_lines']/10)) ) / 2
        return {
            'ambient_score': round(score, 3),
            'component_scores': {'stillness': round(1-vis['visual_intensity'], 3)}
        }

    def _extract_micro(self, lines):
        """
        Returns a lightweight per-line record including tag, word_count, text snippet,
        and the current speaker (for dialogue lines). Used by CharacterVoiceDistinctionAgent
        in the runner to build per-character dialogue corpora.
        """
        micro = []
        current_speaker = None
        for l in lines:
            tag = l.get('tag', '')
            text = l.get('text', '')
            if tag == 'C':
                name = normalize_character_name(text)
                if name:
                    current_speaker = name
                else:
                    current_speaker = None
            entry = {
                'tag': tag,
                'word_count': len(text.split()),
                'text': text[:200],  # Truncate for memory efficiency
            }
            if tag == 'D' and current_speaker:
                entry['speaker'] = current_speaker
            micro.append(entry)
        return micro

    def _extract_reader_frustration(self, lines, char_count):
        """Detects structural issues that confuse readers."""
        raw_chars = [normalize_character_name(l['text']) for l in lines if l['tag'] == 'C']
        chars = [c for c in raw_chars if c] # Filter None from blacklist
        unique_chars = sorted(list(set(chars))) # Sorted for determinism
        
        # 1. Name Crowding: Too many characters introduced at once
        crowding = char_count > 5
        
        # 2. Similar Names: Character names that look/sound too similar (e.g. John & Jon)
        similar = []
        for i in range(len(unique_chars)):
            for j in range(i + 1, len(unique_chars)):
                n1, n2 = unique_chars[i], unique_chars[j]
                if len(n1) > 3 and len(n2) > 3:
                    # Basic similarity: match first 4 chars and ensure lengths are close
                    if n1[:4] == n2[:4] and abs(len(n1) - len(n2)) <= 2:
                        similar.append(f"{n1}/{n2}")
        
        # 3. Unfilmable 'Internal' Action: (already handled by tell_vs_show, but we can group it here too)
        a_lines = [l['text'].lower() for l in lines if l['tag'] == 'A']
        internal_hits = []
        for a in a_lines:
            if any(w in a for w in ['thinks', 'remembers', 'wonders', 'realizes', 'feels']):
                internal_hits.append(a[:30] + "...")

        return {
            'name_crowding': crowding,
            'unique_char_count': char_count,
            'similar_name_pairs': similar,
            'internal_state_hits': internal_hits
        }

    def _extract_narrative_metadata(self, lines):
        text = " ".join([l['text'] for l in lines]).lower()
        vocab = set(re.findall(r'\b\w+\b', text))
        
        # Calculate base confidence for this scene analysis
        confidence = 0.4 # Default for lexical fallback
        if getattr(self, 'classifier', None): confidence = 0.9
        elif getattr(self, 'spacy_model', None): confidence = 0.7
        
        # 1. AI-Enhanced Cognitive Stakes Detection
        scores = self._ai_stakes_detection(text)
        if not scores:
            # Enhanced heuristic fallback with semantic awareness
            scores = self._contextual_stakes_detection(text)
            
        dominant = 'Unknown'
        if scores:
            max_val = -1.0
            for k, v in scores.items():
                try:
                    # Type narrowing to satisfy the IDE and ensure safety
                    if isinstance(v, (int, float, str)):
                        if isinstance(v, str) and not v.strip():
                            curr_val = 0.0
                        else:
                            curr_val = float(v)
                        
                        if curr_val > max_val:
                            max_val = curr_val
                            dominant = k
                except (ValueError, TypeError):
                    continue
            
        # 2. Character Arcs (Per-scene vectors based on context, not just word count)
        # Collect diagnostic representative quotes for later reference
        rep_dialogue = ""
        max_d_len = -1
        rep_action = ""
        max_a_len = -1
        
        for l in lines:
            txt = l.get('text', '')
            tag = l.get('tag', '')
            if tag == 'D' and len(txt) > max_d_len:
                max_d_len = len(txt)
                rep_dialogue = txt
            elif tag == 'A' and len(txt) > max_a_len:
                max_a_len = len(txt)
                rep_action = txt
        arcs = {}
        curr = None
        proactive_lexicon = {'go', 'do', 'will', 'must', 'shall', 'stop', 'done', 'kill', 'give', 'take', 'enough', 'order', 'clear', 'business', 'family', 'offer', 'refuse', 'respect', 'decide', 'arrange', 'settle', 'deal', 'demand', 'insist', 'command', 'forbid', 'allow', 'never', 'always', 'swear'}
        
        # Diagnostics for scene-level features
        monologues = []
        current_mono_len = 0
        
        sticho_count = 0
        prev_tag = None
        
        passive_count = 0
        passive_examples = []
        
        for i, l in enumerate(lines):
            txt = l.get('text', '').strip()
            tag = l.get('tag', '')
            
            # 1. Monologue & Stichomythia Tracking
            if tag == 'D':
                # Stichomythia: Rapid-fire single-line exchanges
                if prev_tag == 'D' and len(txt.split()) < 10:
                    sticho_count += 1
                
                # Monologue: Long uninterrupted speech
                current_mono_len += 1
            elif tag == 'C':
                # End of a monologue?
                if current_mono_len >= 8:
                    monologues.append({'character': curr, 'length': current_mono_len})
                current_mono_len = 0 # Character tag breaks the monologue (unless it's the same char, but we follow the change of tag)
            else:
                current_mono_len = 0

            # 2. Passive Voice Detection in Action lines
            if tag == 'A':
                if getattr(self, 'spacy_model', None):
                    try:
                        doc = self.spacy_model(txt)
                        is_passive = any(token.dep_ == "auxpass" for token in doc)
                        if is_passive:
                            passive_count += 1
                            if len(passive_examples) < 2: passive_examples.append(txt)
                        continue
                    except Exception:
                        pass
                        
                passive_markers = [
                    r'\bis being\b', r'\bwas being\b', r'\bhas been\b', r'\bhad been\b',
                    r'\bis seen\b', r'\bare seen\b', r'\bwas seen\b', r'\bi?s heard\b',
                    r'\bi?s felt\b', r'\bi?s watched\b'
                ]
                for p in passive_markers:
                    if re.search(p, txt, re.I):
                        passive_count += 1
                        if len(passive_examples) < 2: passive_examples.append(txt)

            # 3. Character-level Arcs & Voice Texture
            if tag == 'C': 
                name = normalize_character_name(txt)
                if name: curr = name
                else: curr = None
            elif tag == 'D' and curr:
                if curr not in arcs: 
                    arcs[curr] = {
                        'sentiment': 0.0, 'agency': 0.1, 'line_count': 0,
                        'complexity': 0.0, 'positivity': 0.0, 'punctuation_rate': 0.0
                    }
                arcs[curr]['line_count'] += 1
                dial_text = txt.lower()
                dial_words = re.findall(r'\b\w+\b', dial_text)
                
                # Voice Texture Fix (Fix 4):
                word_lens = [len(w) for w in dial_words]
                arcs[curr]['complexity'] += statistics.mean(word_lens) if word_lens else 0
                arcs[curr]['positivity'] += sum(1 for w in dial_words if w in ['yes', 'love', 'good', 'happy', 'safe']) / max(1, len(dial_words))
                arcs[curr]['punctuation_rate'] += (txt.count('.') + txt.count(',') + txt.count('!') + txt.count('?')) / max(1, len(txt))

                # Agency Logic
                is_question = '?' in dial_text
                is_command = ('!' in dial_text or txt.isupper()) and len(dial_words) < 8
                proactive_count = len(set(dial_words).intersection(proactive_lexicon))
                
                agency_inc = 0.1 # Base participation
                if is_command: agency_inc += 0.7
                elif is_question: agency_inc += 0.1 # Reduced bonus for asking questions
                agency_inc += (proactive_count * 0.6)
                
                if any(w in dial_text for w in ['maybe', 'sorry', 'i think', 'perhaps', 'suppose']):
                    agency_inc -= 0.2
                
                arcs[curr]['agency'] += agency_inc
                arcs[curr]['sentiment'] += 0.1 if 'yes' in dial_text else (-0.1 if 'no' in dial_text else 0)
            
            prev_tag = tag

        # Finalize Monologue at end of scene
        if current_mono_len >= 8:
            monologues.append({'character': curr, 'length': current_mono_len})
        
        # Normalize Agency & Voice Texture
        for c in arcs:
            n = max(1, arcs[c]['line_count'])
            arcs[c]['agency'] = round(min(1.0, arcs[c]['agency'] / (1.0 + n * 0.15)), 3)
            arcs[c]['sentiment'] = round(max(-1.0, min(1.0, arcs[c]['sentiment'] / n)), 3)
            # Normalize voice features
            arcs[c]['complexity'] = round(arcs[c]['complexity'] / n, 2)
            arcs[c]['positivity'] = round(arcs[c]['positivity'] / n, 2)
            arcs[c]['punctuation_rate'] = round(arcs[c]['punctuation_rate'] / n, 3)

        # 4. Scene-level Efficiency/Diagnostics
        n_lines = len([l for l in lines if l['tag'] in ['D', 'A']])
        economy_score = min(100, (sum(1 for l in lines if l['tag'] == 'D') * 5 + sum(1 for l in lines if l['tag'] == 'A') * 3))
        economy_label = 'High Economy' if economy_score < 40 else 'Moderate Economy' if economy_score < 75 else 'Low Economy'
        
        # 5. Opening Hook Detection (Rule based for Scene 0 only)
        hook_label = 'Indeterminate'
        lines_before = 0
        if lines:
            for i, l in enumerate(lines[:15]):
                if any(w in l['text'].lower() for w in ['gun', 'blood', 'shot', 'kill', 'fight', 'scream', 'run']):
                    hook_label = 'Strong Hook'
                    lines_before = i
                    break

        # 6. Masterclass Diagnostics (Smart Heuristics using structural context)
        d_lines = [l['text'].lower() for l in lines if l['tag'] == 'D']
        a_lines = [l['text'].lower() for l in lines if l['tag'] == 'A']
        all_text = " ".join([l['text'] for l in lines]).lower()
        
        # On-the-Nose: Direct emotion stating in dialogue
        otn_phrases = ['i feel', 'i am feeling', 'i am very angry', 'i am so sad', 'i am depressed', 'i hate you so much', 'i am terrified', 'i love you so much', 'i am so mad']
        otn_hits = sum(1 for d in d_lines if any(p in d for p in otn_phrases))
        
        # Shoe-Leather: Pleasantries in the VERY FIRST few dialogue lines of a scene
        shoe_leather_phrases = ['hello', 'hi ', 'hey ', 'good morning', 'how are you', 'how have you been', 'nice to see you', 'good afternoon', 'whats up', 'what is up']
        has_shoe_leather = False
        if len(d_lines) > 0:
            first_few = " ".join(d_lines[:3])
            has_shoe_leather = any(p in first_few for p in shoe_leather_phrases)
            
        # Tell vs Show: Internal emotional states described in Action lines
        emotion_adjectives = ['angry', 'sad', 'happy', 'depressed', 'terrified', 'furious', 'devastated', 'upset', 'jealous', 'nervous', 'anxious']
        tvs_hits = 0
        for a in a_lines:
            for em in emotion_adjectives:
                if f" is {em}" in a or f" feels {em}" in a or f" seems {em}" in a or f" looks {em}" in a:
                    tvs_hits += 1

        # Purpose Detection: Based on action vs dialogue vs vocabulary novelty
        purpose = 'Transition'
        if getattr(self, 'classifier', None):
            try:
                purpose_labels = ['Transition', 'Escalation / Action', 'Revelation / Discovery', 'Negotiation / Conflict']
                result = self.classifier(all_text[:1024], purpose_labels, multi_label=False)
                purpose = result['labels'][0]
            except Exception:
                if len(a_lines) > len(d_lines) * 2 and len(a_lines) > 5:
                    purpose = 'Escalation / Action'
                elif any(w in all_text for w in ['realize', 'discover', 'reveal', 'finds', 'truth']):
                    purpose = 'Revelation / Discovery'
                elif len(d_lines) > 10:
                    purpose = 'Negotiation / Conflict'
        else:
            if len(a_lines) > len(d_lines) * 2 and len(a_lines) > 5:
                purpose = 'Escalation / Action'
            elif any(w in all_text for w in ['realize', 'discover', 'reveal', 'finds', 'truth']):
                purpose = 'Revelation / Discovery'
            elif len(d_lines) > 10:
                purpose = 'Negotiation / Conflict'

        # Check for narrative closure signals in action lines (Strict death/exit detection)
        # Only unambiguous death words — 'falls', 'collapses', 'slumps' are excluded
        # because they appear constantly in normal action (a man falls into a chair, etc.)
        death_lexicon = {
            'dies', 'dead', 'killed', 'murdered', 'corpse', 'funeral',
            'deathbed', 'fatal', 'slain', 'no longer with us', 'rest in peace',
            'is shot', 'is stabbed', 'shoot him', 'stabs him', 'stabs her',
            'shoots him', 'shoots her', 'blows his brains', 'blows her brains'
        }
        scene_has_death = any(w in all_text for w in death_lexicon)

        return {
            'character_scene_vectors': arcs,
            'stakes': {'dominant': dominant, 'breakdown': {k: round(float(v) if (not isinstance(v, str) or v.strip()) else 0.0, 2) for k, v in scores.items() if isinstance(v, (int, float, str))}},
            'payoff': {'payoff_density': round(sum(float(v) if (not isinstance(v, str) or v.strip()) else 0.0 for v in scores.values() if isinstance(v, (int, float, str))) / max(1, len(lines)), 2)},
            'stichomythia': {'has_stichomythia': sticho_count > 4, 'count': sticho_count},
            'monologue_data': {'has_monologue': len(monologues) > 0, 'monologues': monologues},
            'passive_voice': {'passive_ratio': passive_count / max(1, n_lines), 'passive_count': passive_count, 'examples': passive_examples},
            'scene_economy': {'economy_label': economy_label, 'economy_score': economy_score},
            'opening_hook': {'hook_label': hook_label, 'lines_before_conflict': lines_before},
            'purpose': {'purpose': purpose},
            'on_the_nose': {
                'on_the_nose_ratio': round(otn_hits / max(1, len(d_lines)), 3),
                'hit_count': otn_hits
            },
            'shoe_leather': {
                'has_shoe_leather': has_shoe_leather,
                'scene_start_filler': 3 if has_shoe_leather else 0
            },
            'tell_vs_show': {'tell_ratio': min(1.0, tvs_hits / max(1, len(a_lines))), 'literal_emotions': tvs_hits},
            'narrative_closure': scene_has_death,
            'representative_dialogue': rep_dialogue,
            'representative_action': rep_action,
            'scene_vocabulary': list(vocab),
            'research_telemetry': {
                'analytical_confidence': confidence,
                'semantic_density': len(vocab) / max(1, len(text.split())),
                'heuristic_fallback': confidence < 0.8
            }
        }

    def _ai_sentiment_analysis(self, text):
        """
        AI-powered sentiment analysis using zero-shot classification
        Falls back gracefully if models are unavailable
        """
        if not self.classifier or len(text) < 50:
            return None
            
        try:
            result = self.classifier(text[:1024], self.sentiment_labels)
            if result and result.get('labels'):
                scores = dict(zip(result['labels'], result['scores']))
                tension = scores.get('High Tension / Conflict', 0)
                despair = scores.get('Despair / Loss', 0)
                positive = scores.get('Positive Connection', 0)
                neutral = scores.get('Neutral / Calm', 0)
                
                # Map to VADER-like format with cinematic meaning
                compound = tension + (positive * 0.5) - (despair * 0.8)
                return {
                    'pos': round(positive, 3),
                    'neg': round(despair, 3), 
                    'neu': round(neutral, 3),
                    'compound': round(max(-1.0, min(1.0, compound)), 3)
                }
        except:
            pass
            
        return None

    def _contextual_sentiment_fallback(self, text, all_text):
        """
        Enhanced semantic fallback with contextual awareness
        """
        # Expanded narrative lexicon with contextual weighting
        conflict_words = {
            'high': ['gun', 'blood', 'kill', 'fight', 'attack', 'weapon', 'explosion', 'crash'],
            'medium': ['stop', 'no', 'never', 'hate', 'leave', 'angry', 'shout', 'scream'],
            'low': ['worry', 'concern', 'problem', 'issue', 'trouble', 'difficult']
        }
        
        connection_words = {
            'high': ['love', 'beautiful', 'perfect', 'wonderful', 'amazing', 'incredible'],
            'medium': ['happy', 'good', 'nice', 'great', 'help', 'together', 'safe'],
            'low': ['okay', 'fine', 'well', 'better', 'hope', 'maybe', 'think']
        }
        
        # Weighted counting based on word importance
        conflict_score = 0
        for level, words in conflict_words.items():
            weight = {'high': 3, 'medium': 2, 'low': 1}[level]
            conflict_score += sum(text.lower().count(w) * weight for w in words)
            
        connection_score = 0
        for level, words in connection_words.items():
            weight = {'high': 3, 'medium': 2, 'low': 1}[level]
            connection_score += sum(text.lower().count(w) * weight for w in words)
        
        total_words = len(text.split())
        if total_words == 0:
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}
        
        # Calculate compound with adaptive normalization
        raw_compound = (connection_score - conflict_score) / total_words
        compound = max(-1.0, min(1.0, raw_compound * 3.0))  # Amplify signal
        
        return {
            'pos': max(0.0, compound) if compound > 0 else 0.0,
            'neg': abs(compound) if compound < 0 else 0.0,
            'neu': 1.0 - abs(compound),
            'compound': round(compound, 3)
        }

    def _ai_stakes_detection(self, text):
        """
        AI-powered stakes detection using zero-shot classification
        """
        if not self.classifier or len(text) < 30:
            return None
            
        try:
            result = self.classifier(text[:1024], self.stakes_labels)
            if result and result.get('labels'):
                label_map = {
                    'Physical Survival': 'Physical',
                    'Emotional Connection': 'Emotional', 
                    'Social Status': 'Social',
                    'Moral Dilemma': 'Moral',
                    'Existential Dread': 'Existential'
                }
                scores = {label_map[k]: v for k, v in zip(result['labels'], result['scores'])}
                dominant = label_map[result['labels'][0]]
                
                return {
                    'dominant': dominant,
                    'breakdown': {k: round(v, 2) for k, v in scores.items()},
                    'confidence': 0.92,
                    'ai_detected': True
                }
        except:
            pass
            
        return None

    def _contextual_stakes_detection(self, text):
        """
        Enhanced heuristic stakes detection with semantic awareness
        """
        # Expanded stakes lexicon with contextual patterns
        stakes_map = {
            'Physical': {
                'words': ['kill', 'blood', 'gun', 'fight', 'run', 'dead', 'attack', 'hide', 'weapon', 'explosion', 'crash'],
                'patterns': [r'\\bwill\\s+die\\b', r'\\bgot\\s+shot\\b', r'\\bfighting\\s+for\\b'],
                'weight': 1.5
            },
            'Emotional': {
                'words': ['love', 'cry', 'heart', 'fear', 'happy', 'sad', 'forgive', 'hate', 'kiss', 'hug'],
                'patterns': [r'\\bin\\s+love\\b', r'\\bheart\\s+breaks?\\b', r'\\bcannot\\s+live\\b'],
                'weight': 1.3
            },
            'Social': {
                'words': ['reputation', 'friend', 'betray', 'secret', 'status', 'boss', 'fired', 'party', 'promotion'],
                'patterns': [r'\\bleave\\s+me\\b', r'\\btold\\s+everyone\\b', r'\\bpublic\\s+shame\\b'],
                'weight': 1.2
            },
            'Moral': {
                'words': ['right', 'wrong', 'lie', 'truth', 'guilt', 'confess', 'promise', 'swear', 'justice'],
                'patterns': [r'\\bmust\\s+do\\b', r'\\bcannot\\s+lie\\b', r'\\btell\\s+the\\s+truth\\b'],
                'weight': 1.4
            },
            'Existential': {
                'words': ['meaning', 'exist', 'god', 'death', 'soul', 'purpose', 'destiny', 'life', 'nothing'],
                'patterns': [r'\\bwhat\\s+is\\s+the\\s+point\\b', r'\\bwhy\\s+are\\s+we\\s+here\\b', r'\\bnothing\\s+matters\\b'],
                'weight': 1.6
            }
        }
        
        raw_scores = {}
        total_text = text.lower()
        
        for stake_type, config in stakes_map.items():
            score = 0
            
            # Word-based scoring with weights
            for word in config['words']:
                score += total_text.count(word) * config['weight']
            
            # Pattern-based scoring for higher weight
            for pattern in config['patterns']:
                if re.search(pattern, total_text):
                    score += 3.0 * config['weight']
            
            raw_scores[stake_type] = score
        
        # Normalize scores
        total_raw = sum(raw_scores.values()) or 1
        scores = {k: v/total_raw for k, v in raw_scores.items()}
        
        dominant = max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else 'Social'
        
        return {
            'character_scene_vectors': {},  # Will be filled by calling method
            'stakes': {
                'dominant': dominant,
                'breakdown': {k: round(v, 2) for k, v in scores.items()}
            },
            'payoff': {'payoff_density': round(sum(scores.values()) / max(1, len(text.split())), 2)},
            'stichomythia': {'has_stichomythia': False, 'count': 0},
            'monologue_data': {'has_monologue': False, 'monologues': []},
            'passive_voice': {'passive_ratio': 0, 'passive_count': 0, 'examples': []},
            'scene_economy': {'economy_label': 'Moderate Economy', 'economy_score': 50},
            'opening_hook': {'hook_label': 'Indeterminate', 'lines_before_conflict': 0},
            'purpose': {'purpose': 'Transition'},
            'on_the_nose': {'on_the_nose_ratio': 0, 'hit_count': 0},
            'shoe_leather': {'has_shoe_leather': False, 'scene_start_filler': 0},
            'tell_vs_show': {'tell_ratio': 0, 'literal_emotions': 0},
            'narrative_closure': False,
            'representative_dialogue': '',
            'representative_action': '',
            'scene_vocabulary': list(set(re.findall(r'\\b\\w+\\b', text))),
            'research_telemetry': {
                'analytical_confidence': 0.75,
                'semantic_density': len(set(text.split())) / max(1, len(text.split())),
                'heuristic_fallback': True
            }
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
