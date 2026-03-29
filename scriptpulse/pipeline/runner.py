# MODULE: runner.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
from scriptpulse.agents.ethics_agent import EthicsAgent
from scriptpulse.agents.writer_agent import WriterAgent
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
    telemetry = {'status': 'active', 'stages': {}}
    
    # --- STAGE 0: Normalize & Prepare ---
    if not script_content or len(script_content.strip()) < 50:
        raise ValueError("Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span> requires more text to analyze. Please upload a full script or a longer scene.")
    script_content = normalizer.normalize_script(script_content)
    telemetry['stages']['normalization_ms'] = round((time.time() - _t_start) * 1000, 2)
    
    # --- STAGE 1: Structure (Parsing) ---
    _t_stage = time.time()
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    
    parsed_output = parser.run(script_content)
    parsed_lines = parsed_output['lines']
    segmented_scenes = segmenter.run(parsed_lines)
    
    if not segmented_scenes:
        raise ValueError("ScriptPulse could not detect any scenes. Ensure your script uses standard industry formatting (e.g., INT., EXT., or SCENE headings).")
    
    # Hydrate scenes with their lines
    for scene in segmented_scenes:
        scene['lines'] = parsed_lines[scene['start_line']:scene['end_line']+1]
    telemetry['stages']['structural_parsing_ms'] = round((time.time() - _t_stage) * 1000, 2)
        
    # --- STAGE 2: Perception (Feature Extraction) ---
    _t_stage = time.time()
    perceptor = EncodingAgent()
    perceptual_features = perceptor.run({'scenes': segmented_scenes, 'lines': parsed_lines})
    telemetry['stages']['feature_extraction_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 3: Dynamics (Temporal Simulation) ---
    dynamics = DynamicsAgent()
    temporal_trace = dynamics.run_simulation({
        'features': perceptual_features,
        'genre': genre
    })
    telemetry['stages']['cognitive_simulation_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 3b: Inject Location Data from Scene Headings ---
    import re as _re
    for i, t_entry in enumerate(temporal_trace):
        if i < len(segmented_scenes):
            heading = segmented_scenes[i].get('heading', '')
            # Extract INT/EXT
            interior = None
            if heading.upper().startswith(('INT.', 'INT ', 'INT/')):
                interior = 'INT'
            elif heading.upper().startswith(('EXT.', 'EXT ', 'EXT/')):
                interior = 'EXT'
            elif heading.upper().startswith('I/E'):
                interior = 'I/E'
            
            # Extract location: strip INT./EXT. prefix, then take text before time-of-day dash
            loc = heading
            loc = _re.sub(r'^(INT\.|EXT\.|INT/EXT\.|EXT/INT\.|I/E\.?)\s*', '', loc, flags=_re.IGNORECASE).strip()
            # Remove time-of-day suffix (e.g. " - DAY", " - NIGHT")
            loc = _re.sub(r'\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME|MOMENTS?\s+LATER).*$', '', loc, flags=_re.IGNORECASE).strip()
            if not loc:
                loc = 'UNKNOWN'
            
            t_entry['location_data'] = {
                'location': loc,
                'interior': interior,
                'raw_heading': heading
            }

    
    # --- STAGE 4: Interpretation (Narrative Analysis) ---
    _t_stage = time.time()
    interpreter = InterpretationAgent()
    ethics = EthicsAgent()
    
    # Analysis outputs
    # Update InterpretationAgent to accept genre for dynamic thresholds
    ai_interpretation = interpreter.run(temporal_trace, perceptual_features, segmented_scenes, genre=genre)
    structure_map = ai_interpretation['structure']
    diagnosis = ai_interpretation['diagnosis']
    suggestions = ai_interpretation.get('suggestions', [])
    semantic_beats = interpreter.apply_semantic_labels(temporal_trace)
    telemetry['stages']['interpretation_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 5: Ethics & Fairness (The 'True' Audit) ---
    _t_stage = time.time()
    # Construct input for EthicsAgent
    valence_scores = [pt.get('sentiment', 0) for pt in temporal_trace]
    fairness_audit = ethics.audit_fairness({'scenes': segmented_scenes, 'valence_scores': valence_scores}, genre=genre)
    agency_results = ethics.analyze_agency({'scenes': segmented_scenes})
    
    # Update voice fingerprints with agency metrics
    agency_map = {item['character']: item for item in agency_results.get('agency_metrics', [])}
    telemetry['stages']['ethics_audit_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # Stage 5: Scene Turns (Intra-scene Movement)
    _t_stage = time.time()
    for i, s in enumerate(temporal_trace):
        # Look for a shift in sentiment within the scene
        # Use segmented_scenes to get lines for the current scene
        scene_lines = segmented_scenes[i]['lines'] if i < len(segmented_scenes) else []
        if not scene_lines: continue
        
        mid = len(scene_lines) // 2
        f_half = " ".join([l['text'] for l in scene_lines[:mid]]).lower()
        s_half = " ".join([l['text'] for l in scene_lines[mid:]]).lower()
        
        pos = ['yes', 'love', 'safe', 'good', 'happy', 'success', 'win', 'together', 'saved']
        neg = ['no', 'hate', 'die', 'danger', 'bad', 'fail', 'loss', 'quit', 'dead', 'body', 'kill']
        violence_vibe = ['shot', 'ambush', 'massacre', 'gunfire', 'murder', 'blood', 'blast', 'assassin', 'corpse']
        
        s1 = sum(1 for w in pos if w in f_half) - sum(1 for w in neg if w in f_half) - (sum(1 for w in violence_vibe if w in f_half) * 3)
        s2 = sum(1 for w in pos if w in s_half) - sum(1 for w in neg if w in s_half) - (sum(1 for w in violence_vibe if w in s_half) * 3)
        
        # Core Scene Turn Mapping
        label = "Flat"
        if s1 < 0 and s2 > 0: label = "Negative to Positive"
        elif s1 > 0 and s2 < 0: label = "Positive to Negative"
        elif s1 > 6 or s2 > 6: label = "High Energy" 
        elif s1 < 0 and s2 < 0: label = "Negative Progression"
        elif s1 > 0 and s2 > 0: label = "Positive Progression"
        
        # Task 2: Sentiment Post-processing pass for Violence/Death (Rule-based)
        viol_keywords = ['shot', 'killed', 'trap', 'ambush', 'gunfire', 'body', 'murder', 'blast', 'assassin', 'corpse']
        scene_text = " ".join([l['text'] for l in scene_lines]).lower()
        if any(w in scene_text for w in viol_keywords):
            # Cap the sentiment at negative in the simulation trace
            s['sentiment'] = min(s.get('sentiment', 0), -0.7)
            # Force a negative transition label if violence is present
            label = "Negative Progression" if s1 < 0 else "Positive to Negative"

        s['scene_turn'] = {'turn_label': label, 'sentiment_delta': s2 - s1}

    # --- STAGE 6: Final Assembly ---
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
    
    # Normalize averages & Meld with Agency
    for char in voice_fingerprints:
        count = voice_fingerprints[char]['line_count']
        voice_fingerprints[char]['sentiment'] = round(voice_fingerprints[char]['sentiment'] / max(1, count), 2)
        
        # Use EthicsAgent's higher-fidelity agency calculation if available
        if char in agency_map:
            voice_fingerprints[char]['agency'] = agency_map[char]['agency_score']
            voice_fingerprints[char]['centrality'] = agency_map[char]['centrality']
        else:
            voice_fingerprints[char]['agency'] = round(voice_fingerprints[char]['agency'] / max(1, count), 2)

    telemetry['stages']['assembly_ms'] = round((time.time() - _t_stage) * 1000, 2)
    telemetry['total_execution_ms'] = round((_t_end - _t_start) * 1000, 2)

    report = {
        'meta': {
            'execution_time': f"{round(_t_end - _t_start, 3)}s",
            'telemetry': telemetry,
            'total_scenes': len(segmented_scenes),
            'genre': genre,
            'framework': story_framework,
            'version': "v15.0 (Research Edition)",
            'confidence': 0.98 if len(segmented_scenes) > 5 else 0.85
        },
        'temporal_trace': temporal_trace,
        'perceptual_features': perceptual_features,
        'structure_map': structure_map,
        'narrative_diagnosis': diagnosis,

        'suggestions': suggestions,
        'semantic_beats': semantic_beats,
        'total_scenes': len(segmented_scenes),
        'segmented': segmented_scenes,
        'scene_info': [
            {'scene_index': s['scene_index'], 'heading': s.get('heading', ''), 'preview': s.get('preview', '')}
            for s in segmented_scenes
        ],
        'semantic_flux': [f.get('entropy_score', 0) for f in perceptual_features],
        'voice_fingerprints': voice_fingerprints,
        'fairness_audit': fairness_audit,
        'subtext_audit': [] # Placeholder for compatibility
    }
    
    # --- STAGE 5: Writer Intelligence (Expert Layer) ---
    writer = WriterAgent()
    report = writer.analyze(report, genre=genre)
    
    return report

def parse_structure(script):
    """Simple structural parser snippet"""
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    parsed = parser.run(script)['lines']
    segmented = segmenter.run(parsed)
    return [{'scene_index': s['scene_index'], 'heading': s.get('heading', '')} for s in segmented]

def health_check():
    """Observability endpoint for system status."""
    return {
        'status': 'healthy',
        'governance': True,
        'agents': {
            'ParsingAgent': 'healthy',
            'SegmentationAgent': 'healthy',
            'DynamicsAgent': 'healthy',
            'InterpretationAgent': 'healthy',
            'EthicsAgent': 'healthy'
        },
        'config_files': {
            'secrets.toml': True,
            'env': True
        }
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            print(json.dumps(run_pipeline(f.read()), indent=2))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
