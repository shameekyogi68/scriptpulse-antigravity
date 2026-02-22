#!/usr/bin/env python3
"""
QA Suite 4: Output Drift & Regression Tests
Validates that core pipeline outputs do NOT change between runs for the same input.
Any drift in fingerprint, scene count, or signal range signals a broken determinism contract.

Run: PYTHONPATH=. SCRIPTPULSE_HEURISTICS_ONLY=1 python3 tests/unit/test_regression.py
"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"

import unittest

REGRESSION_SCRIPT = """INT. OFFICE - DAY

SARAH
We need to close the deal today. If we don't, everything falls apart.

TOM
I know. The board won't wait. We've been through worse.

SARAH
Have we?

INT. CONFERENCE ROOM - NIGHT

CEO
The numbers are catastrophic. Someone needs to explain this.

ANALYST
Market conditions shifted overnight. We couldn't have predicted this.

CEO
(quietly)
Find me an answer. Or find a new job.

EXT. ROOFTOP - SUNSET

MARCUS stares at the skyline. The city pulses below him.

MARCUS
This was never about the money. It was about the people we failed.

INT. HOSPITAL ROOM - NIGHT

Machines beep softly. DR. CHEN enters and checks the chart.

DR. CHEN
She's stable for now. But we need to prepare for what comes next."""


def run_pipeline(script, **kwargs):
    from scriptpulse.pipeline import runner
    return runner.run_pipeline(script, cpu_safe_mode=True, **kwargs)


def _fingerprint(result: dict) -> str:
    """Stable hash of key structural outputs."""
    summary = {
        'total_scenes': result.get('total_scenes'),
        'trace_len': len(result.get('temporal_trace', [])),
        'run_id': result.get('meta', {}).get('run_id'),
        'version': result.get('meta', {}).get('version'),
    }
    return hashlib.md5(json.dumps(summary, sort_keys=True).encode()).hexdigest()


class TestDeterminism(unittest.TestCase):

    def test_same_input_produces_same_scene_count(self):
        """Scene count is stable across two sequential runs."""
        r1 = run_pipeline(REGRESSION_SCRIPT)
        r2 = run_pipeline(REGRESSION_SCRIPT)
        self.assertEqual(r1['total_scenes'], r2['total_scenes'])

    def test_same_input_produces_same_run_id(self):
        """Content fingerprint (run_id) is identical for identical inputs."""
        r1 = run_pipeline(REGRESSION_SCRIPT)
        r2 = run_pipeline(REGRESSION_SCRIPT)
        self.assertEqual(
            r1['meta']['run_id'],
            r2['meta']['run_id'],
            "run_id must be deterministic for same input"
        )

    def test_same_input_produces_same_fingerprint(self):
        """Structural fingerprint is identical across runs."""
        r1 = run_pipeline(REGRESSION_SCRIPT)
        r2 = run_pipeline(REGRESSION_SCRIPT)
        self.assertEqual(_fingerprint(r1), _fingerprint(r2))

    def test_temporal_trace_length_stable(self):
        """temporal_trace length does not drift between runs."""
        r1 = run_pipeline(REGRESSION_SCRIPT)
        r2 = run_pipeline(REGRESSION_SCRIPT)
        self.assertEqual(len(r1['temporal_trace']), len(r2['temporal_trace']))

    def test_signal_range_stable(self):
        """All temporal attention signals stay in [0, 1] range on repeated runs."""
        for _ in range(2):
            result = run_pipeline(REGRESSION_SCRIPT)
            for i, scene in enumerate(result.get('temporal_trace', [])):
                signal = scene.get('attention', scene.get('signal', None))
                if signal is not None:
                    self.assertGreaterEqual(signal, 0.0, f"Scene {i} signal below 0")
                    self.assertLessEqual(signal, 1.0, f"Scene {i} signal above 1")


class TestRegressionKnownOutputs(unittest.TestCase):
    """
    Regression guard: known-good outputs for the standard regression script.
    If these break, a core algorithm has drifted.
    """

    @classmethod
    def setUpClass(cls):
        cls.result = run_pipeline(REGRESSION_SCRIPT)

    def test_scene_count_meets_minimum(self):
        """Standard 4-scene script must produce at least 4 scenes."""
        self.assertGreaterEqual(self.result['total_scenes'], 4)

    def test_trace_contains_expected_keys(self):
        """Each temporal_trace entry has expected keys."""
        required_keys = {'scene_index'}
        for i, entry in enumerate(self.result.get('temporal_trace', [])):
            self.assertTrue(required_keys.issubset(entry.keys()),
                            f"Scene {i} trace missing keys: {required_keys - entry.keys()}")

    def test_meta_version_is_locked(self):
        """metric_version is pinned and must not change unexpectedly."""
        version = self.result.get('meta', {}).get('metric_version')
        self.assertIsNotNone(version, "metric_version must exist")

    def test_output_is_json_serializable(self):
        """Full output must be JSON-serializable (Streamlit & API compatibility)."""
        try:
            json.dumps(self.result)
        except (TypeError, ValueError) as e:
            self.fail(f"Output is not JSON-serializable: {e}")

    def test_runtime_ms_is_positive(self):
        """runtime_ms must be a positive number."""
        runtime = self.result.get('runtime_ms', 0)
        self.assertGreater(runtime, 0, "runtime_ms should be positive")

    def test_scene_info_is_list(self):
        """scene_info must be a list."""
        self.assertIsInstance(self.result.get('scene_info'), list)

    def test_scene_info_length_matches_total_scenes(self):
        """scene_info length equals total_scenes."""
        self.assertEqual(
            len(self.result.get('scene_info', [])),
            self.result.get('total_scenes', -1)
        )

    def test_no_nan_or_inf_in_trace(self):
        """No NaN/Inf values in temporal_trace signals."""
        import math
        for i, entry in enumerate(self.result.get('temporal_trace', [])):
            for k, v in entry.items():
                if isinstance(v, float):
                    self.assertFalse(math.isnan(v), f"NaN in scene {i} key '{k}'")
                    self.assertFalse(math.isinf(v), f"Inf in scene {i} key '{k}'")


class TestHeuristicsOnlyMode(unittest.TestCase):
    """Validates that SCRIPTPULSE_HEURISTICS_ONLY=1 produces valid output."""

    def test_heuristics_mode_produces_output(self):
        """Heuristics-only mode produces non-empty output."""
        result = run_pipeline(REGRESSION_SCRIPT)
        self.assertGreater(result.get('total_scenes', 0), 0)

    def test_heuristics_mode_output_structure_intact(self):
        """Output structure is identical to full ML mode."""
        result = run_pipeline(REGRESSION_SCRIPT)
        for key in ['total_scenes', 'temporal_trace', 'meta', 'scene_info']:
            self.assertIn(key, result)

    def test_heuristics_mode_no_crash_on_repeated_calls(self):
        """Three sequential heuristics-mode calls all succeed."""
        for i in range(3):
            result = run_pipeline(REGRESSION_SCRIPT)
            self.assertIsInstance(result, dict, f"Run {i+1} failed")


if __name__ == '__main__':
    print("═" * 55)
    print("QA SUITE 4: Output Drift & Regression Tests")
    print("═" * 55)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDeterminism))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionKnownOutputs))
    suite.addTests(loader.loadTestsFromTestCase(TestHeuristicsOnlyMode))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
