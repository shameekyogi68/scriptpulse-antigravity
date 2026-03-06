import streamlit as st

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the ScriptPulse product sidebar — clean and focused."""
    from app.components import uikit
    
    with st.sidebar:
        # Brand Logo
        _, col_logo, _ = st.columns([0.8, 1.4, 0.8])
        with col_logo:
            st.image("ScriptPulse_Icon.png", use_container_width=True)
        
        uikit.render_sidebar_header("ScriptPulse", "AI Story Intelligence")

        st.markdown("---")

        # How It Works
        st.markdown("#### How It Works")
        st.caption(
            "1. **Upload** your screenplay (PDF, TXT, FDX)\n"
            "2. **Select** your genre\n"
            "3. **Analyze** — get instant feedback\n"
            "4. **Export** professional reports"
        )

        st.markdown("---")

        # Color Guide
        uikit.render_quick_guide()

        st.markdown("---")

        # Engine Info
        st.caption("⚡ **Engine**: ScriptPulse v8.0")
        st.caption("🧠 **Mode**: Fast Heuristics + ML Enhancement")
        st.caption("🔒 **Privacy**: Your scripts are never stored.")

        st.markdown("---")

        # Operator Panel (hidden)
        shadow_mode, high_accuracy_mode = stu.render_operator_panel(
            st.session_state.get('prev_run')
        )

        return {
            'ui_mode': "Unified",
            'force_cloud': True,
            'ablation_config': {
                'use_sbert': False,
                'use_gpt2': False,
                'use_multimodal': False
            },
            'shadow_mode': shadow_mode,
            'high_accuracy_mode': high_accuracy_mode
        }
