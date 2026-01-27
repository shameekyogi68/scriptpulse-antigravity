#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
from .agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation


def run_pipeline(screenplay_text, writer_intent=None):
    """
    Execute the full 7-agent pipeline.
    
    Args:
        screenplay_text: Raw screenplay text
        writer_intent: Optional list of writer intent declarations
        
    Returns:
        Final output from mediation agent with scene info
    """
    # Agent 1: Structural Parsing
    parsed = parsing.run(screenplay_text)
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
    # Agent 3: Structural Encoding
    encoded = encoding.run({'scenes': segmented, 'lines': parsed})
    
    # Agent 4: Temporal Dynamics
    temporal_output = temporal.run({'features': encoded})
    
    # Agent 5: Pattern Detection
    patterns_output = patterns.run({
        'temporal_signals': temporal_output,
        'features': encoded  # NEW: pass features for functional differentiation
    })
    
    # Agent 6: Writer Intent & Immunity
    intent_input = {
        'patterns': patterns_output,
        'writer_intent': writer_intent or []
    }
    filtered = intent.run(intent_input)
    
    # Agent 7: Audience-Experience Mediation
    final_output = mediation.run(filtered)
    
    # Add scene info for UI visualization
    final_output['scene_info'] = [
        {
            'scene_index': scene['scene_index'],
            'heading': scene.get('heading', f"Scene {scene['scene_index'] + 1}"),
            'preview': scene.get('preview', '')
        }
        for scene in segmented
    ]
    final_output['total_scenes'] = len(segmented)
    
    return final_output


def main():
    if len(sys.argv) != 2:
        print("Usage: python runner.py <screenplay_file>")
        sys.exit(1)
    
    screenplay_file = sys.argv[1]
    
    # Load screenplay
    with open(screenplay_file, 'r') as f:
        screenplay_text = f.read()
    
    # Run pipeline
    result = run_pipeline(screenplay_text)
    
    # Print result
    import json
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
