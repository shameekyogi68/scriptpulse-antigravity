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
    runtime_mins = runtime_data.get('avg_minutes', 0) if isinstance(runtime_data, dict) else 0
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
        explainer="This chart shows the <b>intensity</b> your script demands from a reader, scene by scene. Peaks are thrilling moments. Valleys are quieter recovery moments."
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
        <b>How to read this chart:</b> The purple line is your story's heartbeat. 
        When it rises into the <span style="color: {Theme.SEMANTIC_CRITICAL};">🔥 red zone</span>, the reader is on the edge of their seat — but staying there too long causes fatigue. 
        When it dips into the <span style="color: {Theme.SEMANTIC_GOOD};">😌 green zone</span>, it's a recovery moment — a breather before the next wave. 
        The <span style="color: {Theme.SEMANTIC_WARNING};">⚡ middle zone</span> is balanced engagement. 
        Great scripts look like a <b>mountain range</b> — peaks and valleys, not a flat line.
    """)

    # =========================================================================
    # SECTION 3: STORY HEALTH DIAGNOSIS
    # =========================================================================
    uikit.render_section_header(
        icon="🩺", 
        title="What Needs Fixing?", 
        explainer=f"ScriptPulse reads your script like a first-time reader and flags potential problems. "
                  f"<b style='color: {Theme.SEMANTIC_CRITICAL};'>Red</b> = Fix this now. "
                  f"<b style='color: {Theme.SEMANTIC_WARNING};'>Orange</b> = Worth a second look. "
                  f"<b style='color: {Theme.SEMANTIC_GOOD};'>Green</b> = You nailed it."
    )
    
    diagnosis = writer_intel.get('narrative_diagnosis', [])
    if diagnosis:
        for diag in diagnosis:
            # Handle both string items (from writer_agent) and dict items (from interpretation_agent)
            if isinstance(diag, dict):
                dtype = diag.get('type', 'Info')
                issue = diag.get('issue', '')
                advice = diag.get('advice', '')
                if dtype == 'Critical':
                    text = f"🔴 **{issue}**: {advice}"
                elif dtype == 'Warning':
                    text = f"🟠 **{issue}**: {advice}"
                elif dtype == 'Insight':
                    text = f"💡 **{issue}**: {advice}"
                else:
                    text = f"🟢 **{issue}**: {advice}"
                uikit.render_insight_card(text)
            else:
                uikit.render_insight_card(str(diag))
    else:
        uikit.render_insight_card("✨ No significant structural issues detected. Your pacing looks solid!")

    # =========================================================================
    # SECTION 4: STRUCTURAL DASHBOARD (Visual Breakdowns)
    # =========================================================================
    uikit.render_section_header(
        icon="🏗️", 
        title="What's Happening Inside Your Script", 
        explainer="Each tab below examines a different aspect of how your script feels to a first-time reader. Think of it as a magnifying glass on your writing."
    )
    
    tabs = st.tabs(["🧠 Sentence Complexity", "💥 Action Weight", "💬 Dialogue Speed", "🎭 Character Juggling", "🌀 Word Freshness", "❤️ Emotional Tone"])
    
    features = report.get('perceptual_features', [])
    if features:
        # Averages from script analysis
        avg_ling = sum(f.get('linguistic_load', {}).get('sentence_length_variance', 0) for f in features) / len(features)
        avg_action = sum(f.get('visual_abstraction', {}).get('action_lines', 0) for f in features) / len(features)
        avg_velocity = sum(f.get('dialogue_dynamics', {}).get('turn_velocity', 0) for f in features) / len(features)
        avg_churn = sum(f.get('referential_load', {}).get('entity_churn', 0) for f in features) / len(features)
        avg_entropy = sum(f.get('entropy_score', 0) for f in features) / len(features)
        
        # Emotional Tone (VADER)
        avg_affective_compound = sum(f.get('affective_load', {}).get('compound', 0) for f in features) / len(features)

        with tabs[0]:
            st.markdown(f'<p class="section-explainer">Are your sentences easy to read, or do they make the reader re-read them?</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Sentence Complexity", f"{avg_ling:.2f}")
            l2.caption("**Low number** = Your sentences are short, punchy, and easy to follow (like a thriller). **High number** = Your sentences are long and layered (like a literary drama). Neither is wrong — it depends on your genre.")
            with st.expander("🔬 For Researchers"):
                st.caption("This measures how much a reader's short-term memory is taxed by long, complex sentences. Longer sentences with multiple sub-clauses require the reader to 'hold' more information before they reach the point.")
            
        with tabs[1]:
            st.markdown(f'<p class="section-explainer">How much descriptive action ("He walks across the room. She slams the door.") fills each scene?</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Action Lines per Scene", f"{avg_action:.1f}")
            l2.caption("**Too high?** Your scenes may feel like novels — the reader has to imagine a lot. **Too low?** Your scenes may feel like talking heads with nothing happening visually. Aim for a balance that matches your story's energy.")
            with st.expander("🔬 For Researchers"):
                st.caption("Readers mentally picture what's happening on screen. Lots of action description makes the reader's brain work harder to 'see' the scene, which is more tiring than reading spoken dialogue.")

        with tabs[2]:
            st.markdown(f'<p class="section-explainer">How fast are your characters talking back and forth? Quick volleys feel intense. Long speeches feel slow.</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Dialogue Speed", f"{avg_velocity:.2f}")
            l2.caption("**High number** = Characters are firing lines at each other rapidly (arguments, comedy, tension). **Low number** = One character is speaking for a long time (exposition, monologues, contemplation). Mix both for great pacing.")
            with st.expander("🔬 For Researchers"):
                st.caption("Quick dialogue exchanges naturally raise the reader's heartbeat and sense of urgency — it's the literary equivalent of a ticking clock. Slower, longer speeches let the reader breathe.")

        with tabs[3]:
            st.markdown(f'<p class="section-explainer">How many characters does the reader have to keep track of at any given time?</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Character Juggling", f"{avg_churn:.2f}")
            l2.caption("**High number** = You introduce many new characters quickly. Readers can comfortably track about 4-5 characters at a time. If this number is too high, consider simplifying crowd scenes or introducing characters more gradually.")
            with st.expander("🔬 For Researchers"):
                st.caption("Studies show people can comfortably track about 4-5 characters at once. Introducing too many characters in a short span forces the reader to keep 'swapping' who's who, which is mentally exhausting and can cause confusion.")

        with tabs[4]:
            st.markdown(f'<p class="section-explainer">Is your writing fresh and surprising, or does it rely on common, expected words?</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            l1.metric("Avg Word Choice Freshness", f"{avg_entropy:.2f}")
            l2.caption("**High number** = Your word choices are unique and surprising — the reader can't predict what's coming next (great for subtext and rich storytelling). **Low number** = Your vocabulary is repetitive or generic — consider varying your word choices to keep the reader engaged.")
            with st.expander("🔬 For Researchers"):
                st.caption("This measures how unpredictable your word choices are. Repetitive, predictable language makes the reader's brain 'tune out' because there's nothing new. Fresh, surprising vocabulary keeps the reader alert and curious.")
            
        with tabs[5]:
            st.markdown(f'<p class="section-explainer">Does your script feel emotionally positive, negative, or neutral overall?</p>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            affective_label = "Positive / Uplifting" if avg_affective_compound > 0.1 else ("Dark / Tense" if avg_affective_compound < -0.1 else "Balanced / Neutral")
            l1.metric("Overall Emotional Tone", affective_label)
            l2.caption(f"Your script's emotional tone reads as **{affective_label}**. A dark/tense tone keeps the reader on edge. A positive tone creates warmth and hope. Most great scripts shift between both across their runtime.")
            with st.expander("🔬 For Researchers"):
                st.caption("Negative emotional language (anger, fear, sadness) creates a physical stress response in readers — their brain treats fictional tension like real-world danger. This is what makes thrillers and horror 'work' without any actual action on screen.")

    else:
        st.info("Cognitive analysis not available.")

    # =========================================================================
    # SECTION 5: REWRITE PRIORITIES
    # =========================================================================
    uikit.render_section_header("✏️", "Your Top To-Do List", "The single most impactful changes you can make in your next draft, ranked by how much they'll improve the reader's experience.")
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
    uikit.render_section_header("🤖", "Ask the AI Story Editor", "Get a plain-English summary of your script's strengths and weaknesses, written like notes from an experienced story editor.")
    if st.button("🪄 Generate AI Consultant Report", type="primary", use_container_width=True):
        import os
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if not api_key: st.error("⚠️ HUGGINGFACE_API_KEY environment variable missing.")
        else:
            with st.spinner("🤖 Consulting... This might take a moment."):
                from scriptpulse.reporters.llm_translator import generate_ai_summary
                summary, err = generate_ai_summary(report, api_key=api_key)
                if summary: st.session_state['ai_summary_cache'] = summary
                else: 
                    st.warning(f"Error: {err}\n\nDon't worry — the detailed analysis and charts above are 100% accurate and don't need AI to work!")

    if st.session_state.get('ai_summary_cache'):
        uikit.render_signal_box("Consultant Analysis", "", st.session_state['ai_summary_cache'], border_color=Theme.ACCENT_PRIMARY)
    
    # Bottom Expander
    st.markdown("---")
    with st.expander("📖 View Your Script", expanded=False):
        st.text_area("Script", value=script_input, height=500, disabled=True, label_visibility="collapsed")
