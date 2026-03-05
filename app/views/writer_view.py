import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts

def render_writer_view(report, script_input):
    """
    Renders the Writer Mode interface — designed to be immediately 
    understandable by a screenwriter with ZERO technical background.
    """
    
    trace = report.get('temporal_trace', [])
    writer_intel = report.get('writer_intelligence', {})
    dashboard = writer_intel.get('structural_dashboard', {})
    
    if not trace:
        st.warning("No scene data found. Please check your screenplay format.")
        return

    # =========================================================================
    # SECTION 1: SCRIPT OVERVIEW (At a Glance)
    # =========================================================================
    uikit.render_section_header(
        icon="📊", 
        title="Your Script at a Glance", 
        explainer="These are the key vital signs of your screenplay — think of them like a health checkup for your story's structure."
    )
    
    # Calculate user-friendly metrics
    total_scenes = len(trace)
    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0
    tension_label = "High" if avg_tension > 0.65 else ("Balanced" if avg_tension > 0.35 else "Low")
    
    runtime_data = dashboard.get('runtime_estimate', {})
    runtime_mins = runtime_data.get('estimated_minutes', 0) if isinstance(runtime_data, dict) else 0
    midpoint_status = dashboard.get('midpoint_status', 'N/A')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scenes", f"{total_scenes}", help="Number of individual scenes detected in your screenplay.")
    c2.metric("Pacing Feel", tension_label, help="**High** = Non-stop intensity (risk of fatigue).\n**Balanced** = Good rhythm between action and rest.\n**Low** = May feel too slow in places.")
    c3.metric("Estimated Runtime", f"{runtime_mins} min" if runtime_mins else "N/A", help="Estimated screen time based on scene structure and dialogue density.")
    c4.metric("Midpoint Energy", midpoint_status, help="**Healthy** = Strong energy at the story's midpoint — the audience stays hooked.\n**Sagging** = The middle loses momentum — the most common screenplay problem.")

    # =========================================================================
    # SECTION 2: EMOTIONAL JOURNEY (The Main Graph)
    # =========================================================================
    uikit.render_section_header(
        icon="📈", 
        title="Your Story's Emotional Journey", 
        explainer="This chart shows how much <b>mental energy</b> your script demands from a reader, scene by scene. Peaks are intense moments. Valleys are quieter recovery moments."
    )
    
    df = pd.DataFrame(trace)
    fig = charts.get_engagement_chart(df)
    
    # Mark structural turning points (these are dynamic so we add them to the cached figure)
    # Note: Adding markers to a cached figure should be done via a copy to avoid mutation issues
    fig_display = go.Figure(fig)
    turning_points = dashboard.get('structural_turning_points', {})
    tp_config = {
        'inciting_incident': (Theme.SEMANTIC_WARNING, 'Inciting Incident'),
        'act1_break': (Theme.SEMANTIC_CRITICAL, 'Act 1 Break'),
        'midpoint': (Theme.ACCENT_PRIMARY, 'Midpoint'),
        'act2_break': (Theme.SEMANTIC_INFO, 'Act 2 Break / Darkest Moment')
    }
    
    for tp_key, (color, label) in tp_config.items():
        tp_data = turning_points.get(tp_key, {})
        if isinstance(tp_data, dict) and 'scene' in tp_data:
            fig_display.add_vline(
                x=tp_data['scene'], line_width=1.5, line_dash="dot", line_color=color,
                annotation_text=label, annotation_position="top",
                annotation_font_size=10, annotation_font_color=color
            )
            
    st.plotly_chart(fig_display, use_container_width=True, config={'displayModeBar': False})
    uikit.render_tooltip_card(f"""
        <b>Reading the Chart:</b> The colored dotted lines mark your story's major structural beats — 
        <span style="color: {Theme.SEMANTIC_WARNING};">Inciting Incident</span>, 
        <span style="color: {Theme.SEMANTIC_CRITICAL};">Act 1 Break</span>, 
        <span style="color: {Theme.ACCENT_PRIMARY};">Midpoint</span>, and 
        <span style="color: {Theme.SEMANTIC_INFO};">Darkest Moment</span>.
    """)

    # =========================================================================
    # SECTION 3: STORY HEALTH DIAGNOSIS
    # =========================================================================
    uikit.render_section_header(
        icon="🩺", 
        title="Story Health Check", 
        explainer=f"ScriptPulse has identified the following patterns in your script. "
                  f"<b style='color: {Theme.SEMANTIC_CRITICAL};'>Red items</b> are critical issues. "
                  f"<b style='color: {Theme.SEMANTIC_WARNING};'>Orange items</b> are worth fixing. "
                  f"<b style='color: {Theme.SEMANTIC_GOOD};'>Green items</b> are things you do well."
    )
    
    diagnosis = writer_intel.get('narrative_diagnosis', [])
    if diagnosis:
        for diag in diagnosis:
            uikit.render_insight_card(diag)
    else:
        uikit.render_insight_card("✨ No significant structural issues detected. Your pacing looks solid!")

    # =========================================================================
    # SECTION 4: STRUCTURAL DASHBOARD (Visual Breakdowns)
    # =========================================================================
    uikit.render_section_header(
        icon="🏗️", 
        title="Structural Breakdown", 
        explainer="Dive deeper into specific aspects of your script's architecture. Each tab focuses on a different dimension."
    )
    
    tabs = st.tabs(["🧠 Linguistic Load", "💥 Action Density", "💬 Dialogue Rhythm", "🎭 Character Tracking", "🌀 Narrative Entropy"])
    
    features = report.get('perceptual_features', [])
    if features:
        # Averages from mathematical extraction
        avg_ling = sum(f.get('linguistic_load', {}).get('sentence_length_variance', 0) for f in features) / len(features)
        avg_action = sum(f.get('visual_abstraction', {}).get('action_lines', 0) for f in features) / len(features)
        avg_velocity = sum(f.get('dialogue_dynamics', {}).get('turn_velocity', 0) for f in features) / len(features)
        avg_churn = sum(f.get('referential_load', {}).get('entity_churn', 0) for f in features) / len(features)
        avg_entropy = sum(f.get('entropy_score', 0) for f in features) / len(features)

        with tabs[0]:
            st.markdown(f'<p class="section-explainer">How hard the reader\'s brain works to parse your sentences.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Syntactic Variance", f"{avg_ling:.2f}")
            l2.caption("Higher variance means complex, nested sentences. Lower means punchy, fast-reading lines.")
            
        with tabs[1]:
            st.markdown(f'<p class="section-explainer">The visual, cinematic weight of your action descriptions.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Action Lines per Scene", f"{avg_action:.1f}")
            l2.caption("Heavy action density requires the reader to use spatial imagination, increasing engagement but also fatigue over time.")

        with tabs[2]:
            st.markdown(f'<p class="section-explainer">The tempo and volley of your conversations.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Turn Velocity", f"{avg_velocity:.2f}")
            l2.caption("Turn Velocity measures how rapidly characters speak and react in a scene. High velocity = high tension/comedy. Low velocity = exposition/monologues.")

        with tabs[3]:
            st.markdown(f'<p class="section-explainer">The mental tax of tracking who is in the room.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Entity Churn", f"{avg_churn:.2f}")
            l2.caption("Entity Churn spikes when you introduce many new characters at once. Keep it low in action scenes to avoid confusing the reader.")

        with tabs[4]:
            st.markdown(f'<p class="section-explainer">The mathematical measurement of surprise and freshness in your vocabulary.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Information Entropy", f"{avg_entropy:.2f}")
            l2.caption("Uses Shannon's Entropy. High entropy = unpredictable, rare words (Rich subtext). Low entropy = generic, expected words (Predictable/Cliché).")
    else:
        st.info("Cognitive analysis not available.")

    # =========================================================================
    # SECTION 5: REWRITE PRIORITIES
    # =========================================================================
    uikit.render_section_header("✏️", "Top Rewrite Priorities", "Highest-impact changes to improve the reader's experience.")
    priorities = writer_intel.get('rewrite_priorities', [])
    if priorities:
        for i, prio in enumerate(priorities, 1):
            action = prio.get('action', str(prio))
            badge = uikit.get_leverage_badge(prio.get('leverage', 'Low'))
            uikit.render_signal_box(f"Priority #{i}", badge, action)
    else: uikit.render_insight_card("✅ No urgent priorities detected.")

    # =========================================================================
    # SECTION 6: AI CONSULTANT
    # =========================================================================
    uikit.render_section_header("🤖", "AI Script Consultant", "Detailed, plain-language evaluation from an AI script consultant.")
    if st.button("🪄 Generate AI Consultant Report", type="primary", use_container_width=True):
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: st.error("⚠️ API key missing.")
        else:
            with st.spinner("🤖 Consulting..."):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                summary, err = generate_ai_summary(report, model="gemini-2.0-flash", api_key=api_key)
                if summary: st.session_state['ai_summary_cache'] = summary
                else: 
                    if "429" in str(err) or "Quota" in str(err):
                        st.warning("⚠️ Google Gemini AI Quota Exceeded. The AI Consultant is currently too busy to generate a text summary. Please rely on the highly detailed mathematical Cognitive Pillars and Diagnostic charts above, which are 100% accurate and unaffected by this AI quota!")
                    else:
                        st.warning(f"Error: {err}")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Consultant Analysis", "", st.session_state['ai_summary_cache'], border_color=Theme.ACCENT_PRIMARY)
    
    # Bottom Expander
    st.markdown("---")
    with st.expander("📖 View Your Script", expanded=False):
        st.text_area("Script", value=script_input, height=500, disabled=True, label_visibility="collapsed")
