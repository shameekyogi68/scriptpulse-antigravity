import streamlit as st
import json

def render_sidebar(ui_mode, is_cloud, stu):
    """Renders the main navigation and orientation sidebar."""
    with st.sidebar:
        st.title("ScriptPulse")
        st.caption("Writer-Native Analytics (or Research Platform)")
        
        st.markdown("---")
        new_ui_mode = st.radio(
            "Interface Mode", 
            ["Writer Mode (Creative)", "Lab Mode (Research)"], 
            index=0 if ui_mode == "Writer Mode (Creative)" else 1,
            help="Lab Mode shows advanced ML ablation and threshold controls."
        )
        st.markdown("---")
        
        with st.expander("Engine Context (RAM Usage)", expanded=new_ui_mode == "Lab Mode (Research)"):
            engine_mode = st.radio(
                "Processing Mode",
                ["Fast Mode (Heuristic Engine – recommended)", "Full AI Mode (Loads SBERT + GPT-2, needs 8 GB RAM)"],
                index=0 if is_cloud else 1,
                help="Fast Mode uses mathematical heuristics — same output structure, no ML model loading. Full AI adds embedding-based analysis."
            )
            force_cloud = "Fast" in engine_mode
            if force_cloud:
                st.caption("Fast Mode active — low memory footprint (<1 GB)")
            else:
                st.caption("Full AI Mode — allocates up to 5 GB RAM. Close other apps if running locally.")
                
        st.markdown("---")
        
        # Mode Selection
        mode = st.radio("Feature", ["Script Analysis", "Scene Compare", "Live Sandbox"], label_visibility="collapsed")
        
        st.markdown("---")
        # --- INFO ---
        st.info(
            "**Reading the Pulse**\n\n"
            "**High Tension (7–10)**: Intense, high cognitive load.\n"
            "**Balanced (4–6)**: Engaging flow, sustainable pacing.\n"
            "(v) **Low Energy (0–3)**: Risk of audience drift — consider adding pressure."
        )
        
        st.markdown("---")
        
        # Ablation Config (Only if Lab Mode)
        ablation_config = {}
        if new_ui_mode == "Lab Mode (Research)":
            with st.expander("Advanced Model Ablation Console", expanded=False):
                st.markdown("Control exact Pipeline constraints.")
                ab_sbert = st.checkbox("Enable SBERT (Thematic Extraction)", value=not force_cloud, key="ab_sbert", disabled=force_cloud)
                ab_gpt2 = st.checkbox("Enable GPT-2 (Surprisal Proxy)", value=not force_cloud, key="ab_gpt2", disabled=force_cloud)
                ab_multimodal = st.checkbox("Enable Multimodal Extrapolation", value=True, key="ab_multimodal")
                
                if force_cloud:
                    st.warning("Heavy models disabled by Hardware Constraints selector above.")
                    
                ab_seed = st.number_input("Random Seed", value=42, key="ab_seed")
                ab_decay = st.number_input("Fatigue Decay Rate (k)", value=0.05, step=0.01, key="ab_decay")
                
                ablation_config = {
                    'use_sbert': ab_sbert,
                    'use_gpt2': ab_gpt2,
                    'use_multimodal': ab_multimodal,
                    'seed': ab_seed,
                    'decay_rate': ab_decay
                }
        else:
            ablation_config = {
                'use_sbert': not force_cloud,
                'use_gpt2': not force_cloud,
                'use_multimodal': True,
            }

        # Operator Panel
        shadow_mode, high_accuracy_mode = stu.render_operator_panel(st.session_state.get('prev_run'))
        
        return {
            'ui_mode': new_ui_mode,
            'force_cloud': force_cloud,
            'feature_mode': mode,
            'ablation_config': ablation_config,
            'shadow_mode': shadow_mode,
            'high_accuracy_mode': high_accuracy_mode
        }
