#!/usr/bin/env python3
"""Quick test to verify escalation works on 17-scene script"""

from scriptpulse import runner
import json

# Your 17-scene script
script = """INT. ROOM – NIGHT

Dark.

A PHONE vibrates on a table.
Stops.
Vibrates again.

A MAN (30) sits nearby, staring.


INT. ROOM – NIGHT

Same room.

The phone vibrates again.
The man checks it.
No message.

He rubs his face.


INT. ROOM – NIGHT

Same angle.

The phone vibrates again.

MAN
Why now?


INT. ROOM – NIGHT

The phone vibrates again.

MAN
(whispering)
It's not supposed to do this.


INT. ROOM – NIGHT

The man stands.
Sits.
Stands again.

The phone vibrates.


INT. ROOM – NIGHT

FLASHES of MEMORY:
– A ROAD
– A SCREAM
– A NUMBER: 17
– A CLOCK TICKING BACKWARD


INT. ROOM – NIGHT

The man breathes fast.

MAN
It already happened.
Or it hasn't.
I can't remember.


INT. ROOM – NIGHT

The phone vibrates.

ON SCREEN: 11:11


INT. ROOM – NIGHT

The same moment again.

ON SCREEN: 11:11


INT. ROOM – NIGHT

The same moment again.

ON SCREEN: 11:11


INT. ROOM – NIGHT

The man laughs suddenly.

MAN
I fixed it.
I think.


INT. ROOM – NIGHT

FLASHBACK:
The man runs.
The road again.
The scream again.


INT. ROOM – NIGHT

BACK TO PRESENT.

The phone vibrates.

MAN
Don't do this.


INT. ROOM – NIGHT

The phone stops vibrating.

Silence.


INT. ROOM – NIGHT

The phone vibrates again.

LOUDER.


INT. ROOM – NIGHT

The man stares at it.

MAN
I already chose.


INT. ROOM – NIGHT

CUT TO BLACK.

A BUZZING SOUND continues.

FADE OUT.
"""

print("="*60)
print("Testing 17-Scene Repetitive Script")
print("="*60)

result = runner.run_pipeline(script)

print(f"\nTotal signals detected: {result['total_surfaced']}")
print("\n" + "="*60)
print("SIGNALS:")
print("="*60)

for i, reflection in enumerate(result['reflections'], 1):
    print(f"\n{i}. Scenes {reflection['scene_range'][0]}-{reflection['scene_range'][1]}")
    print(f"   Confidence: {reflection['confidence'].upper()}")
    print(f"   {reflection['reflection'][:80]}...")

print("\n" + "="*60)
print("\nFull JSON output:")
print("="*60)
print(json.dumps(result, indent=2))
