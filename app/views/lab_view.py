import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts

def render_lab_view(report, script_input, selected_genre, selected_lens, ablation_config, SCIPY_AVAILABLE):
    """
    Renders the advanced research/lab interface with full telemetry.
    Designed for data scientists, producers, and advanced analysts.
    """
    # uikit.render_lab_pipeline_header() # Removed so it flows naturally
    uikit.render_section_header("🔬", "Under the Hood (Advanced View)", 
                                "This section breaks down the individual forces driving your script's pacing — tension, effort, and recovery — so you can see exactly what's happening beneath the surface.")
    
    # =========================================================================
    # 1. PRIMARY TELEMETRY (METRICS)
    # =========================================================================
    trace = report.get('temporal_trace', [])
    avg_attention = sum(p.get('attentional_signal', 0) for p in trace) / len(trace) if trace else 0
    avg_entropy = sum(report.get('semantic_flux', [0.5]*len(trace))) / len(trace) if report.get('semantic_flux') else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: uikit.render_lab_metric("Average Intensity", f"{avg_attention:.0%}")
    with c2: uikit.render_lab_metric("Language Richness", f"{avg_entropy:.0%}")
    with c3: uikit.render_lab_metric("Genre", selected_genre)
    with c4: uikit.render_lab_metric("Total Scenes", f"{len(trace)}")

    # =========================================================================
    # 2. XAI TRACE - MULTI-SIGNAL PULSE
    # =========================================================================
    uikit.render_lab_subheading("01", "THE THREE FORCES (Tension • Effort • Recovery)")
    st.caption("💡 This chart splits your main graph into its three ingredients: 🟥 **Tension** (conflict/stakes), 🟧 **Mental Effort** (how hard the reader works), and 🟩 **Recovery** (moments of calm). The purple area is the overall combination.")
    if trace:
        df = pd.DataFrame([{
            'T_Index': i+1,
            'Load_Effort': p.get('effort', 0.5),
            'Recovery_Valence': p.get('recovery', 0.5),
            'Strain_Tension': p.get('strain', 0.0),
            'Composite_Attention': p.get('attentional_signal', 0.5)
        } for i, p in enumerate(trace)])
        
        fig = charts.get_lab_trace_chart(df)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # =========================================================================
    # 3. KINEMATIC ACTION VS DIALOGUE DENSITY (Energy vs Entropy)
    # =========================================================================
    uikit.render_lab_subheading("02", "SCENE MAP: INTENSITY vs COMPLEXITY")
    st.caption("💡 Each dot is a scene in your script. This map shows if a scene is fast-paced (top) or slow (bottom), and if the language is dense/complex (right) or simple/minimal (left).")
    if trace:
        col_ps1, col_ps2 = st.columns([3, 1])
        df_q = pd.DataFrame([{
            'T_Index': i+1,
            'Energy_Signal': s.get('attentional_signal', 0.5),
            'Entropy_Complexity': report.get('semantic_flux', [0.5]*len(trace))[i],
            'Quadrant': 'Q1' if s.get('attentional_signal', 0.5) > 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] > 0.5 else
                        'Q2' if s.get('attentional_signal', 0.5) > 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] <= 0.5 else
                        'Q3' if s.get('attentional_signal', 0.5) <= 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] <= 0.5 else 'Q4'
        } for i, s in enumerate(trace)])
        
        with col_ps1:
            fig_q = charts.get_phase_space_chart(df_q)
            st.plotly_chart(fig_q, use_container_width=True, config={'displayModeBar': False})
            
        with col_ps2:
            st.markdown(f"""
            <div style="font-size: 12px; color: {Theme.TEXT_SECONDARY}; line-height: 1.8;">
                <p><strong style="color: {Theme.SEMANTIC_CRITICAL};">Top-Right: CLIMAX</strong><br>Fast-paced AND complex — the most demanding scenes for the reader.</p>
                <p><strong style="color: {Theme.SEMANTIC_WARNING};">Top-Left: ACTION</strong><br>Fast-paced but simple language — chase scenes, fights, quick dialogue.</p>
                <p><strong style="color: {Theme.SEMANTIC_GOOD};">Bottom-Left: BREATHER</strong><br>Slow and simple — quiet recovery moments.</p>
                <p><strong style="color: {Theme.ACCENT_PRIMARY};">Bottom-Right: MYSTERY</strong><br>Slow but complex — exposition, reveals, layered dialogue.</p>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # 4. DEEP TELEMETRY (RADAR & HEATMAPS)
    # =========================================================================
    uikit.render_lab_subheading("03", "DEEP DIVES")
    tabs = st.tabs(["🎭 Character Voices", "📊 Full Data", "📝 Writing Style Check"])
    
    with tabs[0]:
        voice = report.get('voice_fingerprints', {})
        if voice:
            st.caption("💡 This radar shows how your top characters 'sound' differently. A bigger shape means the character is more active in that area.")
            top_chars = sorted([(k, v) for k, v in voice.items() if isinstance(v, dict)], 
                               key=lambda x: x[1].get('line_count', 0), reverse=True)[:3]
            fig_r = charts.get_voice_radar(top_chars)
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
        else: st.info("Not enough dialogue detected to compare character voices.")

    with tabs[1]:
        st.caption("💡 The raw data behind your analysis. Useful for exporting or studying the numbers yourself.")
        st.json(report.get('meta', {}))
        with st.expander("📂 View Complete Raw Data"): st.json(report)
        if trace:
            csv = pd.DataFrame(trace).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download All Scene Data (CSV)", csv, "scriptpulse_scene_data.csv", "text/csv", type="primary", use_container_width=True)

    with tabs[2]:
        subtext = report.get('subtext_audit', [])
        if subtext:
            st.markdown(f"<p style='color: {Theme.SEMANTIC_WARNING};'>Some dialogue may be too 'on-the-nose' — characters are saying exactly what they mean with no subtext.</p>", unsafe_allow_html=True)
            for s in subtext[:5]:
                st.code(f"Scene {s.get('scene_index', '?')}: {s.get('issue', 'Dialogue feels too literal.')}")
        else: st.markdown(f"<p style='color: {Theme.SEMANTIC_GOOD};'>✅ Your dialogue has good layers of subtext. Characters aren't being too literal.</p>", unsafe_allow_html=True)

