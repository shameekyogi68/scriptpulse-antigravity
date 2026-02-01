"""
ScriptPulse Hall of Fame Imprints (Studio Platform Layer)
Gap Solved: "The So What? Problem"

Provides synthetic structural traces of "Classic" narrative templates.
Since we cannot copyright-infringe actual scripts, we use theoretical templates.
"""

import math

def resample(trace, target_length):
    """
    Stretch or shrink a trace to match target_length using linear interpolation.
    """
    if not trace or target_length <= 0:
        return []
    
    src_len = len(trace)
    step = (src_len - 1) / (target_length - 1) if target_length > 1 else 0
    
    new_trace = []
    for i in range(target_length):
        x = i * step
        idx = int(x)
        frac = x - idx
        
        if idx >= src_len - 1:
            val = trace[-1]
        else:
            val = trace[idx] * (1 - frac) + trace[idx+1] * frac
            
        new_trace.append(val)
    return new_trace

# === TEMPLATES ===

# 1. The "Save the Cat" Standard (Blake Snyder)
# Opening Image (Low) -> Catalyst (High) -> Fun of Games (Med) -> All is Lost (Low) -> Finale (High)
SAVE_THE_CAT = [
    0.3, # Opening Image
    0.4, # Setup
    0.8, # Catalyst (Inciting Incident)
    0.5, # Debate
    0.6, # Break into Two
    0.7, # Fun and Games (Rising)
    0.9, # Midpoint
    0.4, # Bad Guys Close In
    0.1, # All is Lost (Low point)
    0.3, # Dark Night of the Soul
    0.8, # Break into Three
    0.95, # Finale
    0.4  # Final Image
]

# 2. Although we can't use Die Hard's actual data, we can model the "Action Thriller" pulse.
# Constant escalation.
ACTION_THRILLER = [
    0.4, 0.45, 0.5, 0.8 (Inciting), 
    0.5, 0.6, 0.7, 0.9 (Midpoint),
    0.6, 0.7, 0.8, 0.95 (Climax), 0.3
]

# 3. Slow Burn / Horror (The "Se7en" Arc)
# Low tension for a long time, then exponential rise.
SLOW_BURN = [
    0.2, 0.2, 0.25, 0.3, 0.3, 0.35, 
    0.4, 0.5, 0.6, 0.8, 1.0 (Shock Ending)
]

IMPRINTS = {
    "Save the Cat (Standard Structure)": SAVE_THE_CAT,
    "High Octane Action (Die Hard Style)": ACTION_THRILLER,
    "Slow Burn Horror (Hereditary Style)": SLOW_BURN
}

def get_imprint(name, target_length):
    """
    Get a resized trace for the given template name.
    """
    template = IMPRINTS.get(name, SAVE_THE_CAT)
    return resample(template, target_length)
