
import statistics
import math
import random
import logging

logger = logging.getLogger('scriptpulse.validation')

# Try to import scipy for real p-values
try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not available — p-values will use rough approximation")


class SignificanceTester:
    """
    Calculates statistical significance for validation metrics.
    - p-values for correlations (via scipy.stats.t when available)
    - Bootstrap Confidence Intervals for Pearson r
    """
    
    def __init__(self, n_bootstraps=1000, seed=42):
        self.n_bootstraps = n_bootstraps
        self.seed = seed
        
    def calculate_significance(self, aligned_data):
        """
        Input: list of {'human_val': float, 'system_val': float}
        Returns: dict with pearson_r, p_value, ci_95, n, method
        """
        x = [d['system_val'] for d in aligned_data]
        y = [d['human_val'] for d in aligned_data]
        n = len(x)
        
        if n < 3:
            return {
                'pearson_r': 0.0,
                'p_value': 1.0,
                'ci_95': (0.0, 0.0),
                'n': n,
                'method': 'insufficient_data'
            }
            
        # 1. Pearson r and p-value
        r = self._pearson(x, y)
        
        if HAS_SCIPY:
            # Real p-value using scipy
            stat_result = scipy_stats.pearsonr(x, y)
            p_value = float(stat_result.pvalue) if hasattr(stat_result, 'pvalue') else float(stat_result[1])
            method = 'scipy.stats.pearsonr'
        else:
            # Fallback: approximate p-value from t-distribution
            p_value = self._approx_p_value_t(r, n)
            method = 'approximate_t (scipy not available)'
            
        # 2. Bootstrap CI (seeded for reproducibility)
        rng = random.Random(self.seed)
        boot_rs = []
        for _ in range(self.n_bootstraps):
            indices = [rng.randint(0, n-1) for _ in range(n)]
            bx = [x[i] for i in indices]
            by = [y[i] for i in indices]
            boot_rs.append(self._pearson(bx, by))
            
        boot_rs.sort()
        ci_lower = boot_rs[int(self.n_bootstraps * 0.025)]
        ci_upper = boot_rs[int(self.n_bootstraps * 0.975)]
        
        return {
            'pearson_r': round(r, 4),
            'p_value': round(p_value, 6),
            'ci_95': (round(ci_lower, 4), round(ci_upper, 4)),
            'n': n,
            'method': method
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
        return num / den

    def _approx_p_value_t(self, r, n):
        """Approximate two-tailed p-value from t-distribution.
        Used only when scipy is not available.
        """
        if abs(r) >= 1.0:
            return 0.0
        df = n - 2
        if df < 1:
            return 1.0
        t_stat = abs(r) * math.sqrt(df) / math.sqrt(1 - r**2)
        
        # Rough approximation using normal CDF proxy
        # For research-grade results, install scipy
        if t_stat > 4.0: return 0.0001
        if t_stat > 3.5: return 0.001
        if t_stat > 3.0: return 0.005
        if t_stat > 2.576: return 0.01
        if t_stat > 2.326: return 0.02
        if t_stat > 1.960: return 0.05
        if t_stat > 1.645: return 0.10
        if t_stat > 1.282: return 0.20
        return 0.50

    def generate_report(self, stats):
        md = "### Statistical Significance\n\n"
        md += f"- **Pearson r**: {stats['pearson_r']:.4f}\n"
        
        p = stats['p_value']
        if p < 0.001:
            md += f"- **p-value**: < 0.001 (**Highly Significant**)\n"
        elif p < 0.01:
            md += f"- **p-value**: {p:.4f} (**Significant**)\n"
        elif p < 0.05:
            md += f"- **p-value**: {p:.4f} (*Marginally Significant*)\n"
        else:
            md += f"- **p-value**: {p:.4f} (Not Significant)\n"
        
        md += f"- **95% CI**: [{stats['ci_95'][0]:.4f}, {stats['ci_95'][1]:.4f}]\n"
        md += f"- **N**: {stats['n']}\n"
        md += f"- **Method**: {stats['method']}\n"
        
        if not HAS_SCIPY:
            md += "\n> ⚠️ **Warning**: p-values are approximate. Install `scipy` for exact results.\n"
        
        return md
