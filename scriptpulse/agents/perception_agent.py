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
        ablation_config = input_data.get('ablation_config', {})
        self._force_fallback = not ablation_config.get('use_gpt2', True)
        
        if not scenes: return []
        
        feature_vectors = []
        prev_characters = set() # Track for Entity Churn
        
        for i, scene in enumerate(scenes):
            if 'lines' in scene:
                scene_lines = scene['lines']
            else:
                scene_lines = self.get_scene_lines(scene, lines)
            
            # Extract Ref Load with Context
            ref_load = self.extract_referential_load(scene_lines, prev_characters)
            
            # Update context for next iteration
            # We assume active characters in this scene become the "prev" for the next
            # But strictly speaking, churn is about who entered vs left comparing sets.
            current_chars = ref_load.get('current_character_set', set())
            prev_characters = current_chars
            
            # Remove the set from output to keep JSON clean if needed, 
            # but usually it's fine. We'll strip it if strictly numbers required.
            if 'current_character_set' in ref_load:
                del ref_load['current_character_set']

            features = {
                'scene_index': scene['scene_index'],
                'linguistic_load': self.extract_linguistic_load(scene_lines),
                'dialogue_dynamics': self.extract_dialogue_dynamics(scene_lines),
                'visual_abstraction': self.extract_visual_abstraction(scene_lines),
                'referential_load': ref_load,
                'structural_change': self.extract_structural_change(scene, scenes, i),
                'ambient_signals': self.extract_ambient_signals(scene_lines),
                'micro_structure': self.extract_micro_structure(scene_lines),
                'entropy_score': self.extract_information_entropy(scene_lines),
                'motifs': self.extract_motifs(scene_lines, ref_load.get('current_character_set', set())),
                'tell_vs_show': self.extract_tell_vs_show(scene_lines),
                # Phase 23
                'on_the_nose': self.extract_on_the_nose(scene_lines),
                'shoe_leather': self.extract_shoe_leather(scene_lines),
                'semantic_motifs': self.extract_semantic_motifs(scene_lines),
                'character_scene_vectors': self.extract_character_scene_vectors(scene_lines),
                # Phase 24
                'stakes_taxonomy': self.extract_stakes_taxonomy(scene_lines),
                'stichomythia': self.extract_stichomythia(scene_lines),
                'scene_purpose': self.extract_scene_purpose(scene_lines),
                'payoff_density': self.extract_payoff_density(scene_lines),
                # Phase 25
                'opening_hook': self.extract_opening_hook(scene_lines, i),
                'generic_dialogue': self.extract_generic_dialogue(scene_lines),
                'scene_turn': self.extract_scene_turn(scene_lines),
                'dialogue_action_ratio': self.extract_dialogue_action_ratio(scene_lines),
                # Phase 26
                'passive_voice': self.extract_passive_voice(scene_lines),
                'scene_vocabulary': self.extract_scene_vocabulary(scene_lines),
                # Phase 27
                'interruption_patterns': self.extract_interruption_patterns(scene_lines),
                'location_data': self.extract_location_data(scene),
                'runtime_contribution': self.extract_runtime_contribution(scene_lines),
                # Phase 28
                'monologue_data': self.extract_monologue_detection(scene_lines),
                'scene_economy': self.extract_scene_economy(scene_lines),
                # Phase 29
                'thematic_clusters': self.extract_thematic_clusters(scene_lines),
                'nonlinear_tag': self.extract_nonlinear_tag(scene),
                'reader_frustration': self.extract_reader_frustration(scene_lines),
                # Phase 30
                'format_compliance': self.extract_format_compliance(scene, scene_lines),
                'deus_ex_signals': self.extract_deus_ex_signals(scene_lines, i),
                # Research-Grade: Information-Theoretic Surprisal
                'surprisal': self.extract_surprisal(scene_lines)
            }
            feature_vectors.append(features)
        return feature_vectors

    def get_scene_lines(self, scene, all_lines):
        start = scene['start_line']
        end = scene['end_line']
        return [line for line in all_lines if start <= line['line_index'] <= end]

    def _count_syllables(self, word):
        word = word.lower()
        if len(word) <= 3: return 1
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels: count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                count += 1
        if word.endswith("e"): count -= 1
        if count == 0: count += 1
        return count

    def extract_linguistic_load(self, scene_lines):
        all_text = ' '.join([line['text'] for line in scene_lines if line['text'].strip()])
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {'sentence_count': 0, 'mean_sentence_length': 0.0, 'max_sentence_length': 0, 
                    'sentence_length_variance': 0.0, 'readability_grade': 0.0, 'idea_density': 0.0}
        
        word_list = all_text.split()
        total_words = len(word_list)
        total_sentences = len(sentences)
        
        # Word stats
        word_counts = [len(s.split()) for s in sentences]
        mean_length = sum(word_counts) / len(word_counts)
        max_length = max(word_counts)
        variance = sum((x - mean_length) ** 2 for x in word_counts) / len(word_counts)
        
        # 1. READABILITY (Flesch-Kincaid Grade Level)
        # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        total_syllables = sum(self._count_syllables(w) for w in word_list)
        avg_syllables_per_word = total_syllables / total_words if total_words > 0 else 0
        avg_words_per_sentence = total_words / total_sentences if total_sentences > 0 else 0
        
        fk_grade = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
        fk_grade = max(0.0, round(fk_grade, 2))
        
        # 2. IDEA DENSITY (Propositional Density Approximation)
        # Using Unique Words (Types) + Prepositions as proxy for propositions
        prepositions = {'in', 'on', 'at', 'by', 'with', 'from', 'to', 'for', 'of', 'about', 'under', 'over'}
        prep_count = sum(1 for w in word_list if w.lower() in prepositions)
        unique_words = len(set(w.lower() for w in word_list))
        
        # Idea Density ~ (Unique Words + Prepositions) / Total Words
        idea_density = (unique_words + prep_count) / total_words if total_words > 0 else 0.0
        
        return {
            'sentence_count': len(sentences),
            'mean_sentence_length': round(mean_length, 2),
            'max_sentence_length': max_length,
            'sentence_length_variance': round(variance, 2),
            'readability_grade': fk_grade,
            'idea_density': round(idea_density, 3),
            'clarity_score': round(max(0.0, 1.0 - (fk_grade / 12.0)), 2), # Clamped to [0,1]. Grade > 12 yields 0.
            'novelty_score': round(idea_density * (variance / 10.0), 2) # Heuristic: New ideas + Variety = Novelty
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
            'dialogue_line_count': dialogue_count, # Alias for consistency
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

    def extract_referential_load(self, scene_lines, prev_characters=None):
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
        
        # 1. ENTITY CHURN
        # Churn = (Added + Removed) / Total Active (averaged or max)
        churn = 0.0
        if prev_characters is not None:
             added = len(unique_characters - prev_characters)
             removed = len(prev_characters - unique_characters)
             total_pool = len(unique_characters.union(prev_characters))
             if total_pool > 0:
                 churn = (added + removed) / total_pool
        
        # 2. UNRESOLVED REFERENCES (Ghost Mentions)
        # Names mentioned in dialogue/action but not present as Speakers (Tags)
        # Heuristic: Check for capitalized words in Action that match known characters? 
        # Or just look for any capitalized names not in unique_characters.
        # Simplified: Count capitalized words that look like names.
        text_blobs = [l['text'] for l in scene_lines if l['tag'] in ('A', 'D')]
        full_text = ' '.join(text_blobs)
        # Regex for Capitalized words not at start of sentence (rough proxy)
        # This is noisy without NER, so we use a simpler proxy:
        # Check against a known "All Characters" list if available, or just self-reference.
        # We will count how many times CURRENT characters are mentioned in ACTION (tracking)
        # vs how many "unknown" capitalized entities appear.
        
        # For now, let's track "Non-Speaking Presence"
        # i.e. Characters mentioned in Action but didn't speak.
        ghost_mentions = 0
        potential_names = re.findall(r'\b[A-Z][A-Z]+\b', full_text) # Uppercase formatting common in scripts
        for name in potential_names:
            if name not in unique_characters and len(name) > 2:
                ghost_mentions += 1
        
        return {
            'active_character_count': character_count, 
            'character_reintroductions': reintroductions,
            'entity_churn': round(churn, 2),
            'unresolved_references': ghost_mentions,
            'current_character_set': unique_characters # Internal use
        }

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

    def extract_motifs(self, scene_lines, active_characters):
        """Identifies potential motifs: Capitalized words in action lines that are not characters."""
        motifs = []
        action_text = ' '.join([l['text'] for l in scene_lines if l['tag'] == 'A'])
        
        # Find all fully capitalized words of length > 2
        potential_motifs = re.findall(r'\b[A-Z]{3,}\b', action_text)
        
        # Filter out character names and standard screenplay transitions (INT, EXT, DAY, NIGHT)
        ignore_list = {'INT', 'EXT', 'DAY', 'NIGHT', 'CONTINUOUS', 'CUT', 'FADE', 'DISSOLVE', 'SMASH', 'POV'}
        ignore_list.update(c.upper() for c in active_characters)
        
        for m in potential_motifs:
            if m not in ignore_list:
                motifs.append(m)
                
        return motifs

    def extract_tell_vs_show(self, scene_lines):
        """Scans Action lines for literal emotion words vs kinetic action verbs."""
        action_text = ' '.join([l['text'] for l in scene_lines if l['tag'] == 'A']).lower()
        words = re.findall(r'\b\w+\b', action_text)
        
        literal_emotion_words = {'sad', 'angry', 'happy', 'devastated', 'furious', 'depressed', 'joyful', 'scared', 'terrified', 'crying', 'weeping', 'mad', 'upset', 'glad', 'thrilled', 'shocked', 'surprised'}
        kinetic_action_verbs = {'run', 'jump', 'grab', 'throw', 'hit', 'punch', 'kick', 'sprint', 'crawl', 'slide', 'smash', 'break', 'shatter', 'slam', 'pull', 'push', 'drag', 'drop', 'fall'}
        
        emotion_count = sum(1 for w in words if w in literal_emotion_words)
        action_count = sum(1 for w in words if w in kinetic_action_verbs)
        
        # Calculate ratio: Higher means more telling than showing
        total = emotion_count + action_count
        ratio = emotion_count / total if total > 0 else 0.0
        
        return {
            'literal_emotions': emotion_count,
            'kinetic_actions': action_count,
            'tell_ratio': round(ratio, 3)
        }

    # =========================================================================
    # PHASE 23: MASTERCLASS EXTRACTIONS
    # =========================================================================

    def extract_on_the_nose(self, scene_lines):
        """
        Detect literal dialogue — characters saying exactly what they feel/intend.
        On-the-nose markers: 'I feel', 'I am [emotion]', 'I want', 'You are [emotion]', etc.
        Returns a ratio: higher = more literal / on-the-nose.
        """
        on_the_nose_patterns = [
            r"\bi feel\b", r"\bi am angry\b", r"\bi am sad\b", r"\bi am scared\b",
            r"\bi hate you\b", r"\bi love you\b", r"\bi trust you\b", r"\bi don'?t trust\b",
            r"\bi want to\b", r"\bi need to\b", r"\byou are\b", r"\bwe should\b",
            r"\bi am afraid\b", r"\bi am worried\b", r"\bi am sorry\b",
            r"\bthis is because\b", r"\bthe reason is\b", r"\bwhat i mean is\b",
        ]
        import re as _re
        dialogue_lines = [l for l in scene_lines if l.get('tag') == 'D']
        if not dialogue_lines:
            return {'on_the_nose_hits': 0, 'on_the_nose_ratio': 0.0}

        total_dialogue_words = 0
        hit_count = 0
        for line in dialogue_lines:
            text = line['text'].lower()
            total_dialogue_words += len(text.split())
            for pat in on_the_nose_patterns:
                if _re.search(pat, text):
                    hit_count += 1
                    break  # count each line at most once

        ratio = hit_count / len(dialogue_lines) if dialogue_lines else 0.0
        return {
            'on_the_nose_hits': hit_count,
            'on_the_nose_ratio': round(ratio, 3)
        }

    def extract_shoe_leather(self, scene_lines):
        """
        Detect 'shoe-leather' — meaningless filler at the start or end of a scene.
        Checks first 3 and last 3 dialogue lines for common social filler words.
        """
        filler_words = {
            'hello', 'hi', 'hey', 'bye', 'goodbye', 'goodbye', 'okay', 'ok',
            'sure', 'right', 'alright', 'thanks', 'thank', 'you', 'see ya',
            'later', 'come in', 'have a seat', 'how are you', 'how have you',
            "i'm fine", 'fine', 'good', 'great', 'nice to', 'pleasure', 'welcome'
        }
        dialogue_lines = [l for l in scene_lines if l.get('tag') == 'D']
        if len(dialogue_lines) < 4:
            return {'has_shoe_leather': False, 'scene_start_filler': 0, 'scene_end_filler': 0}

        def filler_score(lines):
            count = 0
            for l in lines:
                words = set(l['text'].lower().split())
                if len(words) <= 6 and words.intersection(filler_words):
                    count += 1
            return count

        start_filler = filler_score(dialogue_lines[:3])
        end_filler = filler_score(dialogue_lines[-3:])

        return {
            'has_shoe_leather': (start_filler >= 2 or end_filler >= 2),
            'scene_start_filler': start_filler,
            'scene_end_filler': end_filler
        }

    def extract_semantic_motifs(self, scene_lines):
        """
        Semantic motif extraction using term frequency on NOUNS in action lines.
        Identifies specific content nouns (not stop words) that may recur across the script.
        Returns a list of candidate motif terms.
        """
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'on',
            'at', 'by', 'for', 'with', 'from', 'as', 'it', 'he', 'she', 'they',
            'we', 'his', 'her', 'their', 'its', 'this', 'that', 'these', 'those',
            'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either',
            'into', 'through', 'over', 'under', 'then', 'than', 'up', 'out',
            'back', 'also', 'just', 'very', 'more', 'now', 'still', 'only',
            'each', 'both', 'few', 'after', 'before', 'same', 'where', 'when',
            'there', 'here', 'around', 'between', 'down', 'off', 'about'
        }
        action_text = ' '.join([l['text'] for l in scene_lines if l.get('tag') == 'A']).lower()
        words = re.findall(r'\b[a-z]{4,}\b', action_text)
        candidates = [w for w in words if w not in stop_words]

        # Return top 5 most-frequent content words as potential motifs
        freq = Counter(candidates)
        top_terms = [term for term, _ in freq.most_common(5) if freq[term] >= 2]
        return top_terms

    def extract_character_scene_vectors(self, scene_lines):
        """
        Per-scene character sentiment and agency snapshot.
        Returns a dict: {char_name: {sentiment: float, agency: float, line_count: int}}
        Used by WriterAgent to build Character Arc Vectors across the script.
        """
        positive_words = {'love', 'good', 'yes', 'hope', 'win', 'safe', 'trust', 'happy', 'joy', 'peace', 'proud', 'brave'}
        negative_words = {'hate', 'no', 'kill', 'fear', 'die', 'pain', 'lose', 'danger', 'dark', 'dead', 'sick', 'evil'}
        active_verbs = {'decide', 'choose', 'act', 'fight', 'lead', 'demand', 'force', 'grab', 'move', 'stop', 'make'}
        passive_markers = {'was', 'were', 'is', 'are', 'been', 'had', 'by', 'done'}

        vectors = {}
        current_char = None
        for line in scene_lines:
            tag = line.get('tag', '')
            if tag == 'C':
                current_char = line['text'].split('(')[0].strip()
                if current_char not in vectors:
                    vectors[current_char] = {'pos': 0, 'neg': 0, 'active': 0, 'passive': 0, 'line_count': 0}
            elif tag == 'D' and current_char:
                words = line['text'].lower().split()
                vectors[current_char]['pos'] += sum(1 for w in words if w in positive_words)
                vectors[current_char]['neg'] += sum(1 for w in words if w in negative_words)
                vectors[current_char]['active'] += sum(1 for w in words if w in active_verbs)
                vectors[current_char]['passive'] += sum(1 for w in words if w in passive_markers)
                vectors[current_char]['line_count'] += 1

        # Normalize to sentiment/agency
        result = {}
        for char, v in vectors.items():
            if v['line_count'] == 0:
                continue
            total_aff = v['pos'] + v['neg']
            sentiment = (v['pos'] - v['neg']) / total_aff if total_aff > 0 else 0.0
            total_verb = v['active'] + v['passive']
            agency = (v['active'] - v['passive']) / total_verb if total_verb > 0 else 0.0
            result[char] = {
                'sentiment': round(sentiment, 3),
                'agency': round(agency, 3),
                'line_count': v['line_count']
            }
        return result

    # =========================================================================
    # PHASE 24: NARRATIVE INTELLIGENCE EXTRACTIONS
    # =========================================================================

    def extract_stakes_taxonomy(self, scene_lines):
        """
        Classify what *type* of stakes are present in this scene.
        Categories: Physical, Emotional, Social, Moral, Existential
        Returns the dominant stakes type and a confidence breakdown.
        """
        all_text = ' '.join([l['text'] for l in scene_lines]).lower()
        words = set(all_text.split())

        physical   = {'kill', 'shot', 'fight', 'die', 'dead', 'survive', 'escape', 'run', 'gun', 'knife', 'wound', 'blood', 'attack', 'chase', 'crash', 'bomb', 'fire', 'fall'}
        emotional  = {'love', 'heart', 'cry', 'fear', 'lonely', 'hope', 'grief', 'loss', 'broken', 'forgive', 'trust', 'regret', 'miss', 'hurt', 'pain', 'shame', 'proud', 'feel'}
        social     = {'reputation', 'family', 'friend', 'betray', 'secret', 'respect', 'humiliate', 'judge', 'gossip', 'status', 'belong', 'accept', 'reject', 'community', 'class', 'honor'}
        moral      = {'right', 'wrong', 'lie', 'truth', 'justice', 'ethics', 'guilty', 'innocent', 'sacrifice', 'duty', 'betray', 'corrupt', 'witness', 'sin', 'redemption', 'moral'}
        existential= {'meaning', 'purpose', 'identity', 'believe', 'faith', 'soul', 'exist', 'void', 'god', 'destiny', 'legacy', 'memory', 'death', 'freedom', 'choice', 'reason', 'nothing'}

        scores = {
            'Physical':   len(words & physical),
            'Emotional':  len(words & emotional),
            'Social':     len(words & social),
            'Moral':      len(words & moral),
            'Existential':len(words & existential)
        }
        total = sum(scores.values())
        if total == 0:
            return {'dominant': 'None', 'breakdown': scores}

        dominant = max(scores, key=scores.get)
        breakdown = {k: round(v / total, 3) for k, v in scores.items()}
        return {'dominant': dominant, 'breakdown': breakdown}

    def extract_stichomythia(self, scene_lines):
        """
        Detect rapid-fire back-and-forth dialogue (stichomythia).
        Flags a scene where 4+ consecutive exchanges are ≤5 words each.
        """
        dialogue_lines = [l for l in scene_lines if l.get('tag') == 'D']
        if len(dialogue_lines) < 4:
            return {'has_stichomythia': False, 'rapid_exchange_count': 0}

        max_run = 0
        current_run = 0
        for line in dialogue_lines:
            words = len(line['text'].split())
            if words <= 6:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0

        return {
            'has_stichomythia': max_run >= 4,
            'rapid_exchange_count': max_run
        }

    def extract_scene_purpose(self, scene_lines):
        """
        Classify the primary narrative purpose of a scene.
        Types: Establishment, Complication, Revelation, Decision, Transition, Confrontation
        Uses keyword heuristics on dialogue and action lines.
        """
        all_text = ' '.join([l['text'] for l in scene_lines]).lower()
        words = all_text.split()
        word_set = set(words)

        establishment  = {'introduce', 'this', 'meet', 'first', 'new', 'welcome', 'name', 'here', 'called', 'known'}
        complication   = {'but', 'however', 'problem', 'wrong', 'worse', 'fail', 'unless', 'until', 'except', 'trouble', 'broken', 'stuck'}
        revelation     = {'realize', 'discover', 'learn', 'know', 'truth', 'secret', 'found', 'reveal', 'finally', 'actually', 'confession', 'exposed', 'hidden'}
        decision       = {'decide', 'choose', 'must', 'will', 'going', 'plan', 'never', 'always', 'promise', 'vow', 'refuse', 'accept', 'okay', 'done'}
        confrontation  = {'stop', 'enough', 'argue', 'fight', 'demand', 'face', 'confront', 'accuse', 'blame', 'why', 'how dare', 'liar', 'admit', 'challenge'}
        transition     = {'later', 'meanwhile', 'outside', 'inside', 'next', 'then', 'walk', 'drive', 'moving', 'arrive', 'leave', 'exit'}

        scores = {
            'Establishment': len(word_set & establishment),
            'Complication':  len(word_set & complication),
            'Revelation':    len(word_set & revelation),
            'Decision':      len(word_set & decision),
            'Confrontation': len(word_set & confrontation),
            'Transition':    len(word_set & transition)
        }

        dominant = max(scores, key=scores.get) if max(scores.values()) > 0 else 'Transition'
        return {'purpose': dominant, 'scores': scores}

    def extract_payoff_density(self, scene_lines):
        """
        Ratio of emotionally charged / high-stakes moments to total lines.
        High-payoff lines = contain valence words (pos/neg) or action verbs.
        High score + short scene = "Powerful Compression"
        Low score + long scene = "Diluted Impact"
        """
        high_impact_words = {
            'love', 'hate', 'kill', 'die', 'blood', 'cry', 'scream', 'gun',
            'truth', 'secret', 'fight', 'fire', 'run', 'never', 'always',
            'betray', 'promise', 'sorry', 'please', 'stop', 'gone', 'lost',
            'dead', 'alive', 'hope', 'fear', 'win', 'lose', 'stay', 'leave'
        }
        total_lines = max(1, len(scene_lines))
        high_impact_count = 0

        for line in scene_lines:
            words = set(line['text'].lower().split())
            if words & high_impact_words:
                high_impact_count += 1

        density = high_impact_count / total_lines

        if density > 0.6 and total_lines <= 15:
            label = "Powerful Compression"
        elif density < 0.2 and total_lines > 20:
            label = "Diluted Impact"
        elif density > 0.5:
            label = "High Intensity"
        else:
            label = "Balanced"

        return {
            'payoff_density': round(density, 3),
            'label': label,
            'total_lines': total_lines,
            'high_impact_lines': high_impact_count
        }

    # =========================================================================
    # PHASE 25: SCENE-LEVEL MICRO-DRAMA EXTRACTIONS
    # =========================================================================

    def extract_opening_hook(self, scene_lines, scene_index):
        """
        Evaluate the quality of the opening hook for the first scene.
        For non-opening scenes, returns None.
        Measures: how quickly conflict/question keywords appear.
        """
        if scene_index != 0:
            return None

        conflict_words = {
            'dead', 'kill', 'gun', 'fight', 'run', 'scream', 'blood', 'crash',
            'wrong', 'lost', 'can\'t', 'never', 'secret', 'stop', 'help', 'please',
            'explode', 'fire', 'shot', 'danger', 'crisis', 'shock', 'wake', 'alone'
        }
        question_words = {'who', 'why', 'where', 'what', 'when', 'how'}

        all_lines = scene_lines
        total = max(1, len(all_lines))

        # Find first-conflict index
        first_conflict_at = None
        for idx, line in enumerate(all_lines):
            words = set(line['text'].lower().split())
            if words & conflict_words or words & question_words:
                first_conflict_at = idx
                break

        pct_into_scene = (first_conflict_at / total) if first_conflict_at is not None else 1.0

        # Score: lower percentage = hook arrives sooner = better
        if first_conflict_at is None:
            hook_label = "No Hook Detected"
            hook_score = 0.0
        elif pct_into_scene <= 0.15:
            hook_label = "Strong Hook"
            hook_score = 1.0
        elif pct_into_scene <= 0.35:
            hook_label = "Moderate Hook"
            hook_score = 0.6
        else:
            hook_label = "Weak Hook"
            hook_score = 0.2

        return {
            'hook_label': hook_label,
            'hook_score': round(hook_score, 2),
            'first_conflict_line': first_conflict_at,
            'lines_before_conflict': first_conflict_at if first_conflict_at is not None else total
        }

    def extract_generic_dialogue(self, scene_lines):
        """
        Detect cinematic clichés and interchangeable lines that could appear in any script.
        Returns a count and ratio of cliché lines.
        """
        cliche_phrases = {
            "we need to talk", "i don't believe you", "you don't understand",
            "i can't do this anymore", "it's not what it looks like",
            "trust me", "i'm sorry", "we have to go", "be careful",
            "what are you doing here", "i love you too", "you have to believe me",
            "we don't have much time", "it's too late", "i had no choice",
            "this changes everything", "you're not alone", "i promise",
            "don't do this", "listen to me", "i need you", "please don't go",
            "everything's going to be okay", "what do you want from me",
            "stay with me", "i don't know what to say", "why are you doing this"
        }
        dialogue_lines = [l for l in scene_lines if l.get('tag') == 'D']
        if not dialogue_lines:
            return {'cliche_count': 0, 'cliche_ratio': 0.0, 'examples': []}

        hits = []
        for line in dialogue_lines:
            text = line['text'].lower().strip()
            for phrase in cliche_phrases:
                if phrase in text:
                    hits.append(text[:60])
                    break

        ratio = len(hits) / len(dialogue_lines)
        return {
            'cliche_count': len(hits),
            'cliche_ratio': round(ratio, 3),
            'examples': hits[:2]
        }

    def extract_scene_turn(self, scene_lines):
        """
        Compare sentiment/conflict signals at start vs end of scene.
        A "Turn" happens when the emotional ground shifts.
        Uses simple valence word counting on first 20% vs last 20%.
        """
        positive_words = {'good', 'yes', 'love', 'hope', 'happy', 'win', 'smile', 'safe', 'trust', 'okay', 'right', 'peace'}
        negative_words = {'bad', 'no', 'hate', 'fear', 'cry', 'lose', 'anger', 'danger', 'wrong', 'dead', 'pain', 'dark'}
        confrontation_words = {'fight', 'stop', 'never', 'refuse', 'demand', 'accuse', 'scream', 'hit', 'kill', 'attack'}

        total = max(1, len(scene_lines))
        split = max(1, total // 5)  # 20% boundary

        opening_lines = scene_lines[:split]
        closing_lines = scene_lines[-split:]

        def score_lines(lines):
            words = ' '.join(l['text'].lower() for l in lines).split()
            word_set = set(words)
            pos = len(word_set & positive_words)
            neg = len(word_set & negative_words)
            conf = len(word_set & confrontation_words)
            total_sig = pos + neg + 1
            return round((pos - neg) / total_sig, 3), round(conf / max(1, len(words)) * 10, 3)

        open_sentiment, open_conflict = score_lines(opening_lines)
        close_sentiment, close_conflict = score_lines(closing_lines)

        sentiment_delta = round(close_sentiment - open_sentiment, 3)
        conflict_delta = round(close_conflict - open_conflict, 3)

        if abs(sentiment_delta) < 0.1 and abs(conflict_delta) < 0.1:
            turn_label = "Flat Turn"
        elif sentiment_delta < -0.2 or conflict_delta > 0.2:
            turn_label = "Negative Turn"   # Things got worse — dramatic
        elif sentiment_delta > 0.2 or conflict_delta < -0.2:
            turn_label = "Positive Turn"   # Things got better — relief
        else:
            turn_label = "Subtle Turn"

        return {
            'turn_label': turn_label,
            'sentiment_delta': sentiment_delta,
            'conflict_delta': conflict_delta,
            'opening_sentiment': open_sentiment,
            'closing_sentiment': close_sentiment
        }

    def extract_dialogue_action_ratio(self, scene_lines):
        """
        Calculate raw Dialogue-to-Action line ratio for this scene.
        (Aggregated at script-level by WriterAgent)
        """
        dialogue_count = sum(1 for l in scene_lines if l.get('tag') == 'D')
        action_count = sum(1 for l in scene_lines if l.get('tag') == 'A')
        total = max(1, dialogue_count + action_count)
        return {
            'dialogue_lines': dialogue_count,
            'action_lines': action_count,
            'dialogue_ratio': round(dialogue_count / total, 3)
        }

    # =========================================================================
    # PHASE 26: MACRO-CONSISTENCY & CRAFT QUALITY EXTRACTIONS
    # =========================================================================

    def extract_passive_voice(self, scene_lines):
        """
        Detect passive voice constructions in action lines.
        Pattern: auxiliary verb (is/are/was/were/been) + past participle (-ed/-en words).
        Returns: count, ratio, and example offenders.
        """
        import re as _re
        # Match: is/are/was/were/been/being + [word ending in -ed or common irregular pp]
        passive_pattern = _re.compile(
            r'\b(is|are|was|were|been|being)\s+\w*(?:ed|en|own|oken|iven|aken|ung|ung|awn|ssen|ought)\b',
            _re.IGNORECASE
        )
        action_lines = [l for l in scene_lines if l.get('tag') == 'A']
        if not action_lines:
            return {'passive_count': 0, 'passive_ratio': 0.0, 'examples': []}

        hits = []
        for line in action_lines:
            text = line['text']
            matches = passive_pattern.findall(text)
            if matches:
                hits.append(text[:70].strip())

        ratio = len(hits) / len(action_lines)
        return {
            'passive_count': len(hits),
            'passive_ratio': round(ratio, 3),
            'examples': hits[:2]
        }

    def extract_scene_vocabulary(self, scene_lines):
        """
        Extract a compact set of the most distinctive content words in this scene.
        Used by WriterAgent for Redundant Scene Detection — two scenes with highly
        overlapping vocabulary are probably covering the same narrative ground.
        """
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'to', 'of', 'in', 'on', 'at', 'by', 'for',
            'with', 'from', 'as', 'it', 'he', 'she', 'they', 'we', 'his', 'her',
            'their', 'its', 'this', 'that', 'and', 'but', 'or', 'not', 'so', 'up',
            'out', 'back', 'now', 'then', 'just', 'also', 'very', 'i', 'you', 'my',
            'me', 'him', 'us', 'no', 'yes', 'here', 'there', 'what', 'how', 'all',
            'one', 'like', 'get', 'go', 'can', 'know', 'see', 'well', 'look',
            'come', 'even', 'still', 'too', 'into', 'over', 'new', 'way'
        }
        all_text = ' '.join(l['text'] for l in scene_lines).lower()
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        content_words = [w for w in words if w not in stop_words]
        freq = Counter(content_words)
        # Return the top 10 most-frequent distinctive words as a vocabulary signature
        return [w for w, _ in freq.most_common(10)]

    # =========================================================================
    # PHASE 27: PRODUCER'S VIEW EXTRACTIONS
    # =========================================================================

    def extract_interruption_patterns(self, scene_lines):
        """
        Detect dialogue interruptions — lines ending in '--' or '—'.
        Tracks which characters interrupt vs. which get interrupted.
        Returns: per-character interrupt/interrupted counts + total rate.
        """
        # Map each dialogue line to its speaker
        interruptions = {}  # char -> {'interrupts': int, 'interrupted': int}
        current_char = None
        prev_char = None

        for line in scene_lines:
            tag = line.get('tag', '')
            if tag == 'C':
                prev_char = current_char
                current_char = line['text'].split('(')[0].strip()
                if current_char not in interruptions:
                    interruptions[current_char] = {'interrupts': 0, 'interrupted': 0}
            elif tag == 'D' and current_char:
                text = line['text'].strip()
                if text.endswith('--') or text.endswith('—') or text.endswith('--"'):
                    # This speaker was interrupted
                    interruptions[current_char]['interrupted'] += 1
                    # The next speaker (prev_char for next round) is the interrupter
                    # We'll approximate: if prev_char exists and is different
                    if prev_char and prev_char != current_char:
                        interruptions[prev_char]['interrupts'] += 1

        total_interruptions = sum(v['interrupted'] for v in interruptions.values())
        dialogue_lines = sum(1 for l in scene_lines if l.get('tag') == 'D')
        interrupt_rate = round(total_interruptions / max(1, dialogue_lines), 3)

        return {
            'interrupt_rate': interrupt_rate,
            'total_interruptions': total_interruptions,
            'per_character': interruptions
        }

    def extract_location_data(self, scene):
        """
        Parse the scene header to extract INT/EXT and location name.
        Returns structured location data for variety analysis.
        """
        header = scene.get('header', '') or scene.get('slug', '') or scene.get('location', '')
        if not header:
            return {'interior': None, 'location': 'UNKNOWN', 'raw_header': ''}

        header_upper = header.upper().strip()
        interior = None
        if header_upper.startswith('INT'):
            interior = 'INT'
        elif header_upper.startswith('EXT'):
            interior = 'EXT'

        # Extract location name: between the first '.' and the next '-' or end of string
        # e.g. "INT. APARTMENT - DAY" → "APARTMENT"
        import re as _re
        loc_match = _re.search(r'(?:INT|EXT)\.\s*([^-\n]+)', header_upper)
        location = loc_match.group(1).strip() if loc_match else header_upper[:30]

        return {
            'interior': interior,
            'location': location,
            'raw_header': header[:60]
        }

    def extract_runtime_contribution(self, scene_lines):
        """
        Estimate the runtime contribution of this scene based on line counts.
        Industry rule of thumb:
          - 1 action line ≈ 1.5 seconds
          - 1 dialogue line ≈ 2.5 seconds
        Returns estimated seconds for this scene.
        """
        action_lines = sum(1 for l in scene_lines if l.get('tag') == 'A')
        dialogue_lines = sum(1 for l in scene_lines if l.get('tag') == 'D')
        estimated_seconds = (action_lines * 1.5) + (dialogue_lines * 2.5)
        return {
            'action_lines': action_lines,
            'dialogue_lines': dialogue_lines,
            'estimated_seconds': round(estimated_seconds, 1)
        }

    # =========================================================================
    # PHASE 28: SYNTHESIS & STRUCTURE EXTRACTIONS
    # =========================================================================

    def extract_monologue_detection(self, scene_lines):
        """
        Detect character monologues — 8+ consecutive dialogue lines from the same character
        with no response from another character.
        Returns a list of detected monologues with character and length.
        """
        monologues = []
        current_char = None
        run_start = 0
        run_length = 0

        for line in scene_lines:
            tag = line.get('tag', '')
            if tag == 'C':
                speaker = line['text'].split('(')[0].strip()
                if speaker != current_char:
                    if run_length >= 8 and current_char:
                        monologues.append({
                            'character': current_char,
                            'length': run_length,
                            'start_line': run_start
                        })
                    current_char = speaker
                    run_length = 0
                    run_start = line.get('line_num', 0)
            elif tag == 'D' and current_char:
                run_length += 1

        # Catch trailing monologue
        if run_length >= 8 and current_char:
            monologues.append({'character': current_char, 'length': run_length, 'start_line': run_start})

        return {
            'has_monologue': len(monologues) > 0,
            'monologues': monologues
        }

    def extract_scene_economy(self, scene_lines):
        """
        Score scene economy: how many distinct narrative elements does this scene introduce?
        Signals: new character names (C-tagged), conflict escalation words, revelation markers.
        Higher score = scene is doing more story work per line.
        """
        new_character_markers = sum(1 for l in scene_lines if l.get('tag') == 'C')

        revelation_words = {
            'realize', 'discover', 'reveal', 'confess', 'admit', 'find out',
            'knew', 'secret', 'truth', 'lie', 'never told', 'all along'
        }
        conflict_words = {
            'refuse', 'demand', 'threaten', 'attack', 'run', 'fight', 'kill',
            'escape', 'chase', 'betrayed', 'shot', 'dead', 'confronted'
        }
        decision_words = {
            "i've decided", "i'm going to", "i will", "make a choice", "no more",
            "i choose", "i'm done", "we have to", "there's only one way"
        }

        all_text = ' '.join(l['text'].lower() for l in scene_lines)

        revelation_hits = sum(1 for w in revelation_words if w in all_text)
        conflict_hits = sum(1 for w in conflict_words if w in all_text)
        decision_hits = sum(1 for w in decision_words if w in all_text)

        economy_score = new_character_markers + revelation_hits + conflict_hits + decision_hits

        if economy_score >= 5:
            economy_label = "High Economy"
        elif economy_score >= 2:
            economy_label = "Moderate Economy"
        else:
            economy_label = "Low Economy"

        return {
            'economy_score': economy_score,
            'economy_label': economy_label,
            'new_characters': new_character_markers,
            'revelation_hits': revelation_hits,
            'conflict_hits': conflict_hits,
            'decision_hits': decision_hits
        }

    # =========================================================================
    # PHASE 29: READER EXPERIENCE & THEMATIC DEPTH
    # =========================================================================

    def extract_thematic_clusters(self, scene_lines):
        """
        Identify thematic word clusters in a scene using predefined thematic families.
        Returns which thematic families appear most strongly in this scene.
        """
        thematic_families = {
            'freedom':      ['freedom', 'escape', 'prison', 'cage', 'trap', 'flee', 'liberate', 'captive', 'chain', 'release'],
            'identity':     ['who', 'identity', 'mask', 'pretend', 'lie', 'real', 'fake', 'become', 'belong', 'recognize'],
            'power':        ['power', 'control', 'dominate', 'weak', 'strong', 'leader', 'obey', 'command', 'authority', 'submit'],
            'love':         ['love', 'heart', 'together', 'apart', 'miss', 'desire', 'trust', 'devoted', 'adore', 'jealous'],
            'betrayal':     ['betray', 'lie', 'deceive', 'cheat', 'backstab', 'secret', 'truth', 'trust', 'reveal', 'double'],
            'redemption':   ['forgive', 'redeem', 'atone', 'sorry', 'guilt', 'punish', 'deserve', 'second chance', 'mistake', 'repair'],
            'survival':     ['survive', 'live', 'die', 'kill', 'dead', 'danger', 'safe', 'protect', 'threat', 'weapon'],
            'justice':      ['justice', 'right', 'wrong', 'fair', 'law', 'punishment', 'innocent', 'guilty', 'crime', 'moral'],
            'greed':        ['money', 'rich', 'wealth', 'steal', 'corrupt', 'bribe', 'greed', 'debt', 'profit', 'cost'],
            'loss':         ['lose', 'gone', 'grief', 'mourn', 'death', 'empty', 'broken', 'left', 'remember', 'past']
        }

        all_text = ' '.join(l['text'].lower() for l in scene_lines)
        words = set(all_text.split())

        scores = {}
        for theme, keywords in thematic_families.items():
            score = sum(1 for kw in keywords if kw in all_text)
            if score > 0:
                scores[theme] = score

        if not scores:
            return {'dominant_themes': [], 'theme_scores': {}}

        sorted_themes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {
            'dominant_themes': [t for t, _ in sorted_themes[:2]],
            'theme_scores': dict(sorted_themes[:5])
        }

    def extract_nonlinear_tag(self, scene):
        """
        Detect if this scene is non-linear (flashback, flash forward, dream, memory).
        Parses the scene header and first action line for these markers.
        """
        import re as _re
        nonlinear_markers = {
            'FLASHBACK': 'Flashback',
            'FLASH BACK': 'Flashback',
            'FLASH FORWARD': 'Flash Forward',
            'FLASH CUT': 'Flash Cut',
            'DREAM': 'Dream Sequence',
            'MEMORY': 'Memory',
            'EARLIER': 'Earlier (Non-linear)',
            'LATER': 'Later (Non-linear)',
            'FANTASY': 'Fantasy Sequence',
            'VISION': 'Vision'
        }

        header = (scene.get('header', '') or scene.get('slug', '') or '').upper()
        lines_text = ' '.join(l.get('text', '') for l in scene.get('lines', [])[:2]).upper()
        search_text = header + ' ' + lines_text

        detected = None
        for marker, label in nonlinear_markers.items():
            if marker in search_text:
                detected = label
                break

        return {
            'is_nonlinear': detected is not None,
            'type': detected
        }

    def extract_reader_frustration(self, scene_lines):
        """
        Detect the 3 biggest reader frustration triggers:
        1. Internal state verbs in action lines (unfilmable)
        2. Too many new characters in one scene (name flooding)
        3. Two characters with similar-sounding names introduced in same scene
        """
        import re as _re

        # 1. Internal state verbs in action lines
        internal_state_verbs = {
            'thinks', 'realizes', 'wonders', 'feels', 'remembers',
            'imagines', 'believes', 'fears', 'hopes', 'understands',
            'knows', 'decides internally', 'senses', 'considers',
            'reflects', 'recalls', 'suspects', 'wishes'
        }
        action_lines = [l for l in scene_lines if l.get('tag') == 'A']
        internal_state_hits = []
        for line in action_lines:
            words = set(line['text'].lower().split())
            matches = words & internal_state_verbs
            if matches:
                internal_state_hits.append(line['text'][:60].strip())

        # 2. Character name crowding — too many new C-tags in one scene
        char_names = [l['text'].split('(')[0].strip()
                      for l in scene_lines if l.get('tag') == 'C']
        unique_chars = list(dict.fromkeys(char_names))  # preserve order, deduplicate
        name_crowding = len(unique_chars) >= 4

        # 3. Similar-sounding names — same first 2 characters among unique char names
        name_similarity_warnings = []
        for i in range(len(unique_chars)):
            for j in range(i + 1, len(unique_chars)):
                a, b = unique_chars[i], unique_chars[j]
                if len(a) >= 3 and len(b) >= 3 and a[:3].upper() == b[:3].upper():
                    name_similarity_warnings.append(f"{a} / {b}")

        frustration_score = (
            min(len(internal_state_hits), 3) +
            (2 if name_crowding else 0) +
            len(name_similarity_warnings)
        )

        return {
            'frustration_score': frustration_score,
            'internal_state_hits': internal_state_hits[:2],
            'name_crowding': name_crowding,
            'unique_char_count': len(unique_chars),
            'similar_name_pairs': name_similarity_warnings[:2]
        }

    # =========================================================================
    # PHASE 30: FORMAT COMPLIANCE & DEUS EX MACHINA
    # =========================================================================

    def extract_format_compliance(self, scene, scene_lines):
        """
        Check this scene against industry screenplay format rules:
        1. Slugline must start with INT. or EXT.
        2. Character cue (C-tag) must be ALL CAPS
        3. Action blocks must not exceed 5 consecutive lines without a break
        4. Slugline must contain a time of day (DAY/NIGHT/CONTINUOUS/LATER/DAWN/DUSK)
        Returns a list of per-scene format issues.
        """
        import re as _re
        issues = []

        header = scene.get('header', '') or scene.get('slug', '') or ''
        header_upper = header.upper().strip()

        # 1. Slugline must start with INT. or EXT.
        if header and not (header_upper.startswith('INT') or header_upper.startswith('EXT')):
            issues.append(f"Missing INT./EXT. in slugline: '{header[:40]}'")

        # 2. Slugline must include time of day
        time_markers = {'DAY', 'NIGHT', 'CONTINUOUS', 'LATER', 'DAWN', 'DUSK', 'MORNING', 'EVENING', 'AFTERNOON'}
        if header and not any(t in header_upper for t in time_markers):
            issues.append(f"Slugline missing time of day (DAY/NIGHT/etc.): '{header[:40]}'")

        # 3. Character cues must be ALL CAPS
        for line in scene_lines:
            if line.get('tag') == 'C':
                name = line['text'].split('(')[0].strip()
                if name and name != name.upper():
                    issues.append(f"Character cue not ALL CAPS: '{name}'")
                    break  # Flag once per scene

        # 4. Action block length — more than 5 consecutive A-tagged lines
        run = 0
        for line in scene_lines:
            if line.get('tag') == 'A':
                run += 1
                if run >= 5:
                    issues.append("Overlong action block (5+ consecutive lines) — break into shots or use white space")
                    break
            else:
                run = 0

        return {
            'issue_count': len(issues),
            'issues': issues
        }

    def extract_deus_ex_signals(self, scene_lines, scene_index):
        """
        Track which character names and key objects appear in this scene.
        Used by WriterAgent to detect Act 3 resolutions that rely on
        things that never appeared in Act 1 or Act 2 (deus ex machina).
        """
        characters_present = set()
        for line in scene_lines:
            if line.get('tag') == 'C':
                name = line['text'].split('(')[0].strip()
                if name:
                    characters_present.add(name)

        # Capture key nouns from action lines as potential "objects"
        action_text = ' '.join(l['text'].lower() for l in scene_lines if l.get('tag') == 'A')
        # Simple noun-proxy: capitalized words in action lines (props, proper nouns)
        import re as _re
        prop_candidates = set(_re.findall(r'\b[A-Z][a-z]{3,}\b', ' '.join(
            l['text'] for l in scene_lines if l.get('tag') == 'A'
        )))

        return {
            'scene_index': scene_index,
            'characters': list(characters_present),
            'prop_candidates': list(prop_candidates)[:10]
        }

    def extract_surprisal(self, scene_lines):
        """
        Information-theoretic Surprisal (Perplexity) via GPT-2.
        Measures how predictable the scene text is. Higher perplexity = higher cognitive load.
        Falls back to lexical entropy if ML is unavailable.
        """
        text = ' '.join([line.get('text', '') for line in scene_lines]).strip()
        if not text:
            return {'perplexity': 0.0, 'method': 'None'}
            
        try:
            if getattr(self, '_force_fallback', False):
                raise Exception("Ablation: GPT-2 disabled by user configuration.")
                
            import torch
            from transformers import GPT2LMHeadModel, GPT2TokenizerFast
            import logging
            logger = logging.getLogger('scriptpulse.mlops')
            
            # Use cached model if available, otherwise load and cache
            if not hasattr(self, '_gpt2_model'):
                logger.info("Loading GPT-2 for Surprisal calculation...")
                self._gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
                self._gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
                if torch.cuda.is_available():
                    self._gpt2_model = self._gpt2_model.cuda()
                elif torch.backends.mps.is_available():
                    self._gpt2_model = self._gpt2_model.to('mps')
                self._gpt2_model.eval()

            device = self._gpt2_model.device
            encodings = self._gpt2_tokenizer(text, return_tensors="pt")
            
            max_length = self._gpt2_model.config.n_positions
            stride = 512
            seq_len = encodings.input_ids.size(1)
            
            if seq_len < 2:
                return {'perplexity': 0.0, 'method': 'GPT-2 (Too Short)'}

            nlls = []
            prev_end_loc = 0
            for begin_loc in range(0, seq_len, stride):
                end_loc = min(begin_loc + max_length, seq_len)
                trg_len = end_loc - prev_end_loc
                input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
                target_ids = input_ids.clone()
                target_ids[:, :-trg_len] = -100

                with torch.no_grad():
                    outputs = self._gpt2_model(input_ids, labels=target_ids)
                    neg_log_likelihood = outputs.loss

                nlls.append(neg_log_likelihood)
                prev_end_loc = end_loc
                if end_loc == seq_len:
                    break

            ppl = torch.exp(torch.stack(nlls).mean()).item()
            return {'perplexity': round(ppl, 3), 'method': 'GPT-2'}
            
        except Exception as e:
            import logging
            logger = logging.getLogger('scriptpulse.mlops')
            logger.warning("Surprisal ML failed: %s. Falling back to lexical entropy.", e)
            return {'perplexity': self.extract_information_entropy(scene_lines) * 10, 'method': 'Lexical Entropy Fallback'}

class ImageryAgent:
    """ScriptPulse Imagery Agent - Visual Density Score"""




    def __init__(self):
        self.labels = ['visual description', 'kinetics', 'color', 'texture', 'optics']
        self.is_ml = True

    def run(self, data):
        scenes = data.get('scenes', [])
        ablation_config = data.get('ablation_config', {})
        if not ablation_config.get('use_sbert', True) and not ablation_config.get('use_gpt2', True):
            self.is_ml = False
            
        scores = []
        
        if self.is_ml:
            try:
                classifier = global_manager.get_zero_shot()
                for scene in scenes:
                    text = " ".join([l['text'] for l in scene['lines']]).lower()
                    if len(text.split()) < 5:
                        scores.append(0.0)
                        continue
                        
                    result = classifier(text, self.labels, multi_label=True)
                    # Use the max score as the visual density proxy
                    max_score = max(result['scores'])
                    scores.append(round(max_score, 3))
                return scores
            except Exception as e:
                import logging
                logger = logging.getLogger('scriptpulse.mlops')
                logger.warning("ImageryAgent ML failed, falling back to lexical: %s", e)
                # Fall through to lexical if ML fails
        
        # Lexical Fallback
        colors = {'red', 'blue', 'green', 'black', 'white', 'yellow', 'crimson', 'azure', 'neon', 'dark', 'bright', 'shadow', 'light', 'grey', 'purple', 'silver', 'gold'}
        optics = {'fade', 'cut', 'dissolve', 'zoom', 'pan', 'tilt', 'focus', 'blur', 'glimpse', 'stare', 'look', 'watch', 'see', 'view', 'angle', 'shot', 'pov'}
        textures = {'rough', 'smooth', 'slick', 'wet', 'dry', 'dusty', 'dirty', 'clean', 'pristine', 'shattered', 'broken', 'rusty', 'metallic', 'glass', 'wood'}
        kinetics = {'run', 'jump', 'fall', 'crash', 'explode', 'shatter', 'sprint', 'crawl', 'fly', 'drive', 'spin', 'roll', 'slide', 'hit', 'punch'}
        
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
