
import csv
import math
import statistics
import os

from .calibration import Calibration
from .error_analysis import ErrorAnalyzer

class HumanAligner:
    """
    Aligns ScriptPulse system outputs with Human Ground Truth ratings.
    Calculates Pearson/Spearman correlation and error metrics.
    Integtrates Calibration and Error Analysis.
    """
    
    def __init__(self, ground_truth_path, multi_rater=False):
        self.multi_rater = multi_rater
        self.ground_truth = self._load_ground_truth(ground_truth_path)
        
    def _load_ground_truth(self, path):
        if not os.path.exists(path):
            print(f"Warning: Ground truth file not found at {path}")
            return {}
            
        gt = {}
        raw_ratings = {} # Key: (script_id, scene_idx) -> {'effort': [r1, r2...], 'tension': [r1...]}
        
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['script_id'], int(row['scene_index']))
                
                if self.multi_rater:
                    if key not in raw_ratings:
                         raw_ratings[key] = {'effort': [], 'tension': []}
                    raw_ratings[key]['effort'].append(float(row['effort_rating']))
                    raw_ratings[key]['tension'].append(float(row['tension_rating']))
                else:
                    gt[key] = {
                        'effort': float(row['human_effort_mean']),
                        'tension': float(row['human_tension_mean']),
                        'satisfaction': float(row.get('human_satisfaction_mean', 0))
                    }
        
        if self.multi_rater:
            # Aggregation step
            for key, data in raw_ratings.items():
                gt[key] = {
                    'effort': statistics.mean(data['effort']),
                    'tension': statistics.mean(data['tension']),
                    'effort_std': statistics.stdev(data['effort']) if len(data['effort']) > 1 else 0,
                    'tension_std': statistics.stdev(data['tension']) if len(data['tension']) > 1 else 0,
                    'raw_effort': data['effort'], # Store raw for Krippendorff
                    'raw_tension': data['tension']
                }
                
        return gt

    def calculate_alignment(self, script_id, system_scenes, features_map=None):
        """
        system_scenes: list of dicts with 'scene_index', 'effort_score', 'tension_score'
        """
        aligned_effort_x = [] # System
        aligned_effort_y = [] # Human
        
        aligned_tension_x = []
        aligned_tension_y = []
        
        missing_scenes = 0
        
        # Collect aligned data for advanced analysis
        aligned_data = [] # List of {'scene_index', 'error', 'system', 'human', 'confidence'}
        predictions_for_calib = []
        


        for scene in system_scenes:
            idx = scene.get('scene_index')
            key = (script_id, idx)
            
            if key in self.ground_truth:
                human = self.ground_truth[key]
                
                # Effort Alignment
                sys_effort = scene.get('effort_score', 0.5)
                aligned_effort_x.append(sys_effort)
                aligned_effort_y.append(human['effort'])
                
                # Tension Alignment
                sys_tension = scene.get('tension_score', 0.5)
                aligned_tension_x.append(sys_tension)
                aligned_tension_y.append(human['tension'])
                
                # Calibration & Error Data
                error = abs(sys_effort - human['effort'])
                conf = scene.get('confidence_score', 0.8)
                
                aligned_data.append({
                    'scene_index': idx,
                    'error': error,
                    'system_val': sys_effort,
                    'human_val': human['effort']
                })
                
                predictions_for_calib.append({
                    'confidence': conf,
                    'is_correct_proxy': error < 0.15
                })

            else:
                missing_scenes += 1
                
        # Run Calibration
        calib = Calibration()
        calib_metrics = calib.compute_calibration(predictions_for_calib)
        
        # Run Error Analysis
        err_analyzer = ErrorAnalyzer()
        err_metrics = err_analyzer.run_analysis(aligned_data, features_map or {})
                
        results = {
            'effort_metrics': self._compute_metrics(aligned_effort_x, aligned_effort_y),
            'tension_metrics': self._compute_metrics(aligned_tension_x, aligned_tension_y),
            'coverage': len(aligned_effort_x) / (len(aligned_effort_x) + missing_scenes) if (len(aligned_effort_x) + missing_scenes) > 0 else 0,
            'calibration_metrics': calib_metrics,
            'error_analysis_metrics': err_metrics
        }
        
        return results

    def _compute_metrics(self, x, y):
        if len(x) < 2: return {'status': 'insufficient_data'}
        
        # Pearson Correlation
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den_x = math.sqrt(sum((xi - mean_x)**2 for xi in x))
        den_y = math.sqrt(sum((yi - mean_y)**2 for yi in y))
        
        pearson = numerator / (den_x * den_y) if (den_x * den_y) > 0 else 0
        
        # Spearman (Rank) Correlation
        rank_x = self._rank(x)
        rank_y = self._rank(y)
        d_squared = sum((rx - ry)**2 for rx, ry in zip(rank_x, rank_y))
        n = len(x)
        spearman = 1 - (6 * d_squared) / (n * (n**2 - 1))
        
        # Error Metrics
        errors = [xi - yi for xi, yi in zip(x, y)]
        mae = statistics.mean([abs(e) for e in errors])
        rmse = math.sqrt(statistics.mean([e**2 for e in errors]))
        
        return {
            'pearson_r': round(pearson, 3),
            'spearman_rho': round(spearman, 3),
            'mae': round(mae, 3),
            'rmse': round(rmse, 3),
            'n': n
        }

    def _rank(self, data):
        """Helper to rank data for Spearman"""
        indexed = sorted([(v, i) for i, v in enumerate(data)])
        ranks = [0] * len(data)
        for rank, (val, idx) in enumerate(indexed):
            ranks[idx] = rank + 1
        return ranks

    def calculate_agreement(self):
        """Calculates Inter-Rater Reliability (Krippendorff's Alpha approximation)"""
        if not self.multi_rater:
            return {'status': 'not_multi_rater'}
            
        # Extract reliability data for Effort and Tension
        effort_matrix = []
        tension_matrix = []
        
        for key, data in self.ground_truth.items():
            if 'raw_effort' in data:
                effort_matrix.append(data['raw_effort'])
            if 'raw_tension' in data:
                tension_matrix.append(data['raw_tension'])
                
        return {
            'effort_alpha': self._krippendorff_alpha(effort_matrix),
            'tension_alpha': self._krippendorff_alpha(tension_matrix)
        }

    def _krippendorff_alpha(self, data_matrix):
        """
        Calculates Alpha for interval data. 
        """
        if not data_matrix: return 0.0
        
        all_values = [v for row in data_matrix for v in row]
        if len(set(all_values)) <= 1: return 0.0 
        
        n_units = len(data_matrix)
        n_raters = len(data_matrix[0])
        total_votes = n_units * n_raters
        
        mean_all = statistics.mean(all_values)
        De = sum((v - mean_all)**2 for v in all_values)
        
        Do = 0
        for row in data_matrix:
            row_mean = statistics.mean(row)
            Do += sum((v - row_mean)**2 for v in row)
            
        if De == 0: return 1.0
        
        within_var = Do / max(1, (total_votes - n_units))
        total_var = De / max(1, (total_votes - 1))
        
        if total_var == 0: return 0.0
        
        alpha = 1 - (within_var / total_var)
        return round(alpha, 3)

    def generate_report(self, results, agreement_metrics=None):
        """Generates a Markdown report snippet"""
        md = "### Human Alignment Report\n\n"
        
        if agreement_metrics and 'effort_alpha' in agreement_metrics:
            md += "**Inter-Rater Reliability (Human-Human Agreement)**\n"
            md += f"- **Effort Alpha**: {agreement_metrics['effort_alpha']}\n"
            md += f"- **Tension Alpha**: {agreement_metrics['tension_alpha']}\n\n"
        
        md += "| Metric | Pearson (r) | Spearman (rho) | MAE | RMSE | N |\n"
        md += "|---|---|---|---|---|---|\n"
        
        for signal_name, metrics in results.items():
            if isinstance(metrics, dict) and 'pearson_r' in metrics:
                md += f"| **{signal_name.replace('_metrics', '').title()}** | {metrics['pearson_r']} | {metrics['spearman_rho']} | {metrics['mae']} | {metrics['rmse']} | {metrics['n']} |\n"
            elif signal_name != 'coverage' and 'metrics' not in signal_name:
                md += f"| **{signal_name}** | N/A | N/A | N/A | N/A | <2 |\n"
                
        md += f"\n**Coverage**: {results.get('coverage', 0)*100:.1f}% of scenes matched ground truth.\n\n"

        if 'calibration_metrics' in results:
             calib = Calibration()
             md += calib.generate_report(results['calibration_metrics'])
             
        if 'error_analysis_metrics' in results:
             err = ErrorAnalyzer()
             md += err.generate_report(results['error_analysis_metrics'])
             
        return md
