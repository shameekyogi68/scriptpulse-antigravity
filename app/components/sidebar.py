import streamlit as st
import json

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the refined navigation sidebar with writer-friendly language."""
    from app.components import uikit
    with st.sidebar:
        # Brand
        _, col_logo, _ = st.columns([1, 1.2, 1])
        with col_logo:
            st.image("ScriptPulse_Icon.png", use_container_width=True)
        uikit.render_sidebar_header("", "YOUR SCREENPLAY ASSISTANT")
        
        st.markdown("---")
        
        # Interface Mode
        st.markdown("### 🎭 How It Works")
        st.info("ScriptPulse reads your script like a first-time reader and gives you clear, actionable feedback on pacing, dialogue, and structure.")

        st.markdown("---")
        
        # Engine Mode — simplified language
        st.markdown("### ⚡ Speed")
        st.success("Fast mode is on. Your script will be analyzed in under a second.")
        
        st.markdown("---")
        
        # Quick Reference — writer-friendly
        uikit.render_quick_guide()
        
        st.markdown("---")
        
        # Operator Panel
        shadow_mode, high_accuracy_mode = stu.render_operator_panel(st.session_state.get('prev_run'))
        
        return {
            'ui_mode': "Unified",
            'force_cloud': True,
            'ablation_config': {'use_sbert': False, 'use_gpt2': False, 'use_multimodal': False},
            'shadow_mode': shadow_mode,
            'high_accuracy_mode': high_accuracy_mode
        }

