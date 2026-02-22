#!/usr/bin/env python3
"""
ScriptPulse v6.0 - The Creative Instrument
Writer-Native Visual Interface
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
import time
import traceback
import plotly.express as px
import plotly.graph_objects as go

# Ensure we can import the locked pipeline
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse import runner
import scriptpulse.streamlit_utils as stu

# =============================================================================
# v13.1 CONTROL 1: STARTUP INTEGRITY CHECK (Run Once)
# =============================================================================
passed, msg = stu.check_integrity()
if not passed:
    st.error(f"🛑 FATAL CONFIG ERROR: {msg}")
    st.info("System halted for safety. Contact Ops.")
    st.stop()


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

@st.cache_resource(show_spinner="Initializing ScriptPulse Neural Engine...")
def preload_models(cloud_mode=False):
    if cloud_mode:
        print("☁️ Cloud Mode Active: Skipping heavy ML preloads to save RAM.")
        return True
    try:
        # v13.1 CONTROL 2: RUNTIME SINGLETONS
        from scriptpulse.utils.model_manager import ModelManager
        loader = ModelManager()
        
        # Pre-fetch weights for fast first run
        loader.get_pipeline('zero-shot-classification')
        loader.get_sentence_transformer('sentence-transformers/all-MiniLM-L6-v2')
        
        return True
    except Exception as e:
        print(f"Preload Warning: {e}")
        return False

# Detect if we are on a constrained cloud environment (Streamlit Cloud, Heroku)
IS_CLOUD = os.environ.get('STREAMLIT_SERVER_PORT') is not None or os.environ.get('CLOUD_MODE', '1') == '1'

# Trigger Preload only if local (avoid 5GB RAM spike on boot)
preload_models(cloud_mode=IS_CLOUD)

# v13.0: Simple, friendly UI for non-technical writers
st.set_page_config(
    page_title="ScriptPulse - Easy Script Analyzer",
    page_icon="🎬",
    layout="wide"
)

# v13.1 CONTROL 3: SYNC SAFETY STATE
stu.sync_safety_state()


# =============================================================================
# THEME & STYLING (The "Premium Instrument" Look)
# =============================================================================

st.markdown("""
<style>
    /* Clean, distraction-free typography */
    body { 
        font-family: 'Inter', sans-serif; 
        background-color: #ffffff;
    }
    
    /* Force main container to be white */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Hide Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Elegant Spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max_width: 900px;
    }
    
    /* Signal Boxes - Writer Native Colors */
    .signal-box {
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        background-color: #fafafa;
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR: ORIENTATION
# =============================================================================

with st.sidebar:
    st.title("ScriptPulse")
    st.caption("Writer-Native Analytics (or Research Platform)")
    
    st.markdown("---")
    ui_mode = st.radio("Interface Mode", ["Writer Mode (Creative)", "Lab Mode (Research)"], index=0, help="Lab Mode shows advanced ML ablation and threshold controls.")
    st.markdown("---")
    
    with st.expander("⚡ Engine Context (RAM Usage)", expanded=ui_mode == "Lab Mode (Research)"):
        engine_mode = st.radio(
            "Hardware Constraints", 
            ["Cloud / Fast (Heuristic Fallback)", "Local (Full AI Engine - Requires 8GB RAM)"],
            index=0 if IS_CLOUD else 1,
            help="Full AI loads GPT-2 and SBERT. Cloud forces mathematical heuristics."
        )
        force_cloud = "Cloud" in engine_mode
        if force_cloud:
            st.caption("🟢 Running in Low-RAM Mode (< 1GB)")
        else:
            st.caption("🔴 Running in High-RAM Mode (5GB+)")
            
    st.markdown("---")
    
    # Simplified Mode Selection
    mode = st.radio("Feature", ["Script Analysis", "Scene Compare", "Live Sandbox"], label_visibility="collapsed")
    
    # Trigger Preload based on user selection
    preload_models(cloud_mode=force_cloud)

    if mode == "Live Sandbox":
        st.header("⚡ Live Sandbox (Intervention)")
        st.caption("Test edits side-by-side to see how changes affect pacing.")
        
        col_base, col_new = st.columns(2)
        with col_base:
            sandbox_base = st.text_area("Baseline Scene:", height=250, placeholder="The original scene...", key="sandbox_base")
        with col_new:
            sandbox_new = st.text_area("Edited Scene:", height=250, placeholder="Your revised scene...", key="sandbox_new")
        
        if st.button("Compare Edit"):
            if len(sandbox_base) > 10 and len(sandbox_new) > 10:
                with st.spinner("Analyzing Intervention..."):
                    try:
                        report_base = runner.run_pipeline(sandbox_base, cpu_safe_mode=True, experimental_mode=False)
                        report_new = runner.run_pipeline(sandbox_new, cpu_safe_mode=True, experimental_mode=False)
                        
                        trace_base = report_base.get('temporal_trace', [])[0] if report_base.get('temporal_trace') else {}
                        trace_new = report_new.get('temporal_trace', [])[0] if report_new.get('temporal_trace') else {}
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Baseline Tension", f"{trace_base.get('strain', 0.0):.2f}")
                        with c2:
                            st.metric("Edited Tension", f"{trace_new.get('strain', 0.0):.2f}", delta=round(trace_new.get('strain', 0.0) - trace_base.get('strain', 0.0), 2))
                        with c3:
                            st.metric("Edited Density", f"{trace_new.get('effort', 0.0):.2f}", delta=round(trace_new.get('effort', 0.0) - trace_base.get('effort', 0.0), 2))
                        
                        st.markdown("---")
                        # Apply XAI Highlighting on Edited Only for brevity
                        st.subheader("Explainability (XAI) Focus Map: Edited Scene")
                        import scriptpulse.utils.xai_highlighter as xai
                        highlighted_html = xai.generate_xai_html(sandbox_new)
                        st.markdown(highlighted_html, unsafe_allow_html=True)
                        st.caption("🔴 High-Density/Action Trigger | 🔵 Dialogue Focus")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
            else:
                st.warning("Please fill both Baseline and Edited text areas to compare.")
        st.stop()
    
    if mode == "Scene Compare":
        st.header("⚖️ Scene A/B")
        st.caption("Compare two versions.")
        
        col1, col2 = st.columns(2)
        with col1:
            file_a = st.file_uploader("Version A", key="file_a")
        with col2:
            file_b = st.file_uploader("Version B", key="file_b")
            
        if file_a and file_b:
            if st.button("Compare"):
                # ... (Logic remains same, just cleaner UI) ...
                import scriptpulse.agents.parsing as p
                import scriptpulse.agents.temporal as t
                import scriptpulse.agents.valence as v
                
                def analyze_full(f):
                    txt = f.getvalue().decode('utf-8')
                    # Run full pipeline to get scene-level tracing
                    return runner.run_pipeline(txt, experimental_mode=False, cpu_safe_mode=True)
                    
                report_a = analyze_full(file_a)
                report_b = analyze_full(file_b)
                
                trace_a = [p.get('strain', 0.0) for p in report_a.get('temporal_trace', [])]
                trace_b = [p.get('strain', 0.0) for p in report_b.get('temporal_trace', [])]
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    avg_a = sum(trace_a)/len(trace_a) if trace_a else 0
                    st.metric("Avg Narrative Tension (A)", f"{avg_a:.2f}")
                with c2:
                    avg_b = sum(trace_b)/len(trace_b) if trace_b else 0
                    st.metric("Avg Narrative Tension (B)", f"{avg_b:.2f}")
                with c3:
                    import scipy.stats as stats
                    if len(trace_a) > 2 and len(trace_b) > 2:
                        # P-value calculation
                        # If sizes differ, use independent t-test instead of paired
                        t_stat, p_val = stats.ttest_ind(trace_a, trace_b, equal_var=False)
                        st.metric("Statistical Sig (p-value)", f"{p_val:.4f}")
                        if p_val < 0.05:
                            st.success("Significant Difference! (p < .05)")
                        else:
                            st.warning("No Sig. Difference (p >= .05)")
                    else:
                        st.metric("Statistical Sig", "N/A (Too short)")
                    
        st.stop()
        
    # --- INFO ---
    st.info(
        "**Reading the Pulse**\n\n"
        "🔴 **High Tension**: Demanding, intense.\n"
        "🟢 **Flow**: Balanced, engaging.\n"
        "🟠 **Risk**: Low energy, potential drift."
    )
    
    st.markdown("---")
    # Hide complex settings by default
    with st.expander("⚙️ Advanced Settings"):
         ref_file = st.file_uploader("Reference Script", type=['txt', 'pdf'])

    ablation_config = {}
    if ui_mode == "Lab Mode (Research)":
        with st.expander("🧪 Ablation & Parameter Console", expanded=True):
            st.markdown("Control exact Pipeline constraints.")
            
            # Force to False if Cloud Mode is active
            ab_sbert = st.checkbox("Enable SBERT (Thematic Extraction)", value=not force_cloud, key="ab_sbert", disabled=force_cloud)
            ab_gpt2 = st.checkbox("Enable GPT-2 (Surprisal Proxy)", value=not force_cloud, key="ab_gpt2", disabled=force_cloud)
            ab_multimodal = st.checkbox("Enable Multimodal Extrapolation", value=True, key="ab_multimodal")
            
            if force_cloud:
                st.warning("⚠️ Heavy models disabled by Hardware Constraints selector above.")
                
            ab_seed = st.number_input("Random Seed", value=42, key="ab_seed")
            ab_decay = st.number_input("Fatigue Decay Rate (k)", value=0.05, step=0.01, key="ab_decay")
            
            ablation_config = {
                'use_sbert': ab_sbert,
                'use_gpt2': ab_gpt2,
                'use_multimodal': ab_multimodal,
                'seed': ab_seed,
                'decay_rate': ab_decay
            }
    else:
        # Implicitly set ablation state for Creative Mode based on Engine
        ablation_config = {
            'use_sbert': not force_cloud,
            'use_gpt2': not force_cloud,
            'use_multimodal': True,
        }

    # v13.1 CONTROL 4 & 6: OPERATOR PANEL + SHADOW TOGGLE
    shadow_mode, high_accuracy_mode = stu.render_operator_panel(st.session_state.get('prev_run'))


# =============================================================================
# MAIN INTERFACE
# =============================================================================

# Add comparator import (safe)
try:
    from scriptpulse.agents import comparator
except ImportError:
    comparator = None

st.title("The Instrument")
st.markdown("*A visual interface for screenplay rhythm.*")

# --- Step 1: Input & Parsing ---

st.header("1. Load Draft")
    
uploaded_file = st.file_uploader(
    "Upload Screenplay (PDF / TXT)",
    type=['txt', 'pdf'],
    help="Upload your draft to see the structural heartbeat."
)

script_input = None
scene_list = []

if uploaded_file is not None:
    # READ FILE
    try:
        file_ext = uploaded_file.name.split('.')[-1].lower() if uploaded_file and hasattr(uploaded_file, 'name') else 'txt'

        if file_ext == 'fdx':
            # FDX Handling
            try:
                from scriptpulse.agents import importers
                string_data = uploaded_file.getvalue().decode("utf-8")
                pre_parsed_lines = importers.run(string_data)
                st.success(f"✅ FDX Parsed: {len(pre_parsed_lines)} lines extracted.")
                
                # Reconstruct text for display/fallback
                script_text = "\n".join([l['text'] for l in pre_parsed_lines])
                
            except Exception as e:
                st.error(f"FDX Parse Error: {e}")
        elif uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_parts = [page.extract_text() for page in pdf_reader.pages]
            script_text = "\n".join(text_parts)
        else: # txt, fountain, md
            script_text = uploaded_file.read().decode('utf-8')
            
        # v13.1 CONTROL 5: SIZE GUARD
        if not stu.check_upload_size(uploaded_file):
            st.stop()
            
        # IMMEDIATE PARSE (For Scene Picker)
        with st.spinner("Parsing structure..."):
            # Use pre_parsed_lines if available, otherwise parse script_text
            if pre_parsed_lines:
                scene_list = runner.parse_structure(pre_parsed_lines=pre_parsed_lines)
            else:
                scene_list = runner.parse_structure(script_text)
            
        if uploaded_file is not None:
            # ... (parsing logic) ...
            
            st.success(f"Loaded {len(scene_list)} scenes.")
            
            # v10.0: Context-Aware Fairness (Character Extraction)
            # Scan parsed lines for characters (tag='C')
            all_chars = sorted(list(set([l['text'] for l in (pre_parsed_lines if pre_parsed_lines else runner.parsing.run(script_text)) if l['tag'] == 'C'])))
            
            with st.expander("🎭 Character Context (Optional) - Tag Roles"):
                st.caption("Help the Fairness Auditor understand context (e.g., Villains are expected to be negative).")
                char_tags = {}
                cols = st.columns(2)
                for i, char in enumerate(all_chars):
                    if i < 10: # Only show top 10 to avoid clutter
                        role = cols[i%2].selectbox(f"Role for {char}", ["Unknown", "Protagonist", "Antagonist", "Supporting"], key=f"role_{char}")
                        if role != "Unknown":
                            char_tags[char] = role
            
            # View Script Text
            with st.expander("View Script Text"):
                 st.text(script_text[:5000] + "...")
        
    except Exception as e:
        st.error(f"Could not read file: {e}")

# Paste Fallback
if script_input is None:
    script_input = st.text_area("Or paste text here", height=150)
    if script_input and len(script_input) > 100:
         scene_list = runner.parse_structure(script_input)


# --- Step 2: Context & Research Settings ---

st.header("2. Context & Settings")

col_genre, col_lens = st.columns(2)

with col_genre:
    # Load baselines for tooltip / trace overlay context
    genre_baselines = {}
    try:
        with open("scriptpulse/config/genre_baselines.json", "r") as f:
            genre_baselines = json.load(f).get('genres', {})
    except:
        pass
        
    genre_options = list(genre_baselines.keys()) if genre_baselines else ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Family"]
    
    selected_genre = st.selectbox(
        "Target Genre Baseline",
        genre_options,
        help="Loads 'Expected Curve' for cross-domain comparison."
    )

if ui_mode == "Lab Mode (Research)":
    with col_lens:
        selected_lens = st.selectbox(
            "Analysis Lens",
            ["viewer", "reader", "narrator"],
            format_func=lambda x: x.capitalize(),
            help="Viewer=Visceral, Reader=Literary, Narrator=Structural"
        )
        
    st.markdown("---")
    selected_profile = st.selectbox(
        "Target Audience (Cognitive Profile)",
        ["General", "Cinephile", "Distracted", "Child"],
        help="Simulates the brain capacity of different viewers."
    )

    if selected_profile == "Cinephile":
        st.caption("🧠 **High Capacity**: Tolerates complexity, remembers context longer.")
    elif selected_profile == "Distracted":
        st.caption("🧠 **Low Capacity**: Needs frequent refresh, hates confusion.")
    elif selected_profile == "Child":
        st.caption("🧠 **Minimal Capacity**: Needs strict continuity.")

    st.markdown("---")
    use_high_res = st.checkbox("High-Resolution Mode (Micro-Beats)", help="Slice scenes into beats for HD analysis (Slower).")
else:
    # Writer Mode Defaults
    selected_lens = "viewer"
    selected_profile = "General"
    use_high_res = False

writer_intent = []
if script_input:
    with st.expander("Declare specific intent (Optional)", expanded=False):
        st.markdown("Select sections where you *aimed* for a specific intense experience.")
        
        # Prepare dropdown options
        # Format: "1. INT. CAFE"
        scene_options = [f"{s['scene_index']}. {s['heading']}" for s in scene_list]
        
        col1, col2 = st.columns(2)
        with col1:
             start_scene_str = st.selectbox("Start Scene", scene_options, index=0)
        with col2:
             end_scene_str = st.selectbox("End Scene", scene_options, index=len(scene_options)-1 if len(scene_options)>0 else 0)
             
        intent_type = st.selectbox("Intent", [
            "intentionally exhausting",
            "intentionally confusing",
            "experimental structure",
            "intentionally minimal"
        ])
        
        if st.checkbox("Apply Intent Tag"):
            # Extract index from string "1. ..." -> 1
            start_idx = int(start_scene_str.split('.')[0])
            end_idx = int(end_scene_str.split('.')[0])
            writer_intent = [{'scene_range': [start_idx, end_idx], 'intent': intent_type}]
            st.info(f"Tagged Scenes {start_idx}-{end_idx} as '{intent_type}'")


# --- Step 3: The Pulse Analysis ---

# Caching Wrapper (Defined at top level within step context)
@st.cache_data(show_spinner="Running Analysis...")
def cached_analysis(text, intent, lens, genre, profile, high_res, shadow=False, high_acc=False, ablation_config=None):
    # Override safe mode if session requests it
    force_safe = st.session_state.get('safe_mode_active', False)
    
    # v13.1 Optimization: Fast Mode Defaults
    use_cpu_safe = True
    use_stride = 3
    use_min_words = 20
    
    if high_acc:
        use_cpu_safe = False
        use_stride = 1
        use_min_words = 10
    
    if force_safe:
        use_cpu_safe = True

    return runner.run_pipeline(
        text, 
        writer_intent=intent,
        lens=lens,
        genre=genre,
        audience_profile=profile,
        high_res_mode=high_res,
        experimental_mode=True, 
        moonshot_mode=True,      
        cpu_safe_mode=use_cpu_safe, 
        shadow_mode=shadow,
        valence_stride=use_stride,
        stanislavski_min_words=use_min_words,
        ablation_config=ablation_config
    )

analyze_clicked = st.button("Analyze Rhythm", type="primary")

if script_input and (analyze_clicked or 'last_report' in st.session_state):
    
    # v13.1 Optimization: Input Guard
    if not stu.check_input_length(script_input):
        st.stop()
        
    report = None
    
    if analyze_clicked:
         try:
            with st.spinner("Processing story architecture..."):
                report = cached_analysis(
                    script_input, 
                    writer_intent,
                    selected_lens,
                    selected_genre,
                    selected_profile,
                    use_high_res,
                    shadow_mode,
                    high_accuracy_mode,
                    ablation_config
                )
            st.session_state['last_report'] = report
         except Exception as e:
            st.error(f"Analysis Failed: {e}")
            st.stop()
            
    elif 'last_report' in st.session_state:
        report = st.session_state['last_report']

    if report is None:
        st.stop()

    # v13.1 CONTROL 5: EXECUTION GUARD
    render_start = time.time()
    HARD_RENDER_LIMIT = 2.0 
    truncated = False
    
    # === THE PULSE DASHBOARD (Writer-First) ===
    st.markdown("---")
    
    # Calculate key metrics
    trace = report.get('temporal_trace', [])
    avg_intensity = sum(p.get('attentional_signal', 0) for p in trace) / len(trace) if trace else 0
    intensity_score = int(avg_intensity * 10)
    
    valence_scores = report.get('valence_scores', [])
    avg_valence = sum(valence_scores) / len(valence_scores) if valence_scores else 0
    
    # Default (Lexicon)
    if avg_valence > 0.1:
        tone_label = "Bright" # Writer term
        tone_emoji = "☀️"
    elif avg_valence < -0.1:
        tone_label = "Dark" # Writer term
        tone_emoji = "🌑"
    else:
        tone_label = "Neutral"
        tone_emoji = "☁️"
        
    # v13.0: OVERRIDE with ML Emotion (Stanislavski)
    ms_data = report.get('moonshot_resonance', [])
    if ms_data:
        emotions = [s.get('stanislavski_state', {}).get('felt_emotion', 'Neutral') for s in ms_data]
        valid_emotions = [e for e in emotions if e and 'N/A' not in e]
        
        if valid_emotions:
            from collections import Counter
            dom_emo = Counter(valid_emotions).most_common(1)[0][0]
            tone_label = dom_emo
            
            # Writer-Centric Emojis
            if "Fear" in dom_emo: tone_emoji = "😨 Tension"
            elif "Suspicion" in dom_emo: tone_emoji = "👀 Mystery"
            elif "Empowered" in dom_emo: tone_emoji = "⚡ Drive"
            elif "Helpless" in dom_emo: tone_emoji = "🏳️ Tragedy"
            elif "Trust" in dom_emo: tone_emoji = "🤝 Warmth"
            else: tone_emoji = "🎭 Drama"
    
    runtime = report.get('runtime_estimate', {})
    runtime_min = runtime.get('avg_minutes', 0)
    
    # Display in 4 clean columns
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Tension", f"{intensity_score}/10")
    with c2:
        st.metric("Mood", tone_label)
    with c3:
        st.metric("Pacing", "Fast" if intensity_score > 6 else "Slow")
    with c4:
        st.metric("Runtime", f"{runtime_min} mins")
    
    # === COLLAPSIBLE SECTIONS (v21.0) ===
    
    # Hide research comparisons in expander
    with st.expander("🔬 Advanced Comparisons", expanded=False):
        with st.expander("🔬 Research Comparison (Longitudinal & Target)", expanded=True):
            cols = st.columns(2)
            
            # A. Longitudinal (Optimization Gain)
            if 'prev_run' in st.session_state:
                delta = comparator.compare_longitudinal(report, st.session_state['prev_run'])
                with cols[0]:
                    st.subheader("Optimization (vs Last Run)")
                    if delta:
                        change = delta.get('load_change_pct', 0)
                        color = "green" if change < 0 else "red"
                        st.markdown(f"**Total Load Change**: :{color}[{change}%]")
                        st.markdown(f"**Peak Strain Delta**: {delta.get('peak_strain_delta')}")
                        st.caption("Lower load is generally better for readability.")
                    else:
                        st.caption("No significant change detected.")
            else:
                 with cols[0]:
                    st.subheader("Optimization")
                    st.caption("Run analysis again to see effective changes.")

            # B. Reference Target (Stylistic Distance)
            if ref_file:
                with st.spinner("Analyzing Reference Target..."):
                    # Quick parse of ref
                    try:
                        # Re-read ref file because stream might be consumed? 
                        # Streamlit file uploader buffers, so typical pattern:
                        ref_file.seek(0)
                        ref_bytes = ref_file.read()
                        if ref_file.type == "application/pdf":
                             import PyPDF2
                             # Complex to re-read PDF bytes in memory with PyPDF2 without file path
                             # Simplified: Just warn if PDF, or skip for now. 
                             # Actually PyPDF2.PdfReader(BytesIO(ref_bytes)) works
                             from io import BytesIO
                             pdf_r = PyPDF2.PdfReader(BytesIO(ref_bytes))
                             ref_text = "\n".join([p.extract_text() for p in pdf_r.pages])
                        else:
                             ref_text = ref_bytes.decode('utf-8')
                             
                        ref_report = runner.run_pipeline(ref_text, lens=selected_lens)
                        comp_res = comparator.compare_to_reference(report.get('temporal_trace'), ref_report.get('temporal_trace'))
                        
                        with cols[1]:
                           st.subheader("Reference Target")
                           st.markdown(f"**Distance**: {comp_res['stylistic_distance']}")
                           st.info(f"Verdict: {comp_res['interpretation']}")
                           
                    except Exception as e:
                        st.error(f"Ref Analysis Failed: {e}")
            else:
                 with cols[1]:
                     st.caption("Upload a Reference Script in Sidebar to compare styles.")
    
    # === CO-CREATIVITY ENGINE (v8.0) ===
    suggestions = report.get('suggestions', {})
    
    # Handle both dict and list formats safely
    if suggestions:
        # Check if it's a dict with 'structural_repair_strategies' key
        if isinstance(suggestions, dict):
            repair_strategies = suggestions.get('structural_repair_strategies', [])
        elif isinstance(suggestions, list):
            repair_strategies = suggestions
        else:
            repair_strategies = []
        
        if repair_strategies:
            with st.expander("💡 Creative Coaching & Repair", expanded=True):
                st.caption("Heuristic-to-Creative suggestions based on structural analysis")
                for sugg in repair_strategies:
                    # Ensure sugg is a dict
                    if isinstance(sugg, dict):
                        scene_num = sugg.get('scene', 'Unknown')
                        diagnosis = sugg.get('diagnosis', 'No diagnosis')
                        st.markdown(f"**Scene {scene_num}**: {diagnosis}")
                        
                        # Heuristic Coaching Translation
                        val = sugg.get('strategy', '')
                        if "decrease" in val.lower() and "density" in val.lower():
                            st.info("🎨 **Writer Tip:** This scene is heavily loaded with physical action or dense text. Try breaking up the long action blocks or insert a brief moment of character reflection to provide 'Breathing Room'.")
                        elif "increase" in val.lower() and "tension" in val.lower():
                            st.info("🎨 **Writer Tip:** This scene is stalling. Consider introducing a complication, raising the stakes, or cutting exposition to accelerate the pacing.")
                        else:
                            st.markdown(f"→ {val}")
                        st.markdown("")  # spacing
                        
    if ui_mode == "Writer Mode (Creative)":
        with st.expander("🛡️ System Blindspots (Trust Management)", expanded=False):
            st.warning("**What the AI Can't See:**\n\nScriptPulse measures *Structural Pacing* and *Lexical Density*. It does **NOT** understand narrative logic. It will not flag plot holes, continuity errors (e.g., 'Chekhov's Gun'), or character logic inconsistencies.")
                    
                    
    # === WRITER WORKSPACE ===
    st.markdown("### 📖 Story Analysis")
    
    tabs = st.tabs(["Themes & Drivers", "Characters", "Structure", "Subtext (AI)"])
    
    # Map tabs
    tab_drivers = tabs[0]
    tab_chars = tabs[1]
    tab_struct = tabs[2]
    tab_subtext = tabs[3]
    
    # 1. THEMES & DRIVERS (was Quick Summary / XAI)
    with tab_drivers:
        st.caption("What is driving your story?")
        xai_attribution = report.get('xai_attribution', [])
        
        if xai_attribution:
            first = xai_attribution[0] if isinstance(xai_attribution, list) and len(xai_attribution) > 0 else {}
            driver = first.get('dominant_driver', 'Unknown').title()
            st.markdown(f"**Primary Driver**: {driver}")
            
            drivers = first.get('drivers', {})
            if drivers:
                # Custom Clean Progress Bars
                for d, pct in drivers.items():
                    st.text(f"{d.title()}")
                    st.progress(pct)
            
    # Prepare Data
    moonshot_data = report.get('moonshot_analysis', []) if report else []

    # 4. SUBTEXT (was Moonshot)

    with tab_subtext:
        if moonshot_data:
            st.info("🧠 **AI Subtext Reader**")
            st.caption("The AI 'reads' the subtext (Safety, Trust, Agency).")
            
            # Prepare Dataframes
            ms_records = []
            for scene in moonshot_data:
                state = scene['stanislavski_state']['internal_state']
                ms_records.append({
                    'Scene': scene['scene_index'],
                    'Safety': state.get('safety', 0),
                    'Trust': state.get('trust', 0),
                    'Agency': state.get('agency', 0)
                })
            
            df_ms = pd.DataFrame(ms_records).set_index('Scene')
            
            st.subheader("Emotional Arc")
            st.line_chart(df_ms[['Safety', 'Trust', 'Agency']], color=["#00CC66", "#FFA500", "#FF4B4B"])
        else:
            st.caption("No subtext data available.")
            
    # 2. CHARACTERS (was Voice Map / Chemistry)
    with tab_chars:
        st.caption("Do your characters sound distinct? Do they grow?")
        
        voice_data = report.get('voice_fingerprints', {})
        if voice_data:
            # A. Voice Map
            st.subheader("🗣️ Voice Distinctiveness")
            v_data = []
            for char, metrics in voice_data.items():
                v_data.append({
                    'Character': char,
                    'Complexity': metrics['complexity'],
                    'Positivity': metrics['positivity'],
                    'Agency': metrics['agency'] * 100, 
                    'Lines': metrics['line_count']
                })
            
            if v_data:
                st.scatter_chart(pd.DataFrame(v_data), x='Complexity', y='Positivity', size='Agency', color='Character')
            
            st.markdown("---")
            
            # B. Character Growth (Arc)
            st.subheader("📈 Character Growth")
            if len(report.get('scenes', [])) > 6:
                # Simple logic: Act 1 vs Act 3 Agency
                char_arcs = {}
                scenes = report['scenes']
                n_scenes = len(scenes)
                for char, profile in voice_data.items():
                    if profile['line_count'] < 5: continue
                    
                    # Trend Calculation (Simplified)
                    active_scores = []
                    for s in scenes:
                         # Check if char in scene lines
                         if any(char in l.get('text', '') for l in s['lines'] if l.get('tag')=='C'):
                             active_scores.append(report['valence_scores'][s['scene_index']] if s['scene_index'] < len(report['valence_scores']) else 0)
                    
                    if len(active_scores) > 2:
                        start = sum(active_scores[:len(active_scores)//3]) / max(1, len(active_scores)//3)
                        end = sum(active_scores[-len(active_scores)//3:]) / max(1, len(active_scores)//3)
                        char_arcs[char] = {'Start': start, 'End': end, 'Growth': end - start}
                
                if char_arcs:
                    for char, data in char_arcs.items():
                        trend = data['Growth']
                        icon = "↗️" if trend > 0.1 else "↘️" if trend < -0.1 else "➡️"
                        st.metric(f"{char}", f"{icon} {trend:.2f} Growth")
            
            # C. Chemistry
            interaction_map = report.get('interaction_map', {})
            if interaction_map:
                st.markdown("---")
                st.subheader("💞 Interaction Chemistry")
                chem_data = []
                val_scores = report.get('valence_scores', [])
                
                for pair, indices in interaction_map.items():
                    if len(indices) < 2: continue
                    p_vals = [val_scores[i] for i in indices if i < len(val_scores)]
                    if not p_vals: continue
                    avg = sum(p_vals)/len(p_vals)
                    c1, c2 = pair.split('|')

                    chem_data.append({'Char A': c1, 'Char B': c2, 'Chemistry': avg})
                
                if chem_data:
                     st.dataframe(pd.DataFrame(chem_data).style.background_gradient(cmap='coolwarm', vmin=-0.5, vmax=0.5))

    # 3. STRUCTURE (was Act Fidelity)
    with tab_struct:
        st.caption("Does the story hold together?")
        
        macro = report.get('macro_structure_fidelity', {})
        if macro:
            st.metric("Structure Fidelity", f"{macro.get('fidelity_score', 0)}%")
            st.caption(f"Best fit: {macro.get('best_fit_template', 'Unknown')}")
            
        trace = report.get('temporal_trace', [])
        if len(trace) > 10:
            st.subheader("Act Pacing")
            n = len(trace)
            acts = {
                "Act 1": trace[:int(n*0.25)],
                "Act 2": trace[int(n*0.25):int(n*0.75)],
                "Act 3": trace[int(n*0.75):]
            }
            act_rows = []
            for name, scenes in acts.items():
                if scenes:
                    avg_t = sum(s.get('attentional_signal', 0) for s in scenes) / len(scenes)
                    act_rows.append({'Act': name, 'Avg Tension': f"{avg_t:.2f}"})
            st.table(pd.DataFrame(act_rows).set_index("Act"))

    # Cleanup Sidebar Message
    # (Removed longitudinal info for simplicity)
    
    # Store current run for next time
    st.session_state['prev_run'] = report
    
    # === VISUALIZATION: THE PULSE LINE ===
    st.markdown("---")
    st.header("The Pulse Line")
    
    # Prepare Data for Chart
    trace = report.get('temporal_trace', [])
    if trace:
        chart_data = []
        for i, point in enumerate(trace):
            # Point contains 'effort', 'recovery', 'strain'
            chart_data.append({
                'Scene': i,
                'Load': point.get('effort', 0.5), # E[i]
                'Recovery': point.get('recovery', 0.5), # R[i]
                'Net Tension': point.get('strain', 0.0), # S[i]
                'Confidence': point.get('confidence', 0.85) # from v1.3 metrics if available
            })
            
        df = pd.DataFrame(chart_data)
        
        if ui_mode == "Lab Mode (Research)":
            # Advanced Plotly Chart with Confidence Intervals
            fig = go.Figure()

            # Bootstrapped Uncertainty (Monte Carlo Feature Noise)
            import numpy as np
            base_tensions = np.array([c['Net Tension'] for c in chart_data])
            n_iterations = 20
            perturbed_traces = []
            for _ in range(n_iterations):
                # Add heuristic bootstrapping noise
                noise = np.random.normal(0, 0.05 + (0.05 * (1.0 - np.array([c.get('Confidence', 0.85) for c in chart_data]))), len(base_tensions))
                perturbed_traces.append(np.clip(base_tensions + noise, 0, 1))
            
            y_lower = np.percentile(perturbed_traces, 5, axis=0).tolist()
            y_upper = np.percentile(perturbed_traces, 95, axis=0).tolist()
            
            # Draw Confidence Interval Band
            fig.add_trace(go.Scatter(
                x=list(df['Scene']) + list(df['Scene'])[::-1],
                y=y_upper + y_lower[::-1],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
                name='Confidence Band'
            ))

            # Top Driving Features Attribution
            hovertemplate = (
                "Scene: %{x}<br>"
                "Tension: %{y:.2f}<br>"
                "---<br>"
                "%{customdata[0]}<br>"
                "%{customdata[1]}<br>"
                "%{customdata[2]}"
            )
            
            # Determine top features for each scene
            custom_data = []
            for scene_data in trace:
                features = [
                    ('Surprisal', scene_data.get('effort', 0) * 0.4), # Proxies for display
                    ('Action', scene_data.get('action_density', 0)),
                    ('Dialogue', scene_data.get('dialogue_density', 0)),
                    ('Confusion', scene_data.get('coherence_penalty', 0))
                ]
                # Sort by impact
                features.sort(key=lambda x: x[1], reverse=True)
                top_3 = [f"{k}: +{v:.2f}" for k, v in features[:3]]
                while len(top_3) < 3: top_3.append("N/A")
                custom_data.append(top_3)

            # Main Line (Colorblind Safe Blue)
            fig.add_trace(go.Scatter(
                x=df['Scene'],
                y=df['Net Tension'],
                line=dict(color='#1f77b4', width=2),
                mode='lines',
                name='Narrative Tension',
                customdata=custom_data,
                hovertemplate=hovertemplate
            ))
            
            # Recovery Line (Colorblind Safe Orange)
            fig.add_trace(go.Scatter(
                x=df['Scene'],
                y=df['Recovery'],
                line=dict(color='#ff7f0e', width=1, dash='dash'),
                mode='lines',
                name='Breathing Room (Recovery)'
            ))

            # Naive Baseline Validation
            if 'scenes' in report:
                naive_counts = [len([l for l in s['lines'] if l.get('text')]) for s in report['scenes']]
                max_words = max(naive_counts) if naive_counts and max(naive_counts) > 0 else 1
                naive_baseline = [(c / max_words) for c in naive_counts]
                fig.add_trace(go.Scatter(
                    x=df['Scene'],
                    y=naive_baseline[:len(df)],
                    line=dict(color='gray', width=2, dash='dot'),
                    mode='lines',
                    name='Naive Baseline (Lexical Density)'
                ))
            
            # Genre Baseline Overlay
            try:
                with open("scriptpulse/config/genre_baselines.json", "r") as f:
                    g_data = json.load(f).get('genres', {})
                    if selected_genre in g_data:
                        base_curve = g_data[selected_genre]['curve']
                        # Interpolate the 7 point baseline curve over the len(df) scripts
                        import numpy as np
                        x_base = np.linspace(0, len(df)-1, len(base_curve))
                        x_interp = np.arange(len(df))
                        y_interp = np.interp(x_interp, x_base, base_curve)
                        
                        fig.add_trace(go.Scatter(
                            x=df['Scene'],
                            y=y_interp,
                            line=dict(color='rgba(44, 160, 44, 0.5)', width=2, dash='dashdot'),
                            mode='lines',
                            name=f'Expected {selected_genre} Curve'
                        ))
            except Exception as e:
                pass
                
            # Full Model Overlay if Ablated
            ablation_active = False
            if 'ablation_config' in locals() and ablation_config and (not ablation_config.get('use_sbert', True) or not ablation_config.get('use_gpt2', True)):
                ablation_active = True
                
            if ablation_active:
                try: 
                    # Fetch cached Full Run or do a quick trace
                    unablated_report = runner.run_pipeline(script_input, cpu_safe_mode=True, experimental_mode=False, ablation_config=None)
                    un_trace = unablated_report.get('temporal_trace', [])
                    un_y = [p.get('strain', 0.0) for p in un_trace]
                    fig.add_trace(go.Scatter(
                        x=df['Scene'],
                        y=un_y[:len(df)],
                        line=dict(color='orange', width=2),
                        mode='lines',
                        name='Full Model Signal (Un-Ablated)'
                    ))
                except Exception as e:
                    pass

            # Ground Truth Overlay with IRR
            st.markdown("### 📊 Empirical Validation")
            gt_file = st.file_uploader("Upload Human Ratings CSV (Ground Truth)", type=['csv'])
            if gt_file:
                try:
                    gt_df = pd.read_csv(gt_file)
                    
                    # IRR Logic
                    annotator_cols = [c for c in gt_df.columns if 'Annotator' in c or 'Human_Tension' in c]
                    if len(annotator_cols) > 0 and 'Scene' in gt_df.columns:
                        
                        # If multiple annotators, calculate agreement
                        if len(annotator_cols) > 1:
                            st.caption(f"Detected {len(annotator_cols)} annotators. Calculating IRR...")
                            # Simple pairwise correlation as proxy for alpha if >=2 annotators
                            if len(annotator_cols) >= 2:
                                c1, c2 = annotator_cols[0], annotator_cols[1]
                                corr, _ = __import__('scipy').stats.pearsonr(gt_df[c1], gt_df[c2])
                                if corr > 0.70:
                                    st.success(f"High Inter-Rater Reliability ($r$ = {corr:.2f})")
                                else:
                                    st.warning(f"Low Inter-Rater Reliability ($r$ = {corr:.2f}). System comparison may be noisy.")
                            
                            # Average for the chart
                            gt_df['Combined_Human'] = gt_df[annotator_cols].mean(axis=1)
                            y_data = gt_df['Combined_Human']
                        else:
                            y_data = gt_df[annotator_cols[0]]
                            
                        fig.add_trace(go.Scatter(
                            x=gt_df['Scene'],
                            y=y_data,
                            line=dict(color='purple', width=2, dash='dot'),
                            mode='lines+markers',
                            name='Human Ground Truth (Combined)'
                        ))
                    else:
                        st.warning("Ground Truth CSV must contain 'Scene' and at least one 'Human_Tension' or 'Annotator_X' column.")
                except Exception as e:
                    st.error(f"Failed to load Ground Truth: {e}")

            fig.update_layout(
                title='Empirical Signal Trace (High-Fidelity)',
                xaxis_title='Scene Index',
                yaxis_title='Normalized Signal Intensity [0-1]',
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Dynamic X/Y Plotting (Exploratory Data Analysis)
            st.markdown("### 🔍 Exploratory Data Analysis")
            feature_cols = [c for c in df.columns if c not in ['Script_Title']]
            col_x, col_y = st.columns(2)
            with col_x: x_axis = st.selectbox("X-Axis Feature", feature_cols, index=feature_cols.index('Scene') if 'Scene' in feature_cols else 0)
            with col_y: y_axis = st.selectbox("Y-Axis Feature", feature_cols, index=feature_cols.index('Load') if 'Load' in feature_cols else 0)
            
            eda_fig = px.scatter(df, x=x_axis, y=y_axis, hover_data=['Scene'], title=f"{y_axis} vs {x_axis}")
            st.plotly_chart(eda_fig, use_container_width=True)
            
            st.markdown("### All Raw Empirical Data")
            st.dataframe(df)

            # CSV Export for empirical analysis
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Empirical Data (CSV)",
                data=csv,
                file_name="scriptpulse_empirical_data.csv",
                mime="text/csv",
            )
        else:
            # Use Streamlit native chart (simpler, creative abstraction)
            st.line_chart(df[['Scene', 'Load', 'Recovery', 'Net Tension']].set_index('Scene'))
            st.caption("BLUE LINE: Narrative Tension | ORANGE LINE: Breathing Room")
    
    
    # === MAIN LAYOUT: EDITOR + SIGNALS ===
    st.markdown("---")
    
    col_script, col_signals = st.columns([1.6, 1])
    
    # -- LEFT: SCRIPT VIEW --
    with col_script:
        st.subheader("Screenplay Text")
        # Simple text area for now, but configured to look like a script page
        # In a real "v6" app, this would be an indexed HTML component
        st.text_area("Script Reader", value=script_input, height=800, disabled=True, label_visibility="collapsed")
    
    # -- RIGHT: SIGNAL FEEDBACK --
    with col_signals:
        st.subheader("Rhythm Signals")
        
        reflections = report.get('reflections', [])
        silence = report.get('silence_explanation')
        intent_acks = report.get('intent_acknowledgments', [])
        ssf_analysis = report.get('ssf_analysis', {})
        
        if intent_acks:
            for ack in intent_acks:
                st.markdown(f"<div class='signal-box signal-flow'>🎯 {ack}</div>", unsafe_allow_html=True)
        
        # 2. Affective Signals (v6.5 - NEW)
        # Scan trace for high-intensity affective blocks
        # Simple aggregator: separate Anxiety vs Excitement
        if trace:
            # Find peaks (top 10% strain)
            sorted_trace = sorted(trace, key=lambda x: x.get('attentional_signal', 0), reverse=True)
            top_points = sorted_trace[:max(1, len(trace)//10)]
            
            for p in top_points:
                idx = p.get('scene_index', 0)
                affect = p.get('affective_state', 'Intense')
                val = p.get('valence_score', 0.0)
                
                # Only show if not mundane
                if affect in ['Excitement', 'Anxiety', 'Melancholy']:
                    css = "signal-tension"
                    # Signal display code would go here
                
                st.markdown("---")
                
                # Tabs for detailed analysis
                # v10.1: Studio Report Export
                from scriptpulse.reporters import studio_report
                
                # v11.0: Custom Reader Notes
                user_notes = st.sidebar.text_area("Add Reader Notes:", height=100, placeholder="E.g., 'Pass. Dialogue is weak.'")
                
                script_title = uploaded_file.name if uploaded_file and hasattr(uploaded_file, 'name') else "Untitled_Script"
                html_report = studio_report.generate_report(report, script_title=script_title, user_notes=user_notes)
                st.sidebar.download_button(
                    label="Export Producer Report",
                    data=html_report,
                    file_name="script_coverage.html",
                    mime="text/html",
                    help="Downloads a Styled Coverage Report. Open in browser and Print to PDF."
                )
                
                # v14.0: Additional Download Options
                st.sidebar.markdown("---")
                st.sidebar.markdown("### Analysis Tools")
                
                # Save Analysis as JSON
                report_json = json.dumps(report, indent=2, default=str)
                st.sidebar.download_button(
                    label="Save Analysis (JSON)",
                    data=json.dumps(report, indent=2),
                    file_name=f"{script_title}_analysis.json",
                    mime="application/json",
                    help="Download raw analysis data for external processing"
                )
                
                # Reproducibility Export
                st.sidebar.markdown("---")
                st.sidebar.markdown("### Reproducibility")
                import io
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    zip_file.writestr("output.json", json.dumps(report, indent=2))
                    zip_file.writestr("ablation_config.json", json.dumps(ablation_config if 'ablation_config' in locals() else {}, indent=2))
                    try:
                        with open("scriptpulse/config/hyperparameters.json", "r") as f:
                            zip_file.writestr("hyperparameters.json", f.read())
                    except:
                        pass

                st.sidebar.download_button(
                    label="📦 Download Experiment State (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{script_title}_experiment_state.zip",
                    mime="application/zip",
                    help="Reproducible artifact with all outputs and model parameters."
                )
                
                # Debug Details (Collapsed by default - v13.1 Optimization)
                with st.expander("🛠️ Debug Output"):
                    st.json(report.get('debug_export', {}))
                
                # Print Summary
                from scriptpulse.reporters import print_summary
                print_html = print_summary.generate_print_summary(report, script_title=script_title)
                st.sidebar.download_button(
                    label="Print Summary (1-page)",
                    data=print_html,
                    file_name=f"{script_title}_summary.html",
                    mime="text/html",
                    help="Concise printable summary"
                )
                
                # Display scene feedback
                scene_fb = report.get('scene_feedback', {})
                if scene_fb:
                    st.markdown("---")
                    st.markdown("### Scene-Level Notes")
                    count = 0
                    for sc_idx in sorted(scene_fb.keys()):
                        if count >= 5: break  # Show top 5
                        notes = scene_fb[sc_idx]
                        if notes:
                            st.warning(f"**Scene {sc_idx+1}:** {notes[0]['suggestion']}")
                            count += 1
                
        if time.time() - render_start > HARD_RENDER_LIMIT:
             st.warning("⚠️ Report Truncated: Render timeout exceeded.")
             truncated = True
             
        # 3. Reflections (Structure)
        if reflections and not truncated:
             st.markdown("---")
             st.caption("Structural Notes")
             for ref in reflections:
                scene_range = ref.get('scene_range', [0, 0])
                text = ref.get('reflection', '')
                css_class = "signal-tension" 
                if "drift" in text.lower(): css_class = "signal-drift"
                
                label = f"Scenes {scene_range[0]}–{scene_range[1]}"
                st.markdown(f"**{label}**")
                st.markdown(f"<div class='signal-box {css_class}'>{text}</div>", unsafe_allow_html=True)
        
        # 4. Silence / Stability
        elif silence:
             is_stable = ssf_analysis.get('is_silent', False)
             if is_stable:
                 st.markdown(f"<div class='signal-box signal-flow'>✅ <strong>Stable Flow.</strong><br>{silence}</div>", unsafe_allow_html=True)
             else:
                 st.markdown(f"<div class='signal-box'>{silence}</div>", unsafe_allow_html=True)
                 
    # === DOWNLOAD REPORT ===
    st.markdown("---")
    st.download_button(
        label="📄 Download Analysis Report",
        data=str(report),
        file_name="scriptpulse_analysis.txt",
        mime="text/plain"
    )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<div class='disclaimer'>ScriptPulse v6.0 | Confidential & Private Instrument</div>", unsafe_allow_html=True)
