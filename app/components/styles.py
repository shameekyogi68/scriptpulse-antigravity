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
        /* ===== ROOT DESIGN TOKENS — Tactile Glass Language ===== */
        :root {
            /* Backgrounds */
            --obsidian: #121212;
            --bg-primary: {BG_PRIMARY};
            --bg-secondary: {BG_SECONDARY};
            --bg-card: {BG_CARD};
            --bg-card-hover: {BG_CARD_HOVER};
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-blur: 24px;

            /* Borders */
            --border-subtle: rgba(155, 81, 224, 0.2);
            --border-glow: rgba(155, 81, 224, 0.5);

            /* Text */
            --text-primary: {TEXT_PRIMARY};
            --text-secondary: {TEXT_SECONDARY};
            --text-muted: {TEXT_MUTED};

            /* Brand Accents */
            --amethyst: {ACCENT_PRIMARY};
            --amethyst-glow: rgba(155, 81, 224, 0.4);
            --accent-primary: {ACCENT_PRIMARY};
            --accent-secondary: {ACCENT_SECONDARY};
            --accent-warm: {ACCENT_WARM};
            --accent-teal: {ACCENT_TEAL};
            --accent-rose: {ACCENT_ROSE};
            --accent-blue: {ACCENT_BLUE};
            --accent-purple: {ACCENT_PURPLE};

            /* Semantic (template uses these names directly) */
            --emerald: #00C853;
            --emerald-glow: rgba(0, 200, 83, 0.3);
            --coral: #FF7043;
            --coral-glow: rgba(255, 112, 67, 0.3);

            /* Gradients */
            --gradient-hero: linear-gradient(135deg, {ACCENT_PRIMARY} 0%, {ACCENT_PURPLE} 50%, {ACCENT_ROSE} 100%);
            --gradient-subtle: linear-gradient(135deg, rgba(155, 81, 224, 0.08) 0%, rgba(255, 112, 67, 0.05) 100%);

            /* Shadows */
            --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
            --shadow-glow: 0 0 20px rgba(155, 81, 224, 0.25);

            /* Radius */
            --radius-sm: 8px;
            --radius-md: 16px;
            --radius-lg: 24px;
            --radius-xl: 24px;
        }

        /* Hide Streamlit's default header space */
        header[data-testid="stHeader"], [data-testid="stHeader"] {
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

        html, body {
            background: var(--bg-primary) !important;
        }

        .stApp, select, input, textarea, button, p, label, li {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        .stApp {
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            padding-top: 0rem !important;
            margin-top: -3rem !important; /* Pull content into the header area */
            max-width: 1360px !important;
        }
        
        .main .block-container,
        .stMainBlockContainer,
        div[data-testid="stAppViewBlockContainer"] {
            padding-bottom: 0.5rem !important;
        }

        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4, h5, h6, .stTitle, [data-testid="stHeader"] h1, [data-testid="stMetricValue"] {
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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .stCaption, caption { 
            color: var(--text-muted) !important; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ===== HIDE STREAMLIT CHROME ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {visibility: hidden;}

        /* ===== METRIC CARDS ===== */
        div[data-testid="stMetric"] {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            -webkit-backdrop-filter: blur(var(--glass-blur)) !important;
            padding: 24px 28px !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid var(--glass-border) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }

        /* Hardware shimmer on native metric cards */
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
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            font-weight: 700 !important;
            margin-bottom: 10px !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: white !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.02em !important;
        }

        /* ===== SIGNAL BOXES (Insight / Priority Cards) ===== */
        .signal-box {
            padding: 24px 28px;
            border-radius: var(--radius-lg);
            margin-bottom: 20px;
            background: var(--glass-bg);
            backdrop-filter: blur(var(--glass-blur));
            border: 1px solid var(--glass-border);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: all 0.4s ease;
            line-height: 1.8;
            font-size: 1rem;
            position: relative;
            overflow: hidden;
        }

        .signal-box::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
            pointer-events: none;
        }

        .signal-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(155, 81, 224, 0.2);
            border-color: rgba(255, 255, 255, 0.15);
        }

        /* ===== INSIGHT CARDS (Color-coded, template .insight-item pattern) ===== */
        .insight-item {
            display: flex;
            gap: 16px;
            padding: 20px;
            margin-bottom: 12px;
            border-radius: var(--radius-md);
            transition: all 0.2s ease;
        }

        .insight-item:hover {
            transform: translateX(3px);
        }

        .insight-icon-box {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }

        .insight-good  { background: rgba(0, 200, 83, 0.05);  border-left: 4px solid var(--emerald); }
        .insight-warning { background: rgba(255, 112, 67, 0.05); border-left: 4px solid var(--coral); }
        .insight-critical { background: rgba(255, 51, 102, 0.05); border-left: 4px solid var(--accent-rose); }
        
        /* ===== HERO SECTION — Tactile Glass template ===== */
        .hero-header {
            text-align: center;
            margin-bottom: 60px;
        }

        .brand-logo {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 4rem;
            letter-spacing: -0.04em;
            margin-bottom: 12px;
            line-height: 1;
        }

        .brand-pulse {
            background: linear-gradient(135deg, #A56DFF 0%, var(--amethyst) 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            display: inline-block !important;
            filter: drop-shadow(0 0 15px var(--amethyst-glow)) !important;
        }

        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.125rem;
            font-weight: 500;
            letter-spacing: 0;
            max-width: 42rem;
            margin: 0 auto 2rem auto;
            line-height: 1.6;
        }

        /* ===== TRUST BAR ===== */
        .trust-bar {
            display: inline-flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            gap: 32px !important;
            padding: 12px 32px !important;
            border-radius: 50px !important;
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid var(--glass-border) !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
        }
        .trust-bar .trust-item {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            white-space: nowrap !important;
        }
        .trust-bar .trust-dot,
        .trust-bar [class*="trust-dot"] {
            width: 6px !important;
            height: 6px !important;
            border-radius: 50% !important;
            background: var(--emerald) !important;
            box-shadow: 0 0 8px var(--emerald-glow) !important;
            display: inline-block !important;
            flex-shrink: 0 !important;
        }

        /* ===== FOOTER — Tactile Glass template footer spec ===== */
        .sp-footer {
            text-align: center;
            padding: 1rem 1rem;
            margin-top: 1rem;
            border-top: 1px solid var(--glass-border) !important;
        }

        .sp-footer > div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 32px !important;
            font-size: 0.7rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            color: var(--text-secondary) !important;
            opacity: 0.6 !important;
            flex-wrap: wrap !important;
        }

        .sp-footer a {
            color: var(--amethyst) !important;
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

        /* ===== TABS — Tactile Glass .tab-bar spec ===== */
        /* Outer tab header container — cohesive glass design */
        div[data-testid="stTabs"] > div:first-child > div:first-child {
            gap: 8px !important;
            background: rgba(0, 0, 0, 0.25) !important;
            border-radius: 16px !important;
            padding: 6px 40px !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            margin-bottom: 16px !important;
            position: relative !important;
            display: flex !important;
            align-items: center !important;
            overflow: hidden !important;
        }

        /* Inner tab lists — completely transparent to prevent double layers */
        .stTabs [data-baseweb="tab-list"],
        .stTabs [role="tablist"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            gap: 8px !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Hide native scrollbars and enable smooth scrolling on the tabs scroller wrapper */
        div[data-testid="stTabs"] > div:first-child > div:first-child > div {
            scrollbar-width: none !important; /* Firefox */
            scroll-behavior: smooth !important;
        }
        div[data-testid="stTabs"] > div:first-child > div:first-child > div::-webkit-scrollbar {
            display: none !important; /* Chrome, Safari, Opera */
            width: 0 !important;
            height: 0 !important;
        }

        /* Apply smooth gradient mask on the scrollable wrapper to fade tabs near edges */
        div[data-testid="stTabs"] > div:first-child > div:first-child > div {
            mask-image: linear-gradient(to right, transparent 0%, black 25px, black calc(100% - 25px), transparent 100%) !important;
            -webkit-mask-image: linear-gradient(to right, transparent 0%, black 25px, black calc(100% - 25px), transparent 100%) !important;
        }

        /* Style the tab list scroll buttons to fit the glass theme and position them inside the edges */
        div[data-testid="stTabs"] > div:first-child > div:first-child button:not([role="tab"]):not([data-baseweb="tab"]),
        div[data-testid="stTabs"] > div:first-child > div:first-child [role="button"]:not([role="tab"]):not([data-baseweb="tab"]) {
            background: rgba(0, 0, 0, 0.45) !important;
            border-radius: 50% !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: white !important;
            backdrop-filter: blur(8px) !important;
            width: 28px !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
            position: absolute !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            margin: 0 !important;
            cursor: pointer !important;
            z-index: 10 !important;
        }
        div[data-testid="stTabs"] > div:first-child > div:first-child button:not([role="tab"]):not([data-baseweb="tab"]):hover,
        div[data-testid="stTabs"] > div:first-child > div:first-child [role="button"]:not([role="tab"]):not([data-baseweb="tab"]):hover {
            background: var(--amethyst) !important;
            color: white !important;
            box-shadow: 0 0 10px var(--amethyst-glow) !important;
            transform: translateY(-50%) scale(1.05) !important;
        }
        div[data-testid="stTabs"] > div:first-child > div:first-child button:not([role="tab"]):not([data-baseweb="tab"]):first-of-type,
        div[data-testid="stTabs"] > div:first-child > div:first-child [role="button"]:not([role="tab"]):not([data-baseweb="tab"]):first-of-type {
            left: 8px !important;
        }
        div[data-testid="stTabs"] > div:first-child > div:first-child button:not([role="tab"]):not([data-baseweb="tab"]):last-of-type,
        div[data-testid="stTabs"] > div:first-child > div:first-child [role="button"]:not([role="tab"]):not([data-baseweb="tab"]):last-of-type {
            right: 8px !important;
        }

        /* Align tabs inside the scroller wrapper cleanly */
        div[data-testid="stTabs"] > div:first-child > div:first-child [role="tablist"] > div,
        div[data-testid="stTabs"] > div:first-child > div:first-child [data-baseweb="tab-list"] > div {
            margin-left: 0px !important;
            margin-right: 0px !important;
        }

        /* Remove default margins/padding from tab panels to remove large gaps */
        div[data-testid="stTab"],
        [data-baseweb="tab-panel"] {
            padding-top: 0px !important;
            margin-top: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
        }

        /* Remove top margin of section headers when they are at the top of a tab panel */
        div[data-testid="stTab"] .section-header-wrapper,
        [data-baseweb="tab-panel"] .section-header-wrapper {
            margin-top: 0px !important;
        }

        /* Pixel-align section header icons with text baselines */
        .section-header-wrapper i.ti {
            transform: translateY(11px) !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px !important;
            background-color: transparent !important;
            border-radius: 10px !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
            border: 1px solid transparent !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--glass-bg) !important;
            color: white !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
            border: 1px solid var(--glass-border) !important;
        }

        /* Hide the default blue underline/highlight bar */
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {
            background-color: transparent !important;
            height: 0 !important;
            display: none !important;
        }

        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {
            background: var(--bg-card) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border-subtle) !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
        }

        /* ===== BUTTONS — Tactile Glass .btn-primary spec ===== */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--amethyst) 0%, #7B3FE4 100%) !important;
            border: none !important;
            border-radius: 40px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            letter-spacing: 0.03em !important;
            padding: 14px 28px !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 15px var(--amethyst-glow) !important;
            cursor: pointer !important;
            width: 100% !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px var(--amethyst-glow) !important;
        }

        .stButton > button {
            border-radius: 20px !important;
            border: 1px solid var(--border-subtle) !important;
            background: var(--glass-bg) !important;
            color: var(--text-primary) !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }

        .stButton > button:hover {
            border-color: var(--amethyst) !important;
            box-shadow: 0 0 15px var(--amethyst-glow) !important;
            color: white !important;
        }

        /* Align the "Analyze New Script" button in the controls row */
        .st-key-analyze_new_script_btn button,
        [class*="analyze_new_script_btn"] button,
        div[data-key="analyze_new_script_btn"] button,
        div[id="analyze_new_script_btn"] button {
            transform: translateY(47px) !important;
        }

        /* ===== FILE UPLOADER ===== */
        div.stApp div[data-testid="stFileUploader"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"],
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] {
            background: rgba(0, 0, 0, 0.2) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
            border: 2px dashed rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important;
            padding: 48px 30px !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 16px !important;
        }
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]:hover,
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            background: rgba(255, 255, 255, 0.01) !important;
        }
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] svg,
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] svg {
            display: none !important;
        }
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::before,
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]::before {
            content: "" !important;
            width: 48px !important;
            height: 48px !important;
            margin: 0 auto 0 auto !important;
            display: block !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%239E9E9E' stroke-width='1.25' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M7 18a4.6 4.4 0 0 1 0 -9a5 4.5 0 0 1 11 2h1a3.5 3.5 0 0 1 0 7h-1'/%3E%3Cpath d='M12 17v-9'/%3E%3Cpath d='M9 11l3 -3l3 3'/%3E%3C/svg%3E") !important;
            background-size: contain !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            opacity: 0.4 !important;
            order: 1 !important;
        }
        /* Inject dropzone prompt text */
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::after,
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]::after {
            content: "Drop your screenplay here (PDF, TXT, or FDX)" !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            color: var(--text-secondary) !important;
            margin-top: 4px !important;
            display: block !important;
            text-align: center !important;
            font-family: 'Inter', sans-serif !important;
            order: 2 !important;
        }
        /* Ensure the button wrapper is ordered 3rd */
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > span,
        div.stApp div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] > span {
            order: 3 !important;
            display: block !important;
        }
        /* Hide the native dropzone instructions */
        div.stApp div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        div.stApp div[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] {
            background: linear-gradient(135deg, var(--accent-primary) 0%, #7B3FE4 100%) !important;
            padding: 12px 32px !important;
            border-radius: 40px !important;
            box-shadow: 0 4px 12px rgba(155, 81, 224, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            border: none !important;
            cursor: pointer !important;
            text-transform: uppercase !important;
            margin-top: 12px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div.stApp div[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] * {
            display: none !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        div.stApp div[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]::after {
            content: "SELECT FILE" !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.05em !important;
            color: white !important;
            display: inline-block !important;
        }
        div.stApp div[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(155, 81, 224, 0.35) !important;
        }


        /* ===== SELECT BOX / INPUTS — Premium pill trigger ===== */
        /* Clear all default BaseWeb focus rings, borders, and shadows on select box trigger */
        [data-baseweb="select"] *,
        [data-baseweb="select"] *:focus,
        [data-baseweb="select"] *:focus-within {
            border-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Clear all default BaseWeb focus rings, borders, and shadows on inputs/textareas */
        [data-baseweb="input"] *,
        [data-baseweb="input"] *:focus,
        [data-baseweb="input"] *:focus-within,
        [data-baseweb="textarea"] *,
        [data-baseweb="textarea"] *:focus,
        [data-baseweb="textarea"] *:focus-within {
            border-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }

        /* Apply custom well background and borders ONLY to the outer control container */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div {
            background: rgba(0, 0, 0, 0.2) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important; /* 16px */
            min-height: 48px !important;
            height: 48px !important;
            transition: all 0.25s ease !important;
            color: var(--text-primary) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Selected value text — white + medium weight, centered vertically, matching body text size */
        [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
        [data-baseweb="select"] span,
        [data-baseweb="select"] input,
        [data-baseweb="select"] div[class*="ValueContainer"] span {
            color: white !important;
            font-weight: 400 !important;
            font-size: 0.875rem !important;
            line-height: normal !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-baseweb="select"], [data-baseweb="select"] div, [data-baseweb="select"] input {
            cursor: pointer !important;
        }

        /* Hover + focus states for the outer control container */
        [data-baseweb="select"] > div:hover,
        [data-baseweb="input"] > div:hover,
        [data-baseweb="textarea"] > div:hover {
            border-color: rgba(255, 255, 255, 0.18) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
        }

        [data-baseweb="select"]:focus-within > div,
        [data-baseweb="input"]:focus-within > div,
        [data-baseweb="textarea"]:focus-within > div {
            border-color: rgba(255, 255, 255, 0.25) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
        }

        /* Chevron icon */
        [data-baseweb="select"] svg {
            color: var(--text-secondary) !important;
            opacity: 0.5 !important;
            transition: opacity 0.2s ease, transform 0.2s ease !important;
        }
        [data-baseweb="select"]:focus-within svg {
            opacity: 0.9 !important;
            color: white !important;
        }

        /* Label above selectbox */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stSelectbox"] > label {
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            margin-bottom: 6px !important;
            display: block !important;
        }

        /* ===== DROPDOWN POPOVER — premium dark panel ===== */
        /* Outermost popover container — style as the clean glass panel */
        [data-baseweb="popover"] {
            background: #000000 !important; /* Completely black background */
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important; /* Matches input's 16px radius perfectly */
            box-shadow: 0 20px 48px rgba(0, 0, 0, 0.9) !important;
            margin-top: 8px !important; /* Creates a clean 8px gap below the input field */
            overflow: hidden !important;
        }

        /* Clear Streamlit's inner dropdown styles to prevent double borders / width mismatch */
        [data-testid="stSelectboxVirtualDropdown"] {
            background: #000000 !important;
            border: none !important;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-baseweb="popover"] *,
        [data-testid="stSelectboxVirtualDropdown"] * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Set inner list container and listbox to completely solid black background */
        [data-baseweb="popover"] ul,
        [data-testid="stSelectboxVirtualDropdown"] ul,
        [data-baseweb="popover"] [role="listbox"],
        [data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
        [data-baseweb="popover"] [role="listbox"] > div {
            background-color: #000000 !important;
            padding: 8px 12px 8px 8px !important;
        }

        /* Black & White Scrollbar overrides inside the dropdown popover */
        [data-baseweb="popover"] ::-webkit-scrollbar {
            width: 6px !important;
            height: 6px !important;
        }
        [data-baseweb="popover"] ::-webkit-scrollbar-track {
            background: #000000 !important;
        }
        [data-baseweb="popover"] ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.25) !important;
            border-radius: 3px !important;
        }
        [data-baseweb="popover"] ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.45) !important;
        }

        [data-baseweb="popover"] [role="option"],
        [data-testid="stSelectboxVirtualDropdown"] [role="option"],
        [data-baseweb="popover"] li,
        [data-testid="stSelectboxVirtualDropdown"] li,
        [data-baseweb="menu-item"] {
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: rgba(255, 255, 255, 0.55) !important; /* Muted white for unselected */
            background-color: transparent !important;
            width: calc(100% - 0px) !important;
            margin: 2px 0 !important;
            box-sizing: border-box !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Clear any nested background/borders/shadows inside the option elements to prevent dynamic double highlights */
        [data-baseweb="popover"] [role="option"] *,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"] *,
        [data-baseweb="popover"] li *,
        [data-testid="stSelectboxVirtualDropdown"] li * {
            background-color: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
        }

        /* Hover state: highlight option with soft neutral off-white glass */
        [data-baseweb="popover"] [role="option"]:hover,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
        [data-baseweb="popover"] li:hover,
        [data-testid="stSelectboxVirtualDropdown"] li:hover {
            background-color: rgba(255, 255, 255, 0.06) !important;
            border-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
        }

        /* Selected state (non-hover): bold white text and white checkmark, subtle transparent highlight */
        [data-baseweb="popover"] [role="option"][aria-selected="true"],
        [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
        [data-baseweb="popover"] li[aria-selected="true"],
        [data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border-color: transparent !important;
            color: white !important;
            font-weight: 700 !important;
        }

        /* Hovered selected state: gets slightly stronger white highlight */
        [data-baseweb="popover"] [role="option"][aria-selected="true"]:hover,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"]:hover,
        [data-baseweb="popover"] li[aria-selected="true"]:hover,
        [data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"]:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
        }

        /* Selected item checkmark — white literal checkmark */
        [data-baseweb="popover"] [role="option"][aria-selected="true"]::after,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"]::after {
            content: "✓" !important;
            font-size: 0.9rem !important;
            color: white !important;
            margin-left: auto !important;
            display: inline-block !important;
            font-weight: 700 !important;
            box-shadow: none !important;
        }

        [data-baseweb="popover"] [role="option"][aria-selected="true"]:hover::after,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"]:hover::after {
            color: white !important;
        }

        /* ===== STREAMLIT NOTIFICATION / INFO BOX WELL ===== */
        div[data-testid="stNotification"], .stAlert {
            background-color: var(--glass-bg) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        }
        div[data-testid="stNotification"] *, .stAlert * {
            color: var(--text-primary) !important;
        }

        /* ===== UPLOADED FILE — premium theme-aligned row ===== */
        div[data-testid="stUploadedFile"] {
            background: rgba(155, 81, 224, 0.06) !important;
            border: 1px solid rgba(155, 81, 224, 0.20) !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin-top: 8px !important;
        }
        div[data-testid="stUploadedFile"] * {
            background: transparent !important;
            background-color: transparent !important;
            border-color: transparent !important;
        }
        div[data-testid="stUploadedFile"] span,
        div[data-testid="stUploadedFile"] p,
        div[data-testid="stUploadedFile"] div {
            color: rgba(244, 246, 251, 0.85) !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
        }
        div[data-testid="stUploadedFile"] svg {
            color: var(--amethyst) !important;
            fill: var(--amethyst) !important;
        }

        /* ===== FILE UPLOADER — collapse when file loaded ===== */
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploaderDropzone"]::before,
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploaderDropzone"]::after,
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploadDropzone"]::before,
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploadDropzone"]::after {
            display: none !important;
        }
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploaderDropzone"] button,
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploadDropzone"] button {
            display: none !important;
        }
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneInstructions"],
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploadDropzone"] [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploaderDropzone"],
        div.stApp div[data-testid="stFileUploader"]:has([data-testid="stUploadedFile"]) section[data-testid="stFileUploadDropzone"] {
            padding: 12px 16px !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            height: auto !important;
            min-height: unset !important;
        }

        /* ===== EXPANDERS — glass card ===== */
        [data-testid="stExpander"] {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
            margin-bottom: 8px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }
        [data-testid="stExpander"]:hover {
            border-color: rgba(155,81,224,0.3) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        }
        .streamlit-expanderHeader,
        [data-testid="stExpander"] summary {
            background: transparent !important;
            border: none !important;
            padding: 16px 20px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            cursor: pointer !important;
        }
        [data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid var(--glass-border) !important;
        }

        /* ===== DATAFRAME — dark glass table ===== */
        [data-testid="stDataFrame"],
        [data-testid="stDataFrameResizable"] {
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
            border: 1px solid var(--glass-border) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
        }
        [data-testid="stDataFrame"] thead th,
        [data-testid="stDataFrame"] th {
            background: rgba(155,81,224,0.12) !important;
            color: white !important;
            font-size: 0.65rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            border-bottom: 1px solid rgba(155,81,224,0.2) !important;
            padding: 12px 16px !important;
        }
        [data-testid="stDataFrame"] tbody tr {
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        }
        [data-testid="stDataFrame"] tbody tr:hover { background: rgba(155,81,224,0.06) !important; }
        [data-testid="stDataFrame"] tbody tr:nth-child(even) { background: transparent !important; }
        [data-testid="stDataFrame"] tbody td {
            color: rgba(255,255,255,0.8) !important;
            font-size: 0.875rem !important;
            padding: 10px 16px !important;
            border: none !important;
        }

        /* ===== PROGRESS BARS — amethyst gradient ===== */
        [data-testid="stProgressBar"] > div {
            background: rgba(255,255,255,0.08) !important;
            border-radius: 6px !important;
            height: 6px !important;
            overflow: hidden !important;
        }
        [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, var(--amethyst) 0%, #A56DFF 100%) !important;
            border-radius: 6px !important;
            box-shadow: 0 0 8px var(--amethyst-glow) !important;
        }

        /* ===== MENTOR CARD ===== */
        .mentor-card {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-left: 3px solid var(--accent-blue) !important;
            border-radius: var(--radius-md) !important;
            padding: 20px 24px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3), -2px 0 12px rgba(85,224,255,0.08) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .mentor-card::before {
            content: '' !important;
            position: absolute !important; top: 0 !important; left: 0 !important; right: 0 !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(85,224,255,0.2), transparent) !important;
        }
        .mentor-card:hover {
            transform: translateX(4px) !important;
            border-left-color: var(--amethyst) !important;
            box-shadow: 0 8px 30px rgba(0,0,0,0.4), -3px 0 16px rgba(155,81,224,0.15) !important;
        }

        /* ===== COMPARABLE FILM CARDS ===== */
        .comp-film-card {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
            padding: 14px 18px !important;
            text-align: center !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            transition: all 0.25s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin-bottom: 8px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .comp-film-card::before {
            content: '' !important;
            position: absolute !important; top: 0 !important; left: 0 !important; right: 0 !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, var(--amethyst-glow), transparent) !important;
        }

        /* ===== SCORE BADGES ===== */
        .score-badge {
            display: inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
        }
        .score-high { background: rgba(0,200,83,0.15); color: var(--emerald); border: 1px solid rgba(0,200,83,0.25); }
        .score-mid  { background: rgba(255,112,67,0.15); color: var(--coral); border: 1px solid rgba(255,112,67,0.25); }
        .score-low  { background: rgba(255,51,102,0.15); color: var(--accent-rose); border: 1px solid rgba(255,51,102,0.25); }

        /* ===== TOOLTIP CARD ===== */
        .tooltip-card {
            background: var(--glass-bg); backdrop-filter: blur(8px);
            border: 1px solid var(--glass-border); border-left: 2px solid var(--amethyst);
            border-radius: var(--radius-sm); padding: 14px 18px;
            font-size: 0.88rem; color: rgba(244,246,251,0.85);
            margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); line-height: 1.6;
        }

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--glass-border) !important;
        }
        [data-testid="stSidebar"] .stMarkdown { color: var(--text-primary) !important; }

        /* ===== DIVIDER ===== */
        hr { border-color: var(--glass-border) !important; opacity: 0.6 !important; }

        /* ===== BOOTSTRAP ICONS ===== */
        .bi { font-size: 1.1em; vertical-align: middle; margin-right: 8px; }
        .icon-pass { color: var(--emerald); }
        .icon-fail { color: var(--accent-rose); }

        /* ===== ELEMENT FADE-IN STAGGER ===== */
        .element-container { animation: fadeInUp 0.45s cubic-bezier(0.23, 1, 0.32, 1) both; }
        .element-container:nth-child(2) { animation-delay: 0.05s; }
        .element-container:nth-child(3) { animation-delay: 0.10s; }
        .element-container:nth-child(4) { animation-delay: 0.15s; }
        .element-container:nth-child(5) { animation-delay: 0.20s; }
        .element-container:nth-child(6) { animation-delay: 0.25s; }

        /* ===== DOWNLOAD BUTTONS ===== */
        .stDownloadButton > button {
            background: var(--glass-bg) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 20px !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            padding: 0.65rem 1.5rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        }

        .stDownloadButton > button:hover {
            border-color: var(--amethyst) !important;
            box-shadow: 0 0 15px var(--amethyst-glow) !important;
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

        @keyframes trustPulse {
            0%, 100% { box-shadow: 0 0 6px var(--emerald-glow); }
            50% { box-shadow: 0 0 12px var(--emerald-glow), 0 0 20px var(--emerald-glow); }
        }

        .trust-bar .trust-dot,
        .trust-bar [class*="trust-dot"],
        span[style*="trust-dot"] {
            animation: trustPulse 2s ease-in-out infinite !important;
        }

        /* ===== BRAND GRADIENT (loading screen) ===== */
        .brand-pulse-gradient {
            background: linear-gradient(135deg, #A56DFF 0%, var(--amethyst) 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            display: inline-block !important;
            filter: drop-shadow(0 0 15px var(--amethyst-glow)) !important;
        }

        /* ===== CUSTOM GLASS CARDS & WELLS — Tactile Glass Template ===== */
        .glass-card {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            -webkit-backdrop-filter: blur(var(--glass-blur)) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
        }

        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
        }

        /* Hardware shimmer overlay — matches template .hardware-metric::after */
        .hardware-metric {
            position: relative !important;
            overflow: hidden !important;
        }

        .hardware-metric::after {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%) !important;
            pointer-events: none !important;
            border-radius: inherit !important;
        }

        /* Score card: centered, with inset well — matches template .score-card */
        .score-card {
            padding: 32px !important;
            text-align: center !important;
        }

        /* Metric tile: left-aligned, compact — matches template .metric-tile */
        .metric-tile {
            padding: 20px !important;
            text-align: left !important;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin-top: 4px !important;
            line-height: 1.1 !important;
        }

        /* Engagement Index big number */
        .engagement-index {
            font-family: 'Outfit', sans-serif !important;
            font-size: 4.5rem !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            margin: 16px 0 !important;
            color: var(--amethyst) !important;
            text-shadow: 0 0 15px var(--amethyst-glow) !important;
        }

        .well {
            background: rgba(0, 0, 0, 0.2) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
        }

        /* ===== VERTICAL CONTAINER BORDER WRAPPER — Tactile Glass ===== */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[class*="stVerticalBlockBorderWrapper"] {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            -webkit-backdrop-filter: blur(var(--glass-blur)) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-lg) !important;
            padding: 40px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }

        /* Smaller padding for column-nested border wrappers (like export cards) */
        [data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="column"] div[class*="stVerticalBlockBorderWrapper"] {
            padding: 24px 20px !important;
        }



        /* Shimmer overlay */
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

        /* ===== CUSTOM METRIC CARDS — legacy alias kept for compatibility ===== */
        .custom-metric-card {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
            padding: 20px !important;
            text-align: left !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            backdrop-filter: blur(var(--glass-blur)) !important;
            -webkit-backdrop-filter: blur(var(--glass-blur)) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
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
    </style>
    """
    
    st.markdown(apply_theme_to_css(css), unsafe_allow_html=True)
