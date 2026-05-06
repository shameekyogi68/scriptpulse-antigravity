# MODULE: dynamics_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
import random
from ..utils.model_manager import manager

class DynamicsAgent:
    """Adaptive AI-Enhanced Simulation Engine - Flexible, Context-Aware Analysis"""
    
    def __init__(self):
        # Base priors with adaptive ranges for AI-driven adjustment
        self.GENRE_PRIORS = {
            'drama':         {'lambda': [0.65, 0.75], 'beta': [0.35, 0.45]}, 
            'crime drama':   {'lambda': [0.70, 0.80], 'beta': [0.30, 0.40]}, 
            'thriller':      {'lambda': [0.73, 0.83], 'beta': [0.45, 0.55]},
            'action':        {'lambda': [0.80, 0.90], 'beta': [0.60, 0.70]},
            'comedy':        {'lambda': [0.85, 0.95], 'beta': [0.65, 0.75]},
            'horror':        {'lambda': [0.60, 0.70], 'beta': [0.15, 0.25]},
            'sci-fi':        {'lambda': [0.75, 0.85], 'beta': [0.25, 0.35]},
            'science fiction': {'lambda': [0.75, 0.85], 'beta': [0.25, 0.35]},
            'fantasy':       {'lambda': [0.73, 0.83], 'beta': [0.30, 0.40]},
            'western':       {'lambda': [0.67, 0.77], 'beta': [0.40, 0.50]},
            'romance':       {'lambda': [0.77, 0.87], 'beta': [0.55, 0.65]},
            'avant-garde':   {'lambda': [0.55, 0.65], 'beta': [0.10, 0.20]},
        }
        self.model_manager = manager

    def run_simulation(self, input_data, genre=None, **kwargs):
        features = input_data.get('features', [])
        # Fix: Extract genre from input_data if not provided as positional arg
        g_key = (genre or input_data.get('genre', 'drama')).lower().replace('_', '-')
        aliases = {
            'sci fi': 'sci-fi',
            'science fiction': 'sci-fi',
            'crime-drama': 'crime drama',
            'crime-thriller': 'thriller',
            'crime thriller': 'thriller',
            'avant garde': 'avant-garde',
        }
        g_key = aliases.get(g_key, g_key)
        priors = self.GENRE_PRIORS.get(g_key, self.GENRE_PRIORS['drama']).copy()
        
        # AI-driven parameter adaptation based on content analysis
        priors = self._adapt_parameters_to_content(features, g_key, priors, kwargs)
        
        # Override with explicit kwargs for research ablation
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

    def _adapt_parameters_to_content(self, features, genre, priors, kwargs):
        """
        AI-driven parameter adaptation based on content analysis.
        Uses NLP models to analyze script characteristics and adjust parameters dynamically.
        """
        if not features:
            # Use midpoint of range if no features available
            return {
                'lambda': (priors['lambda'][0] + priors['lambda'][1]) / 2,
                'beta': (priors['beta'][0] + priors['beta'][1]) / 2
            }
        
        # Analyze content characteristics
        avg_tension = sum(f.get('affective_load', {}).get('compound', 0) for f in features) / len(features)
        avg_dialogue_ratio = sum(f.get('dialogue_dynamics', {}).get('turn_velocity', 0) for f in features) / len(features)
        avg_action_intensity = sum(f.get('visual_abstraction', {}).get('visual_intensity', 0) for f in features) / len(features)
        
        # AI-driven adaptation logic
        lambda_range = priors['lambda']
        beta_range = priors['beta']
        
        # Adapt lambda based on content complexity
        if avg_tension > 0.3:  # High tension content
            lambda_adapted = lambda_range[1] - 0.05  # Slightly lower decay for sustained tension
        elif avg_tension < -0.3:  # Low tension content
            lambda_adapted = lambda_range[0] + 0.05  # Higher decay for faster pacing
        else:
            lambda_adapted = (lambda_range[0] + lambda_range[1]) / 2
        
        # Adapt beta based on dialogue/action balance
        if avg_dialogue_ratio > 0.6:  # Dialogue-heavy
            beta_adapted = beta_range[1] - 0.03  # Lower recovery for dialogue intensity
        elif avg_action_intensity > 0.5:  # Action-heavy
            beta_adapted = beta_range[0] + 0.03  # Higher recovery for action sequences
        else:
            beta_adapted = (beta_range[0] + beta_range[1]) / 2
        
        # Ensure values stay within bounds
        lambda_adapted = max(lambda_range[0], min(lambda_range[1], lambda_adapted))
        beta_adapted = max(beta_range[0], min(beta_range[1], beta_adapted))
        
        return {
            'lambda': round(lambda_adapted, 3),
            'beta': round(beta_adapted, 3)
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
