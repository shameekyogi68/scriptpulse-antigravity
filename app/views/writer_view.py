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
    c3.metric("Est. Runtime", f"{runtime_mins} min" if runtime_mins else "N/A")
    c4.metric("Midpoint Status", midpoint_status)

    # -------------------------------------------------------------------------
    # SECTION 2: THE STORY PULSE
    uikit.render_section_header(icon="📈", title="The Emotional Rollercoaster (Tension Map)", 
        explainer="This chart tracks the reader's heartbeat. Great scripts look like a mountain range — peaks of tension followed by valleys of calm.")
    
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
    # SECTION 3: YOUR UNIQUE VOICE (Radar Chart)
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="🛠️", title="Character Voice Fingerprints", 
        explainer="Are your characters distinct? This radar shows how your main characters 'sound' differently based on their rhythm and dialogue style.")
    
    voice_data = report.get('voice_fingerprints', {})
    if voice_data:
        top_chars = sorted([(k, v) for k, v in voice_data.items() if isinstance(v, dict)], 
                           key=lambda x: x[1].get('line_count', 0), reverse=True)[:3]
        fig_r = charts.get_voice_radar(top_chars)
        st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False}, key="writer_voice_radar_chart")
    else:
        st.info("Not enough dialogue detected to map distinct character voices.")
        
    habits_insight = st.session_state.get('ai_habits_insight')
    if habits_insight: uikit.render_ai_consultant_box(habits_insight)

    # =========================================================================
    # PHASE 2: THE PRODUCER's DESK (Focus: Mechanics & Viability)
    # =========================================================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("### 🏢 The Producer's Desk")
    
    # -------------------------------------------------------------------------
    # SECTION 4: SCENE PACING MAP (DNA)
    uikit.render_section_header(icon="🧬", title="Scene Pacing Map (Speed vs. Detail)", 
        explainer="The structural 'vibe' of the movie. Action/Thrillers cluster top-left (fast); Dramas cluster bottom-right (detailed).")
    
    df_q = pd.DataFrame([{
        'T_Index': i+1,
        'Pacing_Speed': s.get('attentional_signal', 0.5),
        'Story_Detail': report.get('semantic_flux', [0.5]*len(trace))[i]
    } for i, s in enumerate(trace)])
    
    c_dna1, c_dna2 = st.columns([3, 2])
    with c_dna1:
        fig_q = charts.get_phase_space_chart(df_q)
        st.plotly_chart(fig_q, use_container_width=True, config={'displayModeBar': False}, key="prod_dna_chart")

    with c_dna2:
        stakes_data = dashboard.get('stakes_distribution', {})
        if stakes_data:
            st.markdown("<h5 style='text-align: center; margin-top: 10px;'>Dominant Stakes</h5>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; color: #888; font-size: 13px;'>Are they fighting for physical survival, emotional peace, or status?</div>", unsafe_allow_html=True)
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

    dna_insight = st.session_state.get('ai_dna_insight')
    if dna_insight: uikit.render_ai_consultant_box(dna_insight)

    # -------------------------------------------------------------------------
    # SECTION 5: THE AUDIENCE REACTION MEMO
    st.markdown("<br>", unsafe_allow_html=True)
    uikit.render_section_header(icon="📝", title="Audience Reaction Memo", explainer="A single-page, brutally honest summary of how the script feels to read or watch.")
    
    import os
    has_groq = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    has_gemin = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    has_hf = st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN")

    if st.button("🪄 Generate Audience Reaction", type="primary", use_container_width=True):
        if not (has_groq or has_hf or has_gemin):
            st.error("⚠️ AI Consultant is offline (Missing API Keys).")
        else:
            with st.spinner("🤖 Experiencing the story... (This takes 10-20 seconds)"):
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
    with st.expander("📖 View Original Script Text", expanded=False):
        st.text_area("Script", value=script_input, height=500, disabled=True, label_visibility="collapsed")
