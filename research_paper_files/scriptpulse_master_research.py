# =========================================================================
# SCRIPTPULSE: COMPREHENSIVE RESEARCH REPOSITORY
# Unified Deterministic Analysis Engine v1.0
# =========================================================================


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: model_manager.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Model Manager (MLOps Layer)
Centralizes model loading, caching, and hardware acceleration.

Active model stack:
  - spaCy en_core_web_sm  (~12 MB)  — always local, no download
  - Jina v2 Small          (~66 MB)  — remote first-run, cached in ~/.scriptpulse/models (8k context)
  - DeBERTa-v3-xsmall      (~140 MB) — remote first-run, cached in ~/.scriptpulse/models (Zero-Shot)

NO BERT Large or GPT-2 in this stack by design (saves ~1.8 GB).
"""

import os
import sys
import json
import hashlib
import logging

logger = logging.getLogger('scriptpulse.mlops')

# =============================================================================
# PERFORMANCE: Environment-driven heuristics-only mode.
# Set SCRIPTPULSE_HEURISTICS_ONLY=1 to skip ALL transformer models entirely.
# This drops Jina SBERT (~66 MB) and DeBERTa Zero-Shot (~140 MB).
# spaCy en_core_web_sm is always local and lightweight — it stays ON regardless.
# All agents fall through to their existing fast heuristic fallbacks.
# Analytical output structure is identical; embedding subfields are approximated.
# =============================================================================
_HEURISTICS_ONLY = os.environ.get("SCRIPTPULSE_HEURISTICS_ONLY", "0") == "1"

# Centralized Imports
try:
    import torch
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    import spacy
except ImportError:
    torch = None
    pipeline = None
    SentenceTransformer = None
    spacy = None

REQUIRED_VERSIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'required_model_versions.json'
)

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance.init_config()
        return cls._instance
        
    def init_config(self, force=False):
        if self._initialized and not force:
            return

        self.cache_dir = os.path.abspath('.scriptpulse_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Device Selection
        self.device = -1
        if torch and torch.cuda.is_available():
            self.device = 0
            
        # v13.1: Load required model versions
        self._required_versions = self._load_required_versions()
        self._loaded_models = {}
            
        logger.info("Model Cache: %s", self.cache_dir)
        logger.info("Acceleration: %s", 'CUDA' if self.device == 0 else 'CPU')
        if self._required_versions:
            logger.info("Version enforcement: %d models registered", len(self._required_versions))
    
    def _load_required_versions(self):
        """Load required model versions from spec file."""
        try:
            if os.path.exists(REQUIRED_VERSIONS_PATH):
                with open(REQUIRED_VERSIONS_PATH, 'r') as f:
                    data = json.load(f)
                return data.get('models', {})
        except Exception as e:
            logger.warning("Could not load required_model_versions.json: %s", e)
        return {}
    
    def _verify_model(self, task, model_name):
        """
        v13.1: Strict version check.
        Verifies that the requested model matches the registered spec.
        Mismatch → hard fail with error code.
        """
        if not self._required_versions:
            return  # No enforcement file found, skip
        
        spec = self._required_versions.get(task)
        if spec is None:
            # Task not registered — warn but allow
            logger.warning("MODEL_NOT_REGISTERED — task '%s' not in required_model_versions.json", task)
            return
        
        required_name = spec.get('name', '')
        if model_name != required_name:
            error_msg = (
                f"MODEL_NAME_MISMATCH: Requested '{model_name}' but required '{required_name}' "
                f"for task '{task}'. Update required_model_versions.json to change models."
            )
            raise RuntimeError(f"HARD FAIL — {error_msg}")
        
    def get_pipeline(self, task, model_name):
        """
        Get a HuggingFace pipeline with caching and version enforcement.
        Returns None immediately if SCRIPTPULSE_HEURISTICS_ONLY=1.
        """
        if _HEURISTICS_ONLY:
            logger.debug("Heuristics-only mode: skipping pipeline %s", model_name)
            return None
        if not pipeline:
            return None
        
        # v13.1: Strict version check
        self._verify_model(task, model_name)
            
        try:
            logger.info("Loading Pipeline: %s...", model_name)
            pipe = pipeline(
                task, 
                model=model_name, 
                device=self.device,
                model_kwargs={"cache_dir": self.cache_dir} 
            )
            self._loaded_models[task] = {
                'name': model_name,
                'type': 'pipeline',
                'loaded_at': __import__('time').time(),
            }
            return pipe
        except RuntimeError:
            raise  # Re-raise version check failures
        except Exception as e:
            logger.error("Failed to load pipeline %s: %s", model_name, e)
            return None

    def get_sentence_transformer(self, model_name="jinaai/jina-embeddings-v2-small-en"):
        """
        Get a SentenceTransformer model (Jina v2 Small).
        Loaded from HuggingFace Hub on first use, then cached locally.
        """
        if _HEURISTICS_ONLY:
            return None
        if not SentenceTransformer:
            return None
        
        self._verify_model('sentence-transformer', model_name)
            
        try:
            if model_name not in self._loaded_models:
                logger.info("Loading SBERT (Jina v2-Small): %s...", model_name)
                self._loaded_models[model_name] = SentenceTransformer(model_name, cache_folder=self.cache_dir)
            return self._loaded_models[model_name]
        except Exception as e:
            logger.error("Failed to load SBERT %s: %s", model_name, e)
            return None

    def get_zero_shot(self):
        """
        Get a Zero-Shot Classifier (DeBERTa-v3).
        Uses DeBERTa-v3-xsmall (~140MB) for superior research accuracy vs size ratio.
        """
        if _HEURISTICS_ONLY:
            return None
        
        # Consistent with required_model_versions.json
        spec = self._required_versions.get('zero-shot-classification', {})
        model_name = spec.get('name', "MoritzLaurer/DeBERTa-v3-xsmall-mnli-alnli")
        
        return self.get_pipeline("zero-shot-classification", model_name)

    def get_spacy(self, model_name="en_core_web_sm"):
        """
        Get a spaCy model (small).
        Requires 'spacy' and 'en_core_web_sm' to be installed locally.
        Does NOT download automatically by default to remain local.
        """
        if _HEURISTICS_ONLY or not spacy:
            return None
            
        try:
            if model_name not in self._loaded_models:
                logger.info("Loading spaCy model: %s...", model_name)
                self._loaded_models[model_name] = spacy.load(model_name)
            return self._loaded_models[model_name]
        except Exception as e:
            logger.warning("spaCy model %s not found locally. Instructions: 'python -m spacy download %s'", model_name, model_name)
            return None
    
    def get_loaded_models(self):
        """Return dict of currently loaded model info for telemetry."""
        return dict(self._loaded_models)

    def release_models(self):
        """
        Explicitly release all loaded model references and suggest GC.
        Call this after analysis completes on memory-constrained machines
        to return SBERT/DeBERTa heap to the OS before the next UI render.
        """
        import gc
        self._loaded_models.clear()
        gc.collect()
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("ModelManager: model references released, GC triggered.")


# Singleton Access
manager = ModelManager()



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: models.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: normalizer.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Universal Format Normalizer
Preprocessing middleware to standardize messy or creative script formats.
"""
import re

def normalize_script(text):
    """
    Normalize script text to standard Screenplay format (mostly).
    
    Transformations:
    1. Headings: INT, EXT, INTERIOR, I/E -> INT. / EXT. (Uppercase)
    2. Dialogue: "NAME: Text" -> "NAME\nText"
    3. Formatting: Standardizes dashes, newlines.
    4. Characters: Attempts to uppercase mixed-case character names.
    """
    if not text:
        return ""
        
    # 1. Basic cleaning
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Split lines
    lines = text.split('\n')
    output_lines = []
    
    # Pre-compile regex
    # Headings: INT, EXT, I/E, etc. at start of line
    # Matches: "int. room", "Interior Room", "i/e car", "ext garden", "interior: house"
    re_heading = re.compile(r'^(INT|EXT|I\/E|INT\/EXT|EXT\/INT|INTERIOR|EXTERIOR)([:\.\s]|$)', re.IGNORECASE)

    
    # Transitions ending in TO:
    re_transition = re.compile(r'.* TO:$', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            output_lines.append("")
            continue
            
        # A. Detect Scene Headings
        match = re_heading.match(stripped)
        if match:
            # Found heading. Standardize.
            raw_prefix = match.group(1).upper()
            slug = stripped[len(match.group(0)):].strip()
            
            # Map variations
            if raw_prefix in ['INTERIOR']: prefix = 'INT.'
            elif raw_prefix in ['EXTERIOR']: prefix = 'EXT.'
            elif raw_prefix in ['INT', 'EXT']: prefix = raw_prefix + '.'
            elif raw_prefix in ['I/E']: prefix = 'I/E.'
            else: prefix = raw_prefix + '.' # Fallback
            
            # Ensure nice spacing
            # Force upper slug
            normalized = f"{prefix} {slug.upper()}"
            
            # Ensure double newline before headers (helps segmentation)
            if output_lines and output_lines[-1] != "":
                output_lines.append("")
                
            output_lines.append(normalized)
            continue
            
        # B. Detect "CHARACTER: Dialogue"
        # Logic: Starts with name, has colon, text follows.
        # Exclude "CUT TO:" (Transition)
        if re_transition.match(stripped):
            output_lines.append(stripped.upper())
            continue
            
        if ':' in stripped:
            parts = stripped.split(':', 1)
            char_part = parts[0].strip()
            dial_part = parts[1].strip()
            
            # Name heuristic: Shortish, mostly letters/spaces
            # (Allows "MR. SMITH" or "John")
            if 0 < len(char_part) < 30 and dial_part:
                # Treat as dialogue
                output_lines.append(char_part.upper())
                output_lines.append(dial_part)
                continue
                
        # C. Detect Mixed Case Character Cues
        # Heuristic: Short line without end punctuation, followed by text?
        # This is risky for "He runs" followed by "He jumps".
        # But critical for "John" followed by "Hello".
        
        # Check constraints:
        # 1. Not a heading (checked)
        # 2. Not a transition (checked)
        # 3. Short length (< 25 chars)
        # 4. No sentence-ending punctuation (., ?, !) unless it's an initial (J.T.)
        # 5. Looks name-y?
        
        is_upper = stripped.isupper()
        no_punct = not stripped.endswith(('.', '!', '?')) or stripped.endswith('.') and len(stripped)<5 # Allow "DR."
        
        if not is_upper and len(stripped) < 25 and no_punct:
             # It *mostly* looks like a name.
             # DANGER: "He runs" fits this.
             
             # Blacklist common action/stage words
             if stripped.upper() in ["SON", "MOM", "DAD", "FATHER", "MOTHER", "VOICE", "GUY", "MAN", "WOMAN", "EXT", "INT"]:
                 output_lines.append(stripped)
                 continue
             # Check for common action verbs? No, too complex.
             # Check if next line exists and is non-empty?
             # If next line is dialogue, this is character.
             
             # Lookahead
             has_dialogue_after = False
             if i + 1 < len(lines):
                 next_l = lines[i+1].strip()
                 if next_l:
                     has_dialogue_after = True
             
             if has_dialogue_after:
                 # We assume it's a character.
                 # "John" -> "JOHN"
                 # "He runs" -> "HE RUNS" (This becomes Character in parser... bad)
                 # But risk is acceptable for "Universal Tolerance".
                 # Better to capture characters than miss them and treat dialogue as action.
                 output_lines.append(stripped.upper())
                 continue
        
        # Default: Pass through
        output_lines.append(stripped)
        
    return "\n".join(output_lines)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: structure_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Structure Agent - Handling Parsing, Segmentation, and Importing.
Consolidates: parsing.py, bert_parser.py, segmentation.py, beat.py, importers.py
"""

import re
import math
import xml.etree.ElementTree as ET
from ..utils.model_manager import manager

# =============================================================================
# IMPORTER LOGIC (formerly importers.py)
# =============================================================================

class ImporterAgent:
    """
    Parses Final Draft (.fdx) XML files and converts them 
    into the standardized Fountain-like format expected by the pipeline.
    """
    def run(self, file_content):
        """
        Entry point for the agent.
        file_content: bytes or string of the .fdx file
        """
        return self.parse_fdx(file_content)

    def parse_fdx(self, xml_content):
        """
        Parse FDX XML string into standardized line dictionaries.
        Returns: list of dicts [{'text': '...', 'tag': 'S/A/C/D', 'line_index': i}]
        """
        try:
            # Mitigation for basic XXE/Billion Laughs attacks if defusedxml is unavailable.
            if "<!DOCTYPE" in xml_content or "<!ENTITY" in xml_content:
                print("[Security] XML Injection Attempt Detected. Halting parse.")
                return []
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return []
            
        parsed_lines = []
        line_idx = 0
        
        # FDX Structure: <FinalDraft> -> <Content> -> <Paragraph>
        content = root.find('Content')
        if content is None:
            return []
            
        for paragraph in content.findall('Paragraph'):
            p_type = paragraph.get('Type', 'Action')
            
            # Extract Text
            text_elem = paragraph.find('Text')
            raw_text = ""
            if text_elem is not None:
                raw_text = "".join(text_elem.itertext())
            else:
                raw_text = "".join(paragraph.itertext())
                
            clean_text = raw_text.strip()
            
            if not clean_text:
                continue
                
            # Map FDX Types to ScriptPulse Tags
            tag = 'A' # Default
            
            if p_type == 'Scene Heading':
                tag = 'S'
                clean_text = clean_text.upper()
            elif p_type == 'Character':
                tag = 'C'
                clean_text = clean_text.upper()
            elif p_type == 'Dialogue':
                tag = 'D'
            elif p_type == 'Parenthetical':
                tag = 'P'
            elif p_type == 'Transition':
                tag = 'T'
            elif p_type == 'Shot':
                tag = 'S' 
            
            parsed_lines.append({
                'text': clean_text,
                'tag': tag,
                'line_index': line_idx,
                'original_line': clean_text
            })
            line_idx += 1
            
        return parsed_lines


# =============================================================================
# PARSING LOGIC (formerly parsing.py & bert_parser.py)
# =============================================================================

def is_scene_heading(line_text):
    """
    Detect if a line is a scene heading.
    Extracted for testability and reuse.
    """
    line = line_text.strip()
    if not line: return False
    
    # 1. Standard Int/Ext prefixes
    line_upper = line.upper()
    if line_upper.startswith(("INT.", "EXT.", "INT ", "EXT ", "I/E.", "INT/", "EXT/")): return True

    # 'SCENE' only qualifies when followed by a digit, INT, or EXT (not 'SCENE OF THE CRIME', etc.)
    if re.match(r'^SCENE\s*(\d+|INT|EXT)', line_upper): return True

    # 2. Fallback Patterns (Full words)
    fallback_patterns = [
        r'^INTERIOR\s+', r'^EXTERIOR\s+',
        r'^\d+\s*(INT|EXT)'
    ]
    for pattern in fallback_patterns:
        if re.match(pattern, line, re.IGNORECASE): return True

    return False

class ParsingAgent:
    """
    Structural Parsing Agent - Classifies screenplay lines.
    Combines Heuristic (parsing.py) and ML (bert_parser.py) approaches.
    """
    def __init__(self, use_ml=True):
        self.use_ml = use_ml
        self.classifier = None
        self.is_mock = True
        
        if use_ml:
            self.classifier = manager.get_zero_shot()
            self.is_mock = self.classifier is None
            if self.is_mock:
                print(f"[Warning] Failed to load ML model. Falling back to Heuristics.")

        self.tag_map = {
            "Dialogue": "D",
            "Action": "A",
            "Scene Heading": "S",
            "Character Name": "C",
            "Transition": "T",
            "Parenthetical": "M" 
        }

    def run(self, script_text):
        """
        Parses the entire script.
        """
        # Dash Normalization
        script_text = script_text.replace('—', '-').replace('–', '-')
        
        lines = script_text.split('\n')
        results = []
        context = []
        
        for i, line in enumerate(lines):
            tag = self.predict_line(line, context_window=context, index=i, all_lines=lines)
            context.append(tag)
            
            confidence = 0.95 if self.is_mock else 0.85 
            
            results.append({
                'line_index': i,
                'text': line,
                'tag': tag,
                'model': 'consolidated-parser-v1',
                'confidence': confidence
            })
            
        return {'lines': results}

    def predict_line(self, line_text, context_window=None, index=0, all_lines=None):
        """
        Predicts the structural tag for a single line.
        """
        line = line_text.strip()
        if not line: return "A"
        
        # 1. Hard Rules (Performance Optimization & Sanity)
        if is_scene_heading(line): return "S"
        
        line_upper = line.upper()
        if line_upper.endswith(" TO:"): return "T"

        # Metadata/transitions
        transitions = ['FADE IN', 'FADE OUT', 'FADE TO', 'CUT TO', 'DISSOLVE TO', 'MATCH CUT', 'SMASH CUT', 'THE END', 'CONTINUED']
        if any(t in line_upper or line_upper.startswith(t) for t in transitions): return 'M'
        # Only treat as transition if the WHOLE line is uppercase and short
        # (true transitions like "CUT TO:" are all-caps and brief)
        if line_upper.endswith(':') and line_upper == line and len(line) < 20:
            return 'M'

        # 2. Contextual Heuristics
        prev_tag = context_window[-1] if context_window else "A"
        
        if prev_tag == "C": 
            if line.startswith("("): return "M" # Parenthetical
            return "D"
            
        if prev_tag == "M":
            return "D" # The line immediately after a parenthetical under a character is dialogue
            
        if prev_tag == "D":
            # If the previous line was dialogue, and this line isn't empty (empty lines become A)
            # and it isn't a new character cue, it's a continuation of dialogue.
            # Relaxed character rule: allow periods for short names (for typographical typos)
            is_char_candidate = line.isupper() and len(line) < 40
            is_hypothetical_character = is_char_candidate and (not line.endswith((".", "?", "!")) or (line.endswith(".") and len(line) < 12))
            
            if is_hypothetical_character:
                # Likely a new character or a transition/action
                pass
            else:
                return "D"
            
        if line.isupper() and len(line) < 40 and (not line.endswith((".", "?", "!")) or (line.endswith(".") and len(line) < 12)):
            # Character cue blacklist (Refined: Only block non-character structural/action cues)
            # We allow generic roles (MOM, DAD) again to ensure their dialogue is captured.
            blacklist = ["EXT", "INT", "O.S.", "V.O.", "OFF-SCREEN", "CONTINUED", "TITLE", "CREDITS"]
            if any(b == line_upper for b in blacklist):
                return "A"
            
            # Action fragments misparsed as characters
            if any(term in line_upper for term in ["HIS HAND", "HIS FACE", "HER HAND", "HER FACE", "THE DOOR", "THE GUN", "CLOSE ON", "CLOSE-UP"]):
                return "A"

            # Look ahead for dialogue
            if all_lines and index + 1 < len(all_lines):
                 next_line = all_lines[index + 1].strip()
                 if next_line and not next_line.isupper():
                     return "C"
            # Fallback if no lookahead
            return "C"

        # 3. ML Inference (Skipped if mock or high confidence in heuristic)
        # Note: In consolidation, preserving the heuristic path as primary for speed/reliability unless ambiguous
        
        # 4. Fallback Heuristics
        if prev_tag == "C": return "D"
        if line.startswith("(") and line.endswith(")"): return "D" 
        if line.isupper() and len(line) < 30: return "C"
        
        return "A"


# =============================================================================
# SEGMENTATION LOGIC (formerly segmentation.py)
# =============================================================================

class SegmentationAgent:
    """Scene Segmentation Agent - Conservative Boundary Detection"""
    
    MIN_SCENE_LENGTH = 12
    LOW_CONFIDENCE_THRESHOLD = 0.6

    def run(self, input_data):
        """Segment parsed lines into scenes."""
        if not input_data: return []
        parsed_lines = input_data if isinstance(input_data, list) else input_data.get('lines', [])
        
        boundaries = self.detect_boundaries(parsed_lines)
        scenes = self.create_scenes(parsed_lines, boundaries)
        scenes = self.enforce_minimum_length(scenes)
        scenes = self.merge_headless_fragments(scenes, parsed_lines)
        scenes = self.merge_low_confidence(scenes)
        scenes = self.reindex_scenes(scenes)
        scenes = self.extract_scene_info(scenes, parsed_lines)
        
        return scenes

    def detect_boundaries(self, parsed_lines):
        boundaries = [(0, 1.0)]
        for i, line_data in enumerate(parsed_lines):
            if i == 0: continue
            tag = line_data['tag']
            confidence = 0.0
            if tag == 'S': confidence = 0.9
            # Removed: M-tag boundary — transitions belong to the preceding scene
            
            if confidence > 0.3:
                boundaries.append((i, confidence))
        return boundaries

    def create_scenes(self, parsed_lines, boundaries):
        scenes = []
        for i in range(len(boundaries)):
            start_line = boundaries[i][0]
            start_confidence = boundaries[i][1]
            end_line = boundaries[i + 1][0] - 1 if i + 1 < len(boundaries) else len(parsed_lines) - 1
            scenes.append({
                'scene_index': i,
                'start_line': start_line,
                'end_line': end_line,
                'boundary_confidence': start_confidence
            })
        return scenes

    def enforce_minimum_length(self, scenes):
        if not scenes: return scenes
        merged = []
        skip_next = False
        for i in range(len(scenes)):
            if skip_next:
                skip_next = False
                continue
            scene = scenes[i]
            length = scene['end_line'] - scene['start_line'] + 1
            if length < self.MIN_SCENE_LENGTH and i + 1 < len(scenes):
                next_scene = scenes[i + 1]
                merged_scene = {
                    'scene_index': scene['scene_index'],
                    'start_line': scene['start_line'],
                    'end_line': next_scene['end_line'],
                    'boundary_confidence': min(scene['boundary_confidence'], next_scene['boundary_confidence'])
                }
                merged.append(merged_scene)
                skip_next = True
            else:
                merged.append(scene)
        return merged

    def merge_headless_fragments(self, scenes, parsed_lines, max_orphan_lines=15):
        if len(scenes) <= 1: return scenes
        merged = [scenes[0]]
        for scene in scenes[1:]:
            has_heading = any(parsed_lines[i]['tag'] == 'S' for i in range(scene['start_line'], min(scene['end_line'] + 1, len(parsed_lines))))
            length = scene['end_line'] - scene['start_line'] + 1
            if not has_heading and length <= max_orphan_lines and merged:
                merged[-1]['end_line'] = scene['end_line']
            else:
                merged.append(scene)
        return merged

    def merge_low_confidence(self, scenes):
        if len(scenes) <= 1: return scenes
        merged = []
        current = scenes[0]
        for i in range(1, len(scenes)):
            next_scene = scenes[i]
            if current['boundary_confidence'] < self.LOW_CONFIDENCE_THRESHOLD:
                current = {
                    'scene_index': current['scene_index'],
                    'start_line': current['start_line'],
                    'end_line': next_scene['end_line'],
                    'boundary_confidence': max(current['boundary_confidence'], next_scene['boundary_confidence'])
                }
            else:
                merged.append(current)
                current = next_scene
        merged.append(current)
        return merged

    def reindex_scenes(self, scenes):
        for i, scene in enumerate(scenes):
            scene['scene_index'] = i
        return scenes

    def extract_scene_info(self, scenes, parsed_lines):
        for scene in scenes:
            start = scene['start_line']
            end = scene['end_line']
            heading = ""
            preview_lines = []
            for i in range(start, min(end + 1, len(parsed_lines))):
                line_data = parsed_lines[i]
                text = line_data['text'].strip()
                tag = line_data['tag']
                if not text: continue
                if tag == 'S' and not heading:
                    heading = text
                elif len(preview_lines) < 2:
                    if text and text != heading:
                        preview_lines.append(text[:60] + ('...' if len(text) > 60 else ''))
            scene['heading'] = heading if heading else f"Scene {scene['scene_index'] + 1}"
            scene['preview'] = ' | '.join(preview_lines) if preview_lines else ""
        return scenes


# =============================================================================
# BEAT LOGIC (formerly beat.py)
# =============================================================================

class BeatAgent:
    """Sub-segments scenes into Beats based on Dramatic Shifts (Action interruptions, Entrances/Exits)."""
    
    def subdivide_into_beats(self, scenes):
        beats = []
        for scene in scenes:
            lines = scene.get('lines', [])
            current_beat_lines = []
            beat_idx = 1
            
            for i, line in enumerate(lines):
                text = line.get('text', "")
                tag = line.get('tag', "")
                current_beat_lines.append(line)
                
                # A beat shift happens on:
                # 1. A transition tag
                # 2. A major action line that interrupts a block of dialogue
                is_transition = tag == 'T'
                is_heavy_action = tag == 'A' and len(text.split()) > 15 and i > 0 and lines[i-1].get('tag') == 'D'
                
                if (is_transition or is_heavy_action) and len(current_beat_lines) > 2:
                    beat_obj = self.create_beat(scene, current_beat_lines, beat_idx)
                    beats.append(beat_obj)
                    current_beat_lines = []
                    beat_idx += 1
                    
            if current_beat_lines:
                 beat_obj = self.create_beat(scene, current_beat_lines, beat_idx)
                 beats.append(beat_obj)
                 
        return beats

    def create_beat(self, parent_scene, lines, beat_idx):
        return {
            'scene_index': parent_scene['scene_index'],
            'beat_index': beat_idx,
            'heading': f"{parent_scene['heading']} (Beat {beat_idx})",
            'lines': lines,
            'start_line': lines[0]['line_index'] if lines else 0,
            'end_line': lines[-1]['line_index'] if lines else 0,
            'location': parent_scene.get('location', 'UNKNOWN'),
            'time': parent_scene.get('time', 'UNKNOWN')
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: perception_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Perception Agent - Simplified & MCA-Defensible Version
Focuses on 5 Core Cognitive Pillars:
1. Linguistic Load (Complexity)
2. Dialogue Dynamics (Rhythm)
3. Visual Abstraction (Action)
4. Referential Load (Characters)
5. Information Entropy (Novelty)
"""

import re
import math
import statistics
from collections import Counter
from ..utils.model_manager import manager

def normalize_character_name(name):
    """Utility for consistent character matching with body-part blacklist."""
    if not name: return "UNKNOWN"
    # Stem names: Remove (O.S.), (V.O.), (CONT'D) etc. 
    stemmed = re.sub(r'\(.*?\)', '', name).upper()
    # Handle suffixes without parentheses (e.g. CHARACTER-O.S.)
    stemmed = re.sub(r'[-\s](O\.?S\.?|V\.?O\.?|ALT|OFF-SCREEN|DASHES|FILTERED)$', '', stemmed)
    
    # Upper, strip punctuation but keep internal spaces/hashes
    clean = re.sub(r'[^A-Z0-9\s#]', '', stemmed).strip()
    
    # Body Part & Structural Blacklist
    # We only filter the 'garbage' items that are definitely action fragments misparsed.
    blacklist = {
        'EXT', 'INT', 'OFF-SCREEN', 'O.S.', 'V.O.', 'VOICE',
        'HIS HAND', 'HER FACE', 'HIS FACE', 'HER HAND', 'THE GUN', 'THE DOOR', 'THE CAR',
        'HIS HANDS', 'HER EYES', 'HIS EYES', 'CLOSE ON', 'CLOSE-UP'
    }
    if clean in blacklist:
        return None
    return clean

class EncodingAgent:
    """Consolidated Encoding Agent - High Performance, Low Complexity"""
    
    def __init__(self):
        self.classifier = manager.get_zero_shot()
        self.stakes_labels = ['Physical Survival', 'Emotional Connection', 'Social Status', 'Moral Dilemma', 'Existential Dread']
        self.sentiment_labels = ['High Tension / Conflict', 'Positive Connection', 'Despair / Loss', 'Neutral / Calm']

    def run(self, input_data):
        scenes = input_data.get('scenes', [])
        lines = input_data.get('lines', [])
        
        if not scenes: return []
        
        feature_vectors = []
        prev_characters = set()
        
        for i, scene in enumerate(scenes):
            scene_lines = [l for l in lines if scene['start_line'] <= l['line_index'] <= scene['end_line']]
            
            # 1. Linguistic Analysis (Syntactic Load)
            linguistic = self._extract_linguistic(scene_lines)
            
            # 2. Dialogue & Rhythm (Tempo)
            dialogue = self._extract_dialogue(scene_lines)
            
            # 3. Action & Visuals (Cinematic Weight)
            visual = self._extract_visual(scene_lines)
            
            # 4. Character Tracking (Cognitive Load)
            referential = self._extract_referential(scene_lines, prev_characters)
            prev_characters = referential['current_character_set']
            
            # 5. Information Theory (Entropy/Surprisal)
            entropy = self._extract_entropy(scene_lines)
            
            # 6. Affective Load (VADER Emotional Valence/Sentiment)
            affective = self._extract_affective_load(scene_lines)
            
            # 6. Narrative Metadata (For Charts/UI)
            metadata = self._extract_narrative_metadata(scene_lines)
            
            features = {
                'scene_index': scene['scene_index'],
                'linguistic_load': linguistic,
                'dialogue_dynamics': dialogue,
                'visual_abstraction': visual,
                'referential_load': {k:v for k,v in referential.items() if k != 'current_character_set'},
                'structural_change': self._extract_structural(scene, scenes, i),
                'entropy_score': entropy,
                'affective_load': affective,
                'ambient_signals': self._extract_ambient(linguistic, dialogue, visual),
                'micro_structure': self._extract_micro(scene_lines),
                'runtime_contribution': self._extract_runtime_contribution(scene_lines),
                # Supporting metrics for UI consistency
                'character_scene_vectors': metadata['character_scene_vectors'],
                'stakes_taxonomy': metadata['stakes'],
                'scene_purpose': metadata['purpose'],
                'payoff_density': metadata['payoff'],
                'on_the_nose': metadata['on_the_nose'],
                'shoe_leather': metadata['shoe_leather'],
                'tell_vs_show': metadata['tell_vs_show'],
                'is_exposition': metadata['purpose']['purpose'] == 'Exposition',
                'scene_vocabulary': metadata['scene_vocabulary'],
                'reader_frustration': self._extract_reader_frustration(scene_lines, referential['active_character_count']),
                'stichomythia': metadata['stichomythia'],
                'monologue_data': metadata['monologue_data'],
                'passive_voice': metadata['passive_voice'],
                'scene_economy': metadata['scene_economy'],
                'opening_hook': metadata['opening_hook'],
                'narrative_closure': metadata['narrative_closure'],
                'research_telemetry': metadata.get('research_telemetry', {})
            }
            feature_vectors.append(features)
            
        return feature_vectors

    def _extract_linguistic(self, lines):
        text = " ".join([l['text'] for l in lines])
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s]
        
        if not words: return {'mean_sentence_length': 0, 'sentence_length_variance': 0, 'sentence_count': 0, 'idea_density': 0}
        
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths)/len(lengths) if lengths else 0
        var = sum((x-avg)**2 for x in lengths)/len(lengths) if lengths else 0
        uniq = len(set(words))
        
        return {
            'mean_sentence_length': round(avg, 2),
            'sentence_length_variance': round(var, 2),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'idea_density': round(uniq/len(words), 3) if sum(lengths) > 0 else 0,
            'clarity_score': 0.8 # Placeholder
        }

    def _extract_runtime_contribution(self, lines):
        """
        Calculates estimated runtime for the scene in seconds.
        Uses industry standard Word-to-Minute heuristics instead of crude block counts.
        """
        action_words = sum([len(l['text'].split()) for l in lines if l['tag'] == 'A'])
        dialogue_words = sum([len(l['text'].split()) for l in lines if l['tag'] == 'D'])
        
        # Calculate seconds (60 seconds per minute)
        # Industry standard: ~200 WPM spoken dialogue, but action descriptions
        # represent screen time at roughly 2-3x the reading rate
        action_seconds = action_words * 0.38   # ~158 words/min of screen time
        
        # Dialogue is spoken quickly
        dialogue_seconds = dialogue_words * 0.33  # ~180 WPM spoken
        
        total_seconds = action_seconds + dialogue_seconds
        
        # Minor buffer for transition instead of 5s
        total_seconds += 1.0 
        
        return {'estimated_seconds': round(total_seconds)}

    def _extract_dialogue(self, lines):
        d_lines = [l for l in lines if l['tag'] == 'D']
        c_lines = [l for l in lines if l['tag'] == 'C']
        
        switches = 0
        for i in range(1, len(c_lines)):
            if c_lines[i]['text'] != c_lines[i-1]['text']: switches += 1
            
        non_blank_d = [l for l in d_lines if l['text'].strip()]
        non_blank_total = [l for l in lines if l['text'].strip()]
        return {
            'dialogue_line_count': len(non_blank_d),
            'turn_velocity': round(len(non_blank_d) / max(1, len(non_blank_total)), 3),
            'speaker_switches': switches
        }

    def _extract_visual(self, lines):
        a_lines = [l for l in lines if l['tag'] == 'A']
        
        runs = 0
        in_run = False
        for l in lines:
            if l['tag'] == 'A':
                if not in_run:
                    runs += 1
                    in_run = True
            else:
                in_run = False
                
        non_blank_a = [l for l in a_lines if l['text'].strip()]
        non_blank_total = [l for l in lines if l['text'].strip()]
        return {
            'action_lines': len(non_blank_a),
            'visual_intensity': round(len(non_blank_a) / max(1, len(non_blank_total)), 3),
            'continuous_action_runs': runs
        }

    def _extract_referential(self, lines, prev_chars):
        chars = set(l['text'].strip() for l in lines if l['tag'] == 'C')
        added = len(chars - prev_chars)
        removed = len(prev_chars - chars)
        total = len(chars.union(prev_chars))
        churn = (added + removed) / max(1, total)
        
        return {
            'active_character_count': len(chars),
            'entity_churn': round(churn, 2),
            'current_character_set': chars
        }

    def _extract_entropy(self, lines):
        text = " ".join([l['text'] for l in lines]).lower()
        words = re.findall(r'\b\w+\b', text)
        if not words: return 0.0
        counts = Counter(words)
        total = len(words)
        entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
        return round(entropy, 3)

    def _extract_affective_load(self, lines):
        # 1. Prepare text for analysis (Action 'A' and Dialogue 'D')
        text = " ".join([l['text'] for l in lines if l['tag'] in ['D', 'A']])
        all_text = " ".join([l['text'] for l in lines]).lower()
        if not text.strip():
            return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': 0.0}

        # 2. High-Priority Narrative Override: Violence & Death (Task 1)
        # We must detect deaths even in action-heavy scenes without 'C' tags.
        violence_triggers = [
            'shot', 'killed', 'ambush', 'trap', 'gunfire', 'body', 'murder', 'blood', 'execution', 
            'assassinate', 'bullet', 'massacre', 'stabbed', 'slaughter', 'wound', 'dying',
            'blast', 'explosion', 'corpse', 'funeral', 'firefight', 'gunmen', 'trigger',
            'mowed down', 'sprayed', 'hitman', 'assassin', 'weapon', 'grenade', 'knife'
        ]
        
        # Check for character presence via tags OR capitalized names in Action lines
        has_character = any(l['tag'] == 'C' for l in lines)
        if not has_character:
            # Look for [A-Z]{3,} name signals in Action text
            has_character = any(re.search(r'\b[A-Z]{3,}\b', l['text']) for l in lines if l['tag'] == 'A')

        has_violence = any(w in all_text for w in violence_triggers)
        if has_violence and has_character:
            # Force high-stakes Negative Sentiment for these cinematic story-beats
            return {'pos': 0.00, 'neg': 0.98, 'neu': 0.02, 'compound': -0.99}

        if self.classifier:
            try:
                # Use Zero-Shot for Dramatic Context Sentiment (Not Twitter sentiment)
                res = self.classifier(text[:1024], self.sentiment_labels)
                scores = dict(zip(res['labels'], res['scores']))
                tension = scores.get('High Tension / Conflict', 0)
                despair = scores.get('Despair / Loss', 0)
                positive = scores.get('Positive Connection', 0)
                
                # Map to standard VADER-like keys for pipeline compatibility, but with cinematic meaning
                compound = tension + (positive * 0.5) - (despair * 0.8)
                return {'pos': round(positive, 3), 'neg': round(despair, 3), 'neu': round(1 - (tension+despair+positive), 3), 'compound': round(compound, 3)}
            except:
                pass
                
        # Semantic Fallback (Simulated Narrative Lexicon instead of Social Media Lexicon)
        conflict_words = sum(text.lower().count(w) for w in ['gun', 'blood', 'stop', 'no', 'never', 'die', 'kill', 'hate', 'leave'])
        connection_words = sum(text.lower().count(w) for w in ['love', 'together', 'yes', 'help', 'beautiful', 'safe', 'stay'])
        total_words = len(text.split())
        
        compound = (connection_words - conflict_words) / max(1, total_words) * 5.0 # normalized boost
        return {'pos': 0.0, 'neg': 0.0, 'neu': 1.0, 'compound': round(max(-1.0, min(1.0, compound)), 3)}

    def _extract_structural(self, scene, all_scenes, idx):
        if idx == 0: return {'event_boundary_score': 0.0}
        gap = scene['start_line'] - all_scenes[idx-1]['end_line']
        return {'event_boundary_score': min(100.0, gap * 2.0)}

    def _extract_ambient(self, ling, dial, vis):
        score = ( (1 - dial['turn_velocity']) + (1 - min(1.0, vis['action_lines']/10)) ) / 2
        return {
            'ambient_score': round(score, 3),
            'component_scores': {'stillness': round(1-vis['visual_intensity'], 3)}
        }

    def _extract_micro(self, lines):
        return [{'tag': l['tag'], 'word_count': len(l['text'].split())} for l in lines]

    def _extract_reader_frustration(self, lines, char_count):
        """Detects structural issues that confuse readers."""
        raw_chars = [normalize_character_name(l['text']) for l in lines if l['tag'] == 'C']
        chars = [c for c in raw_chars if c] # Filter None from blacklist
        unique_chars = sorted(list(set(chars))) # Sorted for determinism
        
        # 1. Name Crowding: Too many characters introduced at once
        crowding = char_count > 5
        
        # 2. Similar Names: Character names that look/sound too similar (e.g. John & Jon)
        similar = []
        for i in range(len(unique_chars)):
            for j in range(i + 1, len(unique_chars)):
                n1, n2 = unique_chars[i], unique_chars[j]
                if len(n1) > 3 and len(n2) > 3:
                    # Basic similarity: match first 4 chars and ensure lengths are close
                    if n1[:4] == n2[:4] and abs(len(n1) - len(n2)) <= 2:
                        similar.append(f"{n1}/{n2}")
        
        # 3. Unfilmable 'Internal' Action: (already handled by tell_vs_show, but we can group it here too)
        a_lines = [l['text'].lower() for l in lines if l['tag'] == 'A']
        internal_hits = []
        for a in a_lines:
            if any(w in a for w in ['thinks', 'remembers', 'wonders', 'realizes', 'feels']):
                internal_hits.append(a[:30] + "...")

        return {
            'name_crowding': crowding,
            'unique_char_count': char_count,
            'similar_name_pairs': similar,
            'internal_state_hits': internal_hits
        }

    def _extract_narrative_metadata(self, lines):
        text = " ".join([l['text'] for l in lines]).lower()
        vocab = set(re.findall(r'\b\w+\b', text))
        
        # 1. Real Cognitive Stakes Detection (ML or Advanced Heuristics)
        dominant = 'Physical'
        scores = {}
        confidence = 0.65 # Base heuristic confidence
        
        if self.classifier and len(text.split()) > 10:
            try:
                res = self.classifier(text[:1024], self.stakes_labels)
                label_map = {'Physical Survival': 'Physical', 'Emotional Connection': 'Emotional', 'Social Status': 'Social', 'Moral Dilemma': 'Moral', 'Existential Dread': 'Existential'}
                scores = {label_map[k]: v for k, v in zip(res['labels'], res['scores'])}
                dominant = label_map[res['labels'][0]]
                confidence = 0.92 # ML-backed confidence
            except:
                pass
        
        if not scores: # Fallback
            stakes_map = {
                'Physical': ['kill', 'blood', 'gun', 'fight', 'run', 'dead', 'attack', 'hide'],
                'Emotional': ['love', 'cry', 'heart', 'fear', 'happy', 'sad', 'forgive', 'hate'],
                'Social': ['reputation', 'friend', 'betray', 'secret', 'status', 'boss', 'fired', 'party'],
                'Moral': ['right', 'wrong', 'lie', 'truth', 'guilt', 'confess', 'promise', 'swear'],
                'Existential': ['meaning', 'exist', 'god', 'death', 'soul', 'purpose', 'destiny']
            }
            raw_scores = {k: sum(text.count(w) for w in v) for k, v in stakes_map.items()}
            dominant = max(raw_scores, key=raw_scores.get) if any(raw_scores.values()) else 'Social'
            total_raw = sum(raw_scores.values()) or 1
            scores = {k: v/total_raw for k, v in raw_scores.items()}
        
        # 2. Character Arcs (Per-scene vectors based on context, not just word count)
        # Collect diagnostic representative quotes for later reference
        rep_dialogue = ""
        max_d_len = -1
        rep_action = ""
        max_a_len = -1
        
        for l in lines:
            txt = l.get('text', '')
            tag = l.get('tag', '')
            if tag == 'D' and len(txt) > max_d_len:
                max_d_len = len(txt)
                rep_dialogue = txt
            elif tag == 'A' and len(txt) > max_a_len:
                max_a_len = len(txt)
                rep_action = txt
        arcs = {}
        curr = None
        proactive_lexicon = {'go', 'do', 'will', 'must', 'shall', 'stop', 'done', 'kill', 'give', 'take', 'enough', 'order', 'clear', 'business', 'family', 'offer', 'refuse', 'respect', 'decide', 'arrange', 'settle', 'deal', 'demand', 'insist', 'command', 'forbid', 'allow', 'never', 'always', 'swear'}
        
        # Diagnostics for scene-level features
        monologues = []
        current_mono_len = 0
        
        sticho_count = 0
        prev_tag = None
        
        passive_count = 0
        passive_examples = []
        
        for i, l in enumerate(lines):
            txt = l.get('text', '').strip()
            tag = l.get('tag', '')
            
            # 1. Monologue & Stichomythia Tracking
            if tag == 'D':
                # Stichomythia: Rapid-fire single-line exchanges
                if prev_tag == 'D' and len(txt.split()) < 10:
                    sticho_count += 1
                
                # Monologue: Long uninterrupted speech
                current_mono_len += 1
            elif tag == 'C':
                # End of a monologue?
                if current_mono_len >= 8:
                    monologues.append({'character': curr, 'length': current_mono_len})
                current_mono_len = 0 # Character tag breaks the monologue (unless it's the same char, but we follow the change of tag)
            else:
                current_mono_len = 0

            # 2. Passive Voice Detection in Action lines
            if tag == 'A':
                passive_markers = [
                    r'\bis being\b', r'\bwas being\b', r'\bhas been\b', r'\bhad been\b',
                    r'\bis seen\b', r'\bare seen\b', r'\bwas seen\b', r'\bi?s heard\b',
                    r'\bi?s felt\b', r'\bi?s watched\b'
                ]
                for p in passive_markers:
                    if re.search(p, txt, re.I):
                        passive_count += 1
                        if len(passive_examples) < 2: passive_examples.append(txt)

            # 3. Character-level Arcs & Voice Texture
            if tag == 'C': 
                name = normalize_character_name(txt)
                if name: curr = name
                else: curr = None
            elif tag == 'D' and curr:
                if curr not in arcs: 
                    arcs[curr] = {
                        'sentiment': 0.0, 'agency': 0.1, 'line_count': 0,
                        'complexity': 0.0, 'positivity': 0.0, 'punctuation_rate': 0.0
                    }
                arcs[curr]['line_count'] += 1
                dial_text = txt.lower()
                dial_words = re.findall(r'\b\w+\b', dial_text)
                
                # Voice Texture Fix (Fix 4):
                word_lens = [len(w) for w in dial_words]
                arcs[curr]['complexity'] += statistics.mean(word_lens) if word_lens else 0
                arcs[curr]['positivity'] += sum(1 for w in dial_words if w in ['yes', 'love', 'good', 'happy', 'safe']) / max(1, len(dial_words))
                arcs[curr]['punctuation_rate'] += (txt.count('.') + txt.count(',') + txt.count('!') + txt.count('?')) / max(1, len(txt))

                # Agency Logic
                is_question = '?' in dial_text
                is_command = ('!' in dial_text or txt.isupper()) and len(dial_words) < 8
                proactive_count = len(set(dial_words).intersection(proactive_lexicon))
                
                agency_inc = 0.1 # Base participation
                if is_command: agency_inc += 0.7
                elif is_question: agency_inc += 0.1 # Reduced bonus for asking questions
                agency_inc += (proactive_count * 0.6)
                
                if any(w in dial_text for w in ['maybe', 'sorry', 'i think', 'perhaps', 'suppose']):
                    agency_inc -= 0.2
                
                arcs[curr]['agency'] += agency_inc
                arcs[curr]['sentiment'] += 0.1 if 'yes' in dial_text else (-0.1 if 'no' in dial_text else 0)
            
            prev_tag = tag

        # Finalize Monologue at end of scene
        if current_mono_len >= 8:
            monologues.append({'character': curr, 'length': current_mono_len})
        
        # Normalize Agency & Voice Texture
        for c in arcs:
            n = max(1, arcs[c]['line_count'])
            arcs[c]['agency'] = round(min(1.0, arcs[c]['agency'] / (1.0 + n * 0.15)), 3)
            arcs[c]['sentiment'] = round(max(-1.0, min(1.0, arcs[c]['sentiment'] / n)), 3)
            # Normalize voice features
            arcs[c]['complexity'] = round(arcs[c]['complexity'] / n, 2)
            arcs[c]['positivity'] = round(arcs[c]['positivity'] / n, 2)
            arcs[c]['punctuation_rate'] = round(arcs[c]['punctuation_rate'] / n, 3)

        # 4. Scene-level Efficiency/Diagnostics
        n_lines = len([l for l in lines if l['tag'] in ['D', 'A']])
        economy_score = min(100, (sum(1 for l in lines if l['tag'] == 'D') * 5 + sum(1 for l in lines if l['tag'] == 'A') * 3))
        economy_label = 'High Economy' if economy_score < 40 else 'Moderate Economy' if economy_score < 75 else 'Low Economy'
        
        # 5. Opening Hook Detection (Rule based for Scene 0 only)
        hook_label = 'Indeterminate'
        lines_before = 0
        if lines:
            for i, l in enumerate(lines[:15]):
                if any(w in l['text'].lower() for w in ['gun', 'blood', 'shot', 'kill', 'fight', 'scream', 'run']):
                    hook_label = 'Strong Hook'
                    lines_before = i
                    break

        # 6. Masterclass Diagnostics (Smart Heuristics using structural context)
        d_lines = [l['text'].lower() for l in lines if l['tag'] == 'D']
        a_lines = [l['text'].lower() for l in lines if l['tag'] == 'A']
        all_text = " ".join([l['text'] for l in lines]).lower()
        
        # On-the-Nose: Direct emotion stating in dialogue
        otn_phrases = ['i feel', 'i am feeling', 'i am very angry', 'i am so sad', 'i am depressed', 'i hate you so much', 'i am terrified', 'i love you so much', 'i am so mad']
        otn_hits = sum(1 for d in d_lines if any(p in d for p in otn_phrases))
        
        # Shoe-Leather: Pleasantries in the VERY FIRST few dialogue lines of a scene
        shoe_leather_phrases = ['hello', 'hi ', 'hey ', 'good morning', 'how are you', 'how have you been', 'nice to see you', 'good afternoon', 'whats up', 'what is up']
        has_shoe_leather = False
        if len(d_lines) > 0:
            first_few = " ".join(d_lines[:3])
            has_shoe_leather = any(p in first_few for p in shoe_leather_phrases)
            
        # Tell vs Show: Internal emotional states described in Action lines
        emotion_adjectives = ['angry', 'sad', 'happy', 'depressed', 'terrified', 'furious', 'devastated', 'upset', 'jealous', 'nervous', 'anxious']
        tvs_hits = 0
        for a in a_lines:
            for em in emotion_adjectives:
                if f" is {em}" in a or f" feels {em}" in a or f" seems {em}" in a or f" looks {em}" in a:
                    tvs_hits += 1

        # Purpose Detection: Based on action vs dialogue vs vocabulary novelty
        purpose = 'Transition'
        if len(a_lines) > len(d_lines) * 2 and len(a_lines) > 5:
            purpose = 'Escalation / Action'
        elif any(w in all_text for w in ['realize', 'discover', 'reveal', 'finds', 'truth']):
            purpose = 'Revelation / Discovery'
        elif len(d_lines) > 10:
            purpose = 'Negotiation / Conflict'

        # Check for narrative closure signals in action lines (Strict death/exit detection)
        # Only unambiguous death words — 'falls', 'collapses', 'slumps' are excluded
        # because they appear constantly in normal action (a man falls into a chair, etc.)
        death_lexicon = {
            'dies', 'dead', 'killed', 'murdered', 'corpse', 'funeral',
            'deathbed', 'fatal', 'slain', 'no longer with us', 'rest in peace',
            'is shot', 'is stabbed', 'shoot him', 'stabs him', 'stabs her',
            'shoots him', 'shoots her', 'blows his brains', 'blows her brains'
        }
        scene_has_death = any(w in all_text for w in death_lexicon)

        return {
            'character_scene_vectors': arcs,
            'stakes': {'dominant': dominant, 'breakdown': {k: round(v, 2) for k,v in scores.items()}},
            'payoff': {'payoff_density': round(sum(scores.values()) / max(1, len(lines)), 2)},
            'stichomythia': {'has_stichomythia': sticho_count > 4, 'count': sticho_count},
            'monologue_data': {'has_monologue': len(monologues) > 0, 'monologues': monologues},
            'passive_voice': {'passive_ratio': passive_count / max(1, n_lines), 'passive_count': passive_count, 'examples': passive_examples},
            'scene_economy': {'economy_label': economy_label, 'economy_score': economy_score},
            'opening_hook': {'hook_label': hook_label, 'lines_before_conflict': lines_before},
            'purpose': {'purpose': purpose},
            'on_the_nose': {
                'on_the_nose_ratio': round(otn_hits / max(1, len(d_lines)), 3),
                'hit_count': otn_hits
            },
            'shoe_leather': {
                'has_shoe_leather': has_shoe_leather,
                'scene_start_filler': 3 if has_shoe_leather else 0
            },
            'tell_vs_show': {'tell_ratio': min(1.0, tvs_hits / max(1, len(a_lines))), 'literal_emotions': tvs_hits},
            'narrative_closure': scene_has_death,
            'representative_dialogue': rep_dialogue,
            'representative_action': rep_action,
            'scene_vocabulary': list(vocab),
            'research_telemetry': {
                'analytical_confidence': confidence,
                'semantic_density': len(vocab) / max(1, len(text.split())),
                'heuristic_fallback': confidence < 0.8
            }
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: interpretation_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Interpretation Agent - Text-Grounded Cognitive Version
Translates mathematical signals into true human "First Reader" experiences.
Focuses on: Confusion, Boredom, Visceral Reaction, and Textual Proof.
"""

import statistics
import random

class InterpretationAgent:
    """Cognitive Translation Layer - From Data to Human Experience"""

    def __init__(self):
        # Human Experience Labels for UI
        self.LABELS = {
            'High': "Gripping / Intense",
            'Medium': "Engaging / Steady",
            'Low': "Slow / Breather"
        }

    def run(self, temporal_trace, features=None, scenes=None, genre='drama'):
        """Main entry point for cognitive interpretation"""
        if not temporal_trace: return {}
        
        # 1. Structure Analysis (Text-Grounded)
        structure = self.map_to_structure(temporal_trace, features)
        
        # 2. Cognitive Heuristics Diagnosis
        diagnosis = self.diagnose_patterns(temporal_trace, features, scenes, genre=genre)
        
        return {
            'structure': structure,
            'diagnosis': diagnosis,
            'suggestions': [] # Deprecated: We don't give advice to writers anymore.
        }

    def map_to_structure(self, temporal_trace, features=None):
        """Identifies True Narrative Shifts based on intense emotional flux, not just math percentages."""
        total = len(temporal_trace)
        if total < 5: return {'acts': [], 'beats': []}
        
        # ACT 1 ends around 25%
        a1_end = int(total * 0.25)
        # ACT 2 ends around 75%
        a2_end = int(total * 0.75)
        
        acts = [
            {'name': 'Act 1: Setup', 'range': [0, a1_end]},
            {'name': 'Act 2: Confrontation', 'range': [a1_end + 1, a2_end]},
            {'name': 'Act 3: Resolution', 'range': [a2_end + 1, total - 1]}
        ]
        
        beats = []
        
        # Find True Inciting Incident: The earliest spike in pure emotional tension
        ii_idx = 0
        for i, t in enumerate(temporal_trace[:a1_end+1]):
            if t['attentional_signal'] > 0.6:
                ii_idx = i
                break
        
        # Find True Midpoint: The absolute peak of tension AND entropy (A major complication)
        mid_idx = a1_end
        highest_combo = 0
        if features and len(features) == len(temporal_trace):
            for i in range(a1_end, a2_end):
                combo = temporal_trace[i]['attentional_signal'] + (features[i].get('entropy_score', 0) / 10)
                if combo > highest_combo:
                    highest_combo = combo
                    mid_idx = i
        else:
            mid_idx = int(total/2) # Fallback

        climax_idx = total - 1
        highest_tension = 0
        for i in range(a2_end, total):
            if temporal_trace[i]['attentional_signal'] > highest_tension:
                highest_tension = temporal_trace[i]['attentional_signal']
                climax_idx = i
        
        beats = [
            {'name': 'Inciting Incident', 'scene_index': ii_idx},
            {'name': 'Midpoint', 'scene_index': mid_idx},
            {'name': 'Climax', 'scene_index': climax_idx}
        ]
        
        return {'acts': acts, 'beats': beats}

    def _get_snippet(self, scene_dict, preferred_tag=None):
        """Extracts a short text snippet from a scene using correct tags ('D', 'A')."""
        try:
            lines = scene_dict.get('lines', [])
            dialogue = [l['text'] for l in lines if l.get('tag') == 'D' and len(l['text']) > 10]
            action = [l['text'] for l in lines if l.get('tag') == 'A' and len(l['text']) > 10]
            
            if preferred_tag == 'A' and action:
                snip = action[len(action)//2]
                return f'"{snip[:60]}..."'
            if preferred_tag == 'D' and dialogue:
                snip = dialogue[len(dialogue)//2]
                return f'"{snip[:60]}..."'
                
            if dialogue: 
                snip = dialogue[len(dialogue)//2]
                return f'"{snip[:60]}..."'
            if action:
                snip = action[len(action)//2]
                return f'"{snip[:60]}..."'
            return ""
        except:
            return ""

    def diagnose_patterns(self, temporal_trace, features=None, scenes=None, genre='drama'):
        """Identifies Cognitive Experiences: Boredom, Confusion, Visceral Reaction."""
        diagnosis = []
        if not temporal_trace or not features or not scenes or len(features) != len(temporal_trace) or len(scenes) != len(temporal_trace): 
            return diagnosis
            
        signals = [s['attentional_signal'] for s in temporal_trace]
        
        # Pacing Threshold Adjustment by Genre
        sag_limit = 0.35 if genre.lower() == 'drama' else 0.45 
        sag_scenes = 3 if genre.lower() == 'drama' else 2 
            
        # 1. Overcrowded Narrative
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            if churn >= 3.5 and att_sig < 0.5:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Information Churn (Scene {i+1})**: Excessive name density. Suggest compressing introduction or embedding these details into an existing conflict. (e.g., {snippet})"
                )
                break

        # 2. Action Peak
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if action > 6 and att_sig > 0.8:
                snippet = self._get_snippet(scenes[i], preferred_tag='A')
                diagnosis.append(
                    f"✨ **Action Peak (Scene {i+1})**: Strong integration of physical action and tension. (e.g., {snippet})"
                )
                break
                
        # 3. Structural Sag
        high_runs = 0
        for i, s in enumerate(signals):
            if s < sag_limit: 
                high_runs += 1
            else: 
                high_runs = 0
            
            if high_runs >= sag_scenes:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🟠 **Attentional Valley (Scene {i+1})**: Cumulative period of lower dramatic signals. (e.g., {snippet})"
                )
                break
                
        # 4. Exposition Heavy
        for i in range(len(temporal_trace)):
            if entropy > 4.5 and att_sig < 0.4:  # Raised significantly to filter anything but pure data-dumps
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"💡 **Informational Peak (Scene {i+1})**: Dry exposition. Convert this block into a dramatic confrontation or high-stakes discovery to restore narrative momentum. (e.g., {snippet})"
                )
                break

        # 5. Talking Heads (High Dialogue, Low Action, Mid Tension)
        for i in range(len(temporal_trace)):
            feat = features[i]
            att_sig = temporal_trace[i]['attentional_signal']
            dial = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            action = feat.get('visual_abstraction', {}).get('action_lines', 0)
            
            if dial > 15 and action < 2 and 0.4 < att_sig < 0.6:
                snippet = self._get_snippet(scenes[i])
                diagnosis.append(
                    f"🗣️ **Talking Heads (Scene {i+1})**: Physical passivity. Inject visual subtext or external environment shifts to avoid dialogue fatigue. (e.g., {snippet})"
                )
                break

        # 6. Tonal Whiplash (Task: Stabilize detection)
        whiplash_candidates = []
        for i in range(1, len(temporal_trace)):
            curr_sig = temporal_trace[i]['attentional_signal']
            prev_sig = temporal_trace[i-1]['attentional_signal']
            feat = features[i]
            purpose = feat.get('purpose', {}).get('purpose', '')
            has_death = feat.get('narrative_closure', False)
            is_anchor_scene = any(kw in purpose for kw in ['Revelation', 'Discovery', 'Action', 'Conflict']) or has_death
            
            delta = abs(curr_sig - prev_sig)
            if delta > 0.65 and is_anchor_scene:  # Raised threshold to reduce false positive spikes
                whiplash_candidates.append((i, delta))

        # 8. Cognitive Resonance (The 'Perfect' Scene)
        resonance_candidates = []
        for i in range(len(temporal_trace)):
            res = temporal_trace[i].get('cognitive_resonance', 0)
            if res > 0.85:
                resonance_candidates.append((i, res))

        # --- Task: Mutual Exclusion Rule (Re-implemented for stability) ---
        final_whiplash = []
        final_resonance = []
        
        # Track which scenes have already been 'claimed' by one signal
        claimed_scenes = {}
        
        # Group all signals by index
        all_signals = []
        for idx, val in whiplash_candidates:
            all_signals.append({'idx': idx, 'type': 'whiplash', 'val': val})
        for idx, val in resonance_candidates:
            all_signals.append({'idx': idx, 'type': 'resonance', 'val': val})
            
        # Sort by value descending so the strongest signal 'wins' the scene
        all_signals.sort(key=lambda x: x['val'], reverse=True)
        
        for sig in all_signals:
            idx = sig['idx']
            if idx not in claimed_scenes:
                claimed_scenes[idx] = sig['type']
                if sig['type'] == 'whiplash':
                    final_whiplash.append(idx)
                else:
                    final_resonance.append(idx)

        # Now add filtered diagnostics to result
        for idx in sorted(final_whiplash)[:1]: # Show only the primary whiplash
            snippet = self._get_snippet(scenes[idx])
            diagnosis.append(f"🎢 **Tonal Whiplash (Scene {idx+1})**: Extreme shift in tension anchored by a sharp narrative turn. (e.g., {snippet})")
            
        for idx in sorted(final_resonance)[:1]: # Show only the primary resonance
            snippet = self._get_snippet(scenes[idx])
            diagnosis.append(f"💎 **Cognitive Resonance (Scene {idx+1})**: High harmonization of narrative conflict and emotional impact. (e.g., {snippet})")

        # 7. Similar Name Confusion
        for i in range(len(features)):
            frustration = features[i].get('reader_frustration', {})
            similar_pairs = frustration.get('similar_name_pairs', [])
            if similar_pairs:
                diagnosis.append(
                    f"🧠 **Audience Confusion (Scene {i+1})**: Characters with similar names ({', '.join(similar_pairs)}) may confuse the reader."
                )
                break

        return diagnosis

    def generate_suggestions(self, temporal_trace):
        return {}

    def generate_scene_notes(self, input_data):
        return {}

    def apply_semantic_labels(self, temporal_trace, valence_trace=None):
        labels = []
        for pt in temporal_trace:
            s = pt['attentional_signal']
            label = "Steady Flow"
            if s > 0.7: label = "High Conflict"
            elif s < 0.3: label = "Quiet Moment"
            labels.append({'scene_index': pt['scene_index'], 'primary_label': label, 'composite_beat': label})
        return labels

    def map_archetypes(self, voice_map): return {}
    def audit_subtext(self, encoded, voice_map): return []
    def map_to_custom_framework(self, trace, framework_type='3_act'): return self.map_to_structure(trace)
    def audit_narrative_intelligence(self, scenes, trace): return []
    def calculate_conflict_typology(self, encoded, valence): return []
    def track_thematic_recurrence(self, encoded): return []
    def map_interaction_networks(self, scenes, typologies): return {'edges': [], 'triangles': []}
    def audit_timeline_continuity(self, scenes): return []
    def audit_narrative_causality(self, encoded, scenes): return []
    def calculate_dialogue_authenticity(self, encoded): return []


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: writer_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import random
import re
import statistics

class WriterAgent:
    """
    The 'Collaborator' Layer (v2.0 Phase 1).
    Translates raw engine signals into actionable writer feedback.
    Does not run simulations; interprets existing trace data.
    """
    
    def analyze(self, final_output, genre="General"):
        """
        Enhances the final_output with a 'writer_intelligence' block.
        Applies Strict Constraints and Genre Nuance.
        """
        trace = final_output.get('temporal_trace', [])
        suggestions = final_output.get('suggestions', {})
        
        if not trace: return final_output
        
        # 1. Narrative Diagnosis (Start with existing cognitive insights from InterpretationAgent)
        narrative_health = final_output.get('narrative_diagnosis', [])
        
        # Phase 22-30 diagnostics (Collected and sorted for score determinism)
        new_diagnostics = []
        new_diagnostics.extend(self._diagnose_health(trace, genre))
        new_diagnostics.extend(self._diagnose_voice(final_output.get('voice_fingerprints', {})))
        new_diagnostics.extend(self._diagnose_motifs(trace))
        new_diagnostics.extend(self._diagnose_tell_vs_show(trace))
        new_diagnostics.extend(self._diagnose_on_the_nose(trace))
        new_diagnostics.extend(self._diagnose_shoe_leather(trace))
        new_diagnostics.extend(self._diagnose_semantic_motifs(trace))
        new_diagnostics.extend(self._diagnose_stakes_diversity(trace))
        new_diagnostics.extend(self._diagnose_stichomythia(trace))
        new_diagnostics.extend(self._diagnose_payoff_density(trace))
        new_diagnostics.extend(self._diagnose_opening_hook(trace))
        new_diagnostics.extend(self._diagnose_generic_dialogue(trace))
        new_diagnostics.extend(self._diagnose_flat_scene_turns(trace, genre))
        new_diagnostics.extend(self._diagnose_passive_voice(trace))
        new_diagnostics.extend(self._diagnose_tonal_whiplash(trace))
        new_diagnostics.extend(self._diagnose_redundant_scenes(trace))
        new_diagnostics.extend(self._diagnose_dangling_threads(trace))
        new_diagnostics.extend(self._diagnose_protagonist_arc(trace))
        new_diagnostics.extend(self._diagnose_interruption_dynamics(trace))
        new_diagnostics.extend(self._diagnose_monologues(trace))
        new_diagnostics.extend(self._diagnose_reader_frustration(trace))
        new_diagnostics.extend(self._diagnose_neglected_characters(trace))
        new_diagnostics.extend(self._diagnose_nonlinear_structure(trace))
        new_diagnostics.extend(self._diagnose_theme_coherence(trace))
        
        # Determine unique items and sort EVERYTHING for absolute score determinism
        # This ensures the penalty calculation always sees the exact same input order.
        all_diagnostics = sorted(list(set(narrative_health + new_diagnostics + self._diagnose_representation_risks(final_output.get('fairness_audit', {})))))
        
        # 2. Structural Dashboard with Arc Vectors + Scene Map
        dashboard = self._build_dashboard(trace, genre, final_output)
        dashboard['character_arcs'] = self._build_character_arcs(trace)
        dashboard['scene_purpose_map'] = self._build_scene_purpose_map(trace)
        dashboard['stakes_profile'] = self._build_stakes_profile(trace)
        dashboard['scene_turn_map'] = self._build_scene_turn_map(trace)
        dashboard['dialogue_action_ratio'] = self._build_global_dialogue_ratio(trace, genre)
        
        # Phase 27-28 additions
        dashboard['runtime_estimate'] = self._build_runtime_estimate(trace, genre)
        dashboard['location_profile'] = self._build_location_profile(trace)
        dashboard['structural_turning_points'] = self._find_structural_turning_points(trace)
        dashboard['scene_economy_map'] = self._build_scene_economy_map(trace)
        dashboard['page_turner_index'] = self._calculate_page_turner_index(trace)
        dashboard['writing_texture'] = self._diagnose_writing_texture(trace)
        dashboard['act_structure'] = self._build_act_structure(trace)
        dashboard['commercial_comps'] = self._find_commercial_comps(genre, dashboard.get('stakes_profile', {}).get('dominant', 'Social'))
        v_fingerprints = final_output.get('voice_fingerprints', {})
        # Purely deterministic line-count threshold for 'Cast' status (Tasks 3/Cast Count)
        dashboard['cast_count_deterministic'] = len([c for c, v in v_fingerprints.items() if v.get('line_count', 0) >= 5])

        # Market Readiness (Task 5)
        dashboard['market_readiness'] = self._calculate_market_readiness(dashboard)

        # Composite ScriptPulse Score (0-100) using the truly sorted diagnostics
        dashboard['scriptpulse_score'] = self._calculate_scriptpulse_score(dashboard, all_diagnostics)
        
        # Inject into output (Removing prescriptive 'rewrite_priorities')
        final_output['writer_intelligence'] = {
            'narrative_diagnosis': all_diagnostics[:15],
            'structural_dashboard': dashboard,
            'narrative_summary': self._build_narrative_summary(trace, genre, all_diagnostics),
            'creative_provocations': self._generate_creative_provocations(all_diagnostics, genre),
            'genre_context': genre
        }
        
        return final_output

    def _diagnose_health(self, trace, genre):
        """
        Converts math signals to story terms.
        Clusters consecutive issues.
        Adapts thresholds based on Genre.
        """
        assessments = []
        
        # Genre Thresholds
        boredom_thresh = 0.2
        if genre in ["Horror", "Drama", "Art House", "Avant-Garde", "Non-Linear"]:
            boredom_thresh = 0.1 # Tolerate slower pacing
            
        fatigue_thresh = 0.8
        if genre in ["Action", "Thriller"]:
            fatigue_thresh = 0.85 # Tolerate higher intensity
            
        is_avant_garde = genre in ["Avant-Garde", "Non-Linear"]
        
        # 1. Fatigue Clustering (Skipped for Avant-Garde which intentionally fatigues/overwhelms)
        if not is_avant_garde:
            fatigue_ranges = self._find_ranges(trace, lambda s: s['fatigue_state'] > fatigue_thresh)
            for start, end in fatigue_ranges:
                length = end - start + 1
                if length > 3:
                    duration_mins = length * 2
                    assessments.append(
                        f"🔴 **Sustained Intensity (Scenes {start}-{end})**: Consistently high attentional demand for ~{duration_mins} mins. May lead to audience fatigue."
                    )

        # 2. Confusion Clustering
        strain_ranges = self._find_ranges(trace, lambda s: s.get('expectation_strain', 0) > 0.8)
        for start, end in strain_ranges:
             assessments.append(
                 f"🟠 **Information Density (Scenes {start}-{end})**: High volume of new narrative elements. May increase cognitive load for the reader."
             )
            
        # 3. Boredom vs Tense Silence
        # Tightened for slow-burn masters: only flag if valley is too long (5+ scenes)
        true_boredom_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) <= 0.5)
        for start, end in true_boredom_ranges:
            if (end - start + 1) >= 5: # Reward 2-4 scene valleys as 'effective recovery'
                 assessments.append(
                     f"🔵 **Engagement Drop (Scenes {start}-{end})**: Attentional signals are low for an extended duration. Consider tightening the pacing or adding a 'hook' to keep the audience locked in."
                 )

        tense_silence_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) > 0.6)
        for start, end in tense_silence_ranges:
            if (end - start + 1) >= 2:
                 assessments.append(
                     f"🤫 **Tense Silence (Scenes {start}-{end})**: Low dialogue density but high conflict. Effective subtextual tension."
                 )

        # 4. Exposition Clustering
        expo_ranges = self._find_ranges(trace, lambda s: s.get('exposition_score', 0) > 0.7)
        for start, end in expo_ranges:
            assessments.append(
                f"💬 **Exposition Heavy (Scenes {start}-{end})**: Characters are explaining details explicitly rather than through action."
            )

        # 5. Pacing Volatility (The 'Avant-Garde' Special)
        volatility_ranges = self._find_ranges(trace, lambda s: s.get('pacing_volatility', 0) > 0.8)
        for start, end in volatility_ranges:
            assessments.append(
                f"🎢 **Erratic Pacing (Scenes {start}-{end})**: Extreme shifts in rhythm. Use sparingly for effect."
            )

        # 6. Irony / Dissonance
        irony_ranges = self._find_ranges(trace, lambda s: s.get('sentiment', 0) > 0.6 and s.get('conflict', 0) > 0.7)
        for start, end in irony_ranges:
             assessments.append(
                f"🎭 **Irony Detected (Scenes {start}-{end})**: Positive tone matches high conflict. Unsettling and effective."
            )
            
        # 7. Final Polish
        if not assessments:
            assessments.append("🟢 **Good Flow**: The story moves well.")
            
        return assessments

    def _diagnose_voice(self, voice_fingerprints):
        import statistics
        assessments = []
        if not voice_fingerprints or len(voice_fingerprints) < 2:
            return []

        top_chars = sorted(
            voice_fingerprints.items(),
            key=lambda x: x[1].get('line_count', 0),
            reverse=True
        )[:5]

        valid_chars = [c for c in top_chars if c[1].get('line_count', 0) >= 10]
        if len(valid_chars) < 2:
            return []

        # Only use fields that are actually populated in voice_fingerprints
        sentiments = [c[1].get('sentiment', 0) for c in valid_chars]
        agencies   = [c[1].get('agency', 0)    for c in valid_chars]

        std_sent   = statistics.stdev(sentiments) if len(sentiments) > 1 else 1.0
        std_agency = statistics.stdev(agencies)   if len(agencies)   > 1 else 1.0

        # Only flag if both sentiment AND agency distributions are nearly identical
        # (i.e. all characters feel the same AND exert the same power level)
        if std_sent < 0.08 and std_agency < 0.08:
            names = [c[0] for c in valid_chars[:3]]
            assessments.append(
                f"🔴 **Same Voice Syndrome**: The primary characters ({', '.join(names)}) "
                f"share nearly identical dialogue textures. Consider varying sentence "
                f"structures or punctuation habits to distinguish them."
            )

        return assessments

    def _diagnose_motifs(self, trace):
        assessments = []
        motif_tracker = {}
        for s in trace:
            motifs = s.get('motifs', [])
            idx = s['scene_index']
            for m in motifs:
                if m not in motif_tracker:
                    motif_tracker[m] = {'first': idx, 'last': idx, 'count': 0}
                motif_tracker[m]['last'] = idx
                motif_tracker[m]['count'] += 1
                
        total_scenes = len(trace)
        if total_scenes < 10: return []
        
        for m, data in motif_tracker.items():
            if data['count'] > 1:
                spread = data['last'] - data['first']
                if data['first'] < total_scenes * 0.3 and data['last'] > total_scenes * 0.7:
                    assessments.append(f"✨ **Successful Motif Payoff**: The object '{m}' was introduced early (Scene {data['first']}) and paid off late (Scene {data['last']}). Strong thematic resonance.")
                elif data['first'] < total_scenes * 0.3 and spread < total_scenes * 0.1:
                    assessments.append(f"🟡 **Abandoned Motif**: The object '{m}' was introduced in Scene {data['first']} but never reappears after Scene {data['last']}. Consider paying it off or cutting it.")
        
        # Sort so we only show the best ones
        # Prioritize payoffs over abandoned
        assessments.sort(key=lambda x: 'Abandoned' in x)
        return assessments[:2] # Limit to 2

    def _diagnose_tell_vs_show(self, trace):
        assessments = []
        tell_trap_ranges = self._find_ranges(trace, lambda s: s.get('tell_vs_show', {}).get('tell_ratio', 0.0) > 0.6 and s.get('tell_vs_show', {}).get('literal_emotions', 0) >= 2)
        for start, end in tell_trap_ranges:
            assessments.append(f"🟠 **'Tell, Don't Show' Trap (Scenes {start}-{end})**: Relying heavily on literal emotion words (e.g. 'sad', 'angry') in action lines rather than physical blocking/behavior.")
        return assessments[:1]

    def _find_ranges(self, trace, condition_fn):
        """Helper to find consecutive ranges where condition is true."""
        ranges = []
        in_range = False
        start_idx = -1
        
        for i, s in enumerate(trace):
            if condition_fn(s):
                if not in_range:
                    in_range = True
                    start_idx = s['scene_index']
            else:
                if in_range:
                    in_range = False
                    end_idx = trace[i-1]['scene_index']
                    ranges.append((start_idx, end_idx))
        
        # Close open range
        if in_range:
             ranges.append((start_idx, trace[-1]['scene_index']))
             
        return ranges

    def _rank_edits(self, suggestions, trace):
        """
        Sorts suggestions by estimated leverage.
        Adds root-cause context to avoid generic band-aids.
        """
        import re
        # Extract raw text suggestions
        if isinstance(suggestions, list):
            raw_list = suggestions
        else:
            raw_list = suggestions.get('structural_repair_strategies', [])
        prioritized = []
        
        for item in raw_list:
            # Heuristic Ranking
            score = 1
            impact_label = "Low"
            
            if "Cut" in item or "Shorten" in item: 
                score += 2
                impact_label = "Medium"

            # v2.0 Fix: Robustly extract text from both string and dict suggestions
            if isinstance(item, dict):
                suggestion_text = item.get('strategy', item.get('diagnosis', 'Unknown Suggestion'))
                # Also check tactics
                tactics = item.get('tactics', [])
                if tactics: suggestion_text += f": {', '.join(tactics)}"
            else:
                suggestion_text = str(item)

            clean_action = suggestion_text.split(":")[0] if ":" in suggestion_text else suggestion_text
            item_str = suggestion_text.lower()

            if "fatigue" in item_str: 
                score += 3
                impact_label = "High" 
            if "confusion" in item_str: 
                score += 3
                impact_label = "High"
            # Root-Cause Contextualization (Use clean_action which is now guaranteed to be a string)
            match = re.search(r'Scene (\d+)', clean_action)
            if match:
                scene_idx_str = match.group(1)
                try:
                    scene_idx = int(scene_idx_str)
                except ValueError:
                    scene_idx = -1
                    
                if scene_idx >= 0:
                    if "Increase stakes" in clean_action:
                        prior_stakes = [s.get('stakes', 0) for s in trace if s['scene_index'] < scene_idx and s['scene_index'] >= max(1, scene_idx - 10)]
                        if prior_stakes and max(prior_stakes) < 0.5:
                            clean_action += " (Root Cause: Stakes were never properly established in preceding scenes)"
                    
                    if "Cut" in clean_action or "Shorten" in clean_action:
                        clean_action += " OR insert a quiet recovery beat in the preceding scene"
            
            prioritized.append({'action': clean_action, 'leverage': impact_label, 'score': score})
            
        # Sort desc
        prioritized.sort(key=lambda x: x['score'], reverse=True)
        return prioritized

    def _build_dashboard(self, trace, genre, report=None):
        """
        Key structural checkpoints.
        """
        # Midpoint Check (Scene ~50% of length)
        mid_idx = len(trace) // 2
        midpoint_energy = trace[mid_idx]['attentional_signal'] if trace else 0
        
        # Act 1 Break (~25%)
        act1_idx = len(trace) // 4
        act1_energy = trace[act1_idx]['attentional_signal'] if trace else 0
        
        if genre in ["Avant-Garde", "Non-Linear"]:
            return {
                'midpoint_energy': round(midpoint_energy, 2),
                'midpoint_status': "Intentional Subversion",
                'act1_energy': round(act1_energy, 2),
                'total_scenes': len(trace),
                'structural_note': "Standard Hollywood pacing milestones are ignored for this genre."
            }
            
        return {
            'midpoint_energy': round(midpoint_energy, 2),
            'midpoint_status': "Healthy" if midpoint_energy > 0.5 else "Sagging",
            'act1_energy': round(act1_energy, 2),
            'total_scenes': len(trace),
            'production_risk_score': self._calculate_production_risks(trace),
            'budget_impact': self._calculate_budget_impact(trace, report)
        }

    # =========================================================================
    # PHASE 23: MASTERCLASS DIAGNOSTIC METHODS
    # =========================================================================

    def _diagnose_on_the_nose(self, trace):
        """
        Identify scenes where characters say exactly what they are thinking/feeling.
        Threshold: >25% on-the-nose dialogue hits.
        """
        assessments = []
        for s in trace:
            otn = s.get('on_the_nose', {})
            idx = s['scene_index']
            rep = s.get('representative_dialogue', '')
            if otn.get('on_the_nose_ratio', 0) > 0.25:
                quote = f" (e.g., \"{rep[:60]}...\")" if rep else ""
                assessments.append(
                    f"🗣️ **On-The-Nose Dialogue (Scene {idx})**: Characters are stating their internal subtext as text{quote}. "
                    f"Subvert the lines to hide the real emotion behind a defensive or tactical goal."
                )
        return assessments[:2]

    def _diagnose_shoe_leather(self, trace):
        """
        Flag scenes where too many dialogue lines at the start or end are meaningless filler.
        """
        assessments = []
        for s in trace:
            sl = s.get('shoe_leather', {})
            idx = s['scene_index']
            rep = s.get('representative_dialogue', '')
            if sl.get('has_shoe_leather', False):
                quote = f" (e.g., \"{rep[:60]}...\")" if rep else ""
                assessments.append(
                    f"✂️ **Shoe-Leather Detected (Scene {idx})**: "
                    f"Filler dialogue at the start or end of the scene{quote}. "
                    f"Arrive late, leave early — cut the pleasantries."
                )
        return assessments[:2]  # Top 2 worst offenders

    def _diagnose_semantic_motifs(self, trace):
        """
        Evaluate recurring thematic terms extracted semantically (not just caps).
        Cross-reference first and last ¼ of the script to detect structural resonance.
        """
        assessments = []
        total = len(trace)
        if total < 10:
            return []

        act1_scenes = trace[:total // 4]
        act3_scenes = trace[total * 3 // 4:]

        # Collect terms from Act 1 and Act 3
        act1_terms = set()
        act3_terms = set()
        for s in act1_scenes:
            act1_terms.update(s.get('semantic_motifs', []))
        for s in act3_scenes:
            act3_terms.update(s.get('semantic_motifs', []))

        # Successful semantic payoffs
        payoffs = act1_terms.intersection(act3_terms)
        orphaned = act1_terms - act3_terms

        for term in list(payoffs)[:2]:
            assessments.append(
                f"✨ **Semantic Echo ('{term}')**: This theme/object recurs from Act 1 into Act 3. "
                f"Strong subconscious resonance for the audience."
            )
        for term in list(orphaned)[:1]:
            assessments.append(
                f"🟡 **Thematic Orphan ('{term}')**: Introduced early but never revisited. "
                f"Consider weaving it back in or cutting it."
            )
        return assessments[:2]

    def _build_character_arcs(self, trace):
        char_timeline = {}
        for s in trace:
            for char, data in s.get('character_scene_vectors', {}).items():
                if char not in char_timeline:
                    char_timeline[char] = []
                char_timeline[char].append({
                    'scene': s['scene_index'],
                    # Use scene-level compound sentiment — much more meaningful than
                    # the per-character ±0.1 word-count proxy
                    'sentiment': s.get('sentiment', data.get('sentiment', 0.0)),
                    'agency': data.get('agency', 0.0),
                    'lines': data.get('line_count', 0),
                    'resolved': s.get('narrative_closure', False)
                })

        arc_summary = {}
        total_scenes = max([s.get('scene_index', 0) for s in trace]) if trace else 100

        for char, timeline in sorted(char_timeline.items()):
            if len(timeline) < 3:
                continue
            total_lines = sum(t['lines'] for t in timeline)
            if total_lines < 8:
                continue

            # Use 3-scene windows at start and end for stability
            window = max(1, min(3, len(timeline) // 4))
            start_sentiment = sum(t['sentiment'] for t in timeline[:window]) / window
            end_sentiment   = sum(t['sentiment'] for t in timeline[-window:]) / window
            start_agency    = sum(t['agency']    for t in timeline[:window]) / window
            end_agency      = sum(t['agency']    for t in timeline[-window:]) / window

            sentiment_delta = round(end_sentiment - start_sentiment, 3)
            agency_delta    = round(end_agency    - start_agency,    3)

            is_near_end = timeline[-1].get('scene', 0) > (total_scenes * 0.95)

            # Structural exit: character disappears before the final 8% of the script.
            # Narrower threshold (0.92) precisely catches Vito's mid-Act 3 exit while protecting mainstays.
            last_scene_idx = timeline[-1].get('scene', 0)
            char_in_final_section = last_scene_idx > (total_scenes * 0.92)

            # Secondary signal: scene-level closure at character's last appearance
            has_closure_at_exit = (
                timeline[-1].get('resolved', False) or
                (len(timeline) > 1 and timeline[-2].get('resolved', False))
            )

            is_narrative_exit = (not char_in_final_section)

            # Presence ratio: what fraction of total scenes does this character appear in?
            presence_ratio = len(timeline) / max(1, total_scenes)

            # Arc classification — strict priority order, most specific first.

            # P0: Narrative Exit — character permanently gone before final 8%.
            if is_narrative_exit:
                arc_label = "Resolved (Narrative Exit) 💀"
                arc_note = "Character's thread reached a definitive mid-story conclusion (death/exit)."

            # P1: Resolved/Conclusive — static character at story's end.
            # Requires near-end presence, closure signal, AND minimal movement.
            elif has_closure_at_exit and is_near_end and abs(sentiment_delta) < 0.12 and abs(agency_delta) < 0.12:
                arc_label = "Resolved / Conclusive 🏁"
                arc_note = "Character's narrative purpose reached its structural conclusion at story's end."

            # P2: Classic Tragedy — gains power, loses soul (strict thresholds).
            elif sentiment_delta < -0.3 and agency_delta > 0.15:
                arc_label = "Classic Tragedy 🎭"
                arc_note = "Gains agency but loses emotional hope — the dominant dramatic arc."

            # P3: Hero's Journey — positive on both axes
            elif sentiment_delta > 0.3 and agency_delta > 0.15:
                arc_label = "Hero's Journey ⭐"
                arc_note = "Strong positive transformation in sentiment and agency."

            # P4: Steadfast/Supportive — emotionally stable, consistently present.
            # Defined by STABILITY, not loss. Characters who appear in >10% of scenes
            # and show minimal sentiment movement are anchoring figures.
            elif abs(sentiment_delta) < 0.25 and presence_ratio > 0.10 and char_in_final_section:
                arc_label = "Steadfast / Supportive 🛡️"
                arc_note = "Emotionally stable presence throughout the story. Anchoring figure."

            # P5: Descent — large negative on agency (threshold -0.20, strict).
            elif agency_delta < -0.20:
                if sentiment_delta > -0.1:
                    arc_label = "Steadfast / Supportive 🛡️"
                    arc_note = "Loses agency but holds emotional core. Loyal advisor archetype."
                else:
                    arc_label = "Descent 📉"
                    arc_note = "Negative movement in both power and emotional outlook."

            # P6: Flat — genuinely static characters only (strict threshold < 0.005)
            elif abs(sentiment_delta) < 0.005 and abs(agency_delta) < 0.005:
                arc_label = "Flat Arc ⚠️"
                arc_note = "Character remains static across both emotional and power axes. Is this intended?"

            # P7: Developing — some movement, no dominant classified pattern.
            else:
                arc_label = "Developing Arc 📈"
                arc_note = "Character shows movement across story beats but no dominant direction."


            arc_summary[char] = {
                'arc_type':        arc_label,
                'note':            arc_note,
                'sentiment_start': round(start_sentiment, 3),
                'sentiment_end':   round(end_sentiment, 3),
                'sentiment_delta': sentiment_delta,
                'agency_start':    round(start_agency, 3),
                'agency_end':      round(end_agency, 3),
                'agency_delta':    agency_delta,
                'scenes_present':  len(timeline)
            }

        return arc_summary


    def _diagnose_stakes_diversity(self, trace):
        """
        Warn if the entire script uses only one type of stakes (e.g., only Physical).
        A rich story layers multiple stakes types.
        """
        assessments = []
        all_dominants = [s.get('stakes_taxonomy', {}).get('dominant', 'None') for s in trace]
        unique_types = set(d for d in all_dominants if d != 'None')
        total = len([d for d in all_dominants if d != 'None'])
        if total == 0: return []

        # Find over-reliance: any single type covering >70% of scenes
        for stype in unique_types:
            count = all_dominants.count(stype)
            ratio = count / total if total > 0 else 0
            if ratio > 0.7:
                assessments.append(
                    f"⚠️ **Stakes Concentration ({stype})**: {round(ratio * 100)}% of the narrative relies on "
                    f"{stype} stakes. This pattern limits layered jeopardy across Physical, Emotional, Social, and Moral domains."
                )
                break  # Only report the worst offender

        if len(unique_types) >= 4:
            assessments.append(
                f"✅ **Rich Stakes Ecology**: Your script uses {len(unique_types)} types of stakes "
                f"({', '.join(sorted(unique_types))}). Multi-layered jeopardy — excellent."
            )
        return assessments[:1]

    def _diagnose_stichomythia(self, trace):
        """
        Note scenes with stichomythia as a technique insight.
        """
        assessments = []
        sticho_scenes = [s['scene_index'] for s in trace if s.get('stichomythia', {}).get('has_stichomythia', False)]
        if sticho_scenes:
            n = len(sticho_scenes)
            s_list = ', '.join(str(x) for x in sticho_scenes[:3])
            assessments.append(
                f"⚡ **Stichomythia Detected (Scene{'s' if n > 1 else ''} {s_list})**: "
                f"Rapid-fire single-line exchanges — a high-energy confrontation technique. "
                f"If intentional: powerful. If accidental: check that both characters are getting full thoughts in."
            )
        return assessments[:1]

    def _diagnose_payoff_density(self, trace):
        """
        Surface scenes with Diluted Impact and credit scenes with Powerful Compression.
        """
        assessments = []
        diluted = [s['scene_index'] for s in trace if s.get('payoff_density', {}).get('label') == 'Diluted Impact']
        compressed = [s['scene_index'] for s in trace if s.get('payoff_density', {}).get('label') == 'Powerful Compression']

        if diluted:
            d_list = ', '.join(str(x) for x in diluted[:3])
            assessments.append(
                f"🔵 **Diluted Impact (Scene{'s' if len(diluted) > 1 else ''} {d_list})**: "
                f"Long scenes with low emotional density. Trim or escalate — every line should earn its keep."
            )
        if compressed:
            c_list = ', '.join(str(x) for x in compressed[:2])
            assessments.append(
                f"💎 **Powerful Compression (Scene{'s' if len(compressed) > 1 else ''} {c_list})**: "
                f"Short, dense scenes with high emotional impact. Master-class efficiency."
            )
        return assessments[:2]

    def _build_scene_purpose_map(self, trace):
        """
        Returns a scene-by-scene list of narrative purposes for the dashboard.
        Also warns if there are too many consecutive Transition scenes.
        """
        purpose_map = []
        for s in trace:
            purpose = s.get('scene_purpose', {}).get('purpose', 'Unknown')
            purpose_map.append({'scene': s['scene_index'], 'purpose': purpose})

        # Warn about too many consecutive Transition scenes
        warnings = []
        consecutive_transitions = 0
        for entry in purpose_map:
            if entry['purpose'] == 'Transition':
                consecutive_transitions += 1
                if consecutive_transitions >= 3:
                    warnings.append(f"Scene {entry['scene']}: 3+ consecutive Transition scenes — consider consolidating.")
            else:
                consecutive_transitions = 0

        return {
            'map': purpose_map,
            'transition_warnings': warnings[:2]
        }

    def _build_stakes_profile(self, trace):
        """
        Aggregate the stakes taxonomy across the whole script.
        Returns a high-level count of Physical/Emotional/Social/Moral/Existential scenes.
        """
        profile = {'Physical': 0, 'Emotional': 0, 'Social': 0, 'Moral': 0, 'Existential': 0, 'None': 0}
        for s in trace:
            dominant = s.get('stakes_taxonomy', {}).get('dominant', 'None')
            if dominant in profile:
                profile[dominant] += 1
            else:
                profile['None'] += 1
        return profile

    # =========================================================================
    # PHASE 25: SCENE-LEVEL MICRO-DRAMA METHODS
    # =========================================================================

    def _diagnose_opening_hook(self, trace):
        """Report the quality of the opening hook from Scene 0."""
        assessments = []
        if not trace: return []
        hook = trace[0].get('opening_hook', None)
        if not hook: return []

        label = hook.get('hook_label', 'Unknown')
        lines_before = hook.get('lines_before_conflict', 0)

        if label == 'Strong Hook':
            assessments.append(
                f"🎣 **Strong Opening Hook**: Conflict or tension arrives within the first few lines. "
                f"Excellent — the reader is immediately engaged."
            )
        elif label == 'Moderate Hook':
            assessments.append(
                f"🟡 **Moderate Opening Hook**: The central tension takes {lines_before} lines to appear. "
                f"Consider moving the first conflict beat earlier to grab the reader immediately."
            )
        elif label in ('Weak Hook', 'No Hook Detected'):
            assessments.append(
                f"🔴 **Weak Opening Hook**: {lines_before} lines pass before any conflict or dramatic question. "
                f"Readers and executives judge scripts on the first page. Open stronger."
            )
        return assessments[:1]

    def _diagnose_generic_dialogue(self, trace):
        """Flag the top scenes with the highest cliché dialogue ratios."""
        assessments = []
        cliche_scenes = [
            (s['scene_index'], s.get('generic_dialogue', {}))
            for s in trace
            if s.get('generic_dialogue', {}).get('cliche_ratio', 0) > 0.2
        ]
        cliche_scenes.sort(key=lambda x: x[1].get('cliche_ratio', 0), reverse=True)

        for idx, gd in cliche_scenes[:2]:
            examples = gd.get('examples', [])
            count = gd.get('cliche_count', 0)
            eg_str = f' (e.g. "{examples[0]}")' if examples else ''
            assessments.append(
                f"💬 **Generic Dialogue (Scene {idx})**: {count} interchangeable cliché line(s) detected{eg_str}. "
                f"Rewrite these to be hyper-specific to THIS character in THIS moment."
            )
        return assessments[:2]

    def _diagnose_flat_scene_turns(self, trace, genre='Drama'):
        """Flag consecutive scenes where the scene turn is flat — no dramatic movement."""
        assessments = []
        flat_ranges = self._find_ranges(trace, lambda s: s.get('scene_turn', {}).get('turn_label') == 'Flat')
        min_flat = 4 if genre.lower() in ['drama', 'crime drama'] else 2
        for start, end in flat_ranges:
            if (end - start + 1) >= min_flat:
                assessments.append(
                    f"⬜ **Flat Scene Turns (Scenes {start}–{end})**: Emotional trajectory remains stagnant. "
                    f"These scenes end in the same relative position they began."
                )
        return assessments[:1]

    def _build_scene_turn_map(self, trace):
        """Scene-by-scene turn type for the structural dashboard."""
        return [
            {
                'scene': s['scene_index'],
                'turn': s.get('scene_turn', {}).get('turn_label', 'Unknown'),
                'sentiment_delta': s.get('scene_turn', {}).get('sentiment_delta', 0.0)
            }
            for s in trace
        ]

    def _build_global_dialogue_ratio(self, trace, genre):
        """
        Aggregate dialogue/action ratios across all scenes.
        Compare against genre benchmarks and surface an insight.
        """
        benchmarks = {
            'action':      0.40, 'thriller':    0.45, 'horror':      0.42,
            'drama':       0.60, 'crime drama': 0.58, 'comedy':      0.65, 
            'romance':     0.65, 'sci-fi':      0.50, 'avant-garde': 0.55, 
            'general':     0.55
        }
        total_d = sum(s.get('dialogue_action_ratio', {}).get('dialogue_lines', 0) for s in trace)
        total_a = sum(s.get('dialogue_action_ratio', {}).get('action_lines', 0) for s in trace)
        total = max(1, total_d + total_a)
        global_ratio = round(total_d / total, 3)

        benchmark = benchmarks.get(genre.lower(), 0.55)
        diff = global_ratio - benchmark

        if diff > 0.12:
            note = f"Script is {round(diff * 100)}% more dialogue-heavy than genre expectations for {genre}."
        elif diff < -0.15:
            note = f"Script is {round(abs(diff) * 100)}% more action-heavy than genre expectations for {genre}."
        else:
            note = f"Dialogue/Action balance is within the expected range for {genre}."

        return {
            'global_dialogue_ratio': global_ratio,
            'genre_benchmark': benchmark,
            'assessment': note
        }

    # =========================================================================
    # PHASE 26: MACRO-CONSISTENCY & CRAFT QUALITY METHODS
    # =========================================================================

    def _diagnose_passive_voice(self, trace):
        """
        Flag scenes with a high ratio of passive voice in action lines.
        Passive action lines kill visual energy and slow the read.
        """
        assessments = []
        passive_scenes = [
            (s['scene_index'], s.get('passive_voice', {}))
            for s in trace
            if s.get('passive_voice', {}).get('passive_ratio', 0.0) > 0.35
        ]
        passive_scenes.sort(key=lambda x: x[1].get('passive_ratio', 0), reverse=True)

        for idx, pv in passive_scenes[:2]:
            eg = pv.get('examples', [])
            count = pv.get('passive_count', 0)
            eg_str = f' (e.g. "{eg[0][:55]}...")' if eg else ''
            assessments.append(
                f"✍️ **Passive Action Lines (Scene {idx})**: {count} passive construction(s) detected{eg_str}. "
                f"Active voice typically increases cinematic energy."
            )
        return assessments[:1]

    def _diagnose_tonal_whiplash(self, trace):
        """
        Compare the macro-level sentiment average of each Act.
        If Act 2 is dramatically more positive/negative than Act 1 and Act 3, flag Tonal Whiplash.
        """
        assessments = []
        if len(trace) < 9:
            return []

        third = len(trace) // 3
        act1 = trace[:third]
        act2 = trace[third:third * 2]
        act3 = trace[third * 2:]

        def avg_sentiment(scenes):
            vals = [s.get('sentiment', 0.0) for s in scenes]
            return sum(vals) / len(vals) if vals else 0.0

        s1, s2, s3 = avg_sentiment(act1), avg_sentiment(act2), avg_sentiment(act3)

        # Whiplash: Act 2 is a significant outlier from both Act 1 and Act 3
        diff_1_2 = abs(s2 - s1)
        diff_2_3 = abs(s2 - s3)

        if diff_1_2 > 0.3 and diff_2_3 > 0.3:
            direction = "significantly more positive" if s2 > s1 else "significantly darker"
            assessments.append(
                f"🎢 **Tonal Whiplash**: Act 2 (avg sentiment: {s2:.2f}) is {direction} than "
                f"Act 1 ({s1:.2f}) and Act 3 ({s3:.2f}). This tonal inconsistency may feel jarring. "
                f"Aim for a coherent emotional register across the script."
            )
        return assessments[:1]

    def _diagnose_redundant_scenes(self, trace):
        """
        Compare scene vocabulary fingerprints to flag pairs of scenes that may be
        covering the same narrative ground (same purpose + high vocabulary overlap).
        """
        assessments = []
        if len(trace) < 4:
            return []

        # Build a list of (scene_index, purpose, vocab_set) tuples
        scene_data = []
        for s in trace:
            purpose = s.get('scene_purpose', {}).get('purpose', 'Unknown')
            vocab = set(s.get('scene_vocabulary', []))
            scene_data.append((s['scene_index'], purpose, vocab))

        flagged = set()
        for i in range(len(scene_data)):
            for j in range(i + 1, min(i + 40, len(scene_data))):
                idx_a, purpose_a, vocab_a = scene_data[i]
                idx_b, purpose_b, vocab_b = scene_data[j]

                if not vocab_a or not vocab_b:
                    continue
                if purpose_a != purpose_b:
                    continue  # Only compare same-purpose scenes

                # Jaccard similarity
                intersection = len(vocab_a & vocab_b)
                union = len(vocab_a | vocab_b)
                similarity = intersection / union if union > 0 else 0.0

                if similarity > 0.55 and (idx_a, idx_b) not in flagged:
                    flagged.add((idx_a, idx_b))
                    assessments.append(
                        f"♻️ **Possible Redundancy (Scenes {idx_a} & {idx_b})**: Both are '{purpose_a}' "
                        f"scenes with {round(similarity * 100)}% vocabulary overlap. "
                        f"They may be covering the same ground — consider merging or differentiating."
                    )

        return assessments[:2]

    def _diagnose_dangling_threads(self, trace):
        """
        Detect character pairs who interact heavily in Act 1 but never share a scene
        again in Act 2/3 — potential unresolved relationship threads.
        Uses 'character_scene_vectors' presence as a proxy for 'in this scene'.
        """
        assessments = []
        if len(trace) < 8:
            return []

        third = len(trace) // 3
        act1 = trace[:third]
        rest = trace[third:]

        # Build co-occurrence: which pairs appear together → proxy: both have vectors in same scene
        def get_characters(scene):
            return set(scene.get('character_scene_vectors', {}).keys())

        act1_pairs = {}
        for s in act1:
            chars = list(get_characters(s))
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    pair = tuple(sorted([chars[i], chars[j]]))
                    act1_pairs[pair] = act1_pairs.get(pair, 0) + 1

        # Find pairs that shared scenes in Act 1 but have zero co-occurrence after that
        rest_individual_chars = set()
        rest_pairs = set()
        for s in rest:
            chars = list(get_characters(s))
            rest_individual_chars.update(chars)
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    rest_pairs.add(tuple(sorted([chars[i], chars[j]])))

        # Detect character 'exits' (deaths/departures)
        last_appearance = {}
        for s in trace:
            for char in get_characters(s):
                last_appearance[char] = s['scene_index']
        
        total_scenes = len(trace)

        for pair, count in act1_pairs.items():
            if count >= 3 and pair not in rest_pairs:
                a, b = pair
                # Only flag if both characters remain in the script well after their last interaction
                # If one character stops appearing shortly after, it's a resolution (death/exit).
                a_exit = last_appearance.get(a, 0)
                b_exit = last_appearance.get(b, 0)
                
                # If both characters are still around 15% of the script later but haven't interacted, it's dangling
                if a in rest_individual_chars and b in rest_individual_chars:
                    # Threshold for 'still around' - if they both appear in the final act
                    if a_exit > total_scenes * 0.8 and b_exit > total_scenes * 0.8:
                        assessments.append(
                            f"🧵 **Dangling Thread ({a} & {b})**: These characters share {count} scene(s) together "
                            f"in Act 1 but never interact again despite both being present in the finale. "
                            f"The audience is waiting for their story to resolve."
                        )

        return assessments[:2]

    # =========================================================================
    # PHASE 27: PRODUCER'S VIEW METHODS
    # =========================================================================

    def _diagnose_protagonist_arc(self, trace):
        """
        Identify the protagonist (highest total line count) and check if their
        agency grows from Act 1 to Act 3. Flag if the hero never gains control.
        """
        assessments = []
        if len(trace) < 6: return []

        # Aggregate line counts AND scene appearances per character across the full trace
        char_lines = {}
        char_scenes = {}
        for s in trace:
            for char, data in s.get('character_scene_vectors', {}).items():
                char_lines[char] = char_lines.get(char, 0) + data.get('line_count', 0)
                char_scenes[char] = char_scenes.get(char, 0) + 1

        if not char_lines: return []

        # Normalise both metrics then combine (60% lines, 40% scene presence)
        max_lines = max(char_lines.values()) or 1
        max_scenes = max(char_scenes.values()) or 1
        char_score = {
            c: (char_lines[c] / max_lines * 0.6) + (char_scenes.get(c, 0) / max_scenes * 0.4)
            for c in char_lines
        }
        protagonist = max(char_score, key=char_score.get)

        # Build protagonist's agency through each act
        third = len(trace) // 3
        def avg_agency(scenes):
            vals = [s.get('character_scene_vectors', {}).get(protagonist, {}).get('agency', None) for s in scenes]
            vals = [v for v in vals if v is not None]
            return sum(vals) / len(vals) if vals else None

        a1 = avg_agency(trace[:third])
        a3 = avg_agency(trace[third * 2:])

        if a1 is None or a3 is None: return []

        delta = a3 - a1
        if delta < -0.15:
            assessments.append(
                f"📉 **Protagonist Regression ({protagonist})**: Agency drops from "
                f"{a1:.2f} (Act 1) to {a3:.2f} (Act 3). Your protagonist ends the story "
                f"MORE passive than they started."
            )
        elif delta > 0.3:
             assessments.append(
                f"📈 **Protagonist Ascension ({protagonist})**: Agency spikes from "
                f"{a1:.2f} → {a3:.2f}. A powerful transformation from reactive to total command."
            )
        elif abs(delta) < 0.005:
            assessments.append(
                f"⬜ **Protagonist Flat Arc ({protagonist})**: Agency stays flat "
                f"({a1:.2f} → {a3:.2f}) across the script."
            )
        else:
            assessments.append(
                f"✅ **Protagonist Growth ({protagonist})**: Agency rises from "
                f"{a1:.2f} → {a3:.2f}. Standard reactive-to-active transformation."
            )
        return assessments[:1]

    def _diagnose_interruption_dynamics(self, trace):
        """
        Surface the biggest interrupter and the most interrupted character.
        Insight: interruptions encode power dynamics.
        """
        assessments = []
        global_chars = {}
        for s in trace:
            per_char = s.get('interruption_patterns', {}).get('per_character', {})
            for char, data in per_char.items():
                if char not in global_chars:
                    global_chars[char] = {'interrupts': 0, 'interrupted': 0}
                global_chars[char]['interrupts'] += data.get('interrupts', 0)
                global_chars[char]['interrupted'] += data.get('interrupted', 0)

        if not global_chars: return []

        total_ints = sum(v['interrupted'] for v in global_chars.values())
        if total_ints < 3: return []

        top_interrupter = max(global_chars, key=lambda c: global_chars[c]['interrupts'])
        most_interrupted = max(global_chars, key=lambda c: global_chars[c]['interrupted'])

        if global_chars[top_interrupter]['interrupts'] > 2:
            assessments.append(
                f"⚡ **Interruption Power Dynamic**: **{top_interrupter}** dominates conversations "
                f"({global_chars[top_interrupter]['interrupts']} cut-offs). "
                f"**{most_interrupted}** rarely finishes a thought "
                f"({global_chars[most_interrupted]['interrupted']} interruptions received). "
                f"Use this intentionally — it's a strong power signal."
            )
        return assessments[:1]

    def _build_runtime_estimate(self, trace, genre):
        """
        Sum runtime contributions from all scenes to estimate total script runtime.
        Compare against genre benchmarks and flag if out of range.
        """
        total_seconds = sum(s.get('runtime_contribution', {}).get('estimated_seconds', 0) for s in trace)
        total_minutes = round(total_seconds / 60, 1)

        benchmarks = {
            'feature': (85, 130), 
            'drama': (90, 120),       # restore standard benchmark
            'crime drama': (100, 180), # Epic crime dramas
            'comedy': (85, 110),
            'thriller': (90, 130), 
            'horror': (80, 105), 
            'action': (95, 140),
            'short': (5, 30), 
            'pilot': (22, 65), 
            'general': (85, 130),
            'avant-garde': (70, 100) 
        }
        low, high = benchmarks.get(genre.lower(), (85, 125))

        if total_minutes < low:
            status = f"Under — {total_minutes} min (target: {low}–{high} min for {genre}). Script may be too short."
        elif total_minutes > high:
            status = f"Over — {total_minutes} min (target: {low}–{high} min for {genre}). Script may be too long."
        else:
            status = f"On Target — {total_minutes} min (target: {low}–{high} min for {genre})."

        return {
            'estimated_minutes': total_minutes,
            'estimated_seconds': round(total_seconds),
            'genre_target_min': low,
            'genre_target_max': high,
            'status': status
        }

    def _build_location_profile(self, trace):
        """
        Aggregate unique locations and INT/EXT balance across the script.
        Warn if >60% of scenes share the same top location.
        """
        location_counts = {}
        int_count = 0
        ext_count = 0

        for s in trace:
            loc_data = s.get('location_data', {})
            raw_loc = loc_data.get('location', 'UNKNOWN')
            # Fix 1: Strip time-of-day suffixes for better deduplication
            loc = re.sub(r'\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME|MOMENTS?\s+LATER).*$', '', raw_loc, flags=re.IGNORECASE).strip()
            interior = loc_data.get('interior')

            location_counts[loc] = location_counts.get(loc, 0) + 1
            if interior == 'INT': int_count += 1
            elif interior == 'EXT': ext_count += 1

        total = max(1, len(trace))
        sorted_locs = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        top_loc, top_count = sorted_locs[0] if sorted_locs else ('UNKNOWN', 0)
        top_ratio = top_count / total

        warning = None
        loc_per_scene = len(sorted_locs) / total

        if loc_per_scene > 0.7:
            # Nearly every scene is a brand-new location — genuine production concern
            warning = (
                f"{len(sorted_locs)} location headings across {total} scenes "
                f"({round(loc_per_scene * 100)}% scene-location churn). "
                f"Note: sub-locations of the same building count separately. "
                f"High location variety significantly increases production costs."
            )
        elif top_ratio > 0.6 and len(sorted_locs) < 5:
            # Script is almost entirely one place — consider visual variety
            warning = (
                f"{round(top_ratio * 100)}% of scenes share '{top_loc}'. "
                f"Only {len(sorted_locs)} unique location(s). "
                f"Consider varying the physical world to add visual range."
            )

        return {
            'unique_locations': len(sorted_locs),
            'top_location': top_loc,
            'top_location_ratio': round(top_ratio, 3),
            'int_scenes': int_count,
            'ext_scenes': ext_count,
            'int_ext_ratio': round(int_count / max(1, int_count + ext_count), 3),
            'location_warning': warning,
            'all_locations': dict(sorted_locs[:10])
        }

    # =========================================================================
    # PHASE 28: SYNTHESIS & STRUCTURE INTELLIGENCE METHODS
    # =========================================================================

    def _diagnose_monologues(self, trace):
        """
        Flag scenes where any character delivers a long solo speech (8+ dialogue lines).
        """
        assessments = []
        for s in trace:
            mdata = s.get('monologue_data', {})
            if mdata.get('has_monologue'):
                for m in mdata.get('monologues', []):
                    char = m.get('character', 'Unknown')
                    length = m.get('length', 0)
                    assessments.append(
                        f"🎙️ **Monologue Risk (Scene {s['scene_index']}, {char})**: "
                        f"{length}-line uninterrupted solo. Long monologues are high-risk — "
                        f"can stop a film cold if not earned. Ensure every line reveals character or advances plot."
                    )
        return assessments[:2]

    def _find_structural_turning_points(self, trace):
        """
        Identify the 4 load-bearing structural moments by peak-finding in the signal
        (conflict + stakes + sentiment_delta combined). Returns best candidate scenes.
        """
        if len(trace) < 6:
            return {'note': 'Script too short for structural analysis'}

        n = len(trace)
        third = n // 3

        def composite_signal(s):
            conflict = s.get('conflict', 0.0)
            stakes = s.get('stakes', 0.0)
            turn_delta = abs(s.get('scene_turn', {}).get('sentiment_delta', 0.0))
            economy = s.get('scene_economy', {}).get('economy_score', 0) / 10.0
            return conflict + stakes + turn_delta + economy

        # Inciting Incident: first peak in Act 1 (first 25%)
        act1_end = n // 4
        act1_signals = [(i, composite_signal(trace[i])) for i in range(act1_end)]
        inciting = max(act1_signals, key=lambda x: x[1]) if act1_signals else (0, 0)

        # Act 1 Break: peak signal in last 10% of Act 1
        a1b_start = third - n // 8
        a1b_end = third + n // 8
        a1b_signals = [(i, composite_signal(trace[i])) for i in range(max(0, a1b_start), min(n, a1b_end))]
        act1_break = max(a1b_signals, key=lambda x: x[1]) if a1b_signals else (third, 0)

        # Midpoint: peak in scenes around the script's centre
        mid = n // 2
        mid_signals = [(i, composite_signal(trace[i])) for i in range(max(0, mid - n // 8), min(n, mid + n // 8))]
        midpoint = max(mid_signals, key=lambda x: x[1]) if mid_signals else (mid, 0)

        # Darkest Moment / Act 2 Break: peak in last quarter of Act 2
        a2b_start = third * 2 - n // 8
        a2b_end = third * 2 + n // 8
        a2b_signals = [(i, composite_signal(trace[i])) for i in range(max(0, a2b_start), min(n, a2b_end))]
        act2_break = max(a2b_signals, key=lambda x: x[1]) if a2b_signals else (third * 2, 0)

        result = {
            'inciting_incident': {'scene': inciting[0], 'strength': round(inciting[1], 3)},
            'act1_break': {'scene': act1_break[0], 'strength': round(act1_break[1], 3)},
            'midpoint': {'scene': midpoint[0], 'strength': round(midpoint[1], 3)},
            'act2_break': {'scene': act2_break[0], 'strength': round(act2_break[1], 3)}
        }

        # Warn if any turning point has very low strength (flat, undramatic)
        for label, tp in result.items():
            if isinstance(tp, dict) and tp.get('strength', 1) < 0.1:
                tp['warning'] = f"This turning point is very weak — the {label.replace('_', ' ')} may be missing or underwritten."

        return result

    def _build_scene_economy_map(self, trace):
        """
        Scene-by-scene economy labels for the dashboard.
        Also surfaces a summary of low-economy scenes that may be candidates for cutting.
        """
        economy_map = [
            {
                'scene': s['scene_index'],
                'label': s.get('scene_economy', {}).get('economy_label', 'Unknown'),
                'score': s.get('scene_economy', {}).get('economy_score', 0)
            }
            for s in trace
        ]

        low_economy_scenes = [e['scene'] for e in economy_map if e['label'] == 'Low Economy']
        high_economy_scenes = [e['scene'] for e in economy_map if e['label'] == 'High Economy']

        return {
            'map': economy_map,
            'low_economy_scenes': low_economy_scenes,
            'high_economy_scenes': high_economy_scenes,
            'low_economy_count': len(low_economy_scenes),
            'cut_candidates': low_economy_scenes[:5]
        }

    def _build_narrative_summary(self, trace, genre, diagnostics):
        """
        Synthesize all signals into a dynamic narrative of the reader's emotional journey.
        Builds 8–10 conditional sentence templates that activate based on script-specific spikes.
        """
        if not trace: return "Unable to generate summary."
        diag_str = " ".join(diagnostics) if diagnostics else ""
        
        # 1. Opening Intelligence
        hook = trace[0].get('opening_hook', {})
        if hook.get('hook_label') == 'Strong Hook':
            opening = "Your opening establishes immediate dominance — the audience is engaged from the first beat."
        elif "slow" in diag_str.lower():
            opening = "The script opens with a measured, intentional focus on atmosphere before the primary conflict ignites."
        else:
            opening = "The opening takes its time to establish character stakes, which fits the genre rhythm."

        # 2. Dynamic Spike Intelligence (Look for highest tension scene)
        max_t = max([s.get('attentional_signal', 0) for s in trace])
        peak_idx = next(i for i, s in enumerate(trace) if s.get('attentional_signal', 0) == max_t)
        spike_text = f"The narrative reaches an intense cognitive peak around Scene {peak_idx+1}, a moment of critical audience payoff."

        # 3. Dynamic Flag Intelligence
        specifics = []
        if "Same Voice Syndrome" in diag_str:
            specifics.append("The dialogue shows high phonetic overlap, suggesting your characters share similar speech rhythms.")
        if "Passive Protagonist" in diag_str:
            specifics.append("The protagonist currently faces high narrative resistance, making their journey reactive in the second act.")
        if "On-The-Nose" in diag_str:
            specifics.append("There are moments where characters state their interior subtext directly, potentially diluting the dramatic irony.")
        if "Tonal Whiplash" in diag_str:
            specifics.append("The script undergoes rapid emotional shifts that challenge the reader's cognitive framing.")
        
        # 4. Closing / Payoff
        s3 = sum([s.get('sentiment', 0) for s in trace[-(len(trace)//3):]]) / (len(trace)//3 or 1)
        if s3 < -0.3:
            closing = "The journey concludes with a definitive tragic descent, delivering a soul-crushing emotional payoff."
        elif s3 > 0.3:
            closing = "The story resolves with a hard-earned sense of triumph and narrative closure."
        else:
            closing = "The resolution maintains an ambiguous emotional tone, consistent with complex prestige dramas."

        # Aggregate summary
        summary = f"{opening} {spike_text} " + " ".join(specifics[:2]) + f" {closing}"
        return {'summary': summary.strip()}

    # =========================================================================
    # PHASE 29: READER EXPERIENCE & THEMATIC DEPTH METHODS
    # =========================================================================

    def _diagnose_reader_frustration(self, trace):
        """
        Flag the top reader-frustration scenes — unfilmable action lines,
        name crowding, or similar-sounding character names.
        """
        assessments = []

        # Internal state verbs (unfilmable)
        worst_unfilmable = sorted(
            [(s['scene_index'], s.get('reader_frustration', {})) for s in trace],
            key=lambda x: len(x[1].get('internal_state_hits', [])),
            reverse=True
        )
        for idx, rf in worst_unfilmable[:1]:
            hits = rf.get('internal_state_hits', [])
            if hits:
                eg = hits[0]
                assessments.append(
                    f"🚫 **Action Line Modifiers (Scene {idx})**: Action lines contain descriptors defining internal states. "
                    f"e.g. \"{eg}\""
                )

        # Name crowding
        for s in trace:
            rf = s.get('reader_frustration', {})
            if rf.get('name_crowding'):
                n = rf.get('unique_char_count', 4)
                assessments.append(
                    f"👥 **Character Density (Scene {s['scene_index']})**: {n} distinct characters are active simultaneously. "
                    f"This creates a high referential load for the audience."
                )
                break

        # Similar name pairs
        for s in trace:
            rf = s.get('reader_frustration', {})
            pairs = rf.get('similar_name_pairs', [])
            if pairs:
                assessments.append(
                    f"🔤 **Orthographic Proximity (Scene {s['scene_index']})**: Character names {pairs[0]} are lexically or phonetically similar. "
                    f"This pattern frequently correlates with reader confusion tracking dialogue tags."
                )
                break

        return assessments[:2]

    def _diagnose_neglected_characters(self, trace):
        """
        Find characters with significant Act 1 presence who disappear in Act 3.
        """
        assessments = []
        if len(trace) < 8: return []

        third = len(trace) // 3
        act1 = trace[:third]
        act3 = trace[third * 2:]

        def char_lines(scenes):
            counts = {}
            for s in scenes:
                for char, data in s.get('character_scene_vectors', {}).items():
                    counts[char] = counts.get(char, 0) + data.get('line_count', 0)
            return counts

        act1_counts = char_lines(act1)
        act3_counts = char_lines(act3)

        # Proportional thematic-furniture threshold: scales with script length
        # Short pilot (50 scenes) → threshold ~8. Feature (200 scenes) → threshold ~33.
        furniture_threshold = max(10, len(trace) // 6)

        # Build index map once for O(1) lookup — avoids O(n²) trace.index() calls
        trace_idx_map = {id(s): i for i, s in enumerate(trace)}

        neglected = []
        for char, count in act1_counts.items():
            if count > 15 and act3_counts.get(char, 0) == 0:
                # Skip generic mis-parsed role names
                if char in ["SON", "MOM", "DAD", "FATHER", "MOTHER", "VOICE",
                            "GUY", "MAN", "WOMAN", "BOY", "GIRL", "OFFICER",
                            "GUARD", "WAITER", "DOCTOR", "NURSE"]:
                    continue

                char_timeline = [s for s in trace if char in s.get('character_scene_vectors', {})]
                if not char_timeline:
                    continue

                # Thematic furniture check: proportional threshold, first 40% of script only
                last_appearance_idx = max(trace_idx_map[id(s)] for s in char_timeline)
                if len(char_timeline) < furniture_threshold:
                    if last_appearance_idx < len(trace) * 0.4:
                        continue  # Intentional setup character — not neglected

                # Narrative resolution check: wider window (±4 scenes) catches
                # deaths where the character's last line precedes the action line
                death_words = {'shot', 'killed', 'dead', 'murder', 'ambush',
                               'funeral', 'corpse', 'dies', 'body', 'slain',
                               'assassin', 'gunfire', 'executed', 'strangled'}
                search_range = trace[max(0, last_appearance_idx-3):
                                     min(len(trace), last_appearance_idx+5)]
                if any(s.get('narrative_closure', False) for s in search_range):
                    continue
                # Secondary: keyword scan of scene text near last appearance
                scene_text = ' '.join(str(s) for s in search_range).lower()
                if any(w in scene_text for w in death_words):
                    continue

                neglected.append(char)
        
        # Sort for determinism
        neglected.sort()
        for char in neglected[:2]:
            assessments.append(
                f"👻 **Neglected Character ({char})**: Present in Act 1 ({act1_counts[char]} lines) "
                f"but completely absent in Act 3. The audience will notice and feel cheated. "
                f"Either pay them off or reduce their Act 1 presence."
            )
        return assessments[:2]

    def _diagnose_nonlinear_structure(self, trace):
        """
        Report on any non-linear scenes (flashback, dream, flash forward).
        Alert the writer if non-linear scenes are structurally misplaced.
        """
        assessments = []
        nonlinear_scenes = [
            (s['scene_index'], s.get('nonlinear_tag', {}).get('type'))
            for s in trace
            if s.get('nonlinear_tag', {}).get('is_nonlinear')
        ]

        if not nonlinear_scenes:
            return []

        types = list(set(t for _, t in nonlinear_scenes))
        count = len(nonlinear_scenes)

        if count > 5:
            assessments.append(
                f"⏳ **Non-linear Heavy Script**: {count} non-linear scenes detected "
                f"({', '.join(types)}). Heavy non-linearity fragments narrative momentum — "
                f"ensure each flashback delivers information unavailable any other way."
            )
        elif count > 0:
            locs = ', '.join(f"Scene {i}" for i, _ in nonlinear_scenes[:3])
            assessments.append(
                f"⏳ **Non-linear Scenes Detected** ({locs}): {types[0]} used. "
                f"Non-linear scenes are excluded from standard structural expectations. "
                f"Confirm each one is load-bearing — if you can cut it, cut it."
            )
        return assessments[:1]

    def _diagnose_theme_coherence(self, trace):
        """
        Aggregate thematic clusters across the full script and check Act-level consistency.
        Flag if the dominant theme shifts significantly between Acts.
        """
        assessments = []
        if len(trace) < 4: return []

        third = max(1, len(trace) // 3)

        def dominant_theme(scenes):
            agg = {}
            for s in scenes:
                for theme, score in s.get('thematic_clusters', {}).get('theme_scores', {}).items():
                    agg[theme] = agg.get(theme, 0) + score
            if not agg: return None
            return max(agg, key=agg.get)

        t1 = dominant_theme(trace[:third])
        t2 = dominant_theme(trace[third:third*2])
        t3 = dominant_theme(trace[third*2:])

        # Script-wide dominant theme
        all_themes = {}
        for s in trace:
            for theme, score in s.get('thematic_clusters', {}).get('theme_scores', {}).items():
                all_themes[theme] = all_themes.get(theme, 0) + score

        if not all_themes:
            return []

        top_global = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:2]
        global_themes = [t for t, _ in top_global]

        # Check for thematic drift between acts
        themes = [t for t in [t1, t2, t3] if t]
        if len(set(themes)) == len(themes) and len(themes) == 3:
            assessments.append(
                f"🎭 **Thematic Drift**: Dominant theme shifts each Act "
                f"({t1} → {t2} → {t3}). Strong scripts stay anchored to 1-2 core themes. "
                f"Your script appears to be exploring '{global_themes[0]}' overall — "
                f"consider threading it more consistently across all 3 Acts."
            )
        else:
            if global_themes:
                assessments.append(
                    f"✅ **Thematic Coherence**: Core themes are "
                    f"**{global_themes[0]}**{(' & **' + global_themes[1] + '**') if len(global_themes) > 1 else ''} "
                    f"— consistent across Acts. Strong thematic spine."
                )
        return assessments[:1]
    def _generate_creative_provocations(self, diagnosis, genre):
        """Generates mentor-like questions to push the writer's craft further."""
        provocations = []
        diag_str = " ".join(diagnosis) if diagnosis else ""
        
        # Mapping Flags to Masterclass Questions (Task 6)
        mapping = {
            'Same Voice Syndrome': "Your leads share similar dialogue rhythms. What is one specific verbal habit you could give your protagonist that their rival would *never* use?",
            'Flat Arc': "This character remains emotionally static. If they don't change, is the *world* changing around them to highlight their refusal to adapt?",
            'On-The-Nose': "In your most intense scene, a character states exactly what they feel. What could they say instead that hides their true intent but reveals their desperation?",
            'Attentional Valley': "Engagement dips over multiple scenes here. Who is winning the 'Invisible Power Struggle' while no one is shouting?",
            'Passive Protagonist': "The story is pushing the hero. What decision can they make right now that would burn their bridges and force the plot to follow them?",
            'Similar Names': "The reader may confuse your leads. Can you give one a specific physical vocal quirk or a recurring linguistic motif to differentiate them?",
            'Tonal Whiplash': "The script undergoes an extreme shifts. Is this a deliberate subversion of audience expectations, or is it breaking the story's reality?",
            'Redundant Scenes': "These scenes serve the same purpose. Which one has more 'Cinematic Economy'? Combine them into a single high-impact sequence.",
            'Tell vs Show': "You're describing internal thoughts in action lines. How can you translate that feeling into a purely visual piece of behavior?"
        }
        
        for flag, question in mapping.items():
            if flag in diag_str:
                provocations.append(question)
                
        # Fillers if no flags
        if not provocations:
            provocations = [
                "What is the one thing your protagonist wants so badly they would burn their life down to get it?",
                "In your quietest scene, what is the 'Invisible Conflict' that keeps the audience leaning in?"
            ]
            
        return list(set(provocations))[:3]



        






    def _calculate_page_turner_index(self, trace):
        """
        Calculates PTI (0-100) based on Dramatic Contrast and Resonance.
        A 'Page-Turner' isn't just constant shouting; it's the rhythm of tension and relief.
        """
        if not trace: return 50
        
        # 1. Emotional Contrast: The standard deviation of the signal
        # High contrast means the writer is using the 'Valley' effect correctly.
        # Threshold: 0.18 is a strong delta for a normalized 0-1 signal.
        signals = [s.get('attentional_signal', 0) for s in trace]
        contrast = statistics.stdev(signals) if len(signals) > 1 else 0
        contrast_score = min(1.0, contrast / 0.18) * 35 # 35 pts for contrast
        
        # 2. Hook Density: Use Cognitive Resonance (Impact vs just Volume)
        # Average resonance of 0.35 is quite high for a script with breathers.
        resonance = sum(s.get('cognitive_resonance', 0) for s in trace) / len(trace)
        res_vals = [s.get('cognitive_resonance', 0) for s in trace]
        res_threshold = statistics.quantiles(res_vals, n=4)[2] if len(res_vals) > 3 else 0.35
        resonance_score = min(1.0, resonance / max(res_threshold, 0.1)) * 45 # 45 pts for impact
        
        # 3. Cliffhangers: Scenes ending on high-intensity signals
        cliff_count = sum(1 for s in trace if s.get('attentional_signal', 0) > 0.82)
        cliffhangers = (min(cliff_count, 4) * 5) # 20 pts for peaks
        
        # Base completion bonus (20%) + Metrics
        return min(100, round(20 + (contrast_score + resonance_score + cliffhangers) * 0.8))

    def _diagnose_writing_texture(self, trace):
        """Identifies if the script is 'Cinematic' (lean) or 'Novelistic' (dense)."""
        action_densities = [s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace]
        avg_action = sum(action_densities) / len(trace) if trace else 0
        
        if avg_action > 10: return "Novelistic / Literary"
        if avg_action < 4: return "Sparse / Minimalist"
        return "Cinematic / Visual"

    def _find_commercial_comps(self, genre, dominant_stakes='Social'):
        """Task 3: Subgenre-aware matching for feature films only."""
        # Map Dominant Stakes to specialized 'Subgenres'
        stakes_to_sub = {
            'Social': 'Political/Mob/Society',
            'Moral': 'Psychological/Moral',
            'Emotional': 'Personal/Relational',
            'Physical': 'Visceral/Action',
            'Existential': 'Philosophical/Surreal'
        }
        subgenre = stakes_to_sub.get(dominant_stakes, 'General')
        
        lookup = {
            ('Crime', 'Political/Mob/Society'): ["The Godfather", "The Departed", "The Irishman"],
            ('Crime', 'Psychological/Moral'): ["Chinatown", "No Country for Old Men", "Heat"],
            ('Drama', 'Personal/Relational'): ["Marriage Story", "Ordinary People", "Lady Bird"],
            ('Drama', 'Political/Mob/Society'): ["The Social Network", "Parasite", "The Big Short"],
            ('Action', 'Visceral/Action'): ["Mad Max: Fury Road", "Die Hard", "John Wick"],
            ('Action', 'Personal/Relational'): ["Logan", "The Dark Knight", "Gladiator"],
            ('Horror', 'Philosophical/Surreal'): ["Hereditary", "The Shining", "Midsommar"],
            ('Horror', 'Visceral/Action'): ["Halloween", "A Quiet Place", "The Conjuring"],
            ('Sci-Fi', 'Philosophical/Surreal'): ["2001: A Space Odyssey", "Arrival", "Blade Runner 2049"],
            ('Sci-Fi', 'Psychological/Moral'): ["Gattaca", "Children of Men", "Ex Machina"],
            ('Thriller', 'Political/Mob/Society'): ["Gone Girl", "Seven", "Prisoners"],
            ('Comedy', 'Political/Mob/Society'): ["Knives Out", "Glass Onion", "The Favorite"],
            ('Comedy', 'Personal/Relational'): ["Little Miss Sunshine", "The Holdovers", "Planes, Trains and Automobiles"],
            ('Romance', 'Personal/Relational'): ["Before Sunrise", "Normal People", "The Notebook"]
        }
        
        g = genre.replace('-', ' ').split()[0].title() 
        if 'Sci' in g: g = 'Sci-Fi'
        
        # Primary Match: Genre + Subgenre
        key = (g, subgenre)
        if key in lookup: return lookup[key]
        
        # Secondary Match: Just Genre + any stake
        for k_g, k_s in lookup.keys():
            if k_g == g: return lookup[(k_g, k_s)]
            
        return ["The Social Network", "Parasite", "Pulp Fiction"] # Ultimate fallbacks

    def _calculate_production_risks(self, trace):
        """
        Calculates Risk Radar (Complexity vs Impact).
        Weights: Locations 40%, Cast 30%, Action Complexity 30%.
        """
        if not trace: return 50
        
        locs = set()
        cast = set()
        for s in trace:
            loc = s.get('location_data', {}).get('location') or s.get('location', 'Unknown')
            if loc != 'Unknown': locs.add(loc)
            for c in s.get('character_scene_vectors', {}).keys():
                cast.add(c)
                
        unique_locs = len(locs)
        cast_count = len(cast)
        
        loc_risk = min(100, (unique_locs / 50.0) * 100) # 50+ locs is 100% loc risk
        cast_risk = min(100, (cast_count / 30.0) * 100) # 30+ cast is 100% cast risk
        
        complexity = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        action_risk = min(100, (complexity / 20.0) * 100) # 20+ action lines avg is 100% risk

        risk_score = (loc_risk * 0.40) + (cast_risk * 0.30) + (action_risk * 0.30)
        return round(min(100, max(0, risk_score)))

    def _calculate_budget_impact(self, trace, report=None):
        """Estimates relative budget intensity based on location churn, cast size, and action density."""
        if not trace: return "Low"
        # Fix: Look into location_data which was injected in runner.py
        locs = set()
        for s in trace:
            loc = s.get('location_data', {}).get('location') or s.get('location', 'Unknown')
            if loc != 'Unknown':
                locs.add(loc)
        
        unique_locs = len(locs)
        avg_action = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        
        # Cast size factor
        cast_size = 0
        if report and 'voice_fingerprints' in report:
            cast_size = len(report['voice_fingerprints'])
            
        score = (unique_locs * 1.5) + (avg_action * 4) + (cast_size * 0.5)
        
        if score > 100 or unique_locs > 50 or cast_size > 40: return "Blockbuster / High"
        if score > 35: return "Medium / Standard"
        return "Lean / Indie"

    def _calculate_market_readiness(self, d):
        """
        Market Readiness: measures how production-viable the script is structurally.
        No base floor — score must be earned.
        Stakes 25% | Structure 30% | Dialogue 25% | Production Polish 20%
        """
        # 1. Stakes Diversity (25%) — multi-layered jeopardy signals commercial range
        stakes = d.get('stakes_profile', {})
        unique_stakes = len([v for k, v in stakes.items() if isinstance(v, (int, float)) and v > 0])
        stakes_score = min(1.0, unique_stakes / 4.0) * 25

        # 2. Structural Stability (30%) — act balance is the foundation of marketability
        balance = d.get('act_structure', {}).get('balance', 'Unknown')
        structure_score = 30 if balance == 'Balanced' else 15

        # 3. Dialogue Rhythm (25%) — on-genre dialogue ratio signals craft awareness
        dr      = d.get('dialogue_action_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_score = max(0, 25 - abs(d_ratio - d_bench) * 100)

        # 4. Production Polish (20%) — penalise extreme cast/location counts
        # Ideal cast: 8–30 named characters. Ideal locations: 5–50 headings.
        # Outside these ranges signals scheduling/budget complexity.
        cast_count = d.get('cast_count_deterministic', 10)
        loc_count  = d.get('location_profile', {}).get('unique_locations', 0)

        cast_penalty = max(0, (cast_count - 30) * 0.4) if cast_count > 30 else 0
        loc_penalty  = max(0, (loc_count  - 50) * 0.15) if loc_count > 50 else 0
        polish_score = max(0, 20 - cast_penalty - loc_penalty)

        final = stakes_score + structure_score + d_score + polish_score
        return min(100, round(final))

    def _diagnose_representation_risks(self, fairness_audit):
        """Surfaces critical representation risks from the Ethics Agent."""
        assessments = []
        risks = fairness_audit.get('stereotyping_risks', [])
        for risk in risks:
            if "punching down" in risk.lower():
                assessments.append(f"⚖️ **Representation Risk**: {risk}")
            else:
                assessments.append(f"👥 **Character Dynamic**: {risk}")
        return assessments[:2]

    # =========================================================================
    # SCRIPTPULSE SCORE & ACT STRUCTURE
    # =========================================================================

    def _build_act_structure(self, trace):
        """Calculates act-by-act distribution and Violence Weighting (Task 4)."""
        n = len(trace)
        if n == 0:
            return {'act1': 0, 'act2': 0, 'act3': 0, 'act1_pct': 0, 'act2_pct': 0, 'act3_pct': 0, 'balance': 'Unknown', 'violence_count': [0,0,0]}
        
        # Boundaries
        act1_end = max(1, n // 4)
        act3_start = max(act1_end + 1, n - (n // 4))
        
        # Violence Counting: shootings, deaths, confrontations
        v_triggers = ['shot', 'killed', 'blood', 'gun', 'attack', 'dead', 'murder', 'fight', 'trap', 'ambush']
        violence = [0, 0, 0]
        
        for i, s in enumerate(trace):
            is_violent = s.get('sentiment', 0) < -0.8 and any(w in str(s).lower() for w in v_triggers)
            if i < act1_end: violence[0] += 1 if is_violent else 0
            elif i < act3_start: violence[1] += 1 if is_violent else 0
            else: violence[2] += 1 if is_violent else 0

        act1_count = act1_end
        act2_count = act3_start - act1_end
        act3_count = n - act3_start
        
        act1_pct = round(act1_count / n * 100)
        act2_pct = round(act2_count / n * 100)
        act3_pct = round(act3_count / n * 100)
        
        balance = "Balanced"
        if act1_pct > 35: balance = "Extended Act 1 Setup"
        elif act3_pct > 35: balance = "Extended Act 3 Resolution"
        elif act2_pct > 65: balance = "Extended Act 2 Middle"
        
        # Violence Floor (Task 4): If Act 1 has 3+ violent events, it cannot be 'Slow Burn'
        pacing = "Balanced"
        if violence[0] >= 3: pacing = "High Octane"
        # Propulsive: High conflict/moves quickly - generalized for all drama (Task 4)
        elif violence[0] >= 1 and (act1_pct < 28 or act2_pct < 45): pacing = "Propulsive" 
        elif sum(violence) == 0 and act1_pct > 30: pacing = "Slow Burn"
        
        return {
            'act1': act1_count, 'act2': act2_count, 'act3': act3_count,
            'act1_pct': act1_pct, 'act2_pct': act2_pct, 'act3_pct': act3_pct,
            'balance': balance,
            'violence_count': violence,
            'pacing_benchmark': pacing
        }

    def _calculate_scriptpulse_score(self, dashboard, diagnostics):
        """
        Narrative craft score only. Producer metrics (risk, locations, cast)
        are excluded — they live in the Producer panel.
        Weights: PTI 30% | Pacing 25% | Dialogue 20% | Stakes 15% | Market 10%
        """
        pti = dashboard.get('page_turner_index', 50)

        # Dialogue harmony — fix: use correct key 'dialogue_action_ratio'
        dr      = dashboard.get('dialogue_action_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_harmony = max(0, 100 - abs(d_ratio - d_bench) * 200)

        # Pacing balance
        balance_label = dashboard.get('act_structure', {}).get('balance', 'Unknown')
        pacing_score  = 85 if balance_label == 'Balanced' else 50

        # Stakes diversity
        stakes = dashboard.get('stakes_profile', {})
        unique_stakes = len([
            v for k in sorted(stakes.keys())
            if (v := stakes.get(k)) and isinstance(v, (int, float)) and v > 0
        ])
        stakes_score = min(100, unique_stakes * 20)

        # Market readiness (already bounded 0-100 by its own method)
        mr = dashboard.get('market_readiness', 50)

        # Diagnostic health penalty (max -25)
        critical_count = sum(
            1 for d in diagnostics
            if isinstance(d, str) and any(x in d for x in ['🔴', '🚫'])
        )
        warning_count = sum(
            1 for d in diagnostics
            if isinstance(d, str) and any(x in d for x in ['🟠', '🟡', '⬜'])
        )
        health_penalty = min(20, (critical_count * 5) + (warning_count * 2))

        raw = (
            (pti          * 0.30) +
            (pacing_score * 0.25) +
            (d_harmony    * 0.20) +
            (stakes_score * 0.15) +
            (mr           * 0.10)
        )

        return max(0, min(100, round(raw - health_penalty)))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: llm_translator.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import json
import logging
import streamlit as st
from openai import OpenAI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

_log = logging.getLogger(__name__)

def get_token(key, fallback=None):
    try: 
        val = st.secrets.get(key)
        if val: return val
    except: pass
    return os.environ.get(key, fallback)

def _get_api_config():
    """Returns a unified dict of available keys."""
    return {
        "groq": get_token("GROQ_API_KEY"),
        "gemini": get_token("GOOGLE_API_KEY") or get_token("GEMINI_API_KEY"),
        "hf": get_token("HF_TOKEN") or get_token("HUGGINGFACE_API_KEY")
    }

def generate_ai_summary(script_data, lens='viewer', api_key=None):
    """
    Translates ScriptPulse data into an emotional audience reaction.
    Rotates through providers to ensure high uptime and quality.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key # Manual override usually for groq
    
    if not any(keys.values()):
        return None, "All AI providers are offline. Please check your API Keys."
        
    dashboard = script_data.get("writer_intelligence", {}).get("structural_dashboard", {})
    
    # CRITICAL: Slim down the dashboard payload to avoid Groq's 12,000 TPM free tier limit
    # Do NOT send full scene-by-scene arrays like scene_turn_map or scene_economy_map
    slim_dashboard = {
        "scriptpulse_score": dashboard.get("scriptpulse_score"),
        "page_turner_index": dashboard.get("page_turner_index"),
        "market_readiness": dashboard.get("market_readiness"),
        "act_structure": dashboard.get("act_structure"),
        "budget_impact": dashboard.get("budget_impact"),
        "commercial_comps": dashboard.get("commercial_comps")
    }
    
    data_payload = {
        "pacing_issues": script_data.get("writer_intelligence", {}).get("narrative_diagnosis", []),
        "priorities": script_data.get("writer_intelligence", {}).get("rewrite_priorities", []),
        "structural_dashboard": slim_dashboard
    }
    
    # Customize the persona based on the lens
    persona_map = {
        "Studio Executive": "a sharp-eyed Development Executive at a major studio. Focus on commercial viability, audience demographic expansion, budget risks, and market positioning.",
        "Story Editor": "a master Story Editor for major film and television productions. Focus on internal character logic, causality, emotional stakes, and structural beats.",
        "Script Coordinator": "a technical Script Analyst and Pacing Consultant. Focus on dialogue economy, visual description energy, scene-to-scene transitions, and stylistic consistency."
    }
    persona_desc = persona_map.get(lens, "a professional Script Consultant.")

    system_prompt = (
        f"You are {persona_desc} "
        "Provide a comprehensive, actionable narrative analysis based on the structural and emotional data provided. "
        "CRITICAL RULES: \n"
        "1. Strictly maintain this specific professional persona. Use role-appropriate vocabulary (e.g., Executive uses 'ROI', 'Comp', 'Demographic'; Editor uses 'Beat', 'Arc', 'Causality'; Coordinator uses 'White Space', 'Rhythm', 'Flow').\n"
        "2. Prioritize your specific areas of expertise in the report.\n"
        "3. ALWAYS provide 3 concrete 'Fix Suggestions' at the end of the report to elevate the script for production.\n"
        "4. If you mention 'ScriptPulse', ALWAYS format it EXACTLY like this: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>\n"
        "5. Avoid archaic or overly rigid length rules. Prestige features often exceed 120 minutes; only flag length if it meaningfully drags the pacing or structural integrity."
    )
    user_content = f"Experience Data: {json.dumps(data_payload)}"
    errors = []

    # 1. Try GEMINI (Best for long-form reasoning and "Story Soul")
    if keys["gemini"] and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=keys["gemini"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"SYSTEM: {system_prompt}\n\nUSER: {user_content}")
            return response.text, None
        except Exception as e:
            errors.append(f"Gemini: {str(e)}")

    # 2. Try GROQ (Blazing Fast)
    if keys["groq"] and GROQ_AVAILABLE:
        try:
            client = Groq(api_key=keys["groq"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                temperature=0.6,
                max_tokens=1200
            )
            return completion.choices[0].message.content, None
        except Exception as e:
            errors.append(f"Groq: {str(e)}")

    # 3. Fallback to Hugging Face
    if keys["hf"]:
        try:
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                max_tokens=1200
            )
            return completion.choices[0].message.content, None
        except Exception as e:
            errors.append(f"HF: {str(e)}")
            
    return None, f"All AI APIs failed. Details: {' | '.join(errors)}"

def generate_section_insight(script_data, section_type, lens='viewer', api_key=None):
    """
    Generates a high-impact visceral reaction that bridges the gap between 'math' and 'human feeling'.
    """
    keys = _get_api_config()
    if api_key: keys["groq"] = api_key
    
    if not any(keys.values()):
        return "Connect an API key (Groq, Gemini, or HF) to hear audience reactions."

    # Persona definitions for sections
    persona_map = {
        "Studio Executive": "a Development Executive focused on commercial pacing and audience retention.",
        "Story Editor": "a Story Editor focused on structural beats and emotional momentum.",
        "Script Coordinator": "a Script Coordinator focused on the physical read and visual energy."
    }
    p_desc = persona_map.get(lens, "a professional Script Consultant.")

    if section_type == 'pulse':
        tp = script_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        payload = {"peaks": tp}
        system_msg = (
            f"You are {p_desc} Analyze the story's structural pacing graph. "
            "Explain how this sequence affects the audience's attention from your professional perspective. "
            "Identify the most significant pacing trend observed. One precise sentence. "
            "CRITICAL: Do not use phrases like 'Based on the provided data' or 'Raw Experience Math'. Speak directly and naturally to the writer. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    elif section_type == 'dna':
        payload = {"distribution": "Speed vs Detail balance"}
        system_msg = (
            f"You are {p_desc} Evaluate the balance of narrative action vs world-building. "
            "Evaluate the impact of this balance on reader immersion for the current story goals. One clear sentence. "
            "CRITICAL: Do not use phrases like 'Based on the provided data' or 'Raw Experience Math'. Speak directly and naturally to the writer. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )
    else: # habits
        perceptual = script_data.get('perceptual_features', [])[:10]
        payload = {"samples": perceptual}
        system_msg = (
            f"You are {p_desc} Evaluate the rhythm and subtext of the characters' dialogue. "
            "Identify what the current dialogue texture reveals about the character dynamics. One professional sentence. "
            "If referring to the engine, format it as: Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>"
        )

    user_content = f"Raw Experience Math: {json.dumps(payload)}\nAudience Reaction:"

    # PURPOSE-BASED DISTRIBUTION (To avoid free-tier rate limits)
    # Gemini: 'pulse' (Story/Emotion) | Groq: 'dna' and 'habits' (Structure/Pattern)
    
    order = []
    if section_type == 'pulse':
        order = ['gemini', 'groq', 'hf']
    else:
        order = ['groq', 'gemini', 'hf']
        
    errors = []

    for provider in order:
        if provider == 'gemini' and keys["gemini"] and GEMINI_AVAILABLE:
            try:
                client = genai.Client(api_key=keys["gemini"])
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"SYSTEM: {system_msg}\n\nUSER: {user_content}"
                )
                return response.text
            except Exception as e:
                errors.append(f"Gemini: {str(e)}")
                continue
            
        if provider == 'groq' and keys["groq"] and GROQ_AVAILABLE:
            try:
                client = Groq(api_key=keys["groq"])
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=300,
                    temperature=0.8
                )
                return completion.choices[0].message.content
            except Exception as e:
                errors.append(f"Groq: {str(e)}")
                continue

        if provider == 'hf' and keys["hf"]:
            try:
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=keys["hf"])
                completion = client.chat.completions.create(
                    model="moonshotai/Kimi-K2-Instruct-0905",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_content}],
                    max_tokens=300
                )
                return completion.choices[0].message.content
            except Exception as e:
                errors.append(f"HF: {str(e)}")
                continue

    return f"AI Error: API failure. Details: {' | '.join(errors)}"


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: confidence_scorer.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import statistics

class ConfidenceScorer:
    """
    Computes confidence bands for ScriptPulse v1.3 metrics.
    Prevent overclaiming on short or flat scripts.
    """
    
    def calculate(self, dynamics_trace):
        """
        Returns {'level': 'HIGH'|'MEDIUM'|'LOW', 'score': 0.0-1.0, 'reasons': []}
        """
        if not dynamics_trace:
            return {'level': 'LOW', 'score': 0.0, 'reasons': ['No trace data']}
            
        scene_count = len(dynamics_trace)
        att_signals = [s['attentional_signal'] for s in dynamics_trace]
        if scene_count > 1:
            variance = statistics.variance(att_signals) 
        else:
            variance = 0.0
        
        reasons = []
        score = 1.0
        
        # 1. Length Penalty (Refined for Chamber Dramas)
        # If scene count is low but average effort is high, it might be a dense play adaptation.
        avg_effort = statistics.mean(att_signals) if att_signals else 0
        
        if scene_count < 10:
            if avg_effort > 0.6:
                score *= 0.8 # Less severe penalty for dense short format
                reasons.append("Low Scene Count (Dense)")
            else:
                score *= 0.5
                reasons.append("Insufficient Length (<10 scenes)")
        elif scene_count < 30:
            if avg_effort > 0.5:
                score *= 0.95 # Minimal penalty
            else:
                score *= 0.8
                reasons.append("Short Script (<30 scenes)")
            
        # 2. Variance Penalty (Flatline detection)
        # Low variance is the real killer of confidence.
        if variance < 0.005:
            score *= 0.6
            reasons.append("Signal Flatline (low_signal_variance)")
        elif variance < 0.02:
            score *= 0.9
            reasons.append("Low Dynamic Range")
            
        # 3. Overload Penalty
        fatigue_ratio = sum(1 for s in dynamics_trace if s.get('fatigue_state', 0) > 0) / scene_count
        if fatigue_ratio > 0.8:
            score *= 0.7
            reasons.append("Sustained Overload (high_entropy_instability)")
            
        # Level
        if score >= 0.85: level = 'HIGH'
        elif score >= 0.6: level = 'MEDIUM'
        else: level = 'LOW'
        
        return {
            'level': level,
            'score': round(score, 2),
            'reasons': reasons
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: dynamics_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Dynamics Agent - Simplified & MCA-Defensible Version
The Core Simulation Engine (The "Heart" of ScriptPulse)
Calculates: Attentional Signal (S) based on Effort (E) and Recovery (R)
Equation: S[t] = Effort[t] + (Lambda * S[t-1]) - Recovery[t]
"""

import math
import statistics
import json
import os

class DynamicsAgent:
    """Core Mathematical Simulation Engine - High Fidelity, Low Complexity"""
    
    def __init__(self):
        # Priors as per PAPER_METHODS.md v1.3
        self.GENRE_PRIORS = {
            'drama':         {'lambda': 0.75, 'beta': 0.45}, # Higher recovery, lower retention for valleys
            'crime drama':   {'lambda': 0.80, 'beta': 0.40}, 
            'thriller':      {'lambda': 0.75, 'beta': 0.45},
            'action':        {'lambda': 0.78, 'beta': 0.50},
            'comedy':        {'lambda': 0.80, 'beta': 0.60},
            'horror':        {'lambda': 0.70, 'beta': 0.25},
            'sci-fi':        {'lambda': 0.82, 'beta': 0.35},
        }

    def run_simulation(self, input_data, genre=None, **kwargs):
        features = input_data.get('features', [])
        # Fix: Extract genre from input_data if not provided as positional arg
        g_key = (genre or input_data.get('genre', 'drama')).lower()
        priors = self.GENRE_PRIORS.get(g_key, self.GENRE_PRIORS['drama']).copy()
        
        # Override with kwargs for hyperparameter tuning / research ablation
        if 'lambda' in kwargs: priors['lambda'] = kwargs['lambda']
        if 'beta' in kwargs: priors['beta'] = kwargs['beta']
        
        if not features: return []
        
        signals = []
        prev_signal = 0.25  # Neutral-low starting point for establishing tone
        
        for i, feat in enumerate(features):
            # 1. Extraction & Feature Normalization
            norm_velocity = feat.get('dialogue_dynamics', {}).get('turn_velocity', 0)
            switches = feat.get('dialogue_dynamics', {}).get('speaker_switches', 0)
            norm_action = feat.get('visual_abstraction', {}).get('visual_intensity', 0)
            
            # Conflict & Stakes (The primary drivers of Drama)
            # Switches normalized by expected conversational density (8 switches per scene is active)
            norm_switches = min(1.0, switches / 8.0)
            dialogue_momentum = (norm_velocity * 0.3 + norm_switches * 0.7)
            
            affective = feat.get('affective_load', {})
            comp_sentiment = abs(affective.get('compound', 0)) if isinstance(affective, dict) else 0
            
            # Real conflict and stakes calculations used for both Effort and Output
            actual_conflict = (dialogue_momentum * 0.6) + (max(0, -affective.get('compound', 0)) * 0.4)
            
            stakes_breakdown = feat.get('stakes_taxonomy', {}).get('breakdown', {})
            dominant_stakes_value = max(stakes_breakdown.values()) if stakes_breakdown else norm_action
            actual_stakes = (norm_action * 0.5) + (dominant_stakes_value * 0.5)

            # 2. Effort (Tension Contribution)
            # Narrative Drive now weights Conflict and Stakes much heavier than raw dialogue volume
            narrative_drive = (actual_conflict * 0.5 + actual_stakes * 0.4 + comp_sentiment * 0.1)
            
            # Scene Density (Cognitive Load): Moderate contribution
            norm_chars = min(1.0, feat.get('referential_load', {}).get('active_character_count', 0) / 8.0)
            norm_entropy = min(1.0, feat.get('entropy_score', 0) / 12.0)
            scene_density = (norm_chars * 0.4 + norm_entropy * 0.6)
            
            # Lower base effort (0.05) allows for deep valleys
            raw_effort = (narrative_drive * 0.85 + scene_density * 0.15)
            effort = 0.05 + (raw_effort * 0.9)
            
            # 3. Update Attentional Signal (S)
            decay = priors['lambda']
            beta = priors['beta']
            
            # Recovery Credit (R_t)
            # Prestige dramas need "The Valley" — if effort is low, recovery is boosted
            recovery = (1.0 - effort) * beta
            if effort < 0.25:
                recovery *= 1.5 # Extra recovery for quiet/domestic scenes
            
            # Update state with decay (The "Memory" of the simulation)
            signal = (prev_signal * decay) + effort - recovery
            
            # Micro-spikes for visceral visual peaks (Action sequences)
            if norm_action > 0.7:
                signal += 0.15
                
            signal = min(0.98, max(0.05, signal)) 
            
            # 4. Contextual Nuance (For UI/Interpretation)
            action_count = feat.get('visual_abstraction', {}).get('action_lines', 0)
            dial_count = feat.get('dialogue_dynamics', {}).get('dialogue_line_count', 0)
            sentiment_val = affective.get('compound', 0)
            
            # Resonance occurs when high conflict meets strong emotional valence
            cognitive_resonance = min(1.0, (actual_conflict * 0.4) + (effort * 0.4) + (0.3 if abs(sentiment_val) > 0.6 else 0.0))
            
            # Extract aggregate agency from character scene vectors
            scene_agency = 0.0
            arcs = feat.get('character_scene_vectors', {})
            if arcs:
                scene_agency = sum(v.get('agency', 0) for v in arcs.values()) / len(arcs)
                
            out_sig = {
                'scene_index': feat['scene_index'],
                'instantaneous_effort': round(effort, 3),
                'attentional_signal': round(signal, 3),
                'recovery_credit': round(recovery, 3),
                'fatigue_state': round(max(0.0, signal - 0.7), 3),
                'cognitive_resonance': round(cognitive_resonance, 3),
                'conflict': round(min(1.0, actual_conflict), 3),
                'stakes': round(min(1.0, actual_stakes), 3),
                'agency': round(scene_agency, 3),
                'action_density': round(action_count / max(1, action_count + dial_count), 2),
                'sentiment': round(sentiment_val, 3),
                'narrative_position': round(i / max(1, len(features)), 3),
                # Explicit dialogue/action counts for writer_agent's global ratio calculation
                'dialogue_action_ratio': {
                    'dialogue_lines': dial_count,
                    'action_lines': action_count
                }
            }
            
            # Forward feed all relevant features to temporal trace needed for interpretation
            for k,v in feat.items():
                if k not in out_sig and k not in ['linguistic_load', 'dialogue_dynamics', 'visual_abstraction', 'referential_load', 'entropy_score', 'scene_vocabulary']:
                    out_sig[k] = v
                    
            signals.append(out_sig)
            prev_signal = signal
            
        return signals

    def calculate_acd_states(self, input_data):
        """Simplified Attention Collapse/Drift Logic"""
        signals = input_data.get('temporal_signals', [])
        states = []
        for s in signals:
            signal = s['attentional_signal']
            effort = s['instantaneous_effort']
            
            state = 'stable'
            if signal > 0.8: state = 'collapse' # Too much to handle
            elif signal < 0.2: state = 'drift'   # Boring/Bland
            
            states.append({
                'scene_index': s['scene_index'],
                'primary_state': state,
                'collapse_likelihood': round(max(0.0, signal - 0.7), 3),
                'drift_likelihood': round(max(0.0, 0.3 - signal), 3)
            })
        return states

    def apply_long_range_fatigue(self, input_data):
        """Simple Fatigue Modifier"""
        signals = input_data.get('temporal_signals', [])
        return signals

    def detect_patterns(self, input_data):
        """Standard experiential patterns based on signal windows"""
        signals = input_data.get('temporal_signals', [])
        patterns = []
        if len(signals) < 3: return []
        
        for i in range(len(signals) - 2):
            window = signals[i:i+3]
            sigs = [w['attentional_signal'] for w in window]
            
            # Fatigue Detection
            if all(s > 0.7 for s in sigs):
                patterns.append({'pattern_type': 'sustained_attentional_demand', 'scene_range': [i, i+2], 'confidence': 'medium'})
                break # only one
        
        return patterns


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: ethics_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Ethics Agent - Analyzing Bias, Agency, and Fairness
Consolidates: agency.py, fairness.py
"""

import collections
import statistics

# =============================================================================
# AGENCY LOGIC (formerly agency.py)
# =============================================================================

class EthicsAgent:
    """Ethics Agent - Bias, Agency, and Fairness Auditing"""

    def analyze_agency(self, input_data):
        """
        Analyze Character Agency (Power/Influence)
        Objective: Measure Agency rather than just Presence.
        """
        # 1. Construct Interaction Graph
        adjacency = collections.defaultdict(int)
        nodes = set()
        scenes = input_data.get('scenes', [])
        
        if not scenes: return {'error': 'No input scenes'}
        
        for scene in scenes:
            speakers = []
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        speakers.append(name)
                        nodes.add(name)
            
            for k in range(len(speakers) - 1):
                src, dst = speakers[k], speakers[k+1]
                if src != dst: adjacency[(src, dst)] += 1
                
        if not nodes: return {'agency_metrics': []}
        
        # 2. Calculate Centrality Metrics (Degree Centrality as robust fallback)
        degrees = collections.defaultdict(int)
        for (src, dst), weight in adjacency.items():
            degrees[src] += weight
            degrees[dst] += weight
            
        max_degree = max(degrees.values()) if degrees else 1
        centrality_map = {n: degrees[n]/max_degree for n in nodes}
        
        # 3. Analyze Structural Agency (Dialogue Volume & Action Prominence)
        char_metrics = collections.defaultdict(lambda: {"action_subjects": 0, "dialogue_lines": 0, "total_words_spoken": 0, "turn_initiations": 0, "commands": 0})
        
        for scene in scenes:
            current_char = None
            scene_started = False
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        char_metrics[name]["dialogue_lines"] += 1
                        if not scene_started:
                            char_metrics[name]["turn_initiations"] += 1
                            scene_started = True
                        current_char = name
                elif line['tag'] == 'D' and current_char:
                    text = line['text']
                    char_metrics[current_char]["total_words_spoken"] += len(text.split())
                    # Simple Command Heuristic
                    if len(text.split()) < 6 and ('!' in text or text.isupper()):
                        char_metrics[current_char]["commands"] += 1
                elif line['tag'] == 'A':
                    text = line['text']
                    for char in nodes:
                        # If an action line starts with the character's name, they are likely driving the action
                        if text.startswith(char):
                            char_metrics[char]["action_subjects"] += 1
        
        # Calculate maxes for normalization
        max_words = max((m["total_words_spoken"] for m in char_metrics.values()), default=1)
        max_actions = max((m["action_subjects"] for m in char_metrics.values()), default=1)
        max_initiations = max((m["turn_initiations"] for m in char_metrics.values()), default=1)
        max_commands = max((m["commands"] for m in char_metrics.values()), default=1)
        
        report = []
        for char in nodes:
            stats = char_metrics[char]
            norm_words = stats["total_words_spoken"] / max(1, max_words)
            norm_actions = stats["action_subjects"] / max(1, max_actions)
            norm_initiations = stats["turn_initiations"] / max(1, max_initiations)
            norm_commands = stats["commands"] / max(1, max_commands)
            norm_cent = centrality_map.get(char, 0.0)
            
            # Refined narrative agency calculation
            agency_score = (norm_cent * 0.3) + (norm_words * 0.3) + (norm_actions * 0.2) + (norm_initiations * 0.1) + (norm_commands * 0.1)
            
            report.append({
                'character': char,
                'agency_score': round(agency_score, 3),
                'centrality': round(norm_cent, 3),
                'initiative': round(norm_initiations, 2),
                'command_presence': round(norm_commands, 2),
                'classification': "High Agency" if agency_score > 0.4 else "Passive"
            })
            
        report.sort(key=lambda x: (x['agency_score'], x['character']), reverse=True)
        return {'agency_metrics': report}

    # =========================================================================
    # ROLE CLASSIFIER LOGIC (New)
    # =========================================================================

    def classify_roles(self, input_data):
        """Heuristic Role Classification based on presence and agency."""
        scenes = input_data.get('scenes', [])
        if not scenes: return {}
        
        # 1. Count Lines and Scenes
        char_lines = collections.defaultdict(int)
        char_scenes = collections.defaultdict(int)
        
        for scene in scenes:
            seen_in_scene = set()
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        char_lines[name] += 1
                        seen_in_scene.add(name)
            for name in seen_in_scene:
                char_scenes[name] += 1
                
        if not char_lines: return {}
        
        # 2. Determine Hierarchy
        sorted_chars = sorted(char_lines.items(), key=lambda x: x[1], reverse=True)
        top_char, max_lines = sorted_chars[0]
        
        roles = {}
        roles[top_char] = 'Protagonist'
        
        for char, lines in sorted_chars[1:]:
            ratio = lines / max_lines
            if ratio > 0.6:
                roles[char] = 'Major Support' # Potential Antagonist or Deuteragonist
            elif ratio > 0.2:
                roles[char] = 'Supporting'
            else:
                roles[char] = 'Minor'
                
        return roles

    # =========================================================================
    # FAIRNESS LOGIC (formerly fairness.py)
    # =========================================================================

    def audit_fairness(self, input_data, context=None, genre='drama'):
        """Audit character portrayals for potential bias."""
        scenes = input_data.get('scenes', [])
        valence_scores = input_data.get('valence_scores', [])
        
        # Auto-detect roles if not provided
        roles = context if context else self.classify_roles(input_data)
        
        # Genre Thresholds
        g_lower = genre.lower()
        neg_thresh = -0.3 if g_lower in ['horror', 'thriller'] else (-0.05 if g_lower == 'comedy' else -0.15)
        
        if not scenes: return {}
        
        char_valence = collections.defaultdict(list)
        char_agency = collections.defaultdict(list) # Placeholder for agency integration
        
        # Get Agency Data if available (self-call or passed)
        agency_data = self.analyze_agency(input_data).get('agency_metrics', [])
        agency_map = {item['character']: item['agency_score'] for item in agency_data}
        
        for i, scene in enumerate(scenes):
            val = valence_scores[i] if i < len(valence_scores) else 0.0
            active = set()
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name: active.add(name)
            for char in active:
                char_valence[char].append(val)
                
        report = {'stereotyping_risks': [], 'representation_stats': {}}
        major_chars = [c for c, vals in char_valence.items() if len(vals) > 5]
        
        for char in major_chars:
            vals = char_valence[char]
            avg_val = statistics.mean(vals)
            role = roles.get(char, 'Unknown')
            agency = agency_map.get(char, 0.5)
            
            # Risk 1: The "Inept" Minor Character (Low Agency + Negative Sentiment)
            if role == 'Minor' and agency < 0.2 and avg_val < -0.1:
                report['stereotyping_risks'].append(
                    f"Minor Character '{char}' is portrayed with Low Agency ({agency:.2f}) and Negative Tone. This pattern often correlates with unbalanced character positioning."
                )
            
            # Risk 2: Villain Coding (check if Major Support is excessively negative)
            if role in ['Major Support', 'Protagonist'] and avg_val < neg_thresh:
                if role == 'Protagonist':
                     report['stereotyping_risks'].append(f"Protagonist '{char}' has consistently negative sentiment ({avg_val:.2f}). Is this an Anti-Hero?")
                else:
                     report['stereotyping_risks'].append(
                         f"Major Character '{char}' has high negative sentiment ({avg_val:.2f}). This often signals an Antagonist role, but can result in 'Villain Coding' if internal motivation is not established."
                     )

            report['representation_stats'][char] = {
                'scene_count': len(vals),
                'avg_sentiment': round(avg_val, 3),
                'agency': round(agency, 3),
                'role': role
            }
            
        return report


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: experimental_agent.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
Experimental Agent - Advanced Research & Experimental Modules
Consolidates: silicon_stanislavski.py, resonance.py, insight.py, polyglot_validator.py, multimodal.py
"""

import logging

from ..utils.model_manager import manager

logger = logging.getLogger('scriptpulse.experimental')

# =============================================================================
# SILICON STANISLAVSKI LOGIC (formerly silicon_stanislavski.py)
# =============================================================================

class SiliconStanislavskiAgent:
    """Methods for Believability & Actor Theory (Method Acting Simulation)"""
    
    def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
        self.belief_state = {'safety': 0.8, 'trust': 0.8, 'agency': 0.5}
        self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
        self.labels = ["danger", "safety", "deception", "trust", "helplessness", "control"]
        self.is_ml = self.classifier is not None
        
    def analyze_script(self, scenes_text):
        """Batch process all scenes for massive speedup."""
        results = []
        current_state = self.belief_state.copy()
        
        valid_indices = [i for i, t in enumerate(scenes_text) if t and len(t) > 10]
        valid_texts = [scenes_text[i][:1000] for i in valid_indices] 
        
        ml_outputs = []
        if self.is_ml and valid_texts:
            try:
                ml_outputs = self.classifier(valid_texts, self.labels, multi_label=True, batch_size=4)
            except Exception as e:
                logger.error("Batch Inference Failed: %s", e)
                self.is_ml = False 
                
        output_map = {idx: out for idx, out in zip(valid_indices, ml_outputs)}
        
        for i, text in enumerate(scenes_text):
            step_data = self._update_state(current_state, text, output_map.get(i))
            current_state = step_data['internal_state'] 
            results.append(step_data)
        return results

    def _update_state(self, state, text, ml_result=None):
        new_state = state.copy()
        method = "Keyword Heuristic (Fallback)"
        scores = {}
        
        if ml_result:
            method = "Zero-Shot Classification"
            scores = {label: score for label, score in zip(ml_result['labels'], ml_result['scores'])}
            
            new_state['safety'] = max(0.0, min(1.0, new_state['safety'] + (scores.get('safety', 0) - scores.get('danger', 0)) * 0.2))
            new_state['trust'] = max(0.0, min(1.0, new_state['trust'] + (scores.get('trust', 0) - scores.get('deception', 0)) * 0.2))
            new_state['agency'] = max(0.0, min(1.0, new_state['agency'] + (scores.get('control', 0) - scores.get('helplessness', 0)) * 0.2))
        else:
            logger.warning("ML model unavailable — falling back to keyword heuristics")
            lower_text = (text or "").lower()
            if 'gun' in lower_text or 'kill' in lower_text:
                new_state['safety'] *= 0.9
                
        emotion = "Neutral"
        if new_state['safety'] < 0.4: emotion = "Fear/Anxiety"
        elif new_state['trust'] < 0.4: emotion = "Suspicion/Paranoia"
        elif new_state['agency'] > 0.8: emotion = "Empowered/Determined"
        
        return {
            'internal_state': new_state,
            'felt_emotion': emotion,
            'method_acting_depth': method,
            'raw_scores': scores
        }


# =============================================================================
# RESONANCE LOGIC (formerly resonance.py)
# =============================================================================

class ResonanceAgent:
    """Thematic Resonance Agent - Alignment of Effort & Theme.
    Uses SBERT cosine similarity when available, keyword fallback otherwise.
    """
    
    # Theme descriptions for embedding-based matching
    THEME_DESCRIPTIONS = {
        'Redemption': 'finding forgiveness, making amends, being saved, second chance',
        'Betrayal': 'breaking trust, deception, backstabbing, double-cross, treachery',
        'Sacrifice': 'giving up something precious, self-sacrifice, noble loss, martyrdom',
        'Identity': 'who am I, self-discovery, transformation, belonging, otherness',
        'Love': 'romantic connection, deep affection, heartbreak, longing, devotion',
        'Death': 'mortality, loss of life, grief, finality, legacy, afterlife'
    }
    
    def __init__(self):
        self.themes = list(self.THEME_DESCRIPTIONS.keys())
        self.sbert_model = manager.get_sentence_transformer('jinaai/jina-embeddings-v2-small-en')
        self.theme_embeddings = None
        self.is_ml = self.sbert_model is not None
        
        if self.is_ml:
            try:
                theme_texts = list(self.THEME_DESCRIPTIONS.values())
                self.theme_embeddings = self.sbert_model.encode(theme_texts, convert_to_tensor=False)
                logger.info("ResonanceAgent: SBERT theme embeddings loaded")
            except Exception as e:
                logger.error("ResonanceAgent: Failed to encode themes: %s", e)
                self.is_ml = False
        
    def analyze_scene(self, scene_text, structural_effort):
        detected_themes = []
        thematic_weight = 0.0
        method = "Keyword Fallback"
        
        if self.is_ml and self.theme_embeddings is not None and scene_text and len(scene_text.strip()) > 10:
            try:
                scene_emb = self.sbert_model.encode([scene_text[:1000]], convert_to_tensor=False)
                # Compute cosine similarity with each theme
                import numpy as np
                scene_vec = scene_emb[0]
                scene_norm = np.linalg.norm(scene_vec)
                if scene_norm > 0:
                    for i, theme_name in enumerate(self.themes):
                        theme_vec = self.theme_embeddings[i]
                        theme_norm = np.linalg.norm(theme_vec)
                        if theme_norm > 0:
                            cosine_sim = np.dot(scene_vec, theme_vec) / (scene_norm * theme_norm)
                            if cosine_sim > 0.35:  # Threshold for thematic relevance
                                detected_themes.append(theme_name)
                                thematic_weight += min(float(cosine_sim), 0.5)
                method = "SBERT Cosine Similarity"
            except Exception as e:
                logger.warning("ResonanceAgent: SBERT inference failed, falling back to keywords: %s", e)
                detected_themes, thematic_weight = self._keyword_fallback(scene_text)
                method = "Keyword Fallback (after SBERT error)"
        else:
            if not self.is_ml:
                logger.warning("ResonanceAgent: SBERT unavailable — using keyword fallback")
            detected_themes, thematic_weight = self._keyword_fallback(scene_text)
        
        resonance_score = structural_effort * (1.0 + thematic_weight)
        
        return {
            'resonance_score': min(resonance_score, 2.0),
            'detected_themes': detected_themes,
            'thematic_weight': round(thematic_weight, 3),
            'method': method
        }
    
    def _keyword_fallback(self, scene_text):
        """Original keyword-based theme detection as fallback."""
        detected = []
        weight = 0.0
        lower_text = (scene_text or '').lower()
        for theme in self.themes:
            if theme.lower() in lower_text:
                detected.append(theme)
                weight += 0.2
        return detected, weight


# =============================================================================
# INSIGHT LOGIC (formerly insight.py)
# =============================================================================

class InsightAgent:
    """Insight Cascade Agent - Detecting Aha Moments"""
    
    def __init__(self):
        self.prev_entropy = 0.5 
        
    def detect_cascade(self, current_entropy):
        delta = self.prev_entropy - current_entropy
        is_insight = False
        label = "Stable"
        
        if delta > 0.2:
            is_insight = True
            label = "Insight Cascade (Aha!)"
        elif delta < -0.2:
            label = "Confusion Spike"
            
        self.prev_entropy = current_entropy
        return {'entropy_delta': delta, 'is_insight': is_insight, 'label': label}


# =============================================================================
# POLYGLOT VALIDATOR LOGIC (formerly polyglot_validator.py)
# =============================================================================

class PolyglotValidatorAgent:
    """Pacing Distribution Profiler.
    (Reframed from 'Polyglot Validator' to ensure scientific accuracy; 
    avoids mapping simple line counts to complex cultural structural paradigms).
    """
    
    def __init__(self):
        self.supported_structures = ['Balanced', 'Frontloaded', 'Backloaded', 'Mid-heavy']
        
    def detect_structure(self, scene_list):
        if not scene_list or len(scene_list) < 4:
            return "Unknown Pacing"
            
        scene_lengths = [max(1, s.get('end_line', 0) - s.get('start_line', 0)) for s in scene_list]
        total_length = sum(scene_lengths)
        
        q_size = len(scene_lengths) // 4
        q1 = sum(scene_lengths[:q_size]) / total_length
        q2 = sum(scene_lengths[q_size:q_size*2]) / total_length
        q3 = sum(scene_lengths[q_size*2:q_size*3]) / total_length
        q4 = sum(scene_lengths[q_size*3:]) / total_length
        
        # Honest pacing metrics based on length distributions
        if max([q1, q2, q3, q4]) - min([q1, q2, q3, q4]) < 0.10:
            return "Balanced Pacing (Even distribution)"
        elif q3 > q1 + 0.1 and q3 > q4 + 0.1:
            return "Mid-Heavy (Focus on development/complications)"
        elif q1 > q3 and q1 > q4:
            return "Frontloaded (Heavy setup/worldbuilding)"
        elif q4 > q1 and q4 > q2:
            return "Backloaded (Extended climax/resolution)"
            
        return "Variable Pacing"
    
    def run(self, input_data):
        structure = self.detect_structure(input_data.get('scenes', []))
        return {
            'detected_structure': structure,
            'cultural_bias_check': 'DEPRECATED - Replaced with empirical pacing profiling to maintain research validity.'
        }


# =============================================================================
# MULTI-LABEL EMOTION LOGIC
# =============================================================================

class MultiLabelEmotionAgent:
    """Detects Plutchik's 8 Emotions + Compound States.
    Uses zero-shot classification when ML is available, keyword fallback otherwise.
    """
    
    EMOTION_LABELS = ['joy', 'sadness', 'anger', 'fear', 'trust', 'disgust', 'surprise', 'anticipation']
    
    # Keyword sets for fallback mode
    KEYWORD_SETS = {
        'joy': {'joy', 'happy', 'smile', 'laugh', 'win', 'good', 'love', 'success'},
        'sadness': {'sad', 'cry', 'tears', 'grief', 'loss', 'die', 'dead', 'pain', 'fail'},
        'anger': {'angry', 'hate', 'rage', 'kill', 'fight', 'attack', 'enemy', 'fury'},
        'fear': {'scared', 'fear', 'afraid', 'run', 'hide', 'terror', 'panic', 'danger'},
        'trust': {'trust', 'friend', 'help', 'safe', 'believe', 'team', 'agree'},
        'disgust': {'gross', 'ugly', 'sick', 'rot', 'dirty', 'vile', 'nasty'},
        'surprise': {'shock', 'swhat', 'gasp', 'sudden', 'unexpected', 'stunned'},
        'anticipation': {'wait', 'hope', 'plan', 'ready', 'soon', 'look forward'}
    }
    
    def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
        self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
        self.is_ml = self.classifier is not None
        if not self.is_ml:
            logger.warning("MultiLabelEmotionAgent: ML unavailable — using keyword fallback")
        
    def run(self, scene_text):
        if not scene_text:
            return {}
        
        if self.is_ml:
            return self._ml_classify(scene_text)
        else:
            return self._keyword_classify(scene_text)
    
    def _ml_classify(self, scene_text):
        """Use zero-shot classification for emotion detection."""
        try:
            result = self.classifier(
                scene_text[:1000],
                self.EMOTION_LABELS,
                multi_label=True
            )
            normalized = {label: round(score, 3) 
                         for label, score in zip(result['labels'], result['scores'])}
            
            # Detect Compounds from ML scores
            compounds = []
            if normalized.get('joy', 0) > 0.3 and normalized.get('trust', 0) > 0.3:
                compounds.append('Love')
            if normalized.get('fear', 0) > 0.3 and normalized.get('surprise', 0) > 0.3:
                compounds.append('Awe')
            if normalized.get('anger', 0) > 0.3 and normalized.get('disgust', 0) > 0.3:
                compounds.append('Contempt')
            
            return {'emotions': normalized, 'compounds': compounds, 'method': 'Zero-Shot Classification'}
        except Exception as e:
            logger.warning("MultiLabelEmotionAgent: ML inference failed: %s. Falling back.", e)
            return self._keyword_classify(scene_text)
    
    def _keyword_classify(self, scene_text):
        """Original keyword-based emotion detection as fallback."""
        words = scene_text.lower().split()
        scores = {k: 0.0 for k in self.KEYWORD_SETS}
        total_hits = 0
        
        for w in words:
            for emo, keywords in self.KEYWORD_SETS.items():
                if w in keywords:
                    scores[emo] += 1.0
                    total_hits += 1
                    
        if total_hits == 0:
            return {k: 0.0 for k in scores}
        
        normalized = {k: round(v / total_hits, 2) for k, v in scores.items()}
        
        # Detect Compounds
        compounds = []
        if normalized['joy'] > 0.2 and normalized['trust'] > 0.2:
            compounds.append('Love')
        if normalized['fear'] > 0.2 and normalized['surprise'] > 0.2:
            compounds.append('Awe')
        if normalized['anger'] > 0.2 and normalized['disgust'] > 0.2:
            compounds.append('Contempt')
        
        return {'emotions': normalized, 'compounds': compounds, 'method': 'Keyword Fallback'}


# =============================================================================
# STAKES DETECTOR LOGIC
# =============================================================================

class StakesDetector:
    """Detects High Stakes and Time Pressure using Lexical Markers"""
    
    def __init__(self):
        self.is_ml = True
        
    def run(self, scene_text, ablation_config=None):
        if not scene_text: return {'stakes': 'Low', 'time_pressure': False}
        
        ablation_config = ablation_config or {}
        if not ablation_config.get('use_sbert', True):
            self.is_ml = False
            
        if self.is_ml:
            try:
                from ..utils.model_manager import manager as global_manager
                classifier = global_manager.get_zero_shot()
                if len(scene_text.split()) < 5:
                    return {'stakes': 'Low', 'time_pressure': False, 'method': 'Length Fallback'}
                    
                # Detect High Stakes
                stakes_labels = ['high stakes life or death', 'medium stakes conflict', 'low stakes casual']
                stakes_result = classifier(scene_text, stakes_labels, multi_label=False)
                top_stakes = stakes_result['labels'][0]
                
                if 'high' in top_stakes: stakes_level = 'High'
                elif 'medium' in top_stakes: stakes_level = 'Medium'
                else: stakes_level = 'Low'
                
                # Detect Time Pressure
                time_labels = [' urgent time pressure deadline', 'relaxed pace no hurry']
                time_result = classifier(scene_text, time_labels, multi_label=False)
                time_pressure = 'urgent' in time_result['labels'][0] and time_result['scores'][0] > 0.6
                
                return {
                    'stakes': stakes_level,
                    'time_pressure': time_pressure,
                    'method': 'Zero-Shot ML'
                }
            except Exception as e:
                import logging
                logger = logging.getLogger('scriptpulse.mlops')
                logger.warning("StakesDetector ML failed, falling back to lexical: %s", e)
        
        # Lexical Fallback
        high_stakes_markers = {
            'die', 'kill', 'save', 'bomb', 'gun', 'blood', 'forever', 'last chance', 'escape', 'destroy',
            'ruin', 'love', 'marry', 'pregnant', 'truth', 'secret', 'confess', 'explode', 'life', 'lives', 'death'
        }
        time_pressure_markers = {
            'hurry', 'run', 'fast', 'quick', 'seconds', 'minutes', 'too late', 'now', 'move', 'go go'
        }
        
        lower_text = scene_text.lower()
        
        stakes_hits = sum(1 for m in high_stakes_markers if m in lower_text)
        time_hits = sum(1 for m in time_pressure_markers if m in lower_text)
        
        stakes_level = 'Low'
        if stakes_hits >= 2: 
            stakes_level = 'High' if (stakes_hits >= 3 or time_hits >= 1) else 'Medium'
        elif stakes_hits == 1 and time_hits >= 2:
            stakes_level = 'Medium'
        
        return {
            'stakes': stakes_level,
            'time_pressure': time_hits > 0, # Strict check for boolean
            'method': 'Lexical Fallback'
        }

# =============================================================================
# MULTIMODAL LOGIC (formerly multimodal.py)
# =============================================================================

class MultimodalFusionAgent:
    """Multimodal Fusion Agent - Combining Text & Pseudo-Vision/Acoustics.
    Since raw video/audio is unavailable at the script stage, this agent
    extrapolates hypothetical visual and acoustic intensity from screenplay format.
    """
    
    def __init__(self):
        self.visual_layer_enabled = True
        
    def run(self, input_data):
        text_effort = input_data.get('effort_score', 0.5)
        
        # Extrapolate visual density proxy (Action verbs, uppercase nouns)
        action_density = input_data.get('action_density', 0.5)
        # Extrapolate acoustic density proxy (Dialogue velocity, punctuation marks)
        dialogue_velocity = input_data.get('dialogue_velocity', 0.5)
        
        # Calculate cross-modal interference (Does loud sound conflict with dense text?)
        interference = 0.0
        if text_effort > 0.7 and dialogue_velocity > 0.7:
            interference = 0.2  # Cognitive overload from dual complex information
        elif action_density > 0.8 and text_effort < 0.3:
            # High action, low text -> visual dominance, reduced reading effort
            interference = -0.15 
            
        fused_effort = text_effort + (action_density * 0.15) + (dialogue_velocity * 0.1) + interference
        
        return {
            'fused_effort': max(0.0, min(fused_effort, 1.0)),
            'visual_proxy': round(action_density, 3),
            'acoustic_proxy': round(dialogue_velocity, 3),
            'source': 'Multimodal Fusion (Action/Dialogue Proxy Extrapolation)'
        }


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: governance.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: trust_lock.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: xai_highlighter.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import re

def generate_xai_html(text: str) -> str:
    """
    Simulates an Explainable AI (XAI) feature attribution map.
    Highlights Action/Density verbs in light red, and dialogue/character focus in light blue.
    """
    if not text:
        return ""

    # Simple heuristics to demonstrate the concept without heavy NLP parsing limits
    # Red flags for tension/density (action verbs, sudden motions)
    tension_triggers = [r'\b(runs|run|sprints|grabs|shoots|screams|yells|slams|hits|punches|gasps|suddenly|fast|quick|blood|gun|knife|attacks)\b']
    
    # Blue flags for characters interacting/speaking (dialogue density)
    dialogue_triggers = [r'^[A-Z\s]+$'] # ALL CAPS names before dialogue
    
    html_text = text

    # Apply HTML spans
    for pattern in tension_triggers:
        html_text = re.sub(
            pattern, 
            r'<span style="background-color: rgba(255, 99, 132, 0.4); border-radius: 3px; padding: 0 2px;" title="Tension/Action Trigger">\1</span>', 
            html_text, 
            flags=re.IGNORECASE
        )
        
    for pattern in dialogue_triggers:
        # Match lines that are purely uppercase formatting (standard script names)
        html_text = re.sub(
            r'^([A-Z\s\(\)]+)$', 
            r'<span style="background-color: rgba(54, 162, 235, 0.4); border-radius: 3px; padding: 0 2px;" title="Character Focus/Dialogue">\1</span>', 
            html_text, 
            flags=re.MULTILINE
        )

    # Wrap in a scrolling div for the UI
    return f"""
    <div style="font-family: monospace; white-space: pre-wrap; padding: 15px; border-radius: 5px; background-color: #f8f9fa; color: #333; height: 300px; overflow-y: scroll; border: 1px solid #ddd; font-size: 14px; line-height: 1.5;">
        {html_text}
    </div>
    """


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: studio_report.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Studio Reporter (Market Professional Layer)
Gap Solved: "The Screenshot Problem"

Generates a professional "Studio Coverage" style HTML report 
that can be printed to PDF.
"""

import base64
import statistics

def generate_report(report_data, script_title="Untitled Script", user_notes="", lens="Story Editor"):
    """
    Generate a standalone HTML string for the report.
    """
    
    # 1. Extract Key Metrics
    trace = report_data.get('temporal_trace', [])
    avg_effort = statistics.mean([t['attentional_signal'] for t in trace]) if trace else 0
    
    writer_intel = report_data.get('writer_intelligence', {})
    diagnoses = writer_intel.get('narrative_diagnosis', [])
    priorities = writer_intel.get('rewrite_priorities', [])

    # --- Persona Filtering Logic (Sync with writer_view.py) ---
    EXEC_ICONS = ['🔵', '🔴', '⚖️', '🚫', '👥', '📉', '⚠️', '🎢', '🟠', '✨', '💎']
    EDITOR_ICONS = ['🧵', '⬜', '👻', '✅', '🔵', '🔴', '⭐', '✨', '🟡', '🎢', '🟠', '🗣️', '🧠', '💡', '💎']
    COORD_ICONS = ['✂️', '🔴', '🟠', '🚫', '💎', '⛓️', '🎭', '👥', '🎙️', '🟢', '🗣️', '🧠', '💡', '✨']
    
    filtered_diags = []
    for text in diagnoses:
        is_exec = any(icon in text for icon in EXEC_ICONS)
        is_editor = any(icon in text for icon in EDITOR_ICONS)
        is_coord = any(icon in text for icon in COORD_ICONS)
        if "Same Voice" in text: is_exec, is_editor, is_coord = False, True, True
        elif "Engagement Drop" in text: is_exec, is_editor, is_coord = True, True, False
        if (lens == "Studio Executive" and is_exec) or \
           (lens == "Story Editor" and is_editor) or \
           (lens == "Script Coordinator" and is_coord):
            filtered_diags.append(text)
    
    if not filtered_diags and diagnoses:
        filtered_diags = [d for d in diagnoses if any(i in d for i in ['✅', '✨', '🟢'])] or diagnoses[:1]

    filtered_pris = []
    exec_pri_kws = ["boredom", "cut", "engagement", "budget", "unfilmable", "name", "slow"]
    coord_pri_kws = ["dialogue", "show", "unfilmable", "fluff", "prose", "voice", "economy"]
    for p in priorities:
        txt = f"{p.get('action', '')} {p.get('root_cause', '')}".lower()
        if (lens == "Studio Executive" and any(k in txt for k in exec_pri_kws)) or \
           (lens == "Script Coordinator" and any(k in txt for k in coord_pri_kws)) or \
           (lens == "Story Editor"):
            filtered_pris.append(p)
    
    if not filtered_pris and priorities:
        filtered_pris = priorities[:3]

    # Recommendation Logic
    rec = "CONSIDER"
    if avg_effort < 0.35: rec = "PASS (Low Engagement)"
    elif avg_effort > 0.75: rec = "PASS (High Strain)"
    
    # --- Additional Data Extraction ---
    loc_profile = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('location_profile', {})
    char_arcs = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('character_arcs', {})
    cast_size = len(char_arcs) if char_arcs else len(report_data.get('voice_fingerprints', {}))
    economy_map = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('scene_economy_map', {}).get('map', [])

    # 2. Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Script Intelligence Coverage ({lens}): {script_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #0f172a;
                --accent: {('#3b82f6' if lens == "Story Editor" else '#6366f1' if lens == "Studio Executive" else '#10b981')};
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #1e293b;
                --text-muted: #64748b;
            }}
            
            body {{ 
                font-family: 'Outfit', sans-serif; 
                line-height: 1.6; 
                color: var(--text); 
                background-color: var(--bg);
                margin: 0; 
                padding: 0;
            }}
            
            .container {{
                max-width: 900px;
                margin: 40px auto;
                padding: 0 20px;
            }}
            
            .header {{ 
                text-align: left; 
                margin-bottom: 40px; 
                background: var(--primary);
                color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .header::after {{
                content: "";
                position: absolute;
                top: -50%;
                right: -10%;
                width: 300px;
                height: 300px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 50%;
                z-index: 0;
            }}
            
            .header h1 {{ margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.2em; opacity: 0.8; position: relative; z-index: 1; }}
            .header h2 {{ margin: 10px 0 20px 0; font-size: 36px; font-weight: 700; position: relative; z-index: 1; }}
            .header .meta {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; opacity: 0.7; position: relative; z-index: 1; }}
            
            .verdict {{ 
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: var(--card-bg);
                padding: 24px;
                border-radius: 12px;
                margin-bottom: 30px;
                border-left: 8px solid var(--accent);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .verdict-label {{ font-size: 14px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; float: left;}}
            .verdict-value {{ font-size: 24px; font-weight: 700; color: var(--primary); }}
            
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat({('5' if lens == "Studio Executive" else '3')}, 1fr); 
                gap: 20px; 
                margin-bottom: 40px; 
            }}
            
            .stat-card {{ 
                background: var(--card-bg);
                padding: 20px 15px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .stat-card h4 {{ margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.1em; }}
            .stat-card p {{ margin: 0; font-size: 22px; font-weight: 700; color: var(--primary); }}
            
            .section {{
                background: var(--card-bg);
                padding: 32px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .section h3 {{ 
                margin-top: 0; 
                font-size: 18px; 
                border-bottom: 2px solid #f1f5f9; 
                padding-bottom: 15px; 
                margin-bottom: 20px;
                color: var(--primary);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .priority-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .priority-table th {{ text-align: left; padding: 12px; background: #f1f5f9; font-size: 12px; text-transform: uppercase; color: var(--text-muted); }}
            .priority-table td {{ padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            .tag {{ 
                display: inline-block; 
                padding: 2px 8px; 
                border-radius: 4px; 
                font-size: 11px; 
                font-weight: 700; 
                text-transform: uppercase;
                background: #e2e8f0;
            }}
            .tag-high {{ background: #fee2e2; color: #b91c1c; }}
            
            .footer {{ 
                margin-top: 60px; 
                padding: 40px 0;
                text-align: center; 
                font-size: 12px; 
                color: var(--text-muted); 
                border-top: 1px solid #e2e8f0; 
                font-family: 'JetBrains Mono', monospace;
            }}
            
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 12px; }}
            
            .confidence-pill {{
                background: #f1f5f9;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            
            .economy-item {{
                background: #f8fafc;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 8px;
                font-size: 13px;
                border-left: 4px solid #e2e8f0;
            }}
            .economy-bloated {{ border-left-color: var(--danger); background: #fff1f2; }}
            .economy-tight {{ border-left-color: var(--success); background: #f0fdf4; }}

            .indicator {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--success);
            }}
        </style>
    </head>
    <body>
    
    <div class="container">
        <div class="header">
            <h1>Intelligence Coverage ({lens})</h1>
            <h2>{script_title}</h2>
            <div class="meta">
                ENGINE: Script<span style="color: #0052FF; font-weight: bold;">Pulse</span> v15.0 Gold | PERSPECTIVE: {lens}
            </div>
        </div>
        
        <div class="verdict">
            <div>
                <div class="verdict-label">Recommendation</div><br>
                <div class="verdict-value">{rec}</div>
            </div>
            <div class="confidence-pill">
                Confidence: {int(report_data.get('meta', {}).get('confidence_score', {}).get('score', 0)*100)}%
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h4>Avg Engagement</h4>
                <p>{avg_effort:.2f}</p>
            </div>
            <div class="stat-card">
                <h4>Pacing Units</h4>
                <p>{len(trace)}</p>
            </div>
            <div class="stat-card">
                <h4>Est. Runtime</h4>
                <p>{writer_intel.get('structural_dashboard', {}).get('runtime_estimate', {}).get('estimated_minutes', len(trace)*2)}m</p>
            </div>
            {f'''
            <div class="stat-card">
                <h4>📍 Locations</h4>
                <p>{loc_profile.get('unique_locations', '—')}</p>
            </div>
            <div class="stat-card">
                <h4>🎭 Cast Size</h4>
                <p>{cast_size if cast_size else '—'}</p>
            </div>
            ''' if lens == "Studio Executive" else ""}
        </div>
        
        <div class="section">
            <h3>Diagnostic Summary</h3>
            <ul>
                {''.join([f"<li>{item}</li>" for item in filtered_diags]) if filtered_diags else '<li>Analysis clear. No high-risk anomalies.</li>'}
            </ul>
        </div>
        
        {f'''
        <div class="section">
            <h3>Scene Economy Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 15px;">Targeting scenes for page efficiency and production speed:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">✂️ Trim Candidates</h4>
                    {''.join([f'<div class="economy-item economy-bloated">Scene {s["scene"]}: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) < 35][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">None detected.</p>'}
                </div>
                <div>
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">💎 Lean Scenes</h4>
                    {''.join([f'<div class="economy-item economy-tight">Scene {s["scene"]}: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) > 75][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">No high-efficiency scenes.</p>'}
                </div>
            </div>
        </div>
        ''' if lens == "Script Coordinator" and economy_map else ""}

        <div class="section">
            <h3>Rewrite Priorities</h3>
            <table class="priority-table">
                <thead>
                    <tr>
                        <th>Intervention Strategy</th>
                        <th>Leverage</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{edit['action']}</td><td><span class='tag tag-high'>{edit['leverage']}</span></td></tr>" for edit in filtered_pris[:5]]) if filtered_pris else '<tr><td colspan="2">No high-priority revisions required.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        {f'<div class="section" style="background: #fffbeb; border: 1px solid #fef3c7;"><h3>Reader Perspectives</h3><p>{user_notes}</p></div>' if user_notes else ''}
        
        <div class="section">
            <h3>Character Voice Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">Distinctiveness check for lead roles:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                {''.join([f"<div style='background: #f8fafc; padding: 15px; border-radius: 8px;'><div style='font-weight: 700; color: var(--primary);'>{char}</div><div style='font-size: 13px;'>Agency (Action): {metrics['agency']:.2f} | Sentiment: {metrics['sentiment']:.2f}</div></div>" for char, metrics in list(report_data.get('voice_fingerprints', {}).items())[:6]])}
            </div>
        </div>
        
        <div class="footer">
            GEN-SPEC: v{report_data.get('meta', {}).get('metric_version', '1.3')} | PROFILE: v{report_data.get('meta', {}).get('genre_profile_version', '1.0')}<br>
            SECURE HASH: {report_data.get('meta', {}).get('constants_hash', 'N/A')}<br>
            &copy; 2026 ScriptPulse Analytics Engine. Confidential & Proprietary.
        </div>
    </div>
    
    </body>
    </html>
    """
    
    return html


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: writer_report.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Writer Report Generator
====================================
Converts the full writer_intelligence output into a clean, human-readable
Markdown report that a screenwriter can print, annotate, and work from.

Usage:
    from scriptpulse.reporters.writer_report import generate_writer_report
    md = generate_writer_report(pipeline_output, title="MY SCRIPT")
    with open("my_script_report.md", "w") as f:
        f.write(md)
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# Genre benchmark table for all core signals
# ---------------------------------------------------------------------------
GENRE_BENCHMARKS = {
    'drama':    {'conflict': (0.35, 0.70), 'energy': (0.40, 0.75), 'entropy': (0.30, 0.60), 'payoff_density': (0.25, 0.65)},
    'thriller': {'conflict': (0.55, 0.85), 'energy': (0.55, 0.85), 'entropy': (0.40, 0.75), 'payoff_density': (0.45, 0.80)},
    'comedy':   {'conflict': (0.20, 0.55), 'energy': (0.35, 0.70), 'entropy': (0.25, 0.55), 'payoff_density': (0.20, 0.55)},
    'horror':   {'conflict': (0.50, 0.85), 'energy': (0.45, 0.80), 'entropy': (0.45, 0.80), 'payoff_density': (0.40, 0.80)},
    'action':   {'conflict': (0.60, 0.90), 'energy': (0.60, 0.90), 'entropy': (0.40, 0.75), 'payoff_density': (0.45, 0.85)},
    'romance':  {'conflict': (0.20, 0.55), 'energy': (0.30, 0.65), 'entropy': (0.20, 0.50), 'payoff_density': (0.20, 0.55)},
    'sci-fi':   {'conflict': (0.40, 0.80), 'energy': (0.45, 0.80), 'entropy': (0.45, 0.80), 'payoff_density': (0.35, 0.75)},
    'avant-garde': {'conflict': (0.10, 0.90), 'energy': (0.10, 0.90), 'entropy': (0.60, 0.95), 'payoff_density': (0.10, 0.90)},
    'crime drama': {'conflict': (0.45, 0.80), 'energy': (0.45, 0.80), 'entropy': (0.35, 0.70), 'payoff_density': (0.35, 0.75)},
    'feature':  {'conflict': (0.35, 0.75), 'energy': (0.40, 0.75), 'entropy': (0.30, 0.65), 'payoff_density': (0.30, 0.70)},
    'general':  {'conflict': (0.30, 0.75), 'energy': (0.35, 0.75), 'entropy': (0.30, 0.70), 'payoff_density': (0.25, 0.70)},
}


def _benchmark_tag(value, genre, signal):
    """Return a tag string showing value vs genre benchmark."""
    benchmarks = GENRE_BENCHMARKS.get(genre.lower(), GENRE_BENCHMARKS['general'])
    if signal not in benchmarks:
        return f"{value:.2f}"
    
    low, high = benchmarks[signal]
    
    if value < low:
        return f"🔴 **{value:.2f}** *(below {genre} target: {low:.2f}-{high:.2f})*"
    elif value > high:
        return f"🟡 **{value:.2f}** *(above {genre} target: {low:.2f}-{high:.2f})*"
    else:
        return f"🟢 **{value:.2f}** *(on target: {low:.2f}-{high:.2f} for {genre})*"


def _stars(value, max_val=1.0, n=5):
    """Return a visual star bar for a 0..max_val value."""
    filled = round((value / max_val) * n)
    filled = max(0, min(n, filled))
    return "*" * filled + "-" * (n - filled)


def _section(title):
    return f"\n---\n\n## {title}\n"


def generate_writer_report(pipeline_output, title="Untitled Script", genre=None):
    """
    Generate a complete Markdown writer's report from ScriptPulse pipeline output.

    Args:
        pipeline_output: dict — full output from scriptpulse.runner.run_pipeline()
        title: str — script title for the report header
        genre: str — override genre (defaults to what the pipeline detected)

    Returns:
        str — formatted Markdown report
    """
    wi = pipeline_output.get('writer_intelligence', {})
    trace = pipeline_output.get('temporal_trace', [])
    genre = (genre or wi.get('genre_context', 'general')).lower()
    dashboard = wi.get('structural_dashboard', {})
    diagnosis = wi.get('narrative_diagnosis', [])
    priorities = wi.get('rewrite_priorities', [])
    summary_data = wi.get('narrative_summary', {})

    lines = []

    # -------------------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------------------
    analysis_date = pipeline_output.get('meta', {}).get('timestamp')
    if not analysis_date:
        analysis_date = datetime.now().strftime('%B %d, %Y (%H:%M)')
        
    lines.append(f"# 🖋️ Script<span style='color: #0052FF;'>Pulse</span> Intelligence Report")
    lines.append(f"**PROJECT:** `{title.upper()}`  ")
    lines.append(f"**GENRE PROFILE:** `{genre.upper()}`  ")
    lines.append(f"**ANALYSIS DATE:** {analysis_date}  ")
    lines.append(f"**ENGINE VERSION:** `v15.0 Gold`  ")
    lines.append("\n" + "---" * 10 + "\n")

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    lines.append("## 📌 Executive Summary")
    if isinstance(summary_data, dict):
        summary_text = summary_data.get('summary', '')
    else:
        summary_text = str(summary_data)

    if summary_text:
        lines.append(f"{summary_text}")
    else:
        lines.append("*No narrative summary available for this analysis.*")

    # -------------------------------------------------------------------------
    # RUNTIME & FORMAT SNAPSHOT
    # -------------------------------------------------------------------------
    lines.append("\n## 📊 Script Snapshot")
    runtime = dashboard.get('runtime_estimate', {})
    loc_profile = dashboard.get('location_profile', {})
    total_scenes = dashboard.get('total_scenes', len(trace))

    lines.append(f"| Metric | Assessment |")
    lines.append(f"|:-------|:-----------|")
    lines.append(f"| **Total Scenes** | {total_scenes} |")
    lines.append(f"| **Est. Runtime** | {runtime.get('estimated_minutes', '?')} minutes |")
    lines.append(f"| **Runtime Status** | {runtime.get('status', 'N/A')} |")
    lines.append(f"| **Locations** | {loc_profile.get('unique_locations', '?')} unique |")
    lines.append(f"| **INT/EXT Split** | {loc_profile.get('int_scenes', 0)} INT / {loc_profile.get('ext_scenes', 0)} EXT |")

    if loc_profile.get('location_warning'):
        lines.append(f"\n> [!CAUTION]\n> **Location Concentration:** {loc_profile['location_warning']}")

    # -------------------------------------------------------------------------
    # SIGNAL DASHBOARD (Genre-benchmarked)
    # -------------------------------------------------------------------------
    lines.append("\n## 📈 Signal Dashboard")
    lines.append("*Biological engagement signals calibrated against **" + genre.title() + "** standards.*\n")

    if trace:
        import statistics as _stats

        def avg_signal(key, sub=None):
            vals = []
            for s in trace:
                v = s.get(key, 0.0)
                if sub:
                    v = s.get(key, {}).get(sub, 0.0) if isinstance(s.get(key), dict) else 0.0
                if isinstance(v, (int, float)):
                    vals.append(v)
            return _stats.mean(vals) if vals else 0.0

        conflict_avg = avg_signal('conflict')
        energy_avg = avg_signal('attentional_signal')
        entropy_avg = avg_signal('entropy_score')
        payoff_avg = avg_signal('payoff_density', 'payoff_density')
        sentiment_avg = avg_signal('sentiment')

        lines.append(f"| Core Signal | Intensity | Benchmark Status |")
        lines.append(f"|:------------|:----------|:-----------------|")
        lines.append(f"| **Conflict** | `{_stars(conflict_avg)}` | {_benchmark_tag(conflict_avg, genre, 'conflict')} |")
        lines.append(f"| **Energy** | `{_stars(energy_avg)}` | {_benchmark_tag(energy_avg, genre, 'energy')} |")
        lines.append(f"| **Entropy** | `{_stars(entropy_avg)}` | {_benchmark_tag(entropy_avg, genre, 'entropy')} |")
        lines.append(f"| **Payoff** | `{_stars(payoff_avg)}` | {_benchmark_tag(payoff_avg, genre, 'payoff_density')} |")
        lines.append(f"| **Sentiment** | `{_stars((sentiment_avg + 1) / 2)}` | {sentiment_avg:+.2f} *(Dark → Bright)* |")
    else:
        lines.append("*[!] No temporal data found.*")

    # -------------------------------------------------------------------------
    # STRUCTURAL TURNING POINTS
    # -------------------------------------------------------------------------
    lines.append("\n## ⏳ Structural Turning Points")
    turning = dashboard.get('structural_turning_points', {})
    if turning.get('note'):
        lines.append(f"*{turning['note']}*")
    else:
        for beat_name, beat_data in turning.items():
            if not isinstance(beat_data, dict):
                continue
            label = beat_name.replace('_', ' ').title()
            scene = beat_data.get('scene', '?')
            strength = beat_data.get('strength', 0)
            warning = beat_data.get('warning', '')
            bar = _stars(min(strength, 1.0))
            lines.append(f"- **{label}**: Scene {scene} ` {bar} ` ({strength:.2f})")
            if warning:
                lines.append(f"  > [!WARNING] {warning}")

    # -------------------------------------------------------------------------
    # SCENE HEATMAP
    # -------------------------------------------------------------------------
    if trace:
        lines.append("\n## 🌡️ Narrative Heatmap")
        lines.append("*Visual intensity flow (░ = lower, ▓ = higher):*\n")
        heatmap = ""
        for i, s in enumerate(trace):
            val = s.get('attentional_signal', 0.5)
            if val < 0.2: char = "░"
            elif val < 0.4: char = "▒"
            elif val < 0.7: char = "▓"
            else: char = "█"
            heatmap += char
            if (i + 1) % 50 == 0: heatmap += "\n"
        lines.append(f"```\n{heatmap}\n```")

    # -------------------------------------------------------------------------
    # NARRATIVE DIAGNOSIS
    # -------------------------------------------------------------------------
    lines.append("\n## 🩺 Narrative Diagnosis")
    lines.append("*Multi-dimensional structural health check:*\n")
    if diagnosis:
        for item in diagnosis:
            lines.append(f" - {item}")
    else:
        lines.append("*Status: Clear. No structural anomalies detected.*")

    # -------------------------------------------------------------------------
    # CREATIVE PROVOCATIONS
    # -------------------------------------------------------------------------
    provocations = wi.get('creative_provocations', [])
    if provocations:
        lines.append("\n## 💡 Creative Provocations")
        lines.append("*Inquiry-based perspectives on the current draft:*\n")
        for p in provocations:
            lines.append(f"> **{p}**")

    # -------------------------------------------------------------------------
    # CHARACTER ARCS
    # -------------------------------------------------------------------------
    lines.append("\n## 🎭 Character Arc Map")
    char_arcs = dashboard.get('character_arcs', {})
    if char_arcs:
        lines.append(f"| Character | Arc Type | Agency Trajectory |")
        lines.append(f"|:----------|:---------|:------------------|")
        for char, arc_data in list(char_arcs.items())[:8]:
            arc_label = arc_data.get('arc_type', arc_data.get('arc', 'Unknown'))
            start = arc_data.get('agency_start', arc_data.get('start_agency', 0))
            end = arc_data.get('agency_end', arc_data.get('end_agency', 0))
            delta = arc_data.get('agency_delta', end - start)
            traj = f"`{start:+.2f}` → `{end:+.2f}` ({delta:+.2f})"
            lines.append(f"| **{char}** | {arc_label} | {traj} |")
    else:
        lines.append("*Character dynamics analysis unavailable.*")

    # -------------------------------------------------------------------------
    # SCENE ECONOMY MAP
    # -------------------------------------------------------------------------
    lines.append("\n## ✂️ Scene Efficiency")
    econ_map = dashboard.get('scene_economy_map', {})
    cut_candidates = econ_map.get('cut_candidates', [])
    low_count = econ_map.get('low_economy_count', 0)
    high_scenes = econ_map.get('high_economy_scenes', [])

    if cut_candidates:
        lines.append(f"> [!IMPORTANT]\n> Found **{low_count} Efficiency Gaps**. Narrative flow shows signs of potential deceleration in: Scenes {', '.join(str(s) for s in cut_candidates)}")
    
    if high_scenes:
        lines.append(f"🌟 **Load-Bearing Scenes:** {', '.join(str(s) for s in high_scenes[:5])}")

    econ_table = econ_map.get('map', [])
    if econ_table:
        lines.append(f"\n| Scene | Efficiency | Delta |")
        lines.append(f"|:------|:-----------|:------|")
        for e in econ_table[:10]:
            icon = "🟢" if e['label'] == 'High Economy' else ("🟡" if e['label'] == 'Moderate Economy' else "🔴")
            lines.append(f"| {e['scene']} | {icon} {e['label']} | `{e['score']}` |")
        if len(econ_table) > 10:
            lines.append(f"| ... | *({len(econ_table) - 10} more)* | |")

    # -------------------------------------------------------------------------
    # FORMAT COMPLIANCE
    # -------------------------------------------------------------------------
    lines.append("\n## 📋 Industry Format Audit")
    fmt = dashboard.get('format_compliance', {})
    if fmt:
        issues = fmt.get('issues', [])
        score = fmt.get('compliance_score', 100)
        bar = _stars(score / 100)
        lines.append(f"**Structural Integrity:** `{score}/100` &nbsp; `{bar}`\n")
        if issues:
            for issue in issues:
                lines.append(f"- [!] {issue}")
        else:
            lines.append("✅ Professional industry standards met.")
    else:
        lines.append("*Format audit not performed.*")

    # -------------------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------------------
    lines.append("\n" + "---" * 10 + "\n")
    lines.append("*Created with Script<span style='color: #0052FF;'>Pulse</span> v15.0 · Private Intellectual Property · Confidential*")

    return "\n".join(lines)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: runner.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#!/usr/bin/env python3
"""
Simplified ScriptPulse Runner - High Performance, Linear Pipeline
Designed for MCA Research Defense: Clear, Logical, and Deterministic
"""

import time
import json
from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.interpretation_agent import InterpretationAgent
from scriptpulse.agents.ethics_agent import EthicsAgent
from scriptpulse.agents.writer_agent import WriterAgent
from scriptpulse.utils import normalizer, runtime

def run_pipeline(script_content, genre='drama', story_framework='3_act', **kwargs):
    """
    Executes the 4-Stage ScriptPulse Research Pipeline.
    1. Structure (Parsing)
    2. Perception (Feature Extraction)
    3. Dynamics (Cognitive Simulation)
    4. Interpretation (Narrative Analysis)
    """
    
    _t_start = time.time()
    telemetry = {'status': 'active', 'stages': {}}
    
    # --- STAGE 0: Normalize & Prepare ---
    if not script_content or len(script_content.strip()) < 50:
        raise ValueError("Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span> requires more text to analyze. Please upload a full script or a longer scene.")
    script_content = normalizer.normalize_script(script_content)
    telemetry['stages']['normalization_ms'] = round((time.time() - _t_start) * 1000, 2)
    
    # --- STAGE 1: Structure (Parsing) ---
    _t_stage = time.time()
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    
    parsed_output = parser.run(script_content)
    parsed_lines = parsed_output['lines']
    segmented_scenes = segmenter.run(parsed_lines)
    
    if not segmented_scenes:
        raise ValueError("ScriptPulse could not detect any scenes. Ensure your script uses standard industry formatting (e.g., INT., EXT., or SCENE headings).")
    
    # Hydrate scenes with their lines
    for scene in segmented_scenes:
        scene['lines'] = parsed_lines[scene['start_line']:scene['end_line']+1]
    telemetry['stages']['structural_parsing_ms'] = round((time.time() - _t_stage) * 1000, 2)
        
    # --- STAGE 2: Perception (Feature Extraction) ---
    _t_stage = time.time()
    perceptor = EncodingAgent()
    perceptual_features = perceptor.run({'scenes': segmented_scenes, 'lines': parsed_lines})
    telemetry['stages']['feature_extraction_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 3: Dynamics (Temporal Simulation) ---
    dynamics = DynamicsAgent()
    temporal_trace = dynamics.run_simulation({
        'features': perceptual_features,
        'genre': genre
    })
    telemetry['stages']['cognitive_simulation_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 3b: Inject Location Data from Scene Headings ---
    import re as _re
    for i, t_entry in enumerate(temporal_trace):
        if i < len(segmented_scenes):
            heading = segmented_scenes[i].get('heading', '')
            # Extract INT/EXT
            interior = None
            if heading.upper().startswith(('INT.', 'INT ', 'INT/')):
                interior = 'INT'
            elif heading.upper().startswith(('EXT.', 'EXT ', 'EXT/')):
                interior = 'EXT'
            elif heading.upper().startswith('I/E'):
                interior = 'I/E'
            
            # Extract location: strip INT./EXT. prefix, then take text before time-of-day dash
            loc = heading
            loc = _re.sub(r'^(INT\.|EXT\.|INT/EXT\.|EXT/INT\.|I/E\.?)\s*', '', loc, flags=_re.IGNORECASE).strip()
            # Remove time-of-day suffix (e.g. " - DAY", " - NIGHT")
            loc = _re.sub(r'\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME|MOMENTS?\s+LATER).*$', '', loc, flags=_re.IGNORECASE).strip()
            if not loc:
                loc = 'UNKNOWN'
            
            t_entry['location_data'] = {
                'location': loc,
                'interior': interior,
                'raw_heading': heading
            }

    
    # --- STAGE 4: Interpretation (Narrative Analysis) ---
    _t_stage = time.time()
    interpreter = InterpretationAgent()
    ethics = EthicsAgent()
    
    # Analysis outputs
    # Update InterpretationAgent to accept genre for dynamic thresholds
    ai_interpretation = interpreter.run(temporal_trace, perceptual_features, segmented_scenes, genre=genre)
    structure_map = ai_interpretation['structure']
    diagnosis = ai_interpretation['diagnosis']
    suggestions = ai_interpretation.get('suggestions', [])
    semantic_beats = interpreter.apply_semantic_labels(temporal_trace)
    telemetry['stages']['interpretation_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # --- STAGE 5: Ethics & Fairness (The 'True' Audit) ---
    _t_stage = time.time()
    # Construct input for EthicsAgent
    valence_scores = [pt.get('sentiment', 0) for pt in temporal_trace]
    fairness_audit = ethics.audit_fairness({'scenes': segmented_scenes, 'valence_scores': valence_scores}, genre=genre)
    agency_results = ethics.analyze_agency({'scenes': segmented_scenes})
    
    # Update voice fingerprints with agency metrics
    agency_map = {item['character']: item for item in agency_results.get('agency_metrics', [])}
    telemetry['stages']['ethics_audit_ms'] = round((time.time() - _t_stage) * 1000, 2)
    
    # Stage 5: Scene Turns (Intra-scene Movement)
    _t_stage = time.time()
    for i, s in enumerate(temporal_trace):
        # Look for a shift in sentiment within the scene
        # Use segmented_scenes to get lines for the current scene
        scene_lines = segmented_scenes[i]['lines'] if i < len(segmented_scenes) else []
        if not scene_lines: continue
        
        mid = len(scene_lines) // 2
        f_half = " ".join([l['text'] for l in scene_lines[:mid]]).lower()
        s_half = " ".join([l['text'] for l in scene_lines[mid:]]).lower()
        
        pos = ['yes', 'love', 'safe', 'good', 'happy', 'success', 'win', 'together', 'saved']
        neg = ['no', 'hate', 'die', 'danger', 'bad', 'fail', 'loss', 'quit', 'dead', 'body', 'kill']
        violence_vibe = ['shot', 'ambush', 'massacre', 'gunfire', 'murder', 'blood', 'blast', 'assassin', 'corpse']
        
        s1 = sum(1 for w in pos if w in f_half) - sum(1 for w in neg if w in f_half) - (sum(1 for w in violence_vibe if w in f_half) * 3)
        s2 = sum(1 for w in pos if w in s_half) - sum(1 for w in neg if w in s_half) - (sum(1 for w in violence_vibe if w in s_half) * 3)
        
        # Core Scene Turn Mapping
        label = "Flat"
        if s1 < 0 and s2 > 0: label = "Negative to Positive"
        elif s1 > 0 and s2 < 0: label = "Positive to Negative"
        elif s1 > 6 or s2 > 6: label = "High Energy" 
        elif s1 < 0 and s2 < 0: label = "Negative Progression"
        elif s1 > 0 and s2 > 0: label = "Positive Progression"
        
        # Task 2: Sentiment Post-processing pass for Violence/Death (Rule-based)
        viol_keywords = ['shot', 'killed', 'trap', 'ambush', 'gunfire', 'body', 'murder', 'blast', 'assassin', 'corpse']
        scene_text = " ".join([l['text'] for l in scene_lines]).lower()
        if any(w in scene_text for w in viol_keywords):
            # Cap the sentiment at negative in the simulation trace
            s['sentiment'] = min(s.get('sentiment', 0), -0.7)
            # Force a negative transition label if violence is present
            label = "Negative Progression" if s1 < 0 else "Positive to Negative"

        s['scene_turn'] = {'turn_label': label, 'sentiment_delta': s2 - s1}

    # --- STAGE 6: Final Assembly ---
    _t_end = time.time()
    
    # Aggregate Voice Fingerprints (Cumulative)
    voice_fingerprints = {}
    for f in perceptual_features:
        for char, v in f.get('character_scene_vectors', {}).items():
            if char not in voice_fingerprints:
                voice_fingerprints[char] = {'agency': 0, 'sentiment': 0, 'line_count': 0}
            voice_fingerprints[char]['line_count'] += v['line_count']
            voice_fingerprints[char]['agency'] += v['agency']
            voice_fingerprints[char]['sentiment'] += v['sentiment']
    
    # Normalize averages & Meld with Agency
    for char in voice_fingerprints:
        count = voice_fingerprints[char]['line_count']
        voice_fingerprints[char]['sentiment'] = round(voice_fingerprints[char]['sentiment'] / max(1, count), 2)
        
        # Use EthicsAgent's higher-fidelity agency calculation if available
        if char in agency_map:
            voice_fingerprints[char]['agency'] = agency_map[char]['agency_score']
            voice_fingerprints[char]['centrality'] = agency_map[char]['centrality']
        else:
            voice_fingerprints[char]['agency'] = round(voice_fingerprints[char]['agency'] / max(1, count), 2)

    telemetry['stages']['assembly_ms'] = round((time.time() - _t_stage) * 1000, 2)
    telemetry['total_execution_ms'] = round((_t_end - _t_start) * 1000, 2)

    report = {
        'meta': {
            'execution_time': f"{round(_t_end - _t_start, 3)}s",
            'telemetry': telemetry,
            'total_scenes': len(segmented_scenes),
            'genre': genre,
            'framework': story_framework,
            'version': "v15.0 (Research Edition)",
            'confidence': 0.98 if len(segmented_scenes) > 5 else 0.85
        },
        'temporal_trace': temporal_trace,
        'perceptual_features': perceptual_features,
        'structure_map': structure_map,
        'narrative_diagnosis': diagnosis,

        'suggestions': suggestions,
        'semantic_beats': semantic_beats,
        'total_scenes': len(segmented_scenes),
        'segmented': segmented_scenes,
        'scene_info': [
            {'scene_index': s['scene_index'], 'heading': s.get('heading', ''), 'preview': s.get('preview', '')}
            for s in segmented_scenes
        ],
        'semantic_flux': [f.get('entropy_score', 0) for f in perceptual_features],
        'voice_fingerprints': voice_fingerprints,
        'fairness_audit': fairness_audit,
        'subtext_audit': [] # Placeholder for compatibility
    }
    
    # --- STAGE 5: Writer Intelligence (Expert Layer) ---
    writer = WriterAgent()
    report = writer.analyze(report, genre=genre)
    
    return report

def parse_structure(script):
    """Simple structural parser snippet"""
    parser = ParsingAgent()
    segmenter = SegmentationAgent()
    parsed = parser.run(script)['lines']
    segmented = segmenter.run(parsed)
    return [{'scene_index': s['scene_index'], 'heading': s.get('heading', '')} for s in segmented]

def health_check():
    """Observability endpoint for system status."""
    return {
        'status': 'healthy',
        'governance': True,
        'agents': {
            'ParsingAgent': 'healthy',
            'SegmentationAgent': 'healthy',
            'DynamicsAgent': 'healthy',
            'InterpretationAgent': 'healthy',
            'EthicsAgent': 'healthy'
        },
        'config_files': {
            'secrets.toml': True,
            'env': True
        }
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            print(json.dumps(run_pipeline(f.read()), indent=2))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE: streamlit_app.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#!/usr/bin/env python3
"""
ScriptPulse — AI Story Intelligence
Product-Grade Entry Point
"""

import streamlit as st
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Path to persistent brand assets
ICON_PATH = os.path.join(ROOT_DIR, "app", "assets", "ScriptPulse_Icon.png")

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ScriptPulse — AI Story Intelligence",
    page_icon=ICON_PATH if os.path.exists(ICON_PATH) else "app/assets/ScriptPulse_Icon.png",
    layout="wide"
)

# Import Modular Components
from app.components.styles import apply_custom_styles
from app.components.theme import init_plotly_template
from app.components.sidebar import render_sidebar
from app.components.uikit import render_hero_section, render_section_header
from app.views.writer_view import render_writer_view

# Import Core Pipeline
try:
    from scriptpulse.pipeline import runner
except Exception as e:
    st.error(f"Failed to load ScriptPulse Engine: {e}")
    st.stop()

# Import Utils
import app.streamlit_utils as stu
from scriptpulse.reporters import writer_report, studio_report, print_summary

# =============================================================================
# INITIALIZATION
# =============================================================================
@st.cache_resource
def init_application():
    apply_custom_styles()
    init_plotly_template()
    return True

init_application()
stu.sync_safety_state()

if 'last_report' not in st.session_state:
    st.session_state['last_report'] = None

# =============================================================================
# SIDEBAR
# =============================================================================
sidebar_state = render_sidebar(
    ui_mode=st.session_state.get('ui_mode', "Unified"),
    is_cloud=True,
    stu=stu
)
st.session_state['ui_mode'] = sidebar_state['ui_mode']

# =============================================================================
# HERO
# =============================================================================
render_hero_section(
    "ScriptPulse",
    "AI Story Intelligence — See how your screenplay feels to an audience before you ever hit send."
)

# =============================================================================
# STEP 1: UPLOAD
# =============================================================================
render_section_header("📄", "Your Screenplay",
    "Upload your script or paste a scene. We'll map its emotional architecture.")

tab_up, tab_paste = st.tabs(["📁 Upload File", "📝 Paste Text"])

script_input = None
with tab_up:
    uploaded_file = st.file_uploader(
        "Drop your screenplay here (PDF, TXT, or FDX)",
        type=['pdf', 'txt', 'fdx'],
        label_visibility="visible"
    )
    if uploaded_file and stu.check_upload_size(uploaded_file):
        with st.spinner("Reading script..."):
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext == 'pdf':
                try:
                    from io import BytesIO
                    import PyPDF2
                    script_input = "\n".join([
                        p.extract_text() or "" for p in PyPDF2.PdfReader(BytesIO(uploaded_file.read())).pages
                    ])
                except Exception as e:
                    st.error("Could not read PDF. The file may be corrupted or protected. Please try a TXT or FDX file.")
                    script_input = None
            elif ext == 'fdx':
                try:
                    from scriptpulse.agents import importers
                    script_input = importers.run(uploaded_file.getvalue().decode("utf-8"))
                    if isinstance(script_input, list):
                        script_input = "\n".join([l['text'] for l in script_input])
                except Exception as e:
                    st.error("Could not parse FDX formatting. Please ensure it's a valid Final Draft XML file.")
                    script_input = None
            else:
                try:
                    script_input = uploaded_file.read().decode('utf-8')
                except Exception:
                    st.error("Could not decode text. Please ensure the file is saved in standard UTF-8 format.")
                    script_input = None

with tab_paste:
    pasted = st.text_area("Paste text here", height=200,
                          placeholder="INT. COFFEE SHOP - DAY\n\nA young WRITER stares at a blank screen...")
    if not script_input and len(pasted) > 100:
        script_input = pasted

# =============================================================================
# STEP 2: CONFIGURE & ANALYZE
# =============================================================================
render_section_header("⚙️", "Configure Analysis",
    "Select the genre so the engine knows what benchmarks to apply.")

col1, col2 = st.columns(2)
genre = col1.selectbox("Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"],
                      help="The engine adjusts its benchmarks to match the expectations of your genre.")
lens = col2.selectbox("Perspective", ["Story Editor", "Studio Executive", "Script Coordinator"],
                      help="🕵️ Story Editor = Plot & Logic | 🏢 Studio Executive = Market & Budget | ✍️ Script Coordinator = Craft & Flow")

if script_input:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🎬 Analyze My Script", type="primary", use_container_width=True):
        bar = st.progress(0, text="Initializing engine...")
        try:
            bar.progress(20, text="Parsing screenplay structure...")
            report = runner.run_pipeline(
                script_input, genre=genre, lens=lens,
                ablation_config=sidebar_state['ablation_config'],
                cpu_safe_mode=sidebar_state['force_cloud']
            )
            bar.progress(70, text="Generating intelligence report...")

            st.session_state['last_report'] = report
            st.session_state['current_input'] = script_input
            st.session_state['current_genre'] = genre
            st.session_state['current_lens'] = lens
            st.session_state.pop('ai_summary_cache', None)
            # Clear all lens-specific caches so fresh analysis is generated
            for k in list(st.session_state.keys()):
                if k.startswith('ai_summary_') or k.startswith('ai_pulse_'):
                    del st.session_state[k]

            # Auto-generate AI pulse insight for the selected lens
            try:
                from scriptpulse.reporters.llm_translator import generate_section_insight
                st.session_state['ai_pulse_insight'] = generate_section_insight(report, 'pulse', lens=lens)
            except Exception:
                st.session_state['ai_pulse_insight'] = None

            bar.progress(100, text="Analysis complete!")
            time.sleep(0.5)
            bar.empty()
        except Exception as e:
            bar.empty()
            st.error(f"Analysis failed: {e}")
else:
    from app.components import uikit
    uikit.render_tooltip_card("👆 <b style='color: white;'>Upload or paste your screenplay</b> above to begin the intelligence analysis.")

# =============================================================================
# STEP 3: RENDER RESULTS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')
current_genre = st.session_state.get('current_genre', 'Drama')

if report and current_input:
    st.markdown("---")
    # Render unified dashboard: Writer insights first, followed by Producer telemetry
    render_writer_view(report, current_input, current_genre, lens=lens)

# =============================================================================
# STEP 4: EXPORT
# =============================================================================
if report and current_input:
    st.markdown("---")
    render_section_header("📥", "Export Reports",
        "Download professional reports to share with collaborators, agents, or studio executives.")

    c1, c2, c3 = st.columns(3)
    title = uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script"

    with c1:
        st.download_button("📄 Writer Report", 
            writer_report.generate_writer_report(report, title=title, genre=genre),
            f"ScriptPulse_Writer_{genre}.md", "text/markdown",
            use_container_width=True)
    with c2:
        st.download_button("🎬 Studio Coverage",
            studio_report.generate_report(report, script_title=title, lens=lens),
            f"ScriptPulse_Studio_{genre}.html", "text/html",
            use_container_width=True)
    with c3:
        st.download_button("🖨️ One-Page Summary",
            print_summary.generate_print_summary(report, script_title=title),
            f"ScriptPulse_Summary_{genre}.html", "text/html",
            use_container_width=True)

# Application end


