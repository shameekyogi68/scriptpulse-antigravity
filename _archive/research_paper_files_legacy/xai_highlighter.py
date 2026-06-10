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
