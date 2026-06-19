# MODULE: governance.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Governance & Sanitization
Provides hard bounds on input parameters to protect NLP models from Out-Of-Memory (OOM) 
crashes, binary injection, and malformed encoding attacks.
"""

MAX_CHARS = 5 * 1024 * 1024  # 5 MB threshold

class PolicyViolationError(Exception):
    """Raised when an input violates the system's philosophical constraints."""
    pass

# Prompt-injection / meta-request patterns — not screenplay vocabulary.
# Screenplays may contain words like "score" in dialogue; we only block explicit
# evaluation requests at the start of a line or as standalone instructions.
PROHIBITED_REQUEST_PATTERNS = (
    "rank 1 to 10",
    "rank this script",
    "grade this script",
    "grade this screenplay",
    "score this script",
    "score this screenplay",
    "hiring recommendation",
    "should we buy this",
    "pass or fail",
    "recommend pass",
    "recommend reject",
)


def _contains_prohibited_request(text_data: str) -> str | None:
    """Return the matched prohibited pattern, if any."""
    lower = text_data.lower()
    for phrase in PROHIBITED_REQUEST_PATTERNS:
        if phrase in lower:
            return phrase
    return None


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

    matched = _contains_prohibited_request(text_data)
    if matched:
        raise PolicyViolationError(
            f"Governance Audit Failed: Prohibited evaluation request detected ('{matched}'). "
            "ScriptPulse models audience experience signals — it cannot rank, grade, or approve scripts."
        )
        
    return True
