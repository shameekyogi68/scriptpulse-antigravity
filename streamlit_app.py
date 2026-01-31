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
    page_title="ScriptPulse vNext.5",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# MINIMAL STYLING & PROFESSIONAL THEME
# =============================================================================

st.markdown("""
<style>
    /* Only remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Experiential Box Styling */
    .reflection-box {
        padding: 15px;
        border-left: 4px solid #FF4B4B;
        background-color: #f0f2f6;
        border-radius: 4px;
        margin-bottom: 15px;
        font-style: italic;
        color: #000000; /* Force Black Text for Contrast */
    }
    
    /* Earned Silence / Stability Styling (Green/Calm) */
    .stability-box {
        padding: 20px;
        border-left: 4px solid #00CC66;
        background-color: #e8f5e9;
        border-radius: 4px;
        margin-bottom: 15px;
        color: #0d3b0d; /* Dark Green Text */
    }
    
    .silence-box {
        padding: 15px;
        border-left: 4px solid #888;
        background-color: #f9f9f9;
        border-radius: 4px;
        color: #333333; /* Dark Grey Text */
    }
    
    .disclaimer {
        font-size: 0.8em;
        color: #666;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ONBOARDING & PHILOSOPHY SIDEBAR
# =============================================================================

with st.sidebar:
    st.title("Orientation")
    st.info(
        "**ScriptPulse is a Reader Surrogate.**\n\n"
        "It models first-pass attention. "
        "It does not judge quality, marketability, or structure.\n\n"
        "If it stays silent, that is a positive signal of stability."
    )
    
    st.markdown("---")
    st.markdown("### System Limits")
    st.caption("❌ No grading or scoring")
    st.caption("❌ No comparative ranking")
    st.caption("❌ No 'bad writing' detection")
    
    st.markdown("---")
    st.markdown("### How to Read This")
    st.markdown(
        "**If Patterns Surface:**\n"
        "Ask yourself: *Did I intend for the audience to feel this strain here?*\n\n"
        "**If Silence Surfaces:**\n"
        "This means the experience is stable. You don't need to 'fix' anything."
    )

# =============================================================================
# HEADER & SCOPE DISCLAIMER
# =============================================================================

st.title("ScriptPulse")
st.markdown("*A quiet companion for thinking about how your screenplay might feel to watch*")

st.markdown("""
---
**How this works:**  
ScriptPulse reads your draft and considers how a **first-time viewer** might experience 
its rhythm and flow. It reflects those observations back to you as questions—never as judgments.

**What this is not:**  
This is not a score, a grade, or a ranking. It does not tell you what to change. 
It simply offers a mirror for one possible reading of your work.
""")

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown("---")
st.header("Your Draft")

# File upload option
uploaded_file = st.file_uploader(
    "Upload a screenplay file (optional)",
    type=['txt', 'pdf'],
    help="Supports .txt and .pdf files. For large scripts (150+ pages), upload is recommended."
)

script_input = None

if uploaded_file is not None:
    try:
        if uploaded_file.type == "application/pdf":
            # Parse PDF
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            script_input = "\n".join(text_parts)
            st.success(f"✓ Loaded {len(pdf_reader.pages)} pages from PDF")
        else:
            # Read text file
            script_input = uploaded_file.read().decode('utf-8')
            st.success("✓ File loaded successfully")
    except Exception as e:
        st.error(f"Could not read file: {e}")
        script_input = None

# Text area for pasting (only show if no file uploaded)
if script_input is None:
    script_input = st.text_area(
        label="Or paste your screenplay here",
        height=300,
        placeholder="Paste your draft here. Formatting does not need to be clean.\n\nINT. COFFEE SHOP - DAY\n\nJOHN sits alone...",
        help="Messy drafts, placeholders, and experimental formatting are all fine."
    )
else:
    # Show preview of uploaded content
    with st.expander("Preview uploaded script"):
        st.text(script_input[:1000] + ("..." if len(script_input) > 1000 else ""))

# Intent Input (Optional)
st.markdown("### Your Intent (Optional)")
st.markdown("""
If you have deliberately designed certain sections to create a particular effect, 
you can tell us here. When your intent aligns with what we observe, we stay quiet.

**Recognized intent labels:**
- `intentionally exhausting`
- `intentionally confusing`
- `experimental structure`
- `intentionally minimal`
- `intentionally dense`
""")

intent_declared = st.checkbox("I want to share my intent for specific scenes")

writer_intent = None
if intent_declared:
    st.markdown("*Only the labels listed above are recognized. If your intent doesn't fit these categories, you can leave this blank.*")
    
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
# MISUSE DETECTION & EDGE-CASE HANDLING
# =============================================================================

def detect_evaluative_language(text):
    """Detect if input contains evaluative questions."""
    text_lower = text.lower().strip()
    
    evaluative_patterns = [
        "is this good", "is this bad", "is it good", "is it bad",
        "does this work", "will this work", "which part works",
        "will this get made", "will this sell", "is this marketable",
        "should i", "what's wrong", "what is wrong"
    ]
    
    for pattern in evaluative_patterns:
        if pattern in text_lower:
            return True
    return False

def detect_fix_prompts(text):
    """Detect if input asks for prescriptive advice."""
    text_lower = text.lower().strip()
    
    fix_patterns = [
        "how do i fix", "how can i fix", "how to fix",
        "what should i change", "how to improve", "how can i improve",
        "what needs to change", "how do i make it better"
    ]
    
    for pattern in fix_patterns:
        if pattern in text_lower:
            return True
    return False

def is_sufficient_input(text):
    """Check if input has enough content to analyze."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Need at least 5 non-empty lines to have meaningful structure
    if len(lines) < 5:
        return False
    
    # Need at least 100 characters total
    if len(text.strip()) < 100:
        return False
    
    return True

# =============================================================================
# ANALYSIS EXECUTION
# =============================================================================

if st.button("Read My Draft", type="primary"):
    if not script_input or script_input.strip() == "":
        st.info("Please paste your screenplay above.")
    
    # Edge Case 1: Evaluative Questions
    elif detect_evaluative_language(script_input):
        st.markdown("---")
        st.info("**This tool doesn't evaluate or predict outcomes.** It reflects possible audience experience instead. If you'd like to paste your screenplay, I can share observations about how it might feel to watch.")
    
    # Edge Case 2: "Fix This" Prompts
    elif detect_fix_prompts(script_input):
        st.markdown("---")
        st.info("**I can't suggest changes or improvements.** But if you paste your screenplay, I can reflect how it might feel to a first-time audience. You decide what, if anything, to do with that.")
    
    # Edge Case 3: Insufficient Input
    elif not is_sufficient_input(script_input):
        st.markdown("---")
        st.info("**There may not be enough material here yet.** Experiential patterns tend to emerge across multiple scenes. Feel free to paste more when you have it.")
    
    else:
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Stage 1: Parsing
            status_text.text("📖 Parsing screenplay structure...")
            progress_bar.progress(15)
            
            # Stage 2-7: Pipeline execution
            status_text.text("🔄 Running analysis pipeline...")
            progress_bar.progress(30)
            
            # Run the locked pipeline (no new logic)
            import time
            start_time = time.time()
            
            report = runner.run_pipeline(script_input, writer_intent=writer_intent)
            
            elapsed = time.time() - start_time
            
            # Check if we're approaching timeout (55 seconds on free tier)
            if elapsed > 50:
                st.warning("⏱️ Large script detected. Processing took longer than usual but completed successfully.")
            
            progress_bar.progress(100)
            status_text.text("✓ Analysis complete")
            
            # Clear progress indicators
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Extract results
            reflections = report.get('reflections', [])
            silence = report.get('silence_explanation')
            intent_acks = report.get('intent_acknowledgments', [])
            ssf_analysis = report.get('ssf_analysis', {})
            
            st.markdown("---")
            st.header("Audience Experience Reflection")
            
            # Display Intent Acknowledgments (if any)
            if intent_acks:
                st.markdown("### Where Your Intent Was Recognized")
                for ack in intent_acks:
                    st.markdown(f"<div class='reflection-box'>{ack}</div>", unsafe_allow_html=True)
            
            # Display Reflections (if any)
            if reflections:
                st.markdown("### Observations of Strain")
                st.markdown("These moments stood out as potentially demanding for a first-pass viewer.")
                
                # Get scene info for display
                scene_info = report.get('scene_info', [])
                total_scenes = report.get('total_scenes', 0)
                
                # Show total scene count if available
                if total_scenes > 0:
                    st.caption(f"📊 Analyzed {total_scenes} scenes")
                
                for ref in reflections:
                    scene_range = ref.get('scene_range', [0, 0])
                    reflection_text = ref.get('reflection', '')
                    confidence = ref.get('confidence', 'low')
                    
                    scene_label = f"Scenes {scene_range[0]}–{scene_range[1]}" if scene_range[0] != scene_range[1] else f"Scene {scene_range[0]}"
                    
                    # Get scene headings for this range
                    scene_headings = []
                    for s in scene_info:
                        if scene_range[0] <= s['scene_index'] <= scene_range[1]:
                            if s.get('heading'):
                                scene_headings.append(f"• {s['heading']}")
                    
                    st.markdown(f"**{scene_label}**")
                    
                    # Show scene headings in an expander
                    if scene_headings:
                        with st.expander("🎬 View scenes in this range"):
                            for heading in scene_headings[:5]:  # Limit to first 5
                                st.text(heading)
                            if len(scene_headings) > 5:
                                st.caption(f"...and {len(scene_headings) - 5} more scenes")
                    
                    st.markdown(f"<div class='reflection-box'>{reflection_text}</div>", unsafe_allow_html=True)
            
            # Display Silence / Stability (if no reflections) 
            elif silence:
                # Check for "Earned Silence" via SSF
                if ssf_analysis.get('is_silent'):
                    if ssf_analysis.get('explanation_key') == 'stable_continuity':
                         st.markdown("### ✅ Experience Stable")
                         st.markdown(f"<div class='stability-box'><strong>High Stability Detected.</strong><br>{silence}</div>", unsafe_allow_html=True)
                    elif ssf_analysis.get('explanation_key') == 'stable_but_drifting':
                         st.markdown("### ⚠️ Stable but Low Variance")
                         st.markdown(f"<div class='silence-box'>{silence}</div>", unsafe_allow_html=True)
                    else:
                         st.markdown("### Stability Observed")
                         st.markdown(f"<div class='stability-box'>{silence}</div>", unsafe_allow_html=True)
                else:
                    # Fallback for generic silence (low confidence)
                    st.markdown("### Why You May Be Seeing Nothing Here")
                    st.markdown(f"<div class='silence-box'>{silence}</div>", unsafe_allow_html=True)
            
            else:
                # This should not happen, but handle gracefully
                st.markdown("### A Quiet Reading")
                st.markdown("<div class='silence-box'>No strong experiential patterns surfaced. This happens when the rhythm is stable, the structure is highly variable, or signals align with your intent. It does not mean anything about quality.</div>", unsafe_allow_html=True)
            
        except Exception as e:
            # Edge Case 5: Technical Errors (hide stack traces)
            progress_bar.empty()
            status_text.empty()
            
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "time" in error_msg.lower():
                st.error("⏱️ **Processing timeout detected.**")
                st.markdown("""
                Your script may be too large for Streamlit Cloud's free tier (60-second limit).
                
                **Options:**
                - Try a shorter section of your script
                - Split into multiple parts
                - Contact support for processing assistance
                """)
            else:
                st.warning("Something went wrong while reading your draft.")
                st.markdown("This can happen with very unusual formatting. If the problem persists, the draft may need to be in a more standard text format.")

# =============================================================================
# FOOTER DISCLAIMERS (Mandatory)
# =============================================================================

st.markdown("""
<div class='disclaimer'>
<strong>Please remember:</strong><br>
• This is not a score or a grade.<br>
• This does not rank or approve scripts.<br>
• This does not tell you what to change.<br>
• These are observations about one possible reading—nothing more.<br>
• Your intent, stated or unstated, is always authoritative.
</div>
""", unsafe_allow_html=True)
