#!/usr/bin/env python3
"""
ScriptPulse vNext.4 - Writer-Centric Frontend
A presentation layer for first-pass audience experience reflection.
"""

import streamlit as st
import sys
import os

# Ensure we can import the locked pipeline
sys.path.append(os.getcwd())
from scriptpulse import runner

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ScriptPulse vNext.4",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM STYLING (Non-Streamlit-default, Research-Grade)
# =============================================================================

st.markdown("""
<style>
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Calm, writer-friendly typography */
    .main {
        background-color: #fafafa;
    }
    
    h1 {
        font-family: 'Georgia', serif;
        color: #2c3e50;
        font-weight: 400;
        margin-bottom: 0.5em;
    }
    
    h2 {
        font-family: 'Georgia', serif;
        color: #34495e;
        font-weight: 400;
        font-size: 1.4em;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    
    p, li {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.05em;
        line-height: 1.7;
        color: #444;
    }
    
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 0.95em;
        line-height: 1.5;
    }
    
    /* Reflection boxes */
    .reflection-box {
        background-color: #f9f9f9;
        border-left: 3px solid #95a5a6;
        padding: 1.2em;
        margin: 1em 0;
        border-radius: 4px;
    }
    
    .silence-box {
        background-color: #ecf0f1;
        border-left: 3px solid #7f8c8d;
        padding: 1.2em;
        margin: 1em 0;
        border-radius: 4px;
    }
    
    .disclaimer {
        font-size: 0.9em;
        color: #7f8c8d;
        font-style: italic;
        margin-top: 2em;
        padding: 1em;
        background-color: #ecf0f1;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER & SCOPE DISCLAIMER
# =============================================================================

st.title("ScriptPulse vNext.4")
st.markdown("*A reflective instrument for first-pass audience cognitive experience*")

st.markdown("""
---
**What this tool does:**  
ScriptPulse models the attentional demands and recovery patterns that a first-time viewer 
might experience when encountering your screenplay. It reflects observations back to you 
as questions, not judgments.

**What this tool does NOT do:**  
This is not a quality evaluator. It does not recommend changes, rank scripts, or predict success.
""")

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown("---")
st.header("Your Script")

script_input = st.text_area(
    label="Paste your screenplay draft here",
    height=300,
    placeholder="Paste your current draft here — formatting does not need to be clean.\n\nINT. COFFEE SHOP - DAY\n\nJOHN sits alone...",
    help="The system handles messy drafts, placeholders, and experimental formatting."
)

# Intent Input (Optional)
st.markdown("### Writer Intent (Optional)")
st.markdown("""
If you have deliberately designed certain sections to create specific effects, you can declare your intent here. 
This will suppress alerts that align with your stated goals.

**Allowed intent labels only:**
- `intentionally exhausting`
- `intentionally confusing`
- `experimental structure`
- `intentionally minimal`
- `intentionally dense`
""")

intent_declared = st.checkbox("I want to declare intent for specific scenes")

writer_intent = None
if intent_declared:
    col1, col2, col3 = st.columns(3)
    with col1:
        intent_start = st.number_input("Start Scene", min_value=0, value=0, step=1)
    with col2:
        intent_end = st.number_input("End Scene", min_value=0, value=5, step=1)
    with col3:
        intent_label = st.selectbox(
            "Intent Label",
            ["intentionally exhausting", "intentionally confusing", "experimental structure", 
             "intentionally minimal", "intentionally dense"]
        )
    
    if intent_start is not None and intent_end is not None and intent_label:
        writer_intent = [{'scene_range': [intent_start, intent_end], 'intent': intent_label}]

# =============================================================================
# ANALYSIS EXECUTION
# =============================================================================

if st.button("Reflect", type="primary"):
    if not script_input or script_input.strip() == "":
        st.warning("Please paste a script to analyze.")
    else:
        with st.spinner("Processing..."):
            try:
                # Run the locked pipeline (no new logic)
                report = runner.run_pipeline(script_input, writer_intent=writer_intent)
                
                # Extract results
                reflections = report.get('reflections', [])
                silence = report.get('silence_explanation')
                intent_acks = report.get('intent_acknowledgments', [])
                
                st.markdown("---")
                st.header("Possible First-Time Audience Experience")
                
                # Display Intent Acknowledgments (if any)
                if intent_acks:
                    st.markdown("### Intent Alignment")
                    for ack in intent_acks:
                        st.markdown(f"<div class='reflection-box'>{ack}</div>", unsafe_allow_html=True)
                
                # Display Reflections (if any)
                if reflections:
                    st.markdown("### Reflections")
                    for ref in reflections:
                        scene_range = ref.get('scene_range', [0, 0])
                        reflection_text = ref.get('reflection', '')
                        confidence = ref.get('confidence', 'low')
                        
                        scene_label = f"Scenes {scene_range[0]}–{scene_range[1]}" if scene_range[0] != scene_range[1] else f"Scene {scene_range[0]}"
                        
                        st.markdown(f"**{scene_label}** *(confidence: {confidence})*")
                        st.markdown(f"<div class='reflection-box'>{reflection_text}</div>", unsafe_allow_html=True)
                
                # Display Silence Explanation (if no reflections)
                elif silence:
                    st.markdown("### Why you may be seeing silence")
                    st.markdown(f"<div class='silence-box'>{silence}</div>", unsafe_allow_html=True)
                
                else:
                    # This should not happen, but handle gracefully
                    st.markdown("### System Response")
                    st.markdown("<div class='silence-box'>No patterns detected. This does not indicate quality.</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                st.info("Please check that your script is readable text and try again.")

# =============================================================================
# FOOTER DISCLAIMERS (Mandatory)
# =============================================================================

st.markdown("""
<div class='disclaimer'>
<strong>Mandatory Disclosures:</strong><br>
• This is not a quality score.<br>
• This is not a ranking or approval system.<br>
• This tool does not recommend changes.<br>
• Outputs describe first-pass audience experience only.<br>
• Writer intent always overrides system observations.
</div>
""", unsafe_allow_html=True)
