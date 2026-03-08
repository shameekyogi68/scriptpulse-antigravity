import json
from scriptpulse.pipeline.runner import run_pipeline

def run_test(name, script, genre):
    print(f"\n--- Running Test: {name} ({genre}) ---")
    report = run_pipeline(script, genre=genre)
    trace = report['temporal_trace']
    
    if not trace:
        print("❌ No trace generated.")
        return
        
    s0 = trace[0]
    print(f"Attentional Signal:  {s0['attentional_signal']}")
    print(f"Action Density:      {s0['action_density']}")
    print(f"Conflict Score:      {s0['conflict']}")
    print(f"Cognitive Resonance: {s0.get('cognitive_resonance', 'N/A')}")
    
    print("Voice Fingerprints:")
    for char, data in report['voice_fingerprints'].items():
        print(f"  {char}: Agency={data['agency']}, Sentiment={data['sentiment']}")
        
    print("Narrative Diagnoses:")
    for d in report['narrative_diagnosis']:
        print(f"  {d}")

if __name__ == "__main__":
    action_script = """
INT. ABANDONED WAREHOUSE - NIGHT

JACK (40s, grizzled) kicks open the door. He raises his weapon.

JACK
Drop it! Now!

Five MERCENARIES turn and fire. 

Bullets shred the concrete. Jack dives behind a rusted car, returning fire.

JACK
You want some?!

He throws a grenade.

BOOM! The warehouse shakes. The mercenaries are thrown back.
"""

    drama_script = """
INT. COFFEE SHOP - DAY

MARY and JOHN sit at a small table. They sip their coffee slowly.

MARY
The weather is quite nice today.

JOHN
Yes, it is. I think it might rain later though.

MARY
Perhaps. Did you read the newspaper?

JOHN
I did. Nothing interesting. Just the usual politics.

MARY
Same old, same old.

JOHN
Indeed. I should probably get going soon.

MARY
Okay. See you tomorrow.
"""

    overcrowded_script = """
INT. BRIEFING ROOM - DAY

GENERAL SMITH stands at the front. CAPTAIN JONES, LIEUTENANT DAN, SERGEANT PEPPER, CORPORAL PUNISHMENT, and MAJOR TOM sit around the table.

GENERAL SMITH
Listen up!

CAPTAIN JONES
We're ready.

LIEUTENANT DAN
I brought the maps.

SERGEANT PEPPER
The band is here.

CORPORAL PUNISHMENT
Let's do this.

MAJOR TOM
Ground control, receiving.

ADMIRAL ACKBAR bursts in!

ADMIRAL ACKBAR
It's a trap!
"""

    try:
        run_test("High Action", action_script, "action")
        run_test("Flat Drama", drama_script, "drama")
        run_test("Overcrowded Room", overcrowded_script, "drama")
    except Exception as e:
        import traceback
        traceback.print_exc()

