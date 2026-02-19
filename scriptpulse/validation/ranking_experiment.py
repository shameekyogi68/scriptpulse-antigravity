
import os
import csv
import statistics
from scipy.stats import spearmanr
from ..agents.dynamics_agent import DynamicsAgent

class RankingExperiment:
    """
    Validation Experiment 2: Blind Ranking
    Ranks N scripts by Mean Attention and compares to Human Interest Ranking.
    Outputs Spearman Rho.
    """
    
    def __init__(self, agent=None):
        self.agent = agent if agent else DynamicsAgent()
        
    def run(self, script_features_map, ground_truth_rankings):
        """
        script_features_map: { 'script_id': [features...] }
        ground_truth_rankings: { 'script_id': human_rank_int } (1=Best)
        """
        
        # 1. Calculate System Scores
        system_scores = {}
        for script_id, features in script_features_map.items():
            # Use deterministic run
            trace = self.agent.run_simulation({'features': features}, genre='drama', debug=False)
            avg_att = statistics.mean([s['attentional_signal'] for s in trace]) if trace else 0
            system_scores[script_id] = avg_att
            
        # 2. Sort System Ranking (Descending Attention)
        sorted_sys = sorted(system_scores.items(), key=lambda x: x[1], reverse=True)
        system_ranks = {sid: rank+1 for rank, (sid, score) in enumerate(sorted_sys)}
        
        # 3. Prepare Arrays for Spearman
        ids = list(script_features_map.keys())
        sys_vector = [system_ranks.get(i, 999) for i in ids]
        human_vector = [ground_truth_rankings.get(i, 999) for i in ids]
        
        # 4. Compute
        if len(ids) < 2:
            return {'rho': 0.0, 'ci_95': (0.0, 0.0), 'p_value': 1.0, 'n': len(ids)}
            
        rho, p_value = spearmanr(sys_vector, human_vector)
        
        # 5. Bootstrap Confidence Interval (95%)
        boot_rhos = []
        n_boot = 1000
        import random
        import numpy as np
        
        if len(ids) >= 4: # Need enough data to bootstrap
            for _ in range(n_boot):
                # Resample with replacement indices
                indices = [random.randint(0, len(ids)-1) for _ in range(len(ids))]
                s_boot = [sys_vector[i] for i in indices]
                h_boot = [human_vector[i] for i in indices]
                # Handle constant input case (all same rank)
                if len(set(s_boot)) > 1 and len(set(h_boot)) > 1:
                     r, _ = spearmanr(s_boot, h_boot)
                     if not np.isnan(r):
                         boot_rhos.append(r)
            
            if boot_rhos:
                ci_low = np.percentile(boot_rhos, 2.5)
                ci_high = np.percentile(boot_rhos, 97.5)
            else:
                ci_low, ci_high = (rho, rho)
        else:
            ci_low, ci_high = (rho, rho) # Not enough data
            
        # 6. Error Analysis
        errors = []
        for sid in ids:
            rank_err = system_ranks[sid] - ground_truth_rankings[sid] # +ve means System ranked it WORSE (higher number) than Human
            errors.append({
                'id': sid,
                'sys_rank': system_ranks[sid],
                'human_rank': ground_truth_rankings[sid],
                'error': rank_err,
                'abs_error': abs(rank_err)
            })
            
        # Sort by absolute error (Failure Cases)
        errors.sort(key=lambda x: x['abs_error'], reverse=True)
        mare = statistics.mean([e['abs_error'] for e in errors])
        
        return {
            'rho': round(rho, 3),
            'ci_95': (round(ci_low, 3), round(ci_high, 3)),
            'p_value': round(p_value, 4),
            'n': len(ids),
            'mare': round(mare, 2),
            'system_ranks': system_ranks,
            'human_ranks': ground_truth_rankings,
            'errors': errors
        }

    def generate_report(self, results):
        if not results: return "No results."
        
        md = "### Blind Ranking Experiment\n"
        md += f"- **N**: {results['n']} scripts\n"
        md += f"- **Spearman Rho**: {results['rho']} (95% CI: [{results['ci_95'][0]}, {results['ci_95'][1]}])\n"
        md += f"- **p-value**: {results['p_value']} (Target: < 0.05)\n"
        md += f"- **Mean Absolute Rank Error (MARE)**: {results.get('mare', 'N/A')}\n\n"
        
        # Interpretation
        rho = results['rho']
        if rho > 0.7: strength = "Strong"
        elif rho > 0.4: strength = "Moderate"
        else: strength = "Weak"
        
        md += f"**CONCLUSION**: {strength} correlation detected.\n\n"
        
        # Failure Analysis
        errors = results.get('errors', [])
        if errors:
            md += "#### Top Disagreements (Failure Cases)\n"
            md += "| Script ID | Sys Rank | Human Rank | Error |\n"
            md += "|---|---|---|---|\n"
            for e in errors[:3]:
                md += f"| {e['id']} | {e['sys_rank']} | {e['human_rank']} | {e['error']} |\n"
        
        return md
