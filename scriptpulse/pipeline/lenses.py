"""
ScriptPulse Lenses - Contextual Weighting Filters
Defines different 'lenses' through which the script can be experienced.
"""

def get_lens(lens_id):
    """
    Returns the weight configuration for a specific lens.
    """
    lenses = {
        'viewer': {
            'lens_id': 'viewer',
            'description': 'Watch Mode (Balanced Viewer Experience)',
            'effort_weights': {
                'cognitive_mix': 0.55,
                'emotional_mix': 0.45,
                'cognitive_components': {'structural': 0.6, 'semantic': 0.2, 'syntactic': 0.2},
                'emotional_components': {
                    'dialogue_engagement': 0.35, 
                    'visual_intensity': 0.30, 
                    'linguistic_volume': 0.20, 
                    'stillness_penalty': 0.15
                }
            }
        },
        'reader': {
            'lens_id': 'reader',
            'description': 'Read Mode (Producer/Executive Perspective)',
            'effort_weights': {
                'cognitive_mix': 0.70,
                'emotional_mix': 0.30,
                'cognitive_components': {'structural': 0.4, 'semantic': 0.4, 'syntactic': 0.2},
                'emotional_components': {
                    'dialogue_engagement': 0.25, 
                    'visual_intensity': 0.45, 
                    'linguistic_volume': 0.15, 
                    'stillness_penalty': 0.15
                }
            }
        },
        'narrator': {
            'lens_id': 'narrator',
            'description': 'Narrate Mode (Voice and Rhythm Perspective)',
            'effort_weights': {
                'cognitive_mix': 0.40,
                'emotional_mix': 0.60,
                'cognitive_components': {'structural': 0.3, 'semantic': 0.3, 'syntactic': 0.4},
                'emotional_components': {
                    'dialogue_engagement': 0.50, 
                    'visual_intensity': 0.10, 
                    'linguistic_volume': 0.30, 
                    'stillness_penalty': 0.10
                }
            }
        }
    }
    
    return lenses.get(lens_id, lenses['viewer'])
