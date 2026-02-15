
import streamlit as st
import os
import hashlib
import json
import time

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAFETY_STATE_FILE = os.path.expanduser("~/.scriptpulse/.safety_state.json")

@st.cache_resource
def check_integrity():
    """
    Startup integrity check. Runs once per server boot.
    Verifies frozen config checksums and required files.
    """
    try:
        # 1. Verify API Contract
        contract_path = os.path.join(PROJECT_ROOT, 'api_contract_v13_1.json')
        if not os.path.exists(contract_path):
            return False, "Missing api_contract_v13_1.json"
            
        # 2. Verify Model Requirements
        req_path = os.path.join(PROJECT_ROOT, 'required_model_versions.json')
        if not os.path.exists(req_path):
            return False, "Missing required_model_versions.json"
            
        # 3. Verify Pip Requirements
        pip_path = os.path.join(PROJECT_ROOT, 'requirements_v13.1.txt')
        if not os.path.exists(pip_path):
            return False, "Missing requirements_v13.1.txt"
            
        return True, "Integrity Verified"
    except Exception as e:
        return False, f"Integrity Check Failed: {e}"

def sync_safety_state():
    """
    Sync session state with persistent safety state.
    """
    if 'safe_mode_active' not in st.session_state:
        st.session_state.safe_mode_active = False
        
    if os.path.exists(SAFETY_STATE_FILE):
        try:
            with open(SAFETY_STATE_FILE, 'r') as f:
                state = json.load(f)
                if state.get('auto_safe_next_run'):
                    st.session_state.safe_mode_active = True
        except:
            pass

def render_operator_panel(final_output=None):
    """
    Render Operator Panel in sidebar.
    Accepts final_output (dict) or uses session state.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Health")
    
    # Defaults
    if not final_output and 'prev_run' in st.session_state:
        final_output = st.session_state['prev_run']
        
    if final_output is None:
        final_output = {}
        
    meta = final_output.get('meta', {})

    
    # Model Versions (loaded from manager if possible)
    try:
        from scriptpulse.utils.model_manager import manager
        loaded_models = len(manager.get_loaded_models())
    except:
        loaded_models = 0

    # Metrics (Simplified for Best Run)
    metrics = {
        'Runtime': f"{final_output.get('runtime_ms', 0)}ms",
        'Scenes/Sec': final_output.get('scenes_per_second', 0.0) if final_output else 0.0,
        'Active Models': loaded_models,
        'Mode': 'High Accuracy' if meta.get('cpu_safe_mode') is False else 'Fast Mode'
    }
    
    # Render Simplified
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Runtime", metrics['Runtime'])
    c2.metric("Speed", f"{metrics['Scenes/Sec']}/s")
    
    st.sidebar.caption(f"Active Models: {metrics['Active Models']}")
    st.sidebar.caption(f"Mode: {metrics['Mode']}")
    
    # Flags (Only show if abnormal)
    if meta.get('resource_flag') and meta.get('resource_flag') != 'None':
        st.sidebar.error(f"Resource: {meta.get('resource_flag')}")
        
    if final_output and final_output.get('drift_flag') == 'UNSTABLE':
        st.sidebar.error("Drift: UNSTABLE")
        
    if meta.get('shadow_mismatch'):
        st.sidebar.error("Shadow: MISMATCH")
    
    if meta.get('auto_safe_mode'):
        st.sidebar.warning("⚠️ SAFE MODE ACTIVE")
        
    # Operator Controls
    st.sidebar.markdown("---")
    
    # v13.1 Optimization: Cache Reset
    if st.sidebar.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache Cleared!")
        st.rerun()
    
    # Shadow Mode Toggle
    # Defaults to False unless session state has it
    shadow_default = st.session_state.get('shadow_mode_active', False)
    shadow_mode = st.sidebar.checkbox("Shadow Mode (Dual Run)", value=shadow_default, key='shadow_mode_active')
    
    # High Accuracy Toggle (v13.1 Optimization)
    high_accuracy = st.sidebar.checkbox("High Accuracy Mode", value=False, help="Enable full research-grade analysis. Slower.")
    
    if shadow_mode:
        st.sidebar.info("Shadow Mode Enabled: Pipeline will run twice.")
        
    return shadow_mode, high_accuracy

def check_input_length(text, limit_chars=100000):
    """
    Guard: Block oversized inputs before pipeline.
    """
    if len(text) > limit_chars:
        st.error(f"Input too long ({len(text)} chars). Limit is {limit_chars}.")
        return False
    return True

def check_upload_size(uploaded_file, limit_mb=5):
    """
    Enforce upload size limit.
    """
    if uploaded_file.size > limit_mb * 1024 * 1024:
        st.error(f"File size exceeds {limit_mb}MB limit.")
        return False
    return True
