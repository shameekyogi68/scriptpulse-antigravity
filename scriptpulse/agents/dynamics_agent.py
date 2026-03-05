"""
Dynamics Agent - Simplified & MCA-Defensible Version
The Core Simulation Engine (The "Heart" of ScriptPulse)
Calculates: Attentional Signal (S) based on Effort (E) and Recovery (R)
Equation: S[t] = Effort[t] + (Lambda * S[t-1]) - Recovery[t]
"""

import math
import statistics
import json
import os

class DynamicsAgent:
    """Core Mathematical Simulation Engine - High Fidelity, Low Complexity"""
    
    def __init__(self):
        # Base Sensitivity Parameters (Configurable)
        self.LAMBDA = 0.85 # Decay rate (Higher = sustains interest longer)
        self.BETA = 0.3    # Recovery rate (Higher = recovers faster)
        self.R_MAX = 0.6   # Max recovery per scene
        
    def run_simulation(self, input_data, genre='drama', **kwargs):
        features = input_data.get('features', [])
        if not features: return []
        
        signals = []
        prev_signal = 0.5  # Neutral starting point
        
        for i, feat in enumerate(features):
            # 1. Calculate Instantaneous Effort (E)
            # COMBINES: Complexity (Syntactic) + Rhythm (Dialogue) + Action (Visual)
            # E = (Syntactic * 0.4) + (Characters * 0.3) + (Entropy * 0.3)
            
            cog_load = (feat.get('linguistic_load', {}).get('sentence_length_variance', 0) / 100.0 * 0.4 +
                       feat.get('referential_load', {}).get('active_character_count', 0) / 10.0 * 0.3 +
                       feat.get('entropy_score', 0) / 10.0 * 0.3)
            
            emo_load = (feat.get('dialogue_dynamics', {}).get('turn_velocity', 0) * 0.4 +
                       min(1.0, feat.get('visual_abstraction', {}).get('action_lines', 0) / 20.0) * 0.4 +
                       feat.get('referential_load', {}).get('entity_churn', 0) * 0.2)
            
            # Combine to Effort
            effort = (cog_load * 0.6 + emo_load * 0.4)
            effort = min(1.0, max(0.0, effort))
            
            # 2. Calculate Recovery Credit (R)
            # Recovery happens in scenes with low effort
            recovery = max(0, (self.R_MAX - effort)) * self.BETA
            
            # 3. Update Attentional Signal (S)
            # The Core Equation: S_t = E_t + (λ * S_{t-1}) - R_t
            # This is a first-order autoregressive state simulation.
            signal = effort + (self.LAMBDA * prev_signal) - recovery
            signal = min(1.0, max(0.0, signal)) # Keep in [0,1] range
            
            # 4. Narrative Nuance (For UI logic)
            action_count = feat.get('visual_abstraction', {}).get('action_lines', 0)
            dial_count = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            
            out_sig = {
                'scene_index': feat['scene_index'],
                'instantaneous_effort': round(effort, 3),
                'attentional_signal': round(signal, 3),
                'recovery_credit': round(recovery, 3),
                'fatigue_state': round(max(0.0, signal - 0.7), 3),
                'conflict': round(min(1.0, effort * 1.2), 3),
                'stakes': round(effort * 0.8, 3),
                'agency': round(feat.get('referential_load', {}).get('active_character_count', 0) * 0.15, 3),
                'action_density': round(action_count / max(1, action_count + dial_count), 2),
                'sentiment': 0.0, # Placeholder
                'narrative_position': round(i / max(1, len(features)), 3)
            }
            
            # Forward feed all relevant features to temporal trace needed for interpretation
            for k,v in feat.items():
                if k not in out_sig and k not in ['linguistic_load', 'dialogue_dynamics', 'visual_abstraction', 'referential_load', 'entropy_score', 'scene_vocabulary']:
                    out_sig[k] = v
                    
            signals.append(out_sig)
            prev_signal = signal
            
        return signals

    def calculate_acd_states(self, input_data):
        """Simplified Attention Collapse/Drift Logic"""
        signals = input_data.get('temporal_signals', [])
        states = []
        for s in signals:
            signal = s['attentional_signal']
            effort = s['instantaneous_effort']
            
            state = 'stable'
            if signal > 0.8: state = 'collapse' # Too much to handle
            elif signal < 0.2: state = 'drift'   # Boring/Bland
            
            states.append({
                'scene_index': s['scene_index'],
                'primary_state': state,
                'collapse_likelihood': round(max(0.0, signal - 0.7), 3),
                'drift_likelihood': round(max(0.0, 0.3 - signal), 3)
            })
        return states

    def apply_long_range_fatigue(self, input_data):
        """Simple Fatigue Modifier"""
        signals = input_data.get('temporal_signals', [])
        return signals

    def detect_patterns(self, input_data):
        """Standard experiential patterns based on signal windows"""
        signals = input_data.get('temporal_signals', [])
        patterns = []
        if len(signals) < 3: return []
        
        for i in range(len(signals) - 2):
            window = signals[i:i+3]
            sigs = [w['attentional_signal'] for w in window]
            
            # Fatigue Detection
            if all(s > 0.7 for s in sigs):
                patterns.append({'pattern_type': 'sustained_attentional_demand', 'scene_range': [i, i+2], 'confidence': 'medium'})
                break # only one
        
        return patterns
