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
    """Renders the main hero section — exact Tactile Glass template spec."""
    # Brand logo: Outfit 800, 4rem, letter-spacing -0.04em (matches .brand-logo in template)
    brand_html = (
        '<div class="brand-logo" style="font-family: \'Outfit\', sans-serif; font-weight: 800; font-size: 4rem; '
        'letter-spacing: -0.04em; margin-bottom: 12px;">'
        '<span style="color: #FFFFFF;">Script</span>'
        '<span class="brand-pulse">Pulse</span>'
        '</div>'
    )

    # Subtitle: text-lg (1.125rem), text-secondary, font-medium, max-w-2xl centered (matches template p)
    subtitle_html = (
        f'<p style="font-size: 1.125rem; color: var(--text-secondary); font-weight: 500; '
        f'margin-bottom: 2rem; max-width: 42rem; margin-left: auto; margin-right: auto; line-height: 1.6;">'
        f'{subtitle}</p>'
    )

    # Trust bar: gap-32px (matches template .trust-bar gap: 32px)
    trust_bar_html = (
        '<div class="trust-bar" style="display: inline-flex; gap: 32px; padding: 12px 32px; '
        'border-radius: 50px; background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); '
        'font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); '
        'text-transform: uppercase; letter-spacing: 0.1em;">'
        '<div class="trust-item" style="display:flex;align-items:center;gap:8px;">'
        '<span class="trust-dot" style="width:6px;height:6px;border-radius:50%;background:var(--emerald);'
        'box-shadow:0 0 8px var(--emerald-glow);"></span> Engine Online</div>'
        '<div class="trust-item" style="display:flex;align-items:center;gap:8px;">'
        '<span class="trust-dot" style="width:6px;height:6px;border-radius:50%;background:var(--emerald);'
        'box-shadow:0 0 8px var(--emerald-glow);"></span> Privacy First</div>'
        '<div class="trust-item" style="display:flex;align-items:center;gap:8px;">'
        '<span class="trust-dot" style="width:6px;height:6px;border-radius:50%;background:var(--emerald);'
        'box-shadow:0 0 8px var(--emerald-glow);"></span> AI-Verified</div>'
        '<div class="trust-item" style="display:flex;align-items:center;gap:8px;">'
        '<span class="trust-dot" style="width:6px;height:6px;border-radius:50%;background:var(--emerald);'
        'box-shadow:0 0 8px var(--emerald-glow);"></span> Scene-Level Analysis</div>'
        '</div>'
    )

    html_content = (
        '<header class="hero-header" style="text-align:center; margin-bottom: 48px;">'
        + brand_html
        + subtitle_html
        + trust_bar_html
        + '</header>'
    )
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
    """Renders a section header — matches template h2 (text-2xl font-bold) with icon and explainer."""
    st.markdown(clean_html(
        f'<div style="margin: 2.5rem 0 1.5rem 0;">'
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">'
        f'<i class="ti ti-{_section_icon_map(icon)}" style="font-size:1.5rem; color:var(--amethyst);"></i>'
        f'<h2 style="margin:0 !important; font-size:1.5rem !important; font-weight:700 !important; color:white; letter-spacing:-0.02em;">{title}</h2>'
        f'</div>'
        f'<p style="color:rgba(158,158,158,0.9); font-size:0.9rem; margin:0 0 14px 0; font-weight:400; line-height:1.5;">{explainer}</p>'
        f'<div style="height:1px; width:100%; background:linear-gradient(90deg, rgba(155,81,224,0.5) 0%, rgba(155,81,224,0.15) 60%, transparent 100%);"></div>'
        f'</div>'
    ), unsafe_allow_html=True)

def _section_icon_map(emoji_or_name: str) -> str:
    """Maps emoji to a tabler-icon name, or returns the string as-is if it looks like a ti- name."""
    mapping = {
        '📈': 'chart-line', '🧠': 'brain', '👥': 'users', '🏢': 'building',
        '📝': 'notes', '📦': 'package', '📐': 'ruler', '🎢': 'roller-coaster',
        '⚡': 'bolt', '🧭': 'compass', '📥': 'download', '🎬': 'movie',
        '🖨️': 'printer', '🎯': 'target', '💬': 'message',
    }
    # If it's already an emoji used as label, return tabler name; else pass through
    for emoji, name in mapping.items():
        if emoji in emoji_or_name:
            return name
    # Fallback: strip ti- prefix if present, else circle
    cleaned = emoji_or_name.replace('ti-', '')
    return cleaned if cleaned.isalpha() or '-' in cleaned else 'circle'

def render_insight_card(text: str):
    """Renders a color-coded insight card — exact Tactile Glass template .insight-item spec."""
    # Strip leading emojis/signals from display text
    clean_text = text
    for emoji in ['🔴', '🚫', '🟠', '⚠️', '🟡', '✂️', '⬜', '💬', '✍️', '🎢', '♻️', '📉',
                  '🧵', '🎙️', '👻', '👥', '🔤', '✨', '🟢', '✅', '💎', '⭐', '🤫', '⛓️',
                  '🎭', '⚡', 'ℹ️']:
        clean_text = clean_text.replace(emoji, '')
    clean_text = clean_text.strip()

    # Determine severity → colours + icon class (template pattern)
    if any(x in text for x in ['🔴', 'CRITICAL', '🚫']):
        icon_class     = 'ti-alert-circle'
        icon_color     = 'var(--accent-rose)'
        icon_bg        = 'rgba(255, 51, 102, 0.15)'
        card_bg        = 'rgba(255, 51, 102, 0.05)'
        border_left    = '4px solid var(--accent-rose)'
    elif any(x in text for x in ['🟠', 'WARNING', '⚠️', '🟡', '✂️', '⬜', '💬',
                                   '✍️', '🎢', '♻️', '📉', '🧵', '🎙️', '👻', '👥', '🔤']):
        icon_class     = 'ti-alert-triangle'
        icon_color     = 'var(--coral)'
        icon_bg        = 'rgba(255, 112, 67, 0.15)'
        card_bg        = 'rgba(255, 112, 67, 0.05)'
        border_left    = '4px solid var(--coral)'
    elif any(x in text for x in ['✨', '🟢', '✅', '💎', '⭐', '🤫', '⛓️', '🎭', '⚡']):
        icon_class     = 'ti-sparkles'
        icon_color     = 'var(--emerald)'
        icon_bg        = 'rgba(0, 200, 83, 0.15)'
        card_bg        = 'rgba(0, 200, 83, 0.05)'
        border_left    = '4px solid var(--emerald)'
    else:
        icon_class     = 'ti-info-circle'
        icon_color     = 'var(--amethyst)'
        icon_bg        = 'rgba(155, 81, 224, 0.15)'
        card_bg        = 'rgba(155, 81, 224, 0.05)'
        border_left    = '4px solid var(--amethyst)'

    # Convert markdown bold/italics → HTML
    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)

    # Split on first colon → title + body (matches template .text-sm.font-bold + p.text-secondary)
    parts = text_html.split(':', 1)
    if len(parts) == 2:
        title_part = f'<div style="font-size:0.875rem; font-weight:700; color:white; margin-bottom:4px;">{parts[0].strip()}</div>'
        body_part  = f'<p style="font-size:0.875rem; color:var(--text-secondary); line-height:1.6; margin:0;">{parts[1].strip()}</p>'
    else:
        title_part = ''
        body_part  = f'<p style="font-size:0.875rem; color:var(--text-secondary); line-height:1.6; margin:0;">{text_html}</p>'

    html = (
        f'<div class="insight-item glass-card" style="display:flex; gap:16px; padding:20px; margin-bottom:12px; '
        f'background:{card_bg}; border-left:{border_left}; border-radius:var(--radius-md); '
        f'border-top:1px solid rgba(255,255,255,0.04); border-right:1px solid rgba(255,255,255,0.04); '
        f'border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<div class="insight-icon-box" style="width:40px; height:40px; border-radius:10px; background:{icon_bg}; '
        f'color:{icon_color}; display:flex; align-items:center; justify-content:center; '
        f'font-size:1.2rem; flex-shrink:0;">'
        f'<i class="ti {icon_class}"></i>'
        f'</div>'
        f'<div style="flex:1; min-width:0;">'
        f'{title_part}'
        f'{body_part}'
        f'</div>'
        f'</div>'
    )
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
    <div class="glass-card hardware-metric" style="text-align: center; padding: 2.5rem 2rem; margin: 1rem 0; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px;
                    background: linear-gradient(90deg, transparent, rgba(155, 81, 224, 0.45), transparent);"></div>
        <div style="font-size: 2.5rem; margin-bottom: 12px; filter: drop-shadow(0 0 12px rgba(155, 81, 224, 0.45));">📄</div>
        <div style="font-size: 1.15rem; font-weight: 600; color: white; margin-bottom: 8px; font-family: 'Outfit', sans-serif;">
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
    """Renders a metric tile — exact Tactile Glass template .metric-tile spec."""
    tooltip_html = (
        f'<span title="{help_text}" style="cursor:help; opacity:0.35; margin-left:4px;">'
        f'<i class="ti ti-info-circle" style="font-size:0.75rem;"></i></span>'
    ) if help_text else ''

    # Auto-scale value font for long strings
    if len(value) > 12:
        val_size = '1.3rem'
    elif len(value) > 8:
        val_size = '1.55rem'
    else:
        val_size = '1.8rem'

    # Amethyst accent for positive semantic values
    val_color = 'var(--amethyst)' if value in ('Healthy', 'Balanced') else 'white'

    html = clean_html(
        f'<div class="glass-card metric-tile hardware-metric" '
        f'style="padding:20px; text-align:left; margin-bottom:12px; position:relative; overflow:hidden;">'
        f'<div style="font-size:0.65rem; font-weight:700; color:var(--text-secondary); '
        f'text-transform:uppercase; letter-spacing:0.12em; display:flex; '
        f'justify-content:space-between; align-items:center; margin-bottom:4px;">'
        f'<span>{label}</span>{tooltip_html}'
        f'</div>'
        f'<div class="metric-value" style="font-family:\'Outfit\',sans-serif; font-size:{val_size}; '
        f'font-weight:700; color:{val_color}; line-height:1.1; white-space:nowrap; '
        f'overflow:hidden; text-overflow:ellipsis;">{value}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
