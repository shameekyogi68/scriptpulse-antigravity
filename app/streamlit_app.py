#!/usr/bin/env python3
"""
ScriptPulse — AI Story Intelligence
Product-Grade Entry Point
"""

import streamlit as st
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Path to persistent brand assets
ICON_PATH = os.path.join(ROOT_DIR, "app", "assets", "ScriptPulse_Icon.png")

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ScriptPulse — AI Story Intelligence",
    page_icon=ICON_PATH if os.path.exists(ICON_PATH) else "app/assets/ScriptPulse_Icon.png",
    layout="wide"
)

# Import Modular Components
from app.components.styles import apply_custom_styles
from app.components.theme import init_plotly_template
from app.components.sidebar import render_sidebar
from app.components.uikit import render_hero_section, render_section_header
from app.views.writer_view import render_writer_view

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
    apply_custom_styles()
    init_plotly_template()
    return True

init_application()
stu.sync_safety_state()

if 'last_report' not in st.session_state:
    st.session_state['last_report'] = None

# =============================================================================
# SIDEBAR
# =============================================================================
sidebar_state = render_sidebar(
    ui_mode=st.session_state.get('ui_mode', "Unified"),
    is_cloud=True,
    stu=stu
)
st.session_state['ui_mode'] = sidebar_state['ui_mode']

# =============================================================================
# HERO
# =============================================================================
render_hero_section(
    "ScriptPulse",
    "AI Story Intelligence — See how your screenplay feels to an audience before you ever hit send."
)

# =============================================================================
# STEP 1: UPLOAD
# =============================================================================
render_section_header("📄", "Your Screenplay",
    "Upload your script or paste a scene. We'll map its emotional architecture.")

tab_up, tab_paste = st.tabs(["📁 Upload File", "📝 Paste Text"])

script_input = None
with tab_up:
    uploaded_file = st.file_uploader(
        "Drop your screenplay here (PDF, TXT, or FDX)",
        type=['pdf', 'txt', 'fdx'],
        label_visibility="visible"
    )
    if uploaded_file and stu.check_upload_size(uploaded_file):
        with st.spinner("Reading script..."):
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext == 'pdf':
                from io import BytesIO
                import PyPDF2
                script_input = "\n".join([
                    p.extract_text() for p in PyPDF2.PdfReader(BytesIO(uploaded_file.read())).pages
                ])
            elif ext == 'fdx':
                from scriptpulse.agents import importers
                script_input = importers.run(uploaded_file.getvalue().decode("utf-8"))
                if isinstance(script_input, list):
                    script_input = "\n".join([l['text'] for l in script_input])
            else:
                script_input = uploaded_file.read().decode('utf-8')

with tab_paste:
    pasted = st.text_area("Paste text here", height=200,
                          placeholder="INT. COFFEE SHOP - DAY\n\nA young WRITER stares at a blank screen...")
    if not script_input and len(pasted) > 100:
        script_input = pasted

# =============================================================================
# STEP 2: CONFIGURE & ANALYZE
# =============================================================================
render_section_header("⚙️", "Configure Analysis",
    "Select the genre so the engine knows what benchmarks to apply.")

col1, col2 = st.columns(2)
genre = col1.selectbox("Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"],
                      help="The engine adjusts its benchmarks to match the expectations of your genre.")
lens = col2.selectbox("Perspective", ["Story Editor", "Studio Executive", "Script Coordinator"],
                      help="🕵️ Story Editor = Plot & Logic | 🏢 Studio Executive = Market & Budget | ✍️ Script Coordinator = Craft & Flow")

if script_input:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🎬 Analyze My Script", type="primary", use_container_width=True):
        bar = st.progress(0, text="Initializing engine...")
        try:
            bar.progress(20, text="Parsing screenplay structure...")
            report = runner.run_pipeline(
                script_input, genre=genre, lens=lens,
                ablation_config=sidebar_state['ablation_config'],
                cpu_safe_mode=sidebar_state['force_cloud']
            )
            bar.progress(70, text="Generating intelligence report...")

            st.session_state['last_report'] = report
            st.session_state['current_input'] = script_input
            st.session_state['current_genre'] = genre
            st.session_state['current_lens'] = lens
            st.session_state.pop('ai_summary_cache', None)
            # Clear all lens-specific caches so fresh analysis is generated
            for k in list(st.session_state.keys()):
                if k.startswith('ai_summary_') or k.startswith('ai_pulse_'):
                    del st.session_state[k]

            # Auto-generate AI pulse insight for the selected lens
            try:
                from scriptpulse.reporters.llm_translator import generate_section_insight
                st.session_state['ai_pulse_insight'] = generate_section_insight(report, 'pulse', lens=lens)
            except Exception:
                st.session_state['ai_pulse_insight'] = None

            bar.progress(100, text="Analysis complete!")
            time.sleep(0.5)
            bar.empty()
        except Exception as e:
            bar.empty()
            st.error(f"Analysis failed: {e}")
else:
    st.info("👆 Upload or paste your screenplay above to begin.")

# =============================================================================
# STEP 3: RENDER RESULTS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')
current_genre = st.session_state.get('current_genre', 'Drama')

if report and current_input:
    st.markdown("---")
    # Render unified dashboard: Writer insights first, followed by Producer telemetry
    render_writer_view(report, current_input, current_genre, lens=lens)

# =============================================================================
# STEP 4: EXPORT
# =============================================================================
if report and current_input:
    st.markdown("---")
    render_section_header("📥", "Export Reports",
        "Download professional reports to share with collaborators, agents, or studio executives.")

    c1, c2, c3 = st.columns(3)
    title = uploaded_file.name if 'uploaded_file' in locals() and uploaded_file else "Script"

    with c1:
        st.download_button("📄 Writer Report", 
            writer_report.generate_writer_report(report, title=title, genre=genre),
            f"ScriptPulse_Writer_{genre}.md", "text/markdown",
            use_container_width=True)
    with c2:
        st.download_button("🎬 Studio Coverage",
            studio_report.generate_report(report, script_title=title, lens=lens),
            f"ScriptPulse_Studio_{genre}.html", "text/html",
            use_container_width=True)
    with c3:
        st.download_button("🖨️ One-Page Summary",
            print_summary.generate_print_summary(report, script_title=title),
            f"ScriptPulse_Summary_{genre}.html", "text/html",
            use_container_width=True)

# =============================================================================
# SYSTEM DIAGNOSTICS (Hidden)
# =============================================================================
st.markdown("---")
from app.components.diagnostics import render_diagnostics
render_diagnostics()
