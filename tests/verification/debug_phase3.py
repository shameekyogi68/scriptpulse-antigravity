import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname('tests/verification/debug_phase3.py'), '../..')))
from scriptpulse.pipeline import runner
res_acc = runner.run_pipeline("1. INT. ROOM - DAY\nVery short action.\n\n2. EXT. STREET - NIGHT\nA medium length scene. Bob runs.\nBOB\nWhere is it?\n\n3. INT. CAR - DAY\nEnd.", cpu_safe_mode=True, experimental_mode=False)
lines = runner.parse_structure("1. INT. ROOM - DAY\nVery short action.\n\n2. EXT. STREET - NIGHT\nA medium length scene. Bob runs.\nBOB\nWhere is it?\n\n3. INT. CAR - DAY\nEnd.")
print(f"parse_structure returned {len(lines)} scenes: {lines}")
if 'error' in res_acc:
    print('Pipeline Error:', res_acc['error'])
else:
    print('Scenes:', res_acc.get('scenes', []))
