
import statistics
import math
import logging

logger = logging.getLogger('scriptpulse.validation')

class BaselineComparator:
    """
    Compares ScriptPulse Model performance against simple heuristics.
    All baselines are computed from actual data — no hardcoded values.
    
    Baselines:
    1. Length Baseline (Effort = Line Count)
    2. Readability Baseline (Effort = Flesch-Kincaid Grade)
    3. Action Baseline (Effort = Action Density)
    """
    
    def __init__(self):
        pass
        
    def compare_baselines(self, aligned_data):
        """
        Input: aligned_data list from HumanAligner
        Each item must contain:
        - 'human_val': float (ground truth)
        - 'system_val': float (ScriptPulse output)
        - 'scene_features': dict with keys like 'line_count', 'readability_grade', 'action_density'
        """
        if len(aligned_data) < 3:
            return {'status': 'insufficient_data', 'n': len(aligned_data)}
        
        human_vals = [d['human_val'] for d in aligned_data]
        system_vals = [d['system_val'] for d in aligned_data]
        
        # System correlation (real computation)
        sys_corr = self._pearson(system_vals, human_vals)
        
        baselines = {
            'ScriptPulse (System)': sys_corr
        }
        
        # Compute real baselines from features (if available)
        features_available = all('scene_features' in d for d in aligned_data)
        
        if features_available:
            # Length Baseline
            line_counts = [d['scene_features'].get('line_count', 0) for d in aligned_data]
            if any(v > 0 for v in line_counts):
                baselines['Length (Line Count)'] = self._pearson(line_counts, human_vals)
            
            # Readability Baseline
            readability = [d['scene_features'].get('readability_grade', 0) for d in aligned_data]
            if any(v > 0 for v in readability):
                baselines['Readability (FK Grade)'] = self._pearson(readability, human_vals)
            
            # Action Density Baseline
            action_density = [d['scene_features'].get('action_density', 0) for d in aligned_data]
            if any(v > 0 for v in action_density):
                baselines['Action Density'] = self._pearson(action_density, human_vals)
        else:
            logger.warning(
                "BaselineComparator: 'scene_features' not found in aligned_data. "
                "Cannot compute feature-based baselines. Only system correlation is reported."
            )

        # Calculate lift over best baseline
        baseline_vals = {k: v for k, v in baselines.items() if k != 'ScriptPulse (System)'}
        best_baseline_r = max(baseline_vals.values()) if baseline_vals else 0
        
        lift = 0
        if best_baseline_r > 0:
            lift = ((sys_corr - best_baseline_r) / best_baseline_r) * 100
            
        return {
            'correlations': baselines,
            'best_baseline': max(baseline_vals, key=baseline_vals.get) if baseline_vals else 'N/A',
            'lift_over_best_baseline': round(lift, 1),
            'features_available': features_available
        }

    def _pearson(self, x, y):
        n = len(x)
        if n < 2: return 0
        mx = statistics.mean(x)
        my = statistics.mean(y)
        xm = [v - mx for v in x]
        ym = [v - my for v in y]
        num = sum(a*b for a,b in zip(xm, ym))
        den = math.sqrt(sum(a*a for a in xm) * sum(b*b for b in ym))
        if den == 0: return 0
        return round(num / den, 4)

    def generate_report(self, metrics):
        if metrics.get('status') == 'insufficient_data':
            return "### Baseline Comparison\n\n**Insufficient data** (N < 3). Cannot compute baselines.\n"
        
        md = "### Baseline Comparison\n\n"
        
        if not metrics.get('features_available'):
            md += "> **Note:** Feature-based baselines could not be computed (scene_features missing).\n"
            md += "> Only the system correlation is shown.\n\n"
        
        md += "| Model | Human Correlation (r) | Lift |\n"
        md += "|---|---|---|\n"
        
        sorted_bases = sorted(metrics['correlations'].items(), key=lambda x: x[1], reverse=True)
        
        for name, r in sorted_bases:
            lift_str = "-"
            if name == 'ScriptPulse (System)':
                lift_str = f"**+{metrics['lift_over_best_baseline']:.1f}%**"
            md += f"| {name} | {r:.4f} | {lift_str} |\n"
            
        return md
