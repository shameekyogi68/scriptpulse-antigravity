# MODULE: streamlit_app.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#!/usr/bin/env python3
"""
ScriptPulse — AI Story Intelligence
Product-Grade Entry Point
"""

import streamlit as st
import sys
import os
import time
import textwrap
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
import app.components.charts as charts
import app.views.writer_view as writer_view
import app.components.styles as styles
import importlib
importlib.reload(charts)
importlib.reload(writer_view)
importlib.reload(styles)

from app.components.styles import apply_custom_styles
from app.components.theme import init_plotly_template
from app.components.uikit import render_hero_section, render_section_header, clean_html
from app.views.writer_view import render_writer_view

# Import Core Pipeline
try:
    from scriptpulse.pipeline import runner
    from scriptpulse.governance import PolicyViolationError
except Exception as e:
    st.error(f"Failed to load ScriptPulse Engine: {e}")
    st.stop()

# Import Utils
import app.streamlit_utils as stu
import importlib
importlib.reload(stu)
from scriptpulse.reporters import writer_report, studio_report, print_summary

# =============================================================================
# INITIALIZATION
# =============================================================================
APP_BUILD = "v1.0-release"

def init_application():
    apply_custom_styles()
    init_plotly_template()
    return True

init_application()
stu.sync_safety_state()

if 'last_report' not in st.session_state:
    st.session_state['last_report'] = None

# =============================================================================
# CONFIGURATION STATE
# =============================================================================
sidebar_state = {
    'ui_mode': "Unified",
    'force_cloud': True,
    'ablation_config': {
        'use_sbert': True,
        'use_multimodal': False
    },
    'shadow_mode': False,
    'high_accuracy_mode': True
}
st.session_state['ui_mode'] = "Unified"

# =============================================================================
# PERSISTENT VARIABLES & STATE CHECKS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')
is_analyzing = st.session_state.get('is_analyzing', False)

# Decide whether to show the setup section (Hero section + file uploader + config)
show_setup = (report is None) and (not is_analyzing)

if 'current_genre' not in st.session_state:
    st.session_state['current_genre'] = 'drama'
if 'current_lens' not in st.session_state:
    st.session_state['current_lens'] = 'Story Editor'

genre = st.session_state['current_genre']
lens = st.session_state['current_lens']
script_input = st.session_state.get('parsed_file_content')

# =============================================================================
# HERO & SETUP (Only visible when starting from scratch)
# =============================================================================
render_hero_section(
    "ScriptPulse",
    "AI Story Intelligence — Map how your screenplay may feel to a first-time reader. Reference signals for reflection, not judgment."
)

if show_setup:
    # Create two columns for the setup stage: Left for Screenplay, Right for Configuration & Run
    col_setup_left, col_setup_right = st.columns([1.1, 0.9], gap="medium")

    with col_setup_left:
        with st.container(border=True):
            st.markdown(clean_html("""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <i class="ti ti-file-text" style="font-size: 1.75rem; color: var(--amethyst);"></i>
                <h3 style="margin: 0 !important; font-size: 1.25rem !important; font-weight: 700; color: white; letter-spacing: -0.02em;">Your Screenplay</h3>
            </div>
            """), unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Drop your screenplay here (PDF, TXT, or FDX)",
                type=['pdf', 'txt', 'fdx'],
                label_visibility="collapsed"
            )
            if uploaded_file:
                # Inject CSS to hide dropzone elements when file is uploaded
                st.markdown("""
                <style>
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::before,
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::after,
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]::before,
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]::after {
                    display: none !important;
                }
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button,
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] button {
                    display: none !important;
                }
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneInstructions"],
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] [data-testid="stFileUploaderDropzoneInstructions"] {
                    display: none !important;
                }
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"],
                div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] {
                    padding: 12px 16px !important;
                    border: none !important;
                    background: transparent !important;
                    box-shadow: none !important;
                    height: auto !important;
                    min-height: unset !important;
                }
                </style>
                """, unsafe_allow_html=True)

                if stu.check_upload_size(uploaded_file):
                    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
                    if st.session_state.get('parsed_file_key') == file_key:
                        script_input = st.session_state.get('parsed_file_content')
                    else:
                        with st.spinner("Reading script..."):
                            ext = uploaded_file.name.split('.')[-1].lower()
                            if ext == 'pdf':
                                try:
                                    from io import BytesIO
                                    import PyPDF2
                                    script_input = "\n".join([
                                        p.extract_text() or "" for p in PyPDF2.PdfReader(BytesIO(uploaded_file.read())).pages
                                    ])
                                    # PDF validation: check that extracted text has at least 300 words
                                    if script_input and len(script_input.strip().split()) < 300:
                                        st.error("This PDF appears to be image-based (scanned). Please convert to a text-based PDF or upload a TXT/FDX file instead.")
                                        script_input = None
                                    else:
                                        st.session_state['parsed_file_key'] = file_key
                                        st.session_state['parsed_file_content'] = script_input
                                        st.session_state['last_filename'] = uploaded_file.name
                                except Exception as e:
                                    st.error("Could not read PDF. The file may be corrupted or protected. Please try a TXT or FDX file.")
                                    script_input = None
                            elif ext == 'fdx':
                                try:
                                    from scriptpulse.agents.structure_agent import ImporterAgent
                                    importer = ImporterAgent()
                                    parsed_lines = importer.run(uploaded_file.getvalue().decode("utf-8"))
                                    if isinstance(parsed_lines, list):
                                        script_input = "\n".join([l['text'] for l in parsed_lines])
                                    else:
                                        script_input = parsed_lines
                                    if script_input:
                                        st.session_state['parsed_file_key'] = file_key
                                        st.session_state['parsed_file_content'] = script_input
                                        st.session_state['last_filename'] = uploaded_file.name
                                except Exception as e:
                                    st.error("Could not parse FDX formatting. Please ensure it's a valid Final Draft XML file.")
                                    script_input = None
                            else:
                                try:
                                    script_input = uploaded_file.read().decode('utf-8')
                                    if script_input:
                                        st.session_state['parsed_file_key'] = file_key
                                        st.session_state['parsed_file_content'] = script_input
                                        st.session_state['last_filename'] = uploaded_file.name
                                except Exception:
                                    st.error("Could not decode text. Please ensure the file is saved in standard UTF-8 format.")
                                    script_input = None
            else:
                # User cleared or did not upload yet
                st.session_state.pop('parsed_file_key', None)
                st.session_state.pop('parsed_file_content', None)
                st.session_state.pop('scrolled_to_analyze', None)
                script_input = None

    with col_setup_right:
        with st.container(border=True):
            st.markdown(clean_html("""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <i class="ti ti-settings" style="font-size: 1.75rem; color: var(--amethyst);"></i>
                <h3 style="margin: 0 !important; font-size: 1.25rem !important; font-weight: 700; color: white; letter-spacing: -0.02em;">Configure Analysis</h3>
            </div>
            <div class="well" style="padding: 16px 20px; background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: var(--radius-md); margin-bottom: 24px;">
                <p style="font-size: 0.875rem; color: rgba(219, 234, 254, 0.75); line-height: 1.6; margin: 0;">
                    ScriptPulse provides audience-experience reference signals. It does not rank, approve, or predict commercial success.
                </p>
            </div>
            """), unsafe_allow_html=True)

            genre_raw = st.selectbox("Target Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"],
                                  help="The engine adjusts its benchmarks to match the expectations of your genre.", key="setup_genre")
            genre = genre_raw.lower().replace("-", "-")  # Preserve hyphens, force lowercase
            st.session_state['current_genre'] = genre

            lens = st.selectbox("Analysis Perspective", ["Story Editor", "Studio Executive", "Script Coordinator"],
                                  help="🕵️ Story Editor = Plot & Logic | 🏢 Studio Executive = Market & Budget | ✍️ Script Coordinator = Craft & Flow", key="setup_lens")
            st.session_state['current_lens'] = lens

    if script_input:
        st.markdown("<br/>", unsafe_allow_html=True)
        if not st.session_state.get('scrolled_to_analyze', False):
            st.session_state['scrolled_to_analyze'] = True
            stu.inject_scroll_to('.st-key-analyze_my_script_btn', block='center')
        if st.button("🎬 Analyze My Script", type="primary", use_container_width=True, key="analyze_my_script_btn"):
            st.session_state['is_analyzing'] = True
            st.session_state['last_report'] = None
            st.session_state['current_input'] = None
            st.rerun()

# Run the analysis if the flag is set
# Run the analysis if the flag is set
if st.session_state.get('is_analyzing', False) and script_input:
    loading_placeholder = st.empty()
    
    # Pre-parse screenplay statistics for the interactive loading screen
    try:
        word_count = len(script_input.split())
        line_count = len(script_input.splitlines())
        est_pages = max(1, round(line_count / 55))
        import re
        scene_headings = re.findall(r'^(?:INT\.|EXT\.|INT/EXT\.|EXT/INT\.|I/E\.?)\s+.*', script_input, re.IGNORECASE | re.MULTILINE)
        est_scenes = max(1, len(scene_headings))
    except Exception:
        est_pages = 0
        est_scenes = 0

    try:
        stage_labels = {
            "Parsing structure...": "📐 Parsing screenplay structure...",
            "Extracting features...": "🔬 Extracting narrative features...",
            "Simulating dynamics...": "🧠 Running cognitive simulation...",
            "Running interpretation...": "🎯 Interpreting narrative patterns...",
            "Generating insights...": "✨ Generating writer intelligence...",
        }

        # Terminal diagnostic logs mapped to stages
        diagnostic_messages = [
            (0, "SYSTEM: Initializing ScriptPulse Diagnostics Engine..."),
            (5, "SYSTEM: Loading policy governance firewall rules..."),
            (10, "NORMALIZER: Cleaning control chars and whitespace blocks..."),
            (15, "NORMALIZER: Script structure normalized successfully."),
            (25, "PARSING: Scanning for INT./EXT. scene headings & character dialogue..."),
            (30, "PARSING: Screenplay scene blocks mapped successfully."),
            (35, "SEGMENTER: Sequence segmented. 3-Act structural boundaries active."),
            (45, "PERCEPTION: Encoding scene sentiment valence & dialogue density..."),
            (50, "PERCEPTION: Feature extraction: global dialogue-to-action ratio computed."),
            (55, "DYNAMICS: Simulating first-pass reader attention peaks & recovery rates..."),
            (60, "DYNAMICS: Narrative tension curves and cognitive loads computed."),
            (65, "INTERPRETATION: Mapping turning points and act balance limits..."),
            (70, "INTERPRETATION: Genre calibration: adjusting tension baselines for target."),
            (75, "EXPERT: Compiling writer advice & pacing recommendations..."),
            (80, "EXPERT: Running character voice diversity audit..."),
            (90, "SYSTEM: Confidence scoring active. Assembling multi-persona layouts..."),
            (100, "SYSTEM: Assembly complete. Launching AI Story Intelligence Dashboard.")
        ]
        
        # Initialize or retrieve last progress percentage to prevent jumps
        if 'last_progress_pct' not in st.session_state:
            st.session_state['last_progress_pct'] = 0

        def progress_callback(stage_name, pct):
            label = stage_labels.get(stage_name, f"⚡ {stage_name}")
            start_pct = st.session_state.get('last_progress_pct', 0)
            
            # Reset if percentage goes backward (new run)
            if pct < start_pct:
                start_pct = 0
                
            # Count up smoothly 1% at a time
            for current_pct in range(start_pct, pct + 1):
                # Filter logs up to current percentage
                logs = []
                for log_pct, log_msg in diagnostic_messages:
                    if log_pct <= current_pct:
                        logs.append(f'<div style="margin-bottom: 4px;"><span style="color: rgba(155, 81, 224, 0.65); margin-right: 8px;">[{log_pct}%]</span>{log_msg}</div>')
                
                # Show last 5 logs for scrolling console effect
                recent_logs = logs[-5:]
                logs_html = "".join(recent_logs)
                
                html = f"""
                <div style="text-align: center; padding: 2.5rem 1.5rem; background: rgba(18, 18, 18, 0.85); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border-radius: 24px; border: 1px solid rgba(155, 81, 224, 0.15); box-shadow: 0 20px 48px rgba(0, 0, 0, 0.6), 0 0 30px rgba(155, 81, 224, 0.08); max-width: 500px; margin: 3rem auto; position: relative; overflow: hidden; font-family: 'Inter', sans-serif;">
                    <!-- Ambient glow in background -->
                    <div style="position: absolute; top: -50px; left: 50%; transform: translateX(-50%); width: 220px; height: 100px; background: rgba(155, 81, 224, 0.15); filter: blur(50px); pointer-events: none;"></div>
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, rgba(155, 81, 224, 0.5), transparent);"></div>
                    
                    <!-- Modern Spinner / Pulse -->
                    <div style="display: flex; justify-content: center; margin-top: 10px; margin-bottom: 24px; position: relative; width: 50px; height: 50px; margin-left: auto; margin-right: auto;">
                        <div style="position: absolute; width: 100%; height: 100%; border: 2px solid rgba(155, 81, 224, 0.08); border-radius: 50%;"></div>
                        <div style="position: absolute; width: 100%; height: 100%; border: 2px solid transparent; border-top-color: #9B51E0; border-radius: 50%; animation: spin 1s linear infinite; filter: drop-shadow(0 0 8px rgba(155, 81, 224, 0.4));"></div>
                    </div>
                    
                    <!-- Status & Progress -->
                    <div style="color: #FFFFFF; font-size: 1.25rem; font-weight: 700; margin-bottom: 4px; font-family: 'Outfit', sans-serif; letter-spacing: -0.02em;">{label}</div>
                    <div style="color: rgba(255, 255, 255, 0.65); font-size: 0.85rem; margin-bottom: 16px;">Stage Progress: {current_pct}%</div>
                    
                    <!-- Glow Progress Bar -->
                    <div style="background-color: rgba(255, 255, 255, 0.04); border-radius: 10px; height: 6px; width: 85%; margin: 0 auto; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.01); position: relative;">
                        <div style="background: linear-gradient(90deg, #9B51E0 0%, #FF7043 100%); height: 100%; width: {current_pct}%; transition: width 0.1s ease; box-shadow: 0 0 10px rgba(155, 81, 224, 0.7); border-radius: 10px;"></div>
                    </div>
                    
                    <!-- Screenplay Telemetry Panel -->
                    <div style="display: flex; justify-content: space-around; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 12px 8px; margin: 24px auto 16px auto; width: 85%; text-align: left;">
                        <div style="padding: 0 4px;">
                            <div style="font-size: 0.62rem; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 4px;">Size</div>
                            <div style="font-size: 0.88rem; font-weight: 700; color: white; font-family: 'Outfit', sans-serif;">{round(len(script_input)/1024, 1)} KB</div>
                        </div>
                        <div style="border-left: 1px solid rgba(255,255,255,0.06);"></div>
                        <div style="padding: 0 4px;">
                            <div style="font-size: 0.62rem; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 4px;">Pages</div>
                            <div style="font-size: 0.88rem; font-weight: 700; color: white; font-family: 'Outfit', sans-serif;">~{est_pages}</div>
                        </div>
                        <div style="border-left: 1px solid rgba(255,255,255,0.06);"></div>
                        <div style="padding: 0 4px;">
                            <div style="font-size: 0.62rem; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 4px;">Scenes</div>
                            <div style="font-size: 0.88rem; font-weight: 700; color: white; font-family: 'Outfit', sans-serif;">{est_scenes}</div>
                        </div>
                        <div style="border-left: 1px solid rgba(255,255,255,0.06);"></div>
                        <div style="padding: 0 4px;">
                            <div style="font-size: 0.62rem; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 4px;">Genre</div>
                            <div style="font-size: 0.88rem; font-weight: 700; color: #9B51E0; font-family: 'Outfit', sans-serif;">{genre.upper()}</div>
                        </div>
                    </div>
                    
                    <!-- Terminal Console logs -->
                    <div style="text-align: left; background: rgba(0, 0, 0, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 14px 18px; font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 0.68rem; color: rgba(244, 246, 251, 0.85); min-height: 90px; max-height: 100px; overflow-y: hidden; line-height: 1.6; margin: 0 auto; box-shadow: inset 0 2px 8px rgba(0,0,0,0.6); width: 85%;">
                        {logs_html}
                    </div>
                </div>
                """ + """
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """
                loading_placeholder.markdown(clean_html(html), unsafe_allow_html=True)
                time.sleep(0.015)
            
            st.session_state['last_progress_pct'] = pct
        
        # Initial stage
        progress_callback("Parsing structure...", 0)
        
        report = runner.run_pipeline(
            script_input, genre=genre, lens=lens,
            progress_callback=progress_callback,
            ablation_config=sidebar_state['ablation_config'],
            cpu_safe_mode=sidebar_state['force_cloud']
        )

        st.session_state['last_report'] = report
        st.session_state['current_input'] = script_input
        st.session_state['current_genre'] = genre
        st.session_state['current_lens'] = lens
        # Store filename for export consistency
        st.session_state['last_filename'] = st.session_state.get('last_filename', 'PastedScript')
        st.session_state.pop('ai_summary_cache', None)
        # Clear all lens-specific caches so fresh analysis is generated
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and (k.startswith('ai_summary_') or k.startswith('ai_pulse_')):
                del st.session_state[k]

        # Auto-generate AI pulse insight for the selected lens
        try:
            from scriptpulse.reporters.llm_translator import generate_section_insight
            st.session_state['ai_pulse_insight'] = generate_section_insight(report, 'pulse', lens=lens)
        except Exception:
            st.session_state['ai_pulse_insight'] = None

        progress_callback("Generating insights...", 100)
        time.sleep(0.5)
        loading_placeholder.empty()
        
        st.session_state['is_analyzing'] = False
        st.rerun()
    except PolicyViolationError as e:
        st.session_state['is_analyzing'] = False
        st.error(
            "This request looks like an evaluation or ranking task. "
            "ScriptPulse models first-pass audience experience — upload your screenplay for structural analysis instead."
        )
        with st.expander("Technical Details"):
            st.code(str(e))
        st.stop()
    except Exception as e:
        st.session_state['is_analyzing'] = False
        # User-friendly error mapping
        USER_FRIENDLY_ERRORS = {
            "could not detect any scenes": (
                "ScriptPulse couldn't find scene headings in your script. "
                "Make sure scenes start with INT. or EXT. (e.g., 'INT. COFFEE SHOP - DAY'). "
                "You can also try pasting just one scene to test."
            ),
            "could not detect screenplay structure": (
                "ScriptPulse couldn't find screenplay structure in your document. "
                "Please ensure the file is a screenplay containing standard scene headings "
                "(e.g., 'INT. ROOM - DAY') or character dialogue blocks."
            ),
            "requires more text": (
                "Your script is too short for analysis. "
                "Please upload at least 2-3 scenes for meaningful results."
            ),
        }
        
        error_msg = str(e).lower()
        friendly_msg = None
        for key, msg in USER_FRIENDLY_ERRORS.items():
            if key in error_msg:
                friendly_msg = msg
                break
        
        if friendly_msg:
            st.error(friendly_msg)
            with st.expander("Technical Details"):
                st.code(str(e))
        else:
            st.error(f"Analysis failed: {e}")
        st.stop()

# =============================================================================
# STEP 3: RENDER RESULTS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')
current_genre = st.session_state.get('current_genre', 'Drama')

if report and current_input:
    st.markdown("---")
    if not st.session_state.get('scrolled_to_results', False):
        st.session_state['scrolled_to_results'] = True
        stu.inject_scroll_to('.st-key-controls_container', block='start')
    
    # Wrap controls row inside a container with a custom key so we can style the third column button
    with st.container(key="controls_container"):
        # Controls row
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 1], gap="medium")
        with ctrl_col1:
            # Perspective selector
            lens = st.selectbox(
                "Analysis Perspective", 
                ["Story Editor", "Studio Executive", "Script Coordinator"],
                index=["Story Editor", "Studio Executive", "Script Coordinator"].index(st.session_state.get('current_lens', 'Story Editor')),
                key="report_lens",
                disabled=True,
                help="To change the perspective, reset and run a new analysis."
            )
            st.session_state['current_lens'] = lens
        with ctrl_col2:
            # Calibrated genre display
            st.selectbox(
                "Calibrated Genre",
                ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"],
                index=["drama", "action", "thriller", "horror", "comedy", "sci-fi", "romance", "fantasy", "avant-garde"].index(current_genre),
                disabled=True,
                help="To change the genre, reset and run a new analysis."
            )
        with ctrl_col3:
            if st.button("🔄 Analyze New Script", use_container_width=True, type="secondary", key="analyze_new_script_btn"):
                st.session_state['last_report'] = None
                st.session_state['current_input'] = None
                st.session_state.pop('parsed_file_key', None)
                st.session_state.pop('parsed_file_content', None)
                st.session_state.pop('current_genre', None)
                st.session_state.pop('current_lens', None)
                st.session_state.pop('scrolled_to_analyze', None)
                st.session_state.pop('scrolled_to_results', None)
                for k in list(st.session_state.keys()):
                    if isinstance(k, str) and (k.startswith('scrolled_to_critique_') or k.startswith('scrolled_to_memo_')):
                        st.session_state.pop(k, None)
                st.rerun()

    st.markdown("---")
    # Add a custom spacer below the divider to prevent visual crowding
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Render unified dashboard: Writer insights first, followed by Producer telemetry
    try:
        render_writer_view(report, current_input, current_genre, lens=lens)
    except Exception as e:
        st.error(f"A rendering issue occurred. Your analysis data is safe.")
        with st.expander("Technical Details"):
            st.code(str(e))
else:
    # Render empty state only if we are not analyzing AND no script is uploaded
    if not st.session_state.get('is_analyzing', False) and not script_input:
        st.markdown("---")
        from app.components.uikit import render_empty_state
        render_empty_state()

# =============================================================================
# STEP 4: EXPORT
# =============================================================================
if report and current_input:
    st.markdown("---")
    render_section_header("📥", "Export Reports",
        "Download professional reports to share with collaborators, agents, or studio executives.")

    # Check if Google Chrome / Chromium is available for PDF conversion
    chrome_available = False
    try:
        from app.streamlit_utils import find_chrome_path
        chrome_available = find_chrome_path() is not None
    except Exception:
        pass

    if not chrome_available:
        st.warning("⚠️ Headless Google Chrome/Chromium is not installed on this server. PDF exports are temporarily disabled, but you can download fully styled HTML reports below (which can be printed/saved as PDF in your browser).")

    c1, c2, c3 = st.columns(3)
    title = st.session_state.get('last_filename', 'Script')
    run_id = report.get('meta', {}).get('run_id', 'default')

    # Cache Writer Report PDF
    writer_pdf_key = f"writer_pdf_{run_id}_{genre}"
    if chrome_available and st.session_state.get(writer_pdf_key) is None:
        try:
            md_content = writer_report.generate_writer_report(report, title=title, genre=genre)
            html_content = stu.convert_md_report_to_html(md_content, title=title)
            pdf_bytes = stu.convert_html_to_pdf(html_content)
            st.session_state[writer_pdf_key] = pdf_bytes
            # Auto-save to workspace root
            with open(os.path.join(ROOT_DIR, f"ScriptPulse_Writer_{genre}.pdf"), "wb") as f:
                f.write(pdf_bytes)
        except Exception:
            st.session_state[writer_pdf_key] = None

    # Cache Studio Coverage PDF
    studio_pdf_key = f"studio_pdf_{run_id}_{genre}_{lens}"
    if chrome_available and st.session_state.get(studio_pdf_key) is None:
        try:
            html_content = studio_report.generate_report(report, script_title=title, lens=lens)
            pdf_bytes = stu.convert_html_to_pdf(html_content)
            st.session_state[studio_pdf_key] = pdf_bytes
            # Auto-save to workspace root
            with open(os.path.join(ROOT_DIR, f"ScriptPulse_Studio_{genre}.pdf"), "wb") as f:
                f.write(pdf_bytes)
        except Exception:
            st.session_state[studio_pdf_key] = None

    # Cache One-Page Summary PDF
    summary_pdf_key = f"summary_pdf_{run_id}_{genre}"
    if chrome_available and st.session_state.get(summary_pdf_key) is None:
        try:
            html_content = print_summary.generate_print_summary(report, script_title=title)
            pdf_bytes = stu.convert_html_to_pdf(html_content)
            st.session_state[summary_pdf_key] = pdf_bytes
            # Auto-save to workspace root
            with open(os.path.join(ROOT_DIR, f"ScriptPulse_Summary_{genre}.pdf"), "wb") as f:
                f.write(pdf_bytes)
        except Exception:
            st.session_state[summary_pdf_key] = None

    # Clean legacy files in workspace root
    for legacy_ext, prefix in [("md", "Writer"), ("html", "Studio"), ("html", "Summary")]:
        legacy_path = os.path.join(ROOT_DIR, f"ScriptPulse_{prefix}_{genre}.{legacy_ext}")
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
            except Exception:
                pass

    with c1:
        with st.container(border=True):
            st.markdown(clean_html("""
                <div style="text-align: center; margin-bottom: 16px;">
                    <div style="font-size: 2.2rem; margin-bottom: 10px; filter: drop-shadow(0 0 10px rgba(155, 81, 224, 0.35));">📄</div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: white; margin-bottom: 8px; font-family: 'Outfit', sans-serif;">Writer Report</div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; height: 50px; overflow: hidden; font-family: 'Inter', sans-serif;">
                        Pacing maps, scene-level turns, and rewrite priorities calibrated for the writer.
                    </div>
                </div>
            """), unsafe_allow_html=True)
            if st.session_state.get(writer_pdf_key) is not None:
                st.download_button(
                    "Download PDF",
                    st.session_state[writer_pdf_key],
                    f"ScriptPulse_Writer_{genre}.pdf", "application/pdf",
                    use_container_width=True,
                    key="dl_writer_btn"
                )
            else:
                try:
                    md_content = writer_report.generate_writer_report(report, title=title, genre=genre)
                    html_content = stu.convert_md_report_to_html(md_content, title=title)
                    st.download_button(
                        "Download HTML",
                        html_content,
                        f"ScriptPulse_Writer_{genre}.html", "text/html",
                        use_container_width=True,
                        key="dl_writer_html"
                    )
                except Exception:
                    st.button("Unavailable", disabled=True, use_container_width=True, key="dl_writer_disabled")

    with c2:
        with st.container(border=True):
            st.markdown(clean_html("""
                <div style="text-align: center; margin-bottom: 16px;">
                    <div style="font-size: 2.2rem; margin-bottom: 10px; filter: drop-shadow(0 0 10px rgba(155, 81, 224, 0.35));">🎬</div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: white; margin-bottom: 8px; font-family: 'Outfit', sans-serif;">Studio Coverage</div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; height: 50px; overflow: hidden; font-family: 'Inter', sans-serif;">
                        Studio coverage memo — market analysis, budget tier, and complexity.
                    </div>
                </div>
            """), unsafe_allow_html=True)
            if st.session_state.get(studio_pdf_key) is not None:
                st.download_button(
                    "Download PDF",
                    st.session_state[studio_pdf_key],
                    f"ScriptPulse_Studio_{genre}.pdf", "application/pdf",
                    use_container_width=True,
                    key="dl_studio_btn"
                )
            else:
                try:
                    html_content = studio_report.generate_report(report, script_title=title, lens=lens)
                    st.download_button(
                        "Download HTML",
                        html_content,
                        f"ScriptPulse_Studio_{genre}.html", "text/html",
                        use_container_width=True,
                        key="dl_studio_html"
                    )
                except Exception:
                    st.button("Unavailable", disabled=True, use_container_width=True, key="dl_studio_disabled")

    with c3:
        with st.container(border=True):
            st.markdown(clean_html("""
                <div style="text-align: center; margin-bottom: 16px;">
                    <div style="font-size: 2.2rem; margin-bottom: 10px; filter: drop-shadow(0 0 10px rgba(155, 81, 224, 0.35));">🖨️</div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: white; margin-bottom: 8px; font-family: 'Outfit', sans-serif;">One-Page Summary</div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; height: 50px; overflow: hidden; font-family: 'Inter', sans-serif;">
                        Printable one-page summary — key scores, pacing metrics, and genre benchmarks.
                    </div>
                </div>
            """), unsafe_allow_html=True)
            if st.session_state.get(summary_pdf_key) is not None:
                st.download_button(
                    "Download PDF",
                    st.session_state[summary_pdf_key],
                    f"ScriptPulse_Summary_{genre}.pdf", "application/pdf",
                    use_container_width=True,
                    key="dl_summary_btn"
                )
            else:
                try:
                    html_content = print_summary.generate_print_summary(report, script_title=title)
                    st.download_button(
                        "Download HTML",
                        html_content,
                        f"ScriptPulse_Summary_{genre}.html", "text/html",
                        use_container_width=True,
                        key="dl_summary_html"
                    )
                except Exception:
                    st.button("Unavailable", disabled=True, use_container_width=True, key="dl_summary_disabled")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<footer class="sp-footer">
    <div>
        <span>Processed in session only</span>
        <span>•</span>
        <span>Not stored on ScriptPulse servers</span>
        <span>•</span>
        <span>&copy; 2026 ScriptPulse</span>
    </div>
</footer>
""", unsafe_allow_html=True)

