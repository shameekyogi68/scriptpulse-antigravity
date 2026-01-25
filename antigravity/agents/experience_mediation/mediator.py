#!/usr/bin/env python3
"""
Audience-Experience Mediation Agent

Translates internal pattern signals into writer-safe, experiential language.
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


# Experiential translation templates
PATTERN_TRANSLATIONS = {
    'sustained_demand': "The audience may begin to feel mentally tired here.",
    'limited_recovery': "There's little chance to catch their breath.",
    'surprise_cluster': "The shifts may feel sudden on first exposure.",
    'sequence_repetition': "This stretch may feel similar to what came just before.",
    'constructive_strain': "This section asks for sustained focus from the audience.",
    'degenerative_fatigue': "Attention may drift without recovery points."
}

# Question templates
QUESTION_TEMPLATES = [
    "Is this the experience you want for scenes {start}-{end}?",
    "Is this the level of {aspect} you want the audience to hold through scenes {start}-{end}?",
    "Does this match your intention for scenes {start}-{end}?"
]

# Uncertainty words by confidence
UNCERTAINTY_WORDS = {
    'high': 'may',
    'medium': 'might',
    'low': 'could'
}

# Silence explanations
SILENCE_EXPLANATIONS = {
    'stable': "The attentional flow appears stable with regular recovery throughout the script.",
    'low_confidence': "Signals are low confidence due to draft variability.",
    'intent_aligned': "All detected patterns align with your declared intent.",
    'no_patterns': "No persistent patterns were detected across the required scene threshold."
}

# Forbidden words - hard ban
FORBIDDEN_WORDS = [
    'good', 'bad', 'improve', 'fix', 'optimize',
    'too long', 'too short', 'slow', 'fast',
    'weak', 'strong', 'problem', 'issue',
    'ideal', 'optimal', 'boring', 'exciting',
    'confusing', 'clear', 'engaging', 'dull',
    'effective', 'ineffective', 'should', 'must',
    'need to', 'recommend', 'suggest'
]


@dataclass
class Reflection:
    """Writer-facing experiential reflection"""
    scene_range: tuple
    question: str
    experience: str
    uncertainty: str
    confidence_band: str
    
    def to_dict(self) -> Dict:
        return {
            'scene_range': list(self.scene_range),
            'question': self.question,
            'experience': self.experience,
            'uncertainty': self.uncertainty,
            'confidence_band': self.confidence_band
        }


@dataclass
class IntentAcknowledgment:
    """Acknowledgment of writer intent"""
    scene_range: tuple
    intent_label: str
    acknowledgment: str
    
    def to_dict(self) -> Dict:
        return {
            'scene_range': list(self.scene_range),
            'intent_label': self.intent_label,
            'acknowledgment': self.acknowledgment
        }


class ExperienceMediator:
    """Translates patterns into writer-safe language"""
    
    def __init__(self):
        self.reflections: List[Reflection] = []
        self.intent_acknowledgments: List[IntentAcknowledgment] = []
        self.silence_explanation: Optional[str] = None
    
    def mediate(self, surfaced_patterns: List[Dict], 
                suppressed_patterns: List[Dict]) -> Dict:
        """
        Translate patterns into writer-safe output.
        
        Args:
            surfaced_patterns: Patterns to translate
            suppressed_patterns: Patterns suppressed by intent
            
        Returns:
            Writer-facing mediated output
        """
        # Process surfaced patterns
        for pattern in surfaced_patterns:
            reflection = self._create_reflection(pattern)
            self.reflections.append(reflection)
        
        # Process intent acknowledgments
        for suppressed in suppressed_patterns:
            if suppressed.get('suppressed_reason') == 'writer_intent':
                ack = self._create_intent_acknowledgment(suppressed)
                self.intent_acknowledgments.append(ack)
        
        # Handle silence
        if not surfaced_patterns:
            self.silence_explanation = self._determine_silence_reason(
                suppressed_count=len(suppressed_patterns)
            )
        
        return self._build_output()
    
    def _create_reflection(self, pattern: Dict) -> Reflection:
        """Create experiential reflection from pattern"""
        pattern_type = pattern.get('pattern_type', 'sustained_demand')
        scene_range = tuple(pattern.get('scene_range', [0, 0]))
        confidence = pattern.get('confidence_band', 'medium')
        
        # Get translation template
        base_translation = PATTERN_TRANSLATIONS.get(
            pattern_type,
            "The audience may experience elevated attention here."
        )
        
        # Apply uncertainty
        uncertainty_word = UNCERTAINTY_WORDS.get(confidence, 'may')
        experience = self._apply_uncertainty(base_translation, uncertainty_word)
        
        # Create question
        question = self._create_question(pattern_type, scene_range)
        
        return Reflection(
            scene_range=scene_range,
            question=question,
            experience=experience,
            uncertainty=uncertainty_word,
            confidence_band=confidence
        )
    
    def _apply_uncertainty(self, template: str, uncertainty: str) -> str:
        """Apply uncertainty word to translation"""
        # Replace 'may' with appropriate uncertainty word
        if uncertainty == 'might':
            return template.replace(' may ', ' might ')
        elif uncertainty == 'could':
            return template.replace(
                ' may ',
                ', with lower confidence, could '
            ).replace(
                'may ', 
                'With lower confidence, the audience could '
            )
        return template
    
    def _create_question(self, pattern_type: str, scene_range: tuple) -> str:
        """Create question-first framing"""
        aspect_map = {
            'sustained_demand': 'sustained attention',
            'limited_recovery': 'intensity without breaks',
            'surprise_cluster': 'frequent shifts',
            'sequence_repetition': 'similarity to earlier sections',
            'constructive_strain': 'focused engagement',
            'degenerative_fatigue': 'attention drift'
        }
        
        aspect = aspect_map.get(pattern_type, 'experience')
        
        return f"Is this the level of {aspect} you want the audience to hold through scenes {scene_range[0]}-{scene_range[1]}?"
    
    def _create_intent_acknowledgment(self, suppressed: Dict) -> IntentAcknowledgment:
        """Create intent acknowledgment"""
        intent_ref = suppressed.get('intent_reference', {})
        label = intent_ref.get('label', 'intentional')
        scene_range = tuple(intent_ref.get('scene_range', [0, 0]))
        
        # Format label for display
        display_label = label.replace('_', ' ')
        
        acknowledgment = (
            f"You marked scenes {scene_range[0]}-{scene_range[1]} as {display_label}. "
            f"The signals here are consistent with that intent."
        )
        
        return IntentAcknowledgment(
            scene_range=scene_range,
            intent_label=label,
            acknowledgment=acknowledgment
        )
    
    def _determine_silence_reason(self, suppressed_count: int) -> str:
        """Determine why silence occurred"""
        if suppressed_count > 0:
            return SILENCE_EXPLANATIONS['intent_aligned']
        return SILENCE_EXPLANATIONS['stable']
    
    def _build_output(self) -> Dict:
        """Build final output"""
        return {
            'reflections': [r.to_dict() for r in self.reflections],
            'silence_explanation': self.silence_explanation,
            'intent_acknowledgments': [a.to_dict() for a in self.intent_acknowledgments]
        }


def validate_no_forbidden_language(output: Dict) -> bool:
    """Check output for forbidden language"""
    output_str = json.dumps(output).lower()
    
    for word in FORBIDDEN_WORDS:
        if word.lower() in output_str:
            return False
    return True


def mediate_experience(filtered_patterns_file: str) -> Dict:
    """
    Main entry point for experience mediation.
    
    Args:
        filtered_patterns_file: Path to filtered patterns JSON
        
    Returns:
        Writer-facing mediated output
    """
    # Load filtered patterns
    with open(filtered_patterns_file, 'r') as f:
        data = json.load(f)
    
    surfaced = data.get('surfaced_patterns', [])
    suppressed = data.get('suppressed_patterns', [])
    
    # Mediate
    mediator = ExperienceMediator()
    output = mediator.mediate(surfaced, suppressed)
    
    # Validate
    if not validate_no_forbidden_language(output):
        raise ValueError("Forbidden language detected in output")
    
    return output


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python mediator.py <filtered_patterns_json>")
        sys.exit(1)
    
    result = mediate_experience(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
