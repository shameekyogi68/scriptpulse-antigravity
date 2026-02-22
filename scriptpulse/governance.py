"""
ScriptPulse Governance & Sanitization
Provides hard bounds on input parameters to protect NLP models from Out-Of-Memory (OOM) 
crashes, binary injection, and malformed encoding attacks.
"""

MAX_CHARS = 5 * 1024 * 1024  # 5 MB threshold

def validate_request(text_data: str):
    """
    Validates the input string before it enters the parsing pipeline.
    Raises ValueError on violation.
    """
    if not isinstance(text_data, str):
        raise ValueError("Governance Audit Failed: Input must be a valid UTF-8 string.")
        
    if len(text_data) > MAX_CHARS:
        raise ValueError(f"Governance Audit Failed: Input exceeds maximum allowed length of {MAX_CHARS} characters.")
        
    # Check for binary null bytes common in injection or malformed PDF extracts
    if '\x00' in text_data:
        raise ValueError("Governance Audit Failed: Binary payload or null-bytes detected.")
        
    return True
