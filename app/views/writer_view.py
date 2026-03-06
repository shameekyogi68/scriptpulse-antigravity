import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.components.theme import Theme
from app.components import uikit, charts

def render_writer_view(report, script_input, genre="Drama"):
    """
    Renders the Premium Writer Dashboard.
    Designed to function as a high-end digital story consultant.
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
    # SECTION 1: THE VITAL SIGNS
    # =========================================================================
    uikit.render_section_header(
        icon="📊", 
        title="Your Script at a Glance", 
        explainer=f"A quick summary of your {genre} script's basic health."
    )
    
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

    # =========================================================================
    # SECTION 2: THE STORY PULSE
    # =========================================================================
    uikit.render_section_header(
        icon="📈", 
        title="The Emotional Rollercoaster (Tension Map)", 
        explainer="This chart shows how tense the reader feels from scene to scene. Great scripts look like a mountain range — high peaks of tension followed by valleys of calm so the audience can breathe."
    )
    
    # Inject Smart Hover Advice
    for i, p in enumerate(trace):
        intensity = p.get('attentional_signal', 0.5)
        if intensity > 0.8: advice = "<i>Peak intensity. Don't linger here too long.</i>"
        elif intensity < 0.3: advice = "<i>Breather scene. Good place for character focus.</i>"
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
            
    st.plotly_chart(fig_display, use_container_width=True, config={'displayModeBar': False}, key="writer_pulse_chart")
    
    # Display AI Pulse Insight
    pulse_insight = st.session_state.get('ai_pulse_insight')
    if pulse_insight:
        uikit.render_ai_consultant_box(pulse_insight)
    
    # =========================================================================
    # SECTION 3: THE STYLE QUADRANT
    # =========================================================================
    uikit.render_section_header(
        icon="🧬", 
        title="Scene Pacing Map (Speed vs. Detail)", 
        explainer="We plot every scene to show if it's fast and action-packed, or slow and dialogue-heavy."
    )
    
    df_q = pd.DataFrame([{
        'T_Index': i+1,
        'Energy_Signal': s.get('attentional_signal', 0.5),
        'Entropy_Complexity': report.get('semantic_flux', [0.5]*len(trace))[i],
        'Quadrant': '🔥 Climax' if s.get('attentional_signal', 0.5) > 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] > 0.5 else
                    '⚡ Action' if s.get('attentional_signal', 0.5) > 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] <= 0.5 else
                    '😌 Breather' if s.get('attentional_signal', 0.5) <= 0.5 and report.get('semantic_flux', [0.5]*len(trace))[i] <= 0.5 else '🔮 Mystery'
    } for i, s in enumerate(trace)])
    
    c_dna1, c_dna2 = st.columns([3, 2])
    
    with c_dna1:
        fig_q = charts.get_phase_space_chart(df_q)
        st.plotly_chart(fig_q, use_container_width=True, config={'displayModeBar': False}, key="writer_dna_chart")
        st.markdown("<div style='text-align: center; color: #888; font-size: 13px;'><i>Action/Thrillers usually sit in the top-left (fast). Dramas sit in the bottom-right (detailed).</i></div>", unsafe_allow_html=True)

    with c_dna2:
        stakes_data = dashboard.get('stakes_distribution', {})
        if stakes_data:
            st.markdown("<h5 style='text-align: center; margin-top: 10px;'>What's at Stake?</h5>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; color: #888; font-size: 12px; margin-bottom: 5px;'>Are your characters fighting for survival, status, or their soul?</div>", unsafe_allow_html=True)
            stakes = {k: v for k, v in stakes_data.items() if v > 0 and k != 'None'}
            if stakes:
                labels = list(stakes.keys())
                values = list(stakes.values())
                fig_stakes = charts.get_stakes_chart(labels, values, {
                    'Physical': Theme.SEMANTIC_CRITICAL,
                    'Emotional': Theme.SEMANTIC_WARNING,
                    'Social': Theme.SEMANTIC_GOOD,
                    'Moral': Theme.ACCENT_PRIMARY,
                    'Existential': Theme.ACCENT_PURPLE
                })
                st.plotly_chart(fig_stakes, use_container_width=True, config={'displayModeBar': False}, key="writer_stakes_chart")
            else:
                st.info("No dominant stakes detected.")
    
    # Display AI DNA Insight
    dna_insight = st.session_state.get('ai_dna_insight')
    if dna_insight:
        uikit.render_ai_consultant_box(dna_insight)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 4: THE EDITOR'S DESK (ACTION PLAN)
    # =========================================================================
    uikit.render_section_header(
        icon="🖋️", 
        title="Your Rewrite Action Plan", 
        explainer="A prioritized to-do list for your next draft."
    )
    
    diagnosis = writer_intel.get('narrative_diagnosis', [])
    priorities = writer_intel.get('rewrite_priorities', [])
    
    d_col, p_col = st.columns([1, 1])
    
    with d_col:
        st.markdown(f"##### Story Diagnostic (What's Working & What's Broken)")
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if diagnosis:
            for diag in diagnosis:
                if isinstance(diag, dict):
                    dtype = diag.get('type', 'Info')
                    issue = diag.get('issue', '')
                    advice = diag.get('advice', '')
                    icon = "🔴" if dtype == 'Critical' else ("🟠" if dtype == 'Warning' else "🟢")
                    uikit.render_insight_card(f"{icon} **{issue}**: {advice}")
                else:
                    uikit.render_insight_card(diag)
        else:
            uikit.render_insight_card("✅ Clean Bill of Health: No major structural issues detected!")
            
    with p_col:
        st.markdown(f"##### Where to Focus Your Rewrite")
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if priorities:
            for i, prio in enumerate(priorities[:3], 1):
                action = prio.get('action', str(prio))
                badge = uikit.get_leverage_badge(prio.get('leverage', 'Low'))
                uikit.render_signal_box(f"Fix #{i}", badge, action, border_color=Theme.ACCENT_PRIMARY)
        else:
            uikit.render_signal_box("You're Good!", "", "No urgent rewrite priorities identified. Keep writing!", border_color=Theme.SEMANTIC_GOOD)
            
        provocations = writer_intel.get('creative_provocations', [])
        if provocations:
            st.markdown("<br>##### 💡 Questions to Spark Your Rewrite", unsafe_allow_html=True)
            for p in provocations[:2]:
                uikit.render_insight_card(f"💭 {p}")
                
        econ_map = dashboard.get('scene_economy_map', {})
        cut_candidates = econ_map.get('cut_candidates', [])
        if cut_candidates:
            st.markdown("<br>##### ✂️ Scenes to Trim", unsafe_allow_html=True)
            scenes_str = ", ".join(map(str, cut_candidates))
            uikit.render_insight_card(f"**Trim Candidates:** Consider tightening **Scenes {scenes_str}**. They have a lot of words but don't move the story forward quickly.")

    # =========================================================================
    # SECTION 5: CRAFT HABITS
    # =========================================================================
    uikit.render_section_header(
        icon="🛠️", 
        title="Your Unique Writer's Voice", 
        explainer="How your specific choice of words feels to the reader."
    )
    
    tabs = st.tabs(["🧠 Readability", "💥 Action Density", "💬 Dialogue Rhythm", "👥 Speaking Cast", "🎭 Dominant Tone", "🤫 Subtext"])
    
    features = report.get('perceptual_features', [])
    if features:
        avg_ling = sum(f.get('linguistic_load', {}).get('sentence_length_variance', 0) for f in features) / len(features)
        avg_action = sum(f.get('visual_abstraction', {}).get('action_lines', 0) for f in features) / len(features)
        avg_velocity = sum(f.get('dialogue_dynamics', {}).get('turn_velocity', 0) for f in features) / len(features)
        avg_churn = sum(f.get('referential_load', {}).get('entity_churn', 0) for f in features) / len(features)
        avg_affective_compound = sum(f.get('affective_load', {}).get('compound', 0) for f in features) / len(features)

        with tabs[0]:
            label = get_label(avg_ling, 20, 50, "Punchy & Direct", "Varied Flow", "Layered & Rich")
            st.markdown(f"**Style:** {label}")
            st.caption("Do your sentences read fast and punchy like a thriller, or are they poetic and descriptive like a novel?")
            
        with tabs[1]:
            label = get_label(avg_action, 5, 12, "Sparse", "Visual", "Novelistic")
            st.markdown(f"**Action Density:** {label}")
            st.caption("How much physical action you describe. 'Novelistic' means you describe the world in detail; 'Sparse' means scenes are mostly driven by dialogue.")

        with tabs[2]:
            label = get_label(avg_velocity, 0.4, 0.7, "Monologues", "Natural", "Rapid-Fire Exhanges")
            st.markdown(f"**Dialogue Rhythm:** {label}")
            st.caption("How fast characters trade lines. Rapid-Fire dialogue raises the reader's heart rate. Monologues slow the pace to focus on emotion or theme.")

        with tabs[3]:
            label = get_label(avg_churn, 2, 5, "Tight Cast", "Medium", "Large Ensemble")
            st.markdown(f"**Speaking Cast:** {label}")
            st.caption("How many characters speak in each scene. A 'Tight Cast' keeps the focus intimate; a 'Large Ensemble' can feel epic but risks confusing the reader.")
            
        with tabs[4]:
            affective_label = "Positive / Hopeful" if avg_affective_compound > 0.1 else ("Dark / Suspenseful" if avg_affective_compound < -0.1 else "Neutral")
            st.markdown(f"**Dominant Tone:** {affective_label}")
            st.caption("The overall emotional feel of your words. A 'Dark' tone naturally builds stress and suspense for the audience.")
            
        with tabs[5]:
            subtext = report.get('subtext_audit', [])
            if subtext:
                st.markdown(f"**Literal Dialogue Detected**")
                st.caption("Some scenes might have characters stating exactly how they feel, leaving no room for subtext.")
                for s in subtext[:3]:
                    st.code(f"Scene {s.get('scene_index', '?')}: {s.get('issue', 'Dialogue feels literal.')}")
            else:
                st.markdown(f"**Subtext:** Strong ✅")
                st.caption("Your dialogue has good layers of subtext. Characters are showing, not just telling.")

    # Display AI Habits Insight
    habits_insight = st.session_state.get('ai_habits_insight')
    if habits_insight:
        uikit.render_ai_consultant_box(habits_insight)

    # =========================================================================
    # SECTION 6: STUDIO MEMO (AI EDITOR)
    # =========================================================================
    uikit.render_section_header("📝", "Studio Notes", "One page of professional coverage summarizing the script.")
    
    # Check if we have either provider available
    import os
    has_groq = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    has_hf = st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")

    if st.button("🪄 Generate Studio Notes", type="primary", use_container_width=True):
        if not (has_groq or has_hf):
            st.error("⚠️ AI Consultant is offline (Missing API Keys). Please set GROQ_API_KEY or HF_TOKEN in your secrets.")
        else:
            with st.spinner("🤖 Reviewing..."):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                summary, err = generate_ai_summary(report)
                if summary: 
                    st.session_state['ai_summary_cache'] = summary
                    st.rerun()
                else: 
                    st.error(f"AI Consultant Error: {err}")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Coverage", "", st.session_state['ai_summary_cache'], border_color=Theme.SEMANTIC_INFO)
    
    st.markdown("---")
    with st.expander("📖 View Script Text", expanded=False):
        st.text_area("Script", value=script_input, height=500, disabled=True, label_visibility="collapsed")

