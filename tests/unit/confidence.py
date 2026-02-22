
import statistics

class ConfidenceScorer:
    """
    Computes confidence bands for ScriptPulse v1.3 metrics.
    Prevent overclaiming on short or flat scripts.
    """
    
    def calculate(self, dynamics_trace):
        """
        Returns {'level': 'HIGH'|'MEDIUM'|'LOW', 'score': 0.0-1.0, 'reasons': []}
        """
        if not dynamics_trace:
            return {'level': 'LOW', 'score': 0.0, 'reasons': ['No trace data']}
            
        scene_count = len(dynamics_trace)
        att_signals = [s['attentional_signal'] for s in dynamics_trace]
        variance = statistics.variance(att_signals) if scene_count > 1 else 0.0
        
        reasons = []
        score = 1.0
        
        # 1. Length Penalty (Refined for Chamber Dramas)
        # If scene count is low but average effort is high, it might be a dense play adaptation.
        avg_effort = statistics.mean(att_signals) if att_signals else 0
        
        if scene_count < 10:
            if avg_effort > 0.6:
                score *= 0.8 # Less severe penalty for dense short format
                reasons.append("Low Scene Count (Dense)")
            else:
                score *= 0.5
                reasons.append("Insufficient Length (<10 scenes)")
        elif scene_count < 30:
            if avg_effort > 0.5:
                score *= 0.95 # Minimal penalty
            else:
                score *= 0.8
                reasons.append("Short Script (<30 scenes)")
            
        # 2. Variance Penalty (Flatline detection)
        # Low variance is the real killer of confidence.
        if variance < 0.005:
            score *= 0.6
            reasons.append("Signal Flatline (low_signal_variance)")
        elif variance < 0.02:
            score *= 0.9
            reasons.append("Low Dynamic Range")
            
        # 3. Overload Penalty
        fatigue_ratio = sum(1 for s in dynamics_trace if s['fatigue_state'] > 0) / scene_count
        if fatigue_ratio > 0.8:
            score *= 0.7
            reasons.append("Sustained Overload (high_entropy_instability)")
            
        # Level
        if score >= 0.85: level = 'HIGH'
        elif score >= 0.6: level = 'MEDIUM'
        else: level = 'LOW'
        
        return {
            'level': level,
            'score': round(score, 2),
            'reasons': reasons
        }
