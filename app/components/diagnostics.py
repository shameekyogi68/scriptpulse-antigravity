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
            "Memory Safe Mode (no ML models)",
            value=st.session_state['heuristics_only'],
            key="mem_safe_toggle",
            help="Disables SBERT/GPT-2/DistilBART. Saves ~900MB RAM. Uses fast heuristics. Accuracy is preserved for structural analysis."
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
                     help="Releases SBERT/GPT-2 references and triggers GC. Use when RAM is low."):
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

            st.caption("**Core Agents**")
            for agent, ok in h.get('agents', {}).items():
                icon = "<i class='bi bi-check-circle-fill icon-pass'></i>" if ok else "<i class='bi bi-x-circle-fill icon-fail'></i>"
                st.markdown(f"{icon} {agent}", unsafe_allow_html=True)

            st.caption("**Governance & Config**")
            gov_icon = "<i class='bi bi-check-circle-fill icon-pass'></i>" if h.get('governance') else "<i class='bi bi-x-circle-fill icon-fail'></i>"
            st.markdown(f"{gov_icon} Governance Firewall", unsafe_allow_html=True)
            for fname, exists in h.get('config_files', {}).items():
                f_icon = "<i class='bi bi-check-circle-fill icon-pass'></i>" if exists else "<i class='bi bi-x-circle-fill icon-fail'></i>"
                st.markdown(f"{f_icon} {fname}", unsafe_allow_html=True)
