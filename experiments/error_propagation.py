
import sys
import os
import random
import numpy as np

# Simulate dependency
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

class ErrorPropagationStudy:
    """
    vNext.9 Study: How does structural misclassification affect the Audience Model?
    Method: Monte Carlo Perturbation of Tag Labels.
    """
    
    def __init__(self, script_length=100):
        self.script_length = script_length
        # Baseline Schema: A standard Action-Dialogue-Action fluid scene
        self.baseline_tags = ['A', 'D', 'C', 'D'] * (script_length // 4)
        
    def calculate_trace(self, tags):
        """
        Simplified model of encoding + temporal dynamics.
        """
        s_trace = []
        s_curr = 0.0
        decay = 0.85 # Standard
        
        for tag in tags:
            # Simplified Effort Weights
            e_instant = 0.0
            if tag == 'A': e_instant = 0.15 # Visual load
            elif tag == 'D': e_instant = 0.25 # Semantic load
            elif tag == 'S': e_instant = 0.30 # Context switch
            
            # Canonical Equation
            s_curr = e_instant + (decay * s_curr)
            s_trace.append(s_curr)
            
        return np.array(s_trace)

    def run_perturbation(self, error_rate=0.20, n_trials=100):
        """
        Injects error_rate noise into tags and measures RMSE from baseline trace.
        """
        print(f"--- Running Error Propagation Test (Noise={error_rate:.0%}, N={n_trials}) ---")
        
        baseline_trace = self.calculate_trace(self.baseline_tags)
        deviations = []
        
        possible_tags = ['A', 'D', 'S', 'C']
        
        for _ in range(n_trials):
            perturbed_tags = []
            for tag in self.baseline_tags:
                if random.random() < error_rate:
                    # Inject Error
                    perturbation = random.choice([t for t in possible_tags if t != tag])
                    perturbed_tags.append(perturbation)
                else:
                    perturbed_tags.append(tag)
            
            trace = self.calculate_trace(perturbed_tags)
            
            # RMSE
            rmse = np.sqrt(np.mean((baseline_trace - trace)**2))
            deviations.append(rmse)
            
        avg_rmse = np.mean(deviations)
        std_rmse = np.std(deviations)
        
        print(f"Result: Average Trace Deviation (RMSE): {avg_rmse:.4f} ± {std_rmse:.4f}")
        
        if avg_rmse < 0.10:
            print("[PASS] System is Robust to Parser Noise.")
        else:
            print("[WARN] significant signal drift due to parser error.")
            
        return avg_rmse

if __name__ == "__main__":
    study = ErrorPropagationStudy()
    # Test 1: Regex-level noise (20%)
    study.run_perturbation(0.20)
    # Test 2: BERT-level noise (5%)
    study.run_perturbation(0.05)
