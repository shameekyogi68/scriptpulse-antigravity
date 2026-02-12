"""
Field Telemetry Logger (v13.1 Block 7)

Logs per-run telemetry to a JSONL file for operational monitoring.
Does NOT log raw script text — hashes only.

Logged per run:
    - scene_count_bucket
    - runtime_ms
    - cpu_safe_mode
    - model_path (from model_manager)
    - version_tag
    - validation_errors_count
    - content_fingerprint (hash)
    - wall_time_s
    - peak_memory_mb
    - resource_flag
    - timestamp

Usage:
    from scriptpulse.telemetry import log_run
    log_run(pipeline_result)
"""

import json
import os
import hashlib
from datetime import datetime


TELEMETRY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.telemetry')
TELEMETRY_FILE = os.path.join(TELEMETRY_DIR, 'runs.jsonl')


def _scene_bucket(n):
    """Bucket scene counts for telemetry."""
    if n <= 5: return '1-5'
    if n <= 20: return '6-20'
    if n <= 50: return '21-50'
    if n <= 100: return '51-100'
    return '100+'


def log_run(result):
    """
    Log a pipeline result to telemetry. Hash-only, no raw text.
    
    Args:
        result: Full pipeline output dict from runner.run_pipeline()
    """
    os.makedirs(TELEMETRY_DIR, exist_ok=True)
    
    meta = result.get('meta', {})
    timings = meta.get('agent_timings', {})
    debug = result.get('debug_export', {})
    
    total_runtime_ms = sum(timings.values()) if timings else 0
    
    # Count validation errors
    validation_errors = debug.get('validation_errors', [])
    error_count = len(validation_errors) if isinstance(validation_errors, list) else 0
    
    # Get model info if available
    try:
        from .utils.model_manager import manager
        loaded = manager.get_loaded_models()
        model_paths = {k: v.get('name', '') for k, v in loaded.items()}
    except Exception:
        model_paths = {}
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'scene_count_bucket': _scene_bucket(result.get('total_scenes', 0)),
        'total_scenes': result.get('total_scenes', 0),
        'runtime_ms': total_runtime_ms,
        'wall_time_s': meta.get('wall_time_s', 0),
        'peak_memory_mb': meta.get('peak_memory_mb', 0),
        'cpu_safe_mode': debug.get('cpu_safe_mode', False),
        'model_paths': model_paths,
        'version_tag': meta.get('version', ''),
        'validation_errors_count': error_count,
        'content_fingerprint': meta.get('content_fingerprint', ''),
        'resource_flag': meta.get('resource_flag'),
        'lens': meta.get('lens', 'viewer'),
        'run_id': meta.get('run_id', ''),
    }
    
    with open(TELEMETRY_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return entry


def read_telemetry(last_n=50):
    """Read last N telemetry entries."""
    if not os.path.exists(TELEMETRY_FILE):
        return []
    
    with open(TELEMETRY_FILE, 'r') as f:
        lines = f.readlines()
    
    entries = []
    for line in lines[-last_n:]:
        try:
            entries.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue
    
    return entries


def summary():
    """Print telemetry summary."""
    entries = read_telemetry()
    
    if not entries:
        print("No telemetry data.")
        return
    
    print(f"Telemetry: {len(entries)} runs")
    
    # Bucket distribution
    buckets = {}
    for e in entries:
        b = e.get('scene_count_bucket', '?')
        buckets[b] = buckets.get(b, 0) + 1
    
    print(f"  Scene buckets: {buckets}")
    
    # CPU safe mode usage
    cpu_safe = sum(1 for e in entries if e.get('cpu_safe_mode'))
    print(f"  CPU safe mode: {cpu_safe}/{len(entries)} runs")
    
    # Resource flags
    flagged = sum(1 for e in entries if e.get('resource_flag'))
    print(f"  Resource flags: {flagged}/{len(entries)} runs")
    
    # Validation errors
    total_errors = sum(e.get('validation_errors_count', 0) for e in entries)
    print(f"  Validation errors: {total_errors} total")
