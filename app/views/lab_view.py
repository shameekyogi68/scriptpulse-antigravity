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
    uikit.render_section_header("🔬", "Advanced Diagnostics & Telemetry", 
                                "For the data-driven writer: Dive into the raw mathematical signals driving your pacing and structure.")
    
    # =========================================================================
    # 1. PRIMARY TELEMETRY (METRICS)
    # =========================================================================
    trace = report.get('temporal_trace', [])
    avg_attention = sum(p.get('attentional_signal', 0) for p in trace) / len(trace) if trace else 0
    avg_entropy = sum(report.get('semantic_flux', [0.5]*len(trace))) / len(trace) if report.get('semantic_flux') else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: uikit.render_lab_metric("Mean Attention Signal", f"{avg_attention:.3f}")
    with c2: uikit.render_lab_metric("Mean Semantic Entropy", f"{avg_entropy:.3f}")
    with c3: uikit.render_lab_metric("Target Model Stratum", selected_genre)
    with c4: uikit.render_lab_metric("Scene Array Size", f"n={len(trace)}")

    # =========================================================================
    # 2. XAI TRACE - MULTI-SIGNAL PULSE
    # =========================================================================
    uikit.render_lab_subheading("01", "SIGNAL TRACE ARRAY")
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
    uikit.render_lab_subheading("02", "ACTION VS DIALOGUE DENSITY (ENERGY / ENTROPY)")
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
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {Theme.TEXT_SECONDARY};">
                <p><strong style="color: {Theme.SEMANTIC_CRITICAL};">Q1: CLIMAX DENSITY</strong><br>Intense action, dense exposition.</p>
                <p><strong style="color: {Theme.SEMANTIC_WARNING};">Q2: KINETIC ACTION</strong><br>Fast paced momentum.</p>
                <p><strong style="color: {Theme.SEMANTIC_GOOD};">Q3: RECOVERY</strong><br>Low stakes, high readability.</p>
                <p><strong style="color: {Theme.ACCENT_PRIMARY};">Q4: MYSTERY / SETUP</strong><br>Cognitively demanding.</p>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # 4. DEEP TELEMETRY (RADAR & HEATMAPS)
    # =========================================================================
    uikit.render_lab_subheading("03", "SUB-SYSTEM AUDITS")
    tabs = st.tabs(["[VOICE RADAR]", "[XAI HEATMAP]", "[LITERALISM AUDIT]"])
    
    with tabs[0]:
        voice = report.get('voice_fingerprints', {})
        if voice:
            top_chars = sorted([(k, v) for k, v in voice.items() if isinstance(v, dict)], 
                               key=lambda x: x[1].get('line_count', 0), reverse=True)[:3]
            fig_r = charts.get_voice_radar(top_chars)
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
        else: st.info("Insufficient dialogue nodes.")

    with tabs[2]:
        subtext = report.get('subtext_audit', [])
        if subtext:
            st.markdown(f"<p style='color: {Theme.SEMANTIC_WARNING};'>WARNING: High literalism scores detected.</p>", unsafe_allow_html=True)
            for s in subtext[:5]:
                st.code(f"SCENE_{s.get('scene_index', '?')} -> {s.get('issue', 'Subtext decay.')}")
        else: st.markdown(f"<p style='color: {Theme.SEMANTIC_GOOD};'>OK: Subtext patterns stable.</p>", unsafe_allow_html=True)

    # Export
    uikit.render_lab_subheading("04", "ENVIRONMENT & PAYLOAD")
    st.json(report.get('meta', {}))
    with st.expander("VIEW RAW JSON PAYLOAD ARRAY"): st.json(report)
    if trace:
        csv = pd.DataFrame(trace).to_csv(index=False).encode('utf-8')
        st.download_button("DOWNLOAD TELEMETRY DUMP (CSV)", csv, "lab_telemetry_dump.csv", "text/csv", type="primary", use_container_width=True)
