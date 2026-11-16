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

# --- CHARGEMENT DE L'IMAGE DE FOND EN BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return None

banner_path = "banner_connection.png" if os.path.exists("banner_connection.png") else "banner_connexion.png"
banner_b64 = get_image_base64(banner_path)

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
    if df_membres.empty or "Numéro du membre" not in df_membres.columns:
        return "ONG DP 0001"
    numeros = []
    for val in df_membres["Numéro du membre"].dropna().astype(str):
        m = re.search(r'(\d+)', val)
        if m:
            numeros.append(int(m.group(1)))
    if numeros:
        prochain_num = max(numeros) + 1
    else:
        prochain_num = len(df_membres) + 1
    return f"ONG DP {prochain_num:04d}"

col_membre = "Numéro du membre" if "Numéro du membre" in df.columns else (df.columns[0] if len(df.columns) > 0 else "")
col_enfant = "Nom et Prénom de l'enfant" if "Nom et Prénom de l'enfant" in df.columns else (df.columns[1] if len(df.columns) > 1 else "")
col_date = "Date de naissance" if "Date de naissance" in df.columns else (df.columns[2] if len(df.columns) > 2 else "")
col_sexe = "Sexe" if "Sexe" in df.columns else (df.columns[3] if len(df.columns) > 3 else "")
col_ville = "Ville" if "Ville" in df.columns else (df.columns[4] if len(df.columns) > 4 else "")
col_parent = "Nom et prénoms du parent" if "Nom et prénoms du parent" in df.columns else (df.columns[5] if len(df.columns) > 5 else "")
col_tel = "Numero Tèl" if "Numero Tèl" in df.columns else (df.columns[6] if len(df.columns) > 6 else "")
col_adh = [c for c in df.columns if "Adh" in c][0] if any("Adh" in c for c in df.columns) else (df.columns[7] if len(df.columns) > 7 else "")

if not df.empty and col_ville in df.columns:
    df["Zone_Geographique"] = df[col_ville].apply(attribuer_zone)
else:
    df["Zone_Geographique"] = "Intérieur / Autre"

if "user_connected" not in st.session_state:
    st.session_state["user_connected"] = False
    st.session_state["user_info"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Tableau de Bord"
if "selected_member_profile" not in st.session_state:
    st.session_state["selected_member_profile"] = None

# ==========================================
# --- ÉCRAN DE CONNEXION ---
# ==========================================
if not st.session_state["user_connected"]:
    col_c1, col_c2, col_c3 = st.columns([1, 2.2, 1])

    with col_c2:
        st.markdown('<div class="prop3-login-card"><div class="prop3-login-inner">', unsafe_allow_html=True)
        st.markdown('<div class="prop3-title-text">ONG DIEU POURVOIRA</div>', unsafe_allow_html=True)
        
        with st.form("form_connexion_prop3"):
            identifiant = st.text_input("Identifiant utilisateur", placeholder="Ex: asso")
            mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_connexion = st.form_submit_button("Se connecter")

            if btn_connexion:
                if not df_users.empty and "Identifiant" in df_users.columns:
                    match = df_users[(df_users["Identifiant"].astype(str) == identifiant.strip()) & (df_users["Mot_de_passe"].astype(str) == mot_de_passe.strip())]
                    if not match.empty:
                        st.session_state["user_connected"] = True
                        st.session_state["user_info"] = match.iloc[0].to_dict()
                        st.toast(f"Bienvenue {st.session_state['user_info'].get('Nom_Responsable', '')} !", icon="👋")
                        st.rerun()
                    else:
                        st.error("❌ Identifiant ou mot de passe incorrect.")
                else:
                    if identifiant == "admin" and mot_de_passe == "admin123":
                        st.session_state["user_connected"] = True
                        st.session_state["user_info"] = {"Nom_Responsable": "Direction DSI", "Zone": "Vue Globale"}
                        st.rerun()
                    else:
                        st.error("❌ Identifiant ou mot de passe incorrect.")

        st.markdown(
            """
            <div class="prop3-footer-coords">
                📌 <strong>Coordonnées de l'ONG</strong><br>
                📞 <strong>Téléphone :</strong> +225 77 71 04 41 8 / 05 86 99 73 27<br>
                ✉️ <strong>Email :</strong> dieupourvoira187@gmail.com<br>
                📍 <strong>Adresse :</strong> 08 BP 2945 ABIDJAN 08
            </div>
            </div></div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# --- APPLICATION PRINCIPALE CONNECTÉE ---
# ==========================================
else:
    st.markdown(
        """
        <div class="hero-header">
            <h1 style="margin:0; font-size:24px; font-weight:800; color: #ffffff;">ONG DIEU POURVOIRA</h1>
            <p style="margin:4px 0 0 0; font-size:13px; color: #e2e8f0;">Ensemble aidons les enfants atteints de Paralysie cérébrale</p>
            <div style="font-size: 11px; margin-top: 8px; opacity: 0.9; color: #cbd5e1;">
                📞 +225 77 71 04 41 8 / 05 86 99 73 27 &nbsp;|&nbsp; ✉️ dieupourvoira187@gmail.com &nbsp;|&nbsp; 📍 08 BP 2945 ABIDJAN 08
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    user_info = st.session_state["user_info"]

    user_zone = ""
    for key in ["Zone / Rôle", "Zone", "Role", "Rôle"]:
        if key in user_info:
            user_zone = str(user_info[key])
            break
    if not user_zone:
        user_zone = "Vue Globale"

    user_nom = user_info.get("Nom_Responsable", "Utilisateur")

    is_compta = "COMPTA" in user_zone.upper() or "COMPTABILITÉ" in user_zone.upper()
    is_dsi = "DSI" in user_zone.upper() or "VUE GLOBALE" in user_zone.upper()

    # --- BARRE LATÉRALE ---
    st.sidebar.markdown('<div class="sidebar-menu-title">📂 MENU PRINCIPAL</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### 👤 **{user_nom}**")
    st.sidebar.caption(f"📌 **Espace : {user_zone}**")
    st.sidebar.markdown("---")

    if is_compta:
        pages = ["📦 Stock des Dons", "🎁 Remise de Dons", "💳 Suivi Cotisations", "🛍️ Articles & Goodies"]
        if st.session_state["current_page"] not in pages:
            st.session_state["current_page"] = pages[0]
    elif is_dsi:
        pages = [
            "📊 Tableau de Bord", "➕ Enregistrer un Membre", "✏️ Modifier / Supprimer",
            "📋 Liste & Répertoire", "📦 Stock des Dons", "🎁 Remise de Dons",
            "💳 Suivi Cotisations", "🛍️ Articles & Goodies"
        ]
    else:
        pages = [
            "📊 Tableau de Bord", "➕ Enregistrer un Membre", "✏️ Modifier / Supprimer",
            "📋 Liste & Répertoire", "💳 Suivi Cotisations", "🛍️ Articles & Goodies"
        ]

    st.sidebar.markdown("**NAVIGATION**")
    for page in pages:
        is_selected = (st.session_state["current_page"] == page)
        btn_style = "nav-btn-active" if is_selected else "nav-btn-inactive"
        
        st.sidebar.markdown(f'<div class="{btn_style}">', unsafe_allow_html=True)
        if st.sidebar.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state["current_page"] = page
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 Se déconnecter", use_container_width=True):
        st.session_state["user_connected"] = False
        st.session_state["user_info"] = None
        st.rerun()

    if "Zone Sud" in user_zone or "Sud" in user_zone:
        df_f = df[df["Zone_Geographique"] == "Zone Sud"]
        choix_zone_label = "📍 Zone Sud"
    elif "Zone Nord" in user_zone or "Nord" in user_zone:
        df_f = df[df["Zone_Geographique"] == "Zone Nord"]
        choix_zone_label = "📍 Zone Nord"
    elif "Zone Centre" in user_zone or "Centre" in user_zone:
        df_f = df[df["Zone_Geographique"] == "Zone Centre"]
        choix_zone_label = "📍 Zone Centre"
    elif "Intérieur" in user_zone or "Autre" in user_zone:
        df_f = df[df["Zone_Geographique"] == "Intérieur / Autre"]
        choix_zone_label = "📍 Intérieur / Autre"
    else:
        df_f = df
        choix_zone_label = "🌐 Vue Globale"

    menu = st.session_state["current_page"]

    # ==========================================
    # 1. TABLEAU DE BORD
    # ==========================================
    if menu == "📊 Tableau de Bord":
        st.subheader(f"📈 Vue Synthétique - {choix_zone_label}")

        with st.expander("📖 Guide d'utilisation rapide (Cliquez pour ouvrir)", expanded=False):
            st.markdown("""
            Bienvenue sur l'application de gestion de l'**ONG DIEU POURVOIRA** ! Voici comment naviguer facilement :
            * **➕ Enregistrer un Membre** : Permet d'inscrire un nouvel enfant et son parent (le matricule est généré automatiquement).
            * **📋 Liste & Répertoire** : Permet de consulter tous les inscrits, de rechercher un membre, de voir sa **fiche profil détaillée** ou d'imprimer sa **carte d'adhérent**.
            * **📦 Stock des Dons & 🎁 Remise** : Permet de suivre les entrées de matériel/vivres et de les distribuer aux enfants.
            * **💳 Suivi Cotisations & 🛍️ Articles** : Permet d'enregistrer les paiements et l'achat de goodies.
            """)

        if not df_f.empty:
            total_membres = len(df_f)
            total_garcons = len(df_f[df_f[col_sexe].astype(str).str.upper() == "M"]) if col_sexe in df_f.columns else 0
            total_filles = len(df_f[df_f[col_sexe].astype(str).str.upper() == "F"]) if col_sexe in df_f.columns else 0
            total_actifs = len(df_f[df_f[col_adh].astype(str).str.upper() == "OK"]) if col_adh in df_f.columns else 0

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Membres", total_membres)
            with k2:
                st.metric("Adhésions OK", total_actifs)
            with k3:
                st.metric("Garçons", total_garcons)
            with k4:
                st.metric("Filles", total_filles)

            st.markdown("---")
            with st.container(border=True):
                st.markdown("### 🕒 Derniers enfants enregistrés")
                st.caption("Aperçu rapide des 5 derniers ajouts dans votre zone.")
                cols_a_afficher = [c for c in df_f.columns if c != "Zone_Geographique" and c in df.columns and not df[c].isnull().all()]
                st.dataframe(df_f[cols_a_afficher].tail(5), use_container_width=True)
        else:
            st.warning("⚠️ Aucun membre trouvé pour cette zone.")

    # ==========================================
    # 2. ENREGISTRER UN MEMBRE
    # ==========================================
    elif menu == "➕ Enregistrer un Membre":
        st.subheader("📝 Nouvel Enregistrement")
        st.info("💡 Remplissez soigneusement les champs ci-dessous pour inscrire un nouvel enfant. Le matricule s'attribue automatiquement.")

        liste_communes = ["ABOISSO", "ABOBO", "ADIAKE", "ADJAME", "ADJAHUI", "ALÉPÉ", "ANYAMA", "ASSINIE", "ATTECOUBE", "BINGERVILLE", "BONOUA", "DABOU", "DALOA", "DIVO", "DOKUI", "GAGNOA", "GRAND-BASSAM", "GUIBEROUA", "ISSIA", "KOUMASSI", "MARCORY", "MODESTE", "N'DOTRE", "OUMÉ", "PLATEAU", "PORT-BOUET", "SAN-PÉDRO", "SAMO", "SONGON", "TREICHVILLE", "WILLIAMS CIVIL", "YAMOUSSOUKRO", "YAOU", "YOPOUGON", "AUTRE (Préciser ci-dessous)"]
        matricule_auto = obtenir_prochain_matricule(df)

        with st.container(border=True):
            with st.form("form_membre_principal", clear_on_submit=True):
                st.markdown("##### 👶 Informations de l'enfant")
                c1, c2 = st.columns(2)
                with c1:
                    numero_membre = st.text_input("Numéro du membre (Auto)", value=matricule_auto, disabled=True)
                    nom_enfant = st.text_input("Nom et Prénom de l'enfant (Ex: KOUASSI JEAN)").upper()
                with c2:
                    sexe = st.selectbox("Sexe", ["M", "F"])
                    date_naissance = st.text_input("Date de naissance / Âge (Ex: 12/05/2018 ou 5 ans)")

                ville_choix = st.selectbox("Commune / Ville de résidence", liste_communes)
                ville_autre = st.text_input("Si 'AUTRE' sélectionné, précisez la ville :").upper()

                st.markdown("---")
                st.markdown("##### 👪 Informations du parent & Statut")
                c3, c4 = st.columns(2)
                with c3:
                    nom_parent = st.text_input("Nom et prénoms du parent (Ex: KOUASSI MARC)").upper()
                    numero_tel = st.text_input("Numéro de téléphone du parent (Ex: 0700000000)")
                with c4:
                    adhesion = st.selectbox("Statut d'Adhésion", ["OK", "En attente"])

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("💾 Valider et enregistrer le membre", use_container_width=True)

                if submitted:
                    ville_finale = ville_autre if ville_choix.startswith("AUTRE") and ville_autre else ville_choix
                    if nom_enfant and nom_parent:
                        try:
                            date_heure_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            auteur_enregistrement = f"{user_nom} ({user_zone})"
                            nouvelle_ligne = [matricule_auto, nom_enfant, date_naissance, sexe, ville_finale, nom_parent, str(numero_tel), adhesion, date_heure_actuelle, auteur_enregistrement]
                            sheet.append_row(nouvelle_ligne)
                            st.cache_data.clear()
                            st.session_state["toast_msg"] = f"✅ Membre {matricule_auto} enregistré avec succès !"
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                    else:
                        st.error("⚠️ Veuillez renseigner au moins le nom de l'enfant et celui du parent.")

    # ==========================================
    # 3. MODIFIER / SUPPRIMER
    # ==========================================
    elif menu == "✏️ Modifier / Supprimer":
        st.subheader(f"✏️ Modifier ou Supprimer un Membre - {choix_zone_label}")
        st.info("💡 Tapez un nom, un matricule ou un parent dans la barre de recherche ci-dessous pour retrouver rapidement le membre à modifier ou supprimer.")

        if not df_f.empty and col_membre in df_f.columns:
            c_search_edit, c_reset_edit = st.columns([4, 1])
            with c_search_edit:
                recherche_edit = st.text_input("🔍 Rechercher un membre (Nom, Matricule, Parent)...", key="search_filtre_membre")
            with c_reset_edit:
                if st.button("🔄 Réinitialiser", help="Effacer le filtre", use_container_width=True, key="reset_edit"):
                    recherche_edit = ""
            
            if recherche_edit:
                mask_f = df_f.astype(str).apply(lambda row: row.str.contains(recherche_edit, case=False, na=False).any(), axis=1)
                df_filtered_select = df_f[mask_f]
            else:
                df_filtered_select = df_f

            if not df_filtered_select.empty:
                liste_membres_complets = df_filtered_select[col_membre].astype(str).tolist()
                
                if recherche_edit:
                    options_select = liste_membres_complets
                else:
                    options_select = ["-- Sélectionnez un membre dans la liste --"] + liste_membres_complets

                choix_membre = st.selectbox(
                    "Sélectionner le membre dans la liste filtrée", 
                    options_select, 
                    format_func=lambda m: m if m.startswith("--") else f"{m} - {df_filtered_select[df_filtered_select[col_membre].astype(str) == m][col_enfant].values[0]} ({df_filtered_select[df_filtered_select[col_membre].astype(str) == m][col_parent].values[0]})" if col_enfant in df_filtered_select.columns else m
                )

                if choix_membre and not choix_membre.startswith("--"):
                    membre_actuel = df[df[col_membre].astype(str) == choix_membre].iloc[0]

                    st.markdown("---")
                    choix_action = st.radio("Action à effectuer", ["Modifier les informations", "Supprimer le membre"], horizontal=True)

                    with st.container(border=True):
                        if choix_action == "Modifier les informations":
                            with st.form("form_modification", clear_on_submit=True):
                                m_nom_enfant = st.text_input("Nom et Prénom", value=str(membre_actuel.get(col_enfant, ""))).upper()
                                m_date_nais = st.text_input("Date de naissance", value=str(membre_actuel.get(col_date, "")))
                                val_sexe = str(membre_actuel.get(col_sexe, "M")).upper()
                                m_sexe = st.selectbox("Sexe", ["M", "F"], index=0 if val_sexe == "M" else 1)
                                m_ville = st.text_input("Ville", value=str(membre_actuel.get(col_ville, ""))).upper()
                                m_nom_parent = st.text_input("Parent", value=str(membre_actuel.get(col_parent, ""))).upper()
                                m_tel = st.text_input("Téléphone", value=str(membre_actuel.get(col_tel, "")))
                                val_adh = str(membre_actuel.get(col_adh, "OK")).upper()
                                m_adhesion = st.selectbox("Adhésion", ["OK", "En attente"], index=0 if "OK" in val_adh else 1)

                                btn_modifier = st.form_submit_button("💾 Mettre à jour les informations")
                                if btn_modifier:
                                    try:
                                        cell = sheet.find(str(choix_membre))
                                        row_idx = cell.row
                                        sheet.update_cell(row_idx, 2, m_nom_enfant)
                                        sheet.update_cell(row_idx, 3, m_date_nais)
                                        sheet.update_cell(row_idx, 4, m_sexe)
                                        sheet.update_cell(row_idx, 5, m_ville)
                                        sheet.update_cell(row_idx, 6, m_nom_parent)
                                        sheet.update_cell(row_idx, 7, str(m_tel))
                                        sheet.update_cell(row_idx, 8, m_adhesion)
                                        st.cache_data.clear()
                                        st.session_state["toast_msg"] = f"✅ Membre {choix_membre} mis à jour !"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Erreur : {e}")
                        else:
                            st.warning(f"⚠️ Suppression définitive du membre {choix_membre}")
                            confirmer = st.checkbox("Je confirme la suppression définitive de ce dossier")
                            if st.button("🗑️ Confirmer la suppression", type="primary"):
                                if confirmer:
                                    try:
                                        cell = sheet.find(str(choix_membre))
                                        sheet.delete_rows(cell.row)
                                        st.cache_data.clear()
                                        st.session_state["toast_msg"] = f"✅ Membre {choix_membre} supprimé !"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Erreur : {e}")
                                else:
                                    st.error("⚠️ Veuillez cocher la case de confirmation pour continuer.")
                else:
                    st.info("ℹ️ Veuillez sélectionner un membre dans la liste ci-dessus.")
            else:
                st.warning("⚠️ Aucun membre ne correspond à votre recherche.")
        else:
            st.info("Aucun membre disponible.")

    # ==========================================
    # 4. LISTE & REPERTOIRE + CARTES + PROFIL MEMBRE
    # ==========================================
    elif menu == "📋 Liste & Répertoire":
        st.subheader(f"📋 Répertoire & Cartes - {choix_zone_label}")
        st.info("💡 Astuce : Utilisez la barre de recherche ci-dessous pour filtrer instantanément le répertoire. Cliquez sur le bouton **👁️ Voir** de n'importe quelle ligne pour ouvrir la **fiche profil complète** du membre.")
        
        c_search, c_reset = st.columns([4, 1])
        with c_search:
            recherche = st.text_input("🔍 Recherche intuitive (Nom d'enfant, Parent, Téléphone, Matricule)...", key="recherche_liste")
        with c_reset:
            if st.button("🔄 Réinitialiser", help="Effacer la recherche", use_container_width=True):
                recherche = ""

        if not df_f.empty:
            if recherche:
                mask = df_f.astype(str).apply(lambda row: row.str.contains(recherche, case=False, na=False).any(), axis=1)
                df_affiche = df_f[mask]
                st.success(f"ℹ️ Résultats trouvés : {len(df_affiche)} membre(s)")
            else:
                df_affiche = df_f

            tab_liste, tab_cartes = st.tabs(["📋 Liste Générale & Fiches Profils", "🪪 Cartes d'Adhérents"])

            with tab_liste:
                total_lignes = len(df_affiche)
                if total_lignes > 0:
                    col_pg1, col_pg2, col_pg3 = st.columns([1, 2, 1])
                    with col_pg1:
                        lignes_par_page = st.selectbox("Lignes par page", [10, 25, 50, 100], index=0, key="lignes_page")
                    
                    total_pages = math.ceil(total_lignes / lignes_par_page)
                    if "page_courante" not in st.session_state or st.session_state["page_courante"] > total_pages:
                        st.session_state["page_courante"] = 1
                    
                    page_actuelle = st.session_state["page_courante"]
                    
                    with col_pg2:
                        st.markdown(f'<div class="pagination-info">Page {page_actuelle} / {total_pages}</div>', unsafe_allow_html=True)
                    
                    with col_pg3:
                        page_directe = st.selectbox("Aller à page...", range(1, total_pages + 1), 
                                                   index=min(page_actuelle - 1, total_pages - 1), 
                                                   label_visibility="collapsed", key="page_direct")
                    
                    c_prev, c_next = st.columns([1, 1])
                    with c_prev:
                        if st.button("◀️ Précédent", disabled=(page_actuelle <= 1), use_container_width=True, 
                                    key="btn_prev_page"):
                            st.session_state["page_courante"] = max(1, page_actuelle - 1)
                            st.rerun()
                    with c_next:
                        if st.button("Suivant ▶️", disabled=(page_actuelle >= total_pages), use_container_width=True,
                                    key="btn_next_page"):
                            st.session_state["page_courante"] = min(total_pages, page_actuelle + 1)
                            st.rerun()
                    
                    debut = (page_actuelle - 1) * lignes_par_page
                    fin = min(debut + lignes_par_page, total_lignes)
                    df_page = df_affiche.iloc[debut:fin].reset_index(drop=True)

                    cols_affichage = [c for c in df_page.columns if c != "Zone_Geographique"]
                    
                    with st.container(border=True):
                        header_html = '<div class="rep-table-header">'
                        header_html += '<div class="rep-cell c-action" style="justify-content:center;">⚡ Profil</div>'
                        for c in cols_affichage:
                            if c == col_membre: cls = "c-membre"
                            elif c == col_enfant: cls = "c-enfant"
                            elif c == col_date: cls = "c-date"
                            elif c == col_sexe: cls = "c-sexe"
                            elif c == col_ville: cls = "c-ville"
                            elif c == col_parent: cls = "c-parent"
                            elif c == col_tel: cls = "c-tel"
                            elif "Adh" in str(c): cls = "c-adh"
                            else: cls = "c-default"
                            header_html += f'<div class="rep-cell {cls}">{c}</div>'
                        header_html += '</div>'
                        st.markdown(header_html, unsafe_allow_html=True)
                        
                        for idx, row in df_page.iterrows():
                            matricule_val = str(row.get(col_membre, "")).strip()
                            matricule_safe = matricule_val.replace(" ", "_").replace(".", "_")
                            
                            row_html = '<div class="rep-table-row">'
                            for c in cols_affichage:
                                val = str(row.get(c, ""))
                                if c == col_membre: cls = "c-membre"
                                elif c == col_enfant: cls = "c-enfant"
                                elif c == col_date: cls = "c-date"
                                elif c == col_sexe: cls = "c-sexe"
                                elif c == col_ville: cls = "c-ville"
                                elif c == col_parent: cls = "c-parent"
                                elif c == col_tel: cls = "c-tel"
                                elif "Adh" in str(c): cls = "c-adh"
                                else: cls = "c-default"
                                
                                if c == col_membre:
                                    row_html += f'<div class="rep-cell {cls}"><span class="matricule-badge">{val}</span></div>'
                                elif c == col_sexe:
                                    sexe_cls = "sexe-m" if val.upper() == "M" else "sexe-f"
                                    row_html += f'<div class="rep-cell {cls}" style="justify-content:center;"><span class="{sexe_cls}">{val}</span></div>'
                                elif "Adh" in str(c):
                                    badge_cls = "status-ok" if "OK" in val.upper() else "status-wait"
                                    row_html += f'<div class="rep-cell {cls}"><span class="{badge_cls}">{val}</span></div>'
                                else:
                                    row_html += f'<div class="rep-cell {cls}" title="{val}">{val}</div>'
                            row_html += '</div>'
                            
                            c_btn, c_data = st.columns([0.45, 9.55], gap="small")
                            with c_btn:
                                if st.button("👁️ Voir", key=f"vp_{matricule_safe}_{idx}", help=f"Afficher le profil de {row.get(col_enfant, '')}"):
                                    st.session_state["selected_member_profile"] = matricule_val
                                    st.rerun()
                            with c_data:
                                st.markdown(row_html, unsafe_allow_html=True)

                    st.markdown("---")

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df_affiche.to_excel(writer, index=False, sheet_name="Membres")
                    excel_data = output.getvalue()

                    st.download_button(
                        label="📥 Exporter la liste filtrée en Excel (.xlsx)",
                        data=excel_data,
                        file_name=f"Membres_{choix_zone_label.replace(' ', '_')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    st.warning("⚠️ Aucun membre ne correspond à votre recherche.")

            # --- VUE PROFIL DÉTAILLÉE ---
            if st.session_state.get("selected_member_profile"):
                st.markdown("---")
                matricule_sélectionné = st.session_state["selected_member_profile"]
                membre_profil = df_f[df_f[col_membre].astype(str) == matricule_sélectionné]
                
                if not membre_profil.empty:
                    membre = membre_profil.iloc[0]

                    st.markdown(f"""
                        <div class="profile-header">
                            <h2>👤 FICHE PROFIL COMPLÈTE - {membre.get(col_membre, '')}</h2>
                            <p>ONG DIEU POURVOIRA • Dossier de l'enfant et suivi associatif</p>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.container():
                        st.markdown('<div class="profile-body">', unsafe_allow_html=True)

                        col_info_gauche, col_info_droite = st.columns(2)

                        with col_info_gauche:
                            st.markdown("##### 🧒 Informations de l'enfant")
                            st.markdown(f"""
                                <div class="profile-field">
                                    <div class="profile-label">📌 N° Membre :</div>
                                    <div class="profile-value" style="color: #4ade80; font-weight: bold; font-size: 15px;">{membre.get(col_membre, 'N/A')}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">👤 Nom et Prénom :</div>
                                    <div class="profile-value"><strong>{membre.get(col_enfant, 'N/A')}</strong></div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">📅 Date de naissance :</div>
                                    <div class="profile-value">{membre.get(col_date, 'N/A')}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">⚧ Sexe :</div>
                                    <div class="profile-value">{'👦 Garçon (M)' if str(membre.get(col_sexe, '')).upper()=='M' else '👧 Fille (F)'}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">🏙️ Commune / Ville :</div>
                                    <div class="profile-value">{membre.get(col_ville, 'N/A')}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">🗺️ Zone géographique :</div>
                                    <div class="profile-value"><span class="profile-badge badge-ok">{membre.get('Zone_Geographique', 'N/A')}</span></div>
                                </div>
                            """, unsafe_allow_html=True)

                        with col_info_droite:
                            st.markdown("##### 👨‍👩‍👧 Informations du parent & Enregistrement")
                            st.markdown(f"""
                                <div class="profile-field">
                                    <div class="profile-label">👨‍👩‍👧 Nom du Parent :</div>
                                    <div class="profile-value"><strong>{membre.get(col_parent, 'N/A')}</strong></div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">📞 Téléphone Parent :</div>
                                    <div class="profile-value" style="color: #38bdf8; font-weight: bold;">{membre.get(col_tel, 'N/A')}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">✅ Statut Adhésion :</div>
                                    <div class="profile-value"><span class="profile-badge {'badge-ok' if 'OK' in str(membre.get(col_adh, '')).upper() else 'badge-attente'}">{membre.get(col_adh, 'N/A')}</span></div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">📅 Date d'enregistrement :</div>
                                    <div class="profile-value">{membre.get(df.columns[8], 'N/A') if len(df.columns) > 8 else 'N/A'}</div>
                                </div>
                                <div class="profile-field">
                                    <div class="profile-label">👤 Enregistré par :</div>
                                    <div class="profile-value">{membre.get(df.columns[9], 'N/A') if len(df.columns) > 9 else 'N/A'}</div>
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<br>---", unsafe_allow_html=True)
                        st.markdown("##### 📊 Historique des Activités de ce Membre")

                        tab_hist_cotiz, tab_hist_dons, tab_hist_articles = st.tabs([
                            "💳 Cotisations versées", "🎁 Dons reçus", "🛍️ Articles & Goodies"
                        ])

                        with tab_hist_cotiz:
                            if not df_cotiz.empty and "ID_Membre" in df_cotiz.columns:
                                cotiz_membre = df_cotiz[df_cotiz["ID_Membre"].astype(str) == matricule_sélectionné]
                                if not cotiz_membre.empty:
                                    st.dataframe(cotiz_membre, use_container_width=True)
                                else:
                                    st.info("ℹ️ Aucune cotisation enregistrée pour ce membre.")
                            else:
                                st.info("ℹ️ Aucune donnée de cotisation disponible.")

                        with tab_hist_dons:
                            if not df_distrib.empty:
                                col_distrib_membre = next((c for c in ["ID_Membre", "Numéro du membre"] if c in df_distrib.columns), None)
                                if col_distrib_membre:
                                    dons_membre = df_distrib[df_distrib[col_distrib_membre].astype(str) == matricule_sélectionné]
                                    if not dons_membre.empty:
                                        st.dataframe(dons_membre, use_container_width=True)
                                    else:
                                        st.info("ℹ️ Aucun don reçu par ce membre pour le moment.")
                                else:
                                    st.info("ℹ️ Données de distribution non disponibles.")
                            else:
                                st.info("ℹ️ Aucune distribution enregistrée.")

                        with tab_hist_articles:
                            if not df_articles.empty and "ID_Membre" in df_articles.columns:
                                articles_membre = df_articles[df_articles["ID_Membre"].astype(str) == matricule_sélectionné]
                                if not articles_membre.empty:
                                    st.dataframe(articles_membre, use_container_width=True)
                                else:
                                    st.info("ℹ️ Aucun article ou goodies enregistré pour ce membre.")
                            else:
                                st.info("ℹ️ Aucune donnée d'article disponible.")

                        st.markdown('</div>', unsafe_allow_html=True)

                        if st.button("⬅️ Fermer la fiche profil et retourner à la liste", use_container_width=True):
                            st.session_state["selected_member_profile"] = None
                            st.rerun()
                else:
                    st.warning("⚠️ Membre introuvable.")
                    if st.button("⬅️ Retour", use_container_width=True):
                        st.session_state["selected_member_profile"] = None
                        st.rerun()

            with tab_cartes:
                st.markdown("##### 🪪 Génération de Cartes aux couleurs officielles de l'ONG")
                st.caption("Sélectionnez un membre actif pour générer sa carte de membre officielle imprimable.")
                
                if col_adh in df_affiche.columns:
                    df_ok = df_affiche[df_affiche[col_adh].astype(str).str.upper().str.strip() == "OK"]
                else:
                    df_ok = pd.DataFrame()

                if not df_ok.empty:
                    recherche_carte = st.text_input("🔍 Filtrer l'enfant pour la carte...", key="search_filtre_carte")
                    if recherche_carte:
                        mask_c = df_ok.astype(str).apply(lambda row: row.str.contains(recherche_carte, case=False, na=False).any(), axis=1)
                        df_ok_filtered = df_ok[mask_c]
                    else:
                        df_ok_filtered = df_ok

                    if not df_ok_filtered.empty:
                        c_sel, c_img = st.columns([2, 1])
                        with c_sel:
                            membre_selectionne = st.selectbox("1. Sélectionnez l'enfant :", df_ok_filtered[col_membre].astype(str).tolist(), format_func=lambda m: f"{m} - {df_ok_filtered[df_ok_filtered[col_membre].astype(str) == m][col_enfant].values[0]}")
                        with c_img:
                            photo_file = st.file_uploader("2. Photo de l'enfant (Optionnel)", type=["jpg", "png", "jpeg"])

                        if membre_selectionne:
                            row_m = df_ok_filtered[df_ok_filtered[col_membre].astype(str) == membre_selectionne].iloc[0]
                            if photo_file is not None:
                                img_src = f"data:image/png;base64,{base64.b64encode(photo_file.getvalue()).decode()}"
                            else:
                                img_src = "https://via.placeholder.com/130x150/e9ecef/6c757d?text=PHOTO"

                            nom_complet = str(row_m.get(col_enfant, "")).upper().split(" ", 1)
                            nom_e = nom_complet[0]
                            prenom_e = nom_complet[1] if len(nom_complet) > 1 else ""
                            nom_p = str(row_m.get(col_parent, "")).upper()
                            num_m = str(row_m.get(col_membre, ""))
                            date_adh = str(row_m.get(df.columns[8] if len(df.columns) > 8 else "", "")).split(" ")[0]
                            tel_p = str(row_m.get(col_tel, ""))

                            html_carte = f"""
                            <!DOCTYPE html>
                            <html>
                            <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
                            <body style="text-align: center; font-family: Arial, sans-serif;">
                                <div style="max-width: 600px; width: 100%; aspect-ratio: 600/380; background: #ffffff; border-radius: 16px; border: 3px solid #2e8b42; position: relative; margin: auto; text-align: left; overflow: hidden;">
                                    <div style="background: #2e8b42; color: white; padding: 12px; text-align: center; font-weight: bold; font-size: 18px; font-size: clamp(12px, 2.5vw, 18px);">ONG DIEU POURVOIRA - CARTE MEMBRE OFFICIELLE</div>
                                    <div style="position: absolute; left: 30px; top: 75px; width: 130px; height: 150px; border: 2px solid #2e8b42; border-radius: 8px; overflow: hidden;">
                                        <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
                                    </div>
                                    <div style="position: absolute; left: 180px; top: 75px; font-size: 14px; line-height: 26px; color: #222;">
                                        <div><strong>Nom :</strong> {nom_e}</div>
                                        <div><strong>Prénom :</strong> {prenom_e}</div>
                                        <div><strong>Parent :</strong> {nom_p}</div>
                                        <div><strong>N° Membre :</strong> <span style="color: #2e8b42; font-weight: bold;">{num_m}</span></div>
                                        <div><strong>Date :</strong> {date_adh}</div>
                                        <div><strong>Contact :</strong> {tel_p}</div>
                                    </div>
                                    <div style="position: absolute; bottom: 10px; width: 100%; text-align: center; font-size: 11px; color: #666;">
                                        Ensemble aidons les enfants atteints de Paralysie Cérébrale | Contact : +225 77 71 04 41 8
                                    </div>
                                </div>
                                <br>
                                <button onclick="window.print()" style="background: #2e8b42; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer;">🖨️ Imprimer la carte</button>
                            </body>
                            </html>
                            """
                            st.components.v1.html(html_carte, height=450)
                    else:
                        st.warning("⚠️ Aucun enfant ne correspond à votre recherche.")
                else:
                    st.warning("⚠️ Aucun membre actif (avec Adhésion OK) trouvé pour générer une carte.")
        else:
            st.warning("⚠️ Aucune donnée disponible.")

    # ==========================================
    # 5. STOCK DES DONS
    # ==========================================
    elif menu == "📦 Stock des Dons":
        st.subheader("📦 Stock & Réception des Dons")
        st.info("💡 Enregistrez ici les nouveaux dons reçus (matériel, vivres, finances) ou gérez le stock existant.")
        
        tab_ajout_stock, tab_modif_stock = st.tabs(["➕ Enregistrer un Don", "✏️ Modifier / Supprimer un Don du Stock"])

        with tab_ajout_stock:
            with st.container(border=True):
                with st.form("form_entree_don", clear_on_submit=True):
                    type_don = st.selectbox("Type de Don", ["Matériel Médical / Fauteuil", "Produits d'Hygiène / Couches", "Vivres / Alimentation", "Vêtements", "Don Financier (FCFA)", "Autre"])
                    designation = st.text_input("Désignation (Ex: Fauteuils Roulants Enfant)").upper()
                    donateur = st.text_input("Donateur / Partenaire (Laisser vide si anonyme)").upper()
                    quantite_recue = st.number_input("Quantité reçue", min_value=1, value=1, step=1)
                    valeur_estimee = st.number_input("Valeur estimée globale (FCFA)", min_value=0, value=0, step=5000)

                    btn_save_don = st.form_submit_button("📥 Enregistrer en Stock", use_container_width=True)
                    if btn_save_don:
                        if designation:
                            try:
                                ws_stock = spreadsheet.worksheet("Dons_Stock")
                                date_du_jour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                id_don = f"DON-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                nouvelle_ligne_don = [id_don, date_du_jour, type_don, designation, int(quantite_recue), int(quantite_recue), int(valeur_estimee), donateur if donateur else "ANONYME", user_zone, f"{user_nom}"]
                                ws_stock.append_row(nouvelle_ligne_don, value_input_option="USER_ENTERED")
                                st.cache_data.clear()
                                st.session_state["toast_msg"] = f"✅ Don '{designation}' enregistré en stock !"
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur lors de l'enregistrement : {e}")
                        else:
                            st.error("⚠️ Saisissez une désignation.")

        with tab_modif_stock:
            if not df_stock.empty and "ID_Don" in df_stock.columns:
                with st.container(border=True):
                    c_s_stock, c_r_stock = st.columns([4, 1])
                    with c_s_stock:
                        recherche_stock_mod = st.text_input("🔍 Filtrer les dons par Désignation ou ID...", key="search_filtre_stock_mod")
                    with c_r_stock:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_stock"):
                            recherche_stock_mod = ""
                    
                    if recherche_stock_mod:
                        mask_s = df_stock.astype(str).apply(lambda row: row.str.contains(recherche_stock_mod, case=False, na=False).any(), axis=1)
                        df_stock_filtered = df_stock[mask_s]
                    else:
                        df_stock_filtered = df_stock

                    if not df_stock_filtered.empty:
                        liste_dons_f = df_stock_filtered["ID_Don"].astype(str).tolist()
                        options_dons = ["-- Sélectionnez un don --"] + liste_dons_f if not recherche_stock_mod else liste_dons_f

                        choix_id_don = st.selectbox(
                            "Sélectionner le Don à modifier/supprimer", 
                            options_dons, 
                            format_func=lambda d: d if d.startswith("--") else f"{d} - {df_stock_filtered[df_stock_filtered['ID_Don'].astype(str) == d]['Designation'].values[0]}"
                        )

                        if choix_id_don and not choix_id_don.startswith("--"):
                            don_ligne = df_stock[df_stock["ID_Don"].astype(str) == choix_id_don].iloc[0]

                            action_stock = st.radio("Action sur ce stock", ["Modifier", "Supprimer définitivement"], horizontal=True)
                            if action_stock == "Modifier":
                                with st.form("form_modif_stock"):
                                    nouveau_des = st.text_input("Désignation", value=str(don_ligne.get("Designation", ""))).upper()
                                    nouv_stock_act = st.number_input("Stock Actuel", min_value=0, value=safe_int_convert(don_ligne.get("Stock_Actuel", 0)))
                                    nouv_valeur = st.number_input("Valeur (FCFA)", min_value=0, value=safe_int_convert(don_ligne.get("Valeur_Estimee", 0)))

                                    if st.form_submit_button("💾 Mettre à jour le stock"):
                                        try:
                                            ws_stock = spreadsheet.worksheet("Dons_Stock")
                                            cell = ws_stock.find(str(choix_id_don))
                                            row_idx = cell.row
                                            ws_stock.update_cell(row_idx, 4, nouveau_des)
                                            ws_stock.update_cell(row_idx, 6, int(nouv_stock_act))
                                            ws_stock.update_cell(row_idx, 7, int(nouv_valeur))
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Don {choix_id_don} mis à jour avec succès !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                            else:
                                conf_sup = st.checkbox("Je confirme la suppression définitive de ce stock")
                                if st.button("🗑️ Supprimer définitivement du stock", type="primary"):
                                    if conf_sup:
                                        try:
                                            ws_stock = spreadsheet.worksheet("Dons_Stock")
                                            cell = ws_stock.find(str(choix_id_don))
                                            ws_stock.delete_rows(cell.row)
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Don {choix_id_don} supprimé !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                                    else:
                                        st.error("⚠️ Veuillez cocher la case de confirmation.")
                        else:
                            st.info("ℹ️ Veuillez sélectionner un don dans la liste ci-dessus.")
                    else:
                        st.warning("⚠️ Aucun don ne correspond à votre recherche.")
            else:
                st.info("Aucun stock enregistré pour le moment.")

        st.markdown("---")
        st.markdown("### 📊 État actuel des Stocks")
        with st.container(border=True):
            if not df_stock.empty:
                st.dataframe(df_stock, use_container_width=True)
            else:
                st.info("Aucun stock pour le moment.")

    # ==========================================
    # 6. REMISE DE DONS (AMÉLIORÉ AVEC MODIFICATION/SUPPRESSION DE REMISE)
    # ==========================================
    elif menu == "🎁 Remise de Dons":
        st.subheader("🎁 Attribution & Remise de Don aux Enfants")
        st.info("💡 Associez un article disponible en stock à un enfant bénéficiaire, ou gérez l'historique des remises.")
        
        tab_ajout_remise, tab_modif_remise = st.tabs(["🎁 Remettre un Don", "✏️ Modifier / Annuler une Remise"])
        
        with tab_ajout_remise:
            if not df.empty and not df_stock.empty:
                if "Stock_Actuel" in df_stock.columns:
                    df_stock_dispo = df_stock[df_stock["Stock_Actuel"].apply(safe_int_convert) > 0]
                else:
                    df_stock_dispo = df_stock

                if not df_stock_dispo.empty:
                    with st.container(border=True):
                        c_r1_r, c_r2_r = st.columns([4, 1])
                        with c_r1_r:
                            recherche_benef_remise = st.text_input("🔍 Filtrer l'enfant bénéficiaire par mot-clé...")
                        with c_r2_r:
                            if st.button("🔄 Reset Membre", use_container_width=True, key="rst_memb_r"):
                                recherche_benef_remise = ""
                        
                        c_r3_r, c_r4_r = st.columns([4, 1])
                        with c_r3_r:
                            recherche_don_remise = st.text_input("🔍 Filtrer le don en stock par mot-clé...")
                        with c_r4_r:
                            if st.button("🔄 Reset Don", use_container_width=True, key="rst_don_r"):
                                recherche_don_remise = ""
                        
                        if recherche_benef_remise:
                            mask_eb = df.astype(str).apply(lambda row: row.str.contains(recherche_benef_remise, case=False, na=False).any(), axis=1)
                            df_enfants_f = df[mask_eb]
                        else:
                            df_enfants_f = df

                        if recherche_don_remise:
                            mask_db = df_stock_dispo.astype(str).apply(lambda row: row.str.contains(recherche_don_remise, case=False, na=False).any(), axis=1)
                            df_stock_f = df_stock_dispo[mask_db]
                        else:
                            df_stock_f = df_stock_dispo

                        if not df_enfants_f.empty and not df_stock_f.empty:
                            with st.form("form_remise_don", clear_on_submit=True):
                                liste_enfants = df_enfants_f[col_membre].astype(str).tolist()
                                choix_enfant_don = st.selectbox("1. Enfant bénéficiaire", liste_enfants, format_func=lambda m: f"{m} - {df_enfants_f[df_enfants_f[col_membre].astype(str) == m][col_enfant].values[0]}")

                                liste_dons_dispo = df_stock_f["ID_Don"].astype(str).tolist()
                                choix_don = st.selectbox("2. Don à remettre", liste_dons_dispo, format_func=lambda d: f"{d} - {df_stock_f[df_stock_f['ID_Don'].astype(str) == d]['Designation'].values[0]} (Reste: {df_stock_f[df_stock_f['ID_Don'].astype(str) == d]['Stock_Actuel'].values[0]})")

                                quantite_remise = st.number_input("3. Quantité remise", min_value=1, value=1, step=1)
                                btn_remettre = st.form_submit_button("🎁 Valider la Remise du Don", use_container_width=True)

                                if btn_remettre:
                                    try:
                                        enfant_info = df[df[col_membre].astype(str) == choix_enfant_don].iloc[0]
                                        nom_e = enfant_info.get(col_enfant, "")
                                        nom_p = enfant_info.get(col_parent, "")

                                        don_info = df_stock_dispo[df_stock_dispo["ID_Don"].astype(str) == choix_don].iloc[0]
                                        designation_d = don_info.get("Designation", "")
                                        stock_actuel = safe_int_convert(don_info.get("Stock_Actuel", 1))

                                        if quantite_remise <= stock_actuel:
                                            ws_distrib = spreadsheet.worksheet("Remise de Dons")
                                            ws_stock = spreadsheet.worksheet("Dons_Stock")

                                            id_distrib = f"DIST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                            date_remise = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                            ligne_distrib = [id_distrib, date_remise, choix_enfant_don, nom_e, nom_p, designation_d, int(quantite_remise), user_zone, f"{user_nom}"]
                                            ws_distrib.append_row(ligne_distrib, value_input_option="USER_ENTERED")

                                            cell = ws_stock.find(str(choix_don))
                                            nouv_stock = stock_actuel - quantite_remise
                                            ws_stock.update_cell(cell.row, 6, nouv_stock)

                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"🎁 Don remis à {nom_e} avec succès !"
                                            st.rerun()
                                        else:
                                            st.error(f"⚠️ Stock insuffisant (Reste : {stock_actuel})")
                                    except Exception as e:
                                        st.error(f"❌ Erreur lors de la remise : {e}")
                        else:
                            st.warning("⚠️ Aucun résultat pour vos critères de recherche.")
                else:
                    st.warning("⚠️ Aucun don disponible en stock actuellement.")
            else:
                st.warning("⚠️ Données insuffisantes (membres ou stock).")

        with tab_modif_remise:
            st.markdown("### ✏️ Modifier ou Annuler une Remise")
            if not df_distrib.empty:
                col_id_distrib = df_distrib.columns[0]
                col_qte_remise = df_distrib.columns[6] if len(df_distrib.columns) > 6 else "Quantite"
                col_designation_d = df_distrib.columns[5] if len(df_distrib.columns) > 5 else "Designation"

                with st.container(border=True):
                    c_s_dist, c_r_dist = st.columns([4, 1])
                    with c_s_dist:
                        recherche_dist_mod = st.text_input("🔍 Filtrer les remises par Nom d'enfant, Don ou ID...", key="search_filtre_dist_mod")
                    with c_r_dist:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_dist"):
                            recherche_dist_mod = ""
                    
                    if recherche_dist_mod:
                        mask_d = df_distrib.astype(str).apply(lambda row: row.str.contains(recherche_dist_mod, case=False, na=False).any(), axis=1)
                        df_distrib_filtered = df_distrib[mask_d]
                    else:
                        df_distrib_filtered = df_distrib

                    if not df_distrib_filtered.empty:
                        liste_dist_f = df_distrib_filtered[col_id_distrib].astype(str).tolist()
                        options_dist = ["-- Sélectionnez une remise --"] + liste_dist_f if not recherche_dist_mod else liste_dist_f

                        choix_id_dist = st.selectbox(
                            "Sélectionner la remise à modifier/annuler", 
                            options_dist, 
                            format_func=lambda d: d if d.startswith("--") else f"{d} - {df_distrib_filtered[df_distrib_filtered[col_id_distrib].astype(str) == d][df_distrib_filtered.columns[3]].values[0]} ({df_distrib_filtered[df_distrib_filtered[col_id_distrib].astype(str) == d][col_designation_d].values[0]})"
                        )

                        if choix_id_dist and not choix_id_dist.startswith("--"):
                            dist_ligne = df_distrib[df_distrib[col_id_distrib].astype(str) == choix_id_dist].iloc[0]
                            qte_initiale = safe_int_convert(dist_ligne.get(col_qte_remise, 0))
                            designation_concernee = dist_ligne.get(col_designation_d, "")

                            action_dist = st.radio("Action sur cette remise", ["Modifier la quantité", "Annuler la remise (Restituer au stock)"], horizontal=True)
                            
                            if action_dist == "Modifier la quantité":
                                with st.form("form_modif_dist"):
                                    nouvelle_qte_dist = st.number_input(f"Nouvelle quantité pour '{designation_concernee}'", min_value=1, value=qte_initiale)
                                    
                                    if st.form_submit_button("💾 Mettre à jour la remise"):
                                        try:
                                            # Trouver l'ID du don d'origine dans le stock via la désignation
                                            don_stock_correspondant = df_stock[df_stock["Designation"] == designation_concernee]
                                            
                                            if not don_stock_correspondant.empty:
                                                id_don_stock = don_stock_correspondant.iloc[0]["ID_Don"]
                                                stock_actuel = safe_int_convert(don_stock_correspondant.iloc[0]["Stock_Actuel"])
                                                
                                                diff_qte = nouvelle_qte_dist - qte_initiale
                                                
                                                if diff_qte <= stock_actuel:
                                                    ws_distrib = spreadsheet.worksheet("Remise de Dons")
                                                    cell_dist = ws_distrib.find(str(choix_id_dist))
                                                    ws_distrib.update_cell(cell_dist.row, 7, int(nouvelle_qte_dist))
                                                    
                                                    nouveau_stock = stock_actuel - diff_qte
                                                    ws_stock = spreadsheet.worksheet("Dons_Stock")
                                                    cell_stock = ws_stock.find(str(id_don_stock))
                                                    ws_stock.update_cell(cell_stock.row, 6, nouveau_stock)
                                                    
                                                    st.cache_data.clear()
                                                    st.session_state["toast_msg"] = f"✅ Quantité de la remise {choix_id_dist} mise à jour !"
                                                    st.rerun()
                                                else:
                                                    st.error(f"⚠️ Stock insuffisant pour augmenter la quantité (Stock restant : {stock_actuel})")
                                            else:
                                                # Mise à jour simple si don introuvable en stock
                                                ws_distrib = spreadsheet.worksheet("Remise de Dons")
                                                cell_dist = ws_distrib.find(str(choix_id_dist))
                                                ws_distrib.update_cell(cell_dist.row, 7, int(nouvelle_qte_dist))
                                                st.cache_data.clear()
                                                st.session_state["toast_msg"] = f"✅ Quantité mise à jour (Attention : Don d'origine non trouvé dans le stock)."
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                            else:
                                conf_sup_dist = st.checkbox(f"Je confirme l'annulation de la remise. La quantité ({qte_initiale}) sera restituée au stock.")
                                if st.button("🗑️ Annuler la remise", type="primary"):
                                    if conf_sup_dist:
                                        try:
                                            ws_distrib = spreadsheet.worksheet("Remise de Dons")
                                            cell_dist = ws_distrib.find(str(choix_id_dist))
                                            ws_distrib.delete_rows(cell_dist.row)
                                            
                                            don_stock_correspondant = df_stock[df_stock["Designation"] == designation_concernee]
                                            if not don_stock_correspondant.empty:
                                                id_don_stock = don_stock_correspondant.iloc[0]["ID_Don"]
                                                stock_actuel = safe_int_convert(don_stock_correspondant.iloc[0]["Stock_Actuel"])
                                                nouveau_stock = stock_actuel + qte_initiale
                                                
                                                ws_stock = spreadsheet.worksheet("Dons_Stock")
                                                cell_stock = ws_stock.find(str(id_don_stock))
                                                ws_stock.update_cell(cell_stock.row, 6, nouveau_stock)
                                            
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Remise {choix_id_dist} annulée et stock restitué !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                                    else:
                                        st.error("⚠️ Veuillez cocher la case de confirmation.")
                        else:
                            st.info("ℹ️ Veuillez sélectionner une remise dans la liste.")
                    else:
                        st.warning("⚠️ Aucune remise ne correspond à votre recherche.")
            else:
                st.info("Aucune remise enregistrée pour le moment.")

        st.markdown("---")
        st.markdown("### 📋 Historique global des Remises")
        with st.container(border=True):
            if not df_distrib.empty:
                st.dataframe(df_distrib, use_container_width=True)
            else:
                st.info("Aucune distribution enregistrée.")

    # ==========================================
    # 7. SUIVI DES COTISATIONS
    # ==========================================
    elif menu == "💳 Suivi Cotisations":
        st.subheader("💳 Suivi des Cotisations et Frais de Carte")
        st.info("💡 Enregistrez les règlements de cotisations mensuelles ou frais de carte des membres.")
        
        tab_cotiz_saisie, tab_cotiz_suivi, tab_cotiz_modif = st.tabs(["➕ Enregistrer un Paiement", "📊 Tableau de Bord & Impayés", "✏️ Modifier / Supprimer un Paiement"])

        with tab_cotiz_saisie:
            if not df.empty:
                with st.container(border=True):
                    c_sc, c_rc = st.columns([4, 1])
                    with c_sc:
                        recherche_cotiz_saisie = st.text_input("🔍 Filtrer le membre concerné...")
                    with c_rc:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_cotiz_s"):
                            recherche_cotiz_saisie = ""
                    
                    if recherche_cotiz_saisie:
                        mask_cs = df.astype(str).apply(lambda row: row.str.contains(recherche_cotiz_saisie, case=False, na=False).any(), axis=1)
                        df_cotiz_s_f = df[mask_cs]
                    else:
                        df_cotiz_s_f = df

                    if not df_cotiz_s_f.empty:
                        with st.form("form_cotisation", clear_on_submit=True):
                            liste_membres_cotiz = df_cotiz_s_f[col_membre].astype(str).tolist()
                            membre_c = st.selectbox("Membre concerné", liste_membres_cotiz, format_func=lambda m: f"{m} - {df_cotiz_s_f[df_cotiz_s_f[col_membre].astype(str) == m][col_enfant].values[0]}")

                            type_paiement = st.selectbox("Type de règlement", [
                                "Frais de Carte d'Adhésion", "Cotisation - Janvier", "Cotisation - Février", "Cotisation - Mars",
                                "Cotisation - Avril", "Cotisation - Mai", "Cotisation - Juin", "Cotisation - Juillet",
                                "Cotisation - Août", "Cotisation - Septembre", "Cotisation - Octobre", "Cotisation - Novembre",
                                "Cotisation - Décembre", "Cotisation - Autre / Annuelle"
                            ])

                            montant_verse = st.number_input("Montant versé (FCFA)", min_value=0, value=5000, step=500)
                            statut_pay = st.selectbox("Statut", ["Payé en totalité", "Avance / Partiel"])
                            commentaire_cotiz = st.text_input("Commentaire (Optionnel)")

                            if st.form_submit_button("💾 Enregistrer le paiement", use_container_width=True):
                                try:
                                    ws_cotiz = spreadsheet.worksheet("Cotisations")
                                    enfant_info = df[df[col_membre].astype(str) == membre_c].iloc[0]
                                    nom_e = enfant_info.get(col_enfant, "")
                                    nom_p = enfant_info.get(col_parent, "")

                                    id_cotiz = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                    date_c = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                    ligne_cotiz = [id_cotiz, date_c, membre_c, nom_e, nom_p, type_paiement, int(montant_verse), statut_pay, commentaire_cotiz, user_nom]
                                    ws_cotiz.append_row(ligne_cotiz, value_input_option="USER_ENTERED")
                                    st.cache_data.clear()
                                    st.session_state["toast_msg"] = f"✅ Paiement de {montant_verse} FCFA enregistré !"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur : {e}")
                    else:
                        st.warning("⚠️ Aucun membre trouvé.")
            else:
                st.warning("⚠️ Aucun membre enregistré.")

        with tab_cotiz_suivi:
            st.markdown("### 📋 Historique & États des Cotisations")
            if not df_cotiz.empty and "ID_Cotiz" in df_cotiz.columns:
                st.dataframe(df_cotiz, use_container_width=True)
            else:
                st.info("Aucune cotisation enregistrée pour le moment.")

        with tab_cotiz_modif:
            st.markdown("### ✏️ Modifier ou Supprimer un Paiement")
            if not df_cotiz.empty and "ID_Cotiz" in df_cotiz.columns:
                with st.container(border=True):
                    c_scm, c_rcm = st.columns([4, 1])
                    with c_scm:
                        recherche_cotiz_mod = st.text_input("🔍 Filtrer les paiements...", key="search_filtre_cotiz_mod")
                    with c_rcm:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_cotiz_m"):
                            recherche_cotiz_mod = ""
                    
                    if recherche_cotiz_mod:
                        mask_cm = df_cotiz.astype(str).apply(lambda row: row.str.contains(recherche_cotiz_mod, case=False, na=False).any(), axis=1)
                        df_cotiz_f = df_cotiz[mask_cm]
                    else:
                        df_cotiz_f = df_cotiz

                    if not df_cotiz_f.empty:
                        liste_cotiz_f = df_cotiz_f["ID_Cotiz"].astype(str).tolist()
                        options_cotiz = ["-- Sélectionnez un paiement --"] + liste_cotiz_f if not recherche_cotiz_mod else liste_cotiz_f

                        choix_id_cotiz = st.selectbox(
                            "Sélectionner le paiement à modifier/supprimer", 
                            options_cotiz, 
                            format_func=lambda c: c if c.startswith("--") else f"{c} - {df_cotiz_f[df_cotiz_f['ID_Cotiz'].astype(str) == c]['Nom_Enfant'].values[0]} ({df_cotiz_f[df_cotiz_f['ID_Cotiz'].astype(str) == c]['Montant_Verse'].values[0]} FCFA)"
                        )

                        if choix_id_cotiz and not choix_id_cotiz.startswith("--"):
                            cotiz_ligne = df_cotiz[df_cotiz["ID_Cotiz"].astype(str) == choix_id_cotiz].iloc[0]

                            action_cotiz = st.radio("Action", ["Modifier", "Supprimer définitivement"], horizontal=True, key="radio_act_cotiz")

                            if action_cotiz == "Modifier":
                                with st.form("form_modif_cotiz"):
                                    nouveau_montant = st.number_input("Montant versé (FCFA)", min_value=0, value=safe_int_convert(cotiz_ligne.get("Montant_Verse", 0)))
                                    nouveau_statut = st.selectbox("Statut", ["Payé en totalité", "Avance / Partiel"], index=0 if str(cotiz_ligne.get("Statut", "")).startswith("Payé") else 1)
                                    nouveau_comm = st.text_input("Commentaire", value=str(cotiz_ligne.get("Commentaire", "")))

                                    if st.form_submit_button("💾 Mettre à jour le paiement"):
                                        try:
                                            ws_cotiz = spreadsheet.worksheet("Cotisations")
                                            cell = ws_cotiz.find(str(choix_id_cotiz))
                                            row_idx = cell.row
                                            ws_cotiz.update_cell(row_idx, 7, int(nouveau_montant))
                                            ws_cotiz.update_cell(row_idx, 8, nouveau_statut)
                                            ws_cotiz.update_cell(row_idx, 9, nouveau_comm)
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Paiement {choix_id_cotiz} mis à jour !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                            else:
                                conf_sup_c = st.checkbox("Je confirme la suppression de ce paiement", key="chk_sup_cot")
                                if st.button("🗑️ Supprimer ce paiement", type="primary"):
                                    if conf_sup_c:
                                        try:
                                            ws_cotiz = spreadsheet.worksheet("Cotisations")
                                            cell = ws_cotiz.find(str(choix_id_cotiz))
                                            ws_cotiz.delete_rows(cell.row)
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Paiement {choix_id_cotiz} supprimé !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                                    else:
                                        st.error("⚠️ Cochez la case de confirmation.")
                        else:
                            st.info("ℹ️ Veuillez sélectionner un paiement dans la liste.")
                    else:
                        st.warning("⚠️ Aucun paiement trouvé.")
            else:
                st.info("Aucun paiement enregistré.")

    # ==========================================
    # 8. ARTICLES & GOODIES
    # ==========================================
    elif menu == "🛍️ Articles & Goodies":
        st.subheader("🛍️ Gestion des Articles, T-shirts et Goodies d'Événements")
        st.info("💡 Suivez les ventes d'articles promotionnels ou de goodies de l'ONG.")
        
        tab_art_vente, tab_art_suivi, tab_art_modif = st.tabs(["➕ Enregistrer une Vente", "📊 Suivi & Inventaire", "✏️ Modifier / Supprimer un Article"])

        with tab_art_vente:
            if not df.empty:
                with st.container(border=True):
                    c_sav, c_rav = st.columns([4, 1])
                    with c_sav:
                        recherche_art_vente = st.text_input("🔍 Filtrer le membre...")
                    with c_rav:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_art_v"):
                            recherche_art_vente = ""

                    if recherche_art_vente:
                        mask_av = df.astype(str).apply(lambda row: row.str.contains(recherche_art_vente, case=False, na=False).any(), axis=1)
                        df_art_s_f = df[mask_av]
                    else:
                        df_art_s_f = df

                    if not df_art_s_f.empty:
                        with st.form("form_article_event", clear_on_submit=True):
                            liste_membres_art = df_art_s_f[col_membre].astype(str).tolist()
                            membre_a = st.selectbox("Membre acheteur", liste_membres_art, format_func=lambda m: f"{m} - {df_art_s_f[df_art_s_f[col_membre].astype(str) == m][col_enfant].values[0]}")

                            nom_article = st.text_input("Nom de l'article / Goodies (Ex: T-shirt ONG M)").upper()
                            quantite_art = st.number_input("Quantité", min_value=1, value=1, step=1)
                            montant_total = st.number_input("Montant Total (FCFA)", min_value=0, value=3000, step=500)

                            statut_reglement = st.selectbox("Statut du paiement", ["Payé", "Avance", "Impayé"])
                            statut_livraison = st.selectbox("Statut de remise", ["Livré / Remis", "En attente de retrait"])

                            if st.form_submit_button("💾 Enregistrer l'article", use_container_width=True):
                                if nom_article:
                                    try:
                                        ws_art = spreadsheet.worksheet("Articles_Evenements")
                                        enfant_info = df[df[col_membre].astype(str) == membre_a].iloc[0]
                                        nom_e = enfant_info.get(col_enfant, "")
                                        nom_p = enfant_info.get(col_parent, "")

                                        id_art = f"ART-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                        date_a = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                        ligne_art = [id_art, date_a, membre_a, nom_e, nom_p, nom_article, int(quantite_art), int(montant_total), statut_reglement, statut_livraison, user_nom]
                                        ws_art.append_row(ligne_art, value_input_option="USER_ENTERED")
                                        st.cache_data.clear()
                                        st.session_state["toast_msg"] = f"✅ Article '{nom_article}' enregistré !"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Erreur : {e}")
                                else:
                                    st.error("⚠️ Saisissez le nom de l'article.")
                    else:
                        st.warning("⚠️ Aucun membre trouvé.")
            else:
                st.warning("⚠️ Aucun membre enregistré.")

        with tab_art_suivi:
            st.markdown("### 📋 Suivi des Ventes")
            if not df_articles.empty and "ID_Art" in df_articles.columns:
                st.dataframe(df_articles, use_container_width=True)
            else:
                st.info("Aucun article enregistré pour le moment.")

        with tab_art_modif:
            st.markdown("### ✏️ Modifier ou Supprimer un Article")
            if not df_articles.empty and "ID_Art" in df_articles.columns:
                with st.container(border=True):
                    c_sam, c_ram = st.columns([4, 1])
                    with c_sam:
                        recherche_art_mod = st.text_input("🔍 Filtrer les articles...", key="search_filtre_art_mod")
                    with c_ram:
                        if st.button("🔄 Réinitialiser", use_container_width=True, key="reset_art_m"):
                            recherche_art_mod = ""
                    
                    if recherche_art_mod:
                        mask_am = df_articles.astype(str).apply(lambda row: row.str.contains(recherche_art_mod, case=False, na=False).any(), axis=1)
                        df_articles_f = df_articles[mask_am]
                    else:
                        df_articles_f = df_articles

                    if not df_articles_f.empty:
                        liste_art_f = df_articles_f["ID_Art"].astype(str).tolist()
                        options_art = ["-- Sélectionnez un article --"] + liste_art_f if not recherche_art_mod else liste_art_f

                        choix_id_art = st.selectbox(
                            "Sélectionner l'article", 
                            options_art, 
                            format_func=lambda a: a if a.startswith("--") else f"{a} - {df_articles_f[df_articles_f['ID_Art'].astype(str) == a]['Nom_Article'].values[0]}"
                        )

                        if choix_id_art and not choix_id_art.startswith("--"):
                            art_ligne = df_articles[df_articles["ID_Art"].astype(str) == choix_id_art].iloc[0]

                            action_art = st.radio("Action", ["Modifier", "Supprimer définitivement"], horizontal=True, key="radio_act_art")

                            if action_art == "Modifier":
                                with st.form("form_modif_art"):
                                    nouveau_nom_art = st.text_input("Nom de l'article", value=str(art_ligne.get("Nom_Article", ""))).upper()
                                    nouvelle_qte = st.number_input("Quantité", min_value=1, value=safe_int_convert(art_ligne.get("Quantite", 1), default=1))
                                    nouveau_montant_art = st.number_input("Montant Total (FCFA)", min_value=0, value=safe_int_convert(art_ligne.get("Montant_Total", 0)))
                                    nouveau_stat_reg = st.selectbox("Statut paiement", ["Payé", "Avance", "Impayé"])
                                    nouveau_stat_liv = st.selectbox("Statut remise", ["Livré / Remis", "En attente de retrait"])

                                    if st.form_submit_button("💾 Mettre à jour"):
                                        try:
                                            ws_art = spreadsheet.worksheet("Articles_Evenements")
                                            cell = ws_art.find(str(choix_id_art))
                                            row_idx = cell.row
                                            ws_art.update_cell(row_idx, 6, nouveau_nom_art)
                                            ws_art.update_cell(row_idx, 7, int(nouvelle_qte))
                                            ws_art.update_cell(row_idx, 8, int(nouveau_montant_art))
                                            ws_art.update_cell(row_idx, 9, nouveau_stat_reg)
                                            ws_art.update_cell(row_idx, 10, nouveau_stat_liv)
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Article {choix_id_art} mis à jour !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                            else:
                                conf_sup_a = st.checkbox("Je confirme la suppression de cet article", key="chk_sup_art")
                                if st.button("🗑️ Supprimer l'article", type="primary"):
                                    if conf_sup_a:
                                        try:
                                            ws_art = spreadsheet.worksheet("Articles_Evenements")
                                            cell = ws_art.find(str(choix_id_art))
                                            ws_art.delete_rows(cell.row)
                                            st.cache_data.clear()
                                            st.session_state["toast_msg"] = f"✅ Article {choix_id_art} supprimé !"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erreur : {e}")
                                    else:
                                        st.error("⚠️ Cochez la case de confirmation.")
                        else:
                            st.info("ℹ️ Veuillez sélectionner un article dans la liste.")
                    else:
                        st.warning("⚠️ Aucun article trouvé.")
            else:
                st.info("Aucun article enregistré.")

    if "toast_msg" in st.session_state:
        st.toast(st.session_state["toast_msg"], icon="🎉")
        st.success(st.session_state["toast_msg"])
        del st.session_state["toast_msg"]
