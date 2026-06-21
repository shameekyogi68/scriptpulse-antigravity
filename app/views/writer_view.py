# MODULE: writer_view.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
ScriptPulse — Unified Dashboard View
Product-Grade UI: Persona-Responsive Layout v3.0
Each persona sees ONLY what they need, in the order they need it.
"""
import streamlit as st
import pandas as pd
import os
import json
import textwrap
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts
from scriptpulse.disclaimers import (
    SHORT_DISCLAIMER,
    FULL_DISCLAIMER_LINES,
    METHODOLOGY_NOTE,
    engagement_signal_label,
    get_engine_mode_note,
)


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
    # SECTION: ASIDE PANEL
    # =====================================================================
    def render_aside_panel():
        # --- ScriptPulse Score ---
        sp_score = dashboard.get('scriptpulse_score', 50)
        if sp_score >= 70:
            score_color = Theme.SEMANTIC_GOOD
        elif sp_score >= 45:
            score_color = Theme.SEMANTIC_WARNING
        else:
            score_color = Theme.SEMANTIC_CRITICAL
        score_label = engagement_signal_label(sp_score)

        rgb = ','.join(str(int(score_color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))

        # We display the Engagement Index and Confidence in a single unified tactile glass card matching the mockup exactly
        st.markdown(uikit.clean_html(f"""
        <div class="glass-card score-card hardware-metric" style="padding: 32px; text-align: center; margin-bottom: 20px;">
            <div class="well" style="padding: 24px; margin-bottom: 24px; background: rgba(0, 0, 0, 0.2); box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6); border-radius: var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.03);">
                <span style="font-size: 0.65rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.12em; display: block; margin-bottom: 4px;">Engagement Index</span>
                <div style="font-family: 'Outfit', sans-serif; font-size: 4.5rem; font-weight: 800; line-height: 1; margin: 16px 0; color: {score_color}; text-shadow: 0 0 15px rgba({rgb},0.4);">{sp_score}</div>
                <div style="background: rgba({rgb}, 0.1); color: {score_color}; font-size: 0.72rem; font-weight: 700; padding: 4px 12px; border-radius: 12px; display: inline-block; border: 1px solid rgba({rgb}, 0.2); letter-spacing: 0.04em; text-transform: uppercase;">{score_label}</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.75rem; font-weight: 700; color: var(--text-secondary);">
                <i class="ti ti-circle-check" style="font-size: 1rem; color: {confidence_colors[confidence]};"></i>
                <span style="text-transform: uppercase; letter-spacing: 0.05em;">{confidence} CONFIDENCE</span>
            </div>
        </div>
        """), unsafe_allow_html=True)
        if reasons:
            st.markdown(uikit.clean_html(f"""
            <div style="text-align: center; font-size: 0.72rem; color: var(--text-muted); margin-top: -12px; margin-bottom: 20px;">
                Reason: {', '.join(reasons)}
            </div>
            """), unsafe_allow_html=True)

        # --- Metric Values Calculations ---
        pacing = "Balanced"
        if avg_tension < 0.35: pacing = "Slow Burn 🐢"
        elif avg_tension > 0.65: pacing = "High Octane 🔥"

        pti = dashboard.get('page_turner_index', 50)
        texture = dashboard.get('writing_texture', 'Cinematic')
        readiness = dashboard.get('market_readiness', 50)
        runtime_data = dashboard.get('runtime_estimate', {})
        rt_label = f"{runtime_data.get('estimated_minutes', 0)} min" if isinstance(runtime_data, dict) else "N/A"
        loc_profile = dashboard.get('location_profile', {})
        cast_size = len(report.get('voice_fingerprints', {}))

        # --- Render Metric Cards Stacked Vertically ---
        if lens == "Studio Executive":
            uikit.render_metric_card("Market Signal", f"{readiness}/100", help_text="Structural commercial indicators — reference only.")
            uikit.render_metric_card("Budget Tier", dashboard.get('budget_impact', 'Indie'), help_text="Estimated production scale.")
            uikit.render_metric_card("Prod. Complexity", f"{dashboard.get('production_risk_score', 50)}/100", help_text="Complexity vs narrative payoff.")
            uikit.render_metric_card("Locations", str(loc_profile.get('unique_locations', '—')), help_text="Total unique locations.")
            uikit.render_metric_card("Cast Size", str(cast_size if cast_size else '—'), help_text="Total speaking roles.")
            uikit.render_metric_card("Runtime", rt_label)

        elif lens == "Script Coordinator":
            uikit.render_metric_card("Writing Texture", texture, help_text="Cinematic = lean. Novelistic = dense.")
            uikit.render_metric_card("Pacing", pacing)
            uikit.render_metric_card("Page-Turner", f"{pti}/100", help_text="Scene-to-scene momentum signal.")
            uikit.render_metric_card("Scenes", str(total_scenes))
            uikit.render_metric_card("Runtime", rt_label)

        else:  # Story Editor
            uikit.render_metric_card("Page-Turner", f"{pti}/100", help_text="Scene-to-scene momentum signal.")
            uikit.render_metric_card("Pacing", pacing)
            uikit.render_metric_card("Midpoint", dashboard.get('midpoint_status', 'N/A'), help_text="Midpoint structural health.")
            uikit.render_metric_card("Scenes", str(total_scenes))
            
            rt_min = runtime_data.get('estimated_minutes', 0)
            rt_context = f"{rt_min} min"
            rt_help = f"Streaming standard: 90–120m. Feature drama avg: 110–140m."
            uikit.render_metric_card("Runtime", rt_context, help_text=rt_help)

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
            uikit.render_ai_consultant_box(st.session_state[pulse_cache_key], persona=lens, box_title=f"{lens} Pacing Critique")
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
        uikit.render_section_header("🧠", "Narrative Insights", config['diag_desc'])

        diagnoses = writer_intel.get('narrative_diagnosis', [])
        
        # --- Persona Deep Filtering for Diagnostics ---
        EXEC_ICONS = ['🔵', '🔴', '⚖️', '🚫', '👥', '📉', '⚠️', '🎢', '🟠', '✨', '💎']
        EDITOR_ICONS = ['🧵', '⬜', '👻', '✅', '🔵', '🔴', '⭐', '✨', '🟡', '🎢', '🟠', '🗣️', '🧠', '💡', '💎']
        COORD_ICONS = ['✂️', '🔴', '🟠', '🚫', '💎', '⛓️', '🎭', '👥', '🎙️', '🟢', '🗣️', '🧠', '💡', '✨']
        
        filtered_diagnoses = []
        for diag in diagnoses:
            text = diag if isinstance(diag, str) else diag.get('text', str(diag))
            
            is_exec = any(icon in text for icon in EXEC_ICONS)
            is_editor = any(icon in text for icon in EDITOR_ICONS)
            is_coord = any(icon in text for icon in COORD_ICONS)
            
            # Explicit keyword overrides to ensure perfect bucketing
            if "Same Voice" in text:
                is_exec, is_editor, is_coord = False, True, True
            elif "Engagement Drop" in text:
                is_exec, is_editor, is_coord = True, True, False
            elif "Unfilmable" in text:
                is_exec, is_editor, is_coord = True, False, True
                
            if lens == "Studio Executive" and is_exec:
                filtered_diagnoses.append(text)
            elif lens == "Story Editor" and is_editor:
                filtered_diagnoses.append(text)
            elif lens == "Script Coordinator" and is_coord:
                filtered_diagnoses.append(text)

        # Ensure at least something shows if the script is generally good
        if not filtered_diagnoses and diagnoses:
            positives = [d for d in diagnoses if any(i in d for i in ['✅', '✨', '🟢'])]
            filtered_diagnoses = positives if positives else diagnoses[:1]

        if filtered_diagnoses:
            for diag in filtered_diagnoses:
                uikit.render_insight_card(diag)
        else:
            st.success("✅ No structural anomalies detected. Your script is clean.")

        if priorities:
            st.markdown("<br>", unsafe_allow_html=True)
            uikit.render_section_header("⚡", "Priority Fixes", config['fix_desc'])
            
            # --- Persona Deep Filtering for Priorities ---
            pri_limit = 3 if lens == "Story Editor" else 2
            exec_pri_kws = ["boredom", "cut", "engagement", "budget", "unfilmable", "name", "slow"]
            coord_pri_kws = ["dialogue", "show", "unfilmable", "fluff", "prose", "voice", "economy"]
            
            filtered_pri = []
            for p in priorities:
                txt = f"{p.get('action', '')} {p.get('root_cause', '')}".lower()
                if lens == "Studio Executive" and any(k in txt for k in exec_pri_kws):
                    filtered_pri.append(p)
                elif lens == "Script Coordinator" and any(k in txt for k in coord_pri_kws):
                    filtered_pri.append(p)
                elif lens == "Story Editor":
                    filtered_pri.append(p)
                    
            if not filtered_pri and priorities:
                filtered_pri = priorities[:pri_limit]
            
            for i, p in enumerate(filtered_pri[:pri_limit]):
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
        uikit.render_section_header("👥", "Character Dynamics", "Agency and transformation tracking.")
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
    # SECTION: SCENE ECONOMY (Script Coordinator only)
    # =====================================================================
    def render_scene_economy():
        economy_map = dashboard.get('scene_economy_map', {}).get('map', [])
        if not economy_map:
            return
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("📐", "Scene Economy",
            "How efficiently each scene uses its page space. Trim bloated scenes for a tighter read.")

        # Categorize scenes
        bloated = [s for s in economy_map if s.get('score', 0) < 30 and s.get('label') != 'Unknown']
        tight = [s for s in economy_map if s.get('score', 0) >= 70]

        ec1, ec2 = st.columns(2)
        with ec1:
            if bloated:
                st.markdown(f"##### ✂️ Trim Candidates ({len(bloated)})")
                for s in bloated[:5]:
                    st.markdown(f"<div style='background: linear-gradient(90deg, rgba(239,68,68,0.1) 0%, rgba(239,68,68,0.02) 100%); "
                                f"padding: 12px 16px; border-radius: 10px; margin-bottom: 8px; "
                                f"border-left: 3px solid {Theme.SEMANTIC_CRITICAL}; font-size: 0.9rem; "
                                f"box-shadow: 0 4px 12px rgba(0,0,0,0.1); backdrop-filter: blur(8px);'>"
                                f"<span style='color: white;'>Scene {s['scene']}</span> · <b style='color: {Theme.SEMANTIC_CRITICAL};'>{s.get('label', '⚠️')}</b> · Economy: <span style='font-weight: 700;'>{s.get('score', 0)}%</span>"
                                f"</div>", unsafe_allow_html=True)
            else:
                st.success("✅ No bloated scenes detected.")
        with ec2:
            if tight:
                st.markdown(f"##### 💎 Lean Scenes ({len(tight)})")
                for s in tight[:5]:
                    st.markdown(f"<div style='background: linear-gradient(90deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.02) 100%); "
                                f"padding: 12px 16px; border-radius: 10px; margin-bottom: 8px; "
                                f"border-left: 3px solid {Theme.SEMANTIC_GOOD}; font-size: 0.9rem; "
                                f"box-shadow: 0 4px 12px rgba(0,0,0,0.1); backdrop-filter: blur(8px);'>"
                                f"<span style='color: white;'>Scene {s['scene']}</span> · <b style='color: {Theme.SEMANTIC_GOOD};'>{s.get('label', '✨')}</b> · Economy: <span style='font-weight: 700;'>{s.get('score', 0)}%</span>"
                                f"</div>", unsafe_allow_html=True)
            else:
                st.caption("No scenes scored above 70% economy.")

    # =====================================================================
    # SECTION: PRODUCER INTELLIGENCE
    # =====================================================================
    def render_producer_intel():
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header("🏢", "Producer Intelligence",
                                    "Commercial viability, budget estimation & marketplace positioning.")

        loc_profile = dashboard.get('location_profile', {})
        cast_size = len(report.get('voice_fingerprints', {}))

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: uikit.render_metric_card("Production Complexity", f"{dashboard.get('production_risk_score', 50)}/100", help_text="Complexity vs narrative payoff — reference signal.")
        with c2: uikit.render_metric_card("Market Signal", f"{dashboard.get('market_readiness', 50)}/100", help_text="Structural commercial indicators — reference only.")
        with c3: uikit.render_metric_card("Budget Tier", dashboard.get('budget_impact', 'Standard'), help_text="Indie → Studio → Blockbuster.")
        with c4: uikit.render_metric_card("Locations", str(loc_profile.get('unique_locations', '—')), help_text="Unique locations. More = higher budget.")
        with c5: uikit.render_metric_card("Cast", str(cast_size if cast_size else '—'), help_text="Total speaking roles.")
        with c6: uikit.render_metric_card("Midpoint", dashboard.get('midpoint_status', 'N/A'), help_text="Structural health.")

        # Location Insight
        if loc_profile.get('unique_locations', 0) > 0:
            top_loc = loc_profile.get('top_location', 'Unknown')
            top_ratio = loc_profile.get('top_location_ratio', 0)
            loc_count = loc_profile.get('unique_locations', 0)
            if loc_count > 15:
                loc_note = f"⚠️ {loc_count} locations is high — consider consolidating to reduce production costs."
            elif loc_count < 5:
                loc_note = f"✅ {loc_count} locations — lean, production-friendly footprint."
            else:
                loc_note = f"📍 {loc_count} locations. Primary set: **{top_loc}** ({top_ratio:.0%} of scenes)."
            st.caption(loc_note)

        # Comparable Films
        comps = dashboard.get('commercial_comps', [])
        if comps:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 🎬 Comparable Films")
            comp_cols = st.columns(len(comps))
            for i, comp in enumerate(comps):
                with comp_cols[i]:
                    st.markdown(uikit.clean_html(f"""
                    <div class="comp-film-card">
                        <span style="font-size: 1.2rem; margin-right: 8px;">🎥</span>
                        <span style="font-weight: 600; color: white;">{comp}</span>
                    </div>
                    """), unsafe_allow_html=True)

        # Stakes Distribution
        stakes_data = dashboard.get('stakes_profile', {})
        if stakes_data:
            valid_stakes = {'Physical', 'Emotional', 'Social', 'Moral', 'Existential'}
            stakes = {k: v for k, v in stakes_data.items() if k in valid_stakes and isinstance(v, (int, float)) and v > 0}
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

        cache_key = f"ai_summary_{lens}_{hash(str(report.get('meta', {}).get('run_id', '')))}"

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
            st.markdown(uikit.clean_html(f"""
            <div class="mentor-card">
                <div style="font-size: 0.75rem; color: var(--accent-blue); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;">💡 MENTOR INSIGHT</div>
                <div style="color: rgba(244, 246, 251, 0.9); line-height: 1.7; font-weight: 300;">{msg}</div>
            </div>
            """), unsafe_allow_html=True)

    # =====================================================================
    # SECTION: EXPORT — STACKED VERTICALLY
    # =====================================================================
    def render_export():
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
    # PERSONA-RESPONSIVE FLOW — SHOW ONLY WHAT'S NEEDED IN SIDEBAR GRID
    # =====================================================================

    def _safe_render(fn, label):
        """Crash-safe wrapper for section rendering."""
        try:
            fn()
        except Exception as e:
            st.warning(f"⚠️ Could not render {label}. Your analysis data is intact.")
            with st.expander(f"{label} — Technical Details"):
                st.code(str(e))

    # --- Refactored Two-Column Layout ---
    col_aside, col_main = st.columns([1.1, 2.9], gap="large")

    with col_aside:
        # Score card and key metrics list stacked vertically on the left
        _safe_render(render_aside_panel, "Aside Panel")

    with col_main:
        # Title of Dashboard with Persona Details
        st.markdown(uikit.clean_html(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0 0 6px 0 !important; padding: 0 !important; font-size: 1.8rem !important; color: white;">{config['icon']} {config['score_title']}</h3>
            <p style="color: rgba(163, 160, 179, 0.9); font-size: 0.95rem; margin: 0; font-weight: 300; line-height: 1.5;">{config['tagline']}</p>
        </div>
        """), unsafe_allow_html=True)
        



        # High-level AI Consultant Summary box displayed wide at the top
        if isinstance(summary, dict) and summary.get('summary'):
            _safe_render(lambda: uikit.render_ai_consultant_box(summary['summary'], persona=lens), "AI Summary")

        # Act Structure and Dialogue/Action ratio side-by-side above tabs
        act = dashboard.get('act_structure', {})
        dar = dashboard.get('dialogue_action_ratio', {})

        if act or dar:
            st.markdown("<br>", unsafe_allow_html=True)
            ac1, ac2 = st.columns(2)

            with ac1:
                if act and act.get('act1_pct', 0) > 0:
                    st.markdown(uikit.clean_html(f"""
                    <div style="background: rgba(255, 255, 255, 0.03); 
                                backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08);
                                border-radius: var(--radius-lg); padding: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                        <div style="font-weight: 700; margin-bottom: 15px; font-size: 0.85rem; color: white; letter-spacing: 0.05em; text-transform: uppercase;">🎬 Act Structure</div>
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
                    """), unsafe_allow_html=True)

            with ac2:
                if isinstance(dar, dict) and dar.get('global_dialogue_ratio') is not None:
                    d_pct = round(dar.get('global_dialogue_ratio', 0.5) * 100)
                    a_pct = 100 - d_pct
                    bench = round(dar.get('genre_benchmark', 0.5) * 100) if isinstance(dar.get('genre_benchmark'), float) else dar.get('genre_benchmark', 50)
                    st.markdown(uikit.clean_html(f"""
                    <div style="background: rgba(255, 255, 255, 0.03); 
                                backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08);
                                border-radius: var(--radius-lg); padding: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                        <div style="font-weight: 700; margin-bottom: 15px; font-size: 0.85rem; color: white; letter-spacing: 0.05em; text-transform: uppercase;">💬 Dialogue vs Action</div>
                        <div style="display: flex; gap: 3px; height: 26px; border-radius: 6px; overflow: hidden; margin-bottom: 8px;">
                            <div style="width: {max(8, d_pct)}%; background: {Theme.SEMANTIC_INFO};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: #1A1729;">💬 {d_pct}%</div>
                            <div style="width: {max(8, a_pct)}%; background: {Theme.ACCENT_WARM};
                                        display: flex; align-items: center; justify-content: center;
                                        font-size: 0.7rem; font-weight: 700; color: white;">🎬 {a_pct}%</div>
                        </div>
                        <div style="font-size: 0.75rem; color: {Theme.TEXT_MUTED};">
                            {genre} range: {bench - 10}–{bench + 10}% dialogue · Your script: <b>{d_pct}%</b> {'✅' if (bench - 12) <= d_pct <= (bench + 12) else '⚠️'}
                        </div>
                    </div>
                    """), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tab sections inside main content area
        if lens == "Studio Executive":
            tab_pulse, tab_producer, tab_insights, tab_memo, tab_export = st.tabs([
                "📈 Pacing & Tension",
                "🏢 Market & Production",
                "🧠 Narrative Insights",
                "📝 AI Executive Memo",
                "📦 Export & Lab Data"
            ])
            with tab_pulse:
                _safe_render(render_story_pulse, "Tension Map")
            with tab_producer:
                _safe_render(render_producer_intel, "Producer Intel")
            with tab_insights:
                _safe_render(render_diagnostics, "Diagnostics")
            with tab_memo:
                _safe_render(render_coverage_memo, "AI Coverage")
            with tab_export:
                _safe_render(render_export, "Export")

        elif lens == "Script Coordinator":
            tab_pulse, tab_prose, tab_insights, tab_memo, tab_export = st.tabs([
                "📈 Pacing & Tension",
                "📐 Prose & Pacing Flow",
                "🧠 Technical Insights",
                "📝 AI Coordinator Memo",
                "📦 Export & Lab Data"
            ])
            with tab_pulse:
                _safe_render(render_story_pulse, "Tension Map")
            with tab_prose:
                _safe_render(render_scene_economy, "Scene Economy")
                _safe_render(render_scene_turns, "Scene Turns")
            with tab_insights:
                _safe_render(render_diagnostics, "Diagnostics")
            with tab_memo:
                _safe_render(render_coverage_memo, "AI Coverage")
            with tab_export:
                _safe_render(render_export, "Export")

        else:  # Story Editor (Default)
            tab_pulse, tab_insights, tab_characters, tab_producer, tab_memo, tab_export = st.tabs([
                "📈 Pacing & Tension",
                "🧠 Structural Insights",
                "👥 Character Dynamics",
                "🏢 Producer Intel",
                "📝 AI Story Memo",
                "📦 Export & Lab Data"
            ])
            with tab_pulse:
                _safe_render(render_story_pulse, "Tension Map")
            with tab_insights:
                _safe_render(render_diagnostics, "Diagnostics")
                _safe_render(render_mentor, "Mentor")
            with tab_characters:
                _safe_render(render_characters, "Characters")
                _safe_render(render_scene_turns, "Scene Turns")
            with tab_producer:
                _safe_render(render_producer_intel, "Producer Intel")
            with tab_memo:
                _safe_render(render_coverage_memo, "AI Coverage")
            with tab_export:
                _safe_render(render_export, "Export")
