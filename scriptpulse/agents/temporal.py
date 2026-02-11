"""Temporal Dynamics Agent - Fatigue Carryover and Recovery Modeling"""

# Standard Defaults (Fallback)
DEFAULT_LAMBDA = 0.85 
DEFAULT_BETA = 0.3    
DEFAULT_GAMMA = 0.2    
DEFAULT_DELTA = 0.25   
R_MAX = 0.5    
E_THRESHOLD = 0.4 

from . import tam
import random
import statistics
import json
import os

# vNext.6 Schema Loader
try:
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'antigravity', 'schemas', 'genre_priors.json')
    with open(schema_path, 'r') as f:
        GENRE_PRIORS = json.load(f).get('genres', {})
except Exception:
    GENRE_PRIORS = {} # Fallback

def get_genre_config(genre):
    for k, v in GENRE_PRIORS.items():
        if k.lower() == genre.lower():
            return v
    return GENRE_PRIORS.get('Drama', {'lambda_decay': 0.85})

def simulate_consensus(input_data, lens_config=None, genre='drama', profile_params=None, iterations=5):
    """
    MRCS: Multi-Reader Consensus Simulator
    Runs the temporal model multiple times with slight parameter jitter.
    Includes Genre Context & Cognitive Profile.
    """
    if not input_data.get('features'):
        return []
        
    # Use Profile Params or Defaults
    if not profile_params:
        profile_params = {
            'lambda_base': DEFAULT_LAMBDA,
            'beta_recovery': DEFAULT_BETA,
            'fatigue_threshold': 1.0,
            'coherence_weight': 0.15 # Default sensitivity
        }
        
    accumulated_signals = None
    import copy
    base_lens = copy.deepcopy(lens_config) if lens_config else {}
    
    for _ in range(iterations):
        jitter_lens = copy.deepcopy(base_lens)
        if 'effort_weights' in jitter_lens:
            w = jitter_lens['effort_weights']
            w['cognitive_mix'] *= random.uniform(0.95, 1.05)
            w['emotional_mix'] *= random.uniform(0.95, 1.05)
            
        signals = run(input_data, lens_config=jitter_lens, genre=genre, profile_params=profile_params)
        
        if accumulated_signals is None:
            accumulated_signals = []
            for s in signals:
                accumulated_signals.append({
                    'scene_index': s['scene_index'],
                    'instantaneous_effort': s['instantaneous_effort'],
                    'attentional_signal': s['attentional_signal'],
                    'recovery_credit': s['recovery_credit'],
                    'tam_integral': s['tam_integral'],
                    'expectation_strain': s.get('expectation_strain', 0.0), 
                    'temporal_expectation': s.get('temporal_expectation', 0.5),
                    'valence_score': s.get('valence_score', 0.0),
                    'coherence_penalty': s.get('coherence_penalty', 0.0) # NEW
                })
        else:
            for i, s in enumerate(signals):
                accumulated_signals[i]['instantaneous_effort'] += s['instantaneous_effort']
                accumulated_signals[i]['attentional_signal'] += s['attentional_signal']
                accumulated_signals[i]['recovery_credit'] += s['recovery_credit']
                accumulated_signals[i]['tam_integral'] += s['tam_integral']
                accumulated_signals[i]['expectation_strain'] += s.get('expectation_strain', 0.0)
                accumulated_signals[i]['temporal_expectation'] += s.get('temporal_expectation', 0.5)
                accumulated_signals[i]['valence_score'] += s.get('valence_score', 0.0)
                accumulated_signals[i]['coherence_penalty'] += s.get('coherence_penalty', 0.0)
                
    # Average
    all_efforts = []
    for sig in accumulated_signals:
        sig['instantaneous_effort'] = round(sig['instantaneous_effort'] / iterations, 3)
        all_efforts.append(sig['instantaneous_effort'])
        
        sig['attentional_signal'] = round(sig['attentional_signal'] / iterations, 3)
        sig['recovery_credit'] = round(sig['recovery_credit'] / iterations, 3)
        sig['tam_integral'] = round(sig['tam_integral'] / iterations, 3)
        sig['expectation_strain'] = round(sig['expectation_strain'] / iterations, 3)
        sig['temporal_expectation'] = round(sig['temporal_expectation'] / iterations, 3)
        sig['valence_score'] = round(sig['valence_score'] / iterations, 3)
        sig['coherence_penalty'] = round(sig['coherence_penalty'] / iterations, 3)
        
    median_effort = statistics.median(all_efforts) if all_efforts else 0.5
    baseline_factor = max(0.5, min(1.5, median_effort / 0.5))
    length_factor = compute_length_factor(len(accumulated_signals))

    # Re-classify with GENRE & PROFILE
    for sig in accumulated_signals:
         sig['fatigue_state'] = classify_fatigue_state(
             sig['attentional_signal'], 
             length_factor, 
             baseline_factor,
             genre,
             profile_params['fatigue_threshold'] # Profile adjustment
         )
         sig['affective_state'] = classify_affective_state(
             sig['attentional_signal'],
             sig['valence_score'],
             length_factor * baseline_factor
         )
        
    return accumulated_signals


def run(input_data, lens_config=None, genre='drama', profile_params=None):
    """
    Compute temporal dynamics with FULL RESEARCH LAYER (v6.6).
    """
    features = input_data.get('features', [])
    semantic_scores = input_data.get('semantic_scores', [])
    syntax_scores = input_data.get('syntax_scores', [])
    visual_scores = input_data.get('visual_scores', [])
    social_scores = input_data.get('social_scores', [])
    valence_scores = input_data.get('valence_scores', []) 
    coherence_scores = input_data.get('coherence_scores', []) # NEW
    
    if not features:
        return []
    
    # Profile Defaults with Schema Injection (vNext.6)
    if not profile_params:
         config = get_genre_config(genre)
         profile_params = {
             'lambda_base': config.get('lambda_decay', 0.85), 
             'beta_recovery': config.get('recovery_rate', 0.3) * 0.3, # Scale recovery
             'fatigue_threshold': 1.0, 
             'coherence_weight': 0.15
         }
         
    length_factor = compute_length_factor(len(features))
    
    signals = []
    prev_signal = 0.0
    prev_effort = 0.5 
    rolling_expectation = 0.5
    
    for i, scene in enumerate(features):
        sem = semantic_scores[i] if i < len(semantic_scores) else 0.0
        syn = syntax_scores[i] if i < len(syntax_scores) else 0.0
        vis = visual_scores[i] if i < len(visual_scores) else 0.0
        soc = social_scores[i] if i < len(social_scores) else 0.0
        val = valence_scores[i] if i < len(valence_scores) else 0.0
        coh = coherence_scores[i] if i < len(coherence_scores) else 0.0 # Switching Disorientation
        
        # 1. Base Holistic Effort
        effort = compute_instantaneous_effort(scene, lens_config, sem, syn, vis, soc)
        
        # 2. Add Coherence Penalty (Switching Cost)
        # Weight depends on profile (Distracted viewers hurt more)
        # Coh is 0.0-1.0. Weight 0.15 -> max penalty 0.15 effort boost.
        disorientation = coh * profile_params['coherence_weight']
        effort += disorientation
        
        # TAM
        tam_modifiers = tam.run_micro_integration(scene, effort)
        effort = effort * tam_modifiers['effort_modifier']
        
        # TEM
        expectation_strain = abs(effort - rolling_expectation)
        rolling_expectation = 0.9 * rolling_expectation + 0.1 * effort
        
        # Recovery (Use Profile Beta)
        recovery = compute_recovery(scene, effort, prev_effort, profile_params['beta_recovery'])
        recovery = recovery * tam_modifiers['recovery_modifier']
        
        # === HYSTERETIC DECAY (Use Profile Lambda) ===
        # CRITICAL STABILITY FIX: Clamp base lambda to < 1.0 to ensure AR(1) stationarity
        base_lambda = min(0.99, profile_params['lambda_base'])
        adaptive_lambda = base_lambda
        
        if prev_signal > 1.0: # High Strain
            hysteresis_factor = min(1.0, (prev_signal - 1.0))
            adaptive_lambda += 0.01 * hysteresis_factor # Reduced from 0.05 for stability
            
        # CLAMP LAMBDA to prevent instability (Max 0.90 for robust decay)
        adaptive_lambda = min(0.90, adaptive_lambda)
            
        # S[i]
        if i == 0:
            signal = effort
        else:
            signal = effort + adaptive_lambda * prev_signal - recovery
        
        signal = max(0.0, signal)
        
        # use profile threshold
        fatigue = classify_fatigue_state(signal, length_factor, 1.0, genre, profile_params['fatigue_threshold'])
        affect = classify_affective_state(signal, val, length_factor)
        
        signals.append({
            'scene_index': scene['scene_index'],
            'instantaneous_effort': round(effort, 3),
            'attentional_signal': round(signal, 3),
            'recovery_credit': round(recovery, 3),
            'fatigue_state': fatigue,
            'affective_state': affect, 
            'valence_score': val,
            'coherence_penalty': round(disorientation, 3), # Track this
            'tam_integral': tam_modifiers['micro_fatigue_integral'],
            'expectation_strain': round(expectation_strain, 3), 
            'temporal_expectation': round(rolling_expectation, 3) 
        })
        
        prev_signal = signal
        prev_effort = effort
    
    return signals


def compute_instantaneous_effort(scene_features, lens_config=None, sem=0.0, syn=0.0, vis=0.0, soc=0.0):
    """Computes Holistic Cognitive Load."""
    if not lens_config:
        weights = {
            "cognitive_mix": 0.55,
            "emotional_mix": 0.45,
            "cognitive_components": {"ref_score":0.3,"ling_complexity":0.3,"struct_score":0.25,"dial_tracking":0.15},
            "emotional_components": {"dial_engagement":0.35,"visual_score":0.3,"ling_volume":0.2,"stillness_factor":0.15}
        }
    else:
        weights = lens_config['effort_weights']

    ling = scene_features['linguistic_load']
    dial = scene_features['dialogue_dynamics']
    visual = scene_features['visual_abstraction']
    ref = scene_features['referential_load']
    struct = scene_features['structural_change']
    ambient = scene_features.get('ambient_signals', {})
    
    lc = ling['sentence_length_variance'] / 20.0
    rs = (ref['active_character_count']/10.0 + ref['character_reintroductions']/5.0)
    ss = struct['event_boundary_score'] / 100.0
    dt = dial['speaker_switches'] / 20.0
    
    cog_w = weights['cognitive_components']
    base_struct_load = (cog_w['ref_score']*rs + cog_w['ling_complexity']*lc + cog_w['struct_score']*ss + cog_w['dial_tracking']*dt)
    
    # 5-Channel Mind
    final_cognitive_load = (0.50 * base_struct_load + 0.15 * sem + 0.10 * syn + 0.15 * vis + 0.10 * soc)
    
    dial_en = dial['dialogue_turns'] / 50.0
    vis_sc = (visual['action_lines']/50.0 + visual['continuous_action_runs']/10.0)
    ling_vol = ling['sentence_count'] / 50.0
    still = 1.0 - ambient.get('ambient_score', 0.5)
    
    emo_w = weights['emotional_components']
    emotional_attention = (emo_w['dial_engagement']*dial_en + emo_w['visual_score']*vis_sc + emo_w['ling_volume']*ling_vol + emo_w['stillness_factor']*still)
    
    total_effort = (weights['cognitive_mix'] * final_cognitive_load + weights['emotional_mix'] * emotional_attention)
    return total_effort


def compute_recovery(scene_features, effort, prev_effort=0.5, beta=DEFAULT_BETA):
    # Dynamic Beta from Profile
    recovery = 0.0
    if effort < E_THRESHOLD:
        recovery += beta * (E_THRESHOLD - effort)
        if prev_effort > E_THRESHOLD * 1.5: recovery *= 0.6 
    boundary_score = scene_features['structural_change']['event_boundary_score']
    if boundary_score > 0.5: recovery += DEFAULT_GAMMA * (boundary_score / 100.0)
    ambient = scene_features.get('ambient_signals', {})
    if ambient.get('is_ambient'): recovery += DEFAULT_DELTA * ambient.get('ambient_score', 0.0)
    return min(recovery, R_MAX)


def compute_length_factor(total_scenes):
    if total_scenes >= 50: return 1.0
    elif total_scenes >= 20: return 1.0 + (50 - total_scenes) / 30 * 0.5
    else: return 2.0


def classify_fatigue_state(signal, length_factor=1.0, baseline_factor=1.0, genre='drama', profile_threshold=1.0):
    """
    Classify fatigue using GENRE + LENGTH + BASELINE + PROFILE metrics.
    """
    # vNext.6: Use Schema Layer (Peer Review Solved)
    config = get_genre_config(genre)
    # Map lambda/decay profile to a simple multiplier for display threshold
    # Higher lambda (Horror) means fatigue accumulates faster -> lower threshold multiplier?
    # Actually, if lambda is high, signal stays high. Formatting logic:
    # We use the inverse of lambda relative to baseline as a scaler
    base_lambda = 0.85
    g_lambda = config.get('lambda_decay', 0.85)
    
    # Heuristic: If lambda is high (0.92), effective load is higher. 
    # So we increase the threshold tolerance slightly? 
    # Or just use the 'micro_penalty_weight' from schema as a proxy for "Genre Intensity Factor"
    g_factor = config.get('micro_penalty_weight', 1.0)
    
    # Scale adjusts the definition of 'normal' based on user capacity
    scale = length_factor * baseline_factor * g_factor * profile_threshold
    
    if signal < 0.5 * scale: return "normal"
    elif signal < 1.0 * scale: return "elevated"
    elif signal < 1.5 * scale: return "high"
    else: return "extreme"

def classify_affective_state(arousal_signal, valence_score, scale_factor=1.0):
    high_arousal = arousal_signal > (0.8 * scale_factor)
    positive_valence = valence_score > 0.1
    negative_valence = valence_score < -0.1
    
    if high_arousal:
        if positive_valence: return "Excitement"
        elif negative_valence: return "Anxiety"
        else: return "Intense"
    else:
        if positive_valence: return "Relaxation"
        elif negative_valence: return "Melancholy"
        else: return "Calm"
