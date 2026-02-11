"""
ScriptPulse Model Manager (MLOps Layer)
Centralizes model loading, caching, and hardware acceleration logic.
"""

import os
import sys

# Centralized Imports
try:
    import torch
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
except ImportError:
    torch = None
    pipeline = None
    SentenceTransformer = None

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
            # Optional: MPS for Mac (if needed later)
            # elif torch.backends.mps.is_available(): ...
            
        print(f"[MLOps] Model Cache: {self.cache_dir}")
        print(f"[MLOps] Acceleration: {'CUDA' if self.device == 0 else 'CPU'}")
        
    def get_pipeline(self, task, model_name):
        """
        Get a HuggingFace pipeline with caching.
        """
        if not pipeline:
            return None
            
        try:
            # Check cache explicitly or let HF handle it via cache_dir
            # HF transformers automatically handles caching if we point to a dir
            # We set the environment variable or pass cache_dir
            
            print(f"[MLOps] Loading Pipeline: {model_name}...")
            return pipeline(
                task, 
                model=model_name, 
                device=self.device,
                model_kwargs={"cache_dir": self.cache_dir} 
            )
        except Exception as e:
            print(f"[MLOps] Failed to load pipeline {model_name}: {e}")
            return None

    def get_sentence_transformer(self, model_name):
        """
        Get a SentenceTransformer model with caching.
        """
        if not SentenceTransformer:
            return None
            
        try:
            print(f"[MLOps] Loading Sentence Transformer: {model_name}...")
            return SentenceTransformer(model_name, cache_folder=self.cache_dir)
        except Exception as e:
            print(f"[MLOps] Failed to load SBERT {model_name}: {e}")
            return None

# Singleton Access
manager = ModelManager()
