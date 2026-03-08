import streamlit as st

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the ScriptPulse product sidebar — clean and focused."""
    from app.components import uikit
    
    with st.sidebar:
        # Brand Logo
        import os
        ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ScriptPulse_Icon.png")
        _, col_logo, _ = st.columns([0.8, 1.4, 0.8])
        with col_logo:
            st.image(ICON_PATH if os.path.exists(ICON_PATH) else "app/assets/ScriptPulse_Icon.png", use_container_width=True)
        
        # How It Works
        st.markdown("#### How It Works")
        st.caption(
            "1. **Upload** your screenplay (PDF, TXT, FDX)\n"
            "2. **Select** your genre\n"
            "3. **Analyze** — get instant feedback\n"
            "4. **Export** professional reports"
        )

        # System Intelligence & Analysis Depth
        st.markdown("#### Analysis Depth")
        st.caption("🧠 **Multidimensional Evaluation**")
        st.progress(1.0, text="✨ **Narrative Dimensions**: 15+")
        st.progress(1.0, text="📊 **Structural Theory**: 3-Act Logic")
        st.progress(1.0, text="🔬 **Granularity**: Scene-by-Scene")
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(59,130,246,0.15), rgba(59,130,246,0.05)); 
                    border: 1px solid rgba(59, 130, 246, 0.4); border-left: 3px solid #3b82f6;
                    border-radius: 8px; padding: 12px; margin-top: 15px; text-align: center;
                    box-shadow: 0 4px 15px rgba(59,130,246,0.1), inset 0 0 10px rgba(59,130,246,0.05);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <span style="font-size: 1.1rem;">⚡</span>
                <span style="color: #3b82f6; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase;">AI-Powered Analysis</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Engine Info
        st.markdown("<div style='font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 10px;'>⚡ <b>Engine</b>: Script<span style='color: #0052FF; font-weight: 700;'>Pulse</span> v15.0 Gold</div>", unsafe_allow_html=True)
        st.caption("🧠 **Mode**: Hybrid ML + Cognitive Sim")
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
                'use_sbert': True,
                'use_multimodal': False
            },
            'shadow_mode': shadow_mode,
            'high_accuracy_mode': high_accuracy_mode
        }
