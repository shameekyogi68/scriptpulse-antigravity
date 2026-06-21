# MODULE: uikit.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import re
import textwrap
from typing import Optional
import streamlit as st
from app.components.theme import Theme

def clean_html(html_str: str) -> str:
    """Removes leading and trailing whitespace from every line of HTML to prevent Markdown code block parsing."""
    return "\n".join(line.strip() for line in html_str.split("\n"))

def get_brand_html(size: str = "3.8rem", align: str = "center", margin_bottom: str = "0px") -> str:
    """Returns the standardized, globally consistent ScriptPulse brand HTML."""
    return (
        f'<div style="text-align: {align}; margin-bottom: {margin_bottom};">'
        f'<span style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: {size}; '
        f'color: #FFFFFF !important; display: inline;">Script</span>'
        f'<span class="brand-pulse" style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: {size}; '
        f'display: inline-block;">Pulse</span>'
        f'</div>'
    )

def render_hero_section(title: str, subtitle: str):
    """Renders the main hero section with the ScriptPulse icon logo, brand text, and trust bar."""
    import os, base64

    # Resolve icon path relative to any working directory
    _here = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(_here, "..", "assets", "ScriptPulse_Icon.png")
    icon_path = os.path.normpath(icon_path)

    logo_html = ""


    brand_html = get_brand_html(size="3.8rem", align="center", margin_bottom="10px")

    # Trust bar with live indicators
    trust_bar_html = (
        '<div class="trust-bar">'
        '<div class="trust-item"><span class="trust-dot"></span> Engine Online</div>'
        '<div class="trust-item"><span class="trust-dot"></span> Privacy First</div>'
        '<div class="trust-item"><span class="trust-dot"></span> AI-Verified</div>'
        '<div class="trust-item"><span class="trust-dot"></span> Scene-Level Analysis</div>'
        '</div>'
    )

    html_content = f"""
    <div style="text-align: center; padding: 2rem 0 1.5rem 0; width: 100%; background: transparent !important; position: relative;">
        {logo_html}
        {brand_html}
        <div style="color: #A3A0B3 !important; font-size: 1.15rem; font-weight: 300;
                    max-width: 800px; margin: 0 auto; position: relative; z-index: 1;">{subtitle}</div>
        {trust_bar_html}
    </div>
    """
    st.markdown(clean_html(html_content), unsafe_allow_html=True)

def render_sidebar_header(title: str, subtitle: str):
    """Renders the sidebar branding as solid white as requested."""
    st.markdown(clean_html(f"""
    <div style="text-align: center; padding: 0.5rem 0 0.5rem 0;">
        <span style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: white !important; -webkit-text-fill-color: white !important; letter-spacing: -0.02em;">
            ScriptPulse
        </span>
    </div>
    """), unsafe_allow_html=True)

def render_section_header(icon: str, title: str, explainer: str):
    """Renders a premium section header with an animated glowing divider."""
    st.markdown(clean_html(f"""
    <div style="margin: 2.5rem 0 1.5rem 0;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 1.6rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));">{icon}</span>
            <h2 style="margin: 0 !important; font-size: 1.6rem !important; background: linear-gradient(135deg, #FFFFFF 0%, #A3A0B3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h2>
        </div>
        <p style="color: rgba(163, 160, 179, 0.9); font-size: 0.95rem; margin-bottom: 15px; font-weight: 300; letter-spacing: 0.02em;">{explainer}</p>
        <div style="height: 1px; width: 100%; background: linear-gradient(90deg, rgba(85,224,255,0.5) 0%, rgba(106,72,187,0.2) 50%, transparent 100%); margin-bottom: 1rem;"></div>
    </div>
    """), unsafe_allow_html=True)

def render_insight_card(text: str):
    """Renders a color-coded insight card based on text content, styled exactly like the mockup."""
    # Clean up standard emojis from text to avoid duplicating icons
    clean_text = text
    for emoji in ['🔴', '🚫', '🟠', '⚠️', '🟡', '✂️', '⬜', '💬', '✍️', '🎢', '♻️', '📉', '🧵', '🎙️', '👻', '👥', '🔤', '✨', '🟢', '✅', '💎', '⭐', '🤫', '⛓️', '🎭', '⚡', 'ℹ️']:
        clean_text = clean_text.replace(emoji, '')
    clean_text = clean_text.strip()
    
    # Determine type
    icon = 'ti-info-circle'
    icon_color = 'var(--text-secondary)'
    bg_color = 'rgba(255, 255, 255, 0.03)'
    border_left = '4px solid var(--text-secondary)'
    
    if any(x in text for x in ['🔴', 'CRITICAL', '🚫']):
        icon = 'ti-alert-circle'
        icon_color = '#FF3366'
        bg_color = 'rgba(255, 51, 102, 0.05)'
        border_left = '4px solid #FF3366'
    elif any(x in text for x in ['🟠', 'WARNING', '⚠️', '🟡', '✂️', '⬜', '💬', '✍️', '🎢', '♻️', '📉', '🧵', '🎙️', '👻', '👥', '🔤']):
        icon = 'ti-alert-triangle'
        icon_color = 'var(--coral)'
        bg_color = 'rgba(255, 112, 67, 0.05)'
        border_left = '4px solid var(--coral)'
    elif any(x in text for x in ['✨', '🟢', '✅', '💎', '⭐', '🤫', '⛓️', '🎭', '⚡']):
        icon = 'ti-sparkles'
        icon_color = 'var(--emerald)'
        bg_color = 'rgba(0, 200, 83, 0.05)'
        border_left = '4px solid var(--emerald)'

    # Convert markdown bold/italics to HTML
    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)
    
    # Split text into Title and Body if colon is present (e.g. "Action Peak: Strong integration...")
    parts = text_html.split(':', 1)
    if len(parts) == 2:
        title_html = f"<div style='font-size: 0.9rem; font-weight: 700; color: white; margin-bottom: 4px;'>{parts[0].strip()}</div>"
        desc_html = f"<div style='font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;'>{parts[1].strip()}</div>"
    else:
        title_html = ""
        desc_html = f"<div style='font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6;'>{text_html}</div>"

    html = f"""
    <div style="display: flex; gap: 16px; padding: 20px; margin-bottom: 12px;
                background: {bg_color}; border-left: {border_left}; border-radius: var(--radius-md);
                border-top: 1px solid rgba(255,255,255,0.03); border-right: 1px solid rgba(255,255,255,0.03);
                border-bottom: 1px solid rgba(255,255,255,0.03); box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
        <div style="width: 40px; height: 40px; border-radius: 10px; background: rgba(255,255,255,0.03);
                    display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: {icon_color};
                    border: 1px solid rgba(255,255,255,0.05); flex-shrink: 0;">
            <i class="ti {icon}"></i>
        </div>
        <div>
            {title_html}
            {desc_html}
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_tooltip_card(content: str):
    """Renders a subtle tooltip/explainer card."""
    st.markdown(clean_html(f"""
    <div class="tooltip-card">
        {content}
    </div>
    """), unsafe_allow_html=True)

def render_empty_state():
    """Renders a premium empty state with compelling CTA and feature highlights."""
    st.markdown(clean_html("""
    <div style="text-align: center; padding: 2.5rem 2rem; margin: 1rem 0;
                background: linear-gradient(135deg, rgba(155, 81, 224, 0.04) 0%, rgba(165, 109, 255, 0.02) 50%, rgba(155, 81, 224, 0.04) 100%);
                border: 1px solid rgba(155, 81, 224, 0.15); border-radius: 20px;
                position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px;
                    background: linear-gradient(90deg, transparent, rgba(155, 81, 224, 0.45), transparent);"></div>
        <div style="font-size: 2.5rem; margin-bottom: 12px; filter: drop-shadow(0 0 12px rgba(155, 81, 224, 0.45));">📄</div>
        <div style="font-size: 1.15rem; font-weight: 600; color: white; margin-bottom: 8px;">
            Upload your screenplay to begin
        </div>
        <div style="font-size: 0.88rem; color: rgba(163, 160, 179, 0.9); max-width: 500px; margin: 0 auto 20px auto; line-height: 1.6;">
            ScriptPulse will analyze your script's emotional architecture, structural health, and character dynamics in seconds.
        </div>
        <div style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: rgba(244, 246, 251, 0.5);">
                <span style="color: #00D2A0;">✓</span> Supports PDF, TXT, FDX
            </div>
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: rgba(244, 246, 251, 0.5);">
                <span style="color: #00D2A0;">✓</span> Genre-calibrated benchmarks
            </div>
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: rgba(244, 246, 251, 0.5);">
                <span style="color: #00D2A0;">✓</span> 3 professional perspectives
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

def render_signal_box(title: str, badge_html: str, action: str, border_color: Optional[str] = None):
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
    st.markdown(clean_html(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
        <span style="background: {Theme.ACCENT_ROSE}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; letter-spacing: 1px;">LAB PIPELINE</span>
        <span style="color: {Theme.TEXT_MUTED}; font-family: monospace; font-size: 12px;">STATUS: ACTIVE / TELEMETRY: STREAMING</span>
    </div>
    """), unsafe_allow_html=True)

def get_status_icon_html(is_ok: bool) -> str:
    """Returns the themed HTML for a status icon (pass/fail)."""
    icon_class = "bi-check-circle-fill icon-pass" if is_ok else "bi-x-circle-fill icon-fail"
    return f"<i class='bi {icon_class}'></i>"

def render_ai_consultant_box(insight_text: str, persona: str = "Script Consultant", box_title: Optional[str] = None):
    """Renders a premium glassmorphic box for AI-powered consultant insights."""

    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', insight_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)
    
    display_title = box_title if box_title else f"{persona} Intelligence"

    html = (
        f'<div style="background: linear-gradient(135deg, rgba(155, 81, 224, 0.06) 0%, rgba(165, 109, 255, 0.03) 50%, rgba(155, 81, 224, 0.06) 100%); '
        f'border-radius: 16px; padding: 22px 24px; border: 1px solid rgba(155, 81, 224, 0.2); '
        f'backdrop-filter: blur(16px); box-shadow: 0 8px 32px rgba(0,0,0,0.25); margin-top: 20px; '
        f'position: relative; overflow: hidden;">'
        f'<div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; '
        f'background: linear-gradient(90deg, transparent, rgba(155, 81, 224, 0.6), rgba(165, 109, 255, 0.4), transparent);"></div>'
        f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">'
        f'<div style="display: flex; align-items: center; gap: 10px;">'
        f'<span style="font-size: 1.4rem; filter: drop-shadow(0 0 8px rgba(155, 81, 224, 0.5));">🧠</span>'
        f'<span style="font-weight: 700; color: white; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">'
        f'{display_title}</span>'
        f'</div>'
        f'<span style="font-size: 0.6rem; color: rgba(0, 200, 83, 0.7); font-weight: 700; letter-spacing: 0.1em; '
        f'text-transform: uppercase; background: rgba(0, 200, 83, 0.08); border: 1px solid rgba(0, 200, 83, 0.2); '
        f'border-radius: 12px; padding: 3px 10px;">✓ AI-VERIFIED</span>'
        f'</div>'
        f'<div style="color: rgba(244, 246, 251, 0.92); font-size: 0.98rem; line-height: 1.8; font-style: italic; font-weight: 300;">'
        f'"{text_html}"</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, help_text: Optional[str] = None):
    """Renders a premium, non-truncating metric card for the Story Dashboard."""
    # Tooltip logic
    tooltip_html = f'<span title="{help_text}" style="cursor:help; margin-left:4px; opacity:0.3;"><i class="ti ti-info-circle"></i></span>' if help_text else ""
    
    # Value auto-downsizing for long strings
    val_size = "1.8rem"
    if len(value) > 10: val_size = "1.4rem"
    if len(value) > 15: val_size = "1.1rem"

    # Highlight specific values with Amethyst color
    val_color = "white"
    if value in ["Healthy", "Balanced"]:
        val_color = "var(--accent-primary)"

    html = clean_html(f"""
    <div class="custom-metric-card">
        <div style="font-size: 0.65rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; line-height: 1.2; display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <span>{label}</span>
            {tooltip_html}
        </div>
        <div style="font-size: {val_size}; font-weight: 800; color: {val_color}; margin-top: 5px; font-family: 'Outfit', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            {value}
        </div>
    </div>
    """)
    st.markdown(html, unsafe_allow_html=True)
