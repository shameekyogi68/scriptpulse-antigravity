"""
Dynamics Agent - Handling Temporal Simulation & Pattern Detection
Consolidates: temporal.py, tam.py, lrf.py, acd.py, patterns.py
"""

import random
import statistics
import json
import os
import math
import copy

# =============================================================================
# TEMPORAL LOGIC (formerly temporal.py)
# =============================================================================

class ReaderProfile:
    """
    User-configurable profile for the target audience.
    Affects fatigue accumulation, recovery capability, and complexity tolerance.
    """
    def __init__(self, familiarity=0.5, speed=250, tolerance=0.5):
        self.familiarity = max(0.0, min(1.0, familiarity)) # 0.0 (Novice) to 1.0 (Expert)
        self.speed = max(100, min(1000, speed)) # Words Per Minute
        self.tolerance = max(0.0, min(1.0, tolerance)) # Tolerance for high complexity
        
    def get_params(self):
        """Map profile attributes to dynamics parameters."""
        # 1. Lambda (Decay): Higher tolerance = slower decay (sustains interest longer)
        # Base 0.85 -> Range [0.80, 0.95]
        lambda_base = 0.80 + (self.tolerance * 0.15)
        
        # 2. Beta (Recovery): Higher familiarity = faster recovery (better processing)
        # Base 0.3 -> Range [0.2, 0.5]
        beta_recovery = 0.2 + (self.familiarity * 0.3)
        
        # 3. Fatigue Threshold: Higher tolerance = higher threshold
        # Base 1.0 -> Range [0.8, 1.2]
        fatigue_threshold = 0.8 + (self.tolerance * 0.4)
        
        # 4. Coherence Weight: Higher familiarity = less penalty for confusion
        # Base 0.15 -> Range [0.2, 0.05]
        coherence_weight = 0.2 - (self.familiarity * 0.15)
        
        return {
            'lambda_base': lambda_base,
            'beta_recovery': beta_recovery,
            'fatigue_threshold': fatigue_threshold,
            'coherence_weight': coherence_weight
        }


class DynamicsAgent:
    """
    Dynamics Agent - Temporal Simulation & Pattern Detection
    Handles the core cognitive simulation of the reader/viewer experience.
    """
    
    def __init__(self):
        # Configuration Defaults
        self.DEFAULT_LAMBDA = 0.85 
        self.DEFAULT_BETA = 0.3    
        self.DEFAULT_GAMMA = 0.2    
        self.DEFAULT_DELTA = 0.25   
        self.R_MAX = 0.5    
        self.E_THRESHOLD = 0.4
        
        # Load Genre Priors
        try:
            # Adjust path relative to this file location
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            schema_path = os.path.join(base_dir, 'antigravity', 'schemas', 'genre_priors.json')
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    self.GENRE_PRIORS = json.load(f).get('genres', {})
            else:
                self.GENRE_PRIORS = {}
        except Exception:
            self.GENRE_PRIORS = {} # Fallback

    def get_genre_config(self, genre):
        for k, v in self.GENRE_PRIORS.items():
            if k.lower() == genre.lower():
                return v
        return self.GENRE_PRIORS.get('Drama', {'lambda_decay': 0.85})

    def run_simulation(self, input_data, lens_config=None, genre='drama', profile_params=None, iterations=5):
        """
        MRCS: Multi-Reader Consensus Simulator (formerly simulate_consensus)
        Runs the temporal model multiple times with slight parameter jitter.
        """
        if not input_data.get('features'):
            return []
            
        # Use Profile Params or Defaults
        if not profile_params:
            profile_params = {
                'lambda_base': self.DEFAULT_LAMBDA,
                'beta_recovery': self.DEFAULT_BETA,
                'fatigue_threshold': 1.0,
                'coherence_weight': 0.15
            }
            
        # Ensure we have all keys if a partial dict was passed
        defaults = ReaderProfile().get_params()
        for k, v in defaults.items():
            if k not in profile_params:
                profile_params[k] = v
            
        accumulated_signals = None
        base_lens = copy.deepcopy(lens_config) if lens_config else {}
        
        for _ in range(iterations):
            jitter_lens = copy.deepcopy(base_lens)
            if 'effort_weights' in jitter_lens:
                w = jitter_lens['effort_weights']
                w['cognitive_mix'] *= random.uniform(0.95, 1.05)
                w['emotional_mix'] *= random.uniform(0.95, 1.05)
                
            signals = self._run_single_pass(input_data, lens_config=jitter_lens, genre=genre, profile_params=profile_params)
            
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
                        'coherence_penalty': s.get('coherence_penalty', 0.0)
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
        for sig in accumulated_signals:
            sig['instantaneous_effort'] = round(sig['instantaneous_effort'] / iterations, 3)
            sig['attentional_signal'] = round(sig['attentional_signal'] / iterations, 3)
            sig['recovery_credit'] = round(sig['recovery_credit'] / iterations, 3)
            sig['tam_integral'] = round(sig['tam_integral'] / iterations, 3)
            sig['expectation_strain'] = round(sig['expectation_strain'] / iterations, 3)
            sig['temporal_expectation'] = round(sig['temporal_expectation'] / iterations, 3)
            sig['valence_score'] = round(sig['valence_score'] / iterations, 3)
            sig['coherence_penalty'] = round(sig['coherence_penalty'] / iterations, 3)
            
        return accumulated_signals

    def _run_single_pass(self, input_data, lens_config=None, genre='drama', profile_params=None):
        """Core Temporal Dynamics Engine (formerly temporal.run)"""
        features = input_data.get('features', [])
        coherence_scores = input_data.get('coherence_scores', [])
        valence_scores = input_data.get('valence_scores', [])
        
        if not features: return []
        
        # -- 1. Configuration & Weights --
        # Allow lens_config to override defaults
        weights = {
            'cognitive_mix': 0.55,
            'emotional_mix': 0.45,
            'cognitive_components': {'structural': 0.6, 'semantic': 0.2, 'syntactic': 0.2},
            'emotional_components': {'dialogue_engagement': 0.35, 'visual_intensity': 0.30, 
                                   'linguistic_volume': 0.20, 'stillness_penalty': 0.15}
        }
        if lens_config and 'effort_weights' in lens_config:
            weights.update(lens_config['effort_weights'])
            
        genre_cfg = self.get_genre_config(genre)
        
        # Compatibility / Normalization of weights
        cog = weights.get('cognitive_components', {})
        if 'structural' not in cog:
            # Map legacy (lenses.py) to v14 schema
            # REVISION 3: Matching Golden Baselines
            # Monologue (High Text/Dial) needs HIGH weight -> Semantic/Dialogue.
            # Action (High Visual/Struct) needs MODERATE weight -> Structural.
            
            # 1. Structural: Keep purely structural (Event Boundaries).
            # Ref Score (Candidates) moved to Semantic to boost Text/Entropy.
            cog['structural'] = cog.get('struct_score', 0.25)
            
            # 2. Semantic: Map 'ref_score' (Referential) and 'dial_tracking' here.
            # Rationale: Entropy correlates with Tracking Load and References.
            # Base (0.1) + Ref(0.3) + Dial(0.15) = ~0.55.
            cog['semantic'] = 0.1 + cog.get('ref_score', 0.3) + cog.get('dial_tracking', 0.15)
            
            # 3. Syntactic: standard mapping
            cog['syntactic'] = cog.get('ling_complexity', 0.3)
            
        emo = weights.get('emotional_components', {})
        if 'visual_intensity' not in emo:
            emo['visual_intensity'] = emo.get('visual_score', 0.3)
            emo['stillness_penalty'] = emo.get('stillness_factor', 0.15)
            emo['linguistic_volume'] = emo.get('ling_volume', 0.2)
            emo['dialogue_engagement'] = emo.get('dial_engagement', 0.35)
        
        # Profile Parameters
        lambda_base = min(0.99, profile_params['lambda_base'])
        beta_rec = profile_params['beta_recovery']
        fatigue_thresh = profile_params['fatigue_threshold']
        coh_weight = profile_params['coherence_weight']
        
        signals = []
        prev_signal = 0.5 # S[0]
        prev_expectation = 0.5
        
        length_factor = self._compute_length_factor(len(features))
        
        for i, scene_feat in enumerate(features):
            # -- 2. Instantaneous Effort Calculation E[i] --
            
            # A. Cognitive Load
            struct_load = (scene_feat['referential_load']['active_character_count'] / 10.0 + 
                          scene_feat['structural_change']['event_boundary_score'] / 100.0) / 2.0
            sem_load = scene_feat.get('entropy_score', 0) / 8.0 # Approx normalization
            syn_load = scene_feat['linguistic_load']['sentence_length_variance'] / 100.0
            
            cog_load = (struct_load * weights['cognitive_components']['structural'] +
                       sem_load * weights['cognitive_components']['semantic'] +
                       syn_load * weights['cognitive_components']['syntactic'])
            
            # B. Emotional Load
            dial = scene_feat['dialogue_dynamics']
            vis = scene_feat['visual_abstraction']
            ling = scene_feat['linguistic_load']
            amb = scene_feat['ambient_signals']
            
            # Avoid div zero
            dial_eng = dial['turn_velocity']
            
            # -- 2a. Determine Scene Type & Adaptive Decay --
            # "Use separate decay rates for exposition, action, and dialogue heavy scenes"
            scene_type = 'balanced'
            lambda_mod = 0.0
            
            # Simple heuristic based on feature dominance
            if vis['action_lines'] > dial['dialogue_line_count'] * 1.5:
                scene_type = 'action'
                lambda_mod = -0.05 # Faster decay (Action needs constant stimulation)
            elif dial['dialogue_line_count'] > vis['action_lines'] * 2.0:
                scene_type = 'dialogue'
                lambda_mod = 0.05 # Slower decay (Dialogue sustains attention longer via thread tracking)
            elif scene_feat.get('is_exposition', False): # Future proofing
                 scene_type = 'exposition'
                 lambda_mod = 0.10 # Slowest decay (Reader invests effort expecting payoff)
                 
            # -- 2b. Instantaneous Effort Calculation E[i] --
            
            # "Normalize effort by information units, not scene length"
            # Calculate Density Factor (Propensity of info per unit length)
            # Default density is 1.0. High entropy/short length = High Density.
            # Low entropy/long length = Low Density.
            
            density_factor = 1.0
            if 'entropy_score' in scene_feat and ling['sentence_count'] > 0:
                 entropy = scene_feat['entropy_score']
                 # Normalize entropy (typically 0-6 bits) against volume
                 # High volume with low entropy -> Lower the effective load
                 normalized_entropy = entropy / 6.0 # Max entropy approx 6
                 
                 # Logic: If volume is high but entropy is low (verbose), reduce load.
                 # If volume is low but entropy is high (dense), increase load.
                 density_factor = 0.5 + normalized_entropy
            
            # A. Cognitive Load
            struct_load = (scene_feat['referential_load']['active_character_count'] / 10.0 + 
                          scene_feat['structural_change']['event_boundary_score'] / 100.0) / 2.0
            sem_load = scene_feat.get('entropy_score', 0) / 8.0 # Approx normalization
            syn_load = scene_feat['linguistic_load']['sentence_length_variance'] / 100.0
            
            cog_load = (struct_load * weights['cognitive_components']['structural'] +
                       sem_load * weights['cognitive_components']['semantic'] +
                       syn_load * weights['cognitive_components']['syntactic'])
            
            # B. Emotional Load (Normalized by Density)
            dial = scene_feat['dialogue_dynamics']
            vis = scene_feat['visual_abstraction']
            ling = scene_feat['linguistic_load']
            amb = scene_feat['ambient_signals']
            
            # Avoid div zero
            dial_eng = dial['turn_velocity']
            vis_int = min(1.0, vis['action_lines'] / 20.0)
            ling_vol = min(1.0, ling['sentence_count'] / 50.0)
            still_pen = amb['component_scores']['stillness']
            
            # Apply Density Normalization to Volume Metrics
            # "Long but simple scenes still trigger overload flags" -> Fix by scaling volume by density
            ling_vol *= density_factor
            vis_int *= density_factor
            
            # Confusion Markers (Entity Churn) - "Add confusion markers"
            confusion_penalty = 0.0
            if 'entity_churn' in scene_feat.get('referential_load', {}):
                 confusion_penalty = scene_feat['referential_load']['entity_churn'] * 0.2
            if 'unresolved_references' in scene_feat.get('referential_load', {}):
                 confusion_penalty += scene_feat['referential_load']['unresolved_references'] * 0.1
            
            emo_load = (dial_eng * weights['emotional_components']['dialogue_engagement'] +
                       vis_int * weights['emotional_components']['visual_intensity'] +
                       ling_vol * weights['emotional_components']['linguistic_volume'] - 
                       (still_pen * weights['emotional_components']['stillness_penalty']))
            emo_load = max(0.0, emo_load)
            
            # C. Mixed Effort
            base_effort = (cog_load * weights['cognitive_mix'] + 
                          emo_load * weights['emotional_mix'])
            
            # D. Coherence Penalty (Confusion adds effort)
            coh_penalty = 0.0
            if coherence_scores and i < len(coherence_scores):
                coh_penalty = coherence_scores[i] * coh_weight
            
            # Total Effort with Confusion
            effort = base_effort + coh_penalty + confusion_penalty
            
            # -- 3. TAM Integration (Micro-Dynamics) --
            tam_modifiers = self._run_tam_integration(scene_feat, effort)
            effort *= tam_modifiers['effort_modifier']
            
            # -- 4. Recovery Calculation R[i] --
            # Recovery is inverse of effort, scaled by beta and TAM
            raw_recovery = max(0, (self.R_MAX - effort))
            recovery = raw_recovery * beta_rec * tam_modifiers['recovery_modifier']
            
            # -- 5. Signal State Update S[i] --
            # Autoregressive decay + Input
            # Apply Scene Type Modifier to Lambda
            current_lambda = max(0.1, min(0.99, lambda_base + lambda_mod))
            
            if i == 0:
                signal = effort
            else:
                signal = effort + current_lambda * prev_signal - recovery
                
            # Bounds checking
            signal = max(0.0, min(1.0, signal))
            
            # -- 6. Expectation Strain --
            # Surprise = deviation from prediction
            expectation = prev_expectation * 0.7 + effort * 0.3
            strain = abs(effort - prev_expectation)
            
            # Store
            signals.append({
                'scene_index': scene_feat['scene_index'],
                'instantaneous_effort': round(effort, 3),
                'attentional_signal': round(signal, 3),
                'recovery_credit': round(recovery, 3),
                'tam_integral': round(tam_modifiers['micro_fatigue_integral'], 3),
                'expectation_strain': round(strain, 3),
                'temporal_expectation': round(expectation, 3),
                'valence_score': valence_scores[i] if i < len(valence_scores) else 0.0,
                'coherence_penalty': round(coh_penalty, 3)
            })
            
            prev_signal = signal
            prev_expectation = expectation
            
        return signals

    def _compute_length_factor(self, total_scenes):
        if total_scenes >= 50: return 1.0
        elif total_scenes >= 20: return 1.0 + (50 - total_scenes) / (50 - 20) * 0.5
        else: return 2.0

    # =========================================================================
    # TAM LOGIC (formerly tam.py)
    # =========================================================================
    
    def _run_tam_integration(self, scene_features, base_effort):
        micro = scene_features.get('micro_structure', [])
        if not micro:
            return {'effort_modifier': 1.0, 'recovery_modifier': 1.0, 'micro_fatigue_integral': 0.0}
        
        # 1. Map Micro-Effort e(tau)
        e_tau = []
        for item in micro:
            tag = item['tag']
            words = item['word_count']
            if tag == 'A': val = 0.5 + min(0.5, words / 20.0) 
            elif tag == 'D': val = 0.3 + min(0.4, words / 15.0)
            elif tag == 'S': val = 0.8
            elif tag == 'C': val = 0.1
            else: val = 0.2
            e_tau.append(val)
            
        if not e_tau: return {'effort_modifier': 1.0, 'recovery_modifier': 1.0, 'micro_fatigue_integral': 0.0}
            
        # 2. Micro-Fatigue Accumulation
        sigma = []
        prev_s = 0.0
        micro_lambda = 0.9
        for e in e_tau:
            s = e + micro_lambda * prev_s
            sigma.append(s)
            prev_s = s
            
        # 3. Derive Modifiers
        peak_sigma = max(sigma) if sigma else 0
        avg_sigma = sum(sigma) / len(sigma) if sigma else 0
        uniformity = avg_sigma / peak_sigma if peak_sigma > 0 else 1.0
        
        effort_mod = 1.0 + (1.0 - uniformity) * 0.2
        
        # Recovery requires continuous low-load windows
        low_load_count = sum(1 for e in e_tau if e < 0.3)
        recovery_potential = low_load_count / len(e_tau)
        recovery_mod = 0.5 + recovery_potential # 0.5 to 1.5
        
        return {
            'effort_modifier': effort_mod,
            'recovery_modifier': recovery_mod,
            'micro_fatigue_integral': round(avg_sigma, 3)
        }

    # =========================================================================
    # LRF LOGIC (formerly lrf.py)
    # =========================================================================

    def apply_long_range_fatigue(self, input_data):
        """Apply long-range fatigue dynamics (formerly lrf.run)"""
        signals = input_data.get('temporal_signals', [])
        if not signals: return []
        
        refined_signals = []
        fatigue_reserve = 0.0
        
        ACCUMULATION_RATE = 0.15
        DISCHARGE_RATE = 0.4
        DECAY_RATE = 0.05
        SUSTAINED_EFFORT_THRESHOLD = 0.4
        SUSTAINED_ONSET = 3
        K1, K2 = 0.025, 0.008
        
        consecutive_high = 0
        
        for i, sig in enumerate(signals):
            new_sig = sig.copy()
            e_i = sig['instantaneous_effort']
            r_i = sig['recovery_credit']
            s_i = sig['attentional_signal']
            
            if e_i >= SUSTAINED_EFFORT_THRESHOLD: consecutive_high += 1
            else: consecutive_high = max(0, consecutive_high - 2)
            
            accumulation = 0.0
            if 0.3 < e_i < 0.6 and r_i < 0.2:
                accumulation = (e_i - 0.3) * ACCUMULATION_RATE
            if e_i >= 0.6:
                accumulation += e_i * ACCUMULATION_RATE * 0.5
                
            fatigue_reserve += accumulation
            
            discharge = 0.0
            if r_i > 0.3: discharge = fatigue_reserve * DISCHARGE_RATE
            elif s_i > 0.7: discharge = fatigue_reserve * 0.2
                 
            # Apply discharge to signal (latent fatigue manifests as higher signal/stress)
            # Original LRF logic: added discharge to S_i
            new_s_i = s_i + discharge
            fatigue_reserve -= discharge
            
            sustained_penalty = 0.0
            if consecutive_high > SUSTAINED_ONSET:
                excess = consecutive_high - SUSTAINED_ONSET
                sustained_penalty = min(0.4, K1 * excess + K2 * (excess ** 2))
                
            # Penalty reduces attention (tuning out)
            new_s_i = new_s_i * (1.0 - sustained_penalty)
            
            fatigue_reserve *= (1.0 - DECAY_RATE)
            
            new_sig['attentional_signal'] = round(new_s_i, 3)
            new_sig['fatigue_reserve'] = round(fatigue_reserve, 3)
            new_sig['sustained_fatigue_penalty'] = round(sustained_penalty, 3)
            
            refined_signals.append(new_sig)
            
        return refined_signals

    # =========================================================================
    # ACD LOGIC (formerly acd.py)
    # =========================================================================

    def calculate_acd_states(self, input_data):
        """Calculate Attention Collapse vs Drift (formerly acd.run)"""
        signals = input_data.get('temporal_signals', [])
        features = input_data.get('features', [])
        if not signals or not features: return []
        
        acd_states = []
        prev_collapse = 0.0
        prev_drift = 0.0
        
        COLLAPSE_DECAY = 0.85
        DRIFT_DECAY = 0.6
        
        for i, sig in enumerate(signals):
            feat = features[i]
            effort = sig['instantaneous_effort']
            recovery = sig['recovery_credit']
            struct_change = feat['structural_change']['event_boundary_score']
            
            # Collapse
            collapse_pressure = 0.0
            if effort > 0.6: collapse_pressure += (effort - 0.6) * 2.0
            if recovery < 0.1: collapse_pressure += 0.2
            if struct_change > 70: collapse_pressure *= 1.2
            
            collapse = collapse_pressure + COLLAPSE_DECAY * prev_collapse
            collapse = min(1.0, collapse)
            
            # Drift
            drift_pressure = 0.0
            effort_delta = 0.0
            if i > 0:
                effort_delta = abs(effort - signals[i-1]['instantaneous_effort'])
                
            if effort_delta < 0.1 and effort < 0.5: drift_pressure += 0.15
            if struct_change < 20: drift_pressure += 0.15
            
            drift = drift_pressure + DRIFT_DECAY * prev_drift
            drift = min(1.0, drift)
            
            if struct_change > 60 or effort_delta > 0.3:
                drift *= 0.2 # Novelty reset
                
            primary = 'stable'
            if collapse > 0.6 and collapse > drift: primary = 'collapse'
            elif drift > 0.6 and drift > collapse: primary = 'drift'
            
            acd_states.append({
                'scene_index': sig['scene_index'],
                'collapse_likelihood': round(collapse, 3),
                'drift_likelihood': round(drift, 3),
                'primary_state': primary
            })
            prev_collapse = collapse
            prev_drift = drift
            
        return acd_states

    # =========================================================================
    # PATTERNS LOGIC (formerly patterns.py)
    # =========================================================================
    
    def detect_patterns(self, input_data):
        """Detect persistent experiential patterns"""
        signals = input_data.get('temporal_signals', [])
        features = input_data.get('features', [])
        acd_states = input_data.get('acd_states', [])
        
        MIN_PERSISTENCE = 3
        if len(signals) < MIN_PERSISTENCE: return []
        
        length_factor = self._compute_length_factor(len(signals))
        script_contrast = self._compute_script_contrast(signals)
        
        patterns = []
        
        # 1. Repetition
        rep = self._detect_repetition(signals, features, script_contrast, MIN_PERSISTENCE)
        patterns.extend(rep)
        
        if rep:
            escalated = self._apply_cumulative_escalation(rep, signals, length_factor, script_contrast)
            patterns.extend(escalated)
            
        patterns.extend(self._detect_sustained_demand(signals, length_factor, script_contrast, MIN_PERSISTENCE))
        patterns.extend(self._detect_limited_recovery(signals, script_contrast, MIN_PERSISTENCE))
        patterns.extend(self._detect_constructive_strain(signals, script_contrast, MIN_PERSISTENCE))
        patterns.extend(self._detect_degenerative_fatigue(signals, script_contrast, acd_states, MIN_PERSISTENCE))
        
        return patterns

    def _compute_script_contrast(self, signals):
        vals = [s['attentional_signal'] for s in signals]
        contrast = max(vals) - min(vals)
        return {
            'contrast_score': contrast,
            'normalized_contrast': min(1.0, contrast / 2.0),
            'is_low_contrast': contrast < 0.8,
            'is_high_contrast': contrast > 2.0
        }

    def _detect_repetition(self, signals, features, contrast, min_scenes):
        patterns = []
        EFFORT_THRESH = 0.1
        DIV_THRESH = 0.2
        
        for start in range(len(signals) - min_scenes + 1):
            window = signals[start:start+min_scenes]
            efforts = [s['instantaneous_effort'] for s in window]
            mean_e = statistics.mean(efforts)
            var_e = statistics.variance(efforts) if len(efforts) > 1 else 0.0
            
            diversity = 1.0
            if features:
                 w_feat = features[start:start+min_scenes]
                 diversity = self._compute_feature_diversity(w_feat)
            
            if var_e < EFFORT_THRESH and diversity < DIV_THRESH:
                rep_density = {
                    'is_early': start == 0,
                    'effort_variance': var_e,
                    'diversity_score': diversity,
                    'is_extreme': var_e < 0.05 and diversity < 0.1
                }
                conf = self._compute_confidence(window, 'repetition', contrast, rep_density, min_scenes)
                patterns.append({
                    'pattern_type': 'repetition',
                    'scene_range': [start, start + min_scenes - 1],
                    'confidence': conf,
                    'supporting_signals': ['low_effort_variance', 'low_diversity']
                })
                break # Only report first
        return patterns

    def _compute_feature_diversity(self, window_features):
        if len(window_features) < 2: return 0.0
        # ... (Simplified reimplementation of feature diversity logic) ...
        # For brevity, returning a placeholder calculation or fully implementing if critical.
        # Fully implementing core logic:
        try:
             chars = [f['referential_load']['active_character_count'] for f in window_features]
             char_var = sum(abs(chars[i]-chars[i+1]) for i in range(len(chars)-1)) / (len(window_features)*5.0)
             
             dials = [f['dialogue_dynamics']['turn_velocity'] for f in window_features]
             dial_chg = sum(abs(dials[i]-dials[i+1]) for i in range(len(dials)-1)) / len(dials)
             
             bounds = [f['structural_change']['event_boundary_score'] for f in window_features]
             bound_div = (max(bounds) - min(bounds)) / 100.0
             
             display = (0.3*char_var + 0.25*dial_chg + 0.25*bound_div)
             return min(1.0, display)
        except:
             return 0.5 # Fallback

    def _detect_sustained_demand(self, signals, len_factor, contrast, min_scenes):
        patterns = []
        THRESH = 0.6 * len_factor
        in_pat = False
        start = None
        
        for i, sig in enumerate(signals):
            if sig['attentional_signal'] > THRESH:
                if not in_pat: 
                    start = i
                    in_pat = True
            else:
                if in_pat:
                    end = i - 1
                    if end - start + 1 >= min_scenes:
                        conf = self._compute_confidence(signals[start:end+1], 'sustained', contrast, None, min_scenes)
                        patterns.append({
                            'pattern_type': 'sustained_attentional_demand',
                            'scene_range': [start, end],
                            'confidence': conf,
                            'supporting_signals': ['high_signal_persistence']
                        })
                    in_pat = False
        if in_pat and len(signals) - start >= min_scenes:
             conf = self._compute_confidence(signals[start:], 'sustained', contrast, None, min_scenes)
             patterns.append({
                'pattern_type': 'sustained_attentional_demand',
                'scene_range': [start, len(signals)-1],
                'confidence': conf,
                'supporting_signals': ['high_signal_persistence']
             })
        return patterns

    def _detect_limited_recovery(self, signals, contrast, min_scenes):
        patterns = []
        THRESH = 0.05
        count = 0
        start = None
        for i, sig in enumerate(signals):
            if sig['recovery_credit'] < THRESH:
                if count == 0: start = i
                count += 1
            else:
                if count >= min_scenes:
                    conf = self._compute_confidence(signals[start:i], 'limited', contrast, None, min_scenes)
                    patterns.append({
                        'pattern_type': 'limited_recovery',
                        'scene_range': [start, i-1],
                        'confidence': conf
                    })
                count = 0
        if count >= min_scenes:
              patterns.append({'pattern_type': 'limited_recovery', 'scene_range': [start, len(signals)-1], 'confidence': 'high'})
        return patterns

    def _detect_constructive_strain(self, signals, contrast, min_scenes):
        patterns = []
        for start in range(len(signals) - min_scenes + 1):
            window = signals[start:start+min_scenes]
            avg_s = statistics.mean([s['attentional_signal'] for s in window])
            avg_r = statistics.mean([s['recovery_credit'] for s in window])
            if avg_s > 0.6 and avg_r > 0.2:
                conf = self._compute_confidence(window, 'constructive', contrast, None, min_scenes)
                patterns.append({
                    'pattern_type': 'constructive_strain',
                    'scene_range': [start, start+min_scenes-1],
                    'confidence': conf
                })
                break
        return patterns

    def _detect_degenerative_fatigue(self, signals, contrast, acd_states, min_scenes):
        patterns = []
        for start in range(len(signals) - min_scenes + 1):
            window = signals[start:start+min_scenes]
            is_increasing = all(window[i+1]['attentional_signal'] >= window[i]['attentional_signal'] for i in range(len(window)-1))
            if is_increasing:
                avg_r = statistics.mean([s['recovery_credit'] for s in window])
                if avg_r < 0.1:
                    conf = self._compute_confidence(window, 'degenerative', contrast, None, min_scenes)
                    if acd_states and len(acd_states) > start:
                         w_acd = acd_states[start:start+min_scenes]
                         avg_c = statistics.mean([a['collapse_likelihood'] for a in w_acd])
                         if avg_c > 0.6 and conf == 'medium': conf = 'high'
                    patterns.append({
                        'pattern_type': 'degenerative_fatigue',
                        'scene_range': [start, start+min_scenes-1],
                        'confidence': conf
                    })
                    break
        return patterns

    def _apply_cumulative_escalation(self, patterns, signals, len_factor, contrast):
        escalated = []
        for p in patterns:
            if p['pattern_type'] == 'repetition':
                start, end = p['scene_range']
                base_e = signals[start]['instantaneous_effort']
                ext_end = end
                for i in range(end+1, len(signals)):
                    if abs(signals[i]['instantaneous_effort'] - base_e) < 0.2: ext_end = i
                    elif i > end + 2: break
                
                dur = ext_end - start + 1
                if dur >= 6:
                    escalated.append({
                        'pattern_type': 'sustained_attentional_demand',
                        'scene_range': [start, min(ext_end, len(signals)-1)],
                        'confidence': 'medium' if dur < 8 else 'high',
                        'supporting_signals': ['repetition_persistence']
                    })
        return escalated

    def _compute_confidence(self, window, ctx, contrast, rep_density, min_scenes):
        base = 0.7
        if rep_density and rep_density['is_extreme']: base += 0.25
        if contrast and contrast['is_low_contrast'] and not (rep_density and rep_density['is_extreme']): base -= 0.2
        
        vals = [s['attentional_signal'] for s in window]
        var = statistics.variance(vals) if len(vals) > 1 else 0.0
        if not rep_density:
             if var > 0.2: base -= 0.3
             elif var > 0.1: base -= 0.2
             
        if base >= 0.8: return 'high'
        elif base >= 0.5: return 'medium'
        return 'low'
