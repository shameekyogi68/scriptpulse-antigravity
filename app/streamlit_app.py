#!/usr/bin/env python3
"""
ScriptPulse v6.0 - Main Entry Point
Modularized Architecture
"""

import streamlit as st
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ScriptPulse V6.0 — Engine",
    page_icon="🎬",
    layout="wide"
)

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Import Modular Components
from app.components.styles import apply_custom_styles
from app.components.sidebar import render_sidebar
from app.components.diagnostics import render_diagnostics
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
apply_custom_styles()
stu.sync_safety_state()

if 'last_report' not in st.session_state:
    st.session_state['last_report'] = None
if 'prev_run' not in st.session_state:
    st.session_state['prev_run'] = None

# =============================================================================
# SIDEBAR & CONFIG
# =============================================================================
IS_CLOUD = True # Standard for cloud deployment
sidebar_state = render_sidebar(
    ui_mode=st.session_state.get('ui_mode', "Writer Mode (Creative)"),
    is_cloud=IS_CLOUD,
    stu=stu
)

# Update session state from sidebar
st.session_state['ui_mode'] = sidebar_state['ui_mode']

# =============================================================================
# MAIN CONTENT AREA
# =============================================================================
st.title("The Instrument")
st.markdown("*A visual interface for screenplay rhythm.*")

# 1. Load Draft
st.header("1. Load Draft")
tab_up, tab_paste = st.tabs(["Upload Document", "Paste Text"])

script_input = None
with tab_up:
    uploaded_file = st.file_uploader("Upload Screenplay (PDF/TXT/FDX)", type=['pdf', 'txt', 'fdx'])
    if uploaded_file:
        if stu.check_upload_size(uploaded_file):
            with st.spinner("Reading file..."):
                file_ext = uploaded_file.name.split('.')[-1].lower()
                if file_ext == 'pdf':
                    try:
                        import PyPDF2
                        from io import BytesIO
                        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                        script_input = "\n".join([p.extract_text() for p in pdf_reader.pages])
                    except Exception as e:
                        st.error(f"PDF Error: {e}")
                elif file_ext == 'fdx':
                    try:
                        from scriptpulse.agents import importers
                        script_input = importers.run(uploaded_file.getvalue().decode("utf-8"))
                        if isinstance(script_input, list): # Reconstruct if pre-parsed
                             script_input = "\n".join([l['text'] for l in script_input])
                    except Exception as e:
                        st.error(f"FDX Error: {e}")
                else:
                    script_input = uploaded_file.read().decode('utf-8')

with tab_paste:
    pasted_text = st.text_area("Paste text here", height=200)
    if not script_input and len(pasted_text) > 100:
        script_input = pasted_text

# 2. Configuration
st.header("2. Analysis Configuration")
with st.expander("Target Genre & Context", expanded=False):
    col1, col2 = st.columns(2)
    selected_genre = col1.selectbox("Target Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi"])
    selected_lens = col2.selectbox("Analysis Lens", ["viewer", "reader", "narrator"])

# 3. Execution
if script_input:
    if st.button("Analyze Rhythm", type="primary"):
        with st.spinner("Processing story architecture..."):
            try:
                report = runner.run_pipeline(
                    script_input,
                    genre=selected_genre,
                    lens=selected_lens,
                    ablation_config=sidebar_state['ablation_config'],
                    cpu_safe_mode=sidebar_state['force_cloud']
                )
                st.session_state['last_report'] = report
                st.session_state['current_input'] = script_input # For view rendering
            except Exception as e:
                import traceback; st.error(f"Analysis Failed: {traceback.format_exc()}")

# 4. Render Views
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')

if report and current_input:
    if st.session_state['ui_mode'] == "Writer Mode (Creative)":
        render_writer_view(report, current_input)
    else:
        render_lab_view(report, current_input, selected_genre, selected_lens, sidebar_state['ablation_config'], True)

# 5. Export Output
if report and current_input:
    st.markdown("---")
    st.header("3. Extract Intelligence")
    st.markdown("*Download professional exports of this analysis session.*")
    
    col_w, col_s, col_p = st.columns(3)
    
    with col_w:
        md_report = writer_report.generate_writer_report(report, title=uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script", genre=selected_genre)
        st.download_button(
            label="📄 Writer's Intelligence (MD)",
            data=md_report,
            file_name=f"ScriptPulse_Writer_{selected_genre}.md",
            mime="text/markdown",
            help="High-depth analytical report for the writer."
        )
        
    with col_s:
        html_report = studio_report.generate_report(report, script_title=uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script")
        st.download_button(
            label="🎬 Studio Coverage (HTML)",
            data=html_report,
            file_name=f"ScriptPulse_Studio_{selected_genre}.html",
            mime="text/html",
            help="Professional studio-style coverage report."
        )

    with col_p:
        print_html = print_summary.generate_print_summary(report, script_title=uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script")
        st.download_button(
            label="🖨️ Quick Summary (HTML)",
            data=print_html,
            file_name=f"ScriptPulse_Summary_{selected_genre}.html",
            mime="text/html",
            help="One-page summary for physical printing."
        )

# 6. Diagnostics
st.markdown("---")
render_diagnostics()
