#!/usr/bin/env python3
"""
Product Readiness Checker (v13.1 Phase 8)

Measures:
    1. Cold start model load time
    2. Cache hit ratio (second call speedup)
    3. Memory per run (tracemalloc)
    4. Scenes/second throughput
    5. Tokens/second throughput
    6. Model calls per scene estimate

Usage:
    PYTHONPATH=. python3 tests/product_readiness.py
"""

import sys
import os
import time
import tracemalloc
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPORT_PATH = os.path.join(os.path.dirname(__file__), 'readiness_report.json')


def measure_cold_start():
    """Measure time to first model load."""
    print("\n[1/6] Cold Start Model Load Time")
    print("-" * 40)

    from scriptpulse.utils.model_manager import ModelManager

    # Force fresh singleton
    ModelManager._instance = None
    mgr = ModelManager()

    t0 = time.time()
    pipeline = mgr.get_pipeline('zero-shot-classification', 'valhalla/distilbart-mnli-12-3')
    cold_pipeline_ms = round((time.time() - t0) * 1000)
    print(f"  Pipeline cold load: {cold_pipeline_ms}ms")

    t0 = time.time()
    sbert = mgr.get_sentence_transformer('sentence-transformers/all-MiniLM-L6-v2')
    cold_sbert_ms = round((time.time() - t0) * 1000)
    print(f"  SBERT cold load:    {cold_sbert_ms}ms")

    return {
        'cold_pipeline_ms': cold_pipeline_ms,
        'cold_sbert_ms': cold_sbert_ms,
        'total_cold_ms': cold_pipeline_ms + cold_sbert_ms
    }


def measure_cache_hit():
    """Measure cache hit ratio (second call should be near-instant)."""
    print("\n[2/6] Cache Hit Ratio")
    print("-" * 40)

    from scriptpulse.utils.model_manager import ModelManager
    mgr = ModelManager()

    # Warm call (should already be in memory)
    t0 = time.time()
    mgr.get_pipeline('zero-shot-classification', 'valhalla/distilbart-mnli-12-3')
    warm_pipeline_ms = round((time.time() - t0) * 1000)

    t0 = time.time()
    mgr.get_sentence_transformer('sentence-transformers/all-MiniLM-L6-v2')
    warm_sbert_ms = round((time.time() - t0) * 1000)

    print(f"  Pipeline warm load: {warm_pipeline_ms}ms")
    print(f"  SBERT warm load:    {warm_sbert_ms}ms")

    return {
        'warm_pipeline_ms': warm_pipeline_ms,
        'warm_sbert_ms': warm_sbert_ms,
    }


def measure_memory_per_run():
    """Measure peak memory per pipeline run using tracemalloc."""
    print("\n[3/6] Memory Per Run")
    print("-" * 40)

    from scriptpulse import runner

    test_script = """INT. OFFICE - DAY

The room is quiet. ALEX sits at the desk staring at paperwork.

ALEX
(tired)
Another long day.

MARIA
You should go home.

ALEX
Not until this is done."""

    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    runner.run_pipeline(test_script, experimental_mode=True, moonshot_mode=True)

    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    total_delta_mb = sum(s.size_diff for s in stats) / (1024 * 1024)
    peak_mb = sum(s.size for s in snapshot_after.statistics('lineno')) / (1024 * 1024)

    print(f"  Delta memory:  {total_delta_mb:.1f} MB")
    print(f"  Peak snapshot: {peak_mb:.1f} MB")

    return {
        'delta_mb': round(total_delta_mb, 1),
        'peak_snapshot_mb': round(peak_mb, 1),
    }


def measure_throughput():
    """Measure scenes/second and tokens/second."""
    print("\n[4/6] Throughput (Scenes/s, Tokens/s)")
    print("-" * 40)

    from scriptpulse import runner

    # Generate a 10-scene script
    scenes = []
    for i in range(10):
        scenes.append(f"""INT. ROOM {i+1} - DAY

CHARACTER_{i}
This is scene {i+1} dialogue. The plot thickens.

ACTION_{i}
Indeed it does. We must proceed carefully.""")
    
    test_script = "\n\n".join(scenes)
    token_count = len(test_script.split())

    t0 = time.time()
    result = runner.run_pipeline(test_script, experimental_mode=True, moonshot_mode=True)
    elapsed = time.time() - t0

    total_scenes = result.get('total_scenes', 10)
    scenes_per_s = round(total_scenes / elapsed, 2)
    tokens_per_s = round(token_count / elapsed, 1)

    print(f"  Scenes:       {total_scenes}")
    print(f"  Tokens:       {token_count}")
    print(f"  Time:         {elapsed:.1f}s")
    print(f"  Scenes/s:     {scenes_per_s}")
    print(f"  Tokens/s:     {tokens_per_s}")

    # Agent timings
    timings = result.get('meta', {}).get('agent_timings', {})
    if timings:
        print(f"\n  Per-Agent Timing Table:")
        for agent, ms in sorted(timings.items()):
            print(f"    {agent:25s} {ms:>6d} ms")

    return {
        'total_scenes': total_scenes,
        'token_count': token_count,
        'elapsed_s': round(elapsed, 1),
        'scenes_per_s': scenes_per_s,
        'tokens_per_s': tokens_per_s,
        'agent_timings': timings,
    }


def estimate_model_calls():
    """Estimate model calls per scene."""
    print("\n[5/6] Model Calls Per Scene (Estimate)")
    print("-" * 40)

    # Based on pipeline architecture:
    calls = {
        'bert_parser': '1 per line (zero-shot classification)',
        'embeddings (SBERT)': '1 per scene',
        'semantic (SBERT)': '1 per scene',
        'stanislavski': '1 per scene (if enabled)',
        'valence': '1 per scene (or strided)',
    }

    total_per_scene = 4  # parser is per-line, not per-scene
    print(f"  Estimated model calls per scene: ~{total_per_scene}")
    for agent, desc in calls.items():
        print(f"    {agent:30s} {desc}")

    return {'estimated_calls_per_scene': total_per_scene, 'breakdown': calls}


def measure_concurrent():
    """Simple concurrent run test (sequential, since Python GIL)."""
    print("\n[6/6] Sequential Multi-Run Stability")
    print("-" * 40)

    from scriptpulse import runner

    test_script = """INT. ROOM - DAY
ALEX
Hello world."""

    times = []
    for i in range(3):
        t0 = time.time()
        runner.run_pipeline(test_script)
        elapsed = time.time() - t0
        times.append(round(elapsed, 2))
        print(f"  Run {i+1}: {elapsed:.2f}s")

    variance = max(times) - min(times)
    print(f"  Variance: {variance:.2f}s")

    return {
        'run_times': times,
        'variance_s': round(variance, 2),
        'stable': variance < 5.0,
    }


def main():
    print("=" * 60)
    print("PRODUCT READINESS CHECK — v13.1")
    print("=" * 60)

    report = {}

    report['cold_start'] = measure_cold_start()
    report['cache_hit'] = measure_cache_hit()
    report['memory'] = measure_memory_per_run()
    report['throughput'] = measure_throughput()
    report['model_calls'] = estimate_model_calls()
    report['stability'] = measure_concurrent()

    # Summary
    print("\n" + "=" * 60)
    print("READINESS SUMMARY")
    print("=" * 60)
    print(f"  Cold start:     {report['cold_start']['total_cold_ms']}ms")
    print(f"  Cache warmup:   {report['cache_hit']['warm_pipeline_ms'] + report['cache_hit']['warm_sbert_ms']}ms")
    print(f"  Memory delta:   {report['memory']['delta_mb']}MB")
    print(f"  Throughput:     {report['throughput']['scenes_per_s']} scenes/s, {report['throughput']['tokens_per_s']} tokens/s")
    print(f"  Stability:      {'✅ STABLE' if report['stability']['stable'] else '❌ UNSTABLE'}")

    with open(REPORT_PATH, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Readiness report: {REPORT_PATH}")


if __name__ == '__main__':
    main()
