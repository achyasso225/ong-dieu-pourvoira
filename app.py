from datetime import datetime
from io import BytesIO
import math
import re
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import base64

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Application de Gestion",
    page_icon="logo.png",
    layout="wide",
)

# --- INJECTION CSS DESIGN MODERNE & MOBILE-FRIENDLY ---
st.markdown(
    """
    <style>
    /* Styles Globaux */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Bouton d'ouverture du menu en haut (Hamburger) */
    button[aria-label*="sidebar"], 
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] {
        background-color: #1a1f2c !important;
        border: 2px solid #28a745 !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }
    button[aria-label*="sidebar"] svg, 
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #28a745 !important;
        color: #28a745 !important;
    }

    /* En-tête personnalisé à l'intérieur du menu latéral */
    .sidebar-menu-title {
        background-color: #1a1f2c;
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        color: #28a745;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    /* Bannière d'en-tête moderne */
    .hero-header {
        background: linear-gradient(135deg, #1e7e34 0%, #0b4d1d 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,128,0,0.2);
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-header h1 {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.5px;
    }
    .hero-header p {
        font-size: 13px !important;
        color: #e2f0d9 !important;
        margin: 0 !important;
    }
    .hero-contact {
        font-size: 11px !important;
        color: #b2d8b2 !important;
        margin-top: 10px !important;
    }

    /* Cartes de statistiques (KPI Cards) */
    .kpi-card {
        background-color: #1a1f2c;
        border-radius: 12px;
        padding: 16px;
        border-left: 5px solid #28a745;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 12px;
        color: #8e9baf;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 4px;
    }

    /* Styling de la Sidebar */
    div[data-testid="stSidebar"] {
        background-color: #131722 !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    .nav-btn-active button {
        background: linear-gradient(90deg, #28a745 0%, #1e7e34 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(40,167,69,0.3) !important;
        border: none !important;
    }
    
    .nav-btn-inactive button {
        background-color: #1a1f2c !important;
        color: #c5d1e0 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .nav-btn-inactive button:hover {
        background-color: #252c3d !important;
        color: white !important;
        border-color: #28a745 !important;
    }

    /* Boîtes d'informations */
    .info-card {
        background: rgba(255, 127, 0, 0.08);
        border: 1px solid rgba(255, 127, 0, 0.3);
        border-left: 4px solid #ff7f00;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        color: #f1f1f1;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SCRIPT JAVASCRIPT POUR FERMER LA SIDEBAR AUTOMATIQUEMENT SUR MOBILE ---
st.markdown(
    """
    <script>
    const observer = new MutationObserver(() => {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            const buttons = sidebar.querySelectorAll('button');
            buttons.forEach(btn => {
                if (!btn.getAttribute('data-auto-close')) {
                    btn.setAttribute('data-auto-close', 'true');
                    btn.addEventListener('click', () => {
                        if (window.innerWidth <= 768) {
                            setTimeout(() => {
                                const mainOverlay = window.parent.document.querySelector('.main');
                                if (mainOverlay) mainOverlay.click();
                            }, 100);
                        }
                    });
                }
            });
        }
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
""",
    unsafe_allow_html=True,
)

# --- BANNIÈRE D'EN-TÊTE ---
st.markdown(
    """
    <div class="hero-header">
        <h1>ONG DIEU POURVOIRA</h1>
        <p><strong>Ensemble aidons les enfants atteints de Paralysie cérébrale</strong></p>
        <div class="hero-contact">
            📞 +225 77 71 04 41 8 / 05 86 99 73 27 &nbsp;|&nbsp; ✉️ dieupourvoira187@gmail.com &nbsp;|&nbsp; 📍 08 BP 2945 ABIDJAN 08
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


# --- CONNEXION ET CACHE GOOGLE SHEETS (Anti-Quota 429) ---
@st.cache_resource
def init_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  return gspread.authorize(creds)


@st.cache_data(ttl=30)
def charger_donnees_depuis_sheets():
  client = init_connection()
  spreadsheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira")

  # 1. Membres
  sheet_membres = spreadsheet.sheet1
  data = sheet_membres.get_all_records(head=9)

  # 2. Utilisateurs
  try:
    df_users = pd.DataFrame(
        spreadsheet.worksheet
