#!/usr/bin/env python3
"""
Intent Immunity Validator

Validates intent processing output for proper suppression rules.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

ALLOWED_INTENT_LABELS = [
    'intentionally_exhausting',
    'intentionally_confusing',
    'should_feel_smooth',
    'should_feel_tense',
    'experimental_anti_narrative'
]

class ValidationError(Exception):
    pass

def validate_no_suppression_without_intent(suppressed: List[Dict]) -> None:
    """Validate all suppressions have intent reference"""
    for i, pattern in enumerate(suppressed):
        if pattern.get('suppressed_reason') != 'writer_intent':
            raise ValidationError(f"Suppressed pattern {i}: Invalid suppression reason")
        if 'intent_reference' not in pattern:
            raise ValidationError(f"Suppressed pattern {i}: Missing intent reference")
        if 'alignment_note' not in pattern:
            raise ValidationError(f"Suppressed pattern {i}: Missing alignment note")
    print(f"  All {len(suppressed)} suppressed patterns have intent reference ✓")

def validate_intent_labels(suppressed: List[Dict]) -> None:
    """Validate all intent labels are from allowed list"""
    for i, pattern in enumerate(suppressed):
        label = pattern.get('intent_reference', {}).get('label')
        if label not in ALLOWED_INTENT_LABELS:
            raise ValidationError(f"Suppressed pattern {i}: Invalid intent label '{label}'")
    print(f"  All intent labels valid ✓")

def validate_analysis_preserved(suppressed: List[Dict]) -> None:
    """Validate analysis is preserved in suppressed patterns"""
    for i, pattern in enumerate(suppressed):
        if not pattern.get('internal_analysis_preserved', False):
            raise ValidationError(f"Suppressed pattern {i}: Analysis not preserved")
    print(f"  Analysis preserved in all suppressed patterns ✓")

def main():
    if len(sys.argv) != 2:
        print("Usage: python validator.py <filtered_patterns_json>")
        sys.exit(1)
    
    data = json.loads(Path(sys.argv[1]).read_text())
    surfaced = data.get('surfaced_patterns', [])
    suppressed = data.get('suppressed_patterns', [])
    
    print(f"✓ Loaded: {len(surfaced)} surfaced, {len(suppressed)} suppressed patterns")
    print("\nRunning validations...")
    
    if suppressed:
        validate_no_suppression_without_intent(suppressed)
        validate_intent_labels(suppressed)
        validate_analysis_preserved(suppressed)
    else:
        print("  No suppressed patterns to validate ✓")
    
    print("\n✅ All validations passed!")

if __name__ == '__main__':
    main()
