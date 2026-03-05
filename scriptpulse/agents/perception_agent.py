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
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    vader_analyzer = SentimentIntensityAnalyzer()
except:
    vader_analyzer = None

class EncodingAgent:
    """Consolidated Encoding Agent - High Performance, Low Complexity"""
    
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
                # Supporting metrics for UI consistency
                'character_scene_vectors': metadata['arcs'],
                'stakes_taxonomy': metadata['stakes'],
                'scene_purpose': metadata['purpose'],
                'payoff_density': metadata['payoff'],
                'on_the_nose': metadata['on_the_nose'],
                'shoe_leather': metadata['shoe_leather'],
                'tell_vs_show': metadata['tell_vs_show'],
                'is_exposition': metadata['purpose']['purpose'] == 'Exposition',
                'scene_vocabulary': metadata['scene_vocabulary']
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
            'idea_density': round(uniq / max(1, len(words)), 2),
            'clarity_score': 0.8 # Placeholder
        }

    def _extract_dialogue(self, lines):
        d_lines = [l for l in lines if l['tag'] == 'D']
        c_lines = [l for l in lines if l['tag'] == 'C']
        
        switches = 0
        for i in range(1, len(c_lines)):
            if c_lines[i]['text'] != c_lines[i-1]['text']: switches += 1
            
        return {
            'dialogue_line_count': len(d_lines),
            'turn_velocity': round(len(d_lines) / max(1, len(lines)), 3),
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
                
        return {
            'action_lines': len(a_lines),
            'visual_intensity': round(len(a_lines) / max(1, len(lines)), 3),
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
        if not vader_analyzer:
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}
            
        text = " ".join([l['text'] for l in lines])
        if not text.strip():
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}
            
        scores = vader_analyzer.polarity_scores(text)
        return {
            'pos': round(scores['pos'], 3),
            'neg': round(scores['neg'], 3),
            'neu': round(scores['neu'], 3),
            'compound': round(scores['compound'], 3)
        }

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

    def _extract_narrative_metadata(self, lines):
        text = " ".join([l['text'] for l in lines]).lower()
        
        # Vocab definition
        vocab = set(re.findall(r'\b\w+\b', text))
        
        # Simplified Stakes Detection
        stakes_map = {
            'Physical': ['kill', 'blood', 'gun', 'fight', 'run', 'dead'],
            'Emotional': ['love', 'cry', 'heart', 'fear', 'happy', 'sad'],
            'Social': ['reputation', 'friend', 'betray', 'secret', 'status'],
            'Moral': ['right', 'wrong', 'lie', 'truth', 'guilt'],
            'Existential': ['meaning', 'exist', 'god', 'death', 'soul']
        }
        scores = {k: sum(text.count(w) for w in v) for k, v in stakes_map.items()}
        dominant = max(scores, key=scores.get) if any(scores.values()) else 'None'
        
        # Character Arcs (Per-scene vectors)
        arcs = {}
        curr = None
        for l in lines:
            if l['tag'] == 'C': curr = l['text'].strip()
            elif l['tag'] == 'D' and curr:
                if curr not in arcs: arcs[curr] = {'sentiment': 0.0, 'agency': 0.0, 'line_count': 0}
                arcs[curr]['line_count'] += 1
                dial_text = l['text'].lower()
                
                # Simple sentiment/agency heuristics
                pos = sum(dial_text.count(w) for w in ['good', 'love', 'happy', 'yes', 'win'])
                neg = sum(dial_text.count(w) for w in ['bad', 'hate', 'sad', 'no', 'lose', 'die'])
                arcs[curr]['sentiment'] += (pos - neg) * 0.1
                
                act = sum(dial_text.count(w) for w in ['i', 'must', 'will', 'do', 'go', 'stop', 'make'])
                passv = sum(dial_text.count(w) for w in ['me', 'us', 'happened', 'was'])
                arcs[curr]['agency'] += (act - passv) * 0.1
        
        return {
            'stakes': {'dominant': dominant, 'breakdown': {k: round(v/max(1, sum(scores.values())), 2) for k,v in scores.items()}},
            'purpose': {'purpose': 'Revelation' if 'reveal' in text or 'found' in text else 'Transition'},
            'payoff': {'payoff_density': round(sum(scores.values()) / max(1, len(lines)), 2)},
            'on_the_nose': {'on_the_nose_ratio': 0.1 if 'i feel' in text else 0.0},
            'shoe_leather': {'has_shoe_leather': 'hello' in text or 'how are you' in text},
            'tell_vs_show': {'tell_ratio': 0.2 if 'was angry' in text else 0.0},
            'arcs': arcs,
            'scene_vocabulary': list(vocab)
        }
