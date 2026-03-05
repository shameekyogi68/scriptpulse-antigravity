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

    def get_label(val, low_thresh, high_thresh, low_label="Low", mid_label="Balanced", high_label="High"):
        if val < low_thresh: return low_label
        if val > high_thresh: return high_label
        return mid_label

    # =========================================================================
    # SECTION 1: THE BIG PICTURE
    # =========================================================================
    uikit.render_section_header(
        icon="📊", 
        title="Your Script at a Glance", 
        explainer="These are the key vital signs of your screenplay — think of them like a health checkup for your story's structure."
    )
    
    total_scenes = len(trace)
    avg_tension = sum(p.get('attentional_signal', 0) for p in trace) / total_scenes if total_scenes > 0 else 0
    pacing_label = get_label(avg_tension, 0.35, 0.65, "Slow", "Steady", "Intense")
    
    runtime_data = dashboard.get('runtime_estimate', {})
    runtime_mins = runtime_data.get('avg_minutes', 0) if isinstance(runtime_data, dict) else 0
    midpoint_status = dashboard.get('midpoint_status', 'N/A')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scenes", f"{total_scenes}")
    c2.metric("Pacing Feel", pacing_label)
    c3.metric("Estimated Runtime", f"{runtime_mins} min" if runtime_mins else "N/A")
    c4.metric("Midpoint Momentum", midpoint_status)

    # =========================================================================
    # SECTION 2: THE EMOTIONAL JOURNEY
    # =========================================================================
    uikit.render_section_header(
        icon="📈", 
        title="The Reader's Heartbeat", 
        explainer="This chart shows the <b>intensity</b> of your script, scene by scene. Great scripts look like a mountain range — peaks of action and valleys of rest."
    )
    
    df = pd.DataFrame(trace)
    fig = charts.get_engagement_chart(df)
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
    
    # =========================================================================
    # SECTION 3: THE ACTION PLAN
    # =========================================================================
    uikit.render_section_header(
        icon="✏️", 
        title="Your Rewriting Action Plan", 
        explainer="Based on the analysis, here are the most impactful changes you can make to improve your script's flow."
    )
    
    diagnosis = writer_intel.get('narrative_diagnosis', [])
    priorities = writer_intel.get('rewrite_priorities', [])
    
    if diagnosis or priorities:
        d_col, p_col = st.columns(2)
        with d_col:
            st.markdown("##### 🩺 Structural Health Check")
            if diagnosis:
                for diag in diagnosis:
                    if isinstance(diag, dict):
                        dtype = diag.get('type', 'Info')
                        issue = diag.get('issue', '')
                        advice = diag.get('advice', '')
                        icon = "🔴" if dtype == 'Critical' else ("🟠" if dtype == 'Warning' else "🟢")
                        st.markdown(f"{icon} **{issue}**: {advice}")
                    else:
                        st.markdown(diag)
            else:
                st.markdown("✅ No major structural issues detected.")
                
        with p_col:
            st.markdown("##### ✍️ Top Rewrite Priorities")
            if priorities:
                for i, prio in enumerate(priorities[:3], 1):
                    action = prio.get('action', str(prio))
                    badge = uikit.get_leverage_badge(prio.get('leverage', 'Low'))
                    st.markdown(f"**#{i}** {badge}<br/>{action}", unsafe_allow_html=True)
            else:
                st.markdown("✨ Your to-do list is clean!")
    else:
        uikit.render_insight_card("Your script looks solid! No major changes suggested.")

    # =========================================================================
    # SECTION 4: DEEP DIVE DASHBOARD
    # =========================================================================
    uikit.render_section_header(
        icon="🏗️", 
        title="Under the Magnifying Glass", 
        explainer="Check the tabs below to see how specific writing habits are affecting your script's feel."
    )
    
    tabs = st.tabs(["🧠 Language", "💥 Action", "💬 Dialogue", "🎭 Characters", "🌀 Vocabulary", "❤️ Tone"])
    
    features = report.get('perceptual_features', [])
    if features:
        avg_ling = sum(f.get('linguistic_load', {}).get('sentence_length_variance', 0) for f in features) / len(features)
        avg_action = sum(f.get('visual_abstraction', {}).get('action_lines', 0) for f in features) / len(features)
        avg_velocity = sum(f.get('dialogue_dynamics', {}).get('turn_velocity', 0) for f in features) / len(features)
        avg_churn = sum(f.get('referential_load', {}).get('entity_churn', 0) for f in features) / len(features)
        avg_entropy = sum(f.get('entropy_score', 0) for f in features) / len(features)
        avg_affective_compound = sum(f.get('affective_load', {}).get('compound', 0) for f in features) / len(features)

        with tabs[0]:
            label = get_label(avg_ling, 20, 50, "Punchy", "Balanced", "Layered")
            st.markdown(f"**Style:** {label}")
            st.caption("**Punchy** = Short, easy sentences (Thrillers/Action). **Layered** = Long, rich sentences (Literary Drama).")
            with st.expander("🔬 Why this matters?"):
                st.caption("This measures how much a reader's short-term memory is taxed. Long sentences require more focus to follow.")
            
        with tabs[1]:
            label = get_label(avg_action, 5, 12, "Sparse", "Visual", "Dense")
            st.markdown(f"**Action Weight:** {label}")
            st.caption("**Sparse** = Focus on dialogue. **Dense** = Very visual, like a novel.")
            with st.expander("🔬 Why this matters?"):
                st.caption("Readers 'see' action lines. Too much description is tiring; too little feels like 'talking heads'.")

        with tabs[2]:
            label = get_label(avg_velocity, 0.4, 0.7, "Long Speeches", "Natural", "Rapid Fire")
            st.markdown(f"**Dialogue Speed:** {label}")
            st.caption("**Rapid Fire** = Characters firing lines quickly. **Long Speeches** = Monologues or exposition.")
            with st.expander("🔬 Why this matters?"):
                st.caption("Quick exchanges raise the reader's pulse. Slower ones let them absorb information.")

        with tabs[3]:
            label = get_label(avg_churn, 2, 5, "Tight Cast", "Medium", "Large Ensemble")
            st.markdown(f"**Character Load:** {label}")
            st.caption("**Tight Cast** = Few characters to track. **Large Ensemble** = Many characters appearing at once.")
            with st.expander("🔬 Why this matters?"):
                st.caption("Readers can track ~4-5 characters at once. More than that causes confusion.")

        with tabs[4]:
            label = get_label(avg_entropy, 4, 8, "Simple/Direct", "Varied", "Rich/Unique")
            st.markdown(f"**Word Choice:** {label}")
            st.caption("**Simple** = Functional language. **Rich** = Surprising, unique word choices.")
            with st.expander("🔬 Why this matters?"):
                st.caption("Predictable language bores the brain. Surprising vocabulary keeps the reader alert.")
            
        with tabs[5]:
            affective_label = "Positive / Uplifting" if avg_affective_compound > 0.1 else ("Dark / Tense" if avg_affective_compound < -0.1 else "Balanced / Neutral")
            st.markdown(f"**Overall Tone:** {affective_label}")
            st.caption(f"Your script feels **{affective_label}** overall.")
            with st.expander("🔬 Why this matters?"):
                st.caption("Dark tones create physical suspense; positive tones create hope and warmth.")

    # =========================================================================
    # SECTION 5: AI STORY EDITOR
    # =========================================================================
    uikit.render_section_header("🤖", "Ask the AI Story Editor", "A plain-English summary of your draft's strengths, written like notes from a pro editor.")
    if st.button("🪄 Get AI Story Notes", type="primary", use_container_width=True):
        import os
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if not api_key: st.error("⚠️ AI Consultant is currently offline (Missing API Key).")
        else:
            with st.spinner("🤖 Reviewing your script..."):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                summary, err = generate_ai_summary(report, api_key=api_key)
                if summary: st.session_state['ai_summary_cache'] = summary
                else: st.warning(f"Error: {err}. Please check back later.")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Editor's Notes", "", st.session_state['ai_summary_cache'], border_color=Theme.ACCENT_PRIMARY)
    
    st.markdown("---")
    with st.expander("📖 View Script Text", expanded=False):
        st.text_area("Script", value=script_input, height=500, disabled=True, label_visibility="collapsed")

