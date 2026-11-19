import base64
from datetime import datetime
from io import BytesIO
import math
import os
import re
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Application de Gestion",
    page_icon="logo.png",
    layout="wide",
)

# --- CHARGEMENT DES IMAGES EN BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        mime = "jpeg" if ext in ["jpg", "jpeg"] else "png"
        with open(path, "rb") as f:
            return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"
    return None

def esc_html(val):
    return str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

banner_path = "banner_connection.png" if os.path.exists("banner_connection.png") else "banner_connexion.png"
banner_b64 = get_image_base64(banner_path)
logo_b64 = get_image_base64("logo.png")

# Image appliquée à 100% en fond d'écran du bloc de connexion
bg_card_style = f"background-image: url('{banner_b64}'); background-size: cover; background-repeat: no-repeat; background-position: center;" if banner_b64 else "background-color: #1a1a1a;"

# --- INJECTION CSS STRICT - THEME SOMBRE, ERGONOMIE AMÉLIORÉE + RESPONSIVE ---
st.markdown(
    f"""
    <style>
    /* ===== FOND NOIR GLOBAL ===== */
    .stApp {{
        background-color: #121212 !important;
        color: #e0e0e0 !important;
    }}

    /* ===== INPUTS DE SAISIE SOMBRES ===== */
    div[data-baseweb="input"], div[data-baseweb="select"] {{
        background-color: #1e1e1e !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {{
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: 500 !important;
    }}
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{
        border-color: #2e8b42 !important;
        box-shadow: 0 0 0 1px #2e8b42 !important;
    }}

    label[data-testid="stWidgetLabel"], .stMarkdown p, h1, h2, h3, h4, h5, h6 {{
        color: #f0f0f0 !important;
    }}

    /* ===== BOUTONS VERTS PRINCIPAUX ===== */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{
        background-color: #2e8b42 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 3px 8px rgba(46,139,66,0.3) !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }}
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
        background-color: #236f33 !important;
        color: #ffffff !important;
    }}

    /* ===== DATAFRAMES GLOBAUX (thème sombre harmonisé) ===== */
    div[data-testid="stDataFrame"] {{
        background-color: #1e1e1e !important;
        border: 1px solid #2d2d2d !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}
    .stDataFrame thead th {{
        background: linear-gradient(135deg, #1b4332, #2e8b42) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.3px !important;
        border-bottom: 2px solid #4ade80 !important;
        padding: 10px 8px !important;
    }}
    .stDataFrame tbody tr {{
        border-bottom: 1px solid #2a2a2a !important;
        transition: background-color 0.15s !important;
    }}
    .stDataFrame tbody tr:hover {{
        background-color: #27272a !important;
    }}
    .stDataFrame tbody td {{
        color: #e0e0e0 !important;
        font-size: 12px !important;
        padding: 8px !important;
        background-color: #1e1e1e !important;
        border-bottom: 1px solid #2a2a2a !important;
    }}

    /* Tableau de bord metrics */
    div[data-testid="stMetricValue"] {{
        font-size: 2em !important;
    }}

    /* ===== CARTE DE CONNEXION AVEC FOND IMAGE COMPLET ===== */
    .prop3-login-card {{
        width: 480px;
        max-width: 95%;
        margin: 30px auto;
        border-radius: 20px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.8);
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.25);
        {bg_card_style}
        padding: 35px 25px 25px 25px;
        position: relative;
    }}

    /* Voile de lisibilité très doux sur l'image */
    .prop3-login-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.45);
        z-index: 0;
    }}

    .prop3-login-inner {{
        position: relative;
        z-index: 1;
    }}

    /* Ajustement des champs de login pour laisser voir l'image */
    .prop3-login-inner div[data-baseweb="input"] {{
        background-color: rgba(18, 18, 18, 0.75) !important;
        backdrop-filter: blur(4px);
    }}

    .prop3-title-text {{
        text-align: center;
        font-weight: 900;
        color: #ffffff;
        font-size: 22px;
        margin-bottom: 20px;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.9);
    }}

    .prop3-footer-coords {{
        text-align: center;
        padding-top: 15px;
        margin-top: 20px;
        border-top: 1px dashed rgba(255, 255, 255, 0.4);
        font-size: 12px;
        color: #ffffff;
        line-height: 20px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }}

    /* ===== BARRE LATÉRALE ===== */
    button[aria-label*="sidebar"], [data-testid="stSidebarCollapseButton"] button {{
        background-color: #1e1e1e !important;
        border: 2px solid #2e8b42 !important;
        border-radius: 8px !important;
    }}

    .sidebar-menu-title {{
        background-color: #1e1e1e;
        border: 1px solid #2e8b42;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        color: #4ade80;
        font-weight: bold;
    }}

    .hero-header {{
        background: linear-gradient(135deg, #1b4332 0%, #2e8b42 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}

    div[data-testid="stSidebar"] {{
        background-color: #18181b !important;
    }}

    .nav-btn-active button {{
        background-color: #2e8b42 !important;
        color: white !important;
    }}
    .nav-btn-inactive button {{
        background-color: #27272a !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
    }}

    [data-testid="stContainer"] {{
        background-color: #1a1a1a !important;
        border: 1px solid #2d2d2d !important;
        border-radius: 10px;
        padding: 15px;
    }}

    /* ===== CARTE PROFIL MEMBRE ===== */
    .profile-header {{
        background: linear-gradient(135deg, #1b4332 0%, #2e8b42 50%, #4ade80 100%);
        border-radius: 16px 16px 0 0;
        padding: 25px 20px;
        color: white;
        text-align: center;
        position: relative;
    }}
    .profile-header h2 {{
        margin: 0;
        font-size: 22px;
        font-weight: 800;
        color: #ffffff !important;
    }}
    .profile-header p {{
        margin: 5px 0 0 0;
        font-size: 14px;
        color: #e2e8f0 !important;
    }}
    .profile-body {{
        background-color: #1e1e1e;
        border-radius: 0 0 16px 16px;
        padding: 20px;
        border: 1px solid #333;
        border-top: none;
    }}
    .profile-field {{
        display: flex;
        padding: 8px 0;
        border-bottom: 1px solid #2a2a2a;
    }}
    .profile-field:last-child {{
        border-bottom: none;
    }}
    .profile-label {{
        min-width: 200px;
        font-weight: bold;
        color: #4ade80;
        font-size: 13px;
    }}
    .profile-value {{
        flex: 1;
        color: #f0f0f0;
        font-size: 14px;
    }}
    .profile-badge {{
        display: inline-block;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }}
    .badge-ok {{ background-color: #2e8b42; color: white; }}
    .badge-attente {{ background-color: #eab308; color: #121212; }}
    .badge-interieur {{ background-color: #6366f1; color: white; }}

    /* ===== TABLEAU MEMBRES (Liste & Répertoire) ===== */
    .rep-table-wrapper {{
        width: 100%;
        overflow-x: auto;
        border-radius: 8px;
        border: 1px solid #2d2d2d;
    }}
    .rep-table-header {{
        display: flex;
        background: linear-gradient(135deg, #1b4332, #2e8b42);
        color: white;
        padding: 12px 8px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        border-bottom: 2px solid #4ade80;
    }}
    .rep-table-row {{
        display: flex;
        border-bottom: 1px solid #2a2a2a;
        transition: background-color 0.15s;
    }}
    .rep-table-row:hover {{
        background-color: #27272a !important;
    }}
    .rep-cell {{
        padding: 10px 8px;
        color: #e0e0e0;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: flex;
        align-items: center;
    }}
    .matricule-badge {{
        background-color: #27272a;
        color: #4ade80;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
    }}
    .status-ok {{ background-color: #2e8b42; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }}
    .status-wait {{ background-color: #eab308; color: #121212; padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }}
    .sexe-m {{ background-color: #3b82f6; color: white; padding: 3px 8px; border-radius: 50%; font-size: 10px; font-weight: bold; display: inline-flex; justify-content: center; min-width: 22px; }}
    .sexe-f {{ background-color: #ec4899; color: white; padding: 3px 8px; border-radius: 50%; font-size: 10px; font-weight: bold; display: inline-flex; justify-content: center; min-width: 22px; }}

    .c-action {{ width: 58px; min-width: 58px; max-width: 58px; justify-content: center !important; flex-shrink: 0; }}
    .c-membre {{ width: 8.5%; min-width: 75px; flex-shrink: 0; }}
    .c-enfant {{ width: 16%; min-width: 120px; }}
    .c-date {{ width: 9%; min-width: 60px; flex-shrink: 0; }}
    .c-sexe {{ width: 4.5%; min-width: 35px; justify-content: center !important; flex-shrink: 0; }}
    .c-ville {{ width: 7%; min-width: 50px; flex-shrink: 0; }}
    .c-parent {{ width: 14%; min-width: 90px; }}
    .c-tel {{ width: 8%; min-width: 65px; flex-shrink: 0; }}
    .c-adh {{ width: 6%; min-width: 45px; flex-shrink: 0; }}
    .c-date-heure {{ width: 11%; min-width: 85px; }}
    .c-auteur {{ width: 9%; min-width: 70px; }}
    .c-default {{ width: 8%; min-width: 55px; }}

    .pagination-container {{ display: flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 0; }}
    .pagination-info {{ color: #e0e0e0; font-size: 13px; font-weight: bold; padding: 0 12px; }}

    /* ===== RESPONSIVE MOBILE / TABLETTE ===== */
    @media screen and (max-width: 1024px) {{
        .hero-header {{ padding: 15px; }}
        .hero-header h1 {{ font-size: 20px !important; }}
        .hero-header p {{ font-size: 11px !important; }}
        .profile-label {{ min-width: 160px; font-size: 12px; }}
        .profile-value {{ font-size: 13px; }}
    }}

    @media screen and (max-width: 768px) {{
        .stApp {{ font-size: 14px !important; }}
        .hero-header {{ padding: 12px; border-radius: 12px; }}
        .hero-header h1 {{ font-size: 18px !important; }}
        .hero-header p {{ font-size: 10px !important; }}
        .hero-header div {{ font-size: 9px !important; }}

        .rep-table-header, .rep-table-row {{ font-size: 9px; }}
        .rep-cell {{ padding: 6px 4px; font-size: 10px; }}
        .c-date-heure, .c-auteur {{ display: none !important; }}
        .c-enfant {{ min-width: 80px; }}
        .c-parent {{ min-width: 70px; }}
        .matricule-badge, .status-ok, .status-wait {{ font-size: 9px; padding: 2px 5px; }}

        .profile-header {{ padding: 15px 12px; }}
        .profile-header h2 {{ font-size: 16px !important; }}
        .profile-body {{ padding: 12px; }}
        .profile-label {{ min-width: 130px; font-size: 11px; }}
        .profile-value {{ font-size: 12px; }}

        .prop3-login-card {{ width: 95% !important; padding-top: 180px; }}
        [data-testid="stContainer"] {{ padding: 10px; }}
    }}

    @media screen and (max-width: 480px) {{
        .hero-header {{ padding: 10px 8px; }}
        .hero-header h1 {{ font-size: 15px !important; }}
        .hero-header div {{ display: none !important; }}

        .rep-table-header {{ font-size: 8px; padding: 8px 4px; }}
        .rep-cell {{ padding: 5px 3px; font-size: 9px; }}
        .c-ville, .c-parent {{ display: none !important; }}
        .c-date {{ display: none !important; }}
        .c-action {{ width: 45px; min-width: 45px; max-width: 45px; }}

        .prop3-login-card {{ padding-top: 140px; padding-left: 15px; padding-right: 15px; }}
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- JAVASCRIPT FERMETURE MOBILE ---
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

# --- CONVERSION NUMÉRIQUE SÉCURISÉE ---
def safe_int_convert(val, default=0):
    if pd.isna(val) or val is None:
        return default
    val_str = str(val).strip()
    match = re.search(r'(\d+)', val_str)
    if match:
        return int(match.group(1))
    return default

# --- FORMATAGE DATE ADHESION ---
def formater_date_fr(val):
    s = str(val).strip().split(" ")[0]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return s
    return s

# --- GOOGLE SHEETS & CACHE ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=120)
def charger_donnees_depuis_sheets():
    client = init_connection()
    spreadsheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira")

    sheet_membres = spreadsheet.sheet1
    data = sheet_membres.get_all_records(head=9)

    try:
        df_users = pd.DataFrame(spreadsheet.worksheet("Utilisateurs").get_all_records())
    except Exception:
        df_users = pd.DataFrame()

    try:
        df_stock = pd.DataFrame(spreadsheet.worksheet("Dons_Stock").get_all_records())
    except Exception:
        df_stock = pd.DataFrame()

    try:
        df_distrib = pd.DataFrame(spreadsheet.worksheet("Remise de Dons").get_all_records())
    except Exception:
        df_distrib = pd.DataFrame()

    try:
        ws_cotiz = spreadsheet.worksheet("Cotisations")
        val_cotiz = ws_cotiz.get_all_values()
        headers_cotiz = ["ID_Cotiz", "Date", "ID_Membre", "Nom_Enfant", "Nom_Parent", "Type_Paiement", "Montant_Verse", "Statut", "Commentaire", "Enregistre_Par"]
        if not val_cotiz or val_cotiz[0][0] != "ID_Cotiz":
            ws_cotiz.insert_row(headers_cotiz, 1)
        df_cotiz = pd.DataFrame(ws_cotiz.get_all_records())
    except Exception:
        df_cotiz = pd.DataFrame()

    try:
        ws_art = spreadsheet.worksheet("Articles_Evenements")
        val_art = ws_art.get_all_values()
        headers_art = ["ID_Art", "Date", "ID_Membre", "Nom_Enfant", "Nom_Parent", "Nom_Article", "Quantite", "Montant_Total", "Statut_Reglement", "Statut_Livraison", "Enregistre_Par"]
        if not val_art or val_art[0][0] != "ID_Art":
            ws_art.insert_row(headers_art, 1)
        df_articles = pd.DataFrame(ws_art.get_all_records())
    except Exception:
        df_articles = pd.DataFrame()

    return data, df_users, df_stock, df_distrib, df_cotiz, df_articles

try:
    client = init_connection()
    spreadsheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira")
    sheet = spreadsheet.sheet1

    data, df_users, df_stock, df_distrib, df_cotiz, df_articles = charger_donnees_depuis_sheets()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()

    if not df_users.empty:
        df_users.columns = df_users.columns.str.strip()
    if not df_stock.empty:
        df_stock.columns = df_stock.columns.str.strip()
    if not df_distrib.empty:
        df_distrib.columns = df_distrib.columns.str.strip()
    if not df_cotiz.empty:
        df_cotiz.columns = df_cotiz.columns.str.strip()
    if not df_articles.empty:
        df_articles.columns = df_articles.columns.str.strip()

    col_tel_detect = "Numero Tèl" if "Numero Tèl" in df.columns else (df.columns[6] if len(df.columns) > 6 else "")
    if col_tel_detect in df.columns:
        df[col_tel_detect] = df[col_tel_detect].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df[col_tel_detect] = df[col_tel_detect].apply(lambda x: "0" + x if len(x) == 9 and x.isdigit() else x)

    if "Numéro du membre" in df.columns:
        df = df[df["Numéro du membre"].astype(str).str.startswith("ONG DP")]

except Exception as e:
    st.error(f"⚠️ Erreur de connexion à Google Sheets : {e}")
    df = pd.DataFrame()
    df_users = pd.DataFrame()
    df_stock = pd.DataFrame()
    df_distrib = pd.DataFrame()
    df_cotiz = pd.DataFrame()
    df_articles = pd.DataFrame()

# --- ZONES & COMMUNES ---
ZONES_SUD = ["TREICHVILLE", "MARCORY", "KOUMASSI", "PORT-BOUET", "PORTBOUET", "ADJAHUI", "MODESTE", "BASSAM", "GRAND-BASSAM", "YAOU", "BONOUA", "SAMO", "ABOISSO", "ADIAKE", "ASSINIE"]
ZONES_NORD = ["YOPOUGON", "ADJAME", "ADJAMÉ", "ATTECOUBE", "ATTÉCOUBÉ", "ABOBO", "N'DOTRE", "NDOTRE", "WILLIAMS CIVIL", "WILLIAMSSVILLE", "SONGON", "DABOU"]
ZONES_CENTRE = ["COCODY", "PLATEAU", "BINGERVILLE", "ANYAMA", "DOKUI"]

def attribuer_zone(ville):
    v = str(ville).upper().strip()
    if any(z in v for z in ZONES_SUD):
        return "Zone Sud"
    elif any(z in v for z in ZONES_NORD):
        return "Zone Nord"
    elif any(z in v for z in ZONES_CENTRE):
        return "Zone Centre"
    else:
        return "Intérieur / Autre"

def obtenir_prochain_matricule(df_membres):
    if df_membres.empty or "Numéro du membre" not in df
