#!/usr/bin/env python3
"""
Synthetic Ground Truth Generator
Generates a mock dataset of 50 screenplays with simulated human ratings to allow the validation pipeline to run end-to-end for testing purposes before real human data is collected.
"""

import csv
import random
import os

def generate_synthetic_corpus(output_path, num_scripts=50, scenes_per_script=5):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'script_id', 'scene_index', 
            'human_effort_mean', 'human_tension_mean', 
            'human_satisfaction_mean', 'rater_count'
        ])
        
        for i in range(1, num_scripts + 1):
            script_id = f"SCRIPT_{i:03d}"
            
            # Simulate a narrative arc
            for scene_idx in range(1, scenes_per_script + 1):
                # Simulated effort generally rises then falls
                base_effort = 0.3 + (scene_idx / scenes_per_script) * 0.4
                noise_effort = random.uniform(-0.15, 0.15)
                effort = min(1.0, max(0.0, base_effort + noise_effort))
                
                # Tension spikes near the end
                if scene_idx == scenes_per_script - 1:
                    base_tension = 0.8
                else:
                    base_tension = random.uniform(0.1, 0.5)
                tension = min(1.0, max(0.0, base_tension + random.uniform(-0.1, 0.1)))
                
                satisfaction = min(1.0, max(0.0, 0.5 + (tension * 0.3) - (effort * 0.2)))
                
                writer.writerow([
                    script_id,
                    scene_idx,
                    round(effort, 3),
                    round(tension, 3),
                    round(satisfaction, 3),
                    3  # simulated 3 raters
                ])
                
    print(f"✅ Generated synthetic ground truth corpus with {num_scripts * scenes_per_script} scene ratings.")
    print(f"Path: {output_path}")
    print("WARNING: This data is randomly generated for testing the pipeline architecture only. Do not use for actual research conclusions.")

if __name__ == "__main__":
    target_path = os.path.join(os.path.dirname(__file__), 'synthetic_corpus.csv')
    generate_synthetic_corpus(target_path)
