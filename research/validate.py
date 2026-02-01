"""
ScriptPulse Research - K-Fold Cross Validation
Gap Solved: "Overfitting"

This script performs K-Fold Cross Validation to prove system robustness.
It splits the Ground Truth data, trains parameters on N-1 folds, 
and validates on the remaining fold.

IEEE Standard: Prove generalization capability.
"""

import sys
import os
import random
import statistics

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scriptpulse import runner
from scriptpulse.agents import temporal
from research import calibrate # Reuse objective function

def run_k_fold(script_file, data_file='research/human_data.csv', k=5):
    print(f"=== K-Fold Cross Validation (k={k}) ===")
    
    with open(script_file, 'r') as f:
        text = f.read()
    
    # Load all available data
    full_data = calibrate.load_human_data(data_file)
    scene_indices = list(full_data.keys())
    random.shuffle(scene_indices)
    
    # Split into K folds
    fold_size = len(scene_indices) // k
    folds = [scene_indices[i:i + fold_size] for i in range(0, len(scene_indices), fold_size)]
    
    # Handle remainder
    if len(folds) > k:
        folds[k-1].extend(folds[k])
        folds = folds[:k]
        
    results = []
    
    print(f"Data points: {len(scene_indices)}. Fold size: ~{fold_size}")
    
    for i in range(k):
        print(f"\nTraining Fold {i+1}/{k}...")
        
        # Split Train/Test
        test_indices = folds[i]
        train_indices = [idx for f in folds if f != test_indices for idx in f]
        
        train_data = {idx: full_data[idx] for idx in train_indices}
        test_data = {idx: full_data[idx] for idx in test_indices}
        
        # Optimize on Training Data (Simplified Hill Climb)
        best_params = optimize_on_subset(text, train_data)
        
        # Evaluate on Train
        train_score = calibrate.objective_function(best_params, text, train_data)
        
        # Evaluate on Test (Unseen Data)
        test_score = calibrate.objective_function(best_params, text, test_data)
        
        print(f"  Params: L={best_params['lambda']:.2f}, B={best_params['beta']:.2f}")
        print(f"  Train r: {train_score:.4f}")
        print(f"  Test r:  {test_score:.4f}")
        
        results.append({'train': train_score, 'test': test_score})
        
    # Aggregate
    avg_train = statistics.mean([r['train'] for r in results])
    avg_test = statistics.mean([r['test'] for r in results])
    
    print("\n=== VALIDATION SUMMARY ===")
    print(f"Avg Training Correlation: {avg_train:.4f}")
    print(f"Avg Testing Correlation:  {avg_test:.4f}")
    print(f"Generalization Gap:       {abs(avg_train - avg_test):.4f}")
    
    if abs(avg_train - avg_test) < 0.15:
        print("✅ SUCCESS: System generalizes well (Low Overfitting).")
    else:
        print("⚠️ WARNING: High Generalization Gap (Possible Overfitting).")

def optimize_on_subset(text, human_data):
    """Simplified optimizer for the loop"""
    # Reuse logic from calibrate, but quicker
    best_params = {'lambda': 0.85, 'beta': 0.3}
    best_score = calibrate.objective_function(best_params, text, human_data)
    
    # Quick 10-step search
    for _ in range(10):
        c = {
            'lambda': max(0.1, min(0.99, best_params['lambda'] + random.uniform(-0.1, 0.1))),
            'beta': max(0.1, min(0.9, best_params['beta'] + random.uniform(-0.1, 0.1)))
        }
        s = calibrate.objective_function(c, text, human_data)
        if s > best_score:
            best_score = s
            best_params = c
    return best_params

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research/validate.py <script_file>")
        sys.exit(1)
    run_k_fold(sys.argv[1])
