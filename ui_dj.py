import streamlit as st

def aplicar_estilo_dj():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Press+Start+2P&display=swap');

    .stApp {
        background-color: #070812;
        background-image: 
            radial-gradient(circle at 50% 0%, #240b36 0%, #070812 75%),
            linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 127, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 28px 28px, 28px 28px;
        color: #f1f5f9;
        font-family: 'Orbitron', sans-serif;
    }

    header[data-testid="stHeader"] {
        background-color: #070812 !important;
    }

    /* Textos generales y captions legibles */
    .stApp p, .stApp label, [data-testid="stCaptionContainer"] p {
        color: #e2e8f0 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0b0d1f;
        border-right: 2px solid #ff007f;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.25);
    }

    /* Enlaces del menú lateral en verde neón brillante */
    [data-testid="stSidebarNav"] a span {
        color: #39ff14 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-shadow: 0 0 8px rgba(57, 255, 20, 0.7);
    }
    [data-testid="stSidebarNav"] a {
        border: 1px solid rgba(57, 255, 20, 0.25);
        border-radius: 8px;
        margin-bottom: 6px;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: rgba(57, 255, 20, 0.18) !important;
        border: 1.5px solid #39ff14 !important;
        box-shadow: 0 0 12px rgba(57, 255, 20, 0.5);
    }

    h1 {
        font-family: 'Press Start 2P', cursive !important;
        color: #00f0ff !important;
        text-shadow: 0 0 12px #00f0ff, 3px 3px 0px #ff007f;
        font-size: 1.55rem !important;
        line-height: 1.5 !important;
        text-align: center;
    }

    h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #ff007f !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #12142b, #090a17);
        border: 2px solid #00f0ff;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.25);
        text-align: center;
    }

    /* Etiquetas superiores de las tarjetas métricas (TEMPO, BASS DROPS, etc.) */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] label,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        font-family: 'Orbitron', sans-serif !important;
        color: #a5f3fc !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        opacity: 1 !important;
        justify-content: center !important;
        text-shadow: 0 0 6px rgba(0, 240, 255, 0.45);
    }

    [data-testid="stMetricValue"] {
        font-family: 'Press Start 2P', cursive !important;
        color: #39ff14 !important;
        font-size: 1.25rem !important;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.6);
    }

    .stButton > button {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        background: linear-gradient(90deg, #ff007f, #7000ff) !important;
        color: #ffffff !important;
        border: 2px solid #00f0ff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 12px rgba(255, 0, 127, 0.5);
        width: 100%;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px #00f0ff, 0 0 28px #ff007f;
    }

    .dj-banner {
        background: linear-gradient(90deg, rgba(255,0,127,0.2), rgba(0,240,255,0.2));
        border: 1px solid #ff007f;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 0.68rem;
        color: #facc15;
        margin-bottom: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

def banner_dj(texto="NEON DJ BOOTH • MULTIMODAL IOT CONSOLE"):
    st.markdown(f'<div class="dj-banner">🎧 {texto} 🎛️</div>', unsafe_allow_html=True)
