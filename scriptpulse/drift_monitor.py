"""
Organizational Drift Monitor (ODD)
vNext.5 Market Upgrade - Governance

Detects and flags when an organization begins drifting towards 
evaluative misuse (e.g., using the tool as a filter).
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
        if len(self.recent_runs) < 10:
            return
            
        # 1. Check Repetition (Fishing)
        # Same script, small changes, rapid succession
        fingerprints = [r['meta'].get('fingerprint') for r in self.recent_runs]
        unique = set(fingerprints)
        repetition_ratio = 1.0 - (len(unique) / len(fingerprints))
        
        if repetition_ratio > 0.8:
            # High repetition -> Writer is likely "optimizing for green"
            # Action: Increase Refusal Sensitivity (Simulated)
            self.drift_score = 0.8
            # In a real system, this would trigger a "Coaching Interventional Pop-up"
            
        else:
            self.drift_score = 0.0
            
    def get_status(self):
        if self.drift_score > 0.7:
            return "DRIFT_DETECTED: High Repetition/optimization behavior observed."
        return "NORMAL: Usage compliant with creative support model."

# Global singleton for demonstration
monitor = DriftMonitor()
