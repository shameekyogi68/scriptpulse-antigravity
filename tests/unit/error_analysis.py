
import statistics

class ErrorAnalyzer:
    """
     profiles failure modes by correlating high residuals with feature values.
    """
    
    def __init__(self):
        pass
        
    def run_analysis(self, aligned_data, features_map):
        """
        aligned_data: list of {'scene_index', 'error', 'system_val', 'human_val'}
        features_map: dict of scene_index -> feature_dict
        """
        # 1. Identify Top Residuals
        sorted_errors = sorted(aligned_data, key=lambda x: x['error'], reverse=True)
        top_failures = sorted_errors[:5]
        
        # 2. Correlate Error with Features
        # We classify scenes as "High Error" vs "Low Error" and check for feature divergence
        high_error_scenes = [f['scene_index'] for f in top_failures]
        all_scenes = [x['scene_index'] for x in aligned_data]
        
        failure_profile = "No significant profile detected."
        
        # Simplified Check for Key Drivers
        metrics = ['action_density', 'dialogue_density', 'readability']
        
        divergences = []
        
        for m in metrics:
            high_err_vals = []
            low_err_vals = []
            
            for idx in all_scenes:
                feat = features_map.get(idx, {})
                # Extract simplified flattened features (assuming standard structure)
                val = 0.5
                if m == 'readability' and 'linguistic_load' in feat:
                     val = feat['linguistic_load'].get('readability_grade', 0)
                # ... (Simplified extraction for this mock implementation)
                
                if idx in high_error_scenes:
                    high_err_vals.append(val)
                else:
                    low_err_vals.append(val)
            
            if high_err_vals and low_err_vals:
                avg_high = statistics.mean(high_err_vals)
                avg_low = statistics.mean(low_err_vals)
                if abs(avg_high - avg_low) > 1.0: # Arbitrary threshold for "divergence"
                     divergences.append(f"{m} (Avg High-Error: {avg_high:.1f} vs Normal: {avg_low:.1f})")
                     
        if divergences:
            failure_profile = "Valid reliability issues detected in scenes with: " + ", ".join(divergences)
            
        return {
            'top_failures': top_failures,
            'failure_profile': failure_profile
        }

    def generate_report(self, metrics):
        md = "### Error Analysis & Failure Audit\n\n"
        md += f"**Failure Profile**: {metrics['failure_profile']}\n\n"
        md += "**Top 5 Residuals (Largest Errors)**:\n"
        md += "| Scene | System | Human | Error |\n"
        md += "|---|---|---|---|\n"
        for f in metrics['top_failures']:
            md += f"| {f['scene_index']} | {f['system_val']:.2f} | {f['human_val']:.2f} | {f['error']:.2f} |\n"
            
        return md
