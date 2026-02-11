"""
ScriptPulse vNext.11 - Insight Cascade Agent
Objective: Measure "Aha!" moments via Information Bottleneck Theory.
"""

class InsightAgent:
    def __init__(self):
        self.prev_entropy = 0.5 # Initial baseline entropy
        
    def detect_cascade(self, current_entropy):
        """
        Detects massive entropy drops indicating insight.
        
        Args:
            current_entropy (float): The current entropy/expectation strain.
            
        Returns:
            dict: Insight analysis results.
        """
        delta = self.prev_entropy - current_entropy
        
        is_insight = False
        label = "Stable"
        
        if delta > 0.2:
            is_insight = True
            label = "Insight Cascade (Aha!)"
        elif delta < -0.2:
            label = "Confusion Spike"
            
        self.prev_entropy = current_entropy
        
        return {
            'entropy_delta': delta,
            'is_insight': is_insight,
            'label': label
        }
