"""
ScriptPulse Model Manager (MLOps Layer)
Centralizes model loading, caching, and hardware acceleration logic.
v14.0: Strict model version enforcement + structured logging.
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
# This drops SBERT (~80MB), GPT-2 (~500MB), and DistilBART (~300MB) from the 
# process heap. All agents fall through to their existing fast heuristic 
# fallbacks. Analytical output structure is identical; only ML-specific 
# subfields (e.g. raw embeddings) will be zeroed or approximated.
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
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'required_model_versions.json'
)

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.init_config()
        return cls._instance
        
    def init_config(self):
        """Initialize caching and device settings."""
        # Persistent Cache Directory
        self.cache_dir = os.path.expanduser("~/.scriptpulse/models")
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

    def get_sentence_transformer(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Get a SentenceTransformer model (MiniLM).
        Loaded from HuggingFace Hub on first use, then cached locally.
        """
        if _HEURISTICS_ONLY:
            return None
        if not SentenceTransformer:
            return None
        
        self._verify_model('sentence-transformer', model_name)
            
        try:
            if model_name not in self._loaded_models:
                logger.info("Loading SBERT: %s...", model_name)
                self._loaded_models[model_name] = SentenceTransformer(model_name, cache_folder=self.cache_dir)
            return self._loaded_models[model_name]
        except Exception as e:
            logger.error("Failed to load SBERT %s: %s", model_name, e)
            return None

    def get_zero_shot(self):
        """
        Get a Zero-Shot Classifier (DistilBART).
        Uses DistilBART-MNLI (~300MB) instead of BERT-Large (~1.3GB) to save resources.
        """
        if _HEURISTICS_ONLY:
            return None
        
        # Consistent with required_model_versions.json
        spec = self._required_versions.get('zero-shot-classification', {})
        model_name = spec.get('name', "valhalla/distilbart-mnli-12-3")
        
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
        to return SBERT/GPT-2 heap to the OS before the next UI render.
        """
        import gc
        self._loaded_models.clear()
        gc.collect()
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("ModelManager: model references released, GC triggered.")


# Singleton Access
manager = ModelManager()

