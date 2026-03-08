import re
import streamlit as st
from app.components.theme import Theme

def render_hero_section(title: str, subtitle: str):
    """Renders the main hero section with absolute brand colors (White/Blue)."""
    # Use a solid horizontal layout for the title to maximize visual impact
    brand_html = (
        '<div style="text-align: center; margin: 0 auto 10px auto; width: 100%;">'
        '<span style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: 3.8rem; '
        'color: #FFFFFF !important; display: inline; background: transparent !important; margin: 0; padding: 0;">Script</span>'
        '<span style="font-family: \'Outfit\', Helvetica, Arial, sans-serif; font-weight: 700; font-size: 3.8rem; '
        'color: #0052FF !important; display: inline; background: transparent !important; margin: 0; padding: 0;">Pulse</span>'
        '</div>'
    )
    
    html_content = f"""
    <div style="text-align: center; padding: 2.5rem 0; width: 100%; background: transparent !important;">
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
    """Renders a standard section header with an icon and explainer text."""
    st.markdown(f"""
    <div class="section-header">
        <span class="icon">{icon}</span>
        <h2>{title}</h2>
    </div>
    <p class="section-explainer">{explainer}</p>
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
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
        f'<span style="font-weight: 600; color: {Theme.TEXT_PRIMARY};">{title}</span>'
        f'{badge_html}'
        f'</div>'
        f'<div style="color: {Theme.TEXT_SECONDARY}; line-height: 1.6;">{action_html}</div>'
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

def render_lab_metric(label: str, value: str, delta: str = None):
    """Renders a lab-specific metric card."""
    delta_html = f"<div style='color: {Theme.ACCENT_TEAL}; font-size: 11px; margin-top: -5px;'>{delta}</div>" if delta else ""
    st.markdown(f"""
    <div style="background: {Theme.BG_SECONDARY}; border: 1px solid rgba(106, 72, 187, 0.2); 
                padding: 15px; border-radius: 4px; border-left: 3px solid {Theme.ACCENT_PRIMARY};
                font-family: 'JetBrains Mono', monospace;">
        <div style="color: {Theme.TEXT_MUTED}; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
        <div style="color: {Theme.TEXT_PRIMARY}; font-size: 24px; font-weight: bold; margin: 4px 0;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_lab_subheading(index: str, title: str):
    """Renders a monospaced lab subheading."""
    st.markdown(f"<h3 style='margin-top: 30px; border-bottom: 1px solid rgba(106, 72, 187, 0.3); padding-bottom: 5px;'><span style='color: {Theme.ACCENT_PRIMARY};'>[{index}]</span> {title}</h3>", unsafe_allow_html=True)

def render_sidebar_header(title: str, subtitle: str):
    """Renders the top branding for the sidebar."""
    st.markdown(f"""
    <div style="text-align: center; padding: 0.5rem 0 1rem;">
        <span style="font-family: Outfit, sans-serif; font-size: 1.6rem; font-weight: 700; 
                     background: linear-gradient(135deg, {Theme.ACCENT_PRIMARY}, {Theme.SEMANTIC_INFO}); 
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {title}
        </span>
        <br/>
        <span style="font-size: 0.75rem; color: {Theme.SEMANTIC_INFO}; letter-spacing: 0.05em;">
            {subtitle}
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_quick_guide():
    """Renders the standardized quick legend/guide in the sidebar."""
    st.markdown(f"""
    <div style="background: rgba(106, 72, 187, 0.08); border-radius: 12px; 
                padding: 16px; border: 1px solid rgba(106, 72, 187, 0.15);">
        <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.85rem;">📖 What Do the Colors Mean?</div>
        <div style="font-size: 0.78rem; color: {Theme.TEXT_SECONDARY}; line-height: 1.6;">
            <b style="color: {Theme.SEMANTIC_CRITICAL};">🔴 Red</b> — Fix this now — it could lose your reader<br/>
            <b style="color: {Theme.SEMANTIC_WARNING};">🟠 Orange</b> — Worth a second look in your next draft<br/>
            <b style="color: {Theme.SEMANTIC_GOOD};">🟢 Green</b> — Great job — this part works well<br/>
            <b style="color: {Theme.ACCENT_PURPLE};">💡 Purple</b> — Something interesting to think about
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_status_icon_html(is_ok: bool) -> str:
    """Returns the themed HTML for a status icon (pass/fail)."""
    icon_class = "bi-check-circle-fill icon-pass" if is_ok else "bi-x-circle-fill icon-fail"
    return f"<i class='bi {icon_class}'></i>"

def render_ai_consultant_box(insight_text: str, persona: str = "Script Consultant"):
    """Renders a premium, distinctive box for AI-powered consultant insights."""

    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', insight_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)

    html = (
        f'<div style="background: rgba(106, 72, 187, 0.05); border-radius: 12px; padding: 16px; '
        f'border-left: 4px solid {Theme.ACCENT_PRIMARY}; margin-top: 15px; border-top: 1px solid rgba(106, 72, 187, 0.1);'
        f'border-right: 1px solid rgba(106, 72, 187, 0.1); border-bottom: 1px solid rgba(106, 72, 187, 0.1);">'
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">'
        f'<span style="font-size: 1.2rem;">🧠</span>'
        f'<span style="font-weight: 700; color: {Theme.ACCENT_PRIMARY}; font-size: 0.85rem; letter-spacing: 0.5px; text-transform: uppercase;">'
        f'{persona} Insight</span>'
        f'</div>'
        f'<div style="color: {Theme.TEXT_PRIMARY}; font-size: 0.95rem; line-height: 1.5; font-style: italic;">'
        f'{text_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
