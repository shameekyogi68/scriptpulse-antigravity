#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
from .agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation, acd, ssf, lrf
from . import lenses


def run_pipeline(screenplay_text, writer_intent=None, lens='viewer'):
    """
    Execute the full 7-agent pipeline.
    
    Args:
        screenplay_text: Raw screenplay text
        writer_intent: Optional list of writer intent declarations
        lens: Analysis lens ID ('viewer', 'reader', 'narrator')
        
    Returns:
        Final output from mediation agent with scene info
    """
    # Load lens config
    lens_config = lenses.get_lens(lens)
    
    # Agent 1: Structural Parsing
    parsed = parsing.run(screenplay_text)
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
    # Agent 3: Structural Encoding
    encoded = encoding.run({'scenes': segmented, 'lines': parsed})
    
    # Agent 4: Temporal Dynamics
    temporal_output = temporal.run({'features': encoded}, lens_config=lens_config)
    
    # === NEW: Agent 4.4: Long-Range Fatigue (LRF) ===
    # Refine signals with latent fatigue reserve
    temporal_output = lrf.run({
        'temporal_signals': temporal_output,
        'features': encoded
    })
    
    # === NEW: Agent 4.5: Attention Collapse vs Drift (ACD) ===
    acd_output = acd.run({
        'temporal_signals': temporal_output,
        'features': encoded
    })
    
    # Agent 5: Pattern Detection
    patterns_output = patterns.run({
        'temporal_signals': temporal_output,
        'features': encoded,
        'acd_states': acd_output # NEW: Pass ACD states
    })
    
    # Agent 6: Writer Intent & Immunity
    intent_input = {
        'patterns': patterns_output,
        'writer_intent': writer_intent or [],
        'acd_states': acd_output # Pass ACD to intent for potential filtering
    }
    filtered = intent.run(intent_input)
    
    # === NEW: Agent 6.5: Silence-as-Signal Formalization (SSF) ===
    # Analyze if silence is earned/stable
    ssf_output = ssf.run({
        'temporal_signals': temporal_output,
        'acd_states': acd_output,
        'surfaced_patterns': filtered['surfaced_patterns']
    })
    
    # Agent 7: Audience-Experience Mediation
    # Mediation needs ACD states and SSF analysis
    filtered['acd_states'] = acd_output 
    filtered['ssf_analysis'] = ssf_output # NEW
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
    
    # Add metadata
    final_output['meta'] = {
        'lens': lens_config['lens_id'],
        'lens_description': lens_config['description']
    }
    
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
