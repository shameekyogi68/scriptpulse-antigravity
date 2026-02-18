
import math

class Calibration:
    """
    Assesses the reliability of confidence scores.
    """
    
    def __init__(self, n_bins=5):
        self.n_bins = n_bins
        
    def compute_calibration(self, predictions):
        """
        predictions: list of dicts {
            'confidence': float (0-1),
            'actual_error': float (abs diff between system and human),
            'is_correct_proxy': bool (e.g. error < 0.2)
        }
        """
        bins = {i: {'conf_sum': 0.0, 'correct_sum': 0.0, 'count': 0} for i in range(self.n_bins)}
        bin_size = 1.0 / self.n_bins
        
        for p in predictions:
            conf = p['confidence']
            # Determine success (using a threshold on error as a proxy for 'correct' in regression)
            # In regression, "calibration" usually means Prob(error < X) matches Confidence
            # Here we simplify: strict confidence (1.0) should imply near-zero error.
            # We map "Confidence" to "Probability of being within tolerance"
            is_acc = 1.0 if p.get('is_correct_proxy', False) else 0.0
            
            bin_idx = min(int(conf / bin_size), self.n_bins - 1)
            bins[bin_idx]['conf_sum'] += conf
            bins[bin_idx]['correct_sum'] += is_acc
            bins[bin_idx]['count'] += 1
            
        reliability_diagram = []
        total_count = len(predictions)
        ece = 0.0
        
        for i in range(self.n_bins):
            b = bins[i]
            if b['count'] > 0:
                avg_conf = b['conf_sum'] / b['count']
                avg_acc = b['correct_sum'] / b['count']
                reliability_diagram.append({
                    'bin_range': f"{i*bin_size:.1f}-{(i+1)*bin_size:.1f}",
                    'avg_confidence': round(avg_conf, 3),
                    'avg_accuracy': round(avg_acc, 3),
                    'count': b['count']
                })
                
                weight = b['count'] / total_count
                ece += weight * abs(avg_conf - avg_acc)
                
        return {
            'ece': round(ece, 4),
            'reliability_diagram': reliability_diagram
        }
        
    def generate_report(self, metrics):
        md = "### Uncertainty Calibration\n\n"
        md += f"**Expected Calibration Error (ECE)**: {metrics['ece']}\n"
        if metrics['ece'] < 0.1:
            md += "*(System confidence is well-calibrated)*\n\n"
        else:
            md += "*(System is over/under-confident)*\n\n"
            
        md += "| Bin Range | Avg Confidence | Actual Accuracy | Count |\n"
        md += "|---|---|---|---|\n"
        for bin_data in metrics['reliability_diagram']:
            md += f"| {bin_data['bin_range']} | {bin_data['avg_confidence']} | {bin_data['avg_accuracy']} | {bin_data['count']} |\n"
        return md
