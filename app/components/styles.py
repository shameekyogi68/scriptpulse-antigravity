import streamlit as st

def apply_custom_styles():
    """Applies the 'Premium Instrument' visual language via CSS."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
        /* Modern Typography */
        :root {
            --bg-glass: rgba(255, 255, 255, 0.7);
            --border-glass: rgba(255, 255, 255, 0.3);
            --text-main: #1a1a1a;
            --accent: #5d5dff;
        }

        .stApp {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, .stTitle {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        /* Hide Streamlit Chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Glassmorphism Container */
        .block-container {
            padding-top: 3rem;
            padding-bottom: 5rem;
            max-width: 1000px;
        }

        /* Premium Signal Boxes */
        .signal-box {
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            background: var(--bg-glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-glass);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            transition: transform 0.2s ease;
        }
        
        .signal-box:hover {
            transform: translateY(-2px);
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background: var(--bg-glass);
            backdrop-filter: blur(8px);
            padding: 20px;
            border-radius: 16px;
            border: 1px solid var(--border-glass);
            box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.05);
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent !important;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .element-container {
            animation: fadeIn 0.5s ease-out;
        }

        /* Bootstrap Icon styling */
        .bi { font-size: 1.1em; vertical-align: middle; margin-right: 8px; }
        .icon-pass { color: #2ecc71; }
        .icon-fail { color: #e74c3c; }
    </style>
    """, unsafe_allow_html=True)
