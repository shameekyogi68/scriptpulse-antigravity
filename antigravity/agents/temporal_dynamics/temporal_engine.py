#!/usr/bin/env python3
"""
Temporal Dynamics Agent

Models attentional demand accumulation and recovery over time using
deterministic temporal dynamics with fatigue carryover and recovery.
"""

import json
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TemporalSignal:
    """Temporal dynamics for a single scene"""
    scene_index: int
    instantaneous_effort: float
    attentional_signal: float
    recovery_credit: float
    fatigue_state: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'scene_index': self.scene_index,
            'instantaneous_effort': round(self.instantaneous_effort, 3),
            'attentional_signal': round(self.attentional_signal, 3),
            'recovery_credit': round(self.recovery_credit, 3),
            'fatigue_state': self.fatigue_state
        }


class TemporalEngine:
    """Computes temporal dynamics from feature vectors"""
    
    # Fixed parameters (not learned)
    LAMBDA = 0.85  # Fatigue carryover
    BETA = 0.3     # Recovery rate from low effort
    GAMMA = 0.2    # Recovery from structural boundaries
    DELTA = 0.1    # Recovery from compression
    ALPHA = 0.05   # Fatigue wall coefficient
    
    E_THRESHOLD = 0.4    # Low-effort threshold
    S_MAX = 2.0          # Fatigue wall threshold
    R_MAX = 0.5          # Maximum recovery per scene
    
    N_OPENING = 10       # Opening buffer scenes
    N_ENDING_PERCENT = 0.05  # Ending buffer (5% of total)
    
    # Fixed weights for effort calculation
    W_LINGUISTIC = 0.25
    W_DIALOGUE = 0.20
    W_VISUAL = 0.30
    W_REFERENTIAL = 0.15
    W_STRUCTURAL = 0.10
    
    def __init__(self, encoded_scenes: List[Dict]):
        """
        Initialize temporal engine.
        
        Args:
            encoded_scenes: List of scene feature dictionaries from encoding agent
        """
        self.scenes = encoded_scenes
        self.num_scenes = len(encoded_scenes)
        
        # Normalize features within script
        self.normalized_features = self._normalize_features()
    
    def compute_temporal_dynamics(self) -> List[TemporalSignal]:
        """
        Compute temporal dynamics for all scenes.
        
        Returns:
            List of TemporalSignal objects
        """
        signals = []
        prev_signal = 0.0
        
        for i, scene in enumerate(self.scenes):
            scene_idx = scene['scene_index']
            
            # Compute instantaneous effort
            effort = self._compute_instantaneous_effort(i)
            
            # Compute recovery credit
            recovery = self._compute_recovery(i, effort)
            
            # Compute effective lambda with buffers
            lambda_eff = self._compute_effective_lambda(i)
            
            # Apply canonical equation: S[i] = E[i] + λ·S[i-1] - R[i]
            if i == 0:
                signal = effort  # First scene has no carryover
            else:
                signal = effort + lambda_eff * prev_signal - recovery
            
            # Apply nonlinear fatigue wall
            if signal > self.S_MAX:
                excess = signal - self.S_MAX
                signal = signal + self.ALPHA * (excess ** 2)
            
            # Ensure non-negative
            signal = max(0.0, signal)
            
            # Classify fatigue state
            fatigue_state = self._classify_fatigue_state(signal)
            
            # Create temporal signal
            temp_signal = TemporalSignal(
                scene_index=scene_idx,
                instantaneous_effort=effort,
                attentional_signal=signal,
                recovery_credit=recovery,
                fatigue_state=fatigue_state
            )
            
            signals.append(temp_signal)
            prev_signal = signal
        
        return signals
    
    def _normalize_features(self) -> List[Dict]:
        """Normalize all feature groups to [0, 1] within script"""
        # Extract all raw feature values
        all_features = {
            'linguistic': [],
            'dialogue': [],
            'visual': [],
            'referential': [],
            'structural': []
        }
        
        for scene in self.scenes:
            features = scene['features']
            
            # Aggregate each feature group to single value
            ling = features['linguistic_load']
            all_features['linguistic'].append(
                ling['sentence_count'] / 100.0 +  # Normalize to reasonable range
                ling['mean_sentence_length'] / 20.0 +
                ling['sentence_length_variance'] / 50.0
            )
            
            dial = features['dialogue_dynamics']
            all_features['dialogue'].append(
                dial['dialogue_turns'] / 50.0 +
                dial['speaker_switches'] / 20.0 +
                dial['turn_velocity']
            )
            
            vis = features['visual_abstraction']
            all_features['visual'].append(
                vis['action_line_count'] / 50.0 +
                vis['continuous_action_runs'] / 10.0 +
                vis['visual_density'] +
                vis['vertical_writing_load'] / 20.0
            )
            
            ref = features['referential_memory']
            all_features['referential'].append(
                ref['active_character_count'] / 10.0 +
                ref['character_reintroductions'] / 5.0 +
                ref['pronoun_density']
            )
            
            struct = features['structural_change']
            all_features['structural'].append(
                struct['event_boundary_score'] / 50.0  # Normalize to ~[0,1]
            )
        
        # Compute min/max for each group
        ranges = {}
        for group, values in all_features.items():
            min_val = min(values) if values else 0.0
            max_val = max(values) if values else 1.0
            # Avoid division by zero
            ranges[group] = (min_val, max_val if max_val > min_val else min_val + 1.0)
        
        # Normalize
        normalized = []
        for i, scene in enumerate(self.scenes):
            norm_features = {}
            for group in all_features.keys():
                min_val, max_val = ranges[group]
                raw_val = all_features[group][i]
                norm_val = (raw_val - min_val) / (max_val - min_val)
                norm_features[group] = norm_val
            
            normalized.append(norm_features)
        
        return normalized
    
    def _compute_instantaneous_effort(self, scene_idx: int) -> float:
        """Compute instantaneous effort E[i] from normalized features"""
        features = self.normalized_features[scene_idx]
        
        effort = (
            self.W_LINGUISTIC * features['linguistic'] +
            self.W_DIALOGUE * features['dialogue'] +
            self.W_VISUAL * features['visual'] +
            self.W_REFERENTIAL * features['referential'] +
            self.W_STRUCTURAL * features['structural']
        )
        
        return effort
    
    def _compute_recovery(self, scene_idx: int, effort: float) -> float:
        """Compute recovery credit R[i]"""
        recovery = 0.0
        scene = self.scenes[scene_idx]
        features = scene['features']
        
        # 1. Low-effort recovery
        if effort < self.E_THRESHOLD:
            recovery += self.BETA * (self.E_THRESHOLD - effort)
        
        # 2. Structural boundary recovery
        boundary_score = features['structural_change']['event_boundary_score']
        if boundary_score > 0.5:  # Significant boundary
            recovery += self.GAMMA * (boundary_score / 50.0)  # Normalize
        
        # 3. Compression recovery (scene length proxy from visual density)
        # Lower visual density might indicate shorter scene
        visual_density = features['visual_abstraction']['visual_density']
        if visual_density < 0.3:  # Sparse scene (likely short)
            recovery += self.DELTA
        
        # Cap recovery
        recovery = min(recovery, self.R_MAX)
        
        return recovery
    
    def _compute_effective_lambda(self, scene_idx: int) -> float:
        """Compute effective lambda with opening/ending buffers"""
        lambda_eff = self.LAMBDA
        
        # Opening buffer
        if scene_idx < self.N_OPENING:
            ramp = min(1.0, scene_idx / self.N_OPENING)
            lambda_eff = self.LAMBDA * ramp
        
        # Ending buffer
        n_ending = max(1, int(self.num_scenes * self.N_ENDING_PERCENT))
        remaining = self.num_scenes - scene_idx
        
        if remaining <= n_ending:
            reduction = 0.5 * (n_ending - remaining) / n_ending
            lambda_eff = self.LAMBDA * (1 - reduction)
        
        return lambda_eff
    
    def _classify_fatigue_state(self, signal: float) -> str:
        """Classify fatigue state (descriptive, not evaluative)"""
        if signal < 1.5:
            return "normal"
        elif signal < 2.0:
            return "elevated"
        elif signal < 3.0:
            return "high"
        else:
            return "extreme"


def compute_temporal_dynamics(encoded_features_file: str) -> Dict:
    """
    Main entry point for temporal dynamics computation.
    
    Args:
        encoded_features_file: Path to encoded features JSON
        
    Returns:
        Dictionary with temporal signals
    """
    # Load encoded features
    with open(encoded_features_file, 'r') as f:
        data = json.load(f)
        encoded_scenes = data['encoded_scenes']
    
    # Compute temporal dynamics
    engine = TemporalEngine(encoded_scenes)
    signals = engine.compute_temporal_dynamics()
    
    return {
        'temporal_signals': [signal.to_dict() for signal in signals]
    }


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python temporal_engine.py <encoded_features_json>")
        sys.exit(1)
    
    features_file = sys.argv[1]
    
    result = compute_temporal_dynamics(features_file)
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
