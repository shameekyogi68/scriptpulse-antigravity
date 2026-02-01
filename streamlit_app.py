#!/usr/bin/env python3
"""
ScriptPulse v6.0 - The Creative Instrument
Writer-Native Visual Interface
"""

import streamlit as st
import sys
import os
import pandas as pd
import altair as alt
import time

# Ensure we can import the locked pipeline
sys.path.append(os.getcwd())
try:
    from scriptpulse import runner
except ImportError:
    st.error("System Error: ScriptPulse core modules not found. Ensure you are running from the root directory.")
    st.stop()

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ScriptPulse Instrument",
    page_icon="🎼", # Musical score / Instrument icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# THEME & STYLING (The "Premium Instrument" Look)
# =============================================================================

st.markdown("""
<style>
    /* Clean, distraction-free typography */
    body { font-family: 'Inter', sans-serif; }
    
    /* Hide Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Signal Boxes - Writer Native Colors */
    .signal-box {
        padding: 15px;
        border-left: 4px solid;
        background-color: #f8f9fa; /* Light grey base */
        border-radius: 4px;
        margin-bottom: 15px;
        color: #1a1a1a;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Tension / Demand (Red/Orange) */
    .signal-tension { border-color: #FF4B4B; }
    
    /* Drift / Loss of Grip (Yellow/Amber) */
    .signal-drift { border-color: #FFA500; }
    
    /* Stability / Flow (Green/Teal) */
    .signal-flow { border-color: #00CC66; background-color: #e8f5e9; }

    /* AFFECTIVE STATES (v6.5) */
    /* Excitement (High Arousal + Pos Valence) -> Purple/Blue */
    .signal-excitement { border-color: #8A2BE2; background-color: #f3e5f5; }
    
    /* Anxiety (High Arousal + Neg Valence) -> Red (Standard) */
    .signal-anxiety { border-color: #FF4B4B; background-color: #ffebee; }
    
    /* Melancholy (Low Arousal + Neg Valence) -> Grey/Blue */
    .signal-melancholy { border-color: #607D8B; background-color: #eceff1; }
    
    /* Script Editor View (Monospace) */
    .script-view {
        font-family: 'Courier Prime', 'Courier New', monospace;
        background-color: #ffffff;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 4px;
        color: #333;
        white-space: pre-wrap;
        height: 600px;
        overflow-y: auto;
    }
    
    /* Footer Disclaimer */
    .disclaimer {
        font-size: 0.8em;
        color: #888;
        margin-top: 50px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR: ORIENTATION
# =============================================================================

with st.sidebar:
    st.title("ScriptPulse")
    st.caption("v6.0 Instrument Mode")
    
    st.info(
        "**The Pulse Line**\n"
        "Visualize the rhythmic heartbeat of your story. "
        "See where attention tightens, and where it releases."
    )
    
    st.markdown("---")
    st.markdown("**How to Read Signals**")
    
    st.markdown("🔴 **Tension / Demand**")
    st.caption("High effort. The audience is working hard.")
    
    st.markdown("🟠 **Drift / Risk**")
    st.caption("Pacing softens. Grip may loosen.")
    
    st.markdown("🟢 **Flow / Stability**")
    st.caption("Effort and recovery are balanced.")
    
    st.markdown("---")
    st.markdown("**Research Controls**")
    ref_file = st.file_uploader("Upload Target (Reference)", type=['txt', 'pdf'], help="Compare against a gold standard (e.g. Pulp Fiction).")

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
        if uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_parts = [page.extract_text() for page in pdf_reader.pages]
            script_input = "\n".join(text_parts)
        else:
            script_input = uploaded_file.read().decode('utf-8')
            
        # IMMEDIATE PARSE (For Scene Picker)
        with st.spinner("Parsing structure..."):
            scene_list = runner.parse_structure(script_input)
            
        st.success(f"Loaded {len(scene_list)} scenes.")
        
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
    selected_genre = st.selectbox(
        "Genre Context (Adapts Thresholds)",
        ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Family"],
        help="Adjusts fatigue tolerance based on genre expectations."
    )

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

if script_input and st.button("Analyze Rhythm", type="primary"):
    
    # Run Pipeline
    status = st.empty()
    bar = st.progress(0)
    
    status.text("Modeling adaptive attention...")
    bar.progress(30)
    
    start_time = time.time()
    report = runner.run_pipeline(
        script_input, 
        writer_intent=writer_intent,
        lens=selected_lens,
        genre=selected_genre,
        audience_profile=selected_profile,
        high_res_mode=use_high_res # NEW v7.0
    )
    bar.progress(100)
    bar.progress(100)
    # === BIOMETRIC VALIDATION LAB (v7.0) ===
    # Only show if not high res? Or both?
    try:
        from research import biometrics
        import pandas as pd # Added import for pandas
        with st.expander("🧪 Biometric Validation Lab (Empirical)", expanded=False):
            bio_file = st.file_uploader("Import Physiological Data (CSV)", type=['csv'], help="Columns: Time, HeartRate/GSR")
            if bio_file:
                # Mock parsing of CSV for Demo
                # Ideally: pd.read_csv -> clean -> list of floats
                try:
                    df_bio = pd.read_csv(bio_file)
                    # Assume first numeric col is data
                    numeric_cols = df_bio.select_dtypes(include=['float', 'int']).columns
                    if len(numeric_cols) > 0:
                        real_data = df_bio[numeric_cols[0]].tolist()
                        sim_trace = report.get('temporal_trace', [])
                        
                        r_score = biometrics.correlate_biometrics(sim_trace, real_data)
                        
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            st.metric("Pearson Correlation", f"{r_score:.3f}")
                        with b_col2:
                            if r_score > 0.7:
                                st.success("Strong Validation (Scientific Proof)")
                            elif r_score > 0.4:
                                st.info("Moderate Validation")
                            else:
                                st.warning("Weak Correlation (Model Mismatch)")
                                
                        # Plot Overlay? (Future)
                    else:
                        st.error("CSV has no numeric data.")
                except Exception as e:
                    st.error(f"Bio Data Error: {e}")
            else:
                 st.info("Upload real human heart-rate data to validate this trace.")
                 
    except ImportError:
        pass
    
    status.empty()
    bar.empty()
    
    # === RESEARCH COMPARISONS (HCI Layer) ===
    if comparator:
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
    suggestions = report.get('suggestions', [])
    if suggestions:
        st.markdown("### 💡 Creative Repair Strategies (Mixed-Initiative)")
        for sugg in suggestions:
            with st.expander(f"Scene {sugg['scene']}: {sugg['diagnosis']}", expanded=True):
                st.markdown(f"**Strategy:** {sugg['strategy']}")
                for tactic in sugg.get('tactics', []):
                    st.markdown(f"- {tactic}")
                    
    # === DEEP ANALYSIS & ETHICS (Tabs) ===
    st.markdown("### 🔬 Deep Research Metrics")
    tab1, tab2, tab3, tab4 = st.tabs(["Explainability (XAI)", "Macro-Structure", "Algorithmic Fairness", "HCI Validation"])
    
    with tab1:
        xai_data = report.get('xai_attribution', {})
        if xai_data:
            st.markdown(f"**Dominant Driver:** {xai_data.get('dominant_driver', 'Unknown').title()}")
            # Simple bar chart of attribution
            attr = xai_data.get('attribution', {})
            st.bar_chart(attr)
            
    with tab2:
        macro = report.get('macro_structure_fidelity', {})
        if macro:
            best_fit = macro.get('best_fit_template', 'Unknown')
            score = macro.get('fidelity_score', 0.0)
            st.metric("Narrative Arc Match", best_fit, delta=f"{score*100:.1f}% Fidelity")
            
    with tab3: # FAIRNESS AUDIT (v8.0)
        fairness = report.get('fairness_audit', {})
        risks = fairness.get('stereotyping_risks', [])
        
        if risks:
            st.error("⚠️ Algorithmic Fairness Warnings")
            for r in risks:
                st.write(f"- {r}")
        else:
            st.success("No Significant Stereotyping Risks Detected.")
            
        stats = fairness.get('representation_stats', {})
        if stats:
            st.caption("Character Representation Stats")
            st.dataframe(stats)
            
    with tab4: # HCI / Comparator
        import sys # Added for sys.modules check
        if 'comparator' in sys.modules:
            pass # Already handled above or placeholder for more rigorous stats
        st.info("Longitudinal tracking active in sidebar.")
    
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
                'Net Tension': point.get('strain', 0.0) # S[i]
            })
            
        df = pd.DataFrame(chart_data)
        
        # Create Layered Chart
        # Base
        base = alt.Chart(df).encode(x='Scene')
        
        # Area: Net Tension (Red Gradient)
        tension_area = base.mark_area(
            color='red', 
            opacity=0.3, 
            line={'color':'darkred'}
        ).encode(
            y=alt.Y('Net Tension', title='Attentional Load'),
            tooltip=['Scene', 'Net Tension']
        )
        
        # Line: Recovery (Blue)
        recovery_line = base.mark_line(color='#00CC66').encode(
            y='Recovery'
        )
        
        chart = (tension_area + recovery_line).properties(
            height=250,
            width='container'
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        st.caption("RED AREA: Net Tension (Accumulated Strain) | GREEN LINE: Recovery Opportunities")
    
    
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
            sorted_trace = sorted(trace, key=lambda x: x['attentional_signal'], reverse=True)
            top_points = sorted_trace[:max(1, len(trace)//10)]
            
            for p in top_points:
                idx = p['scene_index']
                affect = p.get('affective_state', 'Intense')
                val = p.get('valence_score', 0.0)
                
                # Only show if not mundane
                if affect in ['Excitement', 'Anxiety', 'Melancholy']:
                   css = "signal-tension"
                   emoji = "🔴"
                   if affect == 'Excitement': 
                       css = "signal-excitement"
                       emoji = "🟣"
                   elif affect == 'Anxiety':
                       css = "signal-anxiety"
                       emoji = "🔴"
                   elif affect == 'Melancholy':
                       css = "signal-melancholy"
                       emoji = "🔵"
                       
                   msg = f"{emoji} **Scene {idx}**: {affect.upper()} (Valence: {val})"
                   # Deduplicate: simple check if we already showed this index or similar?
                   # For now, just show top 3 distinct
                   st.markdown(f"<div class='signal-box {css}'>{msg}</div>", unsafe_allow_html=True)

        # 3. Reflections (Structure)
        if reflections:
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
