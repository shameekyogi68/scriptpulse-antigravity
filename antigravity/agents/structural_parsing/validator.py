#!/usr/bin/env python3
"""
Structural Parsing Agent Validator

Validates that the agent output conforms to ScriptPulse boundaries:
- Format correctness (only S, A, D, C, M tags)
- Line count matches input
- No prose or explanations
- Deterministic behavior
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


VALID_TAGS = {'S', 'A', 'D', 'C', 'M'}


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_output_format(tags: List[str], input_lines: List[str]) -> None:
    """
    Validate that tags meet format requirements.
    
    Args:
        tags: List of tags from agent output
        input_lines: Original screenplay lines
        
    Raises:
        ValidationError: If validation fails
    """
    # Check line count match
    if len(tags) != len(input_lines):
        raise ValidationError(
            f"Line count mismatch: {len(tags)} tags for {len(input_lines)} input lines"
        )
    
    # Check each tag
    for i, tag in enumerate(tags, 1):
        tag = tag.strip()
        
        # Check for empty lines
        if not tag:
            raise ValidationError(f"Line {i}: Empty tag")
        
        # Check for invalid characters (only single letter tags allowed)
        if len(tag) != 1:
            raise ValidationError(
                f"Line {i}: Invalid tag '{tag}' - must be single character"
            )
        
        # Check for valid tag
        if tag not in VALID_TAGS:
            raise ValidationError(
                f"Line {i}: Invalid tag '{tag}' - must be one of {VALID_TAGS}"
            )


def check_for_prose(output: str) -> None:
    """
    Check that output contains no prose or explanations.
    
    Args:
        output: Raw output string
        
    Raises:
        ValidationError: If prose is detected
    """
    lines = output.strip().split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for multi-character content (potential prose)
        if len(stripped) > 1:
            raise ValidationError(
                f"Line {i}: Detected prose or explanation '{stripped}' - only single tags allowed"
            )
        
        # Check for common explanation phrases
        explanation_patterns = [
            r'\b(because|this is|note|explanation|confidence)\b',
            r'\d+%',  # Confidence percentages
            r'\(',    # Parenthetical explanations
        ]
        
        for pattern in explanation_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                raise ValidationError(
                    f"Line {i}: Detected explanation pattern in '{line}'"
                )


def validate_determinism(tags1: List[str], tags2: List[str]) -> None:
    """
    Validate that two runs produce identical output (determinism check).
    
    Args:
        tags1: First run output
        tags2: Second run output
        
    Raises:
        ValidationError: If outputs differ
    """
    if tags1 != tags2:
        for i, (t1, t2) in enumerate(zip(tags1, tags2), 1):
            if t1 != t2:
                raise ValidationError(
                    f"Determinism failure at line {i}: '{t1}' vs '{t2}'"
                )
        
        # Different lengths
        raise ValidationError(
            f"Determinism failure: different output lengths {len(tags1)} vs {len(tags2)}"
        )


def load_file(filepath: Path) -> Tuple[List[str], str]:
    """
    Load screenplay file.
    
    Returns:
        Tuple of (lines list, raw content)
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    return lines, content


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validator.py <screenplay_file>")
        print("\nThis validator checks the structural parsing agent output format.")
        print("It does NOT run the agent - you must provide pre-tagged output.")
        sys.exit(1)
    
    screenplay_path = Path(sys.argv[1])
    
    try:
        # Load screenplay
        lines, content = load_file(screenplay_path)
        print(f"✓ Loaded screenplay: {len(lines)} lines")
        
        # Check for corresponding .tags file
        tags_path = screenplay_path.with_suffix('.tags')
        if not tags_path.exists():
            print(f"\n⚠ No tags file found at {tags_path}")
            print("Expected format: one tag per line (S, A, D, C, or M)")
            sys.exit(1)
        
        # Load tags
        tags_content = tags_path.read_text(encoding='utf-8')
        tags = [line.strip() for line in tags_content.split('\n') if line.strip()]
        
        print(f"✓ Loaded tags: {len(tags)} tags")
        
        # Run validations
        print("\nRunning validations...")
        
        print("  • Checking output format...", end='')
        validate_output_format(tags, lines)
        print(" ✓")
        
        print("  • Checking for prose/explanations...", end='')
        check_for_prose(tags_content)
        print(" ✓")
        
        # Tag distribution
        tag_counts = {tag: tags.count(tag) for tag in VALID_TAGS}
        print("\n✓ Tag distribution:")
        for tag, count in sorted(tag_counts.items()):
            if count > 0:
                percentage = (count / len(tags)) * 100
                print(f"    {tag}: {count:4d} ({percentage:5.1f}%)")
        
        print("\n✅ All validations passed!")
        
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
