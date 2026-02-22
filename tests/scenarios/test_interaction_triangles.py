import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scriptpulse.runner import run_pipeline

def test_interaction_triangles():
    print("Running Interaction Triangles Verification...")
    
    # Scene 1: A and B argue (High Social Conflict)
    scene1 = "SCENE 1\nINT. OFFICE - DAY\nALICE\nWhere is the file?\nBOB\nI don't know.\nALICE\nYou lost it!\nBOB\nNo, you did!"
    
    # Scene 2: B and C argue (High Social Conflict)
    scene2 = "SCENE 2\nINT. KITCHEN - NIGHT\nBOB\nAlice is crazy.\nCHARLIE\nShe's not crazy, Bob. You're incompetent.\nBOB\nExcuse me?\nCHARLIE\nYou heard me."
    
    # Scene 3: C and A argue (High Social Conflict) => completing the triangle
    scene3 = "SCENE 3\nEXT. STREET - DAY\nCHARLIE\nBob says you're crazy.\nALICE\nBob is an idiot. And what are you, his lawyer?\nCHARLIE\nI'm just saying.\nALICE\nDon't 'just say' anything to me."
    
    # Scene 4: D is isolated
    scene4 = "SCENE 4\nINT. CAVE - NIGHT\nDAVE\n(to himself)\nIt's very dark in here. Very lonely."

    full_script = f"{scene1}\n\n{scene2}\n\n{scene3}\n\n{scene4}"
    
    report = run_pipeline(full_script)
    networks = report.get('interaction_networks', {})
    
    edges = networks.get('edges', [])
    triangles = networks.get('triangles', [])
    
    print(f"DEBUG: Found {len(edges)} edges and {len(triangles)} triangles.")
    for e in edges:
        print(f" - Edge: {e['source']} <-> {e['target']} (Weight: {e['weight']})")
        
    for t in triangles:
        print(f" - Triangle: {t}")
        
    # Check if triangle Alice-Bob-Charlie is detected
    found_triangle = False
    for t in triangles:
        if set(t) == {'ALICE', 'BOB', 'CHARLIE'}:
            found_triangle = True
            break
            
    if found_triangle:
        print("✅ Conflict Triangle detected correctly.")
    else:
        print("❌ FAILED: Did not detect ALICE-BOB-CHARLIE triangle.")
        # Ensure that weights are above threshold
        sys.exit(1)
        
    # Check Dave isolation
    dave_connected = any(e['source'] == 'DAVE' or e['target'] == 'DAVE' for e in edges)
    if not dave_connected:
         print("✅ Isolated character (DAVE) correctly ignored in tension network.")
    else:
         print("❌ FAILED: DAVE should not have any edges.")
         sys.exit(1)

if __name__ == "__main__":
    try:
        test_interaction_triangles()
        print("\nAll Stage 5 Verifications Passed!")
    except Exception as e:
        print(f"\nVerification Crashed: {e}")
        sys.exit(1)
