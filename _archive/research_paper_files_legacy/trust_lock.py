"""
ScriptPulse Trust Lock (LHTL)
Philosophical Checksum & Invariant Enforcement
"""

import os
import hashlib
from . import governance

# Immutable Constitution Hash (Simulated)
# In a real build system, this would be cryptographically signed.
REQUIRED_REFUSAL_TERMS = {
    "rank 1 to 10",
    "grade this",
    "score",
    "hiring recommendation"
}

def verify_system_integrity():
    """
    LHTL: Long-Horizon Trust Lock
    Verifies that the system's philosophical constraints are active.
    Raises SystemError if constraints are disabled or tampered with.
    """
    
    # 1. Verify Governance Layer is Active
    # Check if forbidden terms are actually forbidden in the loaded module
    try:
        # We can't inspect the local scope easily, but we can test the function
        # Test a forbidden term (expecting PolicyViolationError)
        governance.validate_request("Please rank 1 to 10")
        # If no error, the guardrails are down!
        raise SystemError("CRITICAL: Governance layer inactive. Refusal logic failed.")
    except governance.PolicyViolationError:
        # Good, it refused.
        pass
    except Exception as e:
        # Unexpected error
        raise SystemError(f"CRITICAL: Governance check failed with unexpected error: {e}")

    # 2. Verify Negative Roadmap Exists
    # This document is the system's constitution.
    roadmap_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Negative_Roadmap.md')
    if not os.path.exists(roadmap_path):
        raise SystemError("CRITICAL: Negative Roadmap (Constitution) missing. Deployment unsafe.")
        
    return True
