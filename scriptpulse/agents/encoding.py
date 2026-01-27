"""Structural Encoding Agent - Observable Feature Extraction"""

import re


def run(input_data):
    """
    Convert scenes into observable feature vectors.
    
    Args:
        input_data: Dict with 'scenes' (from segmentation) and 'lines' (from parsing)
        
    Returns:
        List of feature vectors, one per scene
    """
    scenes = input_data.get('scenes', [])
    lines = input_data.get('lines', [])
    
    if not scenes or not lines:
        return []
    
    feature_vectors = []
    
    for scene in scenes:
        # Get lines for this scene
        scene_lines = get_scene_lines(scene, lines)
        
        # Extract features
        features = {
            'scene_index': scene['scene_index'],
            'linguistic_load': extract_linguistic_load(scene_lines),
            'dialogue_dynamics': extract_dialogue_dynamics(scene_lines),
            'visual_abstraction': extract_visual_abstraction(scene_lines),
            'referential_load': extract_referential_load(scene_lines),
            'structural_change': extract_structural_change(scene, scenes),
            'ambient_signals': extract_ambient_signals(scene_lines)  # NEW
        }
        
        feature_vectors.append(features)
    
    return feature_vectors


def get_scene_lines(scene, all_lines):
    """Extract lines belonging to a scene"""
    start = scene['start_line']
    end = scene['end_line']
    return [line for line in all_lines if start <= line['line_index'] <= end]


def extract_linguistic_load(scene_lines):
    """
    Extract linguistic load features (observable text counts only).
    
    Features:
    - sentence_count: number of sentences
    - mean_sentence_length: average words per sentence  
    - max_sentence_length: longest sentence in words
    - sentence_length_variance: variance in sentence lengths
    """
    # Extract all text (ignoring empty lines)
    all_text = ' '.join([line['text'] for line in scene_lines if line['text'].strip()])
    
    # Split into sentences (basic: by period, !, ?)
    sentences = re.split(r'[.!?]+', all_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {
            'sentence_count': 0,
            'mean_sentence_length': 0.0,
            'max_sentence_length': 0,
            'sentence_length_variance': 0.0
        }
    
    # Count words in each sentence
    word_counts = [len(s.split()) for s in sentences]
    
    mean_length = sum(word_counts) / len(word_counts)
    max_length = max(word_counts)
    
    # Calculate variance
    variance = sum((x - mean_length) ** 2 for x in word_counts) / len(word_counts)
    
    return {
        'sentence_count': len(sentences),
        'mean_sentence_length': round(mean_length, 2),
        'max_sentence_length': max_length,
        'sentence_length_variance': round(variance, 2)
    }


def extract_dialogue_dynamics(scene_lines):
    """
    Extract dialogue dynamics (observable turn-taking only).
    
    Features:
    - dialogue_turns: number of dialogue lines
    - speaker_switches: number of character changes
    - turn_velocity: turns per total lines
    - monologue_runs: sequences of same speaker
    """
    dialogue_lines = [line for line in scene_lines if line['tag'] == 'D']
    character_lines = [line for line in scene_lines if line['tag'] == 'C']
    
    dialogue_count = len(dialogue_lines)
    speaker_count = len(character_lines)
    
    # Calculate speaker switches (consecutive different speakers)
    switches = 0
    if speaker_count > 1:
        for i in range(1, len(character_lines)):
            if character_lines[i]['text'] != character_lines[i-1]['text']:
                switches += 1
    
    # Turn velocity: dialogue per total lines
    total_lines = len(scene_lines)
    velocity = dialogue_count / total_lines if total_lines > 0 else 0.0
    
    # Monologue runs: consecutive same speaker
    monologue_runs = 0
    if speaker_count > 0:
        run_length = 1
        for i in range(1, len(character_lines)):
            if character_lines[i]['text'] == character_lines[i-1]['text']:
                run_length += 1
            else:
                if run_length > 1:
                    monologue_runs += 1
                run_length = 1
        if run_length > 1:
            monologue_runs += 1
    
    return {
        'dialogue_turns': dialogue_count,
        'speaker_switches': switches,
        'turn_velocity': round(velocity, 3),
        'monologue_runs': monologue_runs
    }


def extract_visual_abstraction(scene_lines):
    """
    Extract visual abstraction features (observable action density).
    
    Features:
    - action_lines: count of action/description lines
    - continuous_action_runs: sequences of consecutive action lines
    - vertical_writing_load: total action lines (writing density)
    """
    action_lines = [line for line in scene_lines if line['tag'] == 'A']
    action_count = len(action_lines)
    
    # Count continuous runs of action
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
        'vertical_writing_load': action_count  # Total action for density
    }


def extract_referential_load(scene_lines):
    """
    Extract referential load (observable character count only).
    
    Features:
    - active_character_count: unique characters speaking
    - character_reintroductions: same character appearing after gap
    """
    character_lines = [line for line in scene_lines if line['tag'] == 'C']
    
    # Unique characters
    unique_characters = set(line['text'].strip() for line in character_lines)
    character_count = len(unique_characters)
    
    # Reintroductions: character appears again after other character spoke
    reintroductions = 0
    if len(character_lines) > 1:
        seen = set()
        for char_line in character_lines:
            char = char_line['text'].strip()
            if char in seen:
                reintroductions += 1
            seen.add(char)
    
    return {
        'active_character_count': character_count,
        'character_reintroductions': reintroductions
    }


def extract_structural_change(scene, all_scenes):
    """
    Extract structural change features (observable boundary delta).
    
    Features:
    - event_boundary_score: normalized position change from previous scene
    """
    scene_idx = scene['scene_index']
    
    # First scene has boundary score of 0 (no previous scene to compare)
    if scene_idx == 0:
        return {'event_boundary_score': 0.0}
    
    # Calculate normalized position delta
    prev_scene = all_scenes[scene_idx - 1]
    
    # Line delta between scenes
    line_gap = scene['start_line'] - prev_scene['end_line']
    
    # Normalize by script length (approximate)
    total_lines = max(s['end_line'] for s in all_scenes) + 1
    normalized_score = line_gap / total_lines if total_lines > 0 else 0.0
    
    return {
        'event_boundary_score': round(normalized_score * 100, 2)  # Scale to 0-100
    }


def extract_ambient_signals(scene_lines):
    """
    Detect ambient/observational scene qualities.
    
    Ambient scenes provide breathing space through:
    - Stillness (low action density)
    - Sparse dialogue (low turn velocity)
    - Observational focus (simple, non-complex language)
    
    Returns: Ambient score (0.0-1.0) and component metrics
    """
    # Get existing metrics (reuse extraction functions)
    dialogue = extract_dialogue_dynamics(scene_lines)
    visual = extract_visual_abstraction(scene_lines)
    linguistic = extract_linguistic_load(scene_lines)
    
    # Ambient indicators (all normalized 0-1)
    stillness = 1.0 - min(1.0, visual['action_lines'] / 10.0)
    sparse_dialogue = 1.0 - dialogue['turn_velocity']
    low_complexity = 1.0 - min(1.0, linguistic['sentence_length_variance'] / 20.0)
    short_sentences = 1.0 - min(1.0, linguistic['mean_sentence_length'] / 15.0)
    
    # Composite ambient score (weighted)
    ambient_score = (
        0.35 * stillness +           # Visual calm
        0.30 * sparse_dialogue +     # Dialogue sparsity
        0.20 * low_complexity +      # Linguistic simplicity
        0.15 * short_sentences       # Brevity
    )
    
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

