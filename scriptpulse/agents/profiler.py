"""
ScriptPulse Profiler Agent (Cognitive Modeling Layer)
Gap Solved: "The Universal Reader Fallacy"

Provides parameters for the Temporal Dynamics engine based on the 
simulated audience's cognitive capacity.
"""

def get_profile(profile_name="general"):
    """
    Returns cognitive physics parameters for a specific audience type.
    
    Params:
    - lambda_base: Fatigue carryover (Higher = Memory lasts longer).
    - beta_recovery: Recovery rate (Higher = Bounces back faster).
    - fatigue_threshold: Tolerance for Strain (Higher = Harder to tire).
    - coherence_weight: Sensitivity to Context Switches (Higher = Easily confused).
    """
    
    profiles = {
        # Standard Ideal Viewer (Baseline)
        'general': {
            'lambda_base': 0.85,
            'beta_recovery': 0.3,
            'fatigue_threshold': 1.0, # Relative scale factor
            'coherence_weight': 0.15
        },
        
        # The "Cinephile/Critic"
        # - High capacity (hard to tire)
        # - Long memory (high lambda)
        # - Low sensitivity to confusion (likes complexity)
        'cinephile': {
            'lambda_base': 0.90,     # Remembers plot points longer
            'beta_recovery': 0.4,    # Recovers conceptual energy faster
            'fatigue_threshold': 1.3, # Tolerates more strain
            'coherence_weight': 0.10 # Handles jumps easily
        },
        
        # The "Distracted/Mobile Viewer"
        # - Low capacity (tires fast)
        # - Short memory (low lambda - needs constant refreshing)
        # - High sensitivity to confusion (needs clarity)
        'distracted': {
            'lambda_base': 0.75,     # Forgets context quickly
            'beta_recovery': 0.2,    # Slow recovery / easily drained
            'fatigue_threshold': 0.8, # Low tolerance
            'coherence_weight': 0.30 # Hates confusion
        },
        
        # The "Young/Child Viewer"
        # - Very low threshold
        # - Needs linear continuity
        'child': {
            'lambda_base': 0.70,
            'beta_recovery': 0.5,     # Bounces back IF relaxed
            'fatigue_threshold': 0.6, # Very low tolerance for complexity
            'coherence_weight': 0.40 # Needs simple transitions
        }
    }
    
    return profiles.get(profile_name.lower(), profiles['general'])
