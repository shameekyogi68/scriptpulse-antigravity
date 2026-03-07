"""
ScriptPulse — Unified Dashboard View
Product-Grade UI: Persona-Responsive Layout v3.0
Each persona sees ONLY what they need, in the order they need it.
"""
import streamlit as st
import pandas as pd
import os
import json
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts


# ── Persona Configuration ───────────────────────────────────────────────────
PERSONA_CONFIG = {
    "Studio Executive": {
        "icon": "🏢",
        "tagline": "Evaluating commercial viability, market positioning & production risk.",
        "score_title": "Studio Dashboard",
        "pulse_desc": "Where does the audience's attention peak? Where might they disengage?",
        "diag_desc": "Structural risks that could impact audience retention or marketability.",
        "fix_desc": "Changes that will most improve the script's commercial appeal.",
    },
    "Story Editor": {
        "icon": "🕵️",
        "tagline": "Analyzing structural integrity, character logic & emotional architecture.",
        "score_title": "Story Dashboard",
        "pulse_desc": "Emotional architecture — tracking peaks (conflict) and valleys (breathers).",
        "diag_desc": "Data-grounded feedback on narrative health, logic gaps, and pacing issues.",
        "fix_desc": "High-leverage structural changes for this draft.",
    },
    "Script Coordinator": {
        "icon": "✍️",
        "tagline": "Auditing prose economy, visual texture & scene-to-scene momentum.",
        "score_title": "Craft Dashboard",
        "pulse_desc": "Scene-by-scene rhythm and pacing energy across the full read.",
        "diag_desc": "Technical craft issues: exposition dumps, dialogue density, and scene bloat.",
        "fix_desc": "Craft improvements for a faster, cleaner read.",
    }
}


def render_writer_view(report, script_input, genre="Drama", lens="Story Editor"):
    """
    Renders the complete ScriptPulse analysis dashboard.
    Each persona sees ONLY the sections relevant to their role.
    """

    trace = report.get('temporal_trace', [])
    writer_intel = report.get('writer_intelligence', {})
    dashboard = writer_intel.get('structural_dashboard', {})

    if not trace:
        st.warning("No scene data found. Please check your screenplay format.")
        return

    # --- Data Extraction ---
    config = PERSONA_CONFIG.get(lens, PERSONA_CONFIG["Story Editor"])
    summary = writer_intel.get('narrative_summary', {})
    priorities = writer_intel.get('rewrite_priorities', [])
    provocations = writer_intel.get('creative_provocations', [])
    char_arcs = dashboard.get('character_arcs', {})
    total_scenes = len(trace)
    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0

    # =====================================================================
    # SECTION: HERO SCORE CARD
    # =====================================================================
    def render_score_card():
        # --- ScriptPulse Score ---
        sp_score = dashboard.get('scriptpulse_score', 50)
        if sp_score >= 70:
            score_color = Theme.SEMANTIC_GOOD
            score_label = "Strong Draft"
        elif sp_score >= 45:
            score_color = Theme.SEMANTIC_WARNING
            score_label = "Needs Work"
        else:
            score_color = Theme.SEMANTIC_CRITICAL
            score_label = "Major Revision"

        rgb = ','.join(str(int(score_color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))

        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 16px;">
            <div style="background: rgba({rgb}, 0.08); border: 2px solid {score_color};
                        border-radius: 16px; padding: 14px 28px; text-align: center; min-width: 130px;">
                <div style="font-size: 2.4rem; font-weight: 800; color: {score_color};
                            font-family: 'Outfit', sans-serif; line-height: 1;">{sp_score}</div>
                <div style="font-size: 0.65rem; color: {Theme.TEXT_MUTED}; text-transform: uppercase;
                            letter-spacing: 1.5px; margin-top: 4px;">ScriptPulse Score</div>
                <div style="font-size: 0.75rem; color: {score_color}; font-weight: 600; margin-top: 2px;">{score_label}</div>
            </div>
            <div>
                <h3 style="margin: 0 !important; padding: 0 !important;">{config['icon']} {config['score_title']}</h3>
                <p style="color: {Theme.TEXT_SECONDARY}; font-size: 0.85rem; margin: 4px 0 0 0;">{config['tagline']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- Pacing ---
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
            c1.metric("Market Readiness", f"{readiness}/100", help="Commercial viability score.")
            c2.metric("Budget Tier", dashboard.get('budget_impact', 'Indie'), help="Estimated production scale.")
            c3.metric("Prod. Risk", f"{dashboard.get('production_risk_score', 50)}/100", help="Complexity vs payoff.")
            c4.metric("Pacing", pacing)
            c5.metric("Runtime", rt_label)

        elif lens == "Script Coordinator":
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Writing Texture", texture, help="Cinematic = lean. Novelistic = dense.")
            c2.metric("Pacing", pacing)
            c3.metric("Page-Turner", f"{pti}/100", help="Scene cliffhanger momentum.")
            c4.metric("Scenes", total_scenes)
            c5.metric("Runtime", rt_label)

        else:  # Story Editor
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Page-Turner", f"{pti}/100", help="Scene cliffhanger momentum.")
            c2.metric("Pacing", pacing)
            c3.metric("Midpoint", dashboard.get('midpoint_status', 'N/A'), help="Structural midpoint health.")
            c4.metric("Scenes", total_scenes)
            c5.metric("Runtime", rt_label)

        # --- Act Structure & Dialogue Ratio (side by side) ---
        act = dashboard.get('act_structure', {})
        dar = dashboard.get('dialogue_action_ratio', {})

        if act or dar:
            st.markdown("<br>", unsafe_allow_html=True)
            ac1, ac2 = st.columns(2)

            with ac1:
                if act and act.get('act1_pct', 0) > 0:
                    st.markdown(f"""
                    <div style="background: {Theme.BG_CARD}; border: 1px solid rgba(106,72,187,0.15);
                                border-radius: 12px; padding: 16px;">
                        <div style="font-weight: 600; margin-bottom: 10px; font-size: 0.88rem;">🎬 Act Structure</div>
                        <div style="display: flex; gap: 3px; height: 26px; border-radius: 6px; overflow: hidden; margin-bottom: 8px;">
                            <div style="width: {max(8, act['act1_pct'])}%; background: {Theme.SEMANTIC_WARNING};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: white;">I · {act['act1_pct']}%</div>
                            <div style="width: {act['act2_pct']}%; background: {Theme.ACCENT_PRIMARY};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: white;">II · {act['act2_pct']}%</div>
                            <div style="width: {max(8, act['act3_pct'])}%; background: {Theme.SEMANTIC_GOOD};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: white;">III · {act['act3_pct']}%</div>
                        </div>
                        <div style="font-size: 0.75rem; color: {Theme.TEXT_MUTED};">
                            {act['act1']} + {act['act2']} + {act['act3']} scenes · Balance: <b>{act.get('balance', 'N/A')}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with ac2:
                if isinstance(dar, dict) and dar.get('global_dialogue_ratio') is not None:
                    d_pct = round(dar.get('global_dialogue_ratio', 0.5) * 100)
                    a_pct = 100 - d_pct
                    bench = round(dar.get('genre_benchmark', 0.5) * 100) if isinstance(dar.get('genre_benchmark'), float) else dar.get('genre_benchmark', 50)
                    st.markdown(f"""
                    <div style="background: {Theme.BG_CARD}; border: 1px solid rgba(106,72,187,0.15);
                                border-radius: 12px; padding: 16px;">
                        <div style="font-weight: 600; margin-bottom: 10px; font-size: 0.88rem;">💬 Dialogue vs Action</div>
                        <div style="display: flex; gap: 3px; height: 26px; border-radius: 6px; overflow: hidden; margin-bottom: 8px;">
                            <div style="width: {max(8, d_pct)}%; background: {Theme.SEMANTIC_INFO};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: #1A1729;">💬 {d_pct}%</div>
                            <div style="width: {max(8, a_pct)}%; background: {Theme.ACCENT_WARM};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: white;">🎬 {a_pct}%</div>
                        </div>
                        <div style="font-size: 0.75rem; color: {Theme.TEXT_MUTED};">
                            Ideal for {genre}: ~{bench}% dialogue
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- AI Summary ---
        if isinstance(summary, dict) and summary.get('summary'):
            uikit.render_ai_consultant_box(summary['summary'], persona=lens)

    # =====================================================================
    # SECTION: NARRATIVE TENSION MAP
    # =====================================================================
    def render_story_pulse():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📈", "Narrative Tension Map", config['pulse_desc'])

        for p in trace:
            intensity = p.get('attentional_signal', 0.5)
            if intensity > 0.8: p['Hover_Text'] = "<i>🔥 Peak intensity — audience locked in.</i>"
            elif intensity < 0.3: p['Hover_Text'] = "<i>😌 Breather — audience may drift.</i>"
            else: p['Hover_Text'] = "<i>⚡ Steady progression.</i>"

        df_pulse = pd.DataFrame(trace)
        fig_display = go.Figure(charts.get_engagement_chart(df_pulse))

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
                fig_display.add_vline(x=tp_data['scene'], line_width=1.5, line_dash="dot",
                                     line_color=color, annotation_text=label, annotation_position="top")

        st.plotly_chart(fig_display, use_container_width=True,
                       config={'displayModeBar': False}, key=f"pulse_{lens}")

        # AI Pacing Critique
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
    # SECTION: STRUCTURAL DIAGNOSTICS
    # =====================================================================
    def render_diagnostics():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🧠", "Structural Diagnostics", config['diag_desc'])

        diagnoses = writer_intel.get('narrative_diagnosis', [])
        if diagnoses:
            for diag in diagnoses:
                uikit.render_insight_card(diag if isinstance(diag, str) else diag.get('text', str(diag)))
        else:
            st.success("✅ No structural anomalies detected. Your script is clean.")

        if priorities:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("⚡", "Priority Fixes", config['fix_desc'])
            for i, p in enumerate(priorities[:3]):
                uikit.render_signal_box(
                    f"Priority {i+1}",
                    uikit.get_leverage_badge(p.get('leverage', 'Medium')),
                    f"**{p.get('action', '')}**<br><small style='color:{Theme.TEXT_MUTED};'>Root Cause: {p.get('root_cause', 'N/A')}</small>",
                    Theme.ACCENT_PRIMARY
                )

    # =====================================================================
    # SECTION: CHARACTER ARCS
    # =====================================================================
    def render_characters():
        if not char_arcs:
            return
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("👥", "Character Arcs", "Agency and transformation tracking.")
        sorted_chars = sorted(char_arcs.items(), key=lambda x: x[1].get('scenes_present', 0), reverse=True)
        cols = st.columns(min(len(sorted_chars), 3))
        for i, (name, arc) in enumerate(sorted_chars[:3]):
            with cols[i]:
                arc_type = arc.get('arc_type', 'Unknown')
                agency_val = max(0.0, min(1.0, (arc.get('agency_end', 0) + 1) / 2))
                st.markdown(f"**{name}**")
                st.caption(f"Arc: {arc_type} · Agency: {agency_val:.0%}")
                st.progress(agency_val)

    # =====================================================================
    # SECTION: SCENE TURNS
    # =====================================================================
    def render_scene_turns():
        turn_map = dashboard.get('scene_turn_map', [])
        if not turn_map:
            return
        df_turns = pd.DataFrame(turn_map)
        if 'turn' not in df_turns.columns:
            return
        turns_only = df_turns[df_turns['turn'] != 'Flat']
        if turns_only.empty:
            return
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🎢", "Scene Turns", "Emotional shifts within individual scenes.")
        display_cols = [c for c in ['scene', 'turn', 'sentiment_delta'] if c in turns_only.columns]
        st.dataframe(
            turns_only[display_cols].rename(columns={'turn': 'Shift', 'sentiment_delta': 'Intensity'}),
            hide_index=True, use_container_width=True
        )

    # =====================================================================
    # SECTION: PRODUCER INTELLIGENCE
    # =====================================================================
    def render_producer_intel():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🏢", "Producer Intelligence",
                                    "Commercial viability, budget estimation & marketplace positioning.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Production Risk", f"{dashboard.get('production_risk_score', 50)}/100",
                  help="Complexity vs narrative payoff.")
        c2.metric("Market Readiness", f"{dashboard.get('market_readiness', 50)}/100",
                  help="Combined commercial viability.")
        c3.metric("Budget Tier", dashboard.get('budget_impact', 'Standard'),
                  help="Indie → Studio → Blockbuster.")
        c4.metric("Midpoint", dashboard.get('midpoint_status', 'N/A'),
                  help="Structural midpoint health.")

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
                     'Social': Theme.SEMANTIC_GOOD, 'Moral': Theme.ACCENT_PRIMARY,
                     'Existential': Theme.ACCENT_PURPLE}
                ), use_container_width=True, config={'displayModeBar': False}, key=f"stakes_{lens}")

    # =====================================================================
    # SECTION: AI COVERAGE MEMO
    # =====================================================================
    def render_coverage_memo():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📝", f"AI {lens} Coverage",
                                    f"Professional narrative assessment from the {lens} perspective.")

        has_api = any(os.environ.get(k) for k in ["GROQ_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY", "GEMINI_API_KEY"])
        try:
            for k in ["GROQ_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY", "GEMINI_API_KEY"]:
                if st.secrets.get(k): has_api = True
        except Exception:
            pass

        cache_key = f'ai_summary_{lens.lower().replace(" ", "_")}'

        if st.button(f"🪄 Generate {lens} Memo", type="primary", use_container_width=True, key=f"memo_btn_{lens}"):
            if not has_api:
                st.warning("⚠️ AI is offline. Please add API keys to activate.")
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
                f"{config['icon']} {lens} Coverage", "",
                st.session_state[cache_key], Theme.SEMANTIC_INFO
            )

    # =====================================================================
    # SECTION: MENTOR'S CORNER (Story Editor only)
    # =====================================================================
    def render_mentor():
        if not provocations:
            return
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🧭", "Mentor's Corner",
                                    "Creative provocations to challenge your choices and push the draft further.")
        for msg in provocations:
            st.info(f"💡 {msg}")

    # =====================================================================
    # SECTION: EXPORT — STACKED VERTICALLY
    # =====================================================================
    def render_export():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        uikit.render_section_header("📦", "Script & Data", "View your original script and export research data.")

        # --- Original Script (full width) ---
        with st.expander("📖 View Original Script", expanded=False):
            st.text_area("Script", value=script_input, height=400, disabled=True, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Research & Data Export (full width) ---
        with st.expander("🧪 Research & Data Export", expanded=False):
            uikit.render_lab_pipeline_header()

            st.markdown("##### Narrative Efficiency Frontier")
            df_res = pd.DataFrame(trace)
            st.plotly_chart(charts.get_efficiency_frontier(df_res), use_container_width=True,
                           config={'displayModeBar': False}, key="res_eff")

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
    # PERSONA-RESPONSIVE FLOW — SHOW ONLY WHAT'S NEEDED
    # =====================================================================

    if lens == "Studio Executive":
        # Executive Flow: Score → AI Memo → Producer Intel → Tension Map → Diagnostics
        # NO Characters, NO Scene Turns, NO Mentor
        render_score_card()
        render_coverage_memo()
        render_producer_intel()
        st.markdown("---")
        render_story_pulse()
        render_diagnostics()

    elif lens == "Script Coordinator":
        # Coordinator Flow: Score → Tension Map → Diagnostics → Scene Turns → AI Memo
        # NO Producer Intel, NO Mentor, NO Characters
        render_score_card()
        render_story_pulse()
        render_diagnostics()
        render_scene_turns()
        st.markdown("---")
        render_coverage_memo()

    else:  # Story Editor (Default)
        # Editor Flow: Score → Tension Map → Diagnostics → Characters → Scene Turns → Mentor → AI Memo → Producer Intel
        # FULL VIEW — the Editor sees everything
        render_score_card()
        render_story_pulse()
        render_diagnostics()
        render_characters()
        render_scene_turns()
        render_mentor()
        st.markdown("---")
        render_coverage_memo()
        render_producer_intel()

    render_export()
