#!/usr/bin/env python3
"""
Interpretive Pattern Agent

Detects persistent experiential patterns in attentional signals
without evaluation or judgment.
"""

import json
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Pattern:
    """Detected pattern descriptor"""
    pattern_type: str
    scene_range: Tuple[int, int]
    confidence_band: str
    description: str
    supporting_metrics: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'pattern_type': self.pattern_type,
            'scene_range': list(self.scene_range),
            'confidence_band': self.confidence_band,
            'description': self.description,
            'supporting_metrics': self.supporting_metrics
        }


class PatternDetector:
    """Detects persistent patterns in temporal signals"""
    
    # Thresholds for pattern detection
    ELEVATED_SIGNAL = 1.5
    LOW_RECOVERY = 0.2
    MIN_RECOVERY_FOR_CONSTRUCTIVE = 0.2
    HIGH_BOUNDARY = 25.0
    SIMILARITY_THRESHOLD = 0.7
    
    MIN_PERSISTENCE = 3  # Minimum scenes for pattern
    
    def __init__(self, temporal_signals: List[Dict], encoded_features: List[Dict]):
        """
        Initialize pattern detector.
        
        Args:
            temporal_signals: Temporal dynamics output
            encoded_features: Scene feature vectors for similarity analysis
        """
        self.signals = temporal_signals
        self.features = encoded_features
        self.num_scenes = len(temporal_signals)
    
    def detect_all_patterns(self) -> List[Pattern]:
        """
        Detect all patterns in temporal signals.
        
        Returns:
            List of Pattern objects
        """
        patterns = []
        
        # Detect each pattern type
        patterns.extend(self._detect_sustained_demand())
        patterns.extend(self._detect_limited_recovery())
        patterns.extend(self._detect_surprise_clusters())
        patterns.extend(self._detect_sequence_repetition())
        patterns.extend(self._detect_constructive_strain())
        patterns.extend(self._detect_degenerative_fatigue())
        
        # Calculate confidence for all patterns
        patterns = [self._calculate_confidence(p) for p in patterns]
        
        return patterns
    
    def _detect_sustained_demand(self) -> List[Pattern]:
        """Detect sustained attentional demand patterns"""
        patterns = []
        current_start = None
        count = 0
        signals_in_pattern = []
        
        for i, signal in enumerate(self.signals):
            s_value = signal['attentional_signal']
            
            if s_value > self.ELEVATED_SIGNAL:
                if current_start is None:
                    current_start = signal['scene_index']
                count += 1
                signals_in_pattern.append(s_value)
            else:
                # Pattern ended
                if count >= self.MIN_PERSISTENCE:
                    avg_signal = sum(signals_in_pattern) / len(signals_in_pattern)
                    min_signal = min(signals_in_pattern)
                    max_signal = max(signals_in_pattern)
                    
                    pattern = Pattern(
                        pattern_type="sustained_demand",
                        scene_range=(current_start, self.signals[i-1]['scene_index']),
                        confidence_band="medium",  # Will be recalculated
                        description=f"Attentional signal elevated above {self.ELEVATED_SIGNAL} across {count} consecutive scenes",
                        supporting_metrics={
                            'avg_signal': round(avg_signal, 2),
                            'min_signal': round(min_signal, 2),
                            'max_signal': round(max_signal, 2),
                            'scene_count': count
                        }
                    )
                    patterns.append(pattern)
                
                current_start = None
                count = 0
                signals_in_pattern = []
        
        # Handle pattern extending to end
        if count >= self.MIN_PERSISTENCE:
            avg_signal = sum(signals_in_pattern) / len(signals_in_pattern)
            pattern = Pattern(
                pattern_type="sustained_demand",
                scene_range=(current_start, self.signals[-1]['scene_index']),
                confidence_band="medium",
                description=f"Attentional signal elevated above {self.ELEVATED_SIGNAL} across {count} consecutive scenes",
                supporting_metrics={
                    'avg_signal': round(avg_signal, 2),
                    'scene_count': count
                }
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_limited_recovery(self) -> List[Pattern]:
        """Detect limited recovery window patterns"""
        patterns = []
        current_start = None
        count = 0
        recoveries = []
        
        for i, signal in enumerate(self.signals):
            s_value = signal['attentional_signal']
            r_value = signal['recovery_credit']
            
            if s_value > 1.0 and r_value < self.LOW_RECOVERY:
                if current_start is None:
                    current_start = signal['scene_index']
                count += 1
                recoveries.append(r_value)
            else:
                if count >= self.MIN_PERSISTENCE:
                    avg_recovery = sum(recoveries) / len(recoveries)
                    
                    pattern = Pattern(
                        pattern_type="limited_recovery",
                        scene_range=(current_start, self.signals[i-1]['scene_index']),
                        confidence_band="medium",
                        description=f"Recovery credits below {self.LOW_RECOVERY} while signal > 1.0 across {count} scenes",
                        supporting_metrics={
                            'avg_recovery': round(avg_recovery, 3),
                            'scene_count': count
                        }
                    )
                    patterns.append(pattern)
                
                current_start = None
                count = 0
                recoveries = []
        
        return patterns
    
    def _detect_surprise_clusters(self) -> List[Pattern]:
        """Detect surprise cluster patterns (frequent boundary spikes)"""
        patterns = []
        window_size = 5
        
        for i in range(len(self.features) - window_size + 1):
            window = self.features[i:i + window_size]
            
            # Count high boundary scores in window
            high_boundaries = sum(
                1 for scene in window
                if scene['features']['structural_change']['event_boundary_score'] > self.HIGH_BOUNDARY
            )
            
            # If ≥ 60% have high boundaries, it's a cluster
            if high_boundaries >= window_size * 0.6:
                start_scene = self.signals[i]['scene_index']
                end_scene = self.signals[i + window_size - 1]['scene_index']
                
                pattern = Pattern(
                    pattern_type="surprise_cluster",
                    scene_range=(start_scene, end_scene),
                    confidence_band="medium",
                    description=f"Event boundary scores > {self.HIGH_BOUNDARY} in {high_boundaries} of {window_size} scenes",
                    supporting_metrics={
                        'high_boundary_count': high_boundaries,
                        'window_size': window_size
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_sequence_repetition(self) -> List[Pattern]:
        """Detect repetitive sequence patterns"""
        # Simplified: Look for similar feature patterns
        # In full implementation, would compute feature vector similarities
        patterns = []
        
        # For now, skip complex similarity analysis
        # Would require comparing feature vectors across scenes
        
        return patterns
    
    def _detect_constructive_strain(self) -> List[Pattern]:
        """Detect constructive strain patterns (high effort WITH recovery)"""
        patterns = []
        window_size = 5
        
        for i in range(len(self.signals) - window_size + 1):
            window = self.signals[i:i + window_size]
            
            # Calculate average signal and recovery in window
            avg_signal = sum(s['attentional_signal'] for s in window) / window_size
            avg_recovery = sum(s['recovery_credit'] for s in window) / window_size
            
            # Constructive: elevated signal WITH recovery balance
            if avg_signal > self.ELEVATED_SIGNAL and avg_recovery > self.MIN_RECOVERY_FOR_CONSTRUCTIVE:
                start_scene = window[0]['scene_index']
                end_scene = window[-1]['scene_index']
                
                pattern = Pattern(
                    pattern_type="constructive_strain",
                    scene_range=(start_scene, end_scene),
                    confidence_band="medium",
                    description=f"Signal elevated (avg {avg_signal:.2f}) with recovery credits averaging {avg_recovery:.2f} per scene",
                    supporting_metrics={
                        'avg_signal': round(avg_signal, 2),
                        'avg_recovery': round(avg_recovery, 2),
                        'scene_count': window_size
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_degenerative_fatigue(self) -> List[Pattern]:
        """Detect degenerative fatigue patterns (high effort WITHOUT recovery)"""
        patterns = []
        window_size = 7
        
        for i in range(len(self.signals) - window_size + 1):
            window = self.signals[i:i + window_size]
            
            signals_only = [s['attentional_signal'] for s in window]
            avg_signal = sum(signals_only) / window_size
            avg_recovery = sum(s['recovery_credit'] for s in window) / window_size
            
            # Check for upward drift
            first_half_avg = sum(signals_only[:window_size//2]) / (window_size//2)
            second_half_avg = sum(signals_only[window_size//2:]) / (window_size - window_size//2)
            
            # Degenerative: elevated + low recovery + increasing
            if (avg_signal > self.ELEVATED_SIGNAL and 
                avg_recovery < 0.1 and 
                second_half_avg > first_half_avg * 1.2):
                
                start_scene = window[0]['scene_index']
                end_scene = window[-1]['scene_index']
                start_signal = signals_only[0]
                end_signal = signals_only[-1]
                
                pattern = Pattern(
                    pattern_type="degenerative_fatigue",
                    scene_range=(start_scene, end_scene),
                    confidence_band="medium",
                    description=f"Signal rising from {start_signal:.2f} to {end_signal:.2f} with recovery credits < 0.1",
                    supporting_metrics={
                        'start_signal': round(start_signal, 2),
                        'end_signal': round(end_signal, 2),
                        'avg_recovery': round(avg_recovery, 3),
                        'scene_count': window_size
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _calculate_confidence(self, pattern: Pattern) -> Pattern:
        """Calculate confidence band with downgrading"""
        start_idx = pattern.scene_range[0] - 1  # Convert to 0-indexed
        end_idx = pattern.scene_range[1]
        
        window = self.signals[start_idx:end_idx]
        
        # Start with high confidence
        confidence = "high"
        
        # Downgrade based on persistence length
        scene_count = len(window)
        if scene_count < 5:
            confidence = "medium"
        if scene_count == 3:
            confidence = "low"
        
        # Downgrade based on signal volatility
        signals = [s['attentional_signal'] for s in window]
        if len(signals) > 1:
            mean_signal = sum(signals) / len(signals)
            variance = sum((s - mean_signal) ** 2 for s in signals) / len(signals)
            
            if variance > 0.5:
                confidence = "medium" if confidence == "high" else "low"
        
        # Create new pattern with updated confidence
        pattern.confidence_band = confidence
        return pattern


def detect_patterns(temporal_signals_file: str, encoded_features_file: str) -> Dict:
    """
    Main entry point for pattern detection.
    
    Args:
        temporal_signals_file: Path to temporal signals JSON
        encoded_features_file: Path to encoded features JSON
        
    Returns:
        Dictionary with detected patterns
    """
    # Load temporal signals
    with open(temporal_signals_file, 'r') as f:
        temporal_data = json.load(f)
        signals = temporal_data['temporal_signals']
    
    # Load encoded features
    with open(encoded_features_file, 'r') as f:
        features_data = json.load(f)
        features = features_data['encoded_scenes']
    
    # Detect patterns
    detector = PatternDetector(signals, features)
    patterns = detector.detect_all_patterns()
    
    return {
        'patterns': [p.to_dict() for p in patterns]
    }


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python pattern_detector.py <temporal_signals_json> <encoded_features_json>")
        sys.exit(1)
    
    signals_file = sys.argv[1]
    features_file = sys.argv[2]
    
    result = detect_patterns(signals_file, features_file)
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
