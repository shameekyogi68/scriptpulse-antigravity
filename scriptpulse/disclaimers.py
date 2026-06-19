"""
ScriptPulse — mandatory user-facing disclaimers.
Every report, export, and dashboard must surface these truth boundaries.
"""

SHORT_DISCLAIMER = (
    "Reference signals only — not a quality score, ranking, or approval system."
)

FULL_DISCLAIMER_LINES = [
    "This is not a quality score.",
    "This is not a ranking or approval system.",
    "This tool does not replace human judgment or professional coverage.",
    "Outputs describe first-pass audience experience signals for reflection only.",
    "ScriptPulse is not suitable for evaluation, selection, or rejection decisions.",
]

FULL_DISCLAIMER_HTML = (
    "<ul style='margin: 0; padding-left: 1.2rem; line-height: 1.7;'>"
    + "".join(f"<li>{line}</li>" for line in FULL_DISCLAIMER_LINES)
    + "</ul>"
)

FULL_DISCLAIMER_MARKDOWN = "\n".join(f"- {line}" for line in FULL_DISCLAIMER_LINES)

METHODOLOGY_NOTE = (
    "ScriptPulse uses a hybrid pipeline: screenplay parsing → narrative feature extraction → "
    "attentional dynamics simulation → structural interpretation. Numeric indices are calibrated "
    "reference signals derived from your script's structure and pacing — they are not predictions "
    "of commercial success or artistic merit. Optional AI memos are grounded in pipeline data; "
    "when ML models are unavailable, heuristic fallbacks preserve the same output structure "
    "with reduced precision."
)


def engagement_signal_label(score: float) -> str:
    """Neutral, non-judgmental label for the ScriptPulse reference index."""
    if score >= 70:
        return "High engagement signal"
    if score >= 45:
        return "Moderate engagement signal"
    return "Low engagement signal — early exploration"


def get_engine_mode_note() -> str:
    """Describe whether ML models or heuristics are active."""
    import os
    if os.environ.get("SCRIPTPULSE_HEURISTICS_ONLY", "0") == "1":
        return "Engine mode: heuristic analysis (ML models disabled)."
    try:
        import scriptpulse.utils.model_manager as mm
        if mm._HEURISTICS_ONLY:
            return "Engine mode: heuristic analysis (ML models disabled)."
        if mm.torch is None or mm.SentenceTransformer is None:
            return "Engine mode: heuristic analysis (ML dependencies not installed)."
        return "Engine mode: hybrid ML + cognitive simulation."
    except Exception:
        return "Engine mode: hybrid analysis."
