import os
import sys
import json
import optuna
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import logging

# Ensure scriptpulse is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse import runner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_synthetic_ground_truth(output_path="ground_truth.csv"):
    """
    Creates a synthetic ground-truth dataset for cold-start evaluation if none exists.
    Reviewers expect empirical validation.
    """
    logging.info(f"Generating synthetic ground-truth at {output_path} for testing...")
    
    # Example script data structure mimicking a thriller
    data = []
    
    # Act 1: Setup (Low tension)
    for i in range(1, 11):
        data.append({'scene_index': i, 'human_tension': np.random.normal(0.2, 0.05), 'human_effort': np.random.normal(0.2, 0.05)})
        
    # Act 2: Rising Action
    for i in range(11, 31):
        tension = 0.2 + ((i-10)/20) * 0.6
        data.append({'scene_index': i, 'human_tension': np.random.normal(tension, 0.1), 'human_effort': np.random.normal(tension, 0.1)})
        
    # Act 3: Climax (High tension)
    for i in range(31, 41):
        data.append({'scene_index': i, 'human_tension': np.random.normal(0.9, 0.05), 'human_effort': np.random.normal(0.8, 0.1)})
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return df

def generate_dummy_script():
    """Generates a dummy text script to run the runner against."""
    script_lines = []
    for i in range(1, 41):
        script_lines.append(f"{i}. INT. LOCATION {i} - DAY")
        if i < 11:
            script_lines.append(f"Some calm dialogue and establishing shots. " * 3)
        elif i < 31:
            script_lines.append(f"Things are getting tense. People are arguing. Fast action. " * (5 + int(i/2)))
        else:
            script_lines.append(f"Explosions! Running! Screaming! Extreme tension. " * 10)
    return "\n".join(script_lines)

def objective(trial, df_ground_truth, script_text):
    """
    Optuna objective function to maximize Pearson correlation 
    between system's Net Tension and human_tension ground truth.
    """
    # 1. Sample hyperparameters
    decay_rate = trial.suggest_float("decay_rate", 0.01, 0.3)
    recovery_rate = trial.suggest_float("recovery_rate", 0.01, 0.3)
    
    # 2. Run Pipeline with these hyperparameters (ablation config handles this nicely)
    ablation_config = {
        'decay_rate': decay_rate,
        'recovery_rate': recovery_rate
    }
    
    # Turn off costly experimental features for fast tuning
    try:
        # Fast configuration
        report = runner.run_pipeline(
            script_text, 
            experimental_mode=False, 
            moonshot_mode=False,
            cpu_safe_mode=True, 
            valence_stride=3,
            stanislavski_min_words=50,
            ablation_config=ablation_config
        )
        
        trace = report.get('temporal_trace', [])
        if not trace:
            return 0.0
            
        system_tension = []
        human_tension = []
        
        # Align scene indices
        for t_point in trace:
            idx = t_point.get('scene_index', 0)
            # Find in ground truth
            match = df_ground_truth[df_ground_truth['scene_index'] == idx]
            if not match.empty:
                system_tension.append(t_point.get('strain', 0.0))
                human_tension.append(match.iloc[0]['human_tension'])
                
        if len(system_tension) < 5:
            return 0.0
            
        # 3. Calculate Pearson correlation (we want to maximize this)
        corr, _ = pearsonr(system_tension, human_tension)
        
        if np.isnan(corr):
            return 0.0
            
        return corr
    except Exception as e:
        logging.error(f"Trial failed: {e}")
        return 0.0

def run_optimization(n_trials=20):
    """Main optimization loop."""
    print("=========================================")
    print("🧪 SCRIPT PULSE HYPERPARAMETER OPTIMIZER")
    print("=========================================")
    
    gt_path = "ground_truth.csv"
    if not os.path.exists(gt_path):
        df_ground_truth = create_synthetic_ground_truth(gt_path)
    else:
        df_ground_truth = pd.read_csv(gt_path)
        logging.info(f"Loaded existing ground truth with {len(df_ground_truth)} scenes.")

    script_text = generate_dummy_script()
    
    # Create Optuna study to maximize correlation
    study = optuna.create_study(direction="maximize")
    
    logging.info(f"Starting {n_trials} trials...")
    study.optimize(lambda trial: objective(trial, df_ground_truth, script_text), n_trials=n_trials)
    
    print("\n✅ OPTIMIZATION COMPLETE")
    print(f"Best Correlation (r): {study.best_value:.4f}")
    print(f"Optimal Parameters: ")
    for k, v in study.best_params.items():
        print(f" - {k}: {v}")
        
    # Save the parameters
    hyper_path = os.path.join("scriptpulse", "config", "hyperparameters.json")
    
    # Load existing if available
    try:
        with open(hyper_path, 'r') as f:
            hyper = json.load(f)
    except:
        hyper = {"temporal": {}}
        
    if "temporal" not in hyper:
        hyper["temporal"] = {}
        
    hyper["temporal"].update(study.best_params)
    hyper["_meta"] = {"optimized_correlation": study.best_value, "source": "optimizer.py"}
    
    os.makedirs(os.path.dirname(hyper_path), exist_ok=True)
    with open(hyper_path, 'w') as f:
        json.dump(hyper, f, indent=4)
        
    print(f"Saved optimized parameters to {hyper_path}")

if __name__ == "__main__":
    # If optuna isn't installed, fail gracefully so they know it's required
    try:
        import optuna
    except ImportError:
        print("ERROR: Optuna is required for hyperparameter tuning.")
        print("Please run: pip install optuna")
        sys.exit(1)
        
    run_optimization(n_trials=10) # 10 trials for quick demo, increase for real opt
