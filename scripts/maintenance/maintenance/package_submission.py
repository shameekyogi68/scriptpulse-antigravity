import zipfile
import os
import datetime

def package_submission():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"ScriptPulse_Artifact_{timestamp}.zip"
    
    # Files/Dirs to include
    includes = [
        'scriptpulse',
        'data',
        'config',
        'reproduce_results.py',
        'benchmark_suite.py',
        'ablation_study.py',
        'requirements.txt',
        'README.md',
        'RELEASE_README.md',
        'PAPER_METHODS.md',
        'LICENSE'
    ]
    
    # Files/Dirs to exclude patterns
    excludes = [
        '__pycache__',
        '.DS_Store',
        '.git',
        '.gemini',
        'venv',
        'output',
        '.pytest_cache',
        '.vscode'
    ]

    print(f"📦 Packaging submission into {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for item in includes:
            if os.path.isfile(item):
                print(f"  Adding file: {item}")
                zipf.write(item)
            elif os.path.isdir(item):
                print(f"  Adding dir:  {item}")
                for root, dirs, files in os.walk(item):
                    # Filter exclusions
                    dirs[:] = [d for d in dirs if d not in excludes]
                    files = [f for f in files if f not in excludes and not f.endswith('.pyc')]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
            else:
                print(f"⚠️ Warning: {item} not found.")

    print(f"✅ Submission Ready: {output_filename}")
    print(f"   Size: {os.path.getsize(output_filename) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    package_submission()
