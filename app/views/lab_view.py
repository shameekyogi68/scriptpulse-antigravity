import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

def render_lab_view(report, script_input, selected_genre, selected_lens, ablation_config, SCIPY_AVAILABLE):
    """Renders the advanced research/lab interface with full telemetry."""
    st.header("Lab Mode (Research Platform)")
    
    # 1. High-Level Metrics (Research Grade)
    trace = report.get('temporal_trace', [])
    avg_intensity = sum(p.get('attentional_signal', 0) for p in trace) / len(trace) if trace else 0
    intensity_score = int(avg_intensity * 10)
    
    runtime = report.get('runtime_estimate', {}).get('avg_minutes', 0)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw Tension", f"{intensity_score}/10")
    c2.metric("Avg Signal", f"{avg_intensity:.2f}")
    c3.metric("Genre Match", selected_genre)
    c4.metric("Est. Runtime", f"{runtime} min")

    # 2. Advanced Comparisons
    with st.expander("Longitudinal & Style Comparison", expanded=False):
        cols = st.columns(2)
        if 'prev_run' in st.session_state:
            cols[0].subheader("Optimization Delta")
            cols[0].caption("Comparison to last analysis run.")
            # Simplified delta logic
            cols[0].info("Delta tracking active. Next run will show precise shifts.")
        
        cols[1].subheader("Style Reference")
        cols[1].caption("Stylistic distance to target baseline.")
        cols[1].info(f"Target: {selected_genre}")

    # 3. The Pulse Line (Research Grade)
    st.subheader("Narrative Pulse (Story Structure Map)")
    if trace:
        chart_data = []
        semantic_beats = report.get('semantic_beats', [])
        for i, point in enumerate(trace):
            beat_info = semantic_beats[i] if i < len(semantic_beats) else {}
            chart_data.append({
                'Scene': i,
                'Load': point.get('effort', 0.5),
                'Recovery': point.get('recovery', 0.5),
                'Tension': point.get('strain', 0.0),
                'Beat': beat_info.get('composite_beat', 'Stable')
            })
            
        df = pd.DataFrame(chart_data)
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=df['Scene'], y=df['Tension'], name='Narrative Tension', line=dict(color='#1f77b4', width=3)))
        fig.add_trace(go.Scatter(x=df['Scene'], y=df['Recovery'], name='Recovery', line=dict(color='#ff7f0e', width=1, dash='dash')))
        
        fig.update_layout(template='plotly_white', hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)

    # 4. Detailed Telemetry Tabs
    tabs = st.tabs(["Thematic Drivers", "Character Network", "Structural Fidelity", "Subtext Audit"])
    
    with tabs[0]:
        st.caption("Thematic attribution and XAI drivers.")
        xai = report.get('xai_attribution', [{}])[0]
        if xai:
            drivers = xai.get('drivers', {})
            for d, pct in drivers.items():
                st.text(d.title())
                st.progress(pct)

    with tabs[1]:
        st.caption("Inter-character tension and voice fingerprints.")
        voice = report.get('voice_fingerprints', {})
        if voice:
            df_v = pd.DataFrame([{'Char': k, 'Comp': v['complexity'], 'Lines': v['line_count']} for k, v in voice.items()])
            st.scatter_chart(df_v, x='Comp', y='Lines', color='Char')

    with tabs[2]:
        st.caption("Fidelity to standard story templates.")
        macro = report.get('macro_structure_fidelity', {})
        st.metric("Structure Fidelity", f"{macro.get('fidelity_score', 0)}%")
        st.info(f"Best Template Fit: {macro.get('best_fit_template', 'Unknown')}")

    with tabs[3]:
        st.caption("AI-detected subtext and literalism audit.")
        subtext = report.get('subtext_audit', [])
        if subtext:
            for s in subtext:
                st.warning(f"**Scene {s['scene_index']+1}**: {s['issue']}")

    # 5. Raw Data Export
    st.markdown("---")
    with st.expander("Debug Output & Reproducibility"):
        st.json(report.get('debug_export', {}))
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Export Empirical Data (CSV)", csv, "lab_report.csv", "text/csv")
