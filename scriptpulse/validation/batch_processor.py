import os
import glob
import pandas as pd
import argparse
from pathlib import Path
from tqdm import tqdm

from scriptpulse.runner import run_pipeline

def process_corpus(corpus_dir: str, output_csv: str):
    """
    Ingests a directory of scripts, runs the full research pipeline on each,
    and flattens the results into a single empirical dataset suitable for analysis.
    """
    corpus_path = Path(corpus_dir)
    if not corpus_path.exists() or not corpus_path.is_dir():
        print(f"Error: Corpus directory '{corpus_dir}' not found.")
        return

    # Find all .txt files in the corpus directory
    script_files = list(corpus_path.glob('*.txt'))
    if not script_files:
        print(f"No .txt files found in '{corpus_dir}'.")
        return

    print(f"Found {len(script_files)} scripts in '{corpus_dir}'. Beginning batch processing...")

    all_scenes_data = []

    for script_file in tqdm(script_files, desc="Processing Scripts"):
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()

            script_title = script_file.stem

            # Run the full research pipeline
            # Enable experimental and moonshot modes to get all features
            report = run_pipeline(
                script_content=script_content,
                experimental_mode=True,
                moonshot_mode=True,
                cpu_safe_mode=True # Default to CPU safe for bulk processing
            )
            
            trace = report.get('temporal_trace', [])
            
            # Flatten the temporal trace into row-wise scene data
            for i, scene_data in enumerate(trace):
                row = {
                    'Script_Title': script_title,
                    'Scene_Index': i+1,
                }
                
                # Extract all scalar features available in the scene data
                for key, value in scene_data.items():
                    if isinstance(value, (int, float, bool, str)):
                        row[key] = value
                    elif isinstance(value, dict):
                        # Flatten simple nested dicts (like 'resonance' or 'insight' outputs)
                        for sub_k, sub_v in value.items():
                             if isinstance(sub_v, (int, float, bool, str)):
                                 row[f"{key}_{sub_k}"] = sub_v
                
                all_scenes_data.append(row)

        except Exception as e:
            print(f"Failed to process '{script_file.name}': {e}")
            continue

    if not all_scenes_data:
        print("No valid scene data extracted. Aborting.")
        return

    # Create DataFrame and Export
    df = pd.DataFrame(all_scenes_data)
    
    # Reorder columns slightly for readability if they exist
    cols = list(df.columns)
    first_cols = ['Script_Title', 'Scene_Index', 'scene_index', 'effort', 'strain', 'recovery']
    ordered_cols = [c for c in first_cols if c in cols] + [c for c in cols if c not in first_cols]
    df = df[ordered_cols]

    df.to_csv(output_csv, index=False)
    print(f"\nBatch processing complete! Flattened dataset saved to: {output_csv}")
    print(f"Total Rows (Scenes): {len(df)}")
    print(f"Total Columns (Features): {len(df.columns)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScriptPulse Batch Processor for Empirical Research")
    parser.add_argument("--corpus", type=str, required=True, help="Directory containing .txt screenplay files")
    parser.add_argument("--output", type=str, default="master_empirical_dataset.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    print("--- ScriptPulse Batch Processor ---")
    process_corpus(args.corpus, args.output)
