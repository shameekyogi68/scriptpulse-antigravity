#!/usr/bin/env python3
"""
ScriptPulse v7.0 - Main Entry Point
Writer-First Design — Industry Standard Interface
"""

import streamlit as st
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ScriptPulse — Screenplay Intelligence",
    page_icon="/Users/shameekyogi/Desktop/scriptpulse-antigravity/ScriptPulse_Icon.png",
    layout="wide"
)

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Import Modular Components
from app.components.styles import apply_custom_styles
from app.components.theme import init_plotly_template
from app.components.sidebar import render_sidebar
from app.components.uikit import render_hero_section, render_section_header
from app.views.writer_view import render_writer_view
from app.views.lab_view import render_lab_view

# Import Core Pipeline
try:
    from scriptpulse.pipeline import runner
except Exception as e:
    st.error(f"Failed to load ScriptPulse Engine: {e}")
    st.stop()

# Import Utils
import app.streamlit_utils as stu
from scriptpulse.reporters import writer_report, studio_report, print_summary

# =============================================================================
# INITIALIZATION
# =============================================================================
@st.cache_resource
def init_application():
    """Application-level initialization logic."""
    apply_custom_styles()
    init_plotly_template()
    return True

init_application()
stu.sync_safety_state()

if 'last_report' not in st.session_state: st.session_state['last_report'] = None

# =============================================================================
# SIDEBAR & CONFIG
# =============================================================================
sidebar_state = render_sidebar(
    ui_mode=st.session_state.get('ui_mode', "Writer Mode (Creative)"),
    is_cloud=True,
    stu=stu
)
st.session_state['ui_mode'] = sidebar_state['ui_mode']

# =============================================================================
# HERO SECTION
# =============================================================================
render_hero_section("ScriptPulse", "Understand how your screenplay feels to a first-time reader — scene by scene.")

# =============================================================================
# STEP 1: LOAD DRAFT
# =============================================================================
render_section_header("📄", "Load Your Draft", 
                      "Upload your screenplay file or paste text directly. ScriptPulse reads your script and analyzes its structure.")

tab_up, tab_paste = st.tabs(["📁 Upload File", "📝 Paste Text"])

script_input = None
with tab_up:
    uploaded_file = st.file_uploader("Drop your screenplay here (PDF, TXT, or FDX)", type=['pdf', 'txt', 'fdx'])
    if uploaded_file and stu.check_upload_size(uploaded_file):
        with st.spinner("Reading script..."):
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext == 'pdf':
                from io import BytesIO
                import PyPDF2
                script_input = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(BytesIO(uploaded_file.read())).pages])
            elif ext == 'fdx':
                from scriptpulse.agents import importers
                script_input = importers.run(uploaded_file.getvalue().decode("utf-8"))
                if isinstance(script_input, list): script_input = "\n".join([l['text'] for l in script_input])
            else:
                script_input = uploaded_file.read().decode('utf-8')

with tab_paste:
    pasted = st.text_area("Paste text here", height=200, placeholder="INT. COFFEE SHOP - DAY...")
    if not script_input and len(pasted) > 100: script_input = pasted

# =============================================================================
# STEP 2: CONFIGURE & RUN
# =============================================================================
render_section_header("⚙️", "Analysis Settings", "Calibrate feedback based on genre conventions.")
col1, col2 = st.columns(2)
genre = col1.selectbox("Target Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Avant-Garde"])
lens = col2.selectbox("Reading Perspective", ["viewer", "reader", "narrator"])

if script_input:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🎬 Analyze My Script", type="primary", use_container_width=True):
        bar = st.progress(0, text="Stoking engine...")
        try:
            report = runner.run_pipeline(script_input, genre=genre, lens=lens, 
                                        ablation_config=sidebar_state['ablation_config'],
                                        cpu_safe_mode=sidebar_state['force_cloud'])
            st.session_state['last_report'] = report
            st.session_state['current_input'] = script_input
            st.session_state['current_genre'] = genre
            bar.progress(100, text="Complete!")
            time.sleep(0.5)
            bar.empty()
        except Exception as e:
            bar.empty()
            st.error(f"Analysis failed: {e}")
else: st.info("👆 Upload or paste or screenplay above to begin.")

# =============================================================================
# STEP 3: RENDER RESULTS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')

if report and current_input:
    st.markdown("---")
    # Render unified dashboard: Writer insights first, followed by Lab telemetry
    render_writer_view(report, current_input)
    
    st.markdown("---")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Render the Advanced Telemetry (formerly Lab View) at the bottom
    render_lab_view(report, current_input, genre, lens, sidebar_state['ablation_config'], True)

# =============================================================================
# STEP 4: EXPORT
# =============================================================================
if report and current_input:
    st.markdown("---")
    render_section_header("📥", "Export Your Analysis", "Download professional reports for shared use.")
    c1, c2, c3 = st.columns(3)
    title = uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script"
    
    with c1: st.download_button("📄 Writer Report (MD)", writer_report.generate_writer_report(report, title=title, genre=genre), f"ScriptPulse_Writer_{genre}.md", "text/markdown", use_container_width=True)
    with c2: st.download_button("🎬 Studio Coverage (HTML)", studio_report.generate_report(report, script_title=title), f"ScriptPulse_Studio_{genre}.html", "text/html", use_container_width=True)
    with c3: st.download_button("🖨️ One-Page Summary (HTML)", print_summary.generate_print_summary(report, script_title=title), f"ScriptPulse_Summary_{genre}.html", "text/html", use_container_width=True)

# Diagnostics
st.markdown("---")
from app.components.diagnostics import render_diagnostics
render_diagnostics()
