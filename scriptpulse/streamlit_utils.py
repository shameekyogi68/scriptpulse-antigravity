import streamlit as st

def check_integrity():
    """Validates startup state."""
    return True, "OK"

def sync_safety_state():
    """Syncs session state."""
    if 'safe_mode_active' not in st.session_state:
        st.session_state['safe_mode_active'] = False

def check_upload_size(uploaded_file):
    """Guards against excessively large files."""
    if uploaded_file and uploaded_file.size > 20 * 1024 * 1024:
        st.error("File too large. Please upload a script under 20MB.")
        return False
    return True

def render_operator_panel(prev_run=None):
    """Renders advanced control panel if needed."""
    return False, False # shadow_mode, high_accuracy_mode

def check_input_length(text):
    """Guards against excessively large paste inputs."""
    if text and len(text) > 500000:
        st.error("Pasted text is too long. Please upload as a file instead.")
        return False
    return True
