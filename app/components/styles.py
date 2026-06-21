# MODULE: styles.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import streamlit as st

def apply_custom_styles():
    """Applies the 'Premium Instrument' visual language via CSS — Writer-First Design."""
    from app.components.theme import apply_theme_to_css
    
    css = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont/tabler-icons.min.css">
    
    <style>
        /* ===== ROOT DESIGN TOKENS ===== */
        :root {
            --bg-primary: {BG_PRIMARY};
            --bg-secondary: {BG_SECONDARY};
            --bg-card: {BG_CARD};
            --bg-card-hover: {BG_CARD_HOVER};
            --border-subtle: rgba(155, 81, 224, 0.2);
            --border-glow: rgba(155, 81, 224, 0.5);
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
            --gradient-subtle: linear-gradient(135deg, rgba(155, 81, 224, 0.08) 0%, rgba(255, 112, 67, 0.05) 100%);
            --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
            --shadow-glow: 0 0 20px rgba(155, 81, 224, 0.25);
            --radius-sm: 8px;
            --radius-md: 16px;
            --radius-lg: 24px;
            --radius-xl: 24px;
        }

        /* Hide Streamlit's default header space */
        header, [data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
        }

        /* Hide sidebar toggle control completely */
        [data-testid="collapsedControl"] {
            display: none !important;
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
            background: rgba(155, 81, 224, 0.4); 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(155, 81, 224, 0.7); 
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
            max-width: 1360px !important;
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
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            padding: 24px 28px !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stMetric"]::before {
            display: none !important;
        }
        
        div[data-testid="stMetric"]::after {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%) !important;
            pointer-events: none !important;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
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
            animation: pulse-rose 3s infinite ease-in-out;
            transition: all 0.3s ease;
        }
        
        .insight-critical:hover {
            transform: translateX(4px);
            background: linear-gradient(90deg, rgba(255, 51, 102, 0.25) 0%, rgba(255, 51, 102, 0.05) 100%);
        }
        
        @keyframes pulse-rose {
            0% { box-shadow: -4px 0 15px rgba(255, 51, 102, 0.15); }
            50% { box-shadow: -4px 0 30px rgba(255, 51, 102, 0.3); }
            100% { box-shadow: -4px 0 15px rgba(255, 51, 102, 0.15); }
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
            animation: pulse-orange 4s infinite ease-in-out;
            transition: all 0.3s ease;
        }
        
        .insight-warning:hover {
            transform: translateX(4px);
            background: linear-gradient(90deg, rgba(245, 121, 70, 0.25) 0%, rgba(245, 121, 70, 0.05) 100%);
        }

        @keyframes pulse-orange {
            0% { box-shadow: -4px 0 15px rgba(245, 121, 70, 0.15); }
            50% { box-shadow: -4px 0 25px rgba(245, 121, 70, 0.25); }
            100% { box-shadow: -4px 0 15px rgba(245, 121, 70, 0.15); }
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
            animation: pulse-teal 5s infinite ease-in-out;
            transition: all 0.3s ease;
        }
        
        .insight-good:hover {
            transform: translateX(4px);
            background: linear-gradient(90deg, rgba(0, 210, 160, 0.25) 0%, rgba(0, 210, 160, 0.05) 100%);
        }

        @keyframes pulse-teal {
            0% { box-shadow: -4px 0 15px rgba(0, 210, 160, 0.15); }
            50% { box-shadow: -4px 0 25px rgba(0, 210, 160, 0.3); }
            100% { box-shadow: -4px 0 15px rgba(0, 210, 160, 0.15); }
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
            animation: pulse-blue 6s infinite ease-in-out;
            transition: all 0.3s ease;
        }

        .insight-info:hover {
            transform: translateX(4px);
            background: linear-gradient(90deg, rgba(0, 153, 255, 0.25) 0%, rgba(0, 153, 255, 0.05) 100%);
        }

        @keyframes pulse-blue {
            0% { box-shadow: -4px 0 15px rgba(0, 153, 255, 0.15); }
            50% { box-shadow: -4px 0 25px rgba(0, 153, 255, 0.3); }
            100% { box-shadow: -4px 0 15px rgba(0, 153, 255, 0.15); }
        }
        
        /* ===== HERO SECTION ===== */
        .hero-container {
            text-align: center;
            padding: 2rem 1rem 1rem;
            position: relative;
        }

        .hero-container::before {
            content: '';
            position: absolute;
            top: -40px; left: 50%; transform: translateX(-50%);
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(155, 81, 224, 0.08) 0%, rgba(155, 81, 224, 0.03) 40%, transparent 70%);
            pointer-events: none;
            animation: heroGlow 6s ease-in-out infinite;
            z-index: 0;
        }

        @keyframes heroGlow {
            0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1); }
            50% { opacity: 1; transform: translateX(-50%) scale(1.15); }
        }
        
        .hero-container h1 {
            font-size: 3.2rem !important;
            margin-bottom: 0.1rem;
            letter-spacing: -0.04em !important;
            background: none !important;
            -webkit-text-fill-color: initial !important;
            background-clip: initial !important;
            position: relative;
            z-index: 1;
        }

        .brand-script {
            color: white !important;
            -webkit-text-fill-color: white !important;
        }

        .brand-pulse {
            background: linear-gradient(135deg, #A56DFF 0%, var(--accent-primary) 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            display: inline-block !important;
            filter: drop-shadow(0 0 15px rgba(155, 81, 224, 0.45)) !important;
        }
        
        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.05rem;
            font-weight: 300;
            letter-spacing: 0.02em;
            position: relative;
            z-index: 1;
        }

        /* ===== TRUST BAR ===== */
        .trust-bar {
            display: inline-flex !important;
            gap: 32px !important;
            padding: 12px 32px !important;
            border-radius: 50px !important;
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            margin: 20px auto 0 auto !important;
        }
        .trust-bar .trust-item {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
        .trust-bar .trust-item .trust-dot {
            width: 6px !important;
            height: 6px !important;
            border-radius: 50% !important;
            background: var(--accent-teal) !important;
            box-shadow: 0 0 8px rgba(0, 200, 83, 0.6) !important;
            animation: trustPulse 2s ease-in-out infinite !important;
        }
        @keyframes trustPulse {
            0%, 100% { box-shadow: 0 0 6px rgba(0, 200, 83, 0.6); }
            50% { box-shadow: 0 0 12px rgba(0, 200, 83, 0.9); }
        }

        /* ===== FOOTER ===== */
        .sp-footer {
            text-align: center;
            padding: 2.5rem 1rem 1.5rem;
            margin-top: 3rem;
            border-top: 1px solid rgba(155, 81, 224, 0.15) !important;
            color: rgba(224, 224, 224, 0.35) !important;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
        }
        .sp-footer a {
            color: var(--accent-primary) !important;
            text-decoration: none;
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
            background: rgba(0, 0, 0, 0.2) !important;
            border-radius: 14px !important;
            padding: 6px !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255,255,255,0.03) !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px !important;
            background-color: transparent !important;
            border-radius: 10px !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 8px 20px !important;
            transition: all 0.2s ease !important;
            border: 1px solid transparent !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            color: white !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
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
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
            border: none !important;
            border-radius: 40px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            letter-spacing: 0.03em !important;
            padding: 12px 30px !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 15px rgba(155, 81, 224, 0.4) !important;
            text-transform: uppercase !important;
            cursor: pointer !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(155, 81, 224, 0.6) !important;
        }
        
        .stButton > button {
            border-radius: 20px !important;
            border: 1px solid var(--border-subtle) !important;
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }
        
        .stButton > button:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 15px rgba(155, 81, 224, 0.25) !important;
            color: white !important;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.01) !important;
            backdrop-filter: blur(24px) !important;
            border-radius: var(--radius-lg) !important;
            border: 2px dashed var(--border-subtle) !important;
            padding: 2.5rem 2rem !important;
            transition: all 0.4s ease !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-primary) !important;
            background: rgba(255, 255, 255, 0.03) !important;
            box-shadow: 0 0 30px rgba(155, 81, 224, 0.15), inset 0 4px 12px rgba(0,0,0,0.4) !important;
            transform: translateY(-2px) !important;
        }

        /* ===== SELECT BOX / INPUTS ===== */
        [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
            background: rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important;
            transition: all 0.3s ease !important;
            color: var(--text-primary) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
        }
        
        [data-baseweb="select"], [data-baseweb="select"] div, [data-baseweb="select"] input {
            cursor: pointer !important;
        }
        
        [data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover, [data-baseweb="textarea"] > div:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 15px rgba(155, 81, 224, 0.15), inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
        }
        
        [data-baseweb="popover"] {
            background: var(--bg-secondary) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-card) !important;
        }

        /* ===== STREAMLIT NOTIFICATION / INFO BOX WELL ===== */
        div[data-testid="stNotification"], .stAlert {
            background-color: rgba(59, 130, 246, 0.05) !important;
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
            border-radius: var(--radius-md) !important;
            color: rgba(219, 234, 254, 0.75) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        }
        div[data-testid="stNotification"] *, .stAlert * {
            color: rgba(219, 234, 254, 0.75) !important;
        }


        /* ===== DOWNLOAD BUTTONS ===== */
        .stDownloadButton > button {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 20px !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }
        
        .stDownloadButton > button:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 15px rgba(155, 81, 224, 0.25) !important;
            transform: translateY(-1px) !important;
            color: white !important;
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
            background-size: 200% auto !important;
            animation: progressShimmer 2s linear infinite !important;
            border-radius: 4px !important;
        }
        @keyframes progressShimmer {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .element-container {
            animation: fadeInUp 0.5s cubic-bezier(0.23, 1, 0.32, 1) both;
        }

        /* Stagger: each successive element animates slightly later */
        .element-container:nth-child(2) { animation-delay: 0.05s; }
        .element-container:nth-child(3) { animation-delay: 0.1s; }
        .element-container:nth-child(4) { animation-delay: 0.15s; }
        .element-container:nth-child(5) { animation-delay: 0.2s; }
        .element-container:nth-child(6) { animation-delay: 0.25s; }

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

        /* ===== BRAND GRADIENT ===== */
        .brand-pulse-gradient {
            background: linear-gradient(135deg, #A56DFF 0%, var(--accent-primary) 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            display: inline-block !important;
            filter: drop-shadow(0 0 15px rgba(155, 81, 224, 0.45)) !important;
        }

        /* ===== CUSTOM GLASS CARDS & WELLS ===== */
        .glass-card {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
        }

        .well {
            background: rgba(0, 0, 0, 0.2) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
        }

        /* ===== VERTICAL CONTAINER BORDER WRAPPER ===== */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[class*="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-lg) !important;
            padding: 30px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]::after,
        div[class*="stVerticalBlockBorderWrapper"]::after {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%) !important;
            pointer-events: none !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        div[class*="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"],
        div[class*="stVerticalBlockBorderWrapper"] [class*="stVerticalBlock"] {
            background: transparent !important;
        }

        /* ===== CUSTOM METRIC CARDS ===== */
        .custom-metric-card {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important;
            padding: 20px !important;
            text-align: left !important;
            height: 100px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: visible !important;
            margin-bottom: 12px !important;
        }
        
        .custom-metric-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }

        .custom-metric-card::after {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%) !important;
            pointer-events: none !important;
            border-radius: var(--radius-md) !important;
        }

        /* ===== COMPARABLE FILM CARDS ===== */
        .comp-film-card {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            padding: 12px 18px !important;
            text-align: center !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            backdrop-filter: blur(12px) !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin-bottom: 8px !important;
        }
        
        .comp-film-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 25px rgba(155, 81, 224, 0.35) !important;
            border-color: var(--accent-primary) !important;
        }

        /* ===== MENTOR CARDS ===== */
        .mentor-card {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid var(--border-subtle) !important;
            border-left: 4px solid var(--accent-primary) !important;
            border-radius: var(--radius-md) !important;
            padding: 18px 22px !important;
            margin-bottom: 14px !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.25) !important;
            backdrop-filter: blur(12px) !important;
            transition: all 0.3s ease !important;
        }
        
        .mentor-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(155, 81, 224, 0.25) !important;
            border-color: rgba(155, 81, 224, 0.4) !important;
        }
    </style>
    """
    
    st.markdown(apply_theme_to_css(css), unsafe_allow_html=True)
