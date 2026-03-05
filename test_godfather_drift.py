import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scriptpulse.pipeline import runner
from scriptpulse.reporters import llm_translator
from dotenv import load_dotenv
load_dotenv()

def remove_volatile_keys(d):
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            if k in ['wall_time_s', 'timestamp', 'agent_timings', 'runtime_ms']:
                continue
            new_d[k] = remove_volatile_keys(v)
        return new_d
    elif isinstance(d, list):
        return [remove_volatile_keys(i) for i in d]
    else:
        return d

def test_godfather_drift():
    filepath = "Godfather, The.txt"
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    os.environ['SCRIPTPULSE_HEURISTICS_ONLY'] = '1'

    print("--- RUN 1 ---")
    start = time.time()
    report1 = runner.run_pipeline(text, experimental_mode=True, moonshot_mode=False)
    print(f"Run 1 took {time.time() - start:.2f} seconds")

    print("--- RUN 2 ---")
    start = time.time()
    report2 = runner.run_pipeline(text, experimental_mode=True, moonshot_mode=False)
    print(f"Run 2 took {time.time() - start:.2f} seconds")

    clean_report1 = remove_volatile_keys(report1)
    clean_report2 = remove_volatile_keys(report2)

    r1_json = json.dumps(clean_report1, sort_keys=True)
    r2_json = json.dumps(clean_report2, sort_keys=True)

    if r1_json == r2_json:
        print("\n✅ ZERO DRIFT: Outputs are exactly identical.")
    else:
        print("\n❌ DRIFT DETECTED: Outputs are different.")
        # Find differences
        for key in clean_report1:
            if clean_report1.get(key) != clean_report2.get(key):
                print(f"Difference in key: {key}")
                if key == "meta":
                    for mk in clean_report1["meta"]:
                        if clean_report1["meta"].get(mk) != clean_report2['meta'].get(mk):
                            print(f"  meta.{mk} different")

    print("\n--- AI OUTPUT (WRITER INTELLIGENCE) ---")
    writer_intel = report1.get('writer_intelligence', {})
    if writer_intel:
        print("Narrative Diagnosis:")
        for diag in writer_intel.get('narrative_diagnosis', []):
            print(f" - {diag}")
        print("\nRewrite Priorities:")
        for prio in writer_intel.get('rewrite_priorities', []):
            print(f" - {prio.get('action', prio)} (Leverage: {prio.get('leverage', 'N/A')})")
    else:
        print("No writer_intelligence found in report.")

    print("\n--- AI GENERATED SUMMARY ---")
    summary, error = llm_translator.generate_ai_summary(report1)
    if summary:
        print(summary)
    else:
        print(f"Failed to generate AI summary: {error}")

if __name__ == '__main__':
    test_godfather_drift()
