#!/usr/bin/env python3
"""
Structural Encoding Agent

Converts scenes into interpretable structural feature vectors using
only observable metrics. No semantic inference allowed.
"""

import json
import re
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class LinguisticLoad:
    """Linguistic processing load features"""
    sentence_count: int
    mean_sentence_length: float
    max_sentence_length: int
    sentence_length_variance: float


@dataclass
class DialogueDynamics:
    """Dialogue dynamics features"""
    dialogue_turns: int
    speaker_switches: int
    turn_velocity: float
    max_monologue_run: int


@dataclass
class VisualAbstraction:
    """Visual abstraction load features"""
    action_line_count: int
    continuous_action_runs: int
    fg_bg_action_ratio: float
    visual_density: float
    vertical_writing_load: int


@dataclass
class ReferentialMemory:
    """Referential working-memory load features"""
    active_character_count: int
    character_reintroductions: int
    pronoun_density: float


@dataclass
class StructuralChange:
    """Structural change from previous scene"""
    event_boundary_score: float


@dataclass
class SceneFeatures:
    """Complete feature vector for a scene"""
    scene_index: int
    linguistic_load: LinguisticLoad
    dialogue_dynamics: DialogueDynamics
    visual_abstraction: VisualAbstraction
    referential_memory: ReferentialMemory
    structural_change: StructuralChange
    
    def to_dict(self) -> Dict:
        """Convert to nested dictionary for JSON serialization"""
        return {
            'scene_index': self.scene_index,
            'features': {
                'linguistic_load': asdict(self.linguistic_load),
                'dialogue_dynamics': asdict(self.dialogue_dynamics),
                'visual_abstraction': asdict(self.visual_abstraction),
                'referential_memory': asdict(self.referential_memory),
                'structural_change': asdict(self.structural_change)
            }
        }
    
    def to_vector(self) -> List[float]:
        """Convert to flat numeric vector for distance calculations"""
        return [
            float(self.linguistic_load.sentence_count),
            self.linguistic_load.mean_sentence_length,
            float(self.linguistic_load.max_sentence_length),
            self.linguistic_load.sentence_length_variance,
            float(self.dialogue_dynamics.dialogue_turns),
            float(self.dialogue_dynamics.speaker_switches),
            self.dialogue_dynamics.turn_velocity,
            float(self.dialogue_dynamics.max_monologue_run),
            float(self.visual_abstraction.action_line_count),
            float(self.visual_abstraction.continuous_action_runs),
            self.visual_abstraction.fg_bg_action_ratio,
            self.visual_abstraction.visual_density,
            float(self.visual_abstraction.vertical_writing_load),
            float(self.referential_memory.active_character_count),
            float(self.referential_memory.character_reintroductions),
            self.referential_memory.pronoun_density
        ]


class StructuralEncoder:
    """Extracts interpretable structural features from scenes"""
    
    # Pronouns for referential memory tracking
    PRONOUNS = {
        'he', 'she', 'it', 'they', 'him', 'her', 'them',
        'his', 'hers', 'its', 'their', 'theirs',
        'himself', 'herself', 'itself', 'themselves'
    }
    
    def __init__(self, screenplay_lines: List[str], tags: List[str], scenes: List[Dict]):
        """
        Initialize encoder with screenplay data.
        
        Args:
            screenplay_lines: Original screenplay text (one line per element)
            tags: Structural tags (S, A, D, C, M) matching lines
            scenes: Scene boundaries from segmentation agent
        """
        self.lines = screenplay_lines
        self.tags = tags
        self.scenes = scenes
        self.character_history = []  # Track characters across scenes
    
    def encode_all_scenes(self) -> List[SceneFeatures]:
        """
        Encode all scenes into feature vectors.
        
        Returns:
            List of SceneFeatures objects
        """
        encoded_scenes = []
        prev_features = None
        
        for scene in self.scenes:
            features = self._encode_scene(scene, prev_features)
            encoded_scenes.append(features)
            prev_features = features
        
        return encoded_scenes
    
    def _encode_scene(self, scene: Dict, prev_features: Optional[SceneFeatures]) -> SceneFeatures:
        """Encode a single scene"""
        # Extract scene lines and tags
        start_idx = scene['start_line'] - 1  # Convert to 0-indexed
        end_idx = scene['end_line']
        
        scene_lines = self.lines[start_idx:end_idx]
        scene_tags = self.tags[start_idx:end_idx]
        
        # Extract features
        linguistic = self._extract_linguistic_load(scene_lines, scene_tags)
        dialogue = self._extract_dialogue_dynamics(scene_lines, scene_tags)
        visual = self._extract_visual_abstraction(scene_lines, scene_tags)
        referential = self._extract_referential_memory(scene_lines, scene_tags)
        
        # Create features object
        features = SceneFeatures(
            scene_index=scene['scene_index'],
            linguistic_load=linguistic,
            dialogue_dynamics=dialogue,
            visual_abstraction=visual,
            referential_memory=referential,
            structural_change=StructuralChange(event_boundary_score=0.0)
        )
        
        # Calculate structural change if previous scene exists
        if prev_features:
            features.structural_change.event_boundary_score = self._calculate_event_boundary(
                features, prev_features
            )
        
        return features
    
    def _extract_linguistic_load(self, lines: List[str], tags: List[str]) -> LinguisticLoad:
        """Extract linguistic processing load features"""
        # Get dialogue and action text
        text_lines = [
            line for line, tag in zip(lines, tags)
            if tag in ['A', 'D'] and line.strip()
        ]
        
        if not text_lines:
            return LinguisticLoad(
                sentence_count=0,
                mean_sentence_length=0.0,
                max_sentence_length=0,
                sentence_length_variance=0.0
            )
        
        # Extract sentences (period-delimited)
        all_text = ' '.join(text_lines)
        sentences = [s.strip() for s in re.split(r'[.!?]+', all_text) if s.strip()]
        
        if not sentences:
            return LinguisticLoad(
                sentence_count=0,
                mean_sentence_length=0.0,
                max_sentence_length=0,
                sentence_length_variance=0.0
            )
        
        # Calculate sentence lengths in words
        sentence_lengths = [len(s.split()) for s in sentences]
        
        mean_len = sum(sentence_lengths) / len(sentence_lengths)
        max_len = max(sentence_lengths)
        
        # Calculate variance
        if len(sentence_lengths) > 1:
            variance = sum((x - mean_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        else:
            variance = 0.0
        
        return LinguisticLoad(
            sentence_count=len(sentences),
            mean_sentence_length=round(mean_len, 2),
            max_sentence_length=max_len,
            sentence_length_variance=round(variance, 2)
        )
    
    def _extract_dialogue_dynamics(self, lines: List[str], tags: List[str]) -> DialogueDynamics:
        """Extract dialogue dynamics features"""
        dialogue_turns = sum(1 for tag in tags if tag == 'D')
        
        # Track speaker switches
        characters = []
        current_speaker = None
        
        for line, tag in zip(lines, tags):
            if tag == 'C':
                speaker = line.strip()
                characters.append(speaker)
                if current_speaker != speaker:
                    current_speaker = speaker
        
        speaker_switches = len(set(characters)) - 1 if len(characters) > 1 else 0
        
        # Calculate turn velocity (turns per estimated page)
        # Approximate: 55 lines ≈ 1 page
        estimated_pages = max(1, len(lines) / 55.0)
        turn_velocity = round(dialogue_turns / estimated_pages, 2)
        
        # Find max monologue run (consecutive D tags by same speaker)
        max_run = 0
        current_run = 0
        prev_speaker = None
        d_count = 0
        
        for line, tag in zip(lines, tags):
            if tag == 'C':
                prev_speaker = line.strip()
                d_count = 0
            elif tag == 'D':
                d_count += 1
                current_run = d_count
                max_run = max(max_run, current_run)
        
        return DialogueDynamics(
            dialogue_turns=dialogue_turns,
            speaker_switches=speaker_switches,
            turn_velocity=turn_velocity,
            max_monologue_run=max_run
        )
    
    def _extract_visual_abstraction(self, lines: List[str], tags: List[str]) -> VisualAbstraction:
        """Extract visual abstraction load features"""
        action_line_count = sum(1 for tag in tags if tag == 'A')
        
        # Count continuous action runs
        continuous_runs = 0
        in_run = False
        
        for tag in tags:
            if tag == 'A':
                if not in_run:
                    continuous_runs += 1
                    in_run = True
            else:
                in_run = False
        
        # Calculate foreground vs background action ratio
        # Heuristic: short action lines (<20 words) = foreground, long = background
        fg_count = 0
        bg_count = 0
        
        for line, tag in zip(lines, tags):
            if tag == 'A':
                word_count = len(line.split())
                if word_count < 20:
                    fg_count += 1
                else:
                    bg_count += 1
        
        fg_bg_ratio = round(fg_count / bg_count if bg_count > 0 else float(fg_count), 2)
        
        # Visual density
        total_lines = len(lines)
        visual_density = round(action_line_count / total_lines if total_lines > 0 else 0.0, 2)
        
        # Vertical writing load (max consecutive A tag block)
        max_block = 0
        current_block = 0
        
        for tag in tags:
            if tag == 'A':
                current_block += 1
                max_block = max(max_block, current_block)
            else:
                current_block = 0
        
        return VisualAbstraction(
            action_line_count=action_line_count,
            continuous_action_runs=continuous_runs,
            fg_bg_action_ratio=fg_bg_ratio,
            visual_density=visual_density,
            vertical_writing_load=max_block
        )
    
    def _extract_referential_memory(self, lines: List[str], tags: List[str]) -> ReferentialMemory:
        """Extract referential working-memory load features"""
        # Active character count
        characters = set()
        for line, tag in zip(lines, tags):
            if tag == 'C':
                characters.add(line.strip())
        
        active_character_count = len(characters)
        
        # Character reintroductions (not in last 2 scenes)
        reintroductions = 0
        recent_history = self.character_history[-2:] if len(self.character_history) >= 2 else []
        recent_chars = set()
        for scene_chars in recent_history:
            recent_chars.update(scene_chars)
        
        for char in characters:
            if char not in recent_chars:
                reintroductions += 1
        
        # Update character history
        self.character_history.append(characters)
        
        # Pronoun density
        all_text = ' '.join(line for line, tag in zip(lines, tags) if tag in ['A', 'D'])
        words = all_text.lower().split()
        total_words = len(words)
        
        pronoun_count = sum(1 for word in words if word in self.PRONOUNS)
        pronoun_density = round(pronoun_count / total_words if total_words > 0 else 0.0, 3)
        
        return ReferentialMemory(
            active_character_count=active_character_count,
            character_reintroductions=reintroductions,
            pronoun_density=pronoun_density
        )
    
    def _calculate_event_boundary(self, current: SceneFeatures, previous: SceneFeatures) -> float:
        """Calculate Euclidean distance between feature vectors"""
        curr_vec = current.to_vector()
        prev_vec = previous.to_vector()
        
        # Euclidean distance
        distance = math.sqrt(sum((c - p) ** 2 for c, p in zip(curr_vec, prev_vec)))
        
        return round(distance, 2)


def encode_screenplay(screenplay_file: str, tags_file: str, scenes_file: str) -> Dict:
    """
    Main entry point for structural encoding.
    
    Args:
        screenplay_file: Path to original screenplay
        tags_file: Path to structural tags
        scenes_file: Path to scene boundaries JSON
        
    Returns:
        Dictionary with encoded scenes
    """
    # Load inputs
    with open(screenplay_file, 'r') as f:
        lines = f.read().split('\n')
    
    with open(tags_file, 'r') as f:
        tags = [line.strip() for line in f if line.strip()]
    
    with open(scenes_file, 'r') as f:
        scenes_data = json.load(f)
        scenes = scenes_data['scenes']
    
    # Encode
    encoder = StructuralEncoder(lines, tags, scenes)
    encoded_scenes = encoder.encode_all_scenes()
    
    return {
        'encoded_scenes': [scene.to_dict() for scene in encoded_scenes]
    }


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python encoder.py <screenplay_file> <tags_file> <scenes_file>")
        sys.exit(1)
    
    screenplay_file = sys.argv[1]
    tags_file = sys.argv[2]
    scenes_file = sys.argv[3]
    
    result = encode_screenplay(screenplay_file, tags_file, scenes_file)
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
