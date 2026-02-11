#!/usr/bin/env python3
"""
ScriptPulse Runner - Executes full pipeline deterministically
"""

import sys
import random
from .agents import parsing, segmentation, encoding, temporal, patterns, intent, mediation, acd, ssf, lrf, semantic, syntax, xai, imagery, social, valence, profiler, coherence, beat, fairness, suggestion, embeddings, voice, scene_notes, bert_parser, agency, ensemble_uncertainty, multimodal, polyglot_validator # vNext.10 Experimental
from . import lenses, fingerprint, governance
from .utils import runtime  # v13.0


# vNext.11 Experimental
from .agents import resonance, insight, silicon_stanislavski

def run_pipeline(script_content, writer_intent=None, lens='viewer', genre='drama', audience_profile='general', high_res_mode=False, pre_parsed_lines=None, character_context=None, experimental_mode=False, moonshot_mode=False):
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
    governance.validate_request(script_content) # Changed screenplay_text to script_content
    
    # vNext.9 Safety: Drift Monitoring (Domain Adherence)
    from . import drift_monitor, security
    drift_monitor.monitor.check_domain_adherence(script_content.splitlines())
    
    # Load lens config
    lens_config = lenses.get_lens(lens)
    
    # Agent 1: Structural Parsing
    if pre_parsed_lines:
        parsed = pre_parsed_lines
    else:
        # vNext.9 Upgrade: BERT Parser
        parser = bert_parser.BertParserAgent()
        parsed_output = parser.run(script_content)
        parsed = parsed_output['lines']
    
    # Agent 2: Scene Segmentation
    segmented = segmentation.run(parsed)
    
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
    
    # === DRL: Deterministic Run ID ===
    lens_id = lens if lens else 'viewer'
    run_id, version = fingerprint.generate_run_id(struct_fingerprint, lens_id, writer_intent)
    
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
    semantic_flux = embeddings.run({'scenes': segmented})
    
    # === NEW: Agent 10.1: Voice Fingerprinting (Market) ===
    voice_map = voice.run({'scenes': segmented})
    
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
        # 3. Silicon Stanislavski
        try:
            stanislavski = silicon_stanislavski.SiliconStanislavski()
        except:
            stanislavski = None
        
        moonshot_trace = []
        for i, scene in enumerate(temporal_output):
            # Resonance
            scene_text = scene.get('preview', '') # Using preview as proxy for full text
            res_data = res_agent.analyze_scene(scene_text, scene['attentional_signal'])
            
            # Insight
            ins_data = insight_agent.detect_cascade(scene['temporal_expectation']) # Using expectation as entropy proxy
            
            # Stanislavski
            if stanislavski:
                stan_data = stanislavski.act_scene(scene_text)
            else:
                stan_data = {'internal_state': {}, 'felt_emotion': 'N/A (Module Missing)'}
            
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
