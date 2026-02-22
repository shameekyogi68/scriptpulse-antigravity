"""
ScriptPulse Structured Logger
Provides a centralized, environment-aware logging facility for all agents.

Usage:
    from scriptpulse.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.warning("Agent failed, using fallback: %s", error)

The LOG_LEVEL environment variable controls verbosity:
    - DEBUG: All traces, math walkthrough per scene
    - INFO: Agent milestones and model load events
    - WARNING: Fallbacks and non-fatal failures (default)
    - ERROR: Critical failures that may impact correctness
"""

import logging
import os
import sys

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Allow override via environment variable for production deployments
_DEFAULT_LEVEL = os.environ.get("SCRIPTPULSE_LOG_LEVEL", "WARNING").upper()

def _configure_root_logger():
    """Configure root ScriptPulse logger once on first import."""
    root = logging.getLogger("scriptpulse")
    if root.handlers:
        return  # Already configured, skip

    level = getattr(logging, _DEFAULT_LEVEL, logging.WARNING)
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    handler.setFormatter(formatter)
    root.addHandler(handler)

_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger scoped under the 'scriptpulse' namespace.
    e.g. get_logger('scriptpulse.agents.dynamics_agent') 
    """
    return logging.getLogger(name)
