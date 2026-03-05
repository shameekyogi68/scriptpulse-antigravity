import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts

def render_lab_view(report, script_input, selected_genre, selected_lens, ablation_config, SCIPY_AVAILABLE):
    """
    Renders the advanced view with detailed breakdowns.
    Provides deeper insight for producers and advanced writers.
    """
    # uikit.render_lab_pipeline_header() # Removed so it flows naturally
    uikit.render_section_header("🔬", "Under the Hood (Advanced View)", 
                                "This section breaks down the individual forces driving your script's pacing — tension, effort, and recovery — so you can see exactly what's happening beneath the surface.")
    
    # =========================================================================
    # 1. KEY NUMBERS
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
    # 2. THREE FORCES BREAKDOWN
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
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="lab_three_forces_chart")

    # =========================================================================
    # 3. SCENE DATA & VOICES
    # =========================================================================
    uikit.render_lab_subheading("02", "CRAFT DATA")
    tabs = st.tabs(["🎭 Character Voices", "📊 Full Data", "📝 Writing Style Check"])
    
    with tabs[0]:
        voice = report.get('voice_fingerprints', {})
        if voice:
            st.caption("💡 This radar shows how your top characters 'sound' differently. A bigger shape means the character is more active in that area.")
            top_chars = sorted([(k, v) for k, v in voice.items() if isinstance(v, dict)], 
                               key=lambda x: x[1].get('line_count', 0), reverse=True)[:3]
            fig_r = charts.get_voice_radar(top_chars)
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False}, key="lab_voice_radar_chart")
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

