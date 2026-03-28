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
        # Priors as per PAPER_METHODS.md v1.3
        self.GENRE_PRIORS = {
            'drama':         {'lambda': 0.75, 'beta': 0.45}, # Higher recovery, lower retention for valleys
            'crime drama':   {'lambda': 0.80, 'beta': 0.40}, 
            'thriller':      {'lambda': 0.75, 'beta': 0.45},
            'action':        {'lambda': 0.78, 'beta': 0.50},
            'comedy':        {'lambda': 0.80, 'beta': 0.60},
            'horror':        {'lambda': 0.70, 'beta': 0.25},
            'sci-fi':        {'lambda': 0.82, 'beta': 0.35},
        }

    def run_simulation(self, input_data, genre=None, **kwargs):
        features = input_data.get('features', [])
        # Fix: Extract genre from input_data if not provided as positional arg
        g_key = (genre or input_data.get('genre', 'drama')).lower()
        priors = self.GENRE_PRIORS.get(g_key, self.GENRE_PRIORS['drama']).copy()
        
        # Override with kwargs for hyperparameter tuning / research ablation
        if 'lambda' in kwargs: priors['lambda'] = kwargs['lambda']
        if 'beta' in kwargs: priors['beta'] = kwargs['beta']
        
        if not features: return []
        
        signals = []
        prev_signal = 0.25  # Neutral-low starting point for establishing tone
        
        for i, feat in enumerate(features):
            # 1. Extraction & Feature Normalization
            norm_velocity = feat.get('dialogue_dynamics', {}).get('turn_velocity', 0)
            switches = feat.get('dialogue_dynamics', {}).get('speaker_switches', 0)
            norm_action = feat.get('visual_abstraction', {}).get('visual_intensity', 0)
            
            # Conflict & Stakes (The primary drivers of Drama)
            # Switches normalized by expected conversational density (8 switches per scene is active)
            norm_switches = min(1.0, switches / 8.0)
            dialogue_momentum = (norm_velocity * 0.3 + norm_switches * 0.7)
            
            affective = feat.get('affective_load', {})
            comp_sentiment = abs(affective.get('compound', 0)) if isinstance(affective, dict) else 0
            
            # Real conflict and stakes calculations used for both Effort and Output
            actual_conflict = (dialogue_momentum * 0.6) + (max(0, -affective.get('compound', 0)) * 0.4)
            
            stakes_breakdown = feat.get('stakes_taxonomy', {}).get('breakdown', {})
            dominant_stakes_value = max(stakes_breakdown.values()) if stakes_breakdown else norm_action
            actual_stakes = (norm_action * 0.5) + (dominant_stakes_value * 0.5)

            # 2. Effort (Tension Contribution)
            # Narrative Drive now weights Conflict and Stakes much heavier than raw dialogue volume
            narrative_drive = (actual_conflict * 0.5 + actual_stakes * 0.4 + comp_sentiment * 0.1)
            
            # Scene Density (Cognitive Load): Moderate contribution
            norm_chars = min(1.0, feat.get('referential_load', {}).get('active_character_count', 0) / 8.0)
            norm_entropy = min(1.0, feat.get('entropy_score', 0) / 12.0)
            scene_density = (norm_chars * 0.4 + norm_entropy * 0.6)
            
            # Lower base effort (0.05) allows for deep valleys
            raw_effort = (narrative_drive * 0.85 + scene_density * 0.15)
            effort = 0.05 + (raw_effort * 0.9)
            
            # 3. Update Attentional Signal (S)
            decay = priors['lambda']
            beta = priors['beta']
            
            # Recovery Credit (R_t)
            # Prestige dramas need "The Valley" — if effort is low, recovery is boosted
            recovery = (1.0 - effort) * beta
            if effort < 0.25:
                recovery *= 1.5 # Extra recovery for quiet/domestic scenes
            
            # Update state with decay (The "Memory" of the simulation)
            signal = (prev_signal * decay) + effort - recovery
            
            # Micro-spikes for visceral visual peaks (Action sequences)
            if norm_action > 0.7:
                signal += 0.15
                
            signal = min(0.98, max(0.05, signal)) 
            
            # 4. Contextual Nuance (For UI/Interpretation)
            action_count = feat.get('visual_abstraction', {}).get('action_lines', 0)
            dial_count = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            sentiment_val = affective.get('compound', 0)
            
            # Resonance occurs when high conflict meets strong emotional valence
            cognitive_resonance = min(1.0, (actual_conflict * 0.4) + (effort * 0.4) + (0.3 if abs(sentiment_val) > 0.6 else 0.0))
            
            # Extract aggregate agency from character scene vectors
            scene_agency = 0.0
            arcs = feat.get('character_scene_vectors', {})
            if arcs:
                scene_agency = sum(v.get('agency', 0) for v in arcs.values()) / len(arcs)
                
            out_sig = {
                'scene_index': feat['scene_index'],
                'instantaneous_effort': round(effort, 3),
                'attentional_signal': round(signal, 3),
                'recovery_credit': round(recovery, 3),
                'fatigue_state': round(max(0.0, signal - 0.7), 3),
                'cognitive_resonance': round(cognitive_resonance, 3),
                'conflict': round(min(1.0, actual_conflict), 3),
                'stakes': round(min(1.0, actual_stakes), 3),
                'agency': round(scene_agency, 3),
                'action_density': round(action_count / max(1, action_count + dial_count), 2),
                'sentiment': round(sentiment_val, 3),
                'narrative_position': round(i / max(1, len(features)), 3),
                # Explicit dialogue/action counts for writer_agent's global ratio calculation
                'dialogue_action_ratio': {
                    'dialogue_lines': dial_count,
                    'action_lines': action_count
                }
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
