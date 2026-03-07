import os
import ssl
import urllib.request
import traceback

# Bypass SSL locally
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SCRIPTS = {
    "Big_Fish.txt": "https://raw.githubusercontent.com/nyousefi/Fountain/master/Tests/Support%20Files/Big%20Fish.fountain",
    "Brick_and_Steel.txt": "https://raw.githubusercontent.com/nyousefi/Fountain/master/Tests/Support%20Files/Brick%20%26%20Steel.fountain",
    "The_Last_Eye.txt": "https://raw.githubusercontent.com/nyousefi/Fountain/master/Tests/Support%20Files/The%20Last%20Eye.fountain",
    "Slingshot.txt": "https://raw.githubusercontent.com/nyousefi/Fountain/master/Tests/Support%20Files/Slingshot.fountain",
    "The_Spalding_Enigma.txt": "https://raw.githubusercontent.com/nyousefi/Fountain/master/Tests/Support%20Files/The%20Spalding%20Enigma.fountain",
    "Frankenstein.txt": "https://raw.githubusercontent.com/mattdaly/Fountain.js/master/spec/fountain/Frankenstein.fountain",
    "Batman.txt": "https://raw.githubusercontent.com/mattdaly/Fountain.js/master/spec/fountain/Batman.fountain",
    "Action_Movie.txt": "https://raw.githubusercontent.com/mattdaly/Fountain.js/master/spec/fountain/Action_Movie.fountain"
}

demo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo"))
os.makedirs(demo_dir, exist_ok=True)

# Step 1: Download
downloaded = []
for name, url in SCRIPTS.items():
    print(f"Downloading {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            content = response.read().decode('utf-8')
        
        # Simple check to avoid 404 pages disguised as text
        if "404: Not Found" in content or content.strip() == "404: Not Found":
            print(f"  [Error] 404 for {url}")
            continue
            
        filepath = os.path.join(demo_dir, name)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        downloaded.append(filepath)
    except Exception as e:
        print(f"  [Error] Failed to download {name}: {e}")

# Step 2: Validate with ScriptPulse
import sys
sys.path.insert(0, os.path.dirname(__file__))
from scriptpulse.pipeline import runner

valid_scripts = []

for filepath in downloaded:
    name = os.path.basename(filepath)
    print(f"\nEvaluating {name}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Run pipeline
        report = runner.run_pipeline(text, experimental_mode=True, moonshot_mode=True)
        
        # Checks
        if not report:
            print(f"  ❌ FAILED: Pipeline returned None.")
            os.remove(filepath)
            continue
            
        scenes = report.get('total_scenes', 0)
        if scenes < 2:
            print(f"  ❌ FAILED: Found only {scenes} scenes. Needs >1 to be a valid demo script.")
            os.remove(filepath)
            continue
            
        trace = report.get('temporal_trace', [])
        if len(trace) != scenes:
            print(f"  ❌ FAILED: Temporal trace mismatch ({len(trace)} vs {scenes} scenes).")
            os.remove(filepath)
            continue
            
        # Success!
        print(f"  ✅ SUCCESS: Validated {scenes} scenes.")
        valid_scripts.append(name)
        
    except Exception as e:
        print(f"  ❌ FAILED: Execution error -> {e}")
        traceback.print_exc()
        os.remove(filepath)

print("\n" + "="*40)
print("FINAL VALID DEMO SCRIPTS:")
print("="*40)
for v in valid_scripts:
    print(f"- {v}")

