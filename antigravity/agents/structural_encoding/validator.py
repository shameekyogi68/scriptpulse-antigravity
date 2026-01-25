#!/usr/bin/env python3
"""
Structural Encoding Validator

Validates that encoded features are interpretable, observable, and
contain no semantic inference.
"""

import json
import sys
import math
from pathlib import Path
from typing import List, Dict


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


REQUIRED_FEATURE_GROUPS = [
    'linguistic_load',
    'dialogue_dynamics',
    'visual_abstraction',
    'referential_memory',
    'structural_change'
]

REQUIRED_LINGUISTIC_FEATURES = [
    'sentence_count', 'mean_sentence_length', 'max_sentence_length', 'sentence_length_variance'
]

REQUIRED_DIALOGUE_FEATURES = [
    'dialogue_turns', 'speaker_switches', 'turn_velocity', 'max_monologue_run'
]

REQUIRED_VISUAL_FEATURES = [
    'action_line_count', 'continuous_action_runs', 'fg_bg_action_ratio',
    'visual_density', 'vertical_writing_load'
]

REQUIRED_REFERENTIAL_FEATURES = [
    'active_character_count', 'character_reintroductions', 'pronoun_density'
]

REQUIRED_STRUCTURAL_FEATURES = ['event_boundary_score']


def validate_feature_structure(scenes: List[Dict]) -> None:
    """Validate that all required features are present"""
    for scene in scenes:
        scene_idx = scene.get('scene_index', '?')
        features = scene.get('features', {})
        
        # Check all feature groups present
        for group in REQUIRED_FEATURE_GROUPS:
            if group not in features:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing feature group '{group}'"
                )
        
        # Check linguistic load features
        ling = features['linguistic_load']
        for feat in REQUIRED_LINGUISTIC_FEATURES:
            if feat not in ling:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing linguistic feature '{feat}'"
                )
        
        # Check dialogue dynamics features
        dial = features['dialogue_dynamics']
        for feat in REQUIRED_DIALOGUE_FEATURES:
            if feat not in dial:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing dialogue feature '{feat}'"
                )
        
        # Check visual abstraction features
        vis = features['visual_abstraction']
        for feat in REQUIRED_VISUAL_FEATURES:
            if feat not in vis:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing visual feature '{feat}'"
                )
        
        # Check referential memory features
        ref = features['referential_memory']
        for feat in REQUIRED_REFERENTIAL_FEATURES:
            if feat not in ref:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing referential feature '{feat}'"
                )
        
        # Check structural change features
        struct = features['structural_change']
        for feat in REQUIRED_STRUCTURAL_FEATURES:
            if feat not in struct:
                raise ValidationError(
                    f"Scene {scene_idx}: Missing structural feature '{feat}'"
                )


def validate_numeric_values(scenes: List[Dict]) -> None:
    """Validate that all feature values are valid numbers"""
    for scene in scenes:
        scene_idx = scene['scene_index']
        features = scene['features']
        
        # Flatten all features
        all_features = {}
        for group_name, group_features in features.items():
            for feat_name, value in group_features.items():
                all_features[f"{group_name}.{feat_name}"] = value
        
        # Check each value
        for feat_name, value in all_features.items():
            # Must be numeric
            if not isinstance(value, (int, float)):
                raise ValidationError(
                    f"Scene {scene_idx}: Feature '{feat_name}' is not numeric: {type(value)}"
                )
            
            # Must not be NaN or infinite
            if math.isnan(value):
                raise ValidationError(
                    f"Scene {scene_idx}: Feature '{feat_name}' is NaN"
                )
            
            if math.isinf(value):
                raise ValidationError(
                    f"Scene {scene_idx}: Feature '{feat_name}' is infinite"
                )
            
            # Must be non-negative (all our features are counts, ratios, or distances)
            if value < 0:
                raise ValidationError(
                    f"Scene {scene_idx}: Feature '{feat_name}' is negative: {value}"
                )


def validate_interpretability(scenes: List[Dict]) -> None:
    """Check that features are within reasonable ranges (interpretability check)"""
    warnings = []
    
    for scene in scenes:
        scene_idx = scene['scene_index']
        features = scene['features']
        
        # Linguistic features should be reasonable
        ling = features['linguistic_load']
        if ling['sentence_count'] > 1000:
            warnings.append(
                f"Scene {scene_idx}: Very high sentence count ({ling['sentence_count']})"
            )
        
        if ling['mean_sentence_length'] > 100:
            warnings.append(
                f"Scene {scene_idx}: Very high mean sentence length ({ling['mean_sentence_length']})"
            )
        
        # Dialogue features
        dial = features['dialogue_dynamics']
        if dial['dialogue_turns'] > 500:
            warnings.append(
                f"Scene {scene_idx}: Very high dialogue turns ({dial['dialogue_turns']})"
            )
        
        # Visual features
        vis = features['visual_abstraction']
        if vis['visual_density'] > 1.0:
            raise ValidationError(
                f"Scene {scene_idx}: visual_density cannot exceed 1.0: {vis['visual_density']}"
            )
    
    return warnings


def validate_first_scene_boundary(scenes: List[Dict]) -> None:
    """Validate that first scene has event_boundary_score = 0"""
    if not scenes:
        return
    
    first_scene = scenes[0]
    boundary_score = first_scene['features']['structural_change']['event_boundary_score']
    
    if boundary_score != 0.0:
        raise ValidationError(
            f"First scene must have event_boundary_score = 0.0, got {boundary_score}"
        )


def check_for_semantic_features(scenes: List[Dict]) -> None:
    """Check for any features that might indicate semantic inference"""
    forbidden_keywords = [
        'sentiment', 'emotion', 'quality', 'importance', 'impact',
        'theme', 'topic', 'clarity', 'effectiveness', 'embedding'
    ]
    
    # Check feature names
    for scene in scenes:
        features_json = json.dumps(scene['features']).lower()
        
        for keyword in forbidden_keywords:
            if keyword in features_json:
                raise ValidationError(
                    f"Scene {scene['scene_index']}: Detected forbidden semantic keyword '{keyword}'"
                )


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validator.py <encoded_features_json>")
        print("\nValidates structural encoding output from encoder.py")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    try:
        # Load encoded features
        data = json.loads(json_file.read_text())
        scenes = data.get('encoded_scenes', [])
        
        if not scenes:
            raise ValidationError("No encoded scenes found in output")
        
        print(f"✓ Loaded encoding: {len(scenes)} scenes")
        
        # Run validations
        print("\nRunning validations...")
        
        print("  • Checking feature structure...", end='')
        validate_feature_structure(scenes)
        print(" ✓")
        
        print("  • Checking numeric values...", end='')
        validate_numeric_values(scenes)
        print(" ✓")
        
        print("  • Checking interpretability...", end='')
        warnings = validate_interpretability(scenes)
        print(" ✓")
        
        print("  • Checking first scene boundary...", end='')
        validate_first_scene_boundary(scenes)
        print(" ✓")
        
        print("  • Checking for semantic features...", end='')
        check_for_semantic_features(scenes)
        print(" ✓")
        
        # Print warnings
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"    {warning}")
        
        # Print sample features
        print(f"\n✓ Sample features (Scene 1):")
        first_scene = scenes[0]
        for group_name, group_features in first_scene['features'].items():
            print(f"    {group_name}:")
            for feat_name, value in group_features.items():
                print(f"      {feat_name}: {value}")
        
        print("\n✅ All validations passed!")
        
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
