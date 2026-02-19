
import csv
import numpy as np

try:
    import krippendorff
except ImportError:
    krippendorff = None

class InterRaterReliability:
    """
    Validation Experiment 3: Human Annotation Agreement
    Computes Krippendorff's Alpha for ground truth datasets.
    """
    
    def calculate_alpha(self, ratings_file):
        """
        ratings_file: CSV with cols [script_id, rater_id, scene_index, score]
        Returns alpha value.
        """
        if not krippendorff:
            return {'error': 'krippendorff library not installed'}
            
        # Parse CSV into reliability matrix (Units x Raters)
        # For simplicity, we assume one script analysis
        # Matrix shape: [Raters, Units]
        
        data = []
        with open(ratings_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
        if not data: return {'alpha': 0.0}
        
        # Group by Rater
        raters = set(d['rater_id'] for d in data)
        units = set(d['scene_index'] for d in data) # Assuming single script context
        
        # Build Matrix format for krippendorff
        # value_counts[rater_index][unit_index]
        rater_map = {r: i for i, r in enumerate(sorted(raters))}
        unit_map = {u: i for i, u in enumerate(sorted(units, key=int))}
        
        matrix = [[np.nan for _ in range(len(units))] for _ in range(len(raters))]
        
        for row in data:
            r_idx = rater_map[row['rater_id']]
            u_idx = unit_map[row['scene_index']]
            try:
                val = float(row['score'])
                matrix[r_idx][u_idx] = val
            except ValueError:
                pass
                
        # Compute Alpha (Interval data)
        alpha = krippendorff.alpha(reliability_data=matrix, level_of_measurement='interval')
        
        # Bootstrap CI for Alpha (Resample Units/Columns)
        # matrix is [Raters, Units]
        n_boot = 1000
        boot_alphas = []
        n_units = len(units)
        import random
        import numpy as np
        
        if n_units >= 5:
            matrix_np = np.array(matrix) # [R, U]
            for _ in range(n_boot):
                indices = [random.randint(0, n_units-1) for _ in range(n_units)]
                resampled_matrix = matrix_np[:, indices]
                # Check for variance in resample
                try:
                    a = krippendorff.alpha(reliability_data=resampled_matrix, level_of_measurement='interval')
                    if not np.isnan(a):
                        boot_alphas.append(a)
                except:
                    pass
            
            if boot_alphas:
                ci_low = np.percentile(boot_alphas, 2.5)
                ci_high = np.percentile(boot_alphas, 97.5)
            else:
                ci_low, ci_high = (alpha, alpha)
        else:
            ci_low, ci_high = (alpha, alpha)

        return {
            'alpha': round(alpha, 3),
            'ci_95': (round(ci_low, 3), round(ci_high, 3)),
            'n_raters': len(raters),
            'n_units': len(units)
        }
