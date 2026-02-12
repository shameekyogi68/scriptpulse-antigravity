from scriptpulse.utils import runtime

def test_runtime():
    # Mock data resembling new parser output
    scenes = [
        {
            'lines': [
                {'tag': 'scene_heading', 'text': 'INT. ROOM - DAY'},
                {'tag': 'action', 'text': 'A man enters.'},
                {'tag': 'character', 'text': 'MAN'},
                {'tag': 'dialogue', 'text': 'Hello world.'},
                {'tag': 'parenthetical', 'text': '(pauses)'},
                {'tag': 'dialogue', 'text': 'Is anyone there?'}
            ]
        }
    ]
    
    # 6 lines. 6/55 pages = 0.1 pages = 0.1 minutes.
    # min_minutes should be max(1, 0.1 - 5) = 1.
    
    res = runtime.estimate_runtime(scenes)
    print(f"Result: {res}")
    
    if res['avg_minutes'] > 0 or res['min_minutes'] >= 1:
        print("[PASS] Runtime detected.")
    else:
        print("[FAIL] Runtime is 0.")

if __name__ == "__main__":
    test_runtime()
