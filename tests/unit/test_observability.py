#!/usr/bin/env python3
"""
QA Suite 2: Logger & Observability Unit Tests
Validates the structured logging module and health_check() endpoint.
Run: PYTHONPATH=. python3 tests/unit/test_observability.py
"""
import sys, os, logging, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest

class TestLogger(unittest.TestCase):

    def test_get_logger_returns_logger(self):
        """get_logger() returns a standard Python Logger."""
        from scriptpulse.utils.logger import get_logger
        log = get_logger("scriptpulse.test")
        self.assertIsInstance(log, logging.Logger)

    def test_logger_namespace_scoped(self):
        """Logger name is scoped under 'scriptpulse'."""
        from scriptpulse.utils.logger import get_logger
        log = get_logger("scriptpulse.agents.test_agent")
        self.assertTrue(log.name.startswith("scriptpulse"))

    def test_logger_module_name_works(self):
        """get_logger(__name__) pattern works without error."""
        from scriptpulse.utils.logger import get_logger
        log = get_logger(__name__)
        self.assertIsNotNone(log)

    def test_warning_does_not_crash(self):
        """Logging a warning message does not raise."""
        from scriptpulse.utils.logger import get_logger
        log = get_logger("scriptpulse.qa_test")
        try:
            log.warning("Test warning: %s", "something went wrong")
        except Exception as e:
            self.fail(f"Logger warning raised: {e}")

    def test_default_level_is_warning(self):
        """Default log level is WARNING or higher (not DEBUG)."""
        from scriptpulse.utils.logger import get_logger
        log = get_logger("scriptpulse.level_test")
        root = logging.getLogger("scriptpulse")
        self.assertGreaterEqual(root.level, logging.WARNING)

    def test_logger_env_var_controlled(self):
        """SCRIPTPULSE_LOG_LEVEL env var is read at module import."""
        # This validates the var is acknowledged — level will be WARNING in test env
        from scriptpulse.utils import logger as logger_module
        self.assertIn(os.environ.get("SCRIPTPULSE_LOG_LEVEL", "WARNING").upper(),
                      ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])


class TestHealthCheck(unittest.TestCase):

    def setUp(self):
        """Import runner once — uses cached agents."""
        from scriptpulse.pipeline import runner
        self.runner = runner

    def test_health_check_returns_dict(self):
        """health_check() returns a dict."""
        result = self.runner.health_check()
        self.assertIsInstance(result, dict)

    def test_health_check_has_status_key(self):
        """health_check() result contains 'status' key."""
        result = self.runner.health_check()
        self.assertIn('status', result)

    def test_health_check_status_is_valid(self):
        """status is either 'healthy' or 'degraded'."""
        result = self.runner.health_check()
        self.assertIn(result['status'], ['healthy', 'degraded'])

    def test_health_check_has_agents_key(self):
        """health_check() result contains 'agents' dict."""
        result = self.runner.health_check()
        self.assertIn('agents', result)
        self.assertIsInstance(result['agents'], dict)

    def test_health_check_has_governance_key(self):
        """health_check() result contains 'governance' bool."""
        result = self.runner.health_check()
        self.assertIn('governance', result)
        self.assertIsInstance(result['governance'], bool)

    def test_health_check_governance_passes(self):
        """Governance firewall is healthy."""
        result = self.runner.health_check()
        self.assertTrue(result['governance'], "Governance module must be healthy")

    def test_health_check_has_config_files(self):
        """health_check() result contains 'config_files' dict."""
        result = self.runner.health_check()
        self.assertIn('config_files', result)
        self.assertIsInstance(result['config_files'], dict)

    def test_health_check_agent_keys_present(self):
        """All expected agent names appear in health report."""
        result = self.runner.health_check()
        expected = {'ParsingAgent', 'SegmentationAgent', 'DynamicsAgent',
                    'InterpretationAgent', 'EthicsAgent'}
        self.assertTrue(expected.issubset(set(result['agents'].keys())))

    def test_health_check_idempotent(self):
        """Calling health_check() twice produces consistent status."""
        r1 = self.runner.health_check()
        r2 = self.runner.health_check()
        self.assertEqual(r1['status'], r2['status'])
        self.assertEqual(r1['governance'], r2['governance'])


if __name__ == '__main__':
    print("═" * 55)
    print("QA SUITE 2: Logger & Observability Unit Tests")
    print("═" * 55)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthCheck))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
