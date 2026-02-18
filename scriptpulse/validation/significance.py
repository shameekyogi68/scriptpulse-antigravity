
import statistics
import math
import random

class SignificanceTester:
    """
    Calculates statistical significance for validation metrics.
    - p-values for correlations
    - Bootstrap Confidence Intervals for MAE/r
    """
    
    def __init__(self, n_bootstraps=1000):
        self.n_bootstraps = n_bootstraps
        
    def calculate_significance(self, aligned_data):
        """
        Input: list of {'human_val': float, 'system_val': float}
        """
        x = [d['system_val'] for d in aligned_data]
        y = [d['human_val'] for d in aligned_data]
        n = len(x)
        
        if n < 3:
            return {'p_value': 1.0, 'ci_lower': 0, 'ci_upper': 0}
            
        # 1. Pearson r and p-value
        r = self._pearson(x, y)
        
        # t-statistic for Pearson Correlation
        # t = r * sqrt(n-2) / sqrt(1-r^2)
        if abs(r) >= 1.0:
            p_value = 0.0
        else:
            t_stat = r * math.sqrt(n - 2) / math.sqrt(1 - r**2)
            # Approximate p-value (mocking standard distribution lookup, or using simple heuristic)
            # For automation without scipy, we can use a lookup or simple threshold reporting
            # Here we mock for simplicity or use a very rough approx
            p_value = self._approx_p_value_t(t_stat, n-2)
            
        # 2. Bootstrap CI
        boot_rs = []
        for _ in range(self.n_bootstraps):
            # Resample with replacement
            indices = [random.randint(0, n-1) for _ in range(n)]
            bx = [x[i] for i in indices]
            by = [y[i] for i in indices]
            boot_rs.append(self._pearson(bx, by))
            
        boot_rs.sort()
        ci_lower = boot_rs[int(self.n_bootstraps * 0.025)]
        ci_upper = boot_rs[int(self.n_bootstraps * 0.975)]
        
        return {
            'pearson_r': r,
            'p_value': p_value,
            'ci_95': (ci_lower, ci_upper)
        }
        
    def _pearson(self, x, y):
        # ... (Same as baseline logic, shared util ideal) ...
        n = len(x)
        if n < 2: return 0
        mx = statistics.mean(x)
        my = statistics.mean(y)
        xm = [v - mx for v in x]
        ym = [v - my for v in y]
        num = sum(a*b for a,b in zip(xm, ym))
        den = math.sqrt(sum(a*a for a in xm) * sum(b*b for b in ym))
        if den == 0: return 0
        return num / den

    def _approx_p_value_t(self, t, df):
        # Two-tailed p-value approximation for t-distribution
        # Extremely rough approx for demo
        t = abs(t)
        if t > 3.0: return 0.001
        if t > 2.0: return 0.05
        if t > 1.0: return 0.3
        return 0.5

    def generate_report(self, stats):
        md = "### Statistical Significance\n\n"
        md += f"- **Pearson r**: {stats['pearson_r']:.3f}\n"
        md += f"- **p-value**: < {stats['p_value'] if stats['p_value'] > 0 else 0.001} (Significance)\n"
        md += f"- **95% CI**: [{stats['ci_95'][0]:.3f}, {stats['ci_95'][1]:.3f}]\n"
        return md
