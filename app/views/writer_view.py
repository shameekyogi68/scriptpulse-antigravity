"""
ScriptPulse — Unified Dashboard View
Product-Grade UI: Persona-Responsive Layout v2.0
"""
import streamlit as st
import pandas as pd
import os
import json
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts


# ── Persona Descriptions (shown under dashboard title) ──────────────────────
PERSONA_TAGLINES = {
    "Studio Executive": "Evaluating commercial viability, market positioning & production risk.",
    "Story Editor": "Analyzing structural integrity, character logic & emotional architecture.",
    "Script Coordinator": "Auditing prose economy, visual texture & scene-to-scene momentum."
}

PERSONA_ICONS = {
    "Studio Executive": "🏢",
    "Story Editor": "🕵️",
    "Script Coordinator": "✍️"
}


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
    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0

    # =====================================================================
    # COMPONENT: SCORE CARD
    # =====================================================================
    def render_score_card():
        icon = PERSONA_ICONS.get(lens, "🎬")
        tagline = PERSONA_TAGLINES.get(lens, "")
        st.markdown(f"### {icon} {lens} Dashboard")
        st.caption(tagline)

        pacing = "Balanced"
        if avg_tension < 0.35: pacing = "Slow Burn 🐢"
        elif avg_tension > 0.65: pacing = "High Octane 🔥"

        pti = dashboard.get('page_turner_index', 50)
        texture = dashboard.get('writing_texture', 'Cinematic')
        readiness = dashboard.get('market_readiness', 50)
        
        runtime_data = dashboard.get('runtime_estimate', {})
        rt_label = f"{runtime_data.get('estimated_minutes', 0)} min" if isinstance(runtime_data, dict) else "N/A"

        # --- Persona-Specific Metric Cards ---
        if lens == "Studio Executive":
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Market Readiness", f"{readiness}/100",
                      help="Commercial viability based on pacing + payoff.")
            c2.metric("Budget Tier", dashboard.get('budget_impact', 'Indie'),
                      help="Estimated production scale.")
            c3.metric("Prod. Risk", f"{dashboard.get('production_risk_score', 50)}/100",
                      help="Complexity vs narrative payoff.")
            c4.metric("Pacing", pacing)
            c5.metric("Runtime", rt_label)
            
        elif lens == "Script Coordinator":
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Writing Texture", texture,
                      help="Cinematic = lean visual prose. Novelistic = dense literary style.")
            c2.metric("Pacing", pacing)
            c3.metric("Page-Turner", f"{pti}/100",
                      help="Momentum score based on scene cliffhangers.")
            c4.metric("Scenes", total_scenes)
            c5.metric("Runtime", rt_label)
            
        else: # Story Editor
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Page-Turner", f"{pti}/100",
                      help="Momentum score based on scene cliffhangers.")
            c2.metric("Pacing", pacing)
            c3.metric("Midpoint", dashboard.get('midpoint_status', 'N/A'),
                      help="Is the script's structural midpoint healthy?")
            c4.metric("Scenes", total_scenes)
            c5.metric("Runtime", rt_label)
        
        # --- Narrative Summary ---
        if isinstance(summary, dict) and summary.get('summary'):
            uikit.render_ai_consultant_box(summary['summary'], persona=lens)

    # =====================================================================
    # COMPONENT: STORY PULSE (Tension Map)
    # =====================================================================
    def render_story_pulse():
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Persona-specific section descriptions
        pulse_desc = {
            "Studio Executive": "Where does the audience's attention peak? Where might they disengage?",
            "Story Editor": "Emotional architecture tracking peaks (conflict) and valleys (breathers).",
            "Script Coordinator": "Scene-by-scene rhythm and pacing energy across the full read."
        }
        uikit.render_section_header("📈", "Narrative Tension Map", pulse_desc.get(lens, ""))
        
        # Prepare hover text
        for p in trace:
            intensity = p.get('attentional_signal', 0.5)
            if intensity > 0.8: p['Hover_Text'] = "<i>🔥 Peak intensity — audience is fully locked in.</i>"
            elif intensity < 0.3: p['Hover_Text'] = "<i>😌 Breather — audience may drift here.</i>"
            else: p['Hover_Text'] = "<i>⚡ Steady progression.</i>"

        df_pulse = pd.DataFrame(trace)
        fig_pulse = charts.get_engagement_chart(df_pulse)
        fig_display = go.Figure(fig_pulse)

        turning_points = dashboard.get('structural_turning_points', {})
        tp_config = {
            'inciting_incident': (Theme.SEMANTIC_WARNING, '⚡ Inciting Incident'),
            'act1_break': (Theme.SEMANTIC_CRITICAL, '🚪 Act 1 Break'),
            'midpoint': (Theme.ACCENT_PRIMARY, '🎯 Midpoint'),
            'act2_break': (Theme.SEMANTIC_INFO, '💥 Act 2 Break')
        }
        for tp_key, (color, label) in tp_config.items():
            tp_data = turning_points.get(tp_key, {})
            if isinstance(tp_data, dict) and 'scene' in tp_data:
                fig_display.add_vline(x=tp_data['scene'], line_width=1.5, line_dash="dot", line_color=color, 
                                     annotation_text=label, annotation_position="top")

        st.plotly_chart(fig_display, use_container_width=True, config={'displayModeBar': False}, key=f"pulse_{lens}")
        
        # AI Pacing Critique Button
        pulse_cache_key = f'ai_pulse_{lens.lower().replace(" ", "_")}'
        
        if st.session_state.get(pulse_cache_key):
             uikit.render_ai_consultant_box(st.session_state[pulse_cache_key], persona=lens)
        else:
             if st.button(f"🧠 Ask {lens} for Pacing Critique", key=f"pulse_btn_{lens}", use_container_width=True):
                 with st.spinner("Analyzing..."):
                     from scriptpulse.reporters.llm_translator import generate_section_insight
                     insight = generate_section_insight(report, 'pulse', lens=lens)
                     st.session_state[pulse_cache_key] = insight
                     st.rerun()

    # =====================================================================
    # COMPONENT: DIAGNOSTICS & PRIORITIES
    # =====================================================================
    def render_diagnostics():
        st.markdown("<br>", unsafe_allow_html=True)
        
        diag_desc = {
            "Studio Executive": "Structural risks that could impact audience retention or marketability.",
            "Story Editor": "Data-grounded feedback on narrative health, logic gaps, and pacing issues.",
            "Script Coordinator": "Technical craft issues: exposition dumps, dialogue density, and scene bloat."
        }
        uikit.render_section_header("🧠", "Structural Diagnostics", diag_desc.get(lens, ""))
        
        diagnoses = writer_intel.get('narrative_diagnosis', [])
        if diagnoses:
            for diag in diagnoses:
                uikit.render_insight_card(diag if isinstance(diag, str) else diag.get('text', str(diag)))
        else:
            st.success("✅ No structural anomalies detected. Your script is clean.")
            
        if priorities:
            st.markdown("<br>", unsafe_allow_html=True)
            
            fix_desc = {
                "Studio Executive": "Changes that will most improve the script's commercial appeal.",
                "Story Editor": "High-leverage structural changes for this draft.",
                "Script Coordinator": "Craft improvements for a faster, cleaner read."
            }
            uikit.render_section_header("⚡", "Priority Fixes", fix_desc.get(lens, ""))
            
            for i, p in enumerate(priorities[:3]):
                uikit.render_signal_box(
                    f"Priority {i+1}",
                    uikit.get_leverage_badge(p.get('leverage', 'Medium')),
                    f"**{p.get('action', '')}**<br><small style='color:{Theme.TEXT_MUTED};'>Root Cause: {p.get('root_cause', 'N/A')}</small>",
                    Theme.ACCENT_PRIMARY
                )

    # =====================================================================
    # COMPONENT: CHARACTER ARCS & SCENE TURNS
    # =====================================================================
    def render_char_scene():
        if char_arcs:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("👥", "Character Arcs", "Agency and transformation tracking across the full story.")
            sorted_chars = sorted(char_arcs.items(), key=lambda x: x[1].get('scenes_present', 0), reverse=True)
            cols = st.columns(min(len(sorted_chars), 3))
            for i, (name, arc) in enumerate(sorted_chars[:3]):
                with cols[i]:
                    st.markdown(f"**{name}**")
                    arc_type = arc.get('arc_type', 'Unknown')
                    st.caption(f"Arc: {arc_type}")
                    agency_val = max(0.0, min(1.0, (arc.get('agency_end', 0) + 1) / 2))
                    st.progress(agency_val)
                    st.caption(f"Agency: {agency_val:.0%}")

        turn_map = dashboard.get('scene_turn_map', [])
        if turn_map:
            df_turns = pd.DataFrame(turn_map)
            if 'turn' in df_turns.columns:
                turns_only = df_turns[df_turns['turn'] != 'Flat']
                if not turns_only.empty:
                    st.markdown("<br>", unsafe_allow_html=True)
                    uikit.render_section_header("🎢", "Scene Turns", "Emotional shifts within individual scenes.")
                    display_cols = [c for c in ['scene', 'turn', 'sentiment_delta'] if c in turns_only.columns]
                    st.dataframe(
                        turns_only[display_cols].rename(columns={'turn': 'Shift', 'sentiment_delta': 'Intensity'}),
                        hide_index=True, use_container_width=True
                    )

    # =====================================================================
    # COMPONENT: PRODUCER INTELLIGENCE
    # =====================================================================
    def render_producer_intel():
        st.markdown("<br><hr>", unsafe_allow_html=True)
        uikit.render_section_header("🏢", "Producer Intelligence", "Commercial viability, budget estimation, and marketplace positioning.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Production Risk", f"{dashboard.get('production_risk_score', 50)}/100",
                  help="Higher = more expensive scenes relative to narrative payoff.")
        c2.metric("Market Readiness", f"{dashboard.get('market_readiness', 50)}/100",
                  help="Combined commercial viability score.")
        c3.metric("Budget Tier", dashboard.get('budget_impact', 'Standard'),
                  help="Estimated production scale: Indie → Blockbuster.")
        c4.metric("Midpoint", dashboard.get('midpoint_status', 'N/A'),
                  help="Structural midpoint health check.")

        # Comparable Films
        comps = dashboard.get('commercial_comps', [])
        if comps:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 🎬 Comparable Films")
            comp_cols = st.columns(len(comps))
            for i, comp in enumerate(comps):
                with comp_cols[i]:
                    st.info(f"**{comp}**")

        # Stakes Distribution
        stakes_data = dashboard.get('stakes_profile', {})
        if stakes_data:
            stakes = {k: v for k, v in stakes_data.items() if isinstance(v, (int, float)) and v > 0 and k != 'None'}
            if stakes:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 🎯 Stakes Distribution")
                st.plotly_chart(charts.get_stakes_chart(
                    list(stakes.keys()), list(stakes.values()), 
                    {'Physical': Theme.SEMANTIC_CRITICAL, 'Emotional': Theme.SEMANTIC_WARNING, 
                     'Social': Theme.SEMANTIC_GOOD, 'Moral': Theme.ACCENT_PRIMARY, 'Existential': Theme.ACCENT_PURPLE}
                ), use_container_width=True, config={'displayModeBar': False}, key=f"stakes_{lens}")

    # =====================================================================
    # COMPONENT: AI COVERAGE MEMO
    # =====================================================================
    def render_coverage_memo():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📝", f"AI {lens} Coverage",
            f"Professional narrative assessment from the {lens} perspective.")
        
        has_api = any([
            os.environ.get(k) for k in ["GROQ_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY", "GEMINI_API_KEY"]
        ])
        
        # Try st.secrets safely
        try:
            for k in ["GROQ_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY", "GEMINI_API_KEY"]:
                if st.secrets.get(k): has_api = True
        except Exception:
            pass
        
        # Lens-specific cache key
        cache_key = f'ai_summary_{lens.lower().replace(" ", "_")}'
        
        if st.button(f"🪄 Generate {lens} Memo", type="primary", use_container_width=True, key=f"memo_btn_{lens}"):
            if not has_api:
                st.warning("⚠️ AI is offline. Please add API keys (Groq, Gemini, or HuggingFace) to activate.")
            else:
                with st.spinner(f"The {lens} is reading your script..."):
                    from scriptpulse.reporters.llm_translator import generate_ai_summary
                    result, err = generate_ai_summary(report, lens=lens)
                    if result: 
                        st.session_state[cache_key] = result
                        st.rerun()
                    else:
                        st.error(f"AI Error: {err}")

        if st.session_state.get(cache_key):
            uikit.render_signal_box(
                f"{PERSONA_ICONS.get(lens, '📝')} {lens} Coverage",
                "", st.session_state[cache_key], Theme.SEMANTIC_INFO
            )

    # =====================================================================
    # COMPONENT: MENTOR'S CORNER
    # =====================================================================
    def render_mentor():
        if provocations:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("🧭", "Mentor's Corner", "Creative provocations to challenge your choices and push the draft further.")
            for msg in provocations:
                st.info(f"💡 {msg}")

    # =====================================================================
    # COMPONENT: EXPORT & RESEARCH
    # =====================================================================
    def render_export():
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("📖 View Original Script", expanded=False):
                st.text_area("Script", value=script_input, height=300, disabled=True, label_visibility="collapsed")
        with col_b:
            with st.expander("🧪 Research & Data Export", expanded=False):
                uikit.render_lab_pipeline_header()
                
                st.markdown("##### Narrative Efficiency Frontier")
                df_res = pd.DataFrame(trace)
                st.plotly_chart(charts.get_efficiency_frontier(df_res), use_container_width=True, config={'displayModeBar': False}, key="res_eff")
                
                st.divider()
                st.markdown("##### Research Telemetry")
                t1, t2 = st.columns(2)
                telemetry = [s.get('research_telemetry', {}) for s in trace]
                if telemetry:
                    avg_conf = sum(t.get('analytical_confidence', 0) for t in telemetry) / len(telemetry)
                    avg_dens = sum(t.get('semantic_density', 0) for t in telemetry) / len(telemetry)
                    t1.metric("Confidence", f"{avg_conf:.0%}", help="ML model confidence.")
                    t2.metric("Semantic Density", f"{avg_dens:.2f}", help="Lexical diversity per token.")
                    
                    if any(t.get('heuristic_fallback') for t in telemetry):
                        st.caption("⚠️ Heuristic fallbacks active for some features.")
                
                st.divider()
                clean_report = json.loads(json.dumps(report, default=lambda x: list(x) if isinstance(x, set) else str(x)))
                st.download_button("📥 Download Full JSON Trace", data=json.dumps(clean_report, indent=2), 
                                  file_name="scriptpulse_trace.json", use_container_width=True, key="dl_json")

    # =====================================================================
    # PERSONA-RESPONSIVE SECTION ORDERING
    # =====================================================================
    if lens == "Studio Executive":
        render_score_card()
        render_coverage_memo()
        render_producer_intel()
        render_story_pulse()
        render_diagnostics()
        render_char_scene()
    elif lens == "Script Coordinator":
        render_score_card()
        render_story_pulse()
        render_diagnostics()
        render_char_scene()
        render_coverage_memo()
        render_producer_intel()
    else:  # Story Editor (Default)
        render_score_card()
        render_story_pulse()
        render_diagnostics()
        render_char_scene()
        render_mentor()
        render_coverage_memo()
        render_producer_intel()

    render_export()
