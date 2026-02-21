"""
ScriptPulse Pydantic Schemas - Research-Grade Type Safety

Defines strict data contracts for all data flowing through the pipeline.
Replaces the loose dict-based contracts with validated, documented models.
"""

from typing import Optional, List, Dict, Any
try:
    from pydantic import BaseModel, ConfigDict, Field
except ImportError:
    # Graceful degradation if pydantic is not installed
    import logging
    logging.getLogger('scriptpulse.schemas').warning(
        "Pydantic not installed — schemas will not enforce runtime validation. "
        "Install with: pip install pydantic>=2.0"
    )
    # Provide no-op base class
    class BaseModel:
        model_config = {}
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
    class ConfigDict:
        def __init__(self, **kwargs): pass
    def Field(default=None, **kwargs): return default


# =============================================================================
# FEATURE SCHEMAS
# =============================================================================

class LinguisticLoad(BaseModel):
    """Features from syntactic/linguistic analysis of scene lines."""
    model_config = ConfigDict(extra='allow')

    sentence_count: int = 0
    mean_sentence_length: float = 0.0
    readability_grade: float = 0.0
    idea_density: float = 0.0
    syllable_complexity: float = 0.0


class DialogueDynamics(BaseModel):
    """Features from dialogue pattern analysis."""
    model_config = ConfigDict(extra='allow')

    dialogue_turns: int = 0
    speaker_switches: int = 0
    dialogue_density: float = 0.0
    unique_speakers: int = 0
    avg_speech_length: float = 0.0


class VisualAbstraction(BaseModel):
    """Features from visual/action line analysis."""
    model_config = ConfigDict(extra='allow')

    action_line_count: int = 0
    visual_density: float = 0.0
    kinetic_verb_count: int = 0
    color_mentions: int = 0


class ReferentialMemory(BaseModel):
    """Features from character reference tracking."""
    model_config = ConfigDict(extra='allow')

    active_character_count: int = 0
    new_character_count: int = 0
    pronoun_density: float = 0.0
    referential_load: float = 0.0


class StructuralChange(BaseModel):
    """Features from scene boundary/transition analysis."""
    model_config = ConfigDict(extra='allow')

    event_boundary_score: float = 0.0
    location_change: bool = False
    time_change: bool = False


class SceneFeatures(BaseModel):
    """Complete feature vector for a single scene.
    
    This is the output of the PerceptionAgent (EncodingAgent) and the input
    to the DynamicsAgent for temporal simulation.
    """
    model_config = ConfigDict(extra='allow')

    scene_index: int = 0
    scene_heading: str = ""
    line_count: int = 0
    word_count: int = 0

    # Core feature groups
    linguistic_load: Optional[LinguisticLoad] = None
    dialogue_dynamics: Optional[DialogueDynamics] = None
    visual_abstraction: Optional[VisualAbstraction] = None
    referential_memory: Optional[ReferentialMemory] = None
    structural_change: Optional[StructuralChange] = None

    # Derived scalars (from various extractors)
    information_entropy: float = 0.0
    ambient_tension: float = 0.0
    tell_vs_show_ratio: float = 0.0
    on_the_nose_ratio: float = 0.0
    shoe_leather_score: float = 0.0
    payoff_density: float = 0.0
    stichomythia_detected: bool = False

    # Optional advanced features
    stakes_taxonomy: Optional[Dict[str, Any]] = None
    scene_purpose: Optional[str] = None
    character_scene_vectors: Optional[Dict[str, Any]] = None
    opening_hook_score: Optional[float] = None
    passive_voice_ratio: float = 0.0
    cliche_ratio: float = 0.0
    scene_turn_type: Optional[str] = None


# =============================================================================
# TEMPORAL SIGNAL SCHEMAS
# =============================================================================

class TemporalSignal(BaseModel):
    """Output of the DynamicsAgent for a single scene timestep.
    
    Represents the simulated reader's cognitive/emotional state at time t.
    """
    model_config = ConfigDict(extra='allow')

    scene_index: int = 0
    instantaneous_effort: float = 0.0
    recovery_credit: float = 0.0
    attentional_signal: float = 0.5
    fatigue_state: float = 0.0
    confidence_score: float = 0.8

    # ACD state
    acd_state: str = "stable"  # stable | drift | collapse

    # TAM output
    tam_adjustment: float = 0.0

    # Pattern flags
    is_risk_zone: bool = False


class DetectedPattern(BaseModel):
    """A pattern detected in the temporal trace (e.g., sustained demand)."""
    model_config = ConfigDict(extra='allow')

    pattern_type: str = ""
    scene_range: List[int] = []
    confidence_band: str = "medium"
    severity: float = 0.0
    description: str = ""


# =============================================================================
# PIPELINE OUTPUT SCHEMA
# =============================================================================

class WriterIntelligence(BaseModel):
    """Output of the WriterAgent's analysis."""
    model_config = ConfigDict(extra='allow')

    health_report: List[Dict[str, Any]] = []
    ranked_edits: List[Dict[str, Any]] = []
    dashboard: Dict[str, Any] = {}
    character_arcs: Dict[str, Any] = {}


class PipelineOutput(BaseModel):
    """Top-level output of the ScriptPulse pipeline (run_pipeline).
    
    This is the complete analysis result returned to the user.
    """
    model_config = ConfigDict(extra='allow')

    # Structural
    scenes: List[Dict[str, Any]] = []
    parsed_lines: List[Dict[str, Any]] = []

    # Feature extraction
    features: List[Dict[str, Any]] = []

    # Temporal simulation
    trace: List[Dict[str, Any]] = []
    patterns: List[Dict[str, Any]] = []

    # Interpretation
    mediation: Optional[Dict[str, Any]] = None
    explanations: List[Dict[str, Any]] = []
    scene_notes: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []

    # Writer intelligence
    writer_intelligence: Optional[Dict[str, Any]] = None

    # Ethics
    agency_analysis: Optional[Dict[str, Any]] = None
    fairness_audit: Optional[Dict[str, Any]] = None

    # Experimental
    stanislavski_trace: List[Dict[str, Any]] = []
    resonance_scores: List[Dict[str, Any]] = []

    # Metadata
    fingerprint: str = ""
    genre: str = "drama"
    lens: str = "viewer"
    pipeline_version: str = "14.0"
    wall_time_seconds: float = 0.0
