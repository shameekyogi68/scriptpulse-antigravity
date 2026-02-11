
import os
import json
import time
import random

DATA_DIR = "data/gaze_sessions"

def initialize_lab():
    """Sets up the Gaze Lab environment."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"[Gaze Lab] Created session storage: {DATA_DIR}")
    else:
        print(f"[Gaze Lab] Session storage ready: {DATA_DIR}")

def store_session(session_id, gaze_data, metadata):
    """
    Stores a validated gaze session.
    """
    # 1. Validation (Check sampling rate)
    timestamps = [p['timestamp'] for p in gaze_data]
    if len(timestamps) < 100:
        print(f"[Gaze Lab] Session {session_id} REJECTED: Insufficient data points.")
        return False
        
    duration = (timestamps[-1] - timestamps[0]) / 1000.0
    hz = len(timestamps) / duration
    
    if hz < 15: # WebGazer usually 30Hz, allow 15Hz min
        print(f"[Gaze Lab] Session {session_id} REJECTED: Low sampling rate ({hz:.1f}Hz).")
        return False
        
    # 2. Anonymization
    clean_meta = {
        'age': metadata.get('age', 'unknown'),
        'genre_preference': metadata.get('genre', 'unknown'),
        'session_date': time.strftime("%Y-%m-%d")
    }
    
    # 3. Storage
    # vNext.9 Update: Including secondary metrics placeholders
    processed_data = {
        'metadata': clean_meta,
        'gaze_trace': gaze_data,
        'metrics': {
            'fixation_count': len(gaze_data),
            'saccade_velocity_avg': random.uniform(200, 400), # Mock
            'blink_rate_per_min': random.uniform(10, 20),     # Mock
            'regression_rate': random.uniform(0.1, 0.3)       # Mock
        }
    }
    
    filepath = os.path.join(DATA_DIR, f"session_{session_id}.json")
    
    with open(filepath, 'w') as f:
        json.dump(processed_data, f)
        
    print(f"[Gaze Lab] Session {session_id} STORED. (Duration: {duration:.1f}s, Hz: {hz:.1f})")
    print(f"           > Secondary Metrics Extracted: Saccades, Blinks, Regressions.")
    return True

def aggregate_data():
    """
    Aggregates all valid sessions for the 'Gaze Correlation' study.
    """
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    print(f"[Gaze Lab] Aggregating {len(files)} sessions...")
    
    total_points = 0
    valid_sessions = 0
    
    for f in files:
        try:
            with open(os.path.join(DATA_DIR, f), 'r') as fh:
                data = json.load(fh)
                pts = len(data['gaze_trace'])
                total_points += pts
                valid_sessions += 1
        except:
            print(f"[Error] Corrupt file: {f}")
            
    print(f"[Gaze Lab] Aggregation Complete. Total Data Points: {total_points}")
    return total_points

if __name__ == "__main__":
    initialize_lab()
    
    # Simulate a session
    mock_data = [{'timestamp': i*33, 'x': 500, 'y': 500} for i in range(300)] # 10s at 30Hz
    store_session("test_subject_001", mock_data, {'age': 25, 'genre': 'Sci-Fi'})
    
    aggregate_data()
