"""
Interpretation Agent - Logic, Reasoning, and Feedback
Consolidates: intent.py, ssf.py, uncertainty.py, ensemble_uncertainty.py, profiler.py, xai.py, scene_notes.py, suggestion.py
"""

import math
import statistics
import random
import copy
from . import dynamics_agent # Use consolidated dynamics for weighting reference if needed

# =============================================================================
# MEDIATION CONSTANTS
# =============================================================================
WRITER_NATIVE_TRANSLATIONS = {
    'sustained_attentional_demand': (
        "This run of scenes stays intense without a release valve — "
        "the audience may feel pushed without a moment to recover."
    ),
    'limited_recovery': (
        "Fatigue accumulates here. "
        "Without a clear breather, the audience's capacity to track detail may drop."
    ),
    'repetition': (
        "This stretch risks feeling like more of the same — "
        "the audience may stop registering escalation."
    ),
    'surprise_cluster': (
        "The rhythm spikes sharply here. "
        "Without setup, this intensity risks feeling jarring rather than impactful."
    ),
    'constructive_strain': (
        "This section demands heavy lifting. "
        "The audience is working hard to keep up — ensure the payoff is worth the effort."
    ),
    'degenerative_fatigue': {
        'drift': (
            "The audience may start to drift here — "
            "this stretch risks losing grip unless something resets their focus."
        ),
        'collapse': (
            "The mental load here is becoming heavy. "
            "The audience may struggle to track new information effectively."
        )
    }
}

BANNED_WORDS = {
    'good', 'bad', 'fix', 'improve', 'optimize', 'too long', 'too short',
    'slow', 'fast', 'weak', 'strong', 'problem', 'issue', 'ideal', 'optimal',
    'tips', 'suggestions', 'advice', 'should', 'must', 'need to'
}

ADS_DISCLAIMERS = [
    "This reflects one modeled first-pass experience.",
    "Other readers may differ.",
    "This is not a statement about effectiveness.",
    "Attention varies by reader; this model tracks median structural load."
]

# =============================================================================
# INTENT LOGIC (formerly intent.py)
# =============================================================================

class InterpretationAgent:
    """Methods for interpreting analytical data into human-usable insight."""

    def __init__(self):
        self.ALLOWED_INTENTS = {
            'intentionally exhausting',
            'intentionally confusing',
            'should feel smooth',
            'should feel tense',
            'experimental / anti-narrative'
        }

    def apply_writer_intent(self, input_data):
        """Writer Intent Immunity (formerly intent.run)"""
        patterns = input_data.get('patterns', [])
        writer_intents = input_data.get('writer_intent', [])
        
        validated_intents = [i for i in writer_intents if i.get('intent') in self.ALLOWED_INTENTS]
        
        surfaced, suppressed, notes = [], [], []
        
        # Consistency Check
        if len(validated_intents) >= 2:
            for i in range(len(validated_intents)):
                for j in range(i+1, len(validated_intents)):
                    ia, ib = validated_intents[i], validated_intents[j]
                    start_over = max(ia['scene_range'][0], ib['scene_range'][0])
                    end_over = min(ia['scene_range'][1], ib['scene_range'][1])
                    if start_over <= end_over and ia['intent'] != ib['intent']:
                        notes.append({'warning_type': 'intent_conflict', 'message': 'Conflicting intents', 'scene_range': [start_over, end_over]})

        if not validated_intents:
            return {'surfaced_patterns': patterns, 'suppressed_patterns': [], 'intent_alignment_notes': notes}
            
        for pattern in patterns:
            p_start, p_end = pattern['scene_range']
            overlap = self._check_overlap(p_start, p_end, validated_intents)
            
            if overlap['full']:
                suppressed.append(pattern)
                notes.append({'pattern_type': pattern['pattern_type'], 'intent': overlap['intent'], 'action': 'suppressed', 'scene_range': pattern['scene_range']})
            elif overlap['partial']:
                # Suppress overlapping part
                suppr_p = pattern.copy()
                suppr_p['scene_range'] = overlap['overlap_range']
                suppressed.append(suppr_p)
                
                # Surface remaining
                if overlap['remain_range']:
                    rem_p = pattern.copy()
                    rem_p['scene_range'] = overlap['remain_range']
                    rem_p['confidence'] = 'low' # Downgrade
                    surfaced.append(rem_p)
                
                notes.append({'pattern_type': pattern['pattern_type'], 'intent': overlap['intent'], 'action': 'partial_suppression'})
            else:
                surfaced.append(pattern)
                
        return {'surfaced_patterns': surfaced, 'suppressed_patterns': suppressed, 'intent_alignment_notes': notes}

    def _check_overlap(self, p_start, p_end, intents):
        for intent in intents:
            i_start, i_end = intent['scene_range']
            o_start = max(p_start, i_start)
            o_end = min(p_end, i_end)
            
            if o_start <= o_end:
                if i_start <= p_start and i_end >= p_end:
                    return {'full': True, 'partial': False, 'intent': intent['intent'], 'overlap_range': None, 'remain_range': None}
                else:
                    rem = [p_start, i_start-1] if p_start < i_start else [i_end+1, p_end]
                    return {'full': False, 'partial': True, 'intent': intent['intent'], 'overlap_range': [o_start, o_end], 'remain_range': rem}
        return {'full': False, 'partial': False, 'intent': None}

    # =========================================================================
    # SSF LOGIC (formerly ssf.py)
    # =========================================================================

    def analyze_silence(self, input_data):
        """Silence-as-Signal Formalization (formerly ssf.run)"""
        signals = input_data.get('temporal_signals', [])
        acd_states = input_data.get('acd_states', [])
        surfaced = input_data.get('surfaced_patterns', [])
        
        if surfaced:
            return {'is_silent': False, 'silence_confidence': None, 'explanation_key': None}
            
        if not signals:
            return {'is_silent': True, 'silence_confidence': 'low', 'explanation_key': 'no_data'}
            
        s_vals = [s['attentional_signal'] for s in signals]
        r_vals = [s['recovery_credit'] for s in signals]
        
        max_s, avg_s = max(s_vals), statistics.mean(s_vals)
        avg_r = statistics.mean(r_vals)
        max_c = max(a['collapse_likelihood'] for a in acd_states) if acd_states else 0.0
        max_d = max(a['drift_likelihood'] for a in acd_states) if acd_states else 0.0
        
        metrics = {'max_strain': round(max_s,3), 'avg_recovery': round(avg_r,3)}
        
        high_conf = (max_s < 0.6 and avg_r > 0.15 and max_c < 0.5)
        med_conf = (max_s < 0.8 and (avg_r > 0.1 or avg_s < 0.3))
        
        conf = 'low'
        key = 'marginal_strain'
        
        if high_conf: 
            conf, key = 'high', 'stable_continuity'
            if max_d > 0.7: key = 'stable_but_drifting'
        elif med_conf: 
            conf, key = 'medium', 'self_correcting'
            
        return {'is_silent': True, 'silence_confidence': conf, 'stability_metrics': metrics, 'explanation_key': key}

    # =========================================================================
    # UNCERTAINTY LOGIC (formerly uncertainty.py & ensemble_uncertainty.py)
    # =========================================================================

    def calculate_uncertainty(self, input_data):
        """Analytical Uncertainty (formerly uncertainty.run)"""
        signals = input_data.get('temporal_signals', [])
        features = input_data.get('features', [])
        if not signals: return []
        
        outputs = []
        for i, sig in enumerate(signals):
            s_val = sig['attentional_signal']
            feat = features[i]
            
            ent = feat.get('entropy_score', 0)
            u_ent = max(0.0, (ent - 3.0) * 0.05)
            
            micro = feat.get('micro_structure', [])
            u_micro = statistics.stdev([m['word_count'] for m in micro])/50.0 if len(micro) > 1 else 0.1
            
            u_vol = 0.0
            if i >= 3:
                vals = [x['attentional_signal'] for x in signals[i-3:i]]
                u_vol = statistics.stdev(vals) if len(vals) > 1 else 0.0
                
            sigma = min(0.25, 0.05 + 0.3*u_ent + 0.2*u_micro + 0.5*u_vol)
            
            outputs.append({
                'scene_index': sig['scene_index'],
                'sigma': round(sigma, 3),
                'ci_upper': round(s_val + 1.96*sigma, 3),
                'ci_lower': round(max(0, s_val - 1.96*sigma), 3)
            })
        return outputs

    def calculate_ensemble_uncertainty(self, input_data):
        """Ensemble uncertainty using bagging (formerly ensemble_uncertainty.run)"""
        iterations = input_data.get('iterations', 20)
        base_trace = input_data.get('base_trace', [])
        
        if not base_trace: return []
        
        ensemble_results = []
        for _ in range(iterations):
            trace = []
            for pt in base_trace:
                noise = random.gauss(0, 0.07)
                trace.append(max(0, min(1, pt['attentional_signal'] + noise)))
            ensemble_results.append(trace)
            
        output = []
        for i in range(len(base_trace)):
            vals = [run[i] for run in ensemble_results]
            mean = statistics.mean(vals)
            std = statistics.stdev(vals) if len(vals) > 1 else 0.0
            
            output.append({
                'scene_index': i,
                'mean': round(mean, 3),
                'lower_bound_95': round(max(0, mean - 2*std), 3),
                'upper_bound_95': round(min(1, mean + 2*std), 3)
            })
        return output

    # =========================================================================
    # PROFILER LOGIC (formerly profiler.py)
    # =========================================================================

    def get_cognitive_profile(self, profile_name="general"):
        """Returns cognitive physics parameters"""
        profiles = {
            'general': {'lambda_base': 0.85, 'beta_recovery': 0.3, 'fatigue_threshold': 1.0, 'coherence_weight': 0.15},
            'cinephile': {'lambda_base': 0.90, 'beta_recovery': 0.4, 'fatigue_threshold': 1.3, 'coherence_weight': 0.10},
            'distracted': {'lambda_base': 0.75, 'beta_recovery': 0.2, 'fatigue_threshold': 0.8, 'coherence_weight': 0.30},
            'child': {'lambda_base': 0.70, 'beta_recovery': 0.5, 'fatigue_threshold': 0.6, 'coherence_weight': 0.40}
        }
        return profiles.get(profile_name.lower(), profiles['general'])

    # =========================================================================
    # XAI LOGIC (formerly xai.py)
    # =========================================================================

    def generate_explanations(self, data):
        """Decompose effort signal into drivers (formerly xai.run)"""
        features = data.get('features', [])
        sem_scores = data.get('semantic_scores', [])
        syn_scores = data.get('syntax_scores', [])
        
        output = []
        # Weights (reflecting temporal defaults)
        w_cog, w_emo = 0.55, 0.45
        
        for i, scene in enumerate(features):
            sem = sem_scores[i] if i < len(sem_scores) else 0.0
            syn = syn_scores[i] if i < len(syn_scores) else 0.0
            
            # Raw Inputs
            ref = scene['referential_load']
            struct = scene['structural_change']
            dial = scene['dialogue_dynamics']
            vis = scene['visual_abstraction']
            ling = scene['linguistic_load']
            
            # Calculation
            raw_struct = ((ref['active_character_count']/10.0 + ref['character_reintroductions']/5.0)*0.3 + 
                          (ling['sentence_length_variance']/20.0)*0.3 + (struct['event_boundary_score']/100.0)*0.25 + 
                          (dial['speaker_switches']/20.0)*0.15)
            
            raw_motion = (vis['action_lines']/50.0 + vis['continuous_action_runs']/10.0)
            raw_dial = (dial['dialogue_turns']/50.0)*0.6 + (ling['sentence_count']/50.0)*0.4
            
            # Weighted Contributions
            c_struct = w_cog * 0.6 * raw_struct
            c_syn = w_cog * 0.2 * syn
            c_sem = w_cog * 0.2 * sem
            c_motion = w_emo * 0.3 * raw_motion
            c_dial = w_emo * 0.7 * raw_dial
            
            total = c_struct + c_syn + c_sem + c_motion + c_dial
            if total < 0.001: total = 1.0
            
            drivers = {
                'Structure': round(c_struct/total, 2),
                'Syntax': round(c_syn/total, 2),
                'Semantics': round(c_sem/total, 2),
                'Motion': round(c_motion/total, 2),
                'Dialogue': round(c_dial/total, 2)
            }
            
            output.append({
                'scene_index': scene['scene_index'],
                'drivers': drivers,
                'dominant_driver': max(drivers, key=drivers.get)
            })
        return output

    # =========================================================================
    # SCENE NOTES LOGIC (formerly scene_notes.py)
    # =========================================================================

    def generate_scene_notes(self, data):
        """Generate actionable feedback (formerly scene_notes.run)"""
        scenes = data.get('scenes', [])
        trace = data.get('temporal_trace', [])
        valence = data.get('valence_scores', [])
        syntax = data.get('syntax_scores', [])
        
        feedback = {}
        
        for i, scene in enumerate(scenes):
            notes = []
            tp = trace[i] if i < len(trace) else {}
            v = valence[i] if i < len(valence) else 0
            s = syntax[i] if i < len(syntax) else 0
            tsn = tp.get('attentional_signal', 0)
            
            if tsn < 0.3: notes.append({'severity': 'warning', 'issue': '⚠️ Low Conflict', 'suggestion': 'Add obstacle/stakes.'})
            if v < -0.2: notes.append({'severity': 'info', 'issue': '😐 Heavy Tone', 'suggestion': 'Dark. Consider relief if not intended.'})
            if s > 0.7: notes.append({'severity': 'warning', 'issue': '🔴 Complex Language', 'suggestion': 'Simplify sentences/add action.'})
            
            d_lines = [l for l in scene['lines'] if l.get('tag') == 'D']
            if any(len(l['text'].split()) > 40 for l in d_lines):
                notes.append({'severity': 'warning', 'issue': '💬 Long Monologue', 'suggestion': 'Break up long speech.'})
            
            if not d_lines and len(scene['lines']) > 3:
                 notes.append({'severity': 'info', 'issue': '🔇 Silent Scene', 'suggestion': 'Pure visual. Add dialogue if clarity needed.'})
            
            if tsn > 0.7 and v > 0.2:
                 notes.append({'severity': 'info', 'issue': '🎢 Tonal Mismatch?', 'suggestion': 'High tension + Positive tone. Check emotion.'})
            
            if notes: feedback[i] = notes
            
        return feedback

    # =========================================================================
    # SUGGESTION LOGIC (formerly suggestion.py)
    # =========================================================================

    def generate_suggestions(self, temporal_trace):
        """Generate structural strategies (formerly suggestion.run)"""
        suggestions = []
        if not temporal_trace: return {}
        
        for pt in temporal_trace:
            eff = pt.get('instantaneous_effort', 0.5)
            # state = pt.get('affective_state', 'Normal') # Assume state is calculated elsewhere or implied
            
            sugg = None
            if eff < 0.2:
                sugg = {
                    'scene': pt['scene_index'],
                    'diagnosis': "Risk of Boredom",
                    'strategy': "Inject Kinetic Energy",
                    'tactics': ["Cut sentence length", "Add visual words", "Interrupt dialogue"]
                }
            elif eff > 0.85:
                sugg = {
                    'scene': pt['scene_index'],
                    'diagnosis': "Risk of Burnout",
                    'strategy': "Induce Recovery",
                    'tactics': ["Insert visual rest", "Simplify syntax", "Lower social tension"]
                }
            
            if sugg and random.random() < 0.3:
                suggestions.append(sugg)
                
        return {'structural_repair_strategies': suggestions[:3]}

    # =========================================================================
    # MEDIATION LOGIC (formerly mediation.py)
    # =========================================================================

    def mediate_experience(self, input_data):
        """
        Translate patterns into writer-safe, question-first reflections.
        (formerly mediation.run)
        """
        surfaced = input_data.get('surfaced_patterns', [])
        suppressed = input_data.get('suppressed_patterns', [])
        alignment_notes = input_data.get('intent_alignment_notes', [])
        acd_states = input_data.get('acd_states', []) 
        ssf_analysis = input_data.get('ssf_analysis', {}) 
        
        reflections = []
        
        # === AEKS: Alert Escalation Kill-Switch (Constraint) ===
        total_scenes = 100 
        if acd_states:
            total_scenes = len(acd_states)
            
        max_alerts = max(3, int(total_scenes / 12))
        
        # Deduplicate overlapping patterns
        surfaced = self._deduplicate_patterns(surfaced)
        
        if len(surfaced) > max_alerts:
            conf_map = {'high': 3, 'medium': 2, 'low': 1}
            surfaced.sort(key=lambda x: conf_map.get(x.get('confidence'), 0), reverse=True)
            surfaced = surfaced[:max_alerts]
        
        # Generate reflections
        for pattern in surfaced:
            reflection = self._generate_reflection(pattern, acd_states, total_scenes)
            reflections.append(reflection)
        
        # Handle silence
        silence_explanation = None
        if not surfaced:
            silence_explanation = self._generate_silence_explanation(suppressed, alignment_notes, ssf_analysis)
        
        # Generate intent acknowledgments
        intent_acknowledgments = []
        for note in alignment_notes:
            ack = self._generate_intent_acknowledgment(note)
            intent_acknowledgments.append(ack)
            
        return {
            'reflections': reflections,
            'silence_explanation': silence_explanation,
            'intent_acknowledgments': intent_acknowledgments,
            'total_surfaced': len(surfaced), 
            'total_suppressed': len(suppressed),
            'aeks_active': len(input_data.get('surfaced_patterns', [])) > max_alerts 
        }

    def _deduplicate_patterns(self, patterns):
        """Prioritize: Degenerative > Demand > Recovery > Repetition"""
        if not patterns: return []
        priority = {'degenerative_fatigue': 1, 'sustained_attentional_demand': 2, 
                   'limited_recovery': 3, 'surprise_cluster': 4, 'repetition': 5}
        patterns.sort(key=lambda p: priority.get(p.get('pattern_type'), 10))
        unique_patterns = []
        for p in patterns:
            is_redundant = False
            p_start, p_end = p.get('scene_range', [0, 0])
            p_len = p_end - p_start + 1
            for existing in unique_patterns:
                e_start, e_end = existing.get('scene_range', [0, 0])
                overlap_start = max(p_start, e_start)
                overlap_end = min(p_end, e_end)
                if overlap_start <= overlap_end:
                    overlap_len = overlap_end - overlap_start + 1
                    if overlap_len / p_len > 0.8:
                        is_redundant = True
                        break
            if not is_redundant: unique_patterns.append(p)
        return unique_patterns

    def _generate_reflection(self, pattern, acd_states=None, total_scenes=100):
        pattern_type = pattern.get('pattern_type', 'unknown')
        scene_range = pattern.get('scene_range', [0, 0])
        confidence = pattern.get('confidence', 'low')
        
        reflection_text = "This section creates a unique texture that may require specific audience tuning."
        
        if pattern_type == 'degenerative_fatigue' and acd_states:
            start, end = scene_range
            window_acd = [state for state in acd_states if start <= state['scene_index'] <= end]
            avg_drift = sum(s['drift_likelihood'] for s in window_acd) / len(window_acd) if window_acd else 0.5
            avg_collapse = sum(s['collapse_likelihood'] for s in window_acd) / len(window_acd) if window_acd else 0.5
            
            if avg_drift > avg_collapse:
                 reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['drift']
            else:
                 reflection_text = WRITER_NATIVE_TRANSLATIONS['degenerative_fatigue']['collapse']
        elif pattern_type in WRITER_NATIVE_TRANSLATIONS:
            reflection_text = WRITER_NATIVE_TRANSLATIONS[pattern_type]
            
        if total_scenes > 30:
            start, end = scene_range
            if end / max(1, total_scenes) > 0.8:
                reflection_text += " (Deep in the script, this requires even more energy to sustain.)"
                
        return {'scene_range': scene_range, 'reflection': reflection_text, 'confidence': confidence}

    def _generate_silence_explanation(self, suppressed, alignment_notes, ssf_analysis=None):
        if alignment_notes:
            return "Silence here means the system sees exactly what you intended. Your declared intent matches the audience load."
        
        if ssf_analysis and ssf_analysis.get('is_silent'):
            key = ssf_analysis.get('explanation_key')
            if key == 'stable_continuity':
                 return "The experience here is rock stable. Effort and recovery are balanced—the audience is breathing naturally."
            elif key == 'self_correcting':
                return "The flow feels self-correcting. Whenever tension rises, a release valve opens naturally."
            elif key == 'stable_but_drifting':
                 return "The experience is stable, though the water is very still. No strain, but also low demand."
        
        if suppressed: return "Patterns were suppressed based on provided constraints."
        return "The attentional flow is stable. No red flags, no drag, no exhaustion. A clean reading."

    def _generate_intent_acknowledgment(self, note):
        intent = note.get('intent', 'your declared intent')
        start, end = note.get('scene_range', [0, 0])
        return f"You marked scenes {start}–{end} as '{intent}'. This matches the signal perfectly."

