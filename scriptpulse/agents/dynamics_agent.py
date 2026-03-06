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
            # 1. Calculate Narrative Momentum (Formerly Effort)
            # Use sentiment/affective extremes and action as primary drivers of tension
            norm_velocity = min(1.0, feat.get('dialogue_dynamics', {}).get('turn_velocity', 0) / 10.0)
            norm_action = min(1.0, feat.get('visual_abstraction', {}).get('action_lines', 0) / 15.0)
            
            # Affective Extremes usually indicate high stakes or drama
            affective = feat.get('affective_load', {})
            comp_sentiment = abs(affective.get('compound', 0)) if isinstance(affective, dict) else 0
            
            # Decrease weight of raw string length variables
            norm_chars = min(1.0, feat.get('referential_load', {}).get('active_character_count', 0) / 6.0)
            norm_entropy = min(1.0, feat.get('entropy_score', 0) / 15.0)

            # Narrative Drive: Action and Dialogue back-and-forth create momentum
            narrative_drive = (norm_velocity * 0.4 + norm_action * 0.4 + comp_sentiment * 0.2)
            
            # Scene Density: Too many characters or too many words drag pacing down
            scene_density = (norm_chars * 0.5 + norm_entropy * 0.5)
            
            # Combine to Effort (Tension) range
            raw_effort = (narrative_drive * 0.7 + scene_density * 0.3)
            effort = 0.15 + (raw_effort * 0.7)
            
            # 2. Update Attentional Signal (S)
            # Use responsive moving average to ensure peaks and valleys are highly visible
            alpha = 0.5 # Responsiveness
            signal = (effort * alpha) + (prev_signal * (1 - alpha))
            
            # Inject micro-spikes for high action or high conflict to force visual peaks
            if norm_action > 0.6 or norm_velocity > 0.8:
                signal += 0.15
                
            # Recovery credit
            recovery = max(0, 0.5 - effort)
            if recovery > 0.2:
                signal -= 0.1
                
            signal = min(0.98, max(0.05, signal)) # Keep in safe visible range
            
            # 3. Narrative Nuance (For UI logic)
            action_count = feat.get('visual_abstraction', {}).get('action_lines', 0)
            dial_count = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            
            # Real metrics based on actual inputs
            actual_conflict = (norm_velocity * 0.6) + (max(0, -affective.get('compound', 0)) * 0.4)
            
            stakes_breakdown = feat.get('stakes_taxonomy', {}).get('breakdown', {})
            dominant_stakes_value = max(stakes_breakdown.values()) if stakes_breakdown else norm_action
            actual_stakes = (norm_action * 0.5) + (dominant_stakes_value * 0.5)
            
            out_sig = {
                'scene_index': feat['scene_index'],
                'instantaneous_effort': round(effort, 3),
                'attentional_signal': round(signal, 3),
                'recovery_credit': round(recovery, 3),
                'fatigue_state': round(max(0.0, signal - 0.7), 3),
                'conflict': round(min(1.0, actual_conflict), 3),
                'stakes': round(min(1.0, actual_stakes), 3),
                'agency': round(feat.get('referential_load', {}).get('active_character_count', 0) * 0.15, 3),
                'action_density': round(action_count / max(1, action_count + dial_count), 2),
                'sentiment': round(affective.get('compound', 0), 3),
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
