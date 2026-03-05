import streamlit as st
import json

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the refined navigation sidebar with writer-friendly language."""
    from app.components import uikit
    with st.sidebar:
        # Brand
        st.image("ScriptPulse_Icon.png", use_container_width=True)
        uikit.render_sidebar_header("ScriptPulse", "SCREENPLAY INTELLIGENCE ENGINE")
        
        st.markdown("---")
        
        # Interface Mode
        st.markdown("### 🎭 Interface")
        st.info("ScriptPulse is currently running in Unified Mode, providing actionable insights for screenwriters backed by deep structural telemetry.")

        st.markdown("---")
        
        # Engine Mode — simplified language
        st.markdown("### ⚡ Processing Speed")
        st.success("Fast Analysis Engine Enabled. Deep AI heuristics are bypassed for maximum performance and determinism.")
        
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

