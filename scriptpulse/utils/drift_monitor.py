
import json
import statistics
import os
import datetime

class FeatureDriftMonitor:
    """Detects shifts in key metrics across script versions"""
    
    def __init__(self, history_file='drift_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
        
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def log_run(self, metrics):
        """
        metrics: dict of {key: value} (e.g. {'avg_effort': 0.5, 'avg_valence': 0.1})
        """
        entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': metrics
        }
        self.history.append(entry)
        # Keep last 50 runs
        if len(self.history) > 50:
            self.history = self.history[-50:]
            
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def check_drift(self, current_metrics):
        """Compare current metrics against historical baseline"""
        if len(self.history) < 5:
            return {'status': 'insufficient_history'}
            
        alerts = []
        for key, val in current_metrics.items():
            past_vals = [h['metrics'].get(key, 0) for h in self.history if key in h['metrics']]
            if not past_vals: continue
            
            mean = statistics.mean(past_vals)
            stdev = statistics.stdev(past_vals) if len(past_vals) > 1 else 0.1
            
            z_score = (val - mean) / stdev if stdev > 0 else 0
            
            if abs(z_score) > 2.0:
                alerts.append({
                    'metric': key,
                    'current': val,
                    'mean': mean,
                    'sigma': round(z_score, 1),
                    'severity': 'high' if abs(z_score) > 3 else 'medium'
                })
                
        return {'alerts': alerts, 'baseline_samples': len(self.history)}

if __name__ == "__main__":
    # Example Usage
    monitor = FeatureDriftMonitor()
    current = {'avg_effort': 0.65, 'avg_valence': 0.2, 'readability': 8.5}
    monitor.log_run(current)
    print(monitor.check_drift(current))
