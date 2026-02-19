"""
Organizational Drift Monitor (ODD)
vNext.11 Market Upgrade - Statistical Governance

Detects:
1. "Optimization Drift" (Gaming the system)
2. "Data Drift" (Input distribution shift) uses KS-Test.
"""

import time
import numpy as np
from collections import deque
try:
    from scipy import stats
except ImportError:
    stats = None

class DriftMonitor:
    """
    Tracks usage patterns and data distributions to detect drift.
    """
    
    def __init__(self):
        # Rolling window of recent runs (Simulated storage)
        self.recent_runs = deque(maxlen=100)
        self.entropy_baseline = deque(maxlen=500) # Baseline data for KS-Test
        self.drift_score = 0.0
        self.aoi_active = False 
        
    def log_run(self, run_metadata, entropy_scores=None):
        """
        Ingest run metadata to sanity check usage health.
        """
        self.recent_runs.append({
            'timestamp': time.time(),
            'meta': run_metadata
        })
        
        # Ingest data for statistical monitoring
        if entropy_scores:
            self.entropy_baseline.extend(entropy_scores)
            
        self.analyze_drift()
        
    def check_distribution_drift(self, current_scores):
        """
        Check if current script's entropy distribution matches the baseline.
        Uses Kolmogorov-Smirnov Test (KS-Test).
        """
        if len(self.entropy_baseline) < 50 or len(current_scores) < 10:
            return False, 1.0 # Not enough data
            
        # KS Test
        # If scipy is missing, return no drift
        if stats is None:
            return False, 1.0
            
        # Mull Hypothesis: Samples are drawn from same distribution.
        # If p < 0.05, we reject null -> DRIFT DETECTED.
        statistic, p_value = stats.ks_2samp(list(self.entropy_baseline), current_scores)
        
        if p_value < 0.01:
            print(f"[ML Monitor] Distribution Drift Detected (p={p_value:.4f}). Script is statistically anomalous.")
            return True, p_value
            
        return False, p_value
        
    def analyze_drift(self):
        """
        Check for drift signals (Repetition/Gaming).
        """
        if len(self.recent_runs) < 5:
            return
            
        # 1. Check Repetition (Fishing / Optimization)
        fingerprints = [r['meta'].get('fingerprint') for r in self.recent_runs]
        
        # Simple heuristic: If we see the same script fingerprint > 80% of last 10 runs
        repetition_count = 0
        current_fp = fingerprints[-1]
        for fp in fingerprints:
            if fp == current_fp:
                repetition_count += 1
                
        repetition_ratio = repetition_count / len(fingerprints)
        
        if repetition_ratio > 0.6 and len(fingerprints) > 5:
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

    def check_domain_adherence(self, script_lines):
        """
        Risk R-01: Domain Drift Check.
        """
        if not script_lines: return True
        
        headers = sum(1 for line in script_lines if line.strip().upper().startswith(("INT.", "EXT.")))
        
        ratio_headers = headers / len(script_lines)
        
        if headers == 0:
            print("[Warning] Risk R-01: Domain Drift. No Scene Headings detected.")
            return False
            
        if ratio_headers > 0.5:
             print("[Warning] Risk R-01: Domain Drift. Header Density > 50%.")
             return False
             
        return True

# Global singleton
monitor = DriftMonitor()
