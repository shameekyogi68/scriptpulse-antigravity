#!/usr/bin/env python3
"""
Drift Dashboard (v13.1 Block 2)

Tracks rolling per-day production stats and triggers alerts when
metrics drift beyond defined thresholds.

Tracked per day:
    - mean pulse
    - mean uncertainty
    - mean fatigue penalty
    - scene count distribution
    - runtime per scene

Trigger rules:
    - pulse mean drift > 0.07 from baseline → UNSTABLE
    - uncertainty mean drift > 0.05 → UNSTABLE
    - runtime per scene +40% → UNSTABLE
    
On trigger:
    - mark build unstable
    - require calibration run

Usage:
    # Log a run result
    PYTHONPATH=. python3 -c "from scriptpulse.drift_dashboard import DriftDashboard; d = DriftDashboard(); d.log_run(result)"
    
    # Check drift
    PYTHONPATH=. python3 scriptpulse/drift_dashboard.py
"""

import json
import os
import time
import statistics
from datetime import datetime


class DriftDashboard:
    """Rolling stats tracker with drift detection."""
    
    DRIFT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.drift_data')
    BASELINE_FILE = os.path.join(DRIFT_DIR, 'baseline.json')
    DAILY_LOG_DIR = os.path.join(DRIFT_DIR, 'daily')
    
    # Trigger thresholds
    PULSE_DRIFT_THRESHOLD = 0.07
    UNCERTAINTY_DRIFT_THRESHOLD = 0.05
    RUNTIME_DRIFT_PERCENT = 40  # +40%
    
    def __init__(self):
        os.makedirs(self.DAILY_LOG_DIR, exist_ok=True)
    
    def _today_key(self):
        return datetime.now().strftime('%Y-%m-%d')
    
    def _daily_path(self, day_key=None):
        day_key = day_key or self._today_key()
        return os.path.join(self.DAILY_LOG_DIR, f'{day_key}.json')
    
    def _load_daily(self, day_key=None):
        path = self._daily_path(day_key)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {'runs': []}
    
    def _save_daily(self, data, day_key=None):
        path = self._daily_path(day_key)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_run(self, result):
        """
        Log a pipeline result to the daily rolling stats.
        
        Args:
            result: Full pipeline output dict
        """
        trace = result.get('temporal_trace', [])
        uncertainty = result.get('uncertainty_quantification', [])
        timings = result.get('meta', {}).get('agent_timings', {})
        total_scenes = result.get('total_scenes', 0)
        
        # Extract metrics
        pulses = [p.get('attentional_signal', 0) for p in trace]
        uncertainties = [u.get('std_dev', 0) for u in uncertainty]
        fatigue_penalties = [
            p.get('fatigue_penalty', p.get('coherence_penalty', 0)) 
            for p in trace
        ]
        
        total_runtime_ms = sum(timings.values()) if timings else 0
        runtime_per_scene = total_runtime_ms / max(total_scenes, 1)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'mean_pulse': round(statistics.mean(pulses), 4) if pulses else 0,
            'mean_uncertainty': round(statistics.mean(uncertainties), 4) if uncertainties else 0,
            'mean_fatigue_penalty': round(statistics.mean(fatigue_penalties), 4) if fatigue_penalties else 0,
            'total_scenes': total_scenes,
            'runtime_per_scene_ms': round(runtime_per_scene, 1),
            'total_runtime_ms': total_runtime_ms,
        }
        
        daily = self._load_daily()
        daily['runs'].append(entry)
        self._save_daily(daily)
        
        return entry
    
    def get_daily_summary(self, day_key=None):
        """Get aggregated stats for a day."""
        daily = self._load_daily(day_key)
        runs = daily.get('runs', [])
        
        if not runs:
            return None
        
        return {
            'date': day_key or self._today_key(),
            'run_count': len(runs),
            'mean_pulse': round(statistics.mean([r['mean_pulse'] for r in runs]), 4),
            'mean_uncertainty': round(statistics.mean([r['mean_uncertainty'] for r in runs]), 4),
            'mean_fatigue_penalty': round(statistics.mean([r['mean_fatigue_penalty'] for r in runs]), 4),
            'scene_count_distribution': {
                'min': min(r['total_scenes'] for r in runs),
                'max': max(r['total_scenes'] for r in runs),
                'mean': round(statistics.mean([r['total_scenes'] for r in runs]), 1),
            },
            'mean_runtime_per_scene_ms': round(
                statistics.mean([r['runtime_per_scene_ms'] for r in runs]), 1
            ),
        }
    
    def set_baseline(self, day_key=None):
        """Set current day's summary as the drift baseline."""
        summary = self.get_daily_summary(day_key)
        if not summary:
            print("No runs to baseline from.")
            return
        
        with open(self.BASELINE_FILE, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Baseline set from {summary['run_count']} runs on {summary['date']}")
        return summary
    
    def load_baseline(self):
        if not os.path.exists(self.BASELINE_FILE):
            return None
        with open(self.BASELINE_FILE, 'r') as f:
            return json.load(f)
    
    def check_drift(self, day_key=None):
        """
        Compare today's stats against baseline.
        
        Returns:
            (status, triggers) where status is 'STABLE', 'UNSTABLE', or 'NO_DATA'
        """
        baseline = self.load_baseline()
        if not baseline:
            return 'NO_BASELINE', []
        
        summary = self.get_daily_summary(day_key)
        if not summary:
            return 'NO_DATA', []
        
        triggers = []
        
        # Pulse drift
        pulse_drift = abs(summary['mean_pulse'] - baseline['mean_pulse'])
        if pulse_drift > self.PULSE_DRIFT_THRESHOLD:
            triggers.append({
                'metric': 'mean_pulse',
                'drift': round(pulse_drift, 4),
                'threshold': self.PULSE_DRIFT_THRESHOLD,
                'baseline': baseline['mean_pulse'],
                'current': summary['mean_pulse'],
            })
        
        # Uncertainty drift
        unc_drift = abs(summary['mean_uncertainty'] - baseline['mean_uncertainty'])
        if unc_drift > self.UNCERTAINTY_DRIFT_THRESHOLD:
            triggers.append({
                'metric': 'mean_uncertainty',
                'drift': round(unc_drift, 4),
                'threshold': self.UNCERTAINTY_DRIFT_THRESHOLD,
                'baseline': baseline['mean_uncertainty'],
                'current': summary['mean_uncertainty'],
            })
        
        # Runtime drift (+40%)
        baseline_rt = baseline['mean_runtime_per_scene_ms']
        if baseline_rt > 0:
            rt_increase_pct = (
                (summary['mean_runtime_per_scene_ms'] - baseline_rt) / baseline_rt
            ) * 100
            if rt_increase_pct > self.RUNTIME_DRIFT_PERCENT:
                triggers.append({
                    'metric': 'runtime_per_scene',
                    'drift_percent': round(rt_increase_pct, 1),
                    'threshold_percent': self.RUNTIME_DRIFT_PERCENT,
                    'baseline_ms': baseline_rt,
                    'current_ms': summary['mean_runtime_per_scene_ms'],
                })
        
        status = 'UNSTABLE' if triggers else 'STABLE'
        return status, triggers
    
    def report(self, day_key=None):
        """Print a drift report."""
        print("=" * 60)
        print("DRIFT DASHBOARD REPORT")
        print("=" * 60)
        
        summary = self.get_daily_summary(day_key)
        if not summary:
            print("  No runs recorded today.")
            return
        
        print(f"\n  Date:              {summary['date']}")
        print(f"  Runs:              {summary['run_count']}")
        print(f"  Mean Pulse:        {summary['mean_pulse']}")
        print(f"  Mean Uncertainty:  {summary['mean_uncertainty']}")
        print(f"  Mean Fatigue:      {summary['mean_fatigue_penalty']}")
        print(f"  Scene Range:       {summary['scene_count_distribution']['min']}-{summary['scene_count_distribution']['max']}")
        print(f"  Runtime/Scene:     {summary['mean_runtime_per_scene_ms']}ms")
        
        status, triggers = self.check_drift(day_key)
        
        print(f"\n  Drift Status: {status}")
        if triggers:
            print(f"\n  ⚠️  TRIGGERS ({len(triggers)}):")
            for t in triggers:
                print(f"    - {t['metric']}: drift={t.get('drift', t.get('drift_percent', '?'))}")
            print(f"\n  ACTION REQUIRED: Run calibration regression check")
        elif status == 'NO_BASELINE':
            print("  ℹ️  Set baseline first: dashboard.set_baseline()")
        else:
            print("  ✅ All metrics within thresholds")


def main():
    dashboard = DriftDashboard()
    dashboard.report()


if __name__ == '__main__':
    main()
