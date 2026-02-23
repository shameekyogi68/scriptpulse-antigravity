import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scriptpulse.pipeline import runner

text = "INT. ROOM 1 - DAY\n\nThis is action that happens in the room. Someone walks in.\n\nCHARACTER A\nThis is a line of dialogue that is being spoken.\n\nCHARACTER B\nThis is a response to the dialogue.\n"
scenes = runner.parse_structure(text)
print(f"Got {len(scenes)} scenes")
for s in scenes:
    print(s)
