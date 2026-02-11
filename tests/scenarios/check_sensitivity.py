import json
import sys

def check():
    with open('tests/scenarios/sensitivity_output.json', 'r') as f:
        content = f.read()
        json_start = content.find('{')
        if json_start == -1:
            print("No JSON found")
            return
        data = json.loads(content[json_start:])
        
    trace = data['temporal_trace']
    print(f"Total Scenes: {len(trace)}")
    for s in trace:
        print(f"Scene {s['scene_index']}: Effort={s['attentional_signal']:.3f}")
        
    # Check
    low_scenes = [trace[0]['attentional_signal'], trace[1]['attentional_signal'], trace[4]['attentional_signal']]
    high_scenes = [trace[2]['attentional_signal'], trace[3]['attentional_signal']]
    
    avg_low = sum(low_scenes)/len(low_scenes)
    avg_high = sum(high_scenes)/len(high_scenes)
    
    print(f"Avg Low (0,1,4): {avg_low:.3f}")
    print(f"Avg High (2,3):   {avg_high:.3f}")
    
    if avg_high > avg_low + 0.1:
        print("[PASS] ML detected significantly higher tension in danger scenes.")
    else:
        print("[FAIL] ML did not effectively distinguish danger scenes.")

if __name__ == "__main__":
    check()
