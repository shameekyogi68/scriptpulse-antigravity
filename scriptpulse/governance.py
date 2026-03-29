"""
ScriptPulse Governance & Sanitization
Provides hard bounds on input parameters to protect NLP models from Out-Of-Memory (OOM) 
crashes, binary injection, and malformed encoding attacks.
"""

MAX_CHARS = 5 * 1024 * 1024  # 5 MB threshold

class PolicyViolationError(Exception):
    """Raised when an input violates the system's philosophical constraints."""
    pass

PROHIBITED_PHRASES = {
    "rank 1 to 10",
    "grade this",
    "score",
    "hiring recommendation"
}

def validate_request(text_data: str):
    """
    Validates the input string before it enters the parsing pipeline.
    Raises ValueError or PolicyViolationError on violation.
    """
    if not isinstance(text_data, str):
        raise ValueError("Governance Audit Failed: Input must be a valid UTF-8 string.")
        
    if len(text_data) > MAX_CHARS:
        raise ValueError(f"Governance Audit Failed: Input exceeds maximum allowed length of {MAX_CHARS} characters.")
        
    # Check for binary null bytes common in injection or malformed PDF extracts
    if '\x00' in text_data:
        raise ValueError("Governance Audit Failed: Binary payload or null-bytes detected.")

    # LHTL: Enforce philosophical constraints
    for phrase in PROHIBITED_PHRASES:
        if phrase in text_data.lower():
            raise PolicyViolationError(f"Governance Audit Failed: Prohibited request pattern detected ('{phrase}').")
        
    return True
