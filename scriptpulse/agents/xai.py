"""
ScriptPulse XAI Agent (Explainable AI)
Gap Solved: "The Black Box Problem"

Decomposes the final Effort signal into its constituent drivers:
- Syntax (Tree Depth)
- Semantics (Entropy/Confusion)
- Structure (Breaks/Transitions)
- Motion (Visual Action)
- Dialogue (Social/Emotional)

Provides the "Why" behind the "High Strain" alert.
"""

from . import temporal # Reuse weights logic

def run(data, lens_config=None):
    """
    Decompose effort for each scene.
    
    Args:
        data: {
            'features': standard features,
            'semantic_scores': ...,
            'syntax_scores': ...
        }
        
    Returns:
        List of dicts: [
            {'drivers': {'syntax': 0.4, 'semantics': 0.1, ...}, 'dominance': 'syntax'},
            ...
        ]
    """
    features = data.get('features', [])
    semantic_scores = data.get('semantic_scores', [])
    syntax_scores = data.get('syntax_scores', [])
    
    xai_output = []
    
    # Get Weights (Hardcoded to match temporal.py defaults for consistency)
    # Ideally temporal.py should export its standard weights, but we'll reflect them here to avoid import cycles or complex dependency.
    # We will assume Standard Viewer weights.
    
    w_cog_mix = 0.55
    w_emo_mix = 0.45
    
    # Cognitive Internal Breakdown
    # 0.6 Structure, 0.2 Sem, 0.2 Syn
    ratio_struct = 0.6
    ratio_sem = 0.2
    ratio_syn = 0.2
    
    # Emotional Internal Breakdown (Approximate from temporal.py default weights)
    # weights['emotional_components'] = {dial_engagement: 0.35, visual: 0.30, ling_vol: 0.20, still: 0.15}
    # We group these into 'Motion' (Visual) and 'Dialogue' (Engagement+Vol).
    
    for i, scene in enumerate(features):
        sem = semantic_scores[i] if i < len(semantic_scores) else 0.0
        syn = syntax_scores[i] if i < len(syntax_scores) else 0.0
        
        # 1. Calculate Component Raw Scores (Normalized 0-1)
        
        # Structure (Base Structural Load)
        # Re-calc base_struct_load roughly from features
        # We need a simplified proxy or the exact calc. Let's do exact-ish reproduction.
        ling = scene['linguistic_load']
        dial = scene['dialogue_dynamics']
        visual = scene['visual_abstraction']
        ref = scene['referential_load']
        struct = scene['structural_change']
        
        # Component: Structure/Cognitive Form
        # Includes Ref tracking + Parsing Variance + Event Boundaries + Switches
        # Approx:
        raw_struct = (
            (ref['active_character_count']/10.0 + ref['character_reintroductions']/5.0) * 0.3 + 
            (ling['sentence_length_variance']/20.0) * 0.3 + 
            (struct['event_boundary_score']/100.0) * 0.25 + 
            (dial['speaker_switches']/20.0) * 0.15
        )
        
        # Component: Syntax (Tree Depth)
        raw_syn = syn
        
        # Component: Semantics (Entropy)
        raw_sem = sem
        
        # Component: Motion (Visual Action)
        raw_motion = (visual['action_lines']/50.0 + visual['continuous_action_runs']/10.0)
        
        # Component: Dialogue (Emotional Engagement + Flow)
        raw_dial = (dial['dialogue_turns']/50.0) * 0.6 + (ling['sentence_count']/50.0) * 0.4
        
        # 2. Apply Weighting (Contributions to Total Effort)
        
        # Cognitive Branch
        contrib_struct = w_cog_mix * ratio_struct * raw_struct
        contrib_syn    = w_cog_mix * ratio_syn    * raw_syn
        contrib_sem    = w_cog_mix * ratio_sem    * raw_sem
        
        # Emotional Branch
        # Approx allocation: Visual is ~30% of Emo. Dialogue is ~70%.
        contrib_motion = w_emo_mix * 0.30 * raw_motion
        contrib_dial   = w_emo_mix * 0.70 * raw_dial
        
        total = contrib_struct + contrib_syn + contrib_sem + contrib_motion + contrib_dial
        
        # Avoid div zero
        if total < 0.001:
            total = 1.0 # arbitrary to zero out percentages
            
        drivers = {
            'Structure': round(contrib_struct / total, 2),
            'Syntax':    round(contrib_syn / total, 2),
            'Semantics': round(contrib_sem / total, 2),
            'Motion':    round(contrib_motion / total, 2),
            'Dialogue':  round(contrib_dial / total, 2)
        }
        
        # Find dominant driver
        dominant = max(drivers, key=drivers.get)
        
        xai_output.append({
            'scene_index': scene['scene_index'],
            'drivers': drivers,
            'dominant_driver': dominant
        })
        
    return xai_output
