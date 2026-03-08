import re
import streamlit as st
from app.components.theme import Theme

def get_brand_html(size: str = "3.8rem", align: str = "center", margin_bottom: str = "0px") -> str:
    """Returns the standardized, globally consistent ScriptPulse brand HTML."""
    return (
        f'<div style="text-align: {align}; margin-bottom: {margin_bottom};">'
        f'<span style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: {size}; '
        f'color: #FFFFFF !important; display: inline;">Script</span>'
        f'<span style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: {size}; '
        f'color: #0052FF !important; display: inline;">Pulse</span>'
        f'</div>'
    )

def render_hero_section(title: str, subtitle: str):
    """Renders the main hero section using the standardized brand logo."""
    brand_html = get_brand_html(size="3.8rem", align="center", margin_bottom="10px")
    
    html_content = f"""
    <div style="text-align: center; padding: 0rem 0 1.5rem 0; width: 100%; background: transparent !important;">
        {brand_html}
        <div style="color: #A3A0B3 !important; font-size: 1.15rem; font-weight: 300; max-width: 800px; margin: 0 auto;">{subtitle}</div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def render_sidebar_header(title: str, subtitle: str):
    """Renders the sidebar branding as solid white as requested."""
    st.markdown(f"""
    <div style="text-align: center; padding: 0.5rem 0 0.5rem 0;">
        <span style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; '
        'color: white !important; -webkit-text-fill-color: white !important; letter-spacing: -0.02em;">
            ScriptPulse
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(icon: str, title: str, explainer: str):
    """Renders a premium section header with an animated glowing divider."""
    st.markdown(f"""
    <div style="margin: 2.5rem 0 1.5rem 0;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 1.6rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));">{icon}</span>
            <h2 style="margin: 0 !important; font-size: 1.6rem !important; background: linear-gradient(135deg, #FFFFFF 0%, #A3A0B3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h2>
        </div>
        <p style="color: rgba(163, 160, 179, 0.9); font-size: 0.95rem; margin-bottom: 15px; font-weight: 300; letter-spacing: 0.02em;">{explainer}</p>
        <div style="height: 1px; width: 100%; background: linear-gradient(90deg, rgba(85,224,255,0.5) 0%, rgba(106,72,187,0.2) 50%, transparent 100%); margin-bottom: 1rem;"></div>
    </div>
    """, unsafe_allow_html=True)

def render_insight_card(text: str):
    """Renders a color-coded insight card based on text content."""
    css_class = 'insight-info'
    if any(x in text for x in ['🔴', 'CRITICAL', '🚫']):
        css_class = 'insight-critical'
    elif any(x in text for x in ['🟠', 'WARNING', '⚠️', '🟡', '✂️', '⬜', '💬', '✍️', '🎢', '♻️', '📉', '🧵', '🎙️', '👻', '👥', '🔤']):
        css_class = 'insight-warning'
    elif any(x in text for x in ['✨', '🟢', '✅', '💎', '⭐', '🤫', '⛓️', '🎭', '⚡']):
        css_class = 'insight-good'
    

    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)
    
    st.markdown(f"<div class='{css_class}'>{text_html}</div>", unsafe_allow_html=True)


def render_tooltip_card(content: str):
    """Renders a subtle tooltip/explainer card."""
    st.markdown(f"""
    <div class="tooltip-card">
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_signal_box(title: str, badge_html: str, action: str, border_color: str = None):
    """Renders a premium signal box for priorities or AI summaries."""

    action_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', action)
    action_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', action_html)

    style = f' style="border-left: 3px solid {border_color};"' if border_color else ""
    # Use a single-line joined string to avoid Markdown parser breaking the HTML tags
    html = (
        f'<div class="signal-box"{style}>'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
        f'<span style="font-weight: 700; color: #FFFFFF; font-size: 1.1rem; letter-spacing: 0.02em;">{title}</span>'
        f'{badge_html}'
        f'</div>'
        f'<div style="color: rgba(244, 246, 251, 0.85); line-height: 1.7; font-weight: 300;">{action_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def get_score_badge(value: float, label: str) -> str:
    """Returns the HTML for a score badge based on percentage value."""
    if value >= 0.7:
        cls = "score-high"
    elif value >= 0.4:
        cls = "score-mid"
    else:
        cls = "score-low"
    return f"<span class='score-badge {cls}'>{label}: {round(value * 100)}%</span>"

def get_leverage_badge(leverage: str) -> str:
    """Returns the HTML for a leverage/impact badge."""
    badges = {
        'High': f'<span class="score-badge score-low">🔥 HIGH IMPACT</span>',
        'Medium': f'<span class="score-badge score-mid">⚡ MEDIUM IMPACT</span>',
        'Low': f'<span class="score-badge" style="background: rgba(106,72,187,0.15); color: {Theme.TEXT_SECONDARY};">📌 LOW IMPACT</span>'
    }
    return badges.get(leverage, "")

def render_lab_pipeline_header():
    """Renders the top neon bar for the Lab Mode."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
        <span style="background: {Theme.ACCENT_ROSE}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; letter-spacing: 1px;">LAB PIPELINE</span>
        <span style="color: {Theme.TEXT_MUTED}; font-family: monospace; font-size: 12px;">STATUS: ACTIVE / TELEMETRY: STREAMING</span>
    </div>
    """, unsafe_allow_html=True)

def get_status_icon_html(is_ok: bool) -> str:
    """Returns the themed HTML for a status icon (pass/fail)."""
    icon_class = "bi-check-circle-fill icon-pass" if is_ok else "bi-x-circle-fill icon-fail"
    return f"<i class='bi {icon_class}'></i>"

def render_ai_consultant_box(insight_text: str, persona: str = "Script Consultant"):
    """Renders a premium glassmorphic box for AI-powered consultant insights."""

    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', insight_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)

    html = (
        f'<div style="background: linear-gradient(135deg, rgba(106, 72, 187, 0.1) 0%, rgba(106, 72, 187, 0.03) 100%); '
        f'border-radius: var(--radius-lg); padding: 20px; border: 1px solid rgba(106, 72, 187, 0.2); '
        f'backdrop-filter: blur(12px); box-shadow: 0 4px 20px rgba(0,0,0,0.2); margin-top: 20px;">'
        f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">'
        f'<span style="font-size: 1.4rem; filter: drop-shadow(0 0 8px {Theme.ACCENT_PRIMARY});">🧠</span>'
        f'<span style="font-weight: 700; color: white; font-size: 0.9rem; letter-spacing: 0.1em; text-transform: uppercase;">'
        f'{persona} Intelligence</span>'
        f'</div>'
        f'<div style="color: rgba(244, 246, 251, 0.95); font-size: 1rem; line-height: 1.7; font-style: italic; font-weight: 300;">'
        f'"{text_html}"</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
