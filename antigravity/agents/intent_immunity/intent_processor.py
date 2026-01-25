#!/usr/bin/env python3
"""
Writer Intent & Immunity Agent

Applies writer-declared intent to control alert surfacing
without altering analysis.
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# Allowed intent labels (exhaustive)
ALLOWED_INTENT_LABELS = [
    'intentionally_exhausting',
    'intentionally_confusing',
    'should_feel_smooth',
    'should_feel_tense',
    'experimental_anti_narrative'
]


@dataclass
class IntentAnnotation:
    """Writer-declared intent for a scene range"""
    scene_range: Tuple[int, int]
    intent_label: str
    writer_note: Optional[str] = None
    
    def __post_init__(self):
        """Validate intent label"""
        if self.intent_label not in ALLOWED_INTENT_LABELS:
            raise ValueError(
                f"Invalid intent label '{self.intent_label}'. "
                f"Allowed: {ALLOWED_INTENT_LABELS}"
            )


@dataclass
class SuppressedPattern:
    """Pattern suppressed due to writer intent"""
    pattern_type: str
    scene_range: Tuple[int, int]
    suppressed_reason: str
    intent_reference: Dict
    alignment_note: str
    internal_analysis_preserved: bool
    original_data: Dict  # Preserve full pattern
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'pattern_type': self.pattern_type,
            'scene_range': list(self.scene_range),
            'suppressed_reason': self.suppressed_reason,
            'intent_reference': self.intent_reference,
            'alignment_note': self.alignment_note,
            'internal_analysis_preserved': self.internal_analysis_preserved,
            'original_pattern': self.original_data
        }


class IntentProcessor:
    """Processes writer intent annotations to control alert surfacing"""
    
    def __init__(self, intent_annotations: List[Dict]):
        """
        Initialize intent processor.
        
        Args:
            intent_annotations: List of intent annotation dictionaries
        """
        self.intents = [
            IntentAnnotation(
                scene_range=tuple(ann['scene_range']),
                intent_label=ann['intent_label'],
                writer_note=ann.get('writer_note')
            )
            for ann in intent_annotations
        ]
    
    def apply_intent(self, patterns: List[Dict]) -> Dict:
        """
        Apply writer intent to patterns.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Dictionary with surfaced and suppressed patterns
        """
        surfaced = []
        suppressed = []
        
        for pattern in patterns:
            pattern_range = tuple(pattern['scene_range'])
            
            # Find overlapping intent
            matching_intent = self._find_overlapping_intent(pattern_range)
            
            if matching_intent:
                # Check coverage type
                if self._fully_covered(pattern_range, matching_intent):
                    # Fully covered → suppress entire pattern
                    sup_pattern = self._suppress_pattern(pattern, matching_intent, pattern_range)
                    suppressed.append(sup_pattern)
                    
                elif self._partially_covered(pattern_range, matching_intent):
                    # Partially covered → suppress overlap, surface remainder
                    overlap = self._calculate_overlap(pattern_range, matching_intent.scene_range)
                    
                    # Suppress overlapping segment
                    sup_pattern = self._suppress_pattern(pattern, matching_intent, overlap)
                    suppressed.append(sup_pattern)
                    
                    # Surface remainder with downgraded confidence
                    remainder = self._calculate_remainder(pattern_range, overlap)
                    if remainder:
                        downgraded = self._downgrade_pattern(pattern, remainder)
                        surfaced.append(downgraded)
                else:
                    # No overlap (shouldn't happen if _find_overlapping_intent worked)
                    surfaced.append(pattern)
            else:
                # No intent → surface pattern unchanged
                surfaced.append(pattern)
        
        return {
            'surfaced_patterns': surfaced,
            'suppressed_patterns': [p.to_dict() for p in suppressed]
        }
    
    def _find_overlapping_intent(self, pattern_range: Tuple[int, int]) -> Optional[IntentAnnotation]:
        """Find intent annotation that overlaps with pattern"""
        for intent in self.intents:
            if self._ranges_overlap(pattern_range, intent.scene_range):
                return intent
        return None
    
    def _ranges_overlap(self, range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
        """Check if two ranges overlap"""
        return not (range1[1] < range2[0] or range2[1] < range1[0])
    
    def _fully_covered(self, pattern_range: Tuple[int, int], intent: IntentAnnotation) -> bool:
        """Check if pattern is fully covered by intent"""
        return (intent.scene_range[0] <= pattern_range[0] and
                intent.scene_range[1] >= pattern_range[1])
    
    def _partially_covered(self, pattern_range: Tuple[int, int], intent: IntentAnnotation) -> bool:
        """Check if pattern is partially covered by intent"""
        return (self._ranges_overlap(pattern_range, intent.scene_range) and
                not self._fully_covered(pattern_range, intent))
    
    def _calculate_overlap(self, pattern_range: Tuple[int, int], 
                          intent_range: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate overlapping range"""
        start = max(pattern_range[0], intent_range[0])
        end = min(pattern_range[1], intent_range[1])
        return (start, end)
    
    def _calculate_remainder(self, pattern_range: Tuple[int, int],
                            overlap: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Calculate non-overlapping remainder of pattern"""
        # Check if there's a remainder before overlap
        if pattern_range[0] < overlap[0]:
            return (pattern_range[0], overlap[0] - 1)
        
        # Check if there's a remainder after overlap
        if pattern_range[1] > overlap[1]:
            return (overlap[1] + 1, pattern_range[1])
        
        return None
    
    def _suppress_pattern(self, pattern: Dict, intent: IntentAnnotation,
                         suppressed_range: Tuple[int, int]) -> SuppressedPattern:
        """Create suppressed pattern with alignment note"""
        # Generate alignment note
        alignment_note = (
            f"Writer marked scenes {intent.scene_range[0]}-{intent.scene_range[1]} "
            f"as {intent.intent_label.replace('_', ' ')}. "
            f"Detected {pattern['pattern_type'].replace('_', ' ')} pattern "
            f"(scenes {suppressed_range[0]}-{suppressed_range[1]}) "
            f"aligns with declared intent."
        )
        
        return SuppressedPattern(
            pattern_type=pattern['pattern_type'],
            scene_range=suppressed_range,
            suppressed_reason='writer_intent',
            intent_reference={
                'label': intent.intent_label,
                'scene_range': list(intent.scene_range),
                'writer_note': intent.writer_note
            },
            alignment_note=alignment_note,
            internal_analysis_preserved=True,
            original_data=pattern  # Preserve full pattern data
        )
    
    def _downgrade_pattern(self, pattern: Dict, 
                          remainder_range: Tuple[int, int]) -> Dict:
        """Create downgraded pattern for remainder"""
        downgraded = pattern.copy()
        downgraded['scene_range'] = list(remainder_range)
        
        # Downgrade confidence
        current_confidence = pattern.get('confidence_band', 'medium')
        if current_confidence == 'high':
            downgraded['confidence_band'] = 'medium'
        elif current_confidence == 'medium':
            downgraded['confidence_band'] = 'low'
        
        # Add note about partial coverage
        downgraded['note'] = 'Confidence downgraded due to partial intent coverage'
        
        return downgraded


def apply_writer_intent(patterns_file: str, intent_file: str) -> Dict:
    """
    Main entry point for intent processing.
    
    Args:
        patterns_file: Path to detected patterns JSON
        intent_file: Path to intent annotations JSON
        
    Returns:
        Dictionary with surfaced and suppressed patterns
    """
    # Load patterns
    with open(patterns_file, 'r') as f:
        patterns_data = json.load(f)
        patterns = patterns_data.get('patterns', [])
    
    # Load intent annotations
    try:
        with open(intent_file, 'r') as f:
            intent_data = json.load(f)
            intent_annotations = intent_data.get('intent_annotations', [])
    except FileNotFoundError:
        # No intent file → all patterns surface
        return {
            'surfaced_patterns': patterns,
            'suppressed_patterns': []
        }
    
    # Apply intent
    processor = IntentProcessor(intent_annotations)
    result = processor.apply_intent(patterns)
    
    return result


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) not in [2, 3]:
        print("Usage: python intent_processor.py <patterns_json> [intent_json]")
        print("\nIf intent_json not provided, all patterns surface unchanged.")
        sys.exit(1)
    
    patterns_file = sys.argv[1]
    intent_file = sys.argv[2] if len(sys.argv) == 3 else None
    
    if intent_file:
        result = apply_writer_intent(patterns_file, intent_file)
    else:
        # No intent → pass through
        with open(patterns_file, 'r') as f:
            patterns_data = json.load(f)
            result = {
                'surfaced_patterns': patterns_data.get('patterns', []),
                'suppressed_patterns': []
            }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
