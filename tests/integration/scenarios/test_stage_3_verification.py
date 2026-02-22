import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scriptpulse.pipeline.runner import run_pipeline

def test_narrative_intelligence():
    print("Running Narrative Intelligence Verification (Setup/Payoff)...")
    
    # Scene 1 mentions a "gun", Scene 2 does not. No other scenes mention it.
    script_content = """
SCENE 1
EXT. STREET - DAY
JOHN (D)
I have a gun in my pocket.
It is a heavy weapon.

SCENE 2
INT. OFFICE - DAY
MARY (D)
Hello John.
How is your day?
    """
    
    report = run_pipeline(script_content)
    intelligence = report.get('narrative_intelligence', [])
    
    print(f"DEBUG: Found {len(intelligence)} intelligence items.")
    for it in intelligence:
        print(f" - {it['type']}: {it['issue']}")
    
    found_gun = False
    for item in intelligence:
        if "Gun" in item['issue'] and "Dropped Thread" in item['issue']:
            found_gun = True
            print(f"✅ DETECTED: {item['issue']}")
            print(f"Advice: {item['advice']}")
            
    if not found_gun:
        print("❌ FAILED: Dropped thread 'gun' not detected.")
        # Debug scene info
        scenes = report.get('segmented', [])
        print(f"DEBUG: Found {len(scenes)} scenes.")
        for s in scenes:
            print(f" Scene {s['scene_index']} lines: {len(s.get('lines', []))}")
            for l in s.get('lines', []):
                print(f"  [{l.get('tag')}] {l.get('text')}")
        sys.exit(1)

def test_structural_toggles():
    print("\nRunning Structural Diversity Verification (Hero's Journey)...")
    
    # 15 scenes to satisfy thresholds
    script_content = ""
    for i in range(1, 16):
        script_content += f"SCENE {i}\nEXT. LOCATION {i}\nAction {i} happens here. It is very detailed.\n"
    
    # Test Hero's Journey
    report = run_pipeline(script_content, story_framework='heros_journey')
    acts = report.get('structure_map', {}).get('acts', [])
    
    print(f"DEBUG: Found {len(acts)} act markers in structure map.")
    for a in acts:
        print(f" - {a['name']}: {a['range']}")

    found_hero = any("Ordinary World" in a['name'] for a in acts)
    if found_hero:
        print("✅ Hero's Journey mapping successful.")
    else:
        print("❌ FAILED: Hero's Journey map not found or empty.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_narrative_intelligence()
        test_structural_toggles()
        print("\nAll Stage 3 Verifications Passed!")
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)
