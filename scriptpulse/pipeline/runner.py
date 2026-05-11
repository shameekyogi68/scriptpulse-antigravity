# MODULE: runner.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#!/usr/bin/env python3
"""
Simplified ScriptPulse Runner - High Performance, Linear Pipeline
Designed for MCA Research Defense: Clear, Logical, and Deterministic
"""

from typing import Any
import time
import json
import uuid
from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.interpretation_agent import InterpretationAgent
from scriptpulse.agents.ethics_agent import EthicsAgent
from scriptpulse.agents.writer_agent import WriterAgent
from scriptpulse.agents.experimental_agent import CharacterVoiceDistinctionAgent
from scriptpulse.utils import normalizer, runtime
from scriptpulse.utils.confidence_scorer import ConfidenceScorer

def run_pipeline(script_content, genre='drama', story_framework='3_act', progress_callback=None, **kwargs):
    """
    Executes the 4-Stage ScriptPulse Research Pipeline.
    1. Structure (Parsing)
    2. Perception (Feature Extraction)
    3. Dynamics (Cognitive Simulation)
    4. Interpretation (Narrative Analysis)
    """
    
    _t_start = time.time()
    telemetry: dict[str, Any] = {'status': 'active', 'stages': {}}
    
    # --- STAGE 0: Normalize & Prepare ---
    if not script_content or len(script_content.strip()) < 50:
        raise ValueError(
            "ScriptPulse requires more text to analyze. "
            "Please upload a full script or a longer scene (minimum ~50 words)."
        )
    
    # Security: Input size limits and sanitization
    MAX_CHARS = 500_000  # ~500KB, approx 400-page script
    if len(script_content) > MAX_CHARS:
        raise ValueError(
            f"Script too large ({len(script_content):,} chars). "
            f"Maximum is {MAX_CHARS:,} characters (~400 pages)."
        )
    
    # Sanitize input: strip null bytes and control characters
    script_content = ''.join(char for char in script_content if ord(char) >= 32 or char in '\n\r\t')
    
    script_content = normalizer.normalize_script(script_content)
    telemetry['stages']['normalization_ms'] = round((time.time() - _t_start) * 1000, 2)
    
    # --- STAGE 1: Structure (Parsing) ---
    if progress_callback:
        progress_callback("Parsing structure...", 25)
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
    if progress_callback:
        progress_callback("Extracting features...", 45)
    _t_stage = time.time()
    encoder = EncodingAgent()
    perceptual_features = encoder.run({'scenes': segmented_scenes, 'lines': parsed_lines})
    telemetry['stages']['feature_extraction_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 3: Dynamics (Temporal Simulation) ---
    if progress_callback:
        progress_callback("Simulating dynamics...", 55)
    _t_stage = time.time()
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

    
    # --- STAGE 4: Interpretation (Cognitive Translation) ---
    _t_stage = time.time()
    if progress_callback:
        progress_callback("Running interpretation...", 65)
    interpreter = InterpretationAgent()
    
    # Auto-detect only when explicitly requested. A user-selected Drama genre is valid.
    auto_detect_genre = kwargs.get('auto_detect_genre', False)
    if not genre:
        genre = 'drama'
    if auto_detect_genre or str(genre).lower() in ['auto', 'detect', 'auto-detect']:
        detected_genre = interpreter.detect_genre(temporal_trace, perceptual_features)
        if detected_genre != 'drama':
            genre = detected_genre
    
    ai_interpretation = interpreter.run(temporal_trace, perceptual_features, segmented_scenes, genre=genre)
    structure_map = ai_interpretation['structure']
    diagnosis = ai_interpretation['diagnosis']
    suggestions = ai_interpretation.get('suggestions', [])
    semantic_beats = interpreter.apply_semantic_labels(temporal_trace)
    telemetry['stages']['interpretation_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 5: Ethics & Fairness (The 'True' Audit) ---
    _t_stage = time.time()
    # Construct input for EthicsAgent
    ethics = EthicsAgent()
    valence_scores = [pt.get('sentiment', 0) for pt in temporal_trace]
    fairness_audit = ethics.audit_fairness({'scenes': segmented_scenes, 'valence_scores': valence_scores}, genre=genre)
    agency_results = ethics.analyze_agency({'scenes': segmented_scenes})
    
    # Update voice fingerprints with agency metrics
    agency_map = {}
    for item in agency_results.get('agency_metrics', []):
        if isinstance(item, dict) and 'character' in item:
            agency_map[item['character']] = item
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
        
        violence_override = False
        if any(w in scene_text for w in viol_keywords):
            violence_override = True
            # Force a negative transition label if violence is present
            label = "Negative Progression" if s1 < 0 else "Positive to Negative"

        s['scene_turn'] = {
            'turn_label': label, 
            'sentiment_delta': s2 - s1, 
            'violence_override': violence_override
        }

    # --- STAGE 6: Final Assembly ---
    _t_end = time.time()
    _t_stage = time.time()  # Reset timer specifically for assembly measurement
    
    # Aggregate Voice Fingerprints (Cumulative) + collect dialogue samples
    voice_fingerprints = {}
    char_dialogue_samples = {}  # For CharacterVoiceDistinctionAgent
    for f in perceptual_features:
        for char, v in f.get('character_scene_vectors', {}).items():
            if char not in voice_fingerprints:
                voice_fingerprints[char] = {'agency': 0, 'sentiment': 0, 'line_count': 0, 'dialogue_samples': []}
                char_dialogue_samples[char] = []
            voice_fingerprints[char]['line_count'] += v['line_count']
            voice_fingerprints[char]['agency'] += v['agency']
            voice_fingerprints[char]['sentiment'] += v['sentiment']
        # Collect raw dialogue lines per character from micro_structure
        for line in f.get('micro_structure', []):
            if line.get('tag') == 'D' and line.get('speaker'):
                spk = line['speaker']
                txt = line.get('text', '').strip()
                if spk in char_dialogue_samples and txt and len(txt) > 5:
                    if len(char_dialogue_samples[spk]) < 40:  # Cap at 40 samples per char
                        char_dialogue_samples[spk].append(txt)
    
    # Normalize averages & Meld with Agency
    for char in voice_fingerprints:
        count = voice_fingerprints[char]['line_count']
        voice_fingerprints[char]['sentiment'] = round(voice_fingerprints[char]['sentiment'] / max(1, count), 2)
        voice_fingerprints[char]['dialogue_samples'] = char_dialogue_samples.get(char, [])
        
        # Use EthicsAgent's higher-fidelity agency calculation if available
        if char in agency_map and isinstance(agency_map[char], dict):
            agency_data = agency_map[char]
            voice_fingerprints[char]['agency'] = agency_data.get('agency_score', voice_fingerprints[char]['agency'])
            voice_fingerprints[char]['centrality'] = agency_data.get('centrality', 0)
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
            'confidence': 0.85,  # Will be updated below with proper calculation
            'run_id': str(uuid.uuid4()),
            'agent_timings': telemetry['stages']
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
        'subtext_audit': [], # Placeholder for compatibility
        # Ensure standard output keys are always present
        'parsed_lines': parsed_lines,
        'patterns': [],
        'features': perceptual_features,
        'trace': temporal_trace,
        'agency_analysis': agency_results
    }
    
    # --- STAGE 5: Writer Intelligence (Expert Layer) ---
    if progress_callback:
        progress_callback("Generating insights...", 75)
    writer = WriterAgent()
    report = writer.analyze(report, genre=genre)
    
    # --- STAGE 5b: Character Voice Distinction (Unique AI Feature) ---
    try:
        voice_agent = CharacterVoiceDistinctionAgent()
        voice_report = voice_agent.analyze(voice_fingerprints)
        report['voice_distinction_report'] = voice_report
        # Inject standout finding into writer_intelligence diagnostics if available
        if voice_report.get('flagged_pairs') and 'writer_intelligence' in report:
            for flagged in voice_report['flagged_pairs'][:2]:
                diag_msg = (
                    f"🎭 **Voice Similarity ({flagged['pair']})**: "
                    f"{flagged['severity']} — {flagged['advice']}"
                )
                report['writer_intelligence']['narrative_diagnosis'].insert(0, diag_msg)
    except Exception as e:
        import logging
        logging.warning("CharacterVoiceDistinctionAgent failed gracefully: %s", e)
        report['voice_distinction_report'] = {'method': 'Error', 'voice_diversity_index': None}
    
    # --- STAGE 6: Calculate Confidence Score ---
    scorer = ConfidenceScorer()
    confidence_result = scorer.calculate(temporal_trace)
    report['meta']['confidence'] = confidence_result['score']
    report['meta']['confidence_level'] = confidence_result['level']
    report['meta']['confidence_reasons'] = confidence_result['reasons']
    
    # Surface confidence in writer_intelligence for UI transparency
    if 'writer_intelligence' in report:
        report['writer_intelligence']['analysis_confidence'] = {
            'score': confidence_result['score'],
            'level': confidence_result['level'],
            'reasons': confidence_result['reasons'],
            'interpretation': (
                'High confidence: sufficient scene data, strong signal variance.' if confidence_result['level'] == 'HIGH'
                else 'Medium confidence: some results may be imprecise on shorter scripts.'
                if confidence_result['level'] == 'MEDIUM'
                else 'Low confidence: script is too short or too uniform for reliable analysis.'
            )
        }
    
    # Validate against Pydantic schema for type safety
    try:
        from scriptpulse.schemas.models import PipelineOutput
        validated = PipelineOutput(**report)
        return validated.model_dump()
    except Exception as e:
        import logging
        logging.warning(f"Schema validation warning: {e}")
        return report  # Graceful degradation

def parse_structure(script):
    """Simple structural parser snippet"""
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    parsed = parser.run(script)['lines']
    segmented = segmenter.run(parsed)
    return [{'scene_index': s['scene_index'], 'heading': s.get('heading', '')} for s in segmented]

def health_check():
    """Observability endpoint for system status."""
    import os
    status = {'status': 'healthy', 'agents': {}, 'config_files': {}}
    
    # Test agent imports
    agents_to_test = [
        ('ParsingAgent', 'scriptpulse.agents.structure_agent', 'ParsingAgent'),
        ('SegmentationAgent', 'scriptpulse.agents.structure_agent', 'SegmentationAgent'),
        ('DynamicsAgent', 'scriptpulse.agents.dynamics_agent', 'DynamicsAgent'),
        ('InterpretationAgent', 'scriptpulse.agents.interpretation_agent', 'InterpretationAgent'),
        ('EthicsAgent', 'scriptpulse.agents.ethics_agent', 'EthicsAgent')
    ]
    
    for name, module, class_name in agents_to_test:
        try:
            mod = __import__(module, fromlist=[class_name])
            agent_class = getattr(mod, class_name)
            agent_instance = agent_class()
            status['agents'][name] = 'healthy'
        except Exception as e:
            status['agents'][name] = f'ERROR: {e}'
            status['status'] = 'degraded'
    
    # Test config files
    config_files_to_check = [
        'scriptpulse/config/genre_priors.json',
        'scriptpulse/config/required_model_versions.json',
        '.env.example',
        'requirements.txt'
    ]
    
    for config_file in config_files_to_check:
        status['config_files'][config_file] = os.path.exists(config_file)
    
    return status

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            print(json.dumps(run_pipeline(f.read()), indent=2))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
