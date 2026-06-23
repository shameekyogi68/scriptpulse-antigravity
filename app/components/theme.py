# MODULE: theme.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import plotly.graph_objects as go
import plotly.io as pio

class Theme:
    # Core Backgrounds
    BG_PRIMARY = "#121212"
    BG_SECONDARY = "#1E1E1E"
    BG_CARD = "rgba(255, 255, 255, 0.03)"
    BG_CARD_HOVER = "rgba(255, 255, 255, 0.06)"
    
    # Text
    TEXT_PRIMARY = "#E0E0E0"
    TEXT_SECONDARY = "#9E9E9E"
    TEXT_MUTED = "rgba(224, 224, 224, 0.45)"
    
    # Accents & Brand
    ACCENT_PRIMARY = "#9B51E0"
    ACCENT_SECONDARY = "#7B3FE4"
    ACCENT_WARM = "#FF7043"
    ACCENT_TEAL = "#00C853"
    ACCENT_ROSE = "#FF3366"
    ACCENT_BLUE = "#55E0FF"
    ACCENT_PURPLE = "#A56DFF"
    ACCENT_AMBER = "#FFB700"
    
    # Semantic
    SEMANTIC_GOOD = "#00C853"
    SEMANTIC_WARNING = "#FF7043"
    SEMANTIC_CRITICAL = "#FF3366"
    SEMANTIC_INFO = "#55E0FF"

def init_plotly_template():
    """Initializes and registers the custom ScriptPulse Plotly template."""
    pio.templates["scriptpulse_dark"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'Inter', sans-serif", color=Theme.TEXT_PRIMARY),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.04)',
                zeroline=False,
                title_font=dict(family="'Outfit', sans-serif", size=12, color=Theme.TEXT_SECONDARY),
                tickfont=dict(family="'Inter', sans-serif", size=10, color=Theme.TEXT_MUTED)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.04)',
                zeroline=False,
                title_font=dict(family="'Outfit', sans-serif", size=12, color=Theme.TEXT_SECONDARY),
                tickfont=dict(family="'Inter', sans-serif", size=10, color=Theme.TEXT_MUTED)
            ),
            hoverlabel=dict(
                bgcolor='rgba(18, 18, 18, 0.95)',
                bordercolor='rgba(255, 255, 255, 0.08)',
                font=dict(family="'Inter', sans-serif", size=12, color=Theme.TEXT_PRIMARY)
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
        "{ACCENT_AMBER}": Theme.ACCENT_AMBER,
        "{SEMANTIC_GOOD}": Theme.SEMANTIC_GOOD,
        "{SEMANTIC_WARNING}": Theme.SEMANTIC_WARNING,
        "{SEMANTIC_CRITICAL}": Theme.SEMANTIC_CRITICAL,
        "{SEMANTIC_INFO}": Theme.SEMANTIC_INFO,
    }
    for k, v in replacements.items():
        css_string = css_string.replace(k, v)
    return css_string
