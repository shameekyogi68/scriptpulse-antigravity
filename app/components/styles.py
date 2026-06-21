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

        html, body {
            background: var(--bg-primary) !important;
        }

        .stApp, select, input, textarea, button, span, p, div, label, li, a {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        .stApp {
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            padding-top: 0rem !important;
            margin-top: -3rem !important; /* Pull content into the header area */
            padding-bottom: 4rem !important;
            max-width: 1360px !important;
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
        header {visibility: hidden;}

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
            padding: 3rem 1rem 1.5rem;
            margin-top: 6rem;
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
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: rgba(0, 0, 0, 0.2) !important;
            border-radius: 14px !important;
            padding: 6px !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            margin-bottom: 32px !important;
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

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploadDropzone"] {
            background: rgba(0, 0, 0, 0.2) !important;
            box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
            border: 2px dashed rgba(255, 255, 255, 0.08) !important;
            border-radius: var(--radius-md) !important;
            padding: 48px 30px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stFileUploaderDropzone"]:hover,
        [data-testid="stFileUploadDropzone"]:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            background: rgba(255, 255, 255, 0.01) !important;
        }
        [data-testid="stFileUploaderDropzone"] svg,
        [data-testid="stFileUploadDropzone"] svg {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInput"],
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploadDropzoneInput"],
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploadDropzoneInput"],
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInput"],
        [data-testid="stFileUploaderDropzone"] div[class*="DropzoneInput"],
        [data-testid="stFileUploadDropzone"] div[class*="DropzoneInput"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0 !important;
        }
        /* Hide standard help texts and labels inside input wrapper */
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInput"] > *,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploadDropzoneInput"] > *,
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploadDropzoneInput"] > *,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInput"] > *,
        [data-testid="stFileUploaderDropzone"] div[class*="DropzoneInput"] > *,
        [data-testid="stFileUploadDropzone"] div[class*="DropzoneInput"] > * {
            display: none !important;
        }
        /* Show only the button */
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInput"] > button,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploadDropzoneInput"] > button,
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploadDropzoneInput"] > button,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInput"] > button,
        [data-testid="stFileUploaderDropzone"] div[class*="DropzoneInput"] > button,
        [data-testid="stFileUploadDropzone"] div[class*="DropzoneInput"] > button {
            display: inline-flex !important;
        }
        /* Inject custom cloud icon from Tabler Icons using the webfont */
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInput"]::before,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploadDropzoneInput"]::before,
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploadDropzoneInput"]::before,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInput"]::before,
        [data-testid="stFileUploaderDropzone"] div[class*="DropzoneInput"]::before,
        [data-testid="stFileUploadDropzone"] div[class*="DropzoneInput"]::before {
            order: 1 !important;
            content: "\ea75" !important; /* ti-cloud-upload */
            font-family: 'tabler-icons' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 3.5rem !important;
            color: var(--text-secondary) !important;
            opacity: 0.4 !important;
            line-height: 1 !important;
            margin-bottom: 12px !important;
            display: inline-block !important;
        }
        /* Inject custom instructions prompt */
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInput"]::after,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploadDropzoneInput"]::after,
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploadDropzoneInput"]::after,
        [data-testid="stFileUploadDropzone"] div[data-testid="stFileUploaderDropzoneInput"]::after,
        [data-testid="stFileUploaderDropzone"] div[class*="DropzoneInput"]::after,
        [data-testid="stFileUploadDropzone"] div[class*="DropzoneInput"]::after {
            order: 2 !important;
            content: "Drop your screenplay here (PDF, TXT, or FDX)" !important;
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            margin-bottom: 4px !important;
        }
        [data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] {
            order: 3 !important;
            background: linear-gradient(135deg, var(--accent-primary) 0%, #7B3FE4 100%) !important;
            padding: 12px 32px !important;
            border-radius: 40px !important;
            box-shadow: 0 4px 15px rgba(155, 81, 224, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            border: none !important;
            cursor: pointer !important;
            text-transform: uppercase !important;
            margin-top: 12px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] * {
            display: none !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        [data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]::after {
            content: "SELECT FILE" !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.05em !important;
            color: white !important;
            display: inline-block !important;
        }
        [data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(155, 81, 224, 0.6) !important;
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
        
        [data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover, [data-baseweb="textarea"] > div:hover,
        [data-baseweb="select"]:focus-within > div, [data-baseweb="input"]:focus-within > div, [data-baseweb="textarea"]:focus-within > div {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 15px rgba(155, 81, 224, 0.25), inset 0 4px 12px rgba(0, 0, 0, 0.6) !important;
        }
        
        div[data-testid="stSelectbox"] label {
            font-size: 0.65rem !important;
            font-weight: 700 !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            margin-bottom: 8px !important;
        }

        /* Hide custom uploader dropzone elements when a file is uploaded */
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzone"]::before,
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzone"]::after,
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploadDropzone"]::before,
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploadDropzone"]::after {
            display: none !important;
        }
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzone"] button,
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploadDropzone"] button {
            display: none !important;
        }
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploader"]:has(div[data-testid="stUploadedFile"]) [data-testid="stFileUploadDropzone"] {
            padding: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: rgba(0,0,0,0.1) !important;
            box-shadow: none !important;
        }
        
        [data-baseweb="popover"],
        [data-testid="stSelectboxVirtualDropdown"] {
            background: rgba(22, 20, 36, 0.98) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(155, 81, 224, 0.3) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(155, 81, 224, 0.15) !important;
        }

        [data-baseweb="popover"] *,
        [data-testid="stSelectboxVirtualDropdown"] * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        [data-baseweb="popover"] ul,
        [data-testid="stSelectboxVirtualDropdown"] ul {
            background-color: transparent !important;
            padding: 8px 0 !important;
        }

        [data-baseweb="popover"] [role="option"],
        [data-testid="stSelectboxVirtualDropdown"] [role="option"],
        [data-baseweb="popover"] li,
        [data-testid="stSelectboxVirtualDropdown"] li,
        [data-baseweb="menu-item"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            color: rgba(255, 255, 255, 0.85) !important;
            background-color: transparent !important;
            
            /* Absolute positioning sizing overrides with calc to support margins in virtual list */
            width: calc(100% - 16px) !important;
            margin: 2px 8px !important;
            box-sizing: border-box !important;
            
            /* Spacing gaps using transparent borders and padding-box clipping */
            border-top: 3px solid transparent !important;
            border-bottom: 3px solid transparent !important;
            border-left: 3px solid transparent !important;
            border-right: 3px solid transparent !important;
            background-clip: padding-box !important;
            border-radius: 8px !important;
            
            padding: 8px 16px !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-baseweb="popover"] [role="option"]:hover,
        [data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
        [data-baseweb="popover"] li:hover,
        [data-testid="stSelectboxVirtualDropdown"] li:hover,
        [data-baseweb="menu-item"]:hover {
            background-color: rgba(155, 81, 224, 0.15) !important;
            color: #FFFFFF !important;
            border-left: 3px solid var(--accent-primary) !important;
        }

        [data-baseweb="popover"] [role="option"][aria-selected="true"],
        [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
        [data-baseweb="popover"] li[aria-selected="true"],
        [data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"],
        [data-baseweb="menu-item"][aria-selected="true"] {
            background-color: rgba(155, 81, 224, 0.22) !important;
            color: #FFFFFF !important;
            border-left: 3px solid var(--accent-primary) !important;
            font-weight: 600 !important;
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

        /* Top highlight bar (matches template section highlight lines) */
        div[data-testid="stVerticalBlockBorderWrapper"]::before,
        div[class*="stVerticalBlockBorderWrapper"]::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, rgba(155, 81, 224, 0.5), rgba(165, 109, 255, 0.3), transparent) !important;
            pointer-events: none !important;
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
