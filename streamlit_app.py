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

# Ensure we can import the locked pipeline
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse import runner

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

# v13.0: Simple, friendly UI for non-technical writers
st.set_page_config(
    page_title="ScriptPulse - Easy Script Analyzer",
    page_icon="🎬",
    layout="wide"
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
    # v13.0: Friendly, simple title
    st.title("ScriptPulse: Story Analysis Tool")
    st.caption("Upload your script and get instant feedback - no technical knowledge needed!")
    
    # Mode Selection (v10.0: Market Readiness)
    mode = st.sidebar.radio("Analysis Mode", ["Full Script Analysis", "Scene Comparison (A/B)"])
    
    # --- MODE 1: SCENE COMPARISON (A/B) ---
    if mode == "Scene Comparison (A/B)":
        st.header("⚖️ Scene A/B Testing")
        st.caption("Compare two versions of a scene side-by-side to see which hits harder.")
        
        col1, col2 = st.columns(2)
        with col1:
            file_a = st.file_uploader("Upload Version A", key="file_a")
        with col2:
            file_b = st.file_uploader("Upload Version B", key="file_b")
            
        if file_a and file_b:
            if st.button("Compare Versions"):
                # Run lightweight analysis
                import scriptpulse.agents.parsing as p
                import scriptpulse.agents.temporal as t
                import scriptpulse.agents.valence as v
                
                def analyze_snippet(f):
                    txt = f.getvalue().decode('utf-8')
                    parsed = p.run(txt)
                    # Hack: Treat snippets as single scenes
                    scene = {'lines': parsed, 'scene_index': 0}
                    
                    # Manual extraction
                    temp_score = t.calculate_attentional_pulse({'scenes': [scene]})[0]
                    val_score = v.run({'scenes': [scene]})[0]
                    return temp_score, val_score, len(parsed)
                    
                t_a, v_a, len_a = analyze_snippet(file_a)
                t_b, v_b, len_b = analyze_snippet(file_b)
                
                # Display Results
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Cognitive Load (Effort)", f"{t_a['attentional_signal']:.2f}", 
                             delta=f"{t_a['attentional_signal'] - t_b['attentional_signal']:.2f} vs B")
                    st.metric("Emotional Impact (Valence)", f"{v_a:.2f}")
                    st.subheader("Version A")
                
                with c2:
                    st.metric("Cognitive Load (Effort)", f"{t_b['attentional_signal']:.2f}",
                             delta=f"{t_b['attentional_signal'] - t_a['attentional_signal']:.2f} vs A")
                    st.metric("Emotional Impact (Valence)", f"{v_b:.2f}")
                    st.subheader("Version B")
                    
        st.stop() # Stop here so we don't render the main app
        
    # --- MODE 2: FULL ANALYSIS (The Original App) ---
    
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
        file_ext = uploaded_file.name.split('.')[-1].lower()

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
            st.markdown("### 💡 Creative Repair Strategies (Mixed-Initiative)")
            for sugg in repair_strategies:
                # Ensure sugg is a dict
                if isinstance(sugg, dict):
                    scene_num = sugg.get('scene', 'Unknown')
                    diagnosis = sugg.get('diagnosis', 'No diagnosis')
                    with st.expander(f"Scene {scene_num}: {diagnosis}", expanded=True):
                        st.markdown(f"**Strategy:** {sugg.get('strategy', 'N/A')}")
                        for tactic in sugg.get('tactics', []):
                            st.markdown(f"- {tactic}")
                    
                    
    # === DEEP ANALYSIS & ETHICS (Tabs) ===
    st.markdown("### 🔬 Deep Insights")
    # v13.0: Simplified tab names
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Quick Summary",
        "Character Details",
        "Bias Check",
        "Compare to Classics",
        "Writing Tips"
    ])
    
    with tab1:
        # xai_attribution is a LIST of dicts (one per scene)
        xai_attribution = report.get('xai_attribution', [])
        
        if xai_attribution and len(xai_attribution) > 0:
            # Show overall dominant driver (from first scene or aggregate)
            first_scene_xai = xai_attribution[0] if isinstance(xai_attribution[0], dict) else {}
            dominant_driver = first_scene_xai.get('dominant_driver', 'Unknown')
            
            st.markdown(f"**Primary Driver:** {dominant_driver.title() if isinstance(dominant_driver, str) else 'Unknown'}")
            
            # Show driver breakdown (from first scene)
            drivers = first_scene_xai.get('drivers', {})
            if drivers:
                st.caption("Contribution breakdown:")
                for driver, pct in drivers.items():
                    st.progress(pct, text=f"{driver}: {int(pct*100)}%")
            
        # v10.1: Voice Distinctiveness Map
        voice_data = report.get('voice_fingerprints', {})
        if voice_data:
            st.markdown("---")
            st.subheader("🗣️ Character Voice Map")
            st.caption("Are your characters distinct? Overlapping dots = 'Same Voice' problem.")
            
            # Prepare Data for Scatter Plot
            # Streamlit scatter_chart is simple, lets use Vega-Lite via st.vega_lite_chart or just st.scatter_chart
            # st.scatter_chart takes a DF with x, y, color, size
            
            v_data = []
            for char, metrics in voice_data.items():
                v_data.append({
                    'Character': char,
                    'Complexity (Intellect)': metrics['complexity'],
                    'Positivity (Tone)': metrics['positivity'],
                    'Agency (Active Verbs)': metrics['agency'] * 100, # Scale for size
                    'Lines': metrics['line_count']
                })
            
            if v_data:
                df_voice = pd.DataFrame(v_data)
                st.scatter_chart(
                    df_voice,
                    x='Complexity (Intellect)',
                    y='Positivity (Tone)',
                    size='Agency (Active Verbs)',
                    color='Character',
                )
            else:
                st.info("Not enough dialogue for Voice Analysis.")
            
            # v13.0: Character Arc Tracking (Growth Over Time)
            st.markdown("---")
            st.subheader("📈 Character Growth Tracker")
            st.caption("Do your characters evolve? This shows if they become more confident/active over the story.")
            
            voice_map = report.get('voice_fingerprints', {})
            if voice_map and len(report['scenes']) > 6:  # Need enough scenes for acts
                # Divide script into 3 acts
                num_scenes = len(report['scenes'])
                act1_end = num_scenes // 3
                act2_end = 2 * num_scenes // 3
                
                # Calculate agency per act for each character
                char_arcs = {}
                for char, profile in voice_map.items():
                    if profile['line_count'] < 5:  # Skip minor characters
                        continue
                    
                    # Get agency scores per scene
                    scenes = report['scenes']
                    act1_agency = []
                    act2_agency = []
                    act3_agency = []
                    
                    for i, scene in enumerate(scenes):
                        # Check if character speaks in this scene
                        char_in_scene = any(
                            line.get('tag') == 'C' and char in line.get('text', '')
                            for line in scene['lines']
                        )
                        if not char_in_scene:
                            continue
                            
                        # Use valence as proxy for "agency" (positive = active)
                        val_scores = report.get('valence_scores', [])
                        if i < len(val_scores):
                            if i < act1_end:
                                act1_agency.append(val_scores[i])
                            elif i < act2_end:
                                act2_agency.append(val_scores[i])
                            else:
                                act3_agency.append(val_scores[i])
                    
                    if act1_agency and act3_agency:
                        char_arcs[char] = {
                            'Act 1': sum(act1_agency) / len(act1_agency) if act1_agency else 0,
                            'Act 2': sum(act2_agency) / len(act2_agency) if act2_agency else 0,
                            'Act 3': sum(act3_agency) / len(act3_agency) if act3_agency else 0
                        }
                
                if char_arcs:
                    # Show as simple line chart
                    import pandas as pd
                    arc_df = pd.DataFrame(char_arcs).T
                    st.line_chart(arc_df)
                    
                    # Interpret
                    for char, scores in char_arcs.items():
                        trend = scores['Act 3'] - scores['Act 1']
                        if trend > 0.1:
                            st.success(f"✅ **{char}** grows more confident/positive (↗️ +{trend:.2f})")
                        elif trend < -0.1:
                            st.warning(f"⚠️ **{char}** becomes more negative/passive (↘️ {trend:.2f})")
                        else:
                            st.info(f"➡️ **{char}** stays consistent")
                else:
                    st.info("Not enough data to track character arcs.")
            
            # v11.0: Interaction Heatmap (Chemistry)
            interaction_map = report.get('interaction_map', {})
            # Need to compute Valence for pairs
            # Map: "A|B" -> [idx, idx]
            # Valence: report['valence_scores'][idx]
            
            if interaction_map:
                st.markdown("---")
                st.subheader("💞 Interaction Chemistry (Heatmap)")
                st.caption("How positive/negative are key relationships? (Red = Conflict, Blue = Bonding)")
                
                val_scores = report.get('valence_scores', [])
                chem_data = []
                
                for pair, indices in interaction_map.items():
                    if len(indices) < 2: continue # Ignore brief encounters
                    
                    # Calculate Avg Valence for this Pair
                    pair_vals = [val_scores[i] for i in indices if i < len(val_scores)]
                    if not pair_vals: continue
                    
                    avg_val = sum(pair_vals) / len(pair_vals)
                    c1, c2 = pair.split('|')
                    chem_data.append({'Char A': c1, 'Char B': c2, 'Chemistry': avg_val})
                    # Add symmetric for full matrix
                    chem_data.append({'Char A': c2, 'Char B': c1, 'Chemistry': avg_val})
                    
                if chem_data:
                    df_chem = pd.DataFrame(chem_data)
                    # Pivot to matrix
                    matrix = df_chem.pivot(index='Char A', columns='Char B', values='Chemistry').fillna(0)
                    st.dataframe(matrix.style.background_gradient(cmap='coolwarm', vmin=-0.5, vmax=0.5))
                else:
                    st.info("No significant character interactions found.")
            
    with tab2:
        macro = report.get('macro_structure_fidelity', {})
        if macro:
            best_fit = macro.get('best_fit_template', 'Unknown')
            score = macro.get('fidelity_score', 0.0)
            st.metric("Structure Fidelity Score", f"{macro.get('fidelity_score', 0)}%")
            st.caption("Adherence to standard 3-Act structure (Setup, Confrontation, Resolution).")
            
        # v10.1: Act Sequence Analysis
        st.markdown("### 🎬 Act Sequence Analysis")
        trace = report.get('temporal_trace', [])
        if len(trace) > 10:
            n = len(trace)
            act1_end = int(n * 0.25)
            act2_end = int(n * 0.75)
            
            acts = {
                "Act 1 (Setup)": trace[:act1_end],
                "Act 2 (Confrontation)": trace[act1_end:act2_end],
                "Act 3 (Resolution)": trace[act2_end:]
            }
            
            act_data = []
            for name, scenes in acts.items():
                if not scenes: continue
                avg_t = sum(s.get('attentional_signal', 0) for s in scenes) / len(scenes) if scenes else 0
                valence_scores = report.get('valence_scores', [])
                avg_v = sum(valence_scores[s['scene_index']] for s in scenes if s.get('scene_index', 0) < len(valence_scores)) / len(scenes) if scenes and valence_scores else 0
                act_data.append({
                    "Act": name,
                    "Avg Tension": avg_t,
                    "Avg Valence": avg_v,
                    "Scenes": len(scenes)
                })
                
            st.table(pd.DataFrame(act_data).set_index("Act").style.highlight_max(axis=0))
        else:
            st.info("Script too short for Act Analysis.")
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
            
    with tab4: # COMPARATIVE BENCHMARK (v9.0)
        # Main Pulse Chart
        st.subheader("📈 Cognitive Intensity Over Time")
        
        # v12.0: Benchmark Overlay
        benchmark_options = ["None", "Linear Rise", "Three-Act", "Hero's Journey"]
        selected_benchmark = st.selectbox("Compare to Classic:", benchmark_options, help="Overlay your script against classic narrative structures")
        
        chart_data = pd.DataFrame({
            'Your Script': [p.get('attentional_signal', 0) for p in report.get('temporal_trace', [])]
        })
        
        if selected_benchmark != "None":
            # Simple benchmark patterns
            n = len(chart_data)
            if selected_benchmark == "Linear Rise":
                chart_data['Classic Pattern'] = [i/n for i in range(n)]
            elif selected_benchmark == "Three-Act":
                chart_data['Classic Pattern'] = [0.3 if i < n*0.25 else 0.7 if i < n*0.75 else 0.9 for i in range(n)]
            elif selected_benchmark == "Hero's Journey":
                # This pattern is a simplified example, ensure it matches the length of chart_data
                hero_pattern = [0.2, 0.4, 0.5, 0.3, 0.6, 0.8, 0.9, 0.7, 0.5]
                chart_data['Classic Pattern'] = (hero_pattern * (n // len(hero_pattern) + 1))[:n]
            
        st.line_chart(chart_data)
        
        # v12.0: Visual Beat Board (Index Card View)
        st.markdown("---")
        st.subheader("🗂️ Visual Beat Board")
        st.caption("Your script as Index Cards. Color = Tension (Red=Intense, Gray=Calm)")
        
        # Create cards
        trace = report.get('temporal_trace', [])
        cols_per_row = 5
        for row_start in range(0, len(trace), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx >= len(trace):
                    break
                    
                point = trace[idx]
                tension = point.get('attentional_signal', 0)
                state = point.get('affective_state', 'Normal')
                
                # Color mapping
                if tension > 0.8:
                    color = "#ff4444"  # Red
                elif tension > 0.6:
                    color = "#ff9944"  # Orange
                elif tension > 0.4:
                    color = "#ffdd44"  # Yellow
                else:
                    color = "#dddddd"  # Gray
                    
                # Emoji for state
                emoji = "🔥" if state == "Anxiety" else "😐" if state == "Normal" else "🔵"
                
                with col:
                    st.markdown(
                        f"""
                        <div style="background: {color}; padding: 10px; border-radius: 5px; margin: 5px 0; min-height: 80px; border: 2px solid #333;">
                            <div style="font-weight: bold; font-size: 11px;">Scene {idx+1} {emoji}</div>
                            <div style="font-size: 10px; color: #333;">Tension: {tension:.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        st.markdown("---")
        # New v9.1 Comparison: Hybrid NLP vs Heuristic
        flux = report.get('semantic_flux', [])
        if flux:
            st.markdown("---")
            st.markdown("**2. Focus & Coherence Check**")
            st.caption("Comparision of 'Thematic Focus' (Blue) vs 'Structural Coherence' (Red).")
            
            # Get Coherence scores from trace
            coherence_vals = [p.get('coherence_penalty', 0.0) for p in report.get('temporal_trace', [])]
            
            min_len_flux = min(len(flux), len(coherence_vals))
            
            flux_chart = pd.DataFrame({
                'Thematic Shift (Topic Change)': flux[:min_len_flux],
                'Disorientation Risk (Coherence)': coherence_vals[:min_len_flux]
            })
            st.area_chart(flux_chart)

    with tab5: # HCI / Comparator
        import sys 
        if 'comparator' in sys.modules:
            pass 
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
        
        # Use Streamlit native chart (simpler, no altair dependency)
        st.line_chart(df.set_index('Scene'))
        
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
                
                
                # v13.0: Simple Summary Card (Non-Technical)
                st.markdown("---")
                st.markdown("## 📋 Your Script in 3 Numbers")
                
                col1, col2, col3 = st.columns(3)
                
                # Calculate simple metrics
                trace = report.get('temporal_trace', [])
                avg_intensity = sum(p.get('attentional_signal', 0) for p in trace) / len(trace) if trace else 0
                intensity_score = int(avg_intensity * 10)  # 0-10 scale
                
                valence_scores = report.get('valence_scores', [])
                avg_valence = sum(valence_scores) / len(valence_scores) if valence_scores else 0
                
                runtime_info = report.get('runtime_estimate', {})
                runtime_text = f"~{runtime_info.get('avg_minutes', 0)} minutes"
                
                with col1:
                    st.metric(
                        "Story Intensity", 
                        f"{intensity_score}/10",
                        help="How gripping your story is. Higher = more intense."
                    )
                    
                with col2:
                    if avg_valence > 0.1:
                        emotion = "Happy 😊"
                    elif avg_valence < -0.1:
                        emotion = "Serious 😐"
                    else:
                        emotion = "Balanced ⚖️"
                    st.metric(
                        "Overall Tone",
                        emotion,
                        help="The general feeling of your script."
                    )
                    
                with col3:
                    st.metric(
                        "Estimated Length",
                        runtime_text,
                        help="How long your movie will be."
                    )
                
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
                    data=report_json,
                    file_name=f"{uploaded_file.name}_analysis.json",
                    mime="application/json",
                    help="Save analysis to resume later"
                )
                
                # Print Summary
                from scriptpulse.reporters import print_summary
                print_html = print_summary.generate_print_summary(report, script_title=uploaded_file.name)
                st.sidebar.download_button(
                    label="Print Summary (1-page)",
                    data=print_html,
                    file_name=f"{uploaded_file.name}_summary.html",
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
