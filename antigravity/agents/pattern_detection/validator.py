#!/usr/bin/env python3
"""
Pattern Detection Validator

Validates pattern detection output for non-evaluative language,
persistence requirements, and proper confidence assignment.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


# Forbidden evaluative terms
FORBIDDEN_TERMS = [
    'problem', 'issue', 'flaw', 'weakness', 'mistake', 'error',
    'good', 'bad', 'better', 'worse', 'best', 'worst',
    'should', 'must', 'needs to', 'has to', 'ought to',
    'fix', 'correct', 'improve', 'optimize',
    'exhausting', 'boring', 'confusing', 'frustrating', 'tedious',
    'optimal', 'ideal', 'perfect', 'excellent',
    'too much', 'too little', 'too slow', 'too fast', 'too long', 'too short',
    'main issue', 'primary concern', 'top priority', 'most important',
    'failure', 'succeed', 'success', 'fail'
]

ALLOWED_PATTERN_TYPES = [
    'sustained_demand',
    'limited_recovery',
    'sequence_repetition',
    'surprise_cluster',
    'constructive_strain',
    'degenerative_fatigue'
]

ALLOWED_CONFIDENCE = ['high', 'medium', 'low']


def validate_pattern_structure(patterns: List[Dict]) -> None:
    """Validate pattern structure"""
    for i, pattern in enumerate(patterns):
        # Check required fields
        required = ['pattern_type', 'scene_range', 'confidence_band', 'description']
        for field in required:
            if field not in pattern:
                raise ValidationError(f"Pattern {i}: Missing required field '{field}'")
        
        # Check pattern type
        if pattern['pattern_type'] not in ALLOWED_PATTERN_TYPES:
            raise ValidationError(
                f"Pattern {i}: Invalid pattern type '{pattern['pattern_type']}'. "
                f"Allowed: {ALLOWED_PATTERN_TYPES}"
            )
        
        # Check confidence band
        if pattern['confidence_band'] not in ALLOWED_CONFIDENCE:
            raise ValidationError(
                f"Pattern {i}: Invalid confidence '{pattern['confidence_band']}'. "
                f"Allowed: {ALLOWED_CONFIDENCE}"
            )
        
        # Check scene range
        scene_range = pattern['scene_range']
        if not isinstance(scene_range, list) or len(scene_range) != 2:
            raise ValidationError(f"Pattern {i}: scene_range must be [start, end]")
        
        if scene_range[1] < scene_range[0]:
            raise ValidationError(f"Pattern {i}: Invalid scene range {scene_range}")


def validate_persistence(patterns: List[Dict]) -> None:
    """Validate all patterns span ≥ 3 scenes"""
    for i, pattern in enumerate(patterns):
        start, end = pattern['scene_range']
        span = end - start + 1
        
        if span < 3:
            raise ValidationError(
                f"Pattern {i} ({pattern['pattern_type']}): "
                f"Persistence requirement violated. Spans only {span} scenes (min 3 required)"
            )
    
    print(f"  All patterns span ≥ 3 scenes ✓")


def validate_no_evaluative_language(patterns: List[Dict]) -> None:
    """Check for forbidden evaluative language"""
    for i, pattern in enumerate(patterns):
        description = pattern['description'].lower()
        pattern_type = pattern['pattern_type']
        
        # Check for forbidden terms
        for term in FORBIDDEN_TERMS:
            if term in description:
                raise ValidationError(
                    f"Pattern {i} ({pattern_type}): "
                    f"Forbidden evaluative term detected: '{term}' in description"
                )
        
        # Special check for constructive/degenerative misuse
        if pattern_type in ['constructive_strain', 'degenerative_fatigue']:
            # These should only describe signal behavior, not quality
            if any(word in description for word in ['good', 'bad', 'quality', 'effective']):
                raise ValidationError(
                    f"Pattern {i} ({pattern_type}): "
                    f"Constructive/degenerative must be purely descriptive, not evaluative"
                )
    
    print(f"  No evaluative language detected ✓")


def validate_no_ranking(patterns: List[Dict]) -> None:
    """Ensure no ranking or prioritization"""
    # Check for ranking fields
    disallowed_fields = ['priority', 'importance', 'severity', 'rank', 'order']
    
    for i, pattern in enumerate(patterns):
        for field in disallowed_fields:
            if field in pattern:
                raise ValidationError(
                    f"Pattern {i}: Ranking field '{field}' not allowed"
                )
    
    print(f"  No ranking or prioritization ✓")


def validate_confidence_levels(patterns: List[Dict]) -> None:
    """Validate confidence band distribution"""
    if not patterns:
        return
    
    confidence_counts = {c: 0 for c in ALLOWED_CONFIDENCE}
    
    for pattern in patterns:
        confidence_counts[pattern['confidence_band']] += 1
    
    print(f"  Confidence distribution:")
    for conf, count in confidence_counts.items():
        if count > 0:
            pct = 100 * count / len(patterns)
            print(f"    {conf}: {count} ({pct:.1f}%)")


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validator.py <patterns_json>")
        print("\nValidates pattern detection output from pattern_detector.py")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    try:
        # Load patterns
        data = json.loads(json_file.read_text())
        patterns = data.get('patterns', [])
        
        if not patterns:
            print("✓ No patterns detected (valid outcome)")
            print("\n✅ Validation passed (empty pattern set)")
            return
        
        print(f"✓ Loaded pattern detection: {len(patterns)} patterns")
        
        # Run validations
        print("\nRunning validations...")
        
        print("  • Checking pattern structure...", end=' ')
        validate_pattern_structure(patterns)
        print("✓")
        
        print("  • Checking persistence requirement...", end=' ')
        validate_persistence(patterns)
        
        print("  • Checking for evaluative language...", end=' ')
        validate_no_evaluative_language(patterns)
        
        print("  • Checking for ranking/prioritization...", end=' ')
        validate_no_ranking(patterns)
        
        print("  • Checking confidence levels...")
        validate_confidence_levels(patterns)
        
        # Print pattern summary
        print(f"\n✓ Pattern type distribution:")
        type_counts = {}
        for pattern in patterns:
            ptype = pattern['pattern_type']
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        for ptype, count in sorted(type_counts.items()):
            print(f"    {ptype}: {count}")
        
        print("\n✅ All validations passed!")
        
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
