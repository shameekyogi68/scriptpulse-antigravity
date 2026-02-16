"""
Perception Agent - Handling Feature Extraction (The Senses)
Consolidates: encoding.py, imagery.py, social.py, syntax.py, voice.py, valence.py, semantic.py, embeddings.py, coherence.py
"""

import re
import math
import collections
import statistics
from collections import Counter
from ..utils.model_manager import manager as global_manager

# =============================================================================
# ENCODING LOGIC (formerly encoding.py)
# =============================================================================

class EncodingAgent:
    """Structural Encoding Agent - Observable Feature Extraction"""
    
    def run(self, input_data):
        scenes = input_data.get('scenes', [])
        lines = input_data.get('lines', [])
        if not scenes: return []
        
        feature_vectors = []
        for i, scene in enumerate(scenes):
            if 'lines' in scene:
                scene_lines = scene['lines']
            else:
                scene_lines = self.get_scene_lines(scene, lines)
            
            features = {
                'scene_index': scene['scene_index'],
                'linguistic_load': self.extract_linguistic_load(scene_lines),
                'dialogue_dynamics': self.extract_dialogue_dynamics(scene_lines),
                'visual_abstraction': self.extract_visual_abstraction(scene_lines),
                'referential_load': self.extract_referential_load(scene_lines),
                'structural_change': self.extract_structural_change(scene, scenes, i),
                'ambient_signals': self.extract_ambient_signals(scene_lines),
                'micro_structure': self.extract_micro_structure(scene_lines),
                'entropy_score': self.extract_information_entropy(scene_lines)
            }
            feature_vectors.append(features)
        return feature_vectors

    def get_scene_lines(self, scene, all_lines):
        start = scene['start_line']
        end = scene['end_line']
        return [line for line in all_lines if start <= line['line_index'] <= end]

    def extract_linguistic_load(self, scene_lines):
        all_text = ' '.join([line['text'] for line in scene_lines if line['text'].strip()])
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {'sentence_count': 0, 'mean_sentence_length': 0.0, 'max_sentence_length': 0, 'sentence_length_variance': 0.0}
        
        word_counts = [len(s.split()) for s in sentences]
        mean_length = sum(word_counts) / len(word_counts)
        max_length = max(word_counts)
        variance = sum((x - mean_length) ** 2 for x in word_counts) / len(word_counts)
        
        return {
            'sentence_count': len(sentences),
            'mean_sentence_length': round(mean_length, 2),
            'max_sentence_length': max_length,
            'sentence_length_variance': round(variance, 2)
        }

    def extract_dialogue_dynamics(self, scene_lines):
        dialogue_lines = [line for line in scene_lines if line['tag'] == 'D']
        character_lines = [line for line in scene_lines if line['tag'] == 'C']
        
        dialogue_count = len(dialogue_lines)
        speaker_count = len(character_lines)
        
        switches = 0
        if speaker_count > 1:
            for i in range(1, len(character_lines)):
                if character_lines[i]['text'] != character_lines[i-1]['text']:
                    switches += 1
        
        total_lines = len(scene_lines)
        velocity = dialogue_count / total_lines if total_lines > 0 else 0.0
        
        monologue_runs = 0
        if speaker_count > 0:
            run_length = 1
            for i in range(1, len(character_lines)):
                if character_lines[i]['text'] == character_lines[i-1]['text']:
                    run_length += 1
                else:
                    if run_length > 1: monologue_runs += 1
                    run_length = 1
            if run_length > 1: monologue_runs += 1
            
        return {
            'dialogue_turns': dialogue_count,
            'speaker_switches': switches,
            'turn_velocity': round(velocity, 3),
            'monologue_runs': monologue_runs
        }

    def extract_visual_abstraction(self, scene_lines):
        action_lines = [line for line in scene_lines if line['tag'] == 'A']
        action_count = len(action_lines)
        
        continuous_runs = 0
        if action_count > 0:
            in_run = False
            for line in scene_lines:
                if line['tag'] == 'A':
                    if not in_run:
                        continuous_runs += 1
                        in_run = True
                else:
                    in_run = False
        
        return {
            'action_lines': action_count,
            'continuous_action_runs': continuous_runs,
            'vertical_writing_load': action_count
        }

    def extract_referential_load(self, scene_lines):
        character_lines = [line for line in scene_lines if line['tag'] == 'C']
        unique_characters = set(line['text'].strip() for line in character_lines)
        character_count = len(unique_characters)
        
        reintroductions = 0
        if len(character_lines) > 1:
            seen = set()
            for char_line in character_lines:
                char = char_line['text'].strip()
                if char in seen: reintroductions += 1
                seen.add(char)
        
        return {'active_character_count': character_count, 'character_reintroductions': reintroductions}

    def extract_structural_change(self, scene, all_scenes, current_index):
        if current_index == 0: return {'event_boundary_score': 0.0}
        prev_scene = all_scenes[current_index - 1]
        curr_start = scene.get('start_line', 0)
        prev_end = prev_scene.get('end_line', 0)
        line_gap = curr_start - prev_end
        total_lines = max(s.get('end_line', 0) for s in all_scenes) + 1
        normalized_score = line_gap / total_lines if total_lines > 0 else 0.0
        return {'event_boundary_score': round(normalized_score * 100, 2)}

    def extract_ambient_signals(self, scene_lines):
        dialogue = self.extract_dialogue_dynamics(scene_lines)
        visual = self.extract_visual_abstraction(scene_lines)
        linguistic = self.extract_linguistic_load(scene_lines)
        
        stillness = 1.0 - min(1.0, visual['action_lines'] / 10.0)
        sparse_dialogue = 1.0 - dialogue['turn_velocity']
        low_complexity = 1.0 - min(1.0, linguistic['sentence_length_variance'] / 20.0)
        short_sentences = 1.0 - min(1.0, linguistic['mean_sentence_length'] / 15.0)
        
        ambient_score = (0.35 * stillness + 0.30 * sparse_dialogue + 0.20 * low_complexity + 0.15 * short_sentences)
        
        return {
            'ambient_score': round(ambient_score, 3),
            'is_ambient': ambient_score > 0.6,
            'component_scores': {
                'stillness': round(stillness, 3),
                'sparse_dialogue': round(sparse_dialogue, 3),
                'low_complexity': round(low_complexity, 3),
                'short_sentences': round(short_sentences, 3)
            }
        }

    def extract_micro_structure(self, scene_lines):
        micro_structure = []
        total_lines = len(scene_lines)
        for i, line in enumerate(scene_lines):
            text = line['text'].strip()
            word_count = len(text.split()) if text else 0
            micro_structure.append({
                'tag': line['tag'],
                'word_count': word_count,
                'rel_position': i / total_lines if total_lines > 0 else 0.0,
                'line_index': line['line_index']
            })
        return micro_structure

    def extract_information_entropy(self, scene_lines):
        text = ' '.join([line['text'] for line in scene_lines]).lower()
        words = re.findall(r'\b\w+\b', text)
        if not words: return 0.0
        counts = Counter(words)
        total_words = len(words)
        entropy = 0.0
        for count in counts.values():
            p = count / total_words
            if p > 0: entropy -= p * math.log2(p)
        return round(entropy, 3)


# =============================================================================
# IMAGERY LOGIC (formerly imagery.py)
# =============================================================================

class ImageryAgent:
    """ScriptPulse Imagery Agent - Visual Density Score"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        colors = {'red', 'blue', 'green', 'black', 'white', 'yellow', 'crimson', 'azure', 'neon', 'dark', 'bright', 'shadow', 'light', 'grey', 'purple', 'silver', 'gold'}
        optics = {'fade', 'cut', 'dissolve', 'zoom', 'pan', 'tilt', 'focus', 'blur', 'glimpse', 'stare', 'look', 'watch', 'see', 'view', 'angle', 'shot', 'pov'}
        textures = {'rough', 'smooth', 'slick', 'wet', 'dry', 'dusty', 'dirty', 'clean', 'pristine', 'shattered', 'broken', 'rusty', 'metallic', 'glass', 'wood'}
        kinetics = {'run', 'jump', 'fall', 'crash', 'explode', 'shatter', 'sprint', 'crawl', 'fly', 'drive', 'spin', 'roll', 'slide', 'hit', 'punch'}
        
        scores = []
        for scene in scenes:
            text = " ".join([l['text'] for l in scene['lines']]).lower()
            words = text.replace('.', '').replace(',', '').split()
            if not words:
                scores.append(0.0)
                continue
            hits = sum(1 for w in words if w in colors or w in optics or w in textures or w in kinetics)
            density = hits / len(words)
            normalized = min(1.0, density / 0.15)
            scores.append(normalized)
        return scores


# =============================================================================
# SOCIAL LOGIC (formerly social.py)
# =============================================================================

class SocialAgent:
    """ScriptPulse Social Agent - Social Tension"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        entropy_trace = []
        interaction_map = collections.defaultdict(list)
        
        for scene in scenes:
            lines = scene['lines']
            chars_in_scene = sorted(list(self.get_chars(scene)))
            
            if len(chars_in_scene) >= 2:
                for k in range(len(chars_in_scene)):
                    for j in range(k+1, len(chars_in_scene)):
                        c1 = chars_in_scene[k]
                        c2 = chars_in_scene[j]
                        pair = f"{c1}|{c2}"
                        interaction_map[pair].append(scene['scene_index'])
            
            speakers = []
            for line in lines:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name: speakers.append(name)
            
            if len(speakers) < 2:
                entropy_trace.append(0.0)
                continue
                
            degree_map = collections.defaultdict(int)
            for k in range(len(speakers) - 1):
                s1 = speakers[k]
                s2 = speakers[k+1]
                if s1 != s2:
                    degree_map[s1] += 1
                    degree_map[s2] += 1
                    
            total_degrees = sum(degree_map.values())
            if total_degrees == 0:
                entropy_trace.append(0.0)
                continue
                
            proportions = [d / total_degrees for d in degree_map.values()]
            entropy = 0.0
            for p in proportions:
                if p > 0: entropy -= p * math.log2(p)
            
            unique_speakers = len(degree_map)
            norm_entropy = entropy / math.log2(unique_speakers) if unique_speakers > 1 else 0.0
            entropy_trace.append(norm_entropy)
            
        return {'centrality_entropy': entropy_trace, 'interaction_map': dict(interaction_map)}

    def get_chars(self, scene):
        chars = set()
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name: chars.add(name)
        return chars


# =============================================================================
# SYNTAX LOGIC (formerly syntax.py)
# =============================================================================

class SyntaxAgent:
    """ScriptPulse Syntactic Agent - Clause Density"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        if not scenes: return {}
        
        complexity_scores = []
        patterns = [
            r'\bwhich\b', r'\bthat\b', r'\bwho\b', r'\bwhom\b', r'\bwhose\b',
            r'\bbecause\b', r'\balthough\b', r'\bif\b', r'\bwhile\b', r'\bwhen\b',
            r'\buntil\b', r'\bunless\b', r'\bsince\b', r'\bwhereas\b',
            r'[,;]\s*and\b', r'[,;]\s*but\b'
        ]
        regex = re.compile('|'.join(patterns), re.IGNORECASE)
        
        diction_issues = []
        
        for scene in scenes:
            lines = [l['text'] for l in scene['lines']]
            if not lines:
                complexity_scores.append(0.0)
                continue
            
            scene_total_words = 0
            scene_total_matches = 0
            
            for line in lines:
                matches = len(regex.findall(line))
                scene_total_matches += matches
                words_count = len(line.split())
                scene_total_words += words_count
            
            ratio = scene_total_matches / max(1, scene_total_words) * 20
            complexity_scores.append(min(1.0, ratio))
            
            cnt, exs = self.analyze_diction_weakness(scene['lines'])
            if cnt > 2: diction_issues.extend(exs)
            dumps = self.detect_exposition_dumps(scene['lines'])
            diction_issues.extend(dumps)
            
        return {'complexity_scores': complexity_scores, 'diction_issues': diction_issues}

    def analyze_diction_weakness(self, scene_lines):
        weak_markers = {'is', 'are', 'was', 'were', 'has', 'have', 'had'}
        weak_count = 0
        suggestions = []
        for line in scene_lines:
            if line.get('tag') == 'A':
                words = line['text'].lower().split()
                found = [w for w in words if w in weak_markers]
                if found:
                    weak_count += len(found)
                    if len(suggestions) < 3:
                        suggestions.append(f"Line {line.get('line_index', '?')}: usage of '{found[0]}' (Passive/Weak)")
        return weak_count, suggestions

    def detect_exposition_dumps(self, scene_lines):
        expos = []
        for line in scene_lines:
            if line.get('tag') == 'D':
                words = line['text'].split()
                if len(words) > 40:
                    avg_len = sum(len(w) for w in words)/len(words)
                    commas = line['text'].count(',')
                    if avg_len > 4.5 or commas > 3:
                        expos.append(f"Line {line.get('line_index', '?')}: High-Density Monologue ({len(words)} words). Risk of Exposition Dump.")
        return expos


# =============================================================================
# VOICE LOGIC (formerly voice.py)
# =============================================================================

class VoiceAgent:
    """ScriptPulse Voice Agent - Character Distinctiveness"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        char_text = collections.defaultdict(list)
        
        current_char = None
        for scene in scenes:
            for line in scene.get('lines', []):
                tag = line.get('tag', '')
                if tag in ('C', 'character'):
                    current_char = line['text'].split('(')[0].strip()
                elif tag in ('D', 'dialogue') and current_char:
                    if current_char not in char_text or line['text'] not in char_text[current_char]:
                        char_text[current_char].append(line['text'])
        
        fingerprints = {}
        active_verbs = {'run', 'hit', 'take', 'jump', 'decide', 'make', 'fight', 'stop', 'go', 'grab'}
        passive_markers = {'was', 'by', 'is', 'are', 'were', 'had', 'been'}
        pos_words = {'good', 'love', 'yes', 'great', 'happy', 'safe', 'hope'}
        neg_words = {'bad', 'no', 'hate', 'die', 'kill', 'fear', 'pain'}
        
        for char, texts in char_text.items():
            if not texts: continue
            full_text = " ".join(texts).lower()
            words = full_text.split()
            if not words: continue
            
            confidence = 'high' if len(texts) >= 10 else ('medium' if len(texts) >= 5 else 'low')
            
            avg_len = sum(len(t.split()) for t in texts) / len(texts)
            unique_ratio = len(set(words)) / len(words) if len(words) > 0 else 0
            complexity = (min(1.0, avg_len/20.0) + min(1.0, unique_ratio/0.6)) / 2
            
            pos = sum(1 for w in words if w in pos_words)
            neg = sum(1 for w in words if w in neg_words)
            total_aff = pos + neg
            positivity = (pos - neg) / total_aff if total_aff > 0 else 0.0
            
            active = sum(1 for w in words if w in active_verbs)
            passive = sum(1 for w in words if w in passive_markers)
            total_verbs = active + passive
            agency = (active - passive) / max(1, total_verbs)
            
            punct_count = sum(1 for c in full_text if c in '!?...,;:')
            punct_rate = round(punct_count / max(1, len(words)), 3)
            
            fingerprints[char] = {
                'complexity': round(complexity, 2),
                'positivity': round(positivity, 2),
                'agency': round(agency, 2),
                'line_count': len(texts),
                'fingerprint_confidence': confidence,
                'punctuation_rate': punct_rate
            }
        return fingerprints


# =============================================================================
# VALENCE LOGIC (formerly valence.py)
# =============================================================================

class ValenceAgent:
    """ScriptPulse Valence Agent - Emotional Polarity"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        scores = []
        positive_words = {'love', 'good', 'great', 'happy', 'joy', 'smile', 'laugh', 'light', 'sun', 'win', 'success', 'safe', 'calm', 'peace', 'hope', 'kiss', 'hug', 'beautiful', 'bright', 'yes', 'victory', 'friend', 'warm', 'soft', 'sweet', 'free', 'glory', 'alive', 'proud', 'brave', 'trust', 'rich', 'fun', 'party', 'dance', 'music', 'sing', 'heal'}
        negative_words = {'bad', 'dark', 'dead', 'death', 'kill', 'gun', 'blood', 'pain', 'hurt', 'cry', 'scream', 'fear', 'afraid', 'run', 'break', 'shatter', 'crash', 'fight', 'hate', 'enemy', 'trap', 'lose', 'fail', 'cold', 'sick', 'ill', 'sad', 'empty', 'alone', 'lost', 'danger', 'risk', 'hell', 'murder', 'corpse', 'evil', 'cruel', 'ugly', 'no', 'stop', 'lie', 'betray', 'monster', 'ghost', 'shadow'}
        
        for scene in scenes:
            text = " ".join([l['text'] for l in scene['lines']]).lower()
            words = text.replace('.', '').replace(',', '').split()
            if not words:
                scores.append(0.0)
                continue
            pos_hits = sum(1 for w in words if w in positive_words)
            neg_hits = sum(1 for w in words if w in negative_words)
            total_hits = pos_hits + neg_hits
            
            if total_hits == 0:
                scores.append(0.0)
                continue
            
            raw_valence = (pos_hits - neg_hits) / total_hits
            density = total_hits / len(words)
            confidence = min(1.0, density / 0.05)
            final_valence = raw_valence * confidence
            scores.append(round(final_valence, 3))
        return scores


# =============================================================================
# SEMANTIC & EMBEDDINGS LOGIC (formerly semantic.py & embeddings.py)
# =============================================================================

class SemanticAgent:
    """ScriptPulse Semantic Agent & Hybrid NLP Agent - Semantic Flux/Entropy"""
    
    def __init__(self):
        self.model = global_manager.get_sentence_transformer("sentence-transformers/all-MiniLM-L6-v2")
        if self.model:
            print("[ML] Loaded SBERT for Semantic Analysis.")
        else:
            print("[Warning] Semantic ML failed to load. Using Entropy Fallback.")

    def run(self, data):
        """Calculate Semantic Entropy/Flux (merged logic from semantic.py and embeddings.py)"""
        scenes = data.get('scenes', [])
        if not scenes: return []
        
        scores = []
        scene_texts = [" ".join([l['text'] for l in s['lines']]) for s in scenes]
        
        if self.model:
            # SBERT Logic (from both sources, unified)
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                embeddings = self.model.encode(scene_texts)
                for i in range(len(embeddings)):
                    if i == 0:
                        scores.append(0.1)
                        continue
                    curr = embeddings[i].reshape(1, -1)
                    prev = embeddings[i-1].reshape(1, -1)
                    sim = cosine_similarity(curr, prev)[0][0]
                    entropy = 1.0 - max(0.0, sim)
                    scores.append(float(entropy))
            except ImportError:
                 # Fallback to pure pytorch cosine sim if sklearn missing (from embeddings.py)
                 from sentence_transformers import util
                 embeddings = self.model.encode(scene_texts, convert_to_tensor=True)
                 scores.append(0.1) # First scene
                 for i in range(1, len(embeddings)):
                      sim = util.pytorch_cos_sim(embeddings[i], embeddings[i-1]).item()
                      entropy = 1.0 - max(0.0, sim)
                      scores.append(float(entropy))

        else:
            # Fallback (Jaccard + Entropy)
            for text in scene_texts:
                tokens = text.split()
                if not tokens:
                    scores.append(0.0)
                    continue
                counts = Counter(tokens)
                entropy = 0.0
                total = len(tokens)
                for count in counts.values():
                    p = count / total
                    entropy -= p * math.log(p, 2)
                scores.append(min(1.0, entropy / 6.0))
        
        return scores


# =============================================================================
# COHERENCE LOGIC (formerly coherence.py)
# =============================================================================

class CoherenceAgent:
    """ScriptPulse Coherence Agent - Switching Costs"""
    
    def run(self, data):
        scenes = data.get('scenes', [])
        scores = []
        if not scenes: return []
        scores.append(0.0)
        
        for i in range(1, len(scenes)):
            prev = scenes[i-1]
            curr = scenes[i]
            penalty = 0.0
            
            if self.get_loc(prev['heading']) != self.get_loc(curr['heading']):
                penalty += 0.4
            
            p_time = self.get_time(prev['heading'])
            c_time = self.get_time(curr['heading'])
            if p_time and c_time and p_time != c_time:
                penalty += 0.2
            
            prev_chars = self.get_chars(prev)
            curr_chars = self.get_chars(curr)
            if prev_chars and curr_chars:
                intersection = prev_chars.intersection(curr_chars)
                union = prev_chars.union(curr_chars)
                jaccard = len(intersection) / len(union)
                penalty += (1.0 - jaccard) * 0.4
            
            scores.append(round(min(1.0, penalty), 3))
        return scores

    def get_loc(self, heading):
        parts = heading.upper().replace('INT.', '').replace('EXT.', '').split('-')[0]
        return parts.strip()

    def get_time(self, heading):
        h = heading.upper()
        if 'DAY' in h: return 'DAY'
        if 'NIGHT' in h: return 'NIGHT'
        return None

    def get_chars(self, scene):
        chars = set()
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name: chars.add(name)
        return chars
