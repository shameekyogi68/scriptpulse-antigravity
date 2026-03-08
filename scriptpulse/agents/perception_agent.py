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
    # Handle suffixes without parentheses (e.g. MICHAEL-O.S.)
    stemmed = re.sub(r'[-\s](O\.?S\.?|V\.?O\.?|ALT|OFF-SCREEN|DASHES|FILTERED)$', '', stemmed)
    
    # Upper, strip punctuation but keep internal spaces/hashes
    clean = re.sub(r'[^A-Z0-9\s#]', '', stemmed).strip()
    
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
    """Consolidated Encoding Agent - High Performance, Low Complexity"""
    
    def __init__(self):
        self.classifier = manager.get_zero_shot()
        self.stakes_labels = ['Physical Survival', 'Emotional Connection', 'Social Status', 'Moral Dilemma', 'Existential Dread']
        self.sentiment_labels = ['High Tension / Conflict', 'Positive Connection', 'Despair / Loss', 'Neutral / Calm']

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
            
            # 6. Narrative Metadata (For Charts/UI)
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
        
        if not words: return {'mean_sentence_length': 0, 'sentence_length_variance': 0, 'sentence_count': 0, 'idea_density': 0}
        
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths)/len(lengths) if lengths else 0
        var = sum((x-avg)**2 for x in lengths)/len(lengths) if lengths else 0
        uniq = len(set(words))
        
        return {
            'mean_sentence_length': round(avg, 2),
            'sentence_length_variance': round(var, 2),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'idea_density': round(uniq/len(words), 3) if sum(lengths) > 0 else 0,
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
        # Assuming ~180-200 words per minute contextually
        action_seconds = action_words * 0.3
        
        # Dialogue is spoken quickly
        dialogue_seconds = dialogue_words * 0.35
        
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
        words = re.findall(r'\b\w+\b', text)
        if not words: return 0.0
        counts = Counter(words)
        total = len(words)
        entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
        return round(entropy, 3)

    def _extract_affective_load(self, lines):
        # 1. Prepare text for analysis (Action 'A' and Dialogue 'D')
        text = " ".join([l['text'] for l in lines if l['tag'] in ['D', 'A']])
        all_text = " ".join([l['text'] for l in lines]).lower()
        if not text.strip():
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}

        # 2. High-Priority Narrative Override: Violence & Death (Task 1)
        # We must detect deaths even in action-heavy scenes without 'C' tags (explicit character names over dialogue).
        violence_triggers = [
            'shot', 'killed', 'ambush', 'trap', 'gunfire', 'body', 'murder', 'blood', 'execution', 
            'assassinate', 'bullet', 'massacre', 'stabbed', 'slaughter', 'wound', 'dying'
        ]
        
        # Check for character presence via tags OR capitalized names in Action lines
        has_character = any(l['tag'] == 'C' for l in lines)
        if not has_character:
            # Look for [A-Z]{3,} name signals in Action text to identify character agency in dialogue-free scenes
            has_character = any(re.search(r'\b[A-Z]{3,}\b', l['text']) for l in lines if l['tag'] == 'A')

        has_violence = any(w in all_text for w in violence_triggers)
        if has_violence and has_character:
            # Force high-stakes Negative Sentiment for these cinematic story-beats
            return {'pos': 0.01, 'neg': 0.95, 'neu': 0.04, 'compound': -0.98}

        if self.classifier:
            try:
                # Use Zero-Shot for Dramatic Context Sentiment (Not Twitter sentiment)
                res = self.classifier(text[:1024], self.sentiment_labels)
                scores = dict(zip(res['labels'], res['scores']))
                tension = scores.get('High Tension / Conflict', 0)
                despair = scores.get('Despair / Loss', 0)
                positive = scores.get('Positive Connection', 0)
                
                # Map to standard VADER-like keys for pipeline compatibility, but with cinematic meaning
                compound = tension + (positive * 0.5) - (despair * 0.8)
                return {'pos': round(positive, 3), 'neg': round(despair, 3), 'neu': round(1 - (tension+despair+positive), 3), 'compound': round(compound, 3)}
            except:
                pass
                
        # Semantic Fallback (Simulated Narrative Lexicon instead of Social Media Lexicon)
        conflict_words = sum(text.lower().count(w) for w in ['gun', 'blood', 'stop', 'no', 'never', 'die', 'kill', 'hate', 'leave'])
        connection_words = sum(text.lower().count(w) for w in ['love', 'together', 'yes', 'help', 'beautiful', 'safe', 'stay'])
        total_words = len(text.split())
        
        compound = (connection_words - conflict_words) / max(1, total_words) * 5.0 # normalized boost
        return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': round(max(-1.0, min(1.0, compound)), 3)}

    def _extract_structural(self, scene, all_scenes, idx):
        if idx == 0: return {'event_boundary_score': 0.0}
        gap = scene['start_line'] - all_scenes[idx-1]['end_line']
        return {'event_boundary_score': min(100.0, gap * 2.0)}

    def _extract_ambient(self, ling, dial, vis):
        score = ( (1 - dial['turn_velocity']) + (1 - min(1.0, vis['action_lines']/10)) ) / 2
        return {
            'ambient_score': round(score, 3),
            'component_scores': {'stillness': round(1-vis['visual_intensity'], 3)}
        }

    def _extract_micro(self, lines):
        return [{'tag': l['tag'], 'word_count': len(l['text'].split())} for l in lines]

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
        
        # 1. Real Cognitive Stakes Detection (ML or Advanced Heuristics)
        dominant = 'Physical'
        scores = {}
        confidence = 0.65 # Base heuristic confidence
        
        if self.classifier and len(text.split()) > 10:
            try:
                res = self.classifier(text[:1024], self.stakes_labels)
                label_map = {'Physical Survival': 'Physical', 'Emotional Connection': 'Emotional', 'Social Status': 'Social', 'Moral Dilemma': 'Moral', 'Existential Dread': 'Existential'}
                scores = {label_map[k]: v for k, v in zip(res['labels'], res['scores'])}
                dominant = label_map[res['labels'][0]]
                confidence = 0.92 # ML-backed confidence
            except:
                pass
        
        if not scores: # Fallback
            stakes_map = {
                'Physical': ['kill', 'blood', 'gun', 'fight', 'run', 'dead', 'attack', 'hide'],
                'Emotional': ['love', 'cry', 'heart', 'fear', 'happy', 'sad', 'forgive', 'hate'],
                'Social': ['reputation', 'friend', 'betray', 'secret', 'status', 'boss', 'fired', 'party'],
                'Moral': ['right', 'wrong', 'lie', 'truth', 'guilt', 'confess', 'promise', 'swear'],
                'Existential': ['meaning', 'exist', 'god', 'death', 'soul', 'purpose', 'destiny']
            }
            raw_scores = {k: sum(text.count(w) for w in v) for k, v in stakes_map.items()}
            dominant = max(raw_scores, key=raw_scores.get) if any(raw_scores.values()) else 'Social'
            total_raw = sum(raw_scores.values()) or 1
            scores = {k: v/total_raw for k, v in raw_scores.items()}
        
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
        proactive_lexicon = {'go', 'do', 'will', 'must', 'shall', 'stop', 'done', 'kill', 'give', 'take', 'enough', 'order', 'clear', 'business', 'family'}
        
        # Check for narrative closure signals in action lines (Strict death/exit detection)
        # Removed 'leaves', 'gone', 'shot', 'fires' etc. as they cause false positives for living characters
        death_lexicon = {
            'dies', 'dead', 'killed', 'murdered', 'body', 'corpse', 'funeral', 
            'passing', 'expiring', 'deathbed', 'fatal', 'slain', 'slumps', 'falls', 'collapses',
            'no longer with us', 'rest in peace'
        }
        all_action_text = " ".join([l['text'].lower() for l in lines if l['tag'] == 'A'])
        scene_has_death = any(w in all_action_text for w in death_lexicon)

        for i, l in enumerate(lines):
            if l['tag'] == 'C': 
                name = normalize_character_name(l['text'])
                if name: curr = name
                else: curr = None
            elif l['tag'] == 'D' and curr:
                if curr not in arcs: arcs[curr] = {'sentiment': 0.0, 'agency': 0.1, 'line_count': 0}
                arcs[curr]['line_count'] += 1
                dial_text = l['text'].lower()
                dial_words = set(re.findall(r'\b\w+\b', dial_text))
                
                # Agency: Balanced between syntax (questions/commands) and proactivity
                is_question = '?' in dial_text
                is_command = ('!' in dial_text or dial_text.isupper()) and len(dial_text.split()) < 8
                
                proactive_count = len(dial_words.intersection(proactive_lexicon))
                
                # Characters who speak more in a scene generally have higher agency (control)
                # But they must also use decisive language
                agency_inc = 0.1 # Base participation
                if is_command: agency_inc += 0.5
                elif is_question: agency_inc += 0.3 # Asking questions is often investigative control
                
                agency_inc += (proactive_count * 0.6) # Boosted from 0.4

                
                # Passive markers
                if any(w in dial_text for w in ['maybe', 'sorry', 'i think', 'perhaps', 'suppose']):
                    agency_inc -= 0.2
                
                arcs[curr]['agency'] += agency_inc
                arcs[curr]['sentiment'] += 0.1 if 'yes' in dial_text else (-0.1 if 'no' in dial_text else 0)
        
        # Normalize Agency by participation density so quiet but decisive leaders aren't penalized
        for c in arcs:
            # Agency cap - Dampened divisor to allow growth without hitting 100% too easily
            arcs[c]['agency'] = round(min(1.0, arcs[c]['agency'] / (1.0 + arcs[c]['line_count'] * 0.15)), 3)
            arcs[c]['sentiment'] = round(max(-1.0, min(1.0, arcs[c]['sentiment'] / max(1, arcs[c]['line_count']))), 3)
        
        # 3. Masterclass Diagnostics (Smart Heuristics using structural context)
        d_lines = [l['text'].lower() for l in lines if l['tag'] == 'D']
        a_lines = [l['text'].lower() for l in lines if l['tag'] == 'A']
        
        # On-the-Nose: Direct emotion stating in dialogue
        otn_phrases = ['i feel', 'i am feeling', 'i am very angry', 'i am so sad', 'i am depressed', 'i hate you so much', 'i am terrified', 'i love you so much', 'i am so mad']
        otn_hits = sum(1 for d in d_lines if any(p in d for p in otn_phrases))
        
        # Shoe-Leather: Pleasantries in the VERY FIRST few dialogue lines of a scene
        shoe_leather_phrases = ['hello', 'hi ', 'hey ', 'good morning', 'how are you', 'how have you been', 'nice to see you', 'good afternoon', 'whats up', 'what is up']
        has_shoe_leather = False
        if len(d_lines) > 0:
            first_few = " ".join(d_lines[:3])
            has_shoe_leather = any(p in first_few for p in shoe_leather_phrases)
            
        # Tell vs Show: Internal emotional states described in Action lines (which can't be filmed easily)
        emotion_adjectives = ['angry', 'sad', 'happy', 'depressed', 'terrified', 'furious', 'devastated', 'upset', 'jealous', 'nervous', 'anxious']
        tvs_hits = 0
        for a in a_lines:
            for em in emotion_adjectives:
                if f" is {em}" in a or f" feels {em}" in a or f" seems {em}" in a or f" looks {em}" in a:
                    tvs_hits += 1

        # Purpose Detection: Based on action vs dialogue vs vocabulary novelty
        purpose = 'Transition'
        if len(a_lines) > len(d_lines) * 2 and len(a_lines) > 5:
            purpose = 'Escalation / Action'
        elif any(w in text for w in ['realize', 'discover', 'reveal', 'finds', 'truth']):
            purpose = 'Revelation / Discovery'
        elif len(d_lines) > 10:
            purpose = 'Negotiation / Conflict'

        return {
            'stakes': {'dominant': dominant, 'breakdown': {k: round(v, 2) for k,v in scores.items()}},
            'payoff': {'payoff_density': round(sum(scores.values()) / max(1, len(lines)), 2)},
            'on_the_nose': {
                'on_the_nose_ratio': round(otn_hits / max(1, len(d_lines)), 3),
                'hit_count': otn_hits
            },
            'shoe_leather': {
                'has_shoe_leather': has_shoe_leather,
                'scene_start_filler': 3 if has_shoe_leather else 0 # Placeholder for UI
            },
            'tell_vs_show': {'tell_ratio': min(1.0, tvs_hits / max(1, len(a_lines))), 'literal_emotions': tvs_hits},
            'purpose': {'purpose': purpose},
            'character_scene_vectors': arcs,
            'narrative_closure': scene_has_death,  # Inform the downstream agent if characters might be 'resolved' here
            'representative_dialogue': rep_dialogue, # Used by writer agent for pulls
            'representative_action': rep_action,
            'scene_vocabulary': list(vocab),
            'research_telemetry': {
                'analytical_confidence': confidence,
                'semantic_density': len(vocab) / max(1, len(text.split())),
                'heuristic_fallback': confidence < 0.8
            }
        }
