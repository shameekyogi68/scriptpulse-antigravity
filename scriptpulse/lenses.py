"""
ScriptPulse Analysis Lens Registry (vNext.5)

Defines the weight configurations for different modes of consumption:
1. Viewer (Default): Balanced visual/dialogue (Simulates screen viewing)
2. Reader: Emphasizes page mechanics, text density, and scanning load
3. Narrator: Emphasizes rhythm, speakability, and dialogue flow
4. Listener (Future): Emphasizes auditory cues only
"""

LENSES = {
    "viewer": {
        "lens_id": "viewer",
        "description": "Balanced simulation of watching the film (Default).",
        "effort_weights": {
            "cognitive_mix": 0.55,
            "emotional_mix": 0.45,
            "cognitive_components": {
                "ref_score": 0.30,
                "ling_complexity": 0.30,
                "struct_score": 0.25,
                "dial_tracking": 0.15
            },
            "emotional_components": {
                "dial_engagement": 0.35,
                "visual_score": 0.30,
                "ling_volume": 0.20,
                "stillness_factor": 0.15
            }
        }
    },
    "reader": {
        "lens_id": "reader",
        "description": "Simulates the cognitive load of reading the physical page.",
        "effort_weights": {
            "cognitive_mix": 0.60,  # Reading is slightly more cognitive
            "emotional_mix": 0.40,
            "cognitive_components": {
                "ref_score": 0.20,
                "ling_complexity": 0.45,  # Syntax/sentence structure is heavier for readers
                "struct_score": 0.20,
                "dial_tracking": 0.15
            },
            "emotional_components": {
                "dial_engagement": 0.20,
                "visual_score": 0.45,     # Dense action blocks are physically harder to read
                "ling_volume": 0.25,      # Word count matters more
                "stillness_factor": 0.10
            }
        }
    },
    "narrator": {
        "lens_id": "narrator",
        "description": "Simulates the oral experience of speaking/performing the script.",
        "effort_weights": {
            "cognitive_mix": 0.40,
            "emotional_mix": 0.60,  # Performance is more emotional/flow based
            "cognitive_components": {
                "ref_score": 0.20,
                "ling_complexity": 0.20,
                "struct_score": 0.20,
                "dial_tracking": 0.40     # Crucial to track 'who speaks next'
            },
            "emotional_components": {
                "dial_engagement": 0.50,  # The core of narration
                "visual_score": 0.10,     # Visuals are secondary to flow
                "ling_volume": 0.25,      # Breath control
                "stillness_factor": 0.15
            }
        }
    }
}

def get_lens(lens_id="viewer"):
    """
    Retrieve a lens configuration by ID. 
    Returns 'viewer' (default) if ID not found.
    """
    return LENSES.get(lens_id, LENSES["viewer"])

def list_lenses():
    """Return list of available lens IDs and descriptions."""
    return [{
        "id": k, 
        "description": v["description"]
    } for k, v in LENSES.items()]
