"""
ScriptPulse — Unified Dashboard View
Product-Grade UI: Persona-Responsive Layout.
"""
import streamlit as st
import pandas as pd
import random
import os
import json
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts


def render_writer_view(report, script_input, genre="Drama", lens="Story Editor"):
    """
    Renders the complete ScriptPulse analysis dashboard with Persona-Responsive logic.
    """

    trace = report.get('temporal_trace', [])
    writer_intel = report.get('writer_intelligence', {})
    dashboard = writer_intel.get('structural_dashboard', {})

    if not trace:
        st.warning("No scene data found. Please check your screenplay format.")
        return

    # --- Data Extraction ---
    summary = writer_intel.get('narrative_summary', {})
    priorities = writer_intel.get('rewrite_priorities', [])
    provocations = writer_intel.get('creative_provocations', [])
    char_arcs = dashboard.get('character_arcs', {})
    total_scenes = len(trace)

    # --- Component Definitions ---

    def render_score_card():
        st.markdown(f"### 🎬 {lens} Dashboard")
        avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0
        pacing = "Balanced"
        if avg_tension < 0.35: pacing = "Slow Burn"
        elif avg_tension > 0.65: pacing = "High Octane"

        pti = dashboard.get('page_turner_index', 50)
        texture = dashboard.get('writing_texture', 'Cinematic')
        readiness = dashboard.get('market_readiness', 50)
        
        runtime_data = dashboard.get('runtime_estimate', {})
        rt_label = f"{runtime_data.get('estimated_minutes', 0)} min" if isinstance(runtime_data, dict) else "N/A"

        # Highlight different metrics based on lens
        cols = st.columns(5)
        
        # Mapping metric focus
        if lens == "Studio Executive":
            cols[0].metric("Market Readiness", f"{readiness}/100", delta="Executive Focus")
            cols[1].metric("Budget Tier", dashboard.get('budget_impact', 'Indie'))
            cols[2].metric("Page-Turner", f"{pti}/100")
            cols[3].metric("Pacing", pacing)
        elif lens == "Script Coordinator":
            cols[0].metric("Writing Texture", texture, delta="Craft Focus")
            cols[1].metric("Pacing", pacing)
            cols[2].metric("Page-Turner", f"{pti}/100")
            cols[3].metric("Scenes", total_scenes)
        else: # Story Editor
            cols[0].metric("Page-Turner", f"{pti}/100", delta="Story Focus")
            cols[1].metric("Pacing", pacing)
            cols[2].metric("Midpoint", dashboard.get('midpoint_status', 'N/A'))
            cols[3].metric("Scenes", total_scenes)
            
        cols[4].metric("Runtime", rt_label)
        
        if isinstance(summary, dict) and summary.get('summary'):
            uikit.render_ai_consultant_box(summary['summary'])

    def render_story_pulse():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📈", "Narrative Tension Map",
            "Emotional architecture tracking peaks (conflict) and valleys (breathers).")
        
        # Prepare hover text
        for p in trace:
            intensity = p.get('attentional_signal', 0.5)
            p['Hover_Text'] = "<i>Peak intensity.</i>" if intensity > 0.8 else ("<i>Breather scene.</i>" if intensity < 0.3 else "<i>Steady progression.</i>")

        df_pulse = pd.DataFrame(trace)
        fig_pulse = charts.get_engagement_chart(df_pulse)
        fig_display = go.Figure(fig_pulse)

        turning_points = dashboard.get('structural_turning_points', {})
        tp_config = {
            'inciting_incident': (Theme.SEMANTIC_WARNING, 'Inciting Incident'),
            'act1_break': (Theme.SEMANTIC_CRITICAL, 'Act 1 Break'),
            'midpoint': (Theme.ACCENT_PRIMARY, 'Midpoint'),
            'act2_break': (Theme.SEMANTIC_INFO, 'Act 2 Break')
        }
        for tp_key, (color, label) in tp_config.items():
            tp_data = turning_points.get(tp_key, {})
            if isinstance(tp_data, dict) and 'scene' in tp_data:
                fig_display.add_vline(x=tp_data['scene'], line_width=1.5, line_dash="dot", line_color=color, 
                                     annotation_text=label, annotation_position="top")

        st.plotly_chart(fig_display, use_container_width=True, config={'displayModeBar': False}, key=f"pulse_{lens}")
        pulse_insight = st.session_state.get('ai_pulse_insight')
        if pulse_insight: uikit.render_ai_consultant_box(pulse_insight)

    def render_diagnostics():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🧠", "Structural Diagnostics", "Data-grounded feedback on narrative health.")
        diagnoses = writer_intel.get('narrative_diagnosis', [])
        if diagnoses:
            for diag in diagnoses: uikit.render_insight_card(diag if isinstance(diag, str) else diag.get('text', str(diag)))
        else:
            st.success("✅ No structural anomalies detected.")
            
        if priorities:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("⚡", "Priority Fixes", "High-leverage changes for this draft.")
            for i, p in enumerate(priorities[:3]):
                uikit.render_signal_box(f"Priority {i+1}", uikit.get_leverage_badge(p.get('leverage', 'Med')), 
                                      f"**{p.get('action', '')}**<br><small>Cause: {p.get('root_cause', '')}</small>", Theme.ACCENT_PRIMARY)

    def render_char_scene():
        if char_arcs:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("👥", "Character Arcs", "Agency and transformation tracking.")
            sorted_chars = sorted(char_arcs.items(), key=lambda x: x[1].get('scenes_present', 0), reverse=True)
            cols = st.columns(min(len(sorted_chars), 3))
            for i, (name, arc) in enumerate(sorted_chars[:3]):
                with cols[i]:
                    st.markdown(f"**{name}**")
                    st.caption(f"Arc: {arc.get('arc_type', 'Unknown')}")
                    st.progress(max(0.0, min(1.0, (arc.get('agency_end', 0) + 1) / 2)))

        turn_map = dashboard.get('scene_turn_map', [])
        if turn_map:
            turns_only = pd.DataFrame(turn_map)[lambda df: df['turn'] != 'Flat']
            if not turns_only.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                uikit.render_section_header("🎢", "Scene Turns", "Emotional shifts within scenes.")
                st.dataframe(turns_only[['scene', 'turn', 'sentiment_delta']].rename(columns={'turn': 'Shift', 'sentiment_delta': 'Intensity'}), hide_index=True, use_container_width=True)

    def render_producer_intel():
        st.markdown("<br><hr>", unsafe_allow_html=True)
        uikit.render_section_header("🏢", "Producer Intelligence", "Commercial viability and production logistics.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Production Risk", f"{dashboard.get('production_risk_score', 50)}/100")
        c2.metric("Market Readiness", f"{dashboard.get('market_readiness', 50)}/100")
        c3.metric("Budget Tier", dashboard.get('budget_impact', 'Standard'))
        c4.metric("Midpoint", dashboard.get('midpoint_status', 'N/A'))

        comps = dashboard.get('commercial_comps', [])
        if comps:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Comparable Films")
            comp_cols = st.columns(len(comps))
            for i, comp in enumerate(comps):
                with comp_cols[i]: st.info(f"🎬 {comp}")

        stakes_data = dashboard.get('stakes_profile', {})
        if stakes_data:
            stakes = {k: v for k, v in stakes_data.items() if v > 0 and k != 'None'}
            if stakes:
                st.plotly_chart(charts.get_stakes_chart(list(stakes.keys()), list(stakes.values()), 
                               {'Physical': Theme.SEMANTIC_CRITICAL, 'Emotional': Theme.SEMANTIC_WARNING, 'Social': Theme.SEMANTIC_GOOD, 'Moral': Theme.ACCENT_PRIMARY, 'Existential': Theme.ACCENT_PURPLE}),
                               use_container_width=True, config={'displayModeBar': False}, key=f"stakes_{lens}")

    def render_coverage_memo():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📝", f"AI {lens} Coverage", "Professional narrative assessment tailored to this perspective.")
        
        has_api = any([st.secrets.get(k) or os.environ.get(k) for k in ["GROQ_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY", "GEMINI_API_KEY"]])
        
        if st.button(f"🪄 Generate {lens} Memo", type="primary", use_container_width=True):
            if not has_api: st.warning("AI is offline. Please check API keys.")
            else:
                with st.spinner(f"Requesting {lens} analysis..."):
                    from scriptpulse.reporters.llm_translator import generate_ai_summary
                    summary, err = generate_ai_summary(report, lens=lens)
                    if summary: 
                        st.session_state['ai_summary_cache'] = summary
                        st.rerun()
                    else: st.error(err)

        if st.session_state.get('ai_summary_cache'):
            uikit.render_signal_box(f"{lens} Coverage", "", st.session_state['ai_summary_cache'], Theme.SEMANTIC_INFO)

    def render_mentor():
        if provocations:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("🧭", "Mentor's Corner", "Creative provocations for this draft.")
            for msg in provocations: st.info(f"💡 {msg}")

    def render_export():
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("📖 Original Script", expanded=False):
                st.text_area("Script", value=script_input, height=300, disabled=True, label_visibility="collapsed")
        with col_b:
            with st.expander("🧪 Research & Data Export", expanded=False):
                uikit.render_lab_pipeline_header()
                df_res = pd.DataFrame(trace)
                st.plotly_chart(charts.get_efficiency_frontier(df_res), use_container_width=True, config={'displayModeBar': False})
                
                t1, t2 = st.columns(2)
                telemetry = [s.get('research_telemetry', {}) for s in trace]
                if telemetry:
                    t1.metric("Confidence", f"{sum(t.get('analytical_confidence', 0) for t in telemetry)/len(telemetry):.0%}")
                    t2.metric("Semantic Density", f"{sum(t.get('semantic_density', 0) for t in telemetry)/len(telemetry):.2f}")
                
                clean_report = json.loads(json.dumps(report, default=lambda x: list(x) if isinstance(x, set) else str(x)))
                st.download_button("📥 Download JSON Trace", data=json.dumps(clean_report, indent=2), file_name="scriptpulse_trace.json", use_container_width=True)

    # --- PERSONA RESPONSIVE ORDERING ---
    if lens == "Studio Executive":
        # Executive wants the summary and money first
        render_score_card()
        render_coverage_memo()
        render_producer_intel()
        render_story_pulse()
        render_diagnostics()
        render_char_scene()
    elif lens == "Script Coordinator":
        # Coordinator wants the craft and rhythm first
        render_score_card()
        render_diagnostics()
        render_char_scene()
        render_story_pulse()
        render_coverage_memo()
        render_producer_intel()
    else: # Story Editor
        # Editor wants the structure and soul first
        render_score_card()
        render_story_pulse()
        render_diagnostics()
        render_char_scene()
        render_mentor()
        render_coverage_memo()
        render_producer_intel()

    render_export()
