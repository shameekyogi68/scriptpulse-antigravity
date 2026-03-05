import plotly.graph_objects as go
import plotly.io as pio

class Theme:
    # Core Backgrounds
    BG_PRIMARY = "#1A1729"
    BG_SECONDARY = "#221E34"
    BG_CARD = "rgba(32, 29, 48, 0.65)"
    BG_CARD_HOVER = "rgba(40, 36, 60, 0.8)"
    
    # Text
    TEXT_PRIMARY = "#F4F6FB"
    TEXT_SECONDARY = "#A3A0B3"
    TEXT_MUTED = "rgba(244, 246, 251, 0.45)"
    
    # Accents & Brand
    ACCENT_PRIMARY = "#6A48BB"
    ACCENT_SECONDARY = "#2F48B9"
    ACCENT_WARM = "#F57946"
    ACCENT_TEAL = "#00D2A0"
    ACCENT_ROSE = "#D92987"
    ACCENT_BLUE = "#8EC5E9"
    ACCENT_PURPLE = "#A74EC6"
    
    # Semantic
    SEMANTIC_GOOD = "#00D2A0"
    SEMANTIC_WARNING = "#F57946"
    SEMANTIC_CRITICAL = "#D92987"
    SEMANTIC_INFO = "#8EC5E9"

def init_plotly_template():
    """Initializes and registers the custom ScriptPulse Plotly template."""
    pio.templates["scriptpulse_dark"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=Theme.TEXT_PRIMARY),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(106, 72, 187, 0.08)',
                zeroline=False,
                title_font=dict(size=12, color=Theme.TEXT_SECONDARY),
                tickfont=dict(size=10, color=Theme.TEXT_MUTED)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(106, 72, 187, 0.08)',
                zeroline=False,
                title_font=dict(size=12, color=Theme.TEXT_SECONDARY),
                tickfont=dict(size=10, color=Theme.TEXT_MUTED)
            ),
            hoverlabel=dict(
                bgcolor='rgba(26, 23, 41, 0.95)',
                font_size=12,
                font_color=Theme.TEXT_PRIMARY
            )
        )
    )
    pio.templates.default = "scriptpulse_dark"

def apply_theme_to_css(css_string: str) -> str:
    """Injects theme values into a CSS string."""
    replacements = {
        "{BG_PRIMARY}": Theme.BG_PRIMARY,
        "{BG_SECONDARY}": Theme.BG_SECONDARY,
        "{BG_CARD}": Theme.BG_CARD,
        "{BG_CARD_HOVER}": Theme.BG_CARD_HOVER,
        "{TEXT_PRIMARY}": Theme.TEXT_PRIMARY,
        "{TEXT_SECONDARY}": Theme.TEXT_SECONDARY,
        "{TEXT_MUTED}": Theme.TEXT_MUTED,
        "{ACCENT_PRIMARY}": Theme.ACCENT_PRIMARY,
        "{ACCENT_SECONDARY}": Theme.ACCENT_SECONDARY,
        "{ACCENT_WARM}": Theme.ACCENT_WARM,
        "{ACCENT_TEAL}": Theme.ACCENT_TEAL,
        "{ACCENT_ROSE}": Theme.ACCENT_ROSE,
        "{ACCENT_BLUE}": Theme.ACCENT_BLUE,
        "{ACCENT_PURPLE}": Theme.ACCENT_PURPLE,
        "{SEMANTIC_GOOD}": Theme.SEMANTIC_GOOD,
        "{SEMANTIC_WARNING}": Theme.SEMANTIC_WARNING,
        "{SEMANTIC_CRITICAL}": Theme.SEMANTIC_CRITICAL,
        "{SEMANTIC_INFO}": Theme.SEMANTIC_INFO,
    }
    for k, v in replacements.items():
        css_string = css_string.replace(k, v)
    return css_string
