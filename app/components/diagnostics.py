import streamlit as st
import os

def render_diagnostics():
    """Renders system diagnostics and memory management controls."""
    with st.expander("System Diagnostics & Memory", expanded=False):
        # ── Memory Safe Mode toggle ────────────────────────────────
        st.caption("**[RUN] Performance Mode**")
        heuristics_env = os.environ.get("SCRIPTPULSE_HEURISTICS_ONLY", "0") == "1"
        if 'heuristics_only' not in st.session_state:
            st.session_state['heuristics_only'] = heuristics_env

        mem_safe = st.toggle(
            "Memory Safe Mode (heuristics only)",
            value=st.session_state['heuristics_only'],
            key="mem_safe_toggle",
            help=(
                "Disables Jina SBERT (~66 MB) and DeBERTa Zero-Shot (~140 MB). "
                "spaCy (en_core_web_sm) remains active — it is always local and lightweight. "
                "Structural accuracy is fully preserved; only embedding-based subfields are approximated."
            )
        )
        if mem_safe != st.session_state['heuristics_only']:
            st.session_state['heuristics_only'] = mem_safe
            os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1" if mem_safe else "0"
            # Invalidate model cache so next run picks up the change
            try:
                from scriptpulse.pipeline import runner as _runner
                _runner._AGENT_CACHE.clear()
                st.toast("Mode changed — model cache cleared." if mem_safe else "Full ML mode restored.")
            except ImportError:
                pass

        # ── Manual memory release ──────────────────────────────────
        if st.button("Free Model Memory", key="free_mem_btn",
                     help="Releases SBERT/DeBERTa references and triggers GC. Use when RAM is low."):
            try:
                from scriptpulse.utils.model_manager import manager as _mm
                from scriptpulse.pipeline import runner as _runner
                _mm.release_models()
                _runner._AGENT_CACHE.clear()
                st.success("Model memory released. Next analysis will reload if needed.")
            except Exception as _e:
                st.warning(f"Release partial: {_e}")

        st.divider()

        # ── Health check ───────────────────────────────────────────
        if st.button("Run Health Check", key="health_btn"):
            with st.spinner("Checking pipeline health..."):
                try:
                    from scriptpulse.pipeline import runner as _runner
                    h = _runner.health_check()
                    st.session_state['health_report'] = h
                except Exception as _he:
                    st.error(f"Health check failed: {_he}")

        h = st.session_state.get('health_report')
        if h:
            status = h.get('status', 'unknown')
            if status == 'healthy':
                st.success(f"System Status: **{status.upper()}**")
            else:
                st.warning(f"System Status: **{status.upper()}**")

            from app.components import uikit
            st.caption("**Core Agents**")
            for agent, ok in h.get('agents', {}).items():
                icon_html = uikit.get_status_icon_html(ok)
                st.markdown(f"{icon_html} {agent}", unsafe_allow_html=True)

            st.caption("**Governance & Config**")
            gov_icon = uikit.get_status_icon_html(h.get('governance'))
            st.markdown(f"{gov_icon} Governance Firewall", unsafe_allow_html=True)
            for fname, exists in h.get('config_files', {}).items():
                f_icon = uikit.get_status_icon_html(exists)
                st.markdown(f"{f_icon} {fname}", unsafe_allow_html=True)
