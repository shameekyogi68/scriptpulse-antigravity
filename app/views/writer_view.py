"""
ScriptPulse — Unified Dashboard View
Product-Grade UI: Writer + Producer in one clean flow.
"""
import streamlit as st
import pandas as pd
import random
import os
import json
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts


def render_writer_view(report, script_input, genre="Drama"):
    """
    Renders the complete ScriptPulse analysis dashboard.
    
    Flow:
      1. Score Card (At-a-Glance)
      2. Story Pulse (Tension Map)
      3. Diagnostics (What to Fix)
      4. Rewrite Priorities (How to Fix It)
      5. Character & Scene Intelligence
      6. Producer Metrics (Stakes, Risk, Budget)
      7. AI Coverage Memo (On-Demand)
      8. Data Export (Research)
    """

    trace = report.get('temporal_trace', [])
    writer_intel = report.get('writer_intelligence', {})
    dashboard = writer_intel.get('structural_dashboard', {})

    if not trace:
        st.warning("No scene data found. Please check your screenplay format.")
        return

    # --- Extract Intelligence ---
    summary = writer_intel.get('narrative_summary', {})
    priorities = writer_intel.get('rewrite_priorities', [])
    provocations = writer_intel.get('creative_provocations', [])
    char_arcs = dashboard.get('character_arcs', {})
    total_scenes = len(trace)

    def _label(val, lo, hi, lo_t, mid_t, hi_t):
        if val < lo: return lo_t
        if val > hi: return hi_t
        return mid_t

    # =====================================================================
    # 1. SCORE CARD — The "At a Glance" Header
    # =====================================================================
    st.markdown("### 🎬 Script Analysis")

    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes
    pacing = _label(avg_tension, 0.35, 0.65, "Slow Burn", "Steady", "High Octane")
    pti = dashboard.get('page_turner_index', 50)
    texture = dashboard.get('writing_texture', 'Cinematic')

    runtime_data = dashboard.get('runtime_estimate', {})
    rt_label = "N/A"
    if isinstance(runtime_data, dict):
        rt_minutes = runtime_data.get('estimated_minutes', 0)
        if rt_minutes: rt_label = f"{rt_minutes} min"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Scenes", total_scenes)
    c2.metric("Pacing", pacing)
    c3.metric("Page-Turner", f"{pti}/100", help="Momentum score based on hooks and cliffhangers.")
    c4.metric("Texture", texture, help="Your prose style: Cinematic, Novelistic, or Minimalist.")
    c5.metric("Runtime", rt_label)

    # Narrative summary (if available)
    if isinstance(summary, dict) and summary.get('summary'):
        uikit.render_ai_consultant_box(summary['summary'])

    # =====================================================================
    # 2. STORY PULSE — The Tension Map
    # =====================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header("📈", "Story Pulse",
        "Your script's emotional architecture. Peaks are moments of high tension; valleys are breathers.")

    # Prepare hover text
    for i, p in enumerate(trace):
        intensity = p.get('attentional_signal', 0.5)
        if intensity > 0.8: p['Hover_Text'] = "<i>Peak intensity.</i>"
        elif intensity < 0.3: p['Hover_Text'] = "<i>Breather scene.</i>"
        else: p['Hover_Text'] = "<i>Steady progression.</i>"

    df_pulse = pd.DataFrame(trace)
    fig_pulse = charts.get_engagement_chart(df_pulse)
    fig_display = go.Figure(fig_pulse)

    # Overlay turning points
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
            fig_display.add_vline(
                x=tp_data['scene'], line_width=1.5, line_dash="dot",
                line_color=color, annotation_text=label, annotation_position="top",
                annotation_font_size=10, annotation_font_color=color
            )

    st.plotly_chart(fig_display, use_container_width=True,
                    config={'displayModeBar': False}, key="pulse_chart")

    # AI Pulse Insight
    pulse_insight = st.session_state.get('ai_pulse_insight')
    if pulse_insight:
        uikit.render_ai_consultant_box(pulse_insight)

    # =====================================================================
    # 3. DIAGNOSTICS — What Needs Attention
    # =====================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header("🧠", "Diagnostics",
        "Data-grounded feedback on your script's structural health. Each insight is tied to specific scenes and evidence.")

    diagnoses = writer_intel.get('narrative_diagnosis', [])
    if diagnoses:
        for diag in diagnoses:
            if isinstance(diag, str):
                uikit.render_insight_card(diag)
            elif isinstance(diag, dict):
                text = diag.get('text', diag.get('advice', str(diag)))
                uikit.render_insight_card(text)
    else:
        st.success("✅ No structural anomalies detected. Your narrative progression is clean.")

    # =====================================================================
    # 4. REWRITE PRIORITIES — How to Fix It
    # =====================================================================
    if priorities:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("⚡", "Rewrite Priorities",
            "The highest-leverage changes to improve your script. Start here.")

        for i, p in enumerate(priorities[:3]):
            act = p.get('action', 'Review this section.')
            lev = p.get('leverage', 'Medium')
            cause = p.get('root_cause', '')
            badge = uikit.get_leverage_badge(lev)

            cause_html = f"<br><small style='color: {Theme.TEXT_MUTED};'>Root Cause: {cause}</small>" if cause else ""
            uikit.render_signal_box(
                f"Priority {i+1}",
                badge,
                f"**{act}**{cause_html}",
                border_color=Theme.ACCENT_PRIMARY
            )

    # =====================================================================
    # 5. CHARACTER & SCENE INTELLIGENCE
    # =====================================================================

    # 5a. Character Arcs
    if char_arcs:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("👥", "Character Arcs",
            "How your main characters transform over the story.")

        sorted_chars = sorted(char_arcs.items(),
                              key=lambda x: x[1].get('scenes_present', 0), reverse=True)
        cols = st.columns(min(len(sorted_chars), 3))
        for i, (name, arc) in enumerate(sorted_chars[:3]):
            with cols[i]:
                st.markdown(f"**{name}**")
                arc_type = arc.get('arc_type', 'Unknown')
                st.caption(f"Arc: {arc_type}")
                agency_end = arc.get('agency_end', 0)
                st.progress(max(0.0, min(1.0, (agency_end + 1) / 2)))
                st.caption(f"Agency: {arc.get('agency_start', 0):.2f} → {agency_end:.2f}")

    # 5b. Scene Turns
    turn_map = dashboard.get('scene_turn_map', [])
    if turn_map:
        turn_df = pd.DataFrame(turn_map)
        turns_only = turn_df[turn_df['turn'] != 'Flat']
        if not turns_only.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("🎢", "Scene Turns",
                "Scenes where the emotional state 'flips.' Professional scripts turn at least once per scene.")
            st.dataframe(
                turns_only[['scene', 'turn', 'sentiment_delta']].rename(
                    columns={'turn': 'Shift', 'sentiment_delta': 'Intensity'}
                ),
                hide_index=True, use_container_width=True
            )

    # =====================================================================
    # 6. PRODUCER METRICS — Stakes, Risk, Budget
    # =====================================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("### 🏢 Producer Intelligence")

    # 6a. Production Metrics
    risk_score = dashboard.get('production_risk_score', 50)
    budget_impact = dashboard.get('budget_impact', 'Standard')
    midpoint = dashboard.get('midpoint_status', 'N/A')
    comps = dashboard.get('commercial_comps', [])

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Production Risk", f"{risk_score}/100",
              help="Higher = more expensive scenes relative to narrative payoff.")
    p2.metric("Budget Tier", budget_impact,
              help="Estimated production scale: Indie → Blockbuster.")
    p3.metric("Midpoint", midpoint,
              help="Is the script's midpoint structurally 'Healthy' or 'Sagging'?")
    p4.metric("Market Readiness", f"{dashboard.get('market_readiness', 50)}/100",
              help="Combined commercial viability score based on pacing and payoff.")

    # 6b. Marketplace Comps
    if comps:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("💎", "Comparable Films",
            "Scripts with a similar structural DNA. Useful for pitching and positioning.")
        comp_cols = st.columns(len(comps))
        for i, comp in enumerate(comps):
            with comp_cols[i]:
                st.markdown(f"🎬 **{comp}**")
                st.caption(f"{genre}")

    # 6c. Dominant Stakes
    stakes_data = dashboard.get('stakes_profile', {})
    if stakes_data:
        stakes = {k: v for k, v in stakes_data.items() if v > 0 and k != 'None'}
        if stakes:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("⚖️", "Story Stakes",
                "What types of conflict drive your narrative.")
            fig_stakes = charts.get_stakes_chart(
                list(stakes.keys()), list(stakes.values()),
                {'Physical': Theme.SEMANTIC_CRITICAL, 'Emotional': Theme.SEMANTIC_WARNING,
                 'Social': Theme.SEMANTIC_GOOD, 'Moral': Theme.ACCENT_PRIMARY,
                 'Existential': Theme.ACCENT_PURPLE}
            )
            st.plotly_chart(fig_stakes, use_container_width=True,
                           config={'displayModeBar': False}, key="stakes_chart")

    # =====================================================================
    # 7. AI EXECUTIVE COVERAGE (On-Demand)
    # =====================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header("📝", "AI Coverage Memo",
        "Generate a professional narrative assessment powered by AI. This replaces hours of manual script coverage.")

    has_api = (st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
               or st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
               or st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
               or os.environ.get("GEMINI_API_KEY"))

    if st.button("🪄 Generate Coverage", type="primary", use_container_width=True):
        if not has_api:
            st.warning("AI Consultant is offline. Add a GROQ_API_KEY or HF_TOKEN to enable this feature.")
        else:
            with st.spinner("Generating executive coverage... (10–20 seconds)"):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                lens_persona = st.session_state.get('current_lens', 'viewer')
                ai_summary, err = generate_ai_summary(report, lens=lens_persona)
                if ai_summary:
                    st.session_state['ai_summary_cache'] = ai_summary
                    st.rerun()
                else:
                    st.error(f"AI Coverage Error: {err}")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Executive Coverage", "",
            st.session_state['ai_summary_cache'], border_color=Theme.SEMANTIC_INFO)

    # =====================================================================
    # 8. MENTOR'S CORNER
    # =====================================================================
    if provocations:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🧭", "Mentor's Corner",
            "Creative provocations to challenge your choices and push the draft further.")
        for msg in provocations:
            st.info(f"💡 {msg}")

    # =====================================================================
    # 9. DATA & RESEARCH EXPORT
    # =====================================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("📖 View Original Script", expanded=False):
            st.text_area("Script", value=script_input, height=300,
                         disabled=True, label_visibility="collapsed")

    with col_b:
        with st.expander("🧪 Research & Data Export", expanded=False):
            uikit.render_lab_pipeline_header()
            
            st.markdown("##### Narrative Efficiency Frontier")
            df_res = pd.DataFrame(trace)
            fig_eff = charts.get_efficiency_frontier(df_res)
            st.plotly_chart(fig_eff, use_container_width=True, config={'displayModeBar': False}, key="res_eff_chart")

            st.divider()
            st.markdown("##### Research Telemetry")
            telemetry = [s.get('research_telemetry', {}) for s in trace]
            if telemetry:
                avg_conf = sum(t.get('analytical_confidence', 0) for t in telemetry) / len(telemetry)
                avg_dens = sum(t.get('semantic_density', 0) for t in telemetry) / len(telemetry)

                t1, t2 = st.columns(2)
                t1.metric("Confidence", f"{avg_conf:.0%}",
                          help="ML model confidence. >80% = strong alignment.")
                t2.metric("Semantic Density", f"{avg_dens:.2f}",
                          help="Lexical diversity per token.")

                if any(t.get('heuristic_fallback') for t in telemetry):
                    st.caption("⚠️ Heuristic fallbacks active for some features.")

            st.divider()

            # JSON Export
            def _sanitize(obj):
                if isinstance(obj, set): return list(obj)
                if isinstance(obj, dict): return {k: _sanitize(v) for k, v in obj.items()}
                if isinstance(obj, list): return [_sanitize(x) for x in obj]
                return obj

            clean_report = _sanitize(report)
            json_str = json.dumps(clean_report, indent=2)
            st.download_button(
                label="📥 Download Full JSON Trace",
                data=json_str,
                file_name="scriptpulse_analysis.json",
                mime="application/json",
                use_container_width=True
            )
