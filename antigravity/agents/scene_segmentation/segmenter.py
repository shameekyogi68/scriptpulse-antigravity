#!/usr/bin/env python3
"""
Scene Segmentation Agent

Groups structurally tagged screenplay lines into scenes using conservative
boundary detection with confidence smoothing and post-merge heuristics.
"""

import json
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Scene:
    """Represents a scene segment"""
    scene_index: int
    start_line: int  # 1-indexed
    end_line: int    # 1-indexed, inclusive
    boundary_confidence: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'scene_index': self.scene_index,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'boundary_confidence': round(self.boundary_confidence, 2)
        }
    
    def length(self) -> int:
        """Return number of lines in scene"""
        return self.end_line - self.start_line + 1


class SceneSegmenter:
    """Conservative scene segmentation using structural tags only"""
    
    # Configuration
    MIN_SCENE_LENGTH = 3
    LOW_CONFIDENCE_THRESHOLD = 0.5
    MERGE_CONFIDENCE_THRESHOLD = 0.6
    
    def __init__(self, tags: List[str]):
        """
        Initialize segmenter with structural tags.
        
        Args:
            tags: List of structural tags (S, A, D, C, M)
        """
        self.tags = tags
        self.num_lines = len(tags)
    
    def segment(self) -> List[Scene]:
        """
        Perform conservative scene segmentation.
        
        Returns:
            List of Scene objects
        """
        # Step 1: Detect initial boundaries
        boundaries = self._detect_boundaries()
        
        # Step 2: Create initial scenes
        scenes = self._create_scenes(boundaries)
        
        # Step 3: Merge micro-scenes
        scenes = self._merge_micro_scenes(scenes)
        
        # Step 4: Post-merge low-confidence scenes
        scenes = self._merge_low_confidence(scenes)
        
        # Step 5: Renumber scenes
        scenes = self._renumber_scenes(scenes)
        
        return scenes
    
    def _detect_boundaries(self) -> List[Tuple[int, float]]:
        """
        Detect scene boundaries with confidence scores.
        
        Returns:
            List of (line_number, confidence) tuples
        """
        boundaries = [(1, 1.0)]  # First line always starts a scene
        
        for i in range(1, self.num_lines):
            tag = self.tags[i]
            
            if tag == 'S':  # Scene heading
                confidence = self._calculate_boundary_confidence(i)
                
                if confidence > 0.3:  # Only add if confidence is reasonable
                    boundaries.append((i + 1, confidence))  # +1 for 1-indexing
        
        return boundaries
    
    def _calculate_boundary_confidence(self, index: int) -> float:
        """
        Calculate confidence score for a potential boundary at index.
        
        Args:
            index: 0-indexed position of 'S' tag
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        confidence = 0.5  # Base confidence for S tag
        
        # Look at surrounding context (±2 lines)
        window_start = max(0, index - 2)
        window_end = min(self.num_lines, index + 3)
        context = self.tags[window_start:window_end]
        
        # Boost confidence for stable patterns
        # Good pattern: ...A S A C D...
        if index > 0 and self.tags[index - 1] in ['A', 'M', 'D']:
            confidence += 0.2
        
        if index < self.num_lines - 1 and self.tags[index + 1] == 'A':
            confidence += 0.2
        
        if index < self.num_lines - 2 and self.tags[index + 2] == 'C':
            confidence += 0.1
        
        # Reduce confidence for noise indicators
        # Multiple consecutive S tags (formatting error)
        if index > 0 and self.tags[index - 1] == 'S':
            confidence -= 0.3
        
        if index < self.num_lines - 1 and self.tags[index + 1] == 'S':
            confidence -= 0.3
        
        # Isolated S tag surrounded by metadata
        if (index > 0 and self.tags[index - 1] == 'M' and 
            index < self.num_lines - 1 and self.tags[index + 1] == 'M'):
            confidence -= 0.2
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def _create_scenes(self, boundaries: List[Tuple[int, float]]) -> List[Scene]:
        """
        Create initial scene objects from boundaries.
        
        Args:
            boundaries: List of (start_line, confidence) tuples
            
        Returns:
            List of Scene objects
        """
        scenes = []
        
        for i, (start_line, confidence) in enumerate(boundaries):
            # Determine end line
            if i < len(boundaries) - 1:
                end_line = boundaries[i + 1][0] - 1
            else:
                end_line = self.num_lines
            
            scene = Scene(
                scene_index=i + 1,
                start_line=start_line,
                end_line=end_line,
                boundary_confidence=confidence
            )
            scenes.append(scene)
        
        return scenes
    
    def _merge_micro_scenes(self, scenes: List[Scene]) -> List[Scene]:
        """
        Merge scenes that are too short (likely formatting errors).
        
        Args:
            scenes: List of Scene objects
            
        Returns:
            List of Scene objects with micro-scenes merged
        """
        if len(scenes) <= 1:
            return scenes
        
        merged = []
        i = 0
        
        while i < len(scenes):
            current = scenes[i]
            
            # Check if current scene is too short
            if current.length() < self.MIN_SCENE_LENGTH:
                # Try to merge with next scene if available
                if i < len(scenes) - 1:
                    next_scene = scenes[i + 1]
                    # Merge into next scene
                    merged_scene = Scene(
                        scene_index=current.scene_index,
                        start_line=current.start_line,
                        end_line=next_scene.end_line,
                        boundary_confidence=min(current.boundary_confidence, 
                                               next_scene.boundary_confidence)
                    )
                    merged.append(merged_scene)
                    i += 2  # Skip next scene (already merged)
                else:
                    # Last scene is short, merge with previous
                    if merged:
                        prev = merged.pop()
                        merged_scene = Scene(
                            scene_index=prev.scene_index,
                            start_line=prev.start_line,
                            end_line=current.end_line,
                            boundary_confidence=min(prev.boundary_confidence,
                                                   current.boundary_confidence)
                        )
                        merged.append(merged_scene)
                    else:
                        # Only scene, keep it
                        merged.append(current)
                    i += 1
            else:
                merged.append(current)
                i += 1
        
        return merged
    
    def _merge_low_confidence(self, scenes: List[Scene]) -> List[Scene]:
        """
        Merge adjacent scenes with low boundary confidence.
        
        Args:
            scenes: List of Scene objects
            
        Returns:
            List of Scene objects with low-confidence boundaries merged
        """
        if len(scenes) <= 1:
            return scenes
        
        merged = [scenes[0]]
        
        for i in range(1, len(scenes)):
            current = scenes[i]
            prev = merged[-1]
            
            # Merge if boundary confidence is low
            if current.boundary_confidence < self.MERGE_CONFIDENCE_THRESHOLD:
                # Merge with previous scene
                merged_scene = Scene(
                    scene_index=prev.scene_index,
                    start_line=prev.start_line,
                    end_line=current.end_line,
                    boundary_confidence=max(prev.boundary_confidence,
                                           current.boundary_confidence)
                )
                merged[-1] = merged_scene
            else:
                merged.append(current)
        
        return merged
    
    def _renumber_scenes(self, scenes: List[Scene]) -> List[Scene]:
        """
        Renumber scenes sequentially after merging.
        
        Args:
            scenes: List of Scene objects
            
        Returns:
            List of Scene objects with sequential indices
        """
        for i, scene in enumerate(scenes, 1):
            scene.scene_index = i
        return scenes


def segment_scenes(tags: List[str]) -> Dict:
    """
    Main entry point for scene segmentation.
    
    Args:
        tags: List of structural tags
        
    Returns:
        Dictionary with 'scenes' key containing scene list
    """
    segmenter = SceneSegmenter(tags)
    scenes = segmenter.segment()
    
    return {
        'scenes': [scene.to_dict() for scene in scenes]
    }


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python segmenter.py <tags_file>")
        sys.exit(1)
    
    tags_file = sys.argv[1]
    
    # Load tags
    with open(tags_file, 'r') as f:
        tags = [line.strip() for line in f if line.strip()]
    
    # Segment scenes
    result = segment_scenes(tags)
    
    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
