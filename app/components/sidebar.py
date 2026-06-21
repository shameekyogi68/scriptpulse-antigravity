# MODULE: sidebar.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import streamlit as st

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the ScriptPulse product sidebar — market release."""
    from app.components import uikit
    
    with st.sidebar:
        # How It Works
        st.markdown("#### How It Works")
        st.markdown("""
        <div style="font-size: 0.82rem; color: rgba(244,246,251,0.8); line-height: 2.0;">
            <div style="margin-bottom: 4px;"><span style="background: rgba(0,82,255,0.15); color: #5B9AFF; border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 0.7rem; margin-right: 8px;">1</span> Upload your screenplay</div>
            <div style="margin-bottom: 4px;"><span style="background: rgba(0,82,255,0.15); color: #5B9AFF; border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 0.7rem; margin-right: 8px;">2</span> Select genre & perspective</div>
            <div style="margin-bottom: 4px;"><span style="background: rgba(0,82,255,0.15); color: #5B9AFF; border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 0.7rem; margin-right: 8px;">3</span> Get instant AI analysis</div>
            <div><span style="background: rgba(0,82,255,0.15); color: #5B9AFF; border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 0.7rem; margin-right: 8px;">4</span> Export pro reports</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Capabilities
        st.markdown("#### Capabilities")
        st.markdown("""
        <div style="font-size: 0.78rem; line-height: 2.1; color: rgba(244,246,251,0.7);">
            <div>📊 <b>Audience Experience Signals</b></div>
            <div>🎬 <b>Structural & Pacing Analysis</b></div>
            <div>🔬 <b>Scene-by-Scene Granularity</b></div>
            <div>🎭 <b>Character Voice Distinction</b></div>
            <div>🧠 <b>Optional AI Coverage Memos</b></div>
            <div>📥 <b>Pro Export (Writer / Studio / Summary)</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(0,82,255,0.12), rgba(0,82,255,0.04)); 
                    border: 1px solid rgba(0, 82, 255, 0.25); border-left: 3px solid #0052FF;
                    border-radius: 8px; padding: 12px; margin-top: 15px; text-align: center;
                    box-shadow: 0 4px 15px rgba(0,82,255,0.08);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <span style="font-size: 1.1rem;">⚡</span>
                <span style="color: #5B9AFF; font-weight: 800; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase;">AI-Powered Analysis</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Engine Info
        st.markdown("""
        <div style="font-size: 0.78rem; color: rgba(255,255,255,0.5); margin-top: 10px;">
            ⚡ <b>Engine</b>: Script<span style="color: #0052FF; font-weight: 700;">Pulse</span> v1.0
        </div>
        """, unsafe_allow_html=True)
        st.caption("🧠 **Mode**: Hybrid analysis (heuristic fallback when ML unavailable)")
        st.caption("🔒 **Privacy**: Session-only processing")
        st.caption("📊 **Metrics**: Genre-calibrated reference signals — not quality verdicts")
        st.caption("© 2026 ScriptPulse")

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
