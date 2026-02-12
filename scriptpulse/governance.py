"""
Governance & Policy Boundary Layer (GPBL)
vNext.5 Market Upgrade - Integrity Protection

Hard-coded refusal of misuse patterns.
Prevents the system from being used for ranking, scoring, or hiring.
"""

from enum import Enum

class UseContext(Enum):
    PERSONAL = "personal_writing"
    COLLABORATIVE = "collaborative_room"
    ACADEMIC = "academic_research"
    DEVELOPMENT = "development_exploration"

class Role(Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    PRODUCER = "producer"
    AUDITOR = "auditor"

class PolicyViolationError(Exception):
    pass

def validate_context(context_type: UseContext):
    """
    PUCD: Professional Use-Context Declaration
    Ensures analysis runs within declared, valid contexts.
    """
    if not isinstance(context_type, UseContext):
        raise PolicyViolationError("Invalid or missing Use Context declaration.")
    return True

class InputSizeError(PolicyViolationError):
    """Raised when input exceeds size limits."""
    pass

class BinaryInputError(PolicyViolationError):
    """Raised when input contains non-text binary content."""
    pass

# Hard Limits
MAX_BYTES = 5_000_000   # 5 MB
MAX_CHARS = 1_000_000   # 1M characters

def validate_request(input_text, context=None):
    """
    Validate that the request complies with ethical and safety boundaries.
    Raises PolicyViolationError if misuse is detected.
    Raises InputSizeError if input exceeds size limits.
    Raises BinaryInputError if input contains non-text content.
    """
    if not input_text:
        return # Empty is handled elsewhere
    
    # === SIZE GUARD (Priority 1 — Must run BEFORE any parsing) ===
    byte_size = len(input_text.encode('utf-8'))
    char_size = len(input_text)
    
    if byte_size > MAX_BYTES:
        raise InputSizeError(
            f"Input rejected: {byte_size:,} bytes exceeds maximum of {MAX_BYTES:,} bytes (5 MB). "
            "Please reduce script size."
        )
    
    if char_size > MAX_CHARS:
        raise InputSizeError(
            f"Input rejected: {char_size:,} characters exceeds maximum of {MAX_CHARS:,}. "
            "Please reduce script size."
        )
    
    # === BINARY GUARD ===
    if '\x00' in input_text:
        raise BinaryInputError(
            "Input rejected: Binary content detected (null bytes). "
            "Please upload a valid UTF-8 text file."
        )
        
    text_lower = input_text.lower()
    
    # 1. Ranking / Scoring Refusal
    # "Rate this script", "Give me a score", "Rank 1 to 10"
    forbidden_terms = [
        "give me a score",
        "rate this script",
        "rank 1 to 10",
        "grade this",
        "coverage score",
        "box office prediction",
        "hiring recommendation",
        "compare to" 
    ]
    
    for term in forbidden_terms:
        if term in text_lower:
            raise PolicyViolationError(
                f"Policy Refusal: Request contains forbidden term '{term}'. "
                "ScriptPulse cannot be used for scoring, ranking, or predictive valuation."
            )
            
    # 2. Batch / Comparative Refusal (Context Check)
    # If the system detects it is being run in a loop comparison (simulated here)
    if context and context.get('mode') == 'batch_comparison':
         raise PolicyViolationError(
             "Policy Refusal: Batch comparison mode is disabled to prevent "
             "industrial filtering. Please analyze scripts individually."
         )
         
    return True
