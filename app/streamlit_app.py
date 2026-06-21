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
from scriptpulse.reporters import writer_report, studio_report, print_summary

# =============================================================================
# INITIALIZATION
# =============================================================================
APP_BUILD = "v1.0-release"

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
# HERO
# =============================================================================
render_hero_section(
    "ScriptPulse",
    "AI Story Intelligence — Map how your screenplay may feel to a first-time reader. Reference signals for reflection, not judgment."
)

# Create two columns for the setup stage: Left for Screenplay, Right for Configuration & Run
col_setup_left, col_setup_right = st.columns([1.1, 0.9], gap="medium")

with col_setup_left:
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            <i class="ti ti-file-text" style="font-size: 1.8rem; color: #9B51E0;"></i>
            <h3 style="margin: 0 !important; font-size: 1.25rem !important; font-weight: 700; color: white;">Your Screenplay</h3>
        </div>
        """), unsafe_allow_html=True)

        script_input = None
        uploaded_file = st.file_uploader(
            "Drop your screenplay here (PDF, TXT, or FDX)",
            type=['pdf', 'txt', 'fdx'],
            label_visibility="collapsed"
        )
        if uploaded_file and stu.check_upload_size(uploaded_file):
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
                    except Exception as e:
                        st.error("Could not parse FDX formatting. Please ensure it's a valid Final Draft XML file.")
                        script_input = None
                else:
                    try:
                        script_input = uploaded_file.read().decode('utf-8')
                    except Exception:
                        st.error("Could not decode text. Please ensure the file is saved in standard UTF-8 format.")
                        script_input = None

with col_setup_right:
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            <i class="ti ti-settings" style="font-size: 1.8rem; color: #9B51E0;"></i>
            <h3 style="margin: 0 !important; font-size: 1.25rem !important; font-weight: 700; color: white;">Configure Analysis</h3>
        </div>
        <div class="well" style="padding: 20px; background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: var(--radius-md); margin-bottom: 24px;">
            <p style="font-size: 0.88rem; color: rgba(219, 234, 254, 0.75); line-height: 1.6; margin: 0;">
                ScriptPulse provides audience-experience reference signals. It does not rank, approve, or predict commercial success.
            </p>
        </div>
        """), unsafe_allow_html=True)

        genre_raw = st.selectbox("Target Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"],
                              help="The engine adjusts its benchmarks to match the expectations of your genre.")
        genre = genre_raw.lower().replace("-", "-")  # Preserve hyphens, force lowercase
        lens = st.selectbox("Analysis Perspective", ["Story Editor", "Studio Executive", "Script Coordinator"],
                              help="🕵️ Story Editor = Plot & Logic | 🏢 Studio Executive = Market & Budget | ✍️ Script Coordinator = Craft & Flow")



if script_input:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🎬 Analyze My Script", type="primary", use_container_width=True):
        loading_placeholder = st.empty()
        
        def get_logo_base64():
            import base64
            logo_path = os.path.join(ROOT_DIR, "app", "assets", "ScriptPulse_Icon.png")
            if os.path.exists(logo_path):
                try:
                    with open(logo_path, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception:
                    pass
            return None

        try:
            stage_labels = {
                "Parsing structure...": "📐 Parsing screenplay structure...",
                "Extracting features...": "🔬 Extracting narrative features...",
                "Simulating dynamics...": "🧠 Running cognitive simulation...",
                "Running interpretation...": "🎯 Interpreting narrative patterns...",
                "Generating insights...": "✨ Generating writer intelligence...",
            }
            
            def progress_callback(stage_name, pct):
                label = stage_labels.get(stage_name, f"⚡ {stage_name}")
                logo_html = ""
                
                html = f"""
                <div style="text-align: center; padding: 2.5rem; background: linear-gradient(135deg, rgba(32, 29, 48, 0.85) 0%, rgba(26, 23, 41, 0.95) 100%); border-radius: 20px; border: 1px solid rgba(155, 81, 224, 0.25); box-shadow: 0 15px 40px rgba(0,0,0,0.55); max-width: 550px; margin: 2rem auto;">
                    {logo_html}
                    <div style="margin-bottom: 15px;">
                        <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.8rem; color: #FFFFFF;">Script</span>
                        <span class="brand-pulse" style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.8rem; display: inline-block;">Pulse</span>
                    </div>
                    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                        <div style="width: 45px; height: 45px; border: 3px solid rgba(255,255,255,0.08); border-top: 3px solid #9B51E0; border-radius: 50%; animation: spin 1s linear infinite; box-shadow: 0 0 15px rgba(155, 81, 224, 0.4);"></div>
                    </div>
                    <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 600; margin-bottom: 6px;">{label}</div>
                    <div style="color: rgba(244, 246, 251, 0.65); font-size: 0.85rem; margin-bottom: 15px;">Stage Progress: {pct}%</div>
                    <div style="background-color: rgba(255,255,255,0.08); border-radius: 10px; height: 6px; width: 85%; margin: 0 auto; overflow: hidden; border: 1px solid rgba(255,255,255,0.03);">
                        <div style="background: linear-gradient(90deg, #9B51E0, #A56DFF); height: 100%; width: {pct}%; transition: width 0.3s ease;"></div>
                    </div>
                    <div style="color: rgba(244, 246, 251, 0.4); font-size: 0.75rem; margin-top: 15px; font-weight: 300;">Analyzing character voice profiles, pacing, and conflict dynamics...</div>
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
            st.session_state['last_filename'] = uploaded_file.name if uploaded_file else "PastedScript"
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
        except PolicyViolationError as e:
            st.error(
                "This request looks like an evaluation or ranking task. "
                "ScriptPulse models first-pass audience experience — upload your screenplay for structural analysis instead."
            )
            with st.expander("Technical Details"):
                st.code(str(e))
            st.stop()
        except Exception as e:
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
else:
    # Clear landing page layout (instead of redundant empty-state card)
    pass

# =============================================================================
# STEP 3: RENDER RESULTS
# =============================================================================
report = st.session_state.get('last_report')
current_input = st.session_state.get('current_input')
current_genre = st.session_state.get('current_genre', 'Drama')

if report and current_input:
    st.markdown("---")
    # Render unified dashboard: Writer insights first, followed by Producer telemetry
    try:
        render_writer_view(report, current_input, current_genre, lens=lens)
    except Exception as e:
        st.error(f"A rendering issue occurred. Your analysis data is safe.")
        with st.expander("Technical Details"):
            st.code(str(e))

# =============================================================================
# STEP 4: EXPORT
# =============================================================================
if report and current_input:
    st.markdown("---")
    render_section_header("📥", "Export Reports",
        "Download professional reports to share with collaborators, agents, or studio executives.")

    c1, c2, c3 = st.columns(3)
    title = st.session_state.get('last_filename', 'Script')

    with c1:
        try:
            st.download_button("📄 Writer Report", 
                writer_report.generate_writer_report(report, title=title, genre=genre),
                f"ScriptPulse_Writer_{genre}.md", "text/markdown",
                use_container_width=True)
        except Exception:
            st.button("📄 Writer Report", disabled=True, use_container_width=True)
    with c2:
        try:
            st.download_button("🎬 Studio Coverage",
                studio_report.generate_report(report, script_title=title, lens=lens),
                f"ScriptPulse_Studio_{genre}.html", "text/html",
                use_container_width=True)
        except Exception:
            st.button("🎬 Studio Coverage", disabled=True, use_container_width=True)
    with c3:
        try:
            st.download_button("🖨️ One-Page Summary",
                print_summary.generate_print_summary(report, script_title=title),
                f"ScriptPulse_Summary_{genre}.html", "text/html",
                use_container_width=True)
        except Exception:
            st.button("🖨️ One-Page Summary", disabled=True, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="sp-footer">
    <div style="font-size: 0.7rem; color: rgba(244, 246, 251, 0.35); font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; display: flex; justify-content: center; gap: 24px; opacity: 0.6; flex-wrap: wrap;">
        <span>PROCESSED IN SESSION ONLY</span>
        <span>·</span>
        <span>NOT STORED ON SCRIPTPULSE SERVERS</span>
        <span>·</span>
        <span>&copy; 2026 SCRIPTPULSE</span>
    </div>
</div>
""", unsafe_allow_html=True)

