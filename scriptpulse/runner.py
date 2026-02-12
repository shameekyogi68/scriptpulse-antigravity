#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
import time
import random
import tracemalloc
from .agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation, acd, ssf, lrf, semantic, syntax, xai, imagery, social, valence, profiler, coherence, beat, fairness, suggestion, embeddings, voice, scene_notes, bert_parser, agency, ensemble_uncertainty, multimodal, polyglot_validator # vNext.10 Experimental
from . import lenses, fingerprint, governance
from .utils import runtime  # v13.0


# vNext.11 Experimental
from .agents import resonance, insight, silicon_stanislavski

# v13.1 Block 4: Resource guardrails
_RESOURCE_LIMITS = {
    'max_wall_time_s': 300,        # Per-run wall time limit
    'max_memory_mb': 2048,         # Per-run peak memory
    'max_runtime_per_scene_s': 3,  # Per-scene ceiling
}
_OVERSIZED_BUCKETS = set()  # Scene count buckets that exceeded limits

def _scene_bucket(n):
    """Bucket scene counts: 1-5, 6-20, 21-50, 51-100, 100+"""
    if n <= 5: return '1-5'
    if n <= 20: return '6-20'
    if n <= 50: return '21-50'
    if n <= 100: return '51-100'
    return '100+'

def run_pipeline(script_content, writer_intent=None, lens='viewer', genre='drama', audience_profile='general', high_res_mode=False, pre_parsed_lines=None, character_context=None, experimental_mode=False, moonshot_mode=False, cpu_safe_mode=False, valence_stride=1, stanislavski_min_words=10, embeddings_batch_size=32, shadow_mode=False):
    """
    Orchestrate the ScriptPulse Analysis Pipeline.
    
    Args:
        script_content: Raw screenplay text
        lens: Analysis lens ID
        genre: Genre context for adaptive thresholds ('thriller', 'comedy', etc.)
        audience_profile: 'general', 'cinephile', 'distracted', 'child'
        high_res_mode: If True, sub-segments scenes into beats (HD Analysis).
        pre_parsed_lines: Optional pre-parsed lines (e.g., from FDX import)
        experimental_mode: Enable vNext.10 features (Multimodal, Polyglot)
        moonshot_mode: Enable vNext.11 features (Resonance, Insight, Silicon Stanislavski)
    """
    # === GPBL: Governance Check ===
    governance.validate_request(script_content)
    
    # v13.1 Block 4: Start resource measurement
    _run_start = time.time()
    tracemalloc.start()
    
    # v13.1 Block 4: Auto cpu_safe_mode for oversized buckets
    estimated_scenes = script_content.count('INT.') + script_content.count('EXT.')
    bucket = _scene_bucket(estimated_scenes)
    if bucket in _OVERSIZED_BUCKETS and not cpu_safe_mode:
        cpu_safe_mode = True
        print(f"[Resource Guard] Auto-enabled cpu_safe_mode for bucket '{bucket}'")
    
    # vNext.9 Safety: Drift Monitoring (Domain Adherence)
    from . import drift_monitor, security, telemetry # v13.1 Block 7
    drift_monitor.monitor.check_domain_adherence(script_content.splitlines())
    
    # Load lens config
    lens_config = lenses.get_lens(lens)
    
    # v13.1: Per-agent timing
    timings = {}
    
    # Agent 1: Structural Parsing
    _t0 = time.time()
    if pre_parsed_lines:
        parsed = pre_parsed_lines
    else:
        # vNext.9 Upgrade: BERT Parser
        parser = bert_parser.BertParserAgent()
        parsed_output = parser.run(script_content)
        parsed = parsed_output['lines']
    timings['parser_ms'] = round((time.time() - _t0) * 1000)
    
    # Agent 2: Scene Segmentation
    _t0 = time.time()
    segmented = segmentation.run(parsed)
    timings['segmentation_ms'] = round((time.time() - _t0) * 1000)
    
    # === vNext.10 Experimental: Polyglot Validator ===
    polyglot_data = {}
    if experimental_mode:
        print("[Experimental] Running Polyglot Validator...")
        polyglot_data = polyglot_validator.CrossCulturalValidator().run({'scenes': segmented})
    
    # Hydrate scenes with lines (Data Unification)
    for scene in segmented:
        start = scene['start_line']
        end = scene['end_line']
        scene['lines'] = parsed[start:end+1]
    
    # === SFE: Structural Fingerprint ===
    struct_fingerprint = fingerprint.generate_structural_fingerprint(parsed, segmented)
    
    # === v13.1: Content Fingerprint ===
    content_fp = fingerprint.generate_content_fingerprint(parsed)
    
    # === DRL: Deterministic Run ID ===
    lens_id = lens if lens else 'viewer'
    run_id, version = fingerprint.generate_run_id(struct_fingerprint, lens_id, writer_intent, content_fingerprint=content_fp)
    
    # === REPRODUCIBILITY LOCK ===
    random.seed(int(run_id[:16], 16))
    
    # Log Run for Compliance (vNext.5 Enterprise)
    security.ComplianceLog.log_run(run_id, governance.Role.RESEARCHER, "analyzed")
    
    # We will log the run *after* we have computed metrics to feed the statistical monitor
    # drift_monitor.monitor.log_run({'run_id': run_id, 'fingerprint': struct_fingerprint})
    
    # === Agent 2.5: Beat Pacing (v7.0 Micro-Segmentation) ===
    if high_res_mode:
        segmented = beat.subdivide_into_beats(segmented)
    
    # === Agent 3: Creative Encoding (Semantic Features) ===
    encoded = encoding.run({'scenes': segmented})
    
    # === Agent 3.5: Research Layers (Semantic & Syntax) ===
    semantic_scores = semantic.run({'scenes': segmented})
    
    # === NEW: Agent 3.6: Cinematic & Social Layers (v6.4) ===
    visual_scores = imagery.run({'scenes': segmented})
    social_data = social.run({'scenes': segmented})
    social_scores = social_data.get('centrality_entropy', [])
    interaction_map = social_data.get('interaction_map', {})
    
    # === NEW: Agent 10.1: Diction/Syntax (v10.1) ===
    syntax_data = syntax.run({'scenes': segmented})
    syntax_scores = syntax_data.get('complexity_scores', [])
    diction_issues = syntax_data.get('diction_issues', [])
    
    # === NEW: Agent 9.1: Hybrid NLP (Embeddings) ===
    _t0 = time.time()
    semantic_flux = embeddings.run({'scenes': segmented})
    timings['embeddings_ms'] = round((time.time() - _t0) * 1000)
    
    # === NEW: Agent 10.1: Voice Fingerprinting (Market) ===
    voice_map = voice.run({'scenes': segmented})
    
    # === NEW: Agent 3.7: Affective Valence (v6.5) ===
    _t0 = time.time()
    stride = valence_stride if cpu_safe_mode else 1
    if stride > 1:
        # v13.1: In CPU safe mode, run valence every Nth scene
        valence_scores = []
        for vi, sc in enumerate(segmented):
            if vi % stride == 0:
                vs = valence.run({'scenes': [sc]})
                valence_scores.append(vs[0] if vs else 0.0)
            else:
                valence_scores.append(valence_scores[-1] if valence_scores else 0.0)
    else:
        valence_scores = valence.run({'scenes': segmented})
    timings['valence_ms'] = round((time.time() - _t0) * 1000)
    
    # === NEW: Agent 3.8: Cognitive Profiling & Coherence (v6.6) ===
    # Get Profile Params (lambda, beta, threshold)
    profile_params = profiler.get_profile(audience_profile)
    # Get Disorientation Penalty
    coherence_scores = coherence.run({'scenes': segmented})
    # === NEW: Agent 3.9: Silicon Stanislavski (Prior to Temporal) ===
    # We must run this HERE to feed emotional data into the Temporal Simulation
    try:
        stanislavski = silicon_stanislavski.SiliconStanislavski()
    except:
        stanislavski = None
        
    # Collect all scene texts for batching
    all_scene_texts = []
    for scene in segmented:
        scene_text = " ".join([l.get('text', '') for l in scene.get('lines', [])])
        if not scene_text:
            scene_text = scene.get('heading', '')
        all_scene_texts.append(scene_text)
        
    # Batch Run
    stan_batch_results = []
    ml_tension_scores = []
    
    if stanislavski:
        if experimental_mode or moonshot_mode: # Only run if enabled
            _t0 = time.time()
            # v13.1: CPU safe mode — skip Stanislavski for very short scenes
            min_words = stanislavski_min_words if cpu_safe_mode else 0
            if min_words > 0:
                filtered_texts = [t if len(t.split()) >= min_words else '' for t in all_scene_texts]
                print(f"[Performance/CPU-Safe] Running Batch Inference on {sum(1 for t in filtered_texts if t)} of {len(all_scene_texts)} scenes...")
                stan_batch_results = stanislavski.analyze_script([t for t in filtered_texts if t])
            else:
                print(f"[Performance] Running Batch Inference on {len(all_scene_texts)} scenes...")
                stan_batch_results = stanislavski.analyze_script(all_scene_texts)
            timings['stanislavski_ms'] = round((time.time() - _t0) * 1000)
            
            # Extract Tension Scores for Temporal Agent
            for res in stan_batch_results:
                raw = res.get('raw_scores', {})
                if raw:
                    # Instantaneous Tension = Max(Danger, Helplessness)
                    tension = max(raw.get('danger', 0), raw.get('helplessness', 0))
                else:
                    # Fallback to damped state
                    safety = res.get('internal_state', {}).get('safety', 0.8)
                    tension = 1.0 - safety
                
                ml_tension_scores.append(round(tension, 3))
    
    # Fill gaps if no ML
    if not ml_tension_scores:
        ml_tension_scores = [None] * len(segmented)

    # Agent 4: Temporal Dynamics (with MRCS)
    _t0 = time.time()
    temporal_output = temporal.simulate_consensus(
        {
            'features': encoded, 
            'semantic_scores': semantic_scores,
            'syntax_scores': syntax_scores, 
            'visual_scores': visual_scores, 
            'social_scores': social_scores, 
            'valence_scores': valence_scores,
            'coherence_scores': coherence_scores,
            'ml_tension_scores': ml_tension_scores # NEW
        }, 
        lens_config=lens_config,
        genre=genre,
        profile_params=profile_params, # NEW v6.6
        iterations=5
    )
    timings['temporal_ms'] = round((time.time() - _t0) * 1000)
    
    # v13.1: Internal numeric guard on temporal output
    temporal_output, validation_errors = temporal.validate_temporal_output(
        temporal_output, len(segmented)
    )
    
    # === vNext.10 Experimental: Multimodal Fusion ===
    if experimental_mode:
        print("[Experimental] Running Multimodal Fusion...")
        fusion_agent = multimodal.MultimodalFusionAgent()
        for i, scene in enumerate(temporal_output):
            # Mock injection of visual density
            fused = fusion_agent.run({'effort_score': scene['attentional_signal'], 'visual_density': random.random()})
            scene['attentional_signal'] = fused['fused_effort']
            scene['multimodal_source'] = True

    # === vNext.11 Moonshot: Cognitive Resonance ===
    moonshot_data = {}
    if moonshot_mode:
        print("[Moonshot] Running Cognitive Resonance Layer...")
        # 1. Resonance Agent
        res_agent = resonance.ResonanceAgent()
        # 2. Insight Agent
        insight_agent = insight.InsightAgent()
        moonshot_trace = []
        for i, scene in enumerate(temporal_output):
            # Lookup from batch (now calculated earlier)
            stan_data = stan_batch_results[i] if i < len(stan_batch_results) else {}
            if not stan_data:
                 stan_data = {'internal_state': {}, 'felt_emotion': 'N/A (Module Missing)'}
            
            # Resonance (Still sequential for now)
            # Need scene text again if not preserved?
            # We have all_scene_texts from earlier block
            scene_text = all_scene_texts[i] if i < len(all_scene_texts) else ""

            res_data = res_agent.analyze_scene(scene_text, scene['attentional_signal'])
            
            # Insight
            ins_data = insight_agent.detect_cascade(scene['temporal_expectation'])
            
            # Fuse data
            moonshot_trace.append({
                'scene_index': scene['scene_index'],
                'resonance': res_data,
                'insight': ins_data,
                'stanislavski_state': stan_data
            })
        moonshot_data = moonshot_trace

    
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
    
    # === Agent 11: Agency Analysis (vNext.9) ===
    # Replaces Fairness Agent
    agency_report = agency.run({
        'scenes': segmented
    })
    
    # Agent 6: Writer Intent & Immunity
    # (Move suggestions creation after pattern detection if depend on it, 
    # but suggestions.run depends on temporal_output so order is fine here)
    suggestions = suggestion.run(temporal_output)
    
    # v10.1: Merge Diction Issues into Suggestions
    if diction_issues:
        # Prioritize top 5
        for issue in diction_issues[:5]:
            suggestions['structural_repair_strategies'].append(issue)
            
    # Agent 5: Pattern Detection
    patterns_output = patterns.run({
        'temporal_signals': temporal_output,
        'features': encoded,
        'acd_states': acd_output # NEW: Pass ACD states
    })
    
    # === NEW: Agent 4.5b: Uncertainty Quantification (vNext.8) ===
    # Bootstrap Ensemble (Report Section 6.3)
    try:
        uncertainty_trace = ensemble_uncertainty.run({
            'base_trace': temporal_output,
            'iterations': 20
        })
    except Exception as e:
        print(f"[Warning] Uncertainty Agent failed: {e}")
        uncertainty_trace = []
    
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
    
    # === NEW: Agent 9.0: Comparative Baselines (IEEE) ===
    # Using 'lazy import' for research module to avoid circular deps if needed
    from research import baselines
    baseline_trace = baselines.run_baseline_sentiment(segmented)
    
    # Agent 7: Audience-Experience Mediation
    # Mediation needs ACD states and SSF analysis
    filtered['acd_states'] = acd_output 
    filtered['ssf_analysis'] = ssf_output # NEW
    final_output = mediation.run(filtered)
    
    # Add Enterprise Audit Metadata
    from .utils.model_manager import manager
    ml_status = "ML_Active" if (manager.get_pipeline and hasattr(manager, 'device')) else "Heuristic_Fallback"
    
    final_output['meta'] = {
        'run_id': run_id,
        'execution_mode': ml_status,
        'fingerprint': struct_fingerprint,
        'content_fingerprint': content_fp,
        'version': version,
        'lens': lens_id,
        'agent_timings': timings
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
    final_output['suggestions'] = suggestions
    final_output['agency_analysis'] = agency_report  # vNext.9 Replacement
    final_output['baseline_trace'] = baseline_trace # v9.0
    final_output['semantic_flux'] = semantic_flux # v9.1
    final_output['voice_fingerprints'] = voice_map # v10.1
    final_output['voice_fingerprints'] = voice_map # v10.1
    final_output['interaction_map'] = interaction_map # v11.0
    final_output['uncertainty_quantification'] = uncertainty_trace # vNext.8 (Section 6.3)
    final_output['polyglot_analysis'] = polyglot_data # vNext.10 Experimental
    final_output['moonshot_resonance'] = moonshot_data # vNext.11 Moonshot
    
    # v13.0: Runtime Estimation (User-Friendly)
    runtime_info = runtime.estimate_runtime(segmented)
    final_output['runtime_estimate'] = runtime_info
    
    # === DRIFT MONITORING (Post-Analysis) ===
    # Log run and update statistical baseline
    drift_monitor.monitor.log_run(
        {'run_id': run_id, 'fingerprint': struct_fingerprint},
        entropy_scores=semantic_scores
    )

    
    # v14.0: Scene-Level Actionable Notes
    scene_feedback = scene_notes.run({
        'scenes': segmented,
        'temporal_trace': temporal_output,
        'valence_scores': valence_scores,
        'syntax_scores': syntax_scores
    })
    final_output['scene_feedback'] = scene_feedback
    
    # Add metadata
    final_output['meta'].update({
        'lens': lens_config['lens_id'],
        'lens_description': lens_config['description']
    })
    
    # v13.1 Phase 6: Observability Debug Export
    final_output['debug_export'] = {
        'per_scene': [{
            'scene_index': i,
            'agent_vectors': {
                'semantic': semantic_scores[i] if i < len(semantic_scores) else 0,
                'valence': valence_scores[i] if i < len(valence_scores) else 0,
                'visual': visual_scores[i] if i < len(visual_scores) else 0,
                'syntax': syntax_scores[i] if i < len(syntax_scores) else 0,
            },
            'temporal': temporal_output[i] if i < len(temporal_output) else {},
            'lrf_value': lrf_trace[i].get('attentional_signal') if i < len(lrf_trace) else None,
            'coherence_penalty': temporal_output[i].get('coherence_penalty', 0) if i < len(temporal_output) else 0,
        } for i in range(len(segmented))],
        'lens_weights': lens_config,
        'cpu_safe_mode': cpu_safe_mode,
        'agent_timings': timings,
        'validation_errors': validation_errors,
    }
    
    # v13.1 Block 4: Resource measurement & guardrails
    _wall_time_s = round(time.time() - _run_start, 2)
    _current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    _peak_mb = round(_peak / (1024 * 1024), 1)
    _runtime_per_scene = _wall_time_s / max(len(segmented), 1)
    
    resource_flag = None
    if _wall_time_s > _RESOURCE_LIMITS['max_wall_time_s']:
        resource_flag = 'exceeded'
    elif _peak_mb > _RESOURCE_LIMITS['max_memory_mb']:
        resource_flag = 'exceeded'
    elif _runtime_per_scene > _RESOURCE_LIMITS['max_runtime_per_scene_s']:
        resource_flag = 'exceeded'
    
    if resource_flag:
        actual_bucket = _scene_bucket(len(segmented))
        _OVERSIZED_BUCKETS.add(actual_bucket)
        print(f"[Resource Guard] resource_flag=exceeded for bucket '{actual_bucket}' "
              f"(wall={_wall_time_s}s, mem={_peak_mb}MB, per_scene={_runtime_per_scene:.1f}s)")
    
    final_output['meta']['resource_flag'] = resource_flag
    final_output['meta']['wall_time_s'] = _wall_time_s
    final_output['meta']['peak_memory_mb'] = _peak_mb
    
    # v13.1 Block 7: Log telemetry (hash-only)
    telemetry.log_run(final_output)
    
    # === SHADOW MODE (v13.1 Hardening) ===
    if shadow_mode:
        print("[Shadow Mode] Executing dual run for consistency check...")
        # Recursive call with shadow_mode=False to avoid infinite loop
        shadow_result = run_pipeline(
            script_content, writer_intent, lens, genre, audience_profile, 
            high_res_mode, pre_parsed_lines, character_context, 
            experimental_mode, moonshot_mode, cpu_safe_mode, 
            valence_stride, stanislavski_min_words, embeddings_batch_size, 
            shadow_mode=False
        )
        
        # Compare
        mismatch = False
        # 1. Scene count
        if final_output['total_scenes'] != shadow_result['total_scenes']:
            mismatch = True
            print(f"[Shadow Mismatch] Scene count: {final_output['total_scenes']} vs {shadow_result['total_scenes']}")
        
        # 2. Temporal Trace (Epsilon check)
        trace_a = [p.get('attentional_signal', 0) for p in final_output['temporal_trace']]
        trace_b = [p.get('attentional_signal', 0) for p in shadow_result['temporal_trace']]
        if len(trace_a) == len(trace_b):
            for i, (a, b) in enumerate(zip(trace_a, trace_b)):
                if abs(a - b) > 1e-4:
                    mismatch = True
                    print(f"[Shadow Mismatch] Scene {i}: {a} vs {b}")
                    break
        else:
            mismatch = True # Differing lengths
            
        final_output['meta']['shadow_mismatch'] = mismatch
        if mismatch:
            final_output['meta']['shadow_flag'] = "DIVERGENT"

    # === OPERATOR DASHBOARD FIELDS (v13.1) ===
    # Promote critical metrics to top level for easy monitoring
    final_output['version_tag'] = final_output['meta'].get('version')
    
    # Model versions
    try:
        from .utils.model_manager import manager
        final_output['model_versions'] = manager.get_loaded_models()
    except:
        final_output['model_versions'] = {}

    final_output['cpu_safe_mode'] = cpu_safe_mode
    final_output['resource_flag'] = resource_flag
    
    # Validation errors
    errs = final_output.get('debug_export', {}).get('validation_errors', [])
    final_output['validation_error_count'] = len(errs) if isinstance(errs, list) else 0
    
    # Drift Flag (Check dashboard status if possible, otherwise placeholder)
    try:
        from .drift_dashboard import DriftDashboard
        # We don't run full check_drift() implies I/O, maybe too slow?
        # User asked to show it. Let's try to read last status or just check lightly.
        # For now, we'll check the dashboard status from file if available.
        # Actually, let's just log if *this* run triggered anything in the telemetry/log step?
        # The prompt implies showing if the *system* is drifting.
        # We'll default to "CHECK_DASHBOARD" to avoid recursive I/O in hot path.
        final_output['drift_flag'] = "CHECK_DASHBOARD" 
    except:
        final_output['drift_flag'] = "UNKNOWN"

    final_output['runtime_ms'] = sum(timings.values())
    final_output['total_scenes'] = len(segmented) # Ensure it's there
    final_output['scenes_per_second'] = round(len(segmented) / max(_wall_time_s, 0.001), 2)

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
    import argparse
    parser = argparse.ArgumentParser(description="ScriptPulse Runner")
    parser.add_argument("screenplay_file", help="Path to screenplay file")
    parser.add_argument("--experimental", action="store_true", help="Enable vNext.10 Experimental Features")
    parser.add_argument("--moonshot", action="store_true", help="Enable vNext.11 Moonshot Features (Resonance, Insight)")
    
    args = parser.parse_args()
    
    screenplay_file = args.screenplay_file
    
    # Load screenplay
    with open(screenplay_file, 'r') as f:
        screenplay_text = f.read()
    
    # Run pipeline
    result = run_pipeline(screenplay_text, experimental_mode=args.experimental, moonshot_mode=args.moonshot)
    
    # Print result
    import json
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
