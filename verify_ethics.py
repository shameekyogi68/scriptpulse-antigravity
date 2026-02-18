
import sys
import os
sys.path.append(os.getcwd())
from scriptpulse import runner
import json

script = """
INT. BOARDROOM - DAY

CEO
(slamming table)
I decided to fire everyone!

INTERN
(quietly)
I think that's a bad idea.

CEO
I don't care what you think. I choose violence.
"""

print("Running pipeline with Ethics Agent...")
result = runner.run_pipeline(script)

print("\n--- AGENCY ANALYSIS ---")
print(json.dumps(result.get('agency_analysis'), indent=2))

print("\n--- FAIRNESS AUDIT ---")
print(json.dumps(result.get('fairness_audit'), indent=2))
