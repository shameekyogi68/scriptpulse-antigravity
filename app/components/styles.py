import streamlit as st

def apply_custom_styles():
    """Applies the 'Premium Instrument' visual language via CSS — Writer-First Design."""
    from app.components.theme import apply_theme_to_css
    
    css = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@300;500;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
        /* ===== ROOT DESIGN TOKENS ===== */
        :root {
            --bg-primary: {BG_PRIMARY};
            --bg-secondary: {BG_SECONDARY};
            --bg-card: {BG_CARD};
            --bg-card-hover: {BG_CARD_HOVER};
            --border-subtle: rgba(106, 72, 187, 0.25);
            --border-glow: rgba(106, 72, 187, 0.6);
            --text-primary: {TEXT_PRIMARY};
            --text-secondary: {TEXT_SECONDARY};
            --text-muted: {TEXT_MUTED};
            --accent-primary: {ACCENT_PRIMARY};
            --accent-secondary: {ACCENT_SECONDARY};
            --accent-warm: {ACCENT_WARM};
            --accent-teal: {ACCENT_TEAL};
            --accent-rose: {ACCENT_ROSE};
            --accent-blue: {ACCENT_BLUE};
            --gradient-hero: linear-gradient(135deg, {ACCENT_PRIMARY} 0%, {ACCENT_PURPLE} 50%, {ACCENT_ROSE} 100%);
            --gradient-subtle: linear-gradient(135deg, rgba(106, 72, 187, 0.08) 0%, rgba(217, 41, 135, 0.05) 100%);
            --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);
            --shadow-glow: 0 0 20px rgba(106, 72, 187, 0.25);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
        }

        /* ===== GLOBAL ===== */
        .stApp {
            background: var(--bg-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 4rem !important;
            max-width: 1100px !important;
        }

        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, .stTitle {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
            color: var(--text-primary) !important;
        }
        
        h1 { font-size: 2.2rem !important; }
        h2 { font-size: 1.5rem !important; margin-top: 1.5rem !important; }
        h3 { font-size: 1.15rem !important; }
        
        p, li, label, .stMarkdown {
            color: var(--text-primary) !important;
            line-height: 1.7 !important;
        }
        
        .stCaption, caption { color: var(--text-muted) !important; }

        /* ===== HIDE STREAMLIT CHROME ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ===== METRIC CARDS ===== */
        div[data-testid="stMetric"] {
            background: var(--bg-card) !important;
            backdrop-filter: blur(12px) !important;
            padding: 20px 24px !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid var(--border-subtle) !important;
            box-shadow: var(--shadow-card) !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: var(--border-glow) !important;
            box-shadow: var(--shadow-glow) !important;
            transform: translateY(-2px) !important;
        }
        
        div[data-testid="stMetric"] label {
            color: var(--text-secondary) !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
        }

        /* ===== SIGNAL BOXES (Insight Cards) ===== */
        .signal-box {
            padding: 20px 24px;
            border-radius: var(--radius-lg);
            margin-bottom: 16px;
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            box-shadow: var(--shadow-card);
            transition: all 0.3s ease;
            line-height: 1.7;
        }
        
        .signal-box:hover {
            transform: translateY(-2px);
            border-color: var(--border-glow);
            box-shadow: var(--shadow-glow);
        }

        /* ===== INSIGHT CARDS (Color-Coded) ===== */
        .insight-critical {
            padding: 18px 22px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
            background: rgba(255, 51, 102, 0.08); /* #FF3366 */
            border-left: 4px solid var(--accent-rose);
            border-top: 1px solid rgba(255, 51, 102, 0.12);
            border-right: 1px solid rgba(255, 51, 102, 0.06);
            border-bottom: 1px solid rgba(255, 51, 102, 0.06);
            color: var(--text-primary);
            line-height: 1.7;
        }
        
        .insight-warning {
            padding: 18px 22px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
            background: rgba(245, 121, 70, 0.08); /* #F57946 */
            border-left: 4px solid var(--accent-warm);
            border-top: 1px solid rgba(245, 121, 70, 0.12);
            border-right: 1px solid rgba(245, 121, 70, 0.06);
            border-bottom: 1px solid rgba(245, 121, 70, 0.06);
            color: var(--text-primary);
            line-height: 1.7;
        }
        
        .insight-good {
            padding: 18px 22px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
            background: rgba(0, 210, 160, 0.08); /* #00D2A0 */
            border-left: 4px solid var(--accent-teal);
            border-top: 1px solid rgba(0, 210, 160, 0.12);
            border-right: 1px solid rgba(0, 210, 160, 0.06);
            border-bottom: 1px solid rgba(0, 210, 160, 0.06);
            color: var(--text-primary);
            line-height: 1.7;
        }
        
        .insight-info {
            padding: 18px 22px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
            background: rgba(142, 197, 233, 0.08); /* #8EC5E9 */
            border-left: 4px solid var(--accent-blue);
            border-top: 1px solid rgba(142, 197, 233, 0.12);
            border-right: 1px solid rgba(142, 197, 233, 0.06);
            border-bottom: 1px solid rgba(142, 197, 233, 0.06);
            color: var(--text-primary);
            line-height: 1.7;
        }
        
        /* ===== HERO SECTION ===== */
        .hero-container {
            text-align: center;
            padding: 2rem 1rem 1rem;
        }
        
        .hero-container h1 {
            font-size: 3.2rem !important;
            margin-bottom: 0.1rem;
            letter-spacing: -0.04em !important;
            background: none !important;
            -webkit-text-fill-color: initial !important;
            background-clip: initial !important;
        }

        .brand-script {
            color: white !important;
            -webkit-text-fill-color: white !important;
        }

        .brand-pulse {
            color: #55e0ff !important;
            -webkit-text-fill-color: #55e0ff !important;
            text-shadow: 0 0 20px rgba(85, 224, 255, 0.3);
        }
        
        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.05rem;
            font-weight: 300;
            letter-spacing: 0.02em;
        }
        
        /* ===== SECTION HEADERS ===== */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 2rem 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .section-header .icon {
            font-size: 1.3rem;
            opacity: 0.7;
        }
        
        .section-header h2 {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .section-explainer {
            color: var(--text-secondary);
            font-size: 0.88rem;
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: var(--bg-secondary) !important;
            border-radius: var(--radius-md) !important;
            padding: 4px !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px !important;
            background-color: transparent !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--bg-card) !important;
            color: var(--accent-primary) !important;
            box-shadow: var(--shadow-card) !important;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: var(--accent-primary) !important;
        }

        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {
            background: var(--bg-card) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border-subtle) !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }

        /* ===== BUTTONS ===== */
        .stButton > button[kind="primary"] {
            background: var(--gradient-hero) !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.6rem 2rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 16px rgba(106, 72, 187, 0.3) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 24px rgba(106, 72, 187, 0.5) !important;
        }
        
        .stButton > button {
            border-radius: var(--radius-md) !important;
            transition: all 0.2s ease !important;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background: var(--bg-card) !important;
            border-radius: var(--radius-lg) !important;
            border: 2px dashed var(--border-subtle) !important;
            padding: 1.5rem !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-primary) !important;
        }

        /* ===== SELECT BOX / INPUTS ===== */
        [data-baseweb="select"], [data-baseweb="input"] {
            border-radius: var(--radius-sm) !important;
        }

        /* ===== DOWNLOAD BUTTONS ===== */
        .stDownloadButton > button {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stDownloadButton > button:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: var(--shadow-glow) !important;
            transform: translateY(-1px) !important;
        }

        /* ===== TEXT AREA (Script Reader) ===== */
        textarea {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: 'JetBrains Mono', 'Courier New', monospace !important;
            font-size: 0.88rem !important;
            line-height: 1.65 !important;
        }

        /* ===== PROGRESS BARS ===== */
        .stProgress > div > div > div {
            background: var(--gradient-hero) !important;
            border-radius: 4px !important;
        }

        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .element-container {
            animation: fadeInUp 0.4s ease-out;
        }

        /* ===== DIVIDER ===== */
        hr {
            border-color: var(--border-subtle) !important;
            opacity: 0.5 !important;
        }

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown { color: var(--text-primary) !important; }

        /* ===== BOOTSTRAP ICON OVERRIDES ===== */
        .bi { font-size: 1.1em; vertical-align: middle; margin-right: 8px; }
        .icon-pass { color: var(--accent-teal); }
        .icon-fail { color: var(--accent-rose); }
        
        /* ===== TOOLTIP CARDS ===== */
        .tooltip-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 12px 16px;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        /* ===== SCORE BADGE ===== */
        .score-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .score-high { background: rgba(0, 210, 160, 0.15); color: #00D2A0; }
        .score-mid { background: rgba(245, 121, 70, 0.15); color: #F57946; }
        .score-low { background: rgba(255, 51, 102, 0.15); color: #FF3366; }
    </style>
    """
    
    st.markdown(apply_theme_to_css(css), unsafe_allow_html=True)
