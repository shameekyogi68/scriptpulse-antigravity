import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts

def render_writer_view(report, script_input, genre="Drama"):
    """
    Renders the Premium ScriptPulse Dashboard.
    Divided logically: Top 50% for the Writer, Bottom 50% for the Studio/Producer.
    """
    
    trace = report.get('temporal_trace', [])
    writer_intel = report.get('writer_intelligence', {})
    dashboard = writer_intel.get('structural_dashboard', {})
    
    if not trace:
        st.warning("No scene data found. Please check your screenplay format.")
        return

    # --- Extract High-Level Intelligence ---
    summary = writer_intel.get('narrative_summary', {})
    priorities = writer_intel.get('rewrite_priorities', [])
    provocations = writer_intel.get('creative_provocations', [])
    char_arcs = dashboard.get('character_arcs', {})

    def get_label(val, low_thresh, high_thresh, low_label="Low", mid_label="Balanced", high_label="High"):
        if val < low_thresh: return low_label
        if val > high_thresh: return high_label
        return mid_label

    # =========================================================================
    # PHASE 1: THE WRITER's ROOM (Focus: Creative Pulse & Rhythm)
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # SECTION 1: THE VITAL SIGNS
    st.markdown("### 🎬 The Writer's Room")
    uikit.render_section_header(icon="📊", title="Vital Signs", explainer=f"A quick summary of your {genre} script's basic health.")
    
    total_scenes = len(trace)
    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0
    pacing_label = get_label(avg_tension, 0.35, 0.65, "Slow Burn", "Steady Pacing", "High Octane")
    
    runtime_data = dashboard.get('runtime_estimate', {})
    runtime_mins = runtime_data.get('avg_minutes', 0) if isinstance(runtime_data, dict) else 0
    midpoint_status = dashboard.get('midpoint_status', 'N/A')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scenes", f"{total_scenes}")
    c2.metric("Pacing Style", pacing_label)
    c3.metric("Page-Turner Index", f"{dashboard.get('page_turner_index', 70)}/100", help="Predicted momentum based on hooks and cliffhangers.")
    c4.metric("Writing Texture", dashboard.get('writing_texture', 'Cinematic'), help="Classification of your prose style based on action density.")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7 = st.columns(3)
    
    # Use the more professional runtime estimate from WriterAgent
    rt_label = "N/A"
    if isinstance(runtime_data, dict):
        rt_minutes = runtime_data.get('estimated_minutes', 0)
        rt_label = f"{rt_minutes} min"
    
    c5.metric("Est. Runtime", rt_label)
    c6.metric("Midpoint Status", midpoint_status)
    c7.metric("Story Market", f"{genre} Masterclass", help="Tuned against industry-standard benchmarks.")

    # -------------------------------------------------------------------------
    # SECTION 1.1: EXECUTIVE NARRATIVE SUMMARY
    if isinstance(summary, dict) and summary.get('summary'):
        uikit.render_ai_consultant_box(summary['summary'])

    # -------------------------------------------------------------------------
    # SECTION 2: THE STORY PULSE
    uikit.render_section_header(icon="📈", title="Narrative Tension Map", 
        explainer="This chart visualizes the script's structural pacing. Effective narratives demonstrate controlled peaks of dramatic conflict followed by releasing valleys.")
    
    for i, p in enumerate(trace):
        intensity = p.get('attentional_signal', 0.5)
        if intensity > 0.8: advice = "<i>Peak intensity.</i>"
        elif intensity < 0.3: advice = "<i>Breather scene.</i>"
        else: advice = "<i>Steady progression.</i>"
        p['Hover_Text'] = advice

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
            fig_display.add_vline(
                x=tp_data['scene'], line_width=1.5, line_dash="dot", line_color=color,
                annotation_text=label, annotation_position="top",
                annotation_font_size=10, annotation_font_color=color
            )
            
    st.plotly_chart(fig_display, use_container_width=True, config={'displayModeBar': False}, key="writer_pulse_chart")
    
    pulse_insight = st.session_state.get('ai_pulse_insight')
    if pulse_insight: uikit.render_ai_consultant_box(pulse_insight)

    # -------------------------------------------------------------------------
    # SECTION 3: NARRATIVE DIAGNOSTICS
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="🧠", title="Structural Diagnostics", 
        explainer="Text-grounded analysis of your scene work. Highlights structural sag, exposition dumps, and action peaks based on data.")
    
    diagnoses = writer_intel.get('narrative_diagnosis', [])
    if diagnoses:
        for diag in diagnoses:
            uikit.render_insight_card(diag)
    else:
        st.success("The narrative progression is clean. No major structural anomalies detected.")

    # -------------------------------------------------------------------------
    # SECTION 3.1: REWRITE PRIORITIES (ACTIONABLE INTELLIGENCE)
    if priorities:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header(icon="⚡", title="Rewrite Priorities", 
            explainer="The top 3 high-leverage changes that will most significantly improve your script's structural integrity.")
        
        for p in priorities:
            # priorities are dicts: {'action': '...', 'leverage': 'High/Medium/Low', 'root_cause': '...'}
            act = p.get('action', 'Unknown Action')
            lev = p.get('leverage', 'Medium')
            cause = p.get('root_cause', '')
            badge = uikit.get_leverage_badge(lev)
            uikit.render_signal_box(f"Impact: {lev}", badge, f"**Action:** {act}<br><small style='color: grey;'>Root Cause: {cause}</small>", border_color=Theme.ACCENT_PRIMARY)

    # -------------------------------------------------------------------------
    # SECTION 3.2: CHARACTER ARC DIAGNOSTICS
    if char_arcs:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header(icon="👥", title="Protagonist Arc Diagnostics", 
            explainer="How your characters transform over the course of the story.")
        
        # Display the top 2 characters by line count
        sorted_chars = sorted(char_arcs.items(), key=lambda x: x[1].get('scenes_present', 0), reverse=True)
        cols = st.columns(min(len(sorted_chars), 2))
        for i, (name, arc) in enumerate(sorted_chars[:2]):
            with cols[i]:
                st.markdown(f"#### {name}")
                st.markdown(f"**Type:** `{arc.get('arc_type')}`")
                st.caption(arc.get('note', ''))
                st.progress((arc.get('agency_end', 0) + 1) / 2) # normalize -1 to 1 into 0 to 1
                st.caption(f"Agency Transformation: {arc.get('agency_start', 0):.2f} → {arc.get('agency_end', 0):.2f}")

    # -------------------------------------------------------------------------
    # SECTION 3.3: MARKETPLACE CONTEXT (10/10 Industry Standard)
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="💎", title="Marketplace Context", 
        explainer="Industry-comparative scripts (comps) with a similar pacing and structural DNA. Vital for pitching to agents or studios.")
    
    comps = dashboard.get('commercial_comps', [])
    col_c1, col_c2, col_c3 = st.columns(3)
    for i, comp in enumerate(comps):
        with [col_c1, col_c2, col_c3][i % 3]:
            st.markdown(f"🎬 **{comp}**")
            st.caption(f"DNA Match: {genre}")

    # -------------------------------------------------------------------------
    # SECTION 3.4: SCENE TURN MAP
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="🎢", title="The Scene-Turn Map", 
        explainer="Professional scripts 'turn' at least once per scene, shifting from positive to negative or vice versa. This chart maps that emotional movement.")
    
    turn_map = dashboard.get('scene_turn_map', [])
    if turn_map:
        turn_df = pd.DataFrame(turn_map)
        # Filter for non-'Flat' turns to show highs
        turns_only = turn_df[turn_df['turn'] != 'Flat']
        if not turns_only.empty:
            st.dataframe(turns_only[['scene', 'turn', 'sentiment_delta']].rename(columns={'turn': 'Emotional Shift', 'sentiment_delta': 'Intensity'}), hide_index=True, use_container_width=True)
        else:
            st.info("No significant intra-scene turns detected. Most scenes maintain a consistent emotional state.")

    # -------------------------------------------------------------------------
    # SECTION 3.4: MENTOR'S CORNER
    if provocations:
        st.markdown("<br>", unsafe_allow_html=True)
        uikit.render_section_header(icon="🧭", title="The Mentor's Corner", 
            explainer="Tough questions to challenge your creative choices and push the craft further.")
        for msg in provocations:
            st.info(f"💡 {msg}")
        
        # The 10/10 "Wow" Feature: Writer's Wildcard
        wildcards = [
            "What if your protagonist and antagonist had to share a car for the entire next act?",
            "Kill off the most 'comfortable' character in the next ten pages.",
            "Write a scene where no one is allowed to speak. They must use objects to communicate.",
            "Switch the locations of your climax and your midpoint. How does the story change?",
            "Make your protagonist's greatest strength their greatest weakness in the next scene."
        ]
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🃏 **The Writer's Wildcard**: {random.choice(wildcards)}")

    # =========================================================================
    # PHASE 2: THE PRODUCER's DESK (Focus: Mechanics & Viability)
    # =========================================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("### 🏢 The Producer's Desk")
    
    # -------------------------------------------------------------------------
    # SECTION 4: INVESTMENT & PRODUCTION AUDIT
    uikit.render_section_header(icon="📉", title="Production Risk Radar", 
        explainer="A studio-grade assessment of the script's budget intensity versus its narrative payoff potential.")
    
    risk_score = dashboard.get('production_risk_score', 50)
    budget_impact = dashboard.get('budget_impact', 'Medium')
    
    c_inv1, c_inv2 = st.columns(2)
    with c_inv1:
        st.metric("Production Risk", f"{risk_score}/100", help="High scores indicate high financial risk (High complexity/Low payoff).")
        st.progress(risk_score / 100)
    with c_inv2:
        st.metric("Budget Intensity", budget_impact, help="Estimated production scale based on location churn and action density.")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION 4.1: DOMINANT STAKES
    uikit.render_section_header(icon="⚖️", title="Dominant Story Stakes", 
        explainer="A breakdown of the central conflicts driving the narrative, categorized by thematic weight.")
    
    stakes_data = dashboard.get('stakes_profile', {})
    if stakes_data:
        stakes = {k: v for k, v in stakes_data.items() if v > 0 and k != 'None'}
        if stakes:
            labels = list(stakes.keys())
            values = list(stakes.values())
            fig_stakes = charts.get_stakes_chart(labels, values, {
                'Physical': Theme.SEMANTIC_CRITICAL, 'Emotional': Theme.SEMANTIC_WARNING,
                'Social': Theme.SEMANTIC_GOOD, 'Moral': Theme.ACCENT_PRIMARY, 'Existential': Theme.ACCENT_PURPLE
            })
            st.plotly_chart(fig_stakes, use_container_width=True, config={'displayModeBar': False}, key="prod_stakes_chart")
        else:
            st.info("No dominant stakes detected.")
    else:
        st.info("No dominant stakes detected.")

    # -------------------------------------------------------------------------
    # SECTION 5: EXECUTIVE COVERAGE MEMO
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="📝", title="Executive Coverage Memo", explainer="A high-level professional assessment of the script's structure, pacing, and commercial viability.")
    
    import os
    has_groq = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    has_gemin = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    has_hf = st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN")

    if st.button("🪄 Generate Executive Coverage", type="primary", use_container_width=True):
        if not (has_groq or has_hf or has_gemin):
            st.error("⚠️ AI Consultant is offline (Missing API Keys).")
        else:
            with st.spinner("🤖 Analyzing the narrative structure... (This takes 10-20 seconds)"):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                lens_persona = st.session_state.get('current_lens', 'viewer')
                summary, err = generate_ai_summary(report, lens=lens_persona)
                if summary: 
                    st.session_state['ai_summary_cache'] = summary
                    st.rerun()
                else: 
                    st.error(f"AI Consultant Error: {err}")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Coverage", "", st.session_state['ai_summary_cache'], border_color=Theme.SEMANTIC_INFO)
    
    # =========================================================================
    # PHASE 3: ARCHIVE & EXPORT
    # =========================================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("📖 View Original Script Text", expanded=False):
            st.text_area("Script", value=script_input, height=300, disabled=True, label_visibility="collapsed")
            
    with col_exp2:
        with st.expander("🧪 Research & Data Export", expanded=False):
            st.write("Download the full raw analytical trace for academic or production use.")
            
            # --- Research Telemetry Viz ---
            st.markdown("##### Research Telemetry")
            telemetry = [s.get('research_telemetry', {}) for s in trace]
            if telemetry:
                avg_conf = sum(t.get('analytical_confidence', 0) for t in telemetry) / len(telemetry)
                avg_dens = sum(t.get('semantic_density', 0) for t in telemetry) / len(telemetry)
                
                t1, t2 = st.columns(2)
                t1.metric("Analytical Confidence", f"{avg_conf:.1%}", help="Combined ML/Heuristic confidence factor. High (>80%) indicates strong NLP model alignment.")
                t2.metric("Avg. Semantic Density", f"{avg_dens:.2f}", help="Lexical diversity per token. High (>3.0) indicates complex, information-dense prose.")
                
                if any(t.get('heuristic_fallback') for t in telemetry):
                    st.caption("⚠️ System utilizing heuristic fallbacks for partial feature extraction.")
            
            st.divider()
            
            import json
            # Sanitize report to be JSON serializable (sometimes sets exist in referential_load)
            def sanitize(obj):
                if isinstance(obj, set): return list(obj)
                if isinstance(obj, dict): return {k: sanitize(v) for k, v in obj.items()}
                if isinstance(obj, list): return [sanitize(x) for x in obj]
                return obj
            
            clean_report = sanitize(report)
            json_str = json.dumps(clean_report, indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name="scriptpulse_analysis.json",
                mime="application/json",
                use_container_width=True
            )
