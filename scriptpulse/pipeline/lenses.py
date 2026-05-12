# MODULE: lenses.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse Lenses - Contextual Weighting Filters
Defines three distinct professional perspectives through which a script is analyzed.
Each lens has unique weights, vocabulary priorities, and a professional persona.
"""

# ── Master Lens Registry ──────────────────────────────────────────────────────

LENSES = {

    # ── STUDIO EXECUTIVE ──────────────────────────────────────────────────────
    # Reads for commercial return: budget risk, audience fit, market positioning.
    # Cares about: engagement floor, act pacing, cast size, location count.
    # Does NOT care about: line-by-line dialogue quality or formatting minutiae.
    'Studio Executive': {
        'lens_id': 'Studio Executive',
        'short_id': 'exec',
        'description': 'Commercial viability · Audience breadth · Budget & market risk',
        'color': '#6366f1',   # Indigo — bold, decisive
        'icon': '📊',
        'signal_priority': ['engagement', 'market_readiness', 'budget_impact', 'act_structure'],
        'vocabulary': ['ROI', 'Comp', 'Demographic', 'Four-Quadrant', 'Greenlight',
                       'Opening Weekend', 'P&A', 'Vertical Integration', 'IP', 'Marketability'],
        'effort_weights': {
            'cognitive_mix': 0.65,
            'emotional_mix': 0.35,
            'cognitive_components': {
                'structural': 0.60,   # Act beats and pacing arcs matter most
                'semantic':   0.25,   # Genre fit and theme clarity
                'syntactic':  0.15    # Line craft is low priority
            },
            'emotional_components': {
                'dialogue_engagement': 0.20,  # Not the exec's primary lens
                'visual_intensity':    0.50,  # Set-piece potential (budget indicator)
                'linguistic_volume':   0.10,
                'stillness_penalty':   0.20   # Low-energy sections kill greenlight
            }
        },
        # Which diagnostic icons this lens PRIORITISES (shown first / highlighted)
        'priority_icons': ['🔴', '🚫', '📉', '⚠️', '🎢', '🟠', '✨'],
        # Which rewrite-priority keywords this lens cares about
        'priority_keywords': ['engagement', 'budget', 'cut', 'boredom', 'slow', 'unfilmable', 'name'],
    },

    # ── STORY EDITOR ──────────────────────────────────────────────────────────
    # Reads for internal narrative logic: causality, stakes, arc, character truth.
    # Cares about: beat placement, character agency, tonal consistency, subtext.
    # Does NOT care about: production budget or line-level formatting.
    'Story Editor': {
        'lens_id': 'Story Editor',
        'short_id': 'editor',
        'description': 'Narrative logic · Character arcs · Structural integrity',
        'color': '#3b82f6',   # Blue — thoughtful, craft-focused
        'icon': '🧵',
        'signal_priority': ['structural_turning_points', 'character_arcs', 'conflict', 'diagnosis'],
        'vocabulary': ['Beat', 'Arc', 'Causality', 'Inciting Incident', 'Midpoint', 'Climax',
                       'Emotional Stakes', 'Subtext', 'Character Agency', 'Thematic Resonance'],
        'effort_weights': {
            'cognitive_mix': 0.70,
            'emotional_mix': 0.30,
            'cognitive_components': {
                'structural': 0.40,   # Structure and beats
                'semantic':   0.40,   # Theme, character logic, causality
                'syntactic':  0.20    # Moderate — cares about voice but not formatting
            },
            'emotional_components': {
                'dialogue_engagement': 0.35,  # Character voice matters to editor
                'visual_intensity':    0.30,  # Scene energy and atmosphere
                'linguistic_volume':   0.20,  # Volume of emotional exchange
                'stillness_penalty':   0.15
            }
        },
        'priority_icons': ['🧵', '⬜', '👻', '✅', '🔵', '🔴', '⭐', '✨', '🟡',
                           '🎢', '🟠', '🗣️', '🧠', '💡', '💎'],
        'priority_keywords': [],  # Story editor sees all priorities
    },

    # ── SCRIPT COORDINATOR ────────────────────────────────────────────────────
    # Reads for the physical experience of the page: rhythm, economy, voice texture.
    # Cares about: dialogue-to-action ratio, white space, scene length, prose style.
    # Does NOT care about: high-level commercial viability or abstract theme.
    'Script Coordinator': {
        'lens_id': 'Script Coordinator',
        'short_id': 'coord',
        'description': 'Dialogue economy · Visual rhythm · Page-level craft',
        'color': '#10b981',   # Emerald — precise, technical
        'icon': '✂️',
        'signal_priority': ['scene_economy_map', 'dialogue_action_ratio', 'format_compliance'],
        'vocabulary': ['White Space', 'Rhythm', 'Flow', 'Scene Economy', 'Talking Head',
                       'Slug Line', 'Action Block', 'Parenthetical', 'Prose Economy',
                       'Dialogue Compression', 'Visual Subtext'],
        'effort_weights': {
            'cognitive_mix': 0.40,
            'emotional_mix': 0.60,
            'cognitive_components': {
                'structural': 0.30,   # Structure is secondary — craft is primary
                'semantic':   0.30,   # Theme and intent of lines
                'syntactic':  0.40    # Word choice, rhythm, prose style — highest weight
            },
            'emotional_components': {
                'dialogue_engagement': 0.50,  # Dialogue is the primary craft signal
                'visual_intensity':    0.10,  # Action lines matter less here
                'linguistic_volume':   0.30,  # Word economy and rhythm
                'stillness_penalty':   0.10
            }
        },
        'priority_icons': ['✂️', '🔴', '🟠', '🚫', '💎', '⛓️', '🎭', '👥',
                           '🎙️', '🟢', '🗣️', '🧠', '💡', '✨'],
        'priority_keywords': ['dialogue', 'show', 'unfilmable', 'fluff', 'prose', 'voice', 'economy'],
    },
}

# ── Legacy alias support (old code used 'viewer'/'reader'/'narrator') ─────────
_LEGACY_ALIAS = {
    'viewer':   'Studio Executive',
    'reader':   'Story Editor',
    'narrator': 'Script Coordinator',
}


def get_lens(lens_id: str) -> dict:
    """
    Returns the full lens configuration for the given lens ID.
    Supports both new names ('Studio Executive', 'Story Editor', 'Script Coordinator')
    and legacy short-form IDs ('viewer', 'reader', 'narrator').
    Falls back to 'Story Editor' if an unknown lens is requested.
    """
    # Resolve legacy aliases
    resolved = _LEGACY_ALIAS.get(lens_id, lens_id)
    return LENSES.get(resolved, LENSES['Story Editor'])


def list_lenses() -> list:
    """Returns a list of all available lens IDs."""
    return list(LENSES.keys())


def get_persona_description(lens_id: str, mode: str = 'full') -> str:
    """
    Returns the AI persona description for a given lens.
    mode='full'   — full sentence for system prompt injection
    mode='short'  — one-line role label for UI display
    """
    descriptions = {
        'Studio Executive': {
            'full': (
                "a sharp-eyed Development Executive at a major studio. "
                "Focus on commercial viability, audience demographic expansion, "
                "budget risks, and market positioning. Use vocabulary like: "
                "ROI, Comp, Demographic, Four-Quadrant, Greenlight, IP, Marketability. "
                "You assess scripts the way a greenlight committee does — fast, decisive, numbers-first."
            ),
            'short': "Studio Executive — Commercial & Market",
        },
        'Story Editor': {
            'full': (
                "a master Story Editor for major film and television productions. "
                "Focus on internal character logic, narrative causality, emotional stakes, "
                "structural beats, and thematic resonance. Use vocabulary like: "
                "Beat, Arc, Causality, Inciting Incident, Midpoint, Subtext, Character Agency. "
                "You read for the invisible architecture beneath the words."
            ),
            'short': "Story Editor — Structure & Character",
        },
        'Script Coordinator': {
            'full': (
                "a technical Script Analyst and Pacing Consultant. "
                "Focus on dialogue economy, visual description energy, scene-to-scene transitions, "
                "white space balance, and stylistic consistency. Use vocabulary like: "
                "White Space, Rhythm, Flow, Scene Economy, Talking Head, Dialogue Compression. "
                "You experience the script the way a reader feels it on the page — word by word."
            ),
            'short': "Script Coordinator — Page Craft & Rhythm",
        },
    }
    resolved = _LEGACY_ALIAS.get(lens_id, lens_id)
    lens_desc = descriptions.get(resolved, descriptions['Story Editor'])
    return lens_desc.get(mode, lens_desc['short'])
