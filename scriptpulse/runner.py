#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
import random
from .agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation, acd, ssf, lrf, semantic, syntax, xai, imagery, social, valence, profiler, coherence, beat, fairness, suggestion
from . import lenses, fingerprint, governance


def run_pipeline(screenplay_text, writer_intent=None, lens='viewer', genre='drama', audience_profile='general', high_res_mode=False):
    """
    Execute the full pipeline with Research Layers (v7.0).
    
    Args:
        screenplay_text: Raw screenplay text
        writer_intent: Optional list of writer intent declarations
        lens: Analysis lens ID
        genre: Genre context for adaptive thresholds ('thriller', 'comedy', etc.)
        audience_profile: 'general', 'cinephile', 'distracted', 'child'
        high_res_mode: If True, sub-segments scenes into beats (HD Analysis).
    """
    # === GPBL: Governance Check ===
    governance.validate_request(screenplay_text)
    
    # Load lens config
    lens_config = lenses.get_lens(lens)
    
    # Agent 1: Structural Parsing
    parsed = parsing.run(screenplay_text)
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
    # Hydrate scenes with lines (Data Unification)
    for scene in segmented:
        start = scene['start_line']
        end = scene['end_line']
        scene['lines'] = parsed[start:end+1]
    
    # === SFE: Structural Fingerprint ===
    struct_fingerprint = fingerprint.generate_structural_fingerprint(parsed, segmented)
    
    # === DRL: Deterministic Run ID ===
    lens_id = lens if lens else 'viewer'
    run_id, version = fingerprint.generate_run_id(struct_fingerprint, lens_id, writer_intent)
    
    # === REPRODUCIBILITY LOCK ===
    random.seed(int(run_id[:16], 16))
    
    # === Agent 2.5: Beat Pacing (v7.0 Micro-Segmentation) ===
    if high_res_mode:
        segmented = beat.subdivide_into_beats(segmented)
    
    # === Agent 3: Creative Encoding (Semantic Features) ===
    encoded = encoding.run({'scenes': segmented})
    
    # === Agent 3.5: Research Layers (Semantic & Syntax) ===
    semantic_scores = semantic.run({'scenes': segmented})
    syntax_scores = syntax.run({'scenes': segmented}) # NEW v6.1
    
    # === NEW: Agent 3.6: Cinematic & Social Layers (v6.4) ===
    visual_scores = imagery.run({'scenes': segmented})
    social_scores = social.run({'scenes': segmented})
    
    # === NEW: Agent 3.7: Affective Valence (v6.5) ===
    valence_scores = valence.run({'scenes': segmented})
    
    # === NEW: Agent 3.8: Cognitive Profiling & Coherence (v6.6) ===
    # Get Profile Params (lambda, beta, threshold)
    profile_params = profiler.get_profile(audience_profile)
    # Get Disorientation Penalty
    coherence_scores = coherence.run({'scenes': segmented})

    # Agent 4: Temporal Dynamics (with MRCS)
    temporal_output = temporal.simulate_consensus(
        {
            'features': encoded, 
            'semantic_scores': semantic_scores,
            'syntax_scores': syntax_scores, 
            'visual_scores': visual_scores, 
            'social_scores': social_scores, 
            'valence_scores': valence_scores,
            'coherence_scores': coherence_scores # NEW v6.6
        }, 
        lens_config=lens_config,
        genre=genre,
        profile_params=profile_params, # NEW v6.6
        iterations=5
    )
    
    # === NEW: Agent 4.5: XAI Decomposition (Research Layer) ===
    # Explains the "Why" behind the effort
    xai_data = xai.run({
        'features': encoded,
        'semantic_scores': semantic_scores,
        'syntax_scores': syntax_scores
    }, lens_config=lens_config)
    
    # === NEW: Macro-Structure Alignment (Research Layer) ===
    # Compare against canonical narratives (Freytag, etc.)
    try:
        from research import templates
        pulse_trace = [s['attentional_signal'] for s in temporal_output]
        macro_fidelity = templates.analyze_fidelity(pulse_trace)
    except ImportError:
        # Fallback if research module is missing (e.g. slight path issue)
        macro_fidelity = {'best_match': 'N/A', 'fidelity_score': 0.0}
    
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
    
    # === NEW: Agent 8.0: Ethical & Generative Layers ===
    fairness_audit = fairness.run({
        'scenes': segmented, 
        'valence_scores': valence_scores
    })
    
    suggestions = suggestion.run(temporal_output)
    
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
    
    # Add Enterprise Audit Metadata
    final_output['meta'] = {
        'run_id': run_id,
        'fingerprint': struct_fingerprint,
        'version': version,
        'lens': lens_id
    }
    
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
    
    # Add temporal trace for visualization
    final_output['temporal_trace'] = temporal_output
    
    # Add XAI Data (v6.2)
    final_output['xai_attribution'] = xai_data
    
    # Add Macro Structure Data (v6.2)
    final_output['macro_structure_fidelity'] = macro_fidelity
    
    # Add Ethics & Generative Data (v8.0)
    final_output['fairness_audit'] = fairness_audit
    final_output['suggestions'] = suggestions
    
    # Add metadata
    final_output['meta'].update({
        'lens': lens_config['lens_id'],
        'lens_description': lens_config['description']
    })
    
    return final_output


def parse_structure(screenplay_text):
    """
    Helper to parse structure without running full analysis.
    Used for UI Scene Picker population.
    """
    # Agent 1: Structural Parsing
    parsed = parsing.run(screenplay_text)
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
    return [
        {
            'scene_index': s['scene_index'], 
            'heading': s.get('heading', f"Scene {s['scene_index']}")
        }
        for s in segmented
    ]



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
