
import numpy as np
import json
from scipy.optimize import minimize

class ParameterLearner:
    """
    vNext.9 Research Tool: Data-Driven Parameter Learning.
    
    Objective: Fit the fatigue decay parameter (\u03bb) to minimize error between 
    Predicted Effort (Model) and Accumulated Fixation Duration (Human Gaze).
    """
    
    def __init__(self, genre_data):
        self.genre_data = genre_data # Dict of {genre: [sessions]}
        
    def canonical_equation(self, features, lam):
        """Reconstruct trace with specific lambda."""
        s = 0
        trace = []
        for f in features:
            s = f + (lam * s)
            trace.append(s)
        return np.array(trace)
        
    def loss_function(self, lam, human_trace, features):
        """RSS Error between Model and Human."""
        model_trace = self.canonical_equation(features, lam[0])
        # Normalize both
        model_norm = (model_trace - np.mean(model_trace)) / (np.std(model_trace) + 1e-9)
        human_norm = (human_trace - np.mean(human_trace)) / (np.std(human_trace) + 1e-9)
        
        return np.sum((model_norm - human_norm) ** 2)
        
    def fit_genre_lambda(self, genre):
        """Find optimal Lambda for a specific genre."""
        print(f"--- Fitting Parameters for Genre: {genre} ---")
        sessions = self.genre_data.get(genre, [])
        
        best_lambdas = []
        
        for sess in sessions:
            # Mock extracted features (E[i]) and Human Gaze (Y)
            n_scenes = 50
            features = np.random.beta(2, 5, n_scenes) # Skewed low effort
            
            # Simulate Human Trace with "True" Hidden Lambda + Noise
            true_lambda = 0.92 if genre == 'Horror' else 0.75
            hidden_trace = self.canonical_equation(features, true_lambda)
            human_gaze = hidden_trace + np.random.normal(0, 0.1, n_scenes)
            
            # Minimize
            result = minimize(self.loss_function, x0=[0.85], args=(human_gaze, features), bounds=[(0.5, 0.99)])
            best_lambdas.append(result.x[0])
            
        # Stats
        mean_lambda = np.mean(best_lambdas)
        ci_lower = np.percentile(best_lambdas, 2.5)
        ci_upper = np.percentile(best_lambdas, 97.5)
        
        print(f"Optimal Lambda: {mean_lambda:.3f} (95% CI: [{ci_lower:.3f}, {ci_upper:.3f}])")
        return mean_lambda, (ci_lower, ci_upper)

if __name__ == "__main__":
    # Mock N=100 Data (25 per genre)
    data = {
        'Horror': range(25),
        'Comedy': range(25),
        'Drama': range(25),
        'Action': range(25)
    }
    
    learner = ParameterLearner(data)
    
    results = {}
    for genre in data:
        results[genre] = learner.fit_genre_lambda(genre)
        
    print("\n--- Final Learned Parameter Table ---")
    print(json.dumps(results, indent=2))
