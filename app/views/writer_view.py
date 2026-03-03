import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_writer_view(report, script_input):
    """Renders the strictly contract-compliant 'The Instrument' interface."""
    
    # === THE EXPERIENCE TIMELINE (vNext.4 Compliance) ===
    st.subheader("Audience attention demand over first exposure")
    
    trace = report.get('temporal_trace', [])
    if trace:
        df = pd.DataFrame(trace)
        
        # Plotly: No axes, no numbers, just soft waves
        fig = go.Figure()
        
        # Soft translucent band for attention demand
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['attentional_signal'],
            fill='tozeroy',
            mode='lines',
            line=dict(color='rgba(93, 93, 255, 0.5)', width=2),
            fillcolor='rgba(93, 93, 255, 0.1)',
            hoverinfo='none' # No numbers on hover
        ))
        
        # Remove all axes/numbers as per contract
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        # Add Milestones (Act Breaks) as soft vertical lines
        turning_points = report.get('writer_intelligence', {}).get('structural_dashboard', {}).get('structural_turning_points', {})
        for tp_name, tp_data in turning_points.items():
            if isinstance(tp_data, dict) and 'scene' in tp_data:
                scene_idx = tp_data['scene']
                fig.add_vline(x=scene_idx, line_width=1, line_dash="dash", line_color="rgba(0,0,0,0.1)")
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.caption("*Rises represent periods of higher audience demand; valleys represent moments of recovery.*")

    # === REFLECTIONS (Non-Evaluative) ===
    st.markdown("### Reflections")
    
    provocations = report.get('writer_intelligence', {}).get('creative_provocations', [])
    if provocations:
        with st.expander("💡 Creative Provocations", expanded=True):
            for p in provocations:
                st.markdown(f"**{p}**")
    
    st.markdown("---")
    
    intent_acks = report.get('intent_acknowledgments', [])
    if intent_acks:
        for ack in intent_acks:
            st.markdown(f"<div class='signal-box'><i class='bi bi-shield-check'></i> {ack}</div>", unsafe_allow_html=True)

    reflections = report.get('reflections', [])
    if reflections:
        for ref in reflections:
            # Reframe as experiential questions/reflections
            st.markdown(f"**Scenes {ref['scene_range'][0]}–{ref['scene_range'][1]}**")
            st.markdown(f"<div class='signal-box'>{ref['reflection']}</div>", unsafe_allow_html=True)
    else:
        # "Why Silence?" Panel (Mandatory)
        silence_msg = report.get('silence_explanation', "Attentional flow appears stable with regular recovery.")
        st.markdown(f"<div class='signal-box'><i class='bi bi-info-circle'></i> {silence_msg}</div>", unsafe_allow_html=True)
        st.caption("Silence indicates a lack of persistent signal patterns, not necessarily 'success'.")

    # === EXECUTIVE AI SUMMARY ===
    st.markdown("---")
    st.subheader("Executive AI Summary")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("*Generate a plain-language summary of your script's structural health using AI.*")
    with col2:
        if st.button("🪄 Run Diagnostics", type="primary", use_container_width=True):
            import os
            # Attempt to pull from Streamlit Secrets first, then local .env
            api_key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
            
            if not api_key:
                st.error("⚠️ Developer Setup Required: Please add `GEMINI_API_KEY` to the Streamlit Cloud 'Secrets' settings menu.")
            else:
                with st.spinner("Consulting the model (Fail-safe active)..."):
                    from scriptpulse.reporters.llm_translator import generate_ai_summary
                    summary, ai_error = generate_ai_summary(report, model="gemini-2.5-flash", api_key=api_key)
                    
                    if summary:
                        st.session_state['ai_summary_cache'] = summary
                        # Inject back into the report object so it appears in exports
                        if 'writer_intelligence' in report:
                            if 'narrative_summary' not in report['writer_intelligence']:
                                report['writer_intelligence']['narrative_summary'] = {}
                            
                            if isinstance(report['writer_intelligence']['narrative_summary'], dict):
                                report['writer_intelligence']['narrative_summary']['summary'] = summary
                            else:
                                report['writer_intelligence']['narrative_summary'] = {"summary": summary}
                    else:
                        st.warning(f"AI Generation Failed: {ai_error or 'Unknown Error'}. Defaulting to heuristic rule-sets.")

    if st.session_state.get('ai_summary_cache'):
        st.success(st.session_state['ai_summary_cache'])

    # === SCRIPT READER ===
    st.markdown("---")
    st.subheader("Script Draft")
    st.text_area("Read", value=script_input, height=500, disabled=True, label_visibility="collapsed")
