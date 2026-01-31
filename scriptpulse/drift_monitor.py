"""
Organizational Drift Monitor (ODD)
vNext.5 Market Upgrade - Governance

Detects and flags when an organization begins drifting towards 
evaluative misuse (e.g., using the tool as a filter).

Includes AOI (Anti-Optimization Immunity).
"""

import time
from collections import deque

class DriftMonitor:
    """
    Tracks usage patterns to detect 'Evaluative Drift'.
    """
    
    def __init__(self):
        # Rolling window of recent runs (Simulated storage)
        self.recent_runs = deque(maxlen=100)
        self.drift_score = 0.0
        self.aoi_active = False # AOI: Anti-Optimization Immunity
        
    def log_run(self, run_metadata):
        """
        Ingest run metadata to sanity check usage health.
        """
        self.recent_runs.append({
            'timestamp': time.time(),
            'meta': run_metadata
        })
        self.analyze_drift()
        
    def analyze_drift(self):
        """
        Check for drift signals:
        1. Rapid Reruns (Fishing for alerts)
        2. Mass Batching (Running 50 scripts in 1 hour)
        3. Exclusionary Silence (Rejecting scripts that are silent) - Hard to detect here without outcome data
        """
        if len(self.recent_runs) < 5:
            return
            
        # 1. Check Repetition (Fishing / Optimization)
        # Same script name/fingerprint, rapid succession
        fingerprints = [r['meta'].get('fingerprint') for r in self.recent_runs]
        unique_fps = set(fingerprints)
        
        # Simple heuristic: If we see the same script fingerprint > 80% of last 10 runs
        # It implies optimization loop.
        repetition_count = 0
        current_fp = fingerprints[-1]
        for fp in fingerprints:
            if fp == current_fp:
                repetition_count += 1
                
        repetition_ratio = repetition_count / len(fingerprints)
        
        if repetition_ratio > 0.6 and len(fingerprints) > 5:
            # High repetition -> Writer is likely "optimizing for green" (AOI Trigger)
            self.drift_score = 0.8
            self.aoi_active = True
        else:
            self.drift_score = 0.0
            self.aoi_active = False
            
    def get_status(self):
        if self.aoi_active:
             return "AOI_ACTIVE: Optimization dampening engaged due to repetition."
        if self.drift_score > 0.7:
            return "DRIFT_DETECTED: High Repetition/optimization behavior observed."
        return "NORMAL: Usage compliant with creative support model."

    def get_dampening_factor(self):
        """
        AOI: If optimization detected, reduce system sensitivity.
        
        Returns:
            float: 1.0 (Normal) to 0.5 (Heavily Dampened)
        """
        if self.aoi_active:
            # Dampen sensitivity to discourage gaming
            return 0.7 
        return 1.0

# Global singleton for demonstration
monitor = DriftMonitor()
