#!/usr/bin/env python3
"""
Scene Segmentation Validator

Validates scene segmentation output against ScriptPulse constraints:
- All lines covered exactly once
- No micro-scenes
- Conservative segmentation
- Reasonable confidence scores
"""

import json
import sys
from pathlib import Path
from typing import List, Dict


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_coverage(scenes: List[Dict], total_lines: int) -> None:
    """
    Validate that all lines are covered exactly once.
    
    Args:
        scenes: List of scene dictionaries
        total_lines: Total number of lines in screenplay
        
    Raises:
        ValidationError: If coverage is incomplete or overlapping
    """
    covered = set()
    
    for scene in scenes:
        start = scene['start_line']
        end = scene['end_line']
        
        # Check valid range
        if start < 1 or end > total_lines:
            raise ValidationError(
                f"Scene {scene['scene_index']}: Invalid range [{start}, {end}] "
                f"for {total_lines} total lines"
            )
        
        if start > end:
            raise ValidationError(
                f"Scene {scene['scene_index']}: start_line ({start}) > end_line ({end})"
            )
        
        # Check for overlaps
        scene_lines = set(range(start, end + 1))
        overlap = covered & scene_lines
        
        if overlap:
            raise ValidationError(
                f"Scene {scene['scene_index']}: Overlapping lines {sorted(overlap)}"
            )
        
        covered.update(scene_lines)
    
    # Check complete coverage
    expected = set(range(1, total_lines + 1))
    missing = expected - covered
    
    if missing:
        raise ValidationError(
            f"Incomplete coverage: {len(missing)} lines not in any scene: {sorted(missing)[:10]}..."
        )


def validate_scene_lengths(scenes: List[Dict], min_length: int = 3) -> None:
    """
    Validate that scenes meet minimum length requirements.
    
    Args:
        scenes: List of scene dictionaries
        min_length: Minimum scene length
        
    Raises:
        ValidationError: If micro-scenes are detected
    """
    micro_scenes = []
    
    for scene in scenes:
        length = scene['end_line'] - scene['start_line'] + 1
        
        if length < min_length:
            micro_scenes.append(
                f"Scene {scene['scene_index']}: {length} lines "
                f"[{scene['start_line']}-{scene['end_line']}]"
            )
    
    if micro_scenes:
        raise ValidationError(
            f"Micro-scenes detected (< {min_length} lines):\n" + 
            "\n".join(f"  - {s}" for s in micro_scenes)
        )


def validate_confidence_scores(scenes: List[Dict]) -> None:
    """
    Validate boundary confidence scores are reasonable.
    
    Args:
        scenes: List of scene dictionaries
        
    Raises:
        ValidationError: If confidence scores are invalid
    """
    for scene in scenes:
        conf = scene['boundary_confidence']
        
        if not 0.0 <= conf <= 1.0:
            raise ValidationError(
                f"Scene {scene['scene_index']}: Invalid confidence {conf} "
                "(must be 0.0-1.0)"
            )
    
    # Check for suspiciously uniform high confidence (possible over-confidence)
    if len(scenes) > 2:
        high_conf_count = sum(1 for s in scenes if s['boundary_confidence'] > 0.9)
        
        if high_conf_count == len(scenes):
            print("⚠️  Warning: All scenes have very high confidence (> 0.9)")
            print("   This may indicate over-confident segmentation")


def validate_conservative_segmentation(scenes: List[Dict], total_lines: int) -> None:
    """
    Validate that segmentation is conservative (not too many scenes).
    
    Args:
        scenes: List of scene dictionaries
        total_lines: Total number of lines
    """
    avg_scene_length = total_lines / len(scenes) if scenes else 0
    
    # Warning if average scene is very short (possible over-segmentation)
    if avg_scene_length < 10 and len(scenes) > 3:
        print(f"⚠️  Warning: Average scene length is {avg_scene_length:.1f} lines")
        print(f"   This may indicate over-segmentation ({len(scenes)} scenes)")


def validate_sequential_indices(scenes: List[Dict]) -> None:
    """
    Validate that scene indices are sequential starting from 1.
    
    Args:
        scenes: List of scene dictionaries
        
    Raises:
        ValidationError: If indices are not sequential
    """
    for i, scene in enumerate(scenes, 1):
        if scene['scene_index'] != i:
            raise ValidationError(
                f"Scene index mismatch: expected {i}, got {scene['scene_index']}"
            )


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validator.py <segmentation_json_file>")
        print("\nValidates scene segmentation output from segmenter.py")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    try:
        # Load segmentation output
        data = json.loads(json_file.read_text())
        scenes = data.get('scenes', [])
        
        if not scenes:
            raise ValidationError("No scenes found in output")
        
        print(f"✓ Loaded segmentation: {len(scenes)} scenes")
        
        # Infer total lines from max end_line
        total_lines = max(s['end_line'] for s in scenes)
        print(f"✓ Total lines: {total_lines}")
        
        # Run validations
        print("\nRunning validations...")
        
        print("  • Checking sequential indices...", end='')
        validate_sequential_indices(scenes)
        print(" ✓")
        
        print("  • Checking coverage...", end='')
        validate_coverage(scenes, total_lines)
        print(" ✓")
        
        print("  • Checking scene lengths...", end='')
        validate_scene_lengths(scenes)
        print(" ✓")
        
        print("  • Checking confidence scores...", end='')
        validate_confidence_scores(scenes)
        print(" ✓")
        
        print("  • Checking conservative segmentation...", end='')
        validate_conservative_segmentation(scenes, total_lines)
        print(" ✓")
        
        # Print summary
        print("\n✓ Scene summary:")
        for scene in scenes:
            length = scene['end_line'] - scene['start_line'] + 1
            conf = scene['boundary_confidence']
            print(f"    Scene {scene['scene_index']}: "
                  f"lines {scene['start_line']:3d}-{scene['end_line']:3d} "
                  f"({length:2d} lines, confidence: {conf:.2f})")
        
        # Statistics
        avg_length = total_lines / len(scenes)
        avg_conf = sum(s['boundary_confidence'] for s in scenes) / len(scenes)
        
        print(f"\n✓ Statistics:")
        print(f"    Average scene length: {avg_length:.1f} lines")
        print(f"    Average confidence: {avg_conf:.2f}")
        
        print("\n✅ All validations passed!")
        
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
