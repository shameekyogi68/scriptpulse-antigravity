import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def stage8_validation():
    print("--- STAGE 8: MULTI-SCRIPT STABILITY ---")
    
    # Define diverse scripts
    scripts = [
        ("Standard Hollywood", "INT. BAR - NIGHT\nBARTENDER\nDrink?\nJOHN\nWater."),
        ("Indie Implicit", "OFFICE - DAY\nJohn works.\nMARY (O.S.)\nCoffee?"),
        ("Dialogue Only", "JOHN\nI think we should go.\nMARY\nWhere?\nJOHN\nEast."),
        ("Mixed INT/EXT", "I/E. TAXI - MOVING - RAIN\nThe driver stares."),
        ("No Headings", "A vast desert. Heat shimmers.\nA LONELY RIDER appears."),
        ("Action Heavy", "EXT. CLIFF - DAY\nJOHN CLIMBS. His fingers SLIP. He GRABS a root. He SCREAMS."),
        ("Minimalist", "A.\nB."),
        ("Final Draft Style", '<?xml version="1.0" encoding="UTF-8"?><FinalDraft DocumentType="Script" Version="12"><Content><Paragraph Type="Scene Heading"><Text>INT. HOUSE - DAY</Text></Paragraph><Paragraph Type="Character"><Text>JOHN</Text></Paragraph><Paragraph Type="Dialogue"><Text>Hello.</Text></Paragraph></Content></FinalDraft>'),
    ]
    
    # Ensure heuristics for stability test
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    
    success_count = 0
    from scriptpulse.agents.structure_agent import ImporterAgent
    importer = ImporterAgent()
    
    for name, text in scripts:
        try:
            print(f"Processing: {name}...")
            if text.startswith("<?xml"):
                importer.run(text)
            else:
                runner.run_pipeline(text)
            success_count += 1
            print(f"✅ {name} Success.")
        except Exception as e:
            print(f"❌ {name} Failed: {e}")
            import traceback
            traceback.print_exc()
            
    if success_count == len(scripts):
        print("\n🏆 STAGE 8 PASSED: All diverse inputs processed successfully.")
    else:
        print(f"\n⚠️ STAGE 8 FAILED: {len(scripts)-success_count} failures.")
        sys.exit(1)

if __name__ == "__main__":
    stage8_validation()
