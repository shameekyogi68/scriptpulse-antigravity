import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scriptpulse.pipeline import runner

def generate_script(scenes=1):
    text = ""
    for i in range(scenes):
        if i > 0:
            text += "\n\n"
        text += f"INT. ROOM {i+1} - DAY\n\n"
        text += "This is action that happens in the room. Someone walks in.\n\n"
        text += "CHARACTER A\n"
        text += "This is a line of dialogue that is being spoken.\n\n"
        text += "CHARACTER B\n"
        text += "This is a response to the dialogue.\n"
    return text

print("--- Testing Phase 2 120 Scenes ---")
s120 = generate_script(120)
res120 = runner.run_pipeline(s120, cpu_safe_mode=True, experimental_mode=False)
if 'scenes' in res120:
    print(f"Got {len(res120['scenes'])} scenes for 120.")
else:
    print(f"No scenes in 120. Keys: {res120.keys()}")

print("--- Testing Phase 3 Exact Code ---")
acc_script = "1. INT. ROOM - DAY\nVery short action.\n\n2. EXT. STREET - NIGHT\nA medium length scene. Bob runs outside desperately looking for the item.\nBOB\nWhere is it?\n\n3. INT. CAR - DAY\nEnd."
res_acc = runner.run_pipeline(acc_script, cpu_safe_mode=True)
if 'scenes' in res_acc:
    print(f"Got {len(res_acc['scenes'])} scenes in Phase 3.")
else:
    print(f"No scenes in Phase 3. Keys: {res_acc.keys()}")
