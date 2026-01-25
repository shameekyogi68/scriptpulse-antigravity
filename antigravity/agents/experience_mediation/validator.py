#!/usr/bin/env python3
"""
Experience Mediation Validator

Validates output for forbidden language and required elements.
"""

import json
import sys
from pathlib import Path
from typing import Dict

FORBIDDEN_WORDS = [
    'good', 'bad', 'improve', 'fix', 'optimize',
    'too long', 'too short', 'slow', 'fast',
    'weak', 'strong', 'problem', 'issue',
    'ideal', 'optimal', 'boring', 'exciting',
    'confusing', 'clear', 'engaging', 'dull',
    'effective', 'ineffective', 'should', 'must',
    'need to', 'recommend', 'suggest'
]

REQUIRED_UNCERTAINTY = ['may', 'might', 'could']

class ValidationError(Exception):
    pass

def validate_no_forbidden_language(output: Dict) -> None:
    """Check for forbidden language"""
    output_str = json.dumps(output).lower()
    
    for word in FORBIDDEN_WORDS:
        if word.lower() in output_str:
            raise ValidationError(f"Forbidden language detected: '{word}'")
    
    print("  No forbidden language ✓")

def validate_question_framing(output: Dict) -> None:
    """Check all reflections have question framing"""
    reflections = output.get('reflections', [])
    
    for i, ref in enumerate(reflections):
        question = ref.get('question', '')
        if not question.strip().endswith('?'):
            raise ValidationError(f"Reflection {i}: Question must end with '?'")
    
    print(f"  All {len(reflections)} reflections have question framing ✓")

def validate_uncertainty_markers(output: Dict) -> None:
    """Check uncertainty markers present"""
    reflections = output.get('reflections', [])
    
    for i, ref in enumerate(reflections):
        uncertainty = ref.get('uncertainty', '')
        if uncertainty not in REQUIRED_UNCERTAINTY:
            raise ValidationError(f"Reflection {i}: Invalid uncertainty '{uncertainty}'")
    
    print(f"  All uncertainty markers valid ✓")

def validate_silence_handling(output: Dict) -> None:
    """Check silence explanation when no reflections"""
    reflections = output.get('reflections', [])
    silence = output.get('silence_explanation')
    
    if not reflections and not silence:
        raise ValidationError("No reflections but silence_explanation is missing")
    
    if not reflections:
        print(f"  Silence explanation present: '{silence[:50]}...' ✓")
    else:
        print(f"  {len(reflections)} reflections present ✓")

def main():
    if len(sys.argv) != 2:
        print("Usage: python validator.py <mediated_output_json>")
        sys.exit(1)
    
    data = json.loads(Path(sys.argv[1]).read_text())
    
    print("✓ Loaded mediated output")
    print("\nRunning validations...")
    
    validate_no_forbidden_language(data)
    validate_question_framing(data)
    validate_uncertainty_markers(data)
    validate_silence_handling(data)
    
    print("\n✅ All validations passed!")

if __name__ == '__main__':
    main()
