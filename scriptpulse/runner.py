#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
from agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation


def run_pipeline(screenplay_text):
    """
    Execute the full 7-agent pipeline.
    
    Args:
        screenplay_text: Raw screenplay text
        
    Returns:
        Final output from mediation agent
    """
    # Agent 1: Structural Parsing
    parsed = parsing.run(screenplay_text)
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
    # Agent 3: Structural Encoding
    encoded = encoding.run(segmented)
    
    # Agent 4: Temporal Dynamics
    temporal_output = temporal.run(encoded)
    
    # Agent 5: Pattern Detection
    patterns_output = patterns.run(temporal_output)
    
    # Agent 6: Writer Intent & Immunity
    filtered = intent.run(patterns_output)
    
    # Agent 7: Audience-Experience Mediation
    final_output = mediation.run(filtered)
    
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
