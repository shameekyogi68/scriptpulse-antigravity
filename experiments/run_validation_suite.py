
import json
import logging
from scriptpulse.runner import run_pipeline

# Configure logging
logging.basicConfig(level=logging.ERROR)

def run_test_case(title, script_type, content, intent=None, expected=None):
    print(f"\n{'='*60}")
    print(f"RUNNING TEST CASE: {title} ({script_type})")
    print(f"{'='*60}")
    
    try:
        result = run_pipeline(content, writer_intent=intent, lens='viewer', genre='drama', experimental_mode=True)
        
        # Calculate stats for display
        total_words = len(content.split())
        
        print("\nINPUT BLOCK")
        print(f"Script title: {title}")
        print(f"Script type: {script_type}")
        print(f"Scene text (first 100 chars): {content[:100]}...")
        print(f"Scene length in words: {total_words}")
        print(f"Notes on intent: {intent}")
        
        if expected:
            print("\nEXPECTED OUTPUT BLOCK")
            for k, v in expected.items():
                print(f"{k}: {v}")
                
        print("\nSCRIPT PULSE RUN BLOCK")
        # Extract key metrics
        trace = result.get('temporal_trace', [])
        meta = result.get('meta', {})
        
        if trace:
            avg_effort = sum(t['instantaneous_effort'] for t in trace) / len(trace)
            avg_attention = sum(t['attentional_signal'] for t in trace) / len(trace)
            avg_recovery = sum(t['recovery_credit'] for t in trace) / len(trace)
            peak_effort = max(t['instantaneous_effort'] for t in trace)
        else:
            avg_effort = 0
            avg_attention = 0
            avg_recovery = 0
            peak_effort = 0
            
        print(json.dumps({
            'avg_effort': round(avg_effort, 3),
            'avg_attention': round(avg_attention, 3),
            'avg_recovery': round(avg_recovery, 3),
            'peak_effort': round(peak_effort, 3),
            'surfaced_patterns': [p['pattern_type'] for p in result.get('surfaced_patterns', [])],
            'silence_check': result.get('output', {}).get('silence_explanation', 'N/A')
        }, indent=2))
        
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

# =============================================================================
# TEST CASES
# =============================================================================

# 1. Feature Film
feature_script = """
INT. FACTORY - DAY

Sparks fly. Metal SCREECHES.

JOHN (40s) wipes grease from his face.

JOHN
(grunting)
Just one more turn.

He wrenches the lever. A hiss of steam.

EXT. ALLEY - CONTINUOUS

John bursts out the door. Running.
"""
print("Running Feature Film...")
run_test_case(
    "The Escape", "Feature Film", feature_script, 
    intent=[{"scene_range": [0, 1], "intent": "should feel tense"}],
    expected={
        "Attention risk level": "Low (High action)",
        "Mental effort level": "Medium (Visual density)",
        "Fatigue risk level": "Low",
        "Scene blending risk": "Low",
        "Rhythm stability": "High",
        "Novelty saturation level": "Medium",
        "Recovery window presence": "Low",
        "Flag decision": "No Flag"
    }
)

# 2. Short Film (Visual)
short_script = """
EXT. DESERT - DAY

Silence. Wind blows sand across a skull.

A LIZARD scampers over the bone.

FADE TO:

INT. TENT - DAY

A hand reaches for a canteen. Dry. Empty.
"""
print("Running Short Film...")
run_test_case(
    "Thirst", "Short Film", short_script,
    expected={
        "Attention risk level": "Medium (Slow pace)",
        "Mental effort level": "Low (Simple visual)",
        "Flag decision": "No Flag"
    }
)

# 3. Web Series (Dialogue Heavy)
web_script = """
INT. COFFEE SHOP - DAY

JESS and MARK sit at a table.

JESS
So you're saying it's over? Just like that? After three years of sharing a Netflix account?

MARK
It's not about the Netflix, Jess. It's about the Hulu. You never watch Hulu.

JESS
I watch The Bear!

MARK
You watched one episode! One!
"""
print("Running Web Series...")
run_test_case(
    "Stream Wars", "Web Series", web_script,
    expected={
        "Attention risk level": "Low (High dialogue conflict)",
        "Mental effort level": "Low (Conversational)",
        "Flag decision": "No Flag"
    }
)

# 4. TV Drama Scene
tv_script = """
INT. HOSPITAL ROOM - NIGHT

MONITOR BEEPS steadily.

DOCTOR EVANS looks at the chart. Looks at SARAH.

DOCTOR EVANS
I'm afraid the results aren't what we hoped for.

Sarah stares at the wall.

SARAH
How long?

DOCTOR EVANS
Months. Maybe less.
"""
print("Running TV Drama...")
run_test_case(
    "The Diagnosis", "TV Drama", tv_script,
    expected={
        "Attention risk level": "Low (High stakes)",
        "Mental effort level": "Medium (Emotional load)",
        "Flag decision": "No Flag"
    }
)

# 5. Stage Play Scene (Monologue)
play_script = """
INT. STAGE - NIGHT

HAMLET stands alone. Center stage. Spotlight.

HAMLET
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd.
"""
print("Running Stage Play...")
run_test_case(
    "Hamlet", "Stage Play", play_script,
    expected={
        "Attention risk level": "Medium (Dense language)",
        "Mental effort level": "High (Archaic syntax)",
        "Flag decision": "Possible Pattern (Sustained Demand)"
    }
)

# 6. Audio Drama
audio_script = """
INT. SPACESHIP COCKPIT - SOUND ONLY

SFX: LOW HUM OF ENGINE. SUDDEN ALARM.

COMMANDER (V.O.)
Brace for impact!

SFX: VIOLENT CRASH. BREAKING GLASS. HISSING AIR.

PILOT (V.O.)
(coughing)
Status report! Anyone copy?
"""
print("Running Audio Drama...")
run_test_case(
    "Void Drift", "Audio Drama", audio_script,
    expected={
        "Attention risk level": "Low (High auditory stimulus)",
        "Mental effort level": "Medium (Imagination required)",
        "Flag decision": "No Flag"
    }
)

# 7. Documentary Narration
doc_script = """
EXT. SAVANNAH - DAY

A LION stalks through the grass.

NARRATOR (V.O.)
Here, on the endless plains of the Serengeti, the circle of life turns with brutal efficiency. The lioness has not eaten in three days. Her cubs are waiting.

The lioness crouches. Muscles tense.
"""
print("Running Documentary...")
run_test_case(
    "Survival", "Documentary", doc_script,
    expected={
        "Attention risk level": "Low (Engaging visuals + voice)",
        "Mental effort level": "Low (Clear exposition)",
        "Flag decision": "No Flag"
    }
)

# 8. Ad Film
ad_script = """
INT. KITCHEN - DAY

Fast cuts.

Chopping vegetables. Sizzling pan. Steam rising.

A FAMILY laughs. Eats.

NARRATOR (V.O.)
Taste the joy. Every single day.

LOGO: SPICY DELIGHT.
"""
print("Running Ad Film...")
run_test_case(
    "Spicy Delight", "Ad Film", ad_script,
    expected={
        "Attention risk level": "Low (Very fast)",
        "Mental effort level": "Low",
        "Flag decision": "Possible Pattern (Short Duration)"
    }
)

# 9. YouTube Storytelling
yt_script = """
INT. BEDROOM - DAY

JAKE looks at the camera.

JAKE
Okay guys, story time. So I was at the grocery store, right? And this lady—let's call her Karen—she comes up to me in the produce aisle.

CUT TO:

EXT. GROCERY STORE - FLASHBACK

Jake holding a melon.
"""
print("Running YouTube...")
run_test_case(
    "Storytime", "YouTube", yt_script,
    expected={
        "Attention risk level": "Low (Direct address)",
        "Mental effort level": "Low",
        "Flag decision": "No Flag"
    }
)

# 10. Nonlinear / Experimental
exp_script = """
INT. MIND PALACE - DREAM

A clock that melts. Time flows backwards.

WOMAN
The red door is the blue key.

The floor becomes the ceiling.

INT. BASEMENT - REALITY?

Darkness.
"""
print("Running Experimental...")
run_test_case(
    "Inception_Lite", "Experimental", exp_script,
    expected={
        "Attention risk level": "High (Confusion)",
        "Mental effort level": "High (Abstract)",
        "Flag decision": "Pattern (Degenerative Fatigue/Collapse)"
    }
)

# CONSISTENCY CHECK
print("\nRUNNING CONSISTENCY CHECK...")
base_scene = """
INT. ROOM - DAY
The cat sits on the mat.
"""
var_scene = """
INT. ROOM - DAY
The dog sits on the rug.
"""

print("Running Base...")
res1 = run_test_case("Base", "Test", base_scene)
print("Running Variant (Structure Preserved)...")
res2 = run_test_case("Variant", "Test", var_scene)

if res1 and res2 and res1.get('temporal_trace') and res2.get('temporal_trace'):
    t1 = res1['temporal_trace'][0]
    t2 = res2['temporal_trace'][0]
    
    diff = abs(t1['instantaneous_effort'] - t2['instantaneous_effort'])
    print(f"\nEffort Difference: {diff}")
    if diff < 0.15:
        print("CONSISTENCY PASS")
    else:
        print("CONSISTENCY FAIL")
else:
     print("CONSISTENCY CHECK SKIPPED (No Trace Data)")

