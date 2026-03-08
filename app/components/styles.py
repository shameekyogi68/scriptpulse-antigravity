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
        /* Hide Streamlit's default header space */
        header, [data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary); 
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(106, 72, 187, 0.5); 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(106, 72, 187, 0.9); 
        }

        .stApp {
            background: var(--bg-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            padding-top: 0rem !important;
            margin-top: -3rem !important; /* Pull content into the header area */
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
            background: linear-gradient(135deg, rgba(40, 36, 60, 0.8) 0%, rgba(32, 29, 48, 0.95) 100%) !important;
            backdrop-filter: blur(16px) !important;
            padding: 24px 28px !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.05) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stMetric"]::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important; height: 3px !important;
            background: var(--gradient-hero) !important;
            opacity: 0 !important;
            transition: opacity 0.4s ease !important;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-6px) scale(1.02) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(106, 72, 187, 0.4) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }
        
        div[data-testid="stMetric"]:hover::before {
            opacity: 1 !important;
        }
        
        div[data-testid="stMetric"] label {
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            font-weight: 600 !important;
            margin-bottom: 10px !important;
        }
        
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: white !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2.6rem !important;
            text-shadow: 0 2px 15px rgba(255, 255, 255, 0.15) !important;
            letter-spacing: -0.02em !important;
        }

        /* ===== SIGNAL BOXES (Insight Cards) ===== */
        .signal-box {
            padding: 24px 28px;
            border-radius: var(--radius-lg);
            margin-bottom: 20px;
            background: linear-gradient(135deg, rgba(32, 29, 48, 0.7) 0%, rgba(26, 23, 41, 0.95) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.05);
            border-top: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: all 0.4s ease;
            line-height: 1.8;
            font-size: 1.05rem;
        }
        
        .signal-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 20px rgba(106, 72, 187, 0.25);
            border-color: rgba(255,255,255,0.15);
        }

        /* ===== INSIGHT CARDS (Color-Coded) ===== */
        .insight-critical {
            padding: 20px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 16px;
            background: linear-gradient(90deg, rgba(255, 51, 102, 0.15) 0%, rgba(255, 51, 102, 0.02) 100%);
            border-left: 4px solid var(--accent-rose);
            border-top: 1px solid rgba(255, 51, 102, 0.1);
            border-right: 1px solid rgba(255, 51, 102, 0.05);
            border-bottom: 1px solid rgba(255, 51, 102, 0.05);
            color: var(--text-primary);
            line-height: 1.8;
            box-shadow: -4px 0 15px rgba(255, 51, 102, 0.15);
            font-size: 1.05rem;
        }
        
        .insight-warning {
            padding: 20px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 16px;
            background: linear-gradient(90deg, rgba(245, 121, 70, 0.15) 0%, rgba(245, 121, 70, 0.02) 100%);
            border-left: 4px solid var(--accent-warm);
            border-top: 1px solid rgba(245, 121, 70, 0.1);
            border-right: 1px solid rgba(245, 121, 70, 0.05);
            border-bottom: 1px solid rgba(245, 121, 70, 0.05);
            color: var(--text-primary);
            line-height: 1.8;
            box-shadow: -4px 0 15px rgba(245, 121, 70, 0.15);
            font-size: 1.05rem;
        }
        
        .insight-good {
            padding: 20px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 16px;
            background: linear-gradient(90deg, rgba(0, 210, 160, 0.15) 0%, rgba(0, 210, 160, 0.02) 100%);
            border-left: 4px solid var(--accent-teal);
            border-top: 1px solid rgba(0, 210, 160, 0.1);
            border-right: 1px solid rgba(0, 210, 160, 0.05);
            border-bottom: 1px solid rgba(0, 210, 160, 0.05);
            color: var(--text-primary);
            line-height: 1.8;
            box-shadow: -4px 0 15px rgba(0, 210, 160, 0.15);
            font-size: 1.05rem;
        }
        
        .insight-info {
            padding: 20px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 16px;
            background: linear-gradient(90deg, rgba(0, 153, 255, 0.15) 0%, rgba(0, 153, 255, 0.02) 100%);
            border-left: 4px solid #0099ff;
            border-top: 1px solid rgba(0, 153, 255, 0.1);
            border-right: 1px solid rgba(0, 153, 255, 0.05);
            border-bottom: 1px solid rgba(0, 153, 255, 0.05);
            color: var(--text-primary);
            line-height: 1.8;
            box-shadow: -4px 0 15px rgba(0, 153, 255, 0.15);
            font-size: 1.05rem;
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
            gap: 12px !important;
            background: rgba(32, 29, 48, 0.5) !important;
            border-radius: var(--radius-lg) !important;
            padding: 6px !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255,255,255,0.03) !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px !important;
            background-color: transparent !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            padding: 8px 24px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--accent-primary) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(106, 72, 187, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: transparent !important;
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
            background-size: 200% auto !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: var(--radius-md) !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            letter-spacing: 0.03em !important;
            padding: 1rem 2.5rem !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 20px rgba(106, 72, 187, 0.4), inset 0 2px 0 rgba(255, 255, 255, 0.2) !important;
            text-transform: uppercase !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-4px) scale(1.02) !important;
            box-shadow: 0 10px 30px rgba(217, 41, 135, 0.6), inset 0 2px 0 rgba(255, 255, 255, 0.3) !important;
            background-position: right center !important;
        }
        
        .stButton > button {
            border-radius: var(--radius-md) !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background: linear-gradient(180deg, rgba(32, 29, 48, 0.4), rgba(32, 29, 48, 0.8)) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: var(--radius-lg) !important;
            border: 2px dashed rgba(85, 224, 255, 0.3) !important;
            padding: 2.5rem 2rem !important;
            transition: all 0.4s ease !important;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.2) !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #55e0ff !important;
            background: linear-gradient(180deg, rgba(40, 36, 60, 0.6), rgba(40, 36, 60, 0.9)) !important;
            box-shadow: 0 0 30px rgba(85, 224, 255, 0.2), inset 0 0 20px rgba(85, 224, 255, 0.1) !important;
            transform: translateY(-2px) !important;
        }

        /* ===== SELECT BOX / INPUTS ===== */
        [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
            background: rgba(32, 29, 48, 0.8) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            transition: all 0.3s ease !important;
            color: var(--text-primary) !important;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        
        [data-baseweb="select"], [data-baseweb="select"] div, [data-baseweb="select"] input {
            cursor: pointer !important;
        }
        
        [data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover, [data-baseweb="textarea"] > div:hover {
            border-color: #55e0ff !important;
            box-shadow: 0 0 15px rgba(85, 224, 255, 0.15), inset 0 2px 5px rgba(0,0,0,0.2) !important;
        }
        
        [data-baseweb="popover"] {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-card) !important;
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
            background: linear-gradient(135deg, rgba(40, 36, 60, 0.6) 0%, rgba(32, 29, 48, 0.8) 100%);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.05);
            border-left: 2px solid var(--accent-primary);
            border-radius: var(--radius-sm);
            padding: 14px 18px;
            font-size: 0.88rem;
            color: rgba(244, 246, 251, 0.85);
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            line-height: 1.6;
        }
        
        /* ===== SCORE BADGE ===== */
        .score-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.1);
            backdrop-filter: blur(4px);
        }
        .score-high { background: linear-gradient(90deg, rgba(0,210,160,0.2) 0%, rgba(0,210,160,0.05) 100%); color: #00D2A0; border: 1px solid rgba(0,210,160,0.3); box-shadow: 0 0 10px rgba(0,210,160,0.2); }
        .score-mid { background: linear-gradient(90deg, rgba(245,121,70,0.2) 0%, rgba(245,121,70,0.05) 100%); color: #F57946; border: 1px solid rgba(245,121,70,0.3); box-shadow: 0 0 10px rgba(245,121,70,0.2); }
        .score-low { background: linear-gradient(90deg, rgba(255,51,102,0.2) 0%, rgba(255,51,102,0.05) 100%); color: #FF3366; border: 1px solid rgba(255,51,102,0.3); box-shadow: 0 0 10px rgba(255,51,102,0.2); }
    </style>
    """
    
    st.markdown(apply_theme_to_css(css), unsafe_allow_html=True)
