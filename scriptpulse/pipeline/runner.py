#!/usr/bin/env python3
"""
Simplified ScriptPulse Runner - High Performance, Linear Pipeline
Designed for MCA Research Defense: Clear, Logical, and Deterministic
"""

import time
import json
from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.interpretation_agent import InterpretationAgent
from scriptpulse.utils import normalizer, runtime

def run_pipeline(script_content, genre='drama', story_framework='3_act', **kwargs):
    """
    Executes the 4-Stage ScriptPulse Research Pipeline.
    1. Structure (Parsing)
    2. Perception (Feature Extraction)
    3. Dynamics (Cognitive Simulation)
    4. Interpretation (Narrative Analysis)
    """
    
    _t_start = time.time()
    
    # --- STAGE 0: Normalize & Prepare ---
    script_content = normalizer.normalize_script(script_content)
    
    # --- STAGE 1: Structure (Parsing) ---
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    
    parsed_output = parser.run(script_content)
    parsed_lines = parsed_output['lines']
    segmented_scenes = segmenter.run(parsed_lines)
    
    # Hydrate scenes with their lines
    for scene in segmented_scenes:
        scene['lines'] = parsed_lines[scene['start_line']:scene['end_line']+1]
        
    # --- STAGE 2: Perception (Feature Extraction) ---
    perceptor = EncodingAgent()
    perceptual_features = perceptor.run({'scenes': segmented_scenes, 'lines': parsed_lines})
    
    # --- STAGE 3: Dynamics (Temporal Simulation) ---
    dynamics = DynamicsAgent()
    temporal_trace = dynamics.run_simulation({
        'features': perceptual_features,
        'genre': genre
    })
    
    # --- STAGE 4: Interpretation (Narrative Analysis) ---
    interpreter = InterpretationAgent()
    
    # Analysis outputs
    structure_map = interpreter.map_to_structure(temporal_trace)
    diagnosis = interpreter.diagnose_patterns(temporal_trace, perceptual_features)
    suggestions = interpreter.generate_suggestions(temporal_trace)
    semantic_beats = interpreter.apply_semantic_labels(temporal_trace)
    
    # --- Final Report Assembly ---
    _t_end = time.time()
    
    # Aggregate Voice Fingerprints (Cumulative)
    voice_fingerprints = {}
    for f in perceptual_features:
        for char, v in f.get('character_scene_vectors', {}).items():
            if char not in voice_fingerprints:
                voice_fingerprints[char] = {'agency': 0, 'sentiment': 0, 'line_count': 0}
            voice_fingerprints[char]['line_count'] += v['line_count']
            voice_fingerprints[char]['agency'] += v['agency']
            voice_fingerprints[char]['sentiment'] += v['sentiment']
    
    # Normalize averages
    for char in voice_fingerprints:
        count = voice_fingerprints[char]['line_count']
        voice_fingerprints[char]['agency'] = round(voice_fingerprints[char]['agency'] / max(1, count), 2)
        voice_fingerprints[char]['sentiment'] = round(voice_fingerprints[char]['sentiment'] / max(1, count), 2)

    report = {
        'meta': {
            'execution_time': f"{round(_t_end - _t_start, 3)}s",
            'total_scenes': len(segmented_scenes),
            'genre': genre,
            'framework': story_framework,
            'version': "v15.0 (Simplified)"
        },
        'temporal_trace': temporal_trace,
        'perceptual_features': perceptual_features,
        'structure_map': structure_map,
        'narrative_diagnosis': diagnosis,
        'suggestions': suggestions,
        'semantic_beats': semantic_beats,
        'segmented': segmented_scenes,
        'scene_info': [
            {'scene_index': s['scene_index'], 'heading': s.get('heading', ''), 'preview': s.get('preview', '')}
            for s in segmented_scenes
        ],
        'semantic_flux': [f.get('entropy_score', 0) for f in perceptual_features],
        'voice_fingerprints': voice_fingerprints,
        'subtext_audit': [] # Placeholder for compatibility
    }
    
    # Add high-level intelligence for Writer View
    mid_scene = structure_map['beats'][1]['scene_index'] if len(structure_map['beats']) > 1 else 0
    ii_scene = structure_map['beats'][0]['scene_index'] if len(structure_map['beats']) > 0 else 0

    # Convert interpretation_agent diagnosis (dicts) to clean readable strings
    clean_diagnosis = []
    for d in diagnosis:
        if isinstance(d, dict):
            dtype = d.get('type', 'Info')
            issue = d.get('issue', '')
            advice = d.get('advice', '')
            if dtype == 'Critical':
                clean_diagnosis.append(f"🔴 **{issue}**: {advice}")
            elif dtype == 'Warning':
                clean_diagnosis.append(f"🟠 **{issue}**: {advice}")
            elif dtype == 'Insight':
                clean_diagnosis.append(f"💡 **{issue}**: {advice}")
            else:
                clean_diagnosis.append(f"🟢 **{issue}**: {advice}")
        else:
            clean_diagnosis.append(str(d))

    # Calculate Stakes Distribution (derived from semantics)
    physical, emotional, social, moral, existential = 0, 0, 0, 0, 0
    cut_candidates = []
    
    for i, (feat, trace) in enumerate(zip(perceptual_features, temporal_trace)):
        comp = feat.get('affective_load', {}).get('compound', 0)
        action = feat.get('visual_abstraction', {}).get('action_lines', 0)
        tension = trace.get('attentional_signal', 0)
        
        if action > 8: physical += 1
        elif comp > 0.5 or comp < -0.5: emotional += 1
        elif tension > 0.6: moral += 1
        else: social += 1
        
        # Detect Cut Candidates: High word count (entropy) but low tension
        if feat.get('entropy_score', 0) > 4.5 and tension < 0.35:
            cut_candidates.append(trace['scene_index'])

    total_stakes = max(1, physical + emotional + social + moral + existential)

    report['writer_intelligence'] = {
        'structural_dashboard': {
            'runtime_estimate': runtime.estimate_runtime(segmented_scenes),
            'midpoint_status': "Healthy" if mid_scene > 0 else "Sagging",
            'structural_turning_points': {
                'inciting_incident': {'scene': ii_scene},
                'midpoint': {'scene': mid_scene},
                'act2_break': {'scene': int(len(segmented_scenes) * 0.75)}
            },
            'stakes_distribution': {
                'Physical': round(physical/total_stakes, 2),
                'Emotional': round(emotional/total_stakes, 2),
                'Social': round(social/total_stakes, 2),
                'Moral': round(moral/total_stakes, 2),
                'Existential': round(existential/total_stakes, 2)
            },
            'scene_economy_map': {
                'cut_candidates': cut_candidates[:3] # Top 3 worst offenders
            }
        },
        'narrative_diagnosis': clean_diagnosis
    }
    
    return report

def parse_structure(script):
    """Simple structural parser snippet"""
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    parsed = parser.run(script)['lines']
    segmented = segmenter.run(parsed)
    return [{'scene_index': s['scene_index'], 'heading': s.get('heading', '')} for s in segmented]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            print(json.dumps(run_pipeline(f.read()), indent=2))
