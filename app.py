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

# --- FONCTION SECURISEE CONVERSION NUMERIQUE ---
def safe_int_convert(val, default=0):
    if pd.isna(val) or val is None:
        return default
    val_str = str(val).strip()
    match = re.search(r'(\d+)', val_str)
    if match:
        return int(match.group(1))
    return default

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
        df_users = pd.DataFrame(spreadsheet.worksheet("Utilisateurs").get_all_records())
    except Exception:
        df_users = pd.DataFrame()

    # 3. Stock des Dons
    try:
        df_stock = pd.DataFrame(spreadsheet.worksheet("Dons_Stock").get_all_records())
    except Exception:
        df_stock = pd.DataFrame()

    # 4. Remise de Dons
    try:
        df_distrib = pd.DataFrame(spreadsheet.worksheet("Remise de Dons").get_all_records())
    except Exception:
        df_distrib = pd.DataFrame()

    # 5. Cotisations (Avec vérification automatique des en-têtes)
    try:
        ws_cotiz = spreadsheet.worksheet("Cotisations")
        val_cotiz = ws_cotiz.get_all_values()
        headers_cotiz = ["ID_Cotiz", "Date", "ID_Membre", "Nom_Enfant", "Nom_Parent", "Type_Paiement", "Montant_Verse", "Statut", "Commentaire", "Enregistre_Par"]
        if not val_cotiz or val_cotiz[0][0] != "ID_Cotiz":
            ws_cotiz.insert_row(headers_cotiz, 1)
        df_cotiz = pd.DataFrame(ws_cotiz.get_all_records())
    except Exception:
        df_cotiz = pd.DataFrame()

    # 6. Articles & Goodies Événements (Avec vérification automatique des en-têtes)
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

# --- ÉCRAN DE CONNEXION ---
if not st.session_state["user_connected"]:
    st.subheader("🔐 Connexion au Portail ONG DIEU POURVOIRA")
    st.markdown("""
      <div class="info-card">
          Veuillez saisir vos identifiants pour accéder à votre espace de travail.
      </div>
  """, unsafe_allow_html=True)

    col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
    with col_login2:
        with st.form("form_connexion"):
            identifiant = st.text_input("Identifiant utilisateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")
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

# --- APPLICATION PRINCIPALE ---
else:
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

    # --- BARRE LATÉRALE - MENU PERSONNALISÉ ---
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

    # Filtrage géographique
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
    # 1. TABLEAU DE BORD MODERNE
    # ==========================================
    if menu == "📊 Tableau de Bord":
        st.subheader(f"📈 Vue Synthétique - {choix_zone_label}")

        if not df_f.empty:
            total_membres = len(df_f)
            total_garcons = len(df_f[df_f[col_sexe].astype(str).str.upper() == "M"]) if col_sexe in df_f.columns else 0
            total_filles = len(df_f[df_f[col_sexe].astype(str).str.upper() == "F"]) if col_sexe in df_f.columns else 0
            total_actifs = len(df_f[df_f[col_adh].astype(str).str.upper() == "OK"]) if col_adh in df_f.columns else 0

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-title">Membres</div><div class="kpi-value">{total_membres}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="kpi-card" style="border-left-color: #17a2b8;"><div class="kpi-title">Adhésions OK</div><div class="kpi-value">{total_actifs}</div></div>', unsafe_allow_html=True)
            with k3:
                st.markdown(f'<div class="kpi-card" style="border-left-color: #007bff;"><div class="kpi-title">Garçons</div><div class="kpi-value">{total_garcons}</div></div>', unsafe_allow_html=True)
            with k4:
                st.markdown(f'<div class="kpi-card" style="border-left-color: #e83e8c;"><div class="kpi-title">Filles</div><div class="kpi-value">{total_filles}</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            with st.container(border=True):
                st.markdown("### 🕒 Derniers enfants enregistrés")
                cols_a_afficher = [c for c in df_f.columns if c != "Zone_Geographique" and c in df.columns and not df[c].isnull().all()]
                st.dataframe(df_f[cols_a_afficher].tail(5), use_container_width=True)
        else:
            st.warning("⚠️ Aucun membre trouvé pour cette zone.")

    # ==========================================
    # 2. ENREGISTRER UN MEMBRE
    # ==========================================
    elif menu == "➕ Enregistrer un Membre":
        st.subheader("📝 Nouvel Enregistrement")
        st.markdown(f'<div class="info-card">Saisie d\'un nouvel enfant rattaché à l\'espace : <strong>{choix_zone_label}</strong>.</div>', unsafe_allow_html=True)

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
                    date_naissance = st.text_input("Date de naissance / Âge")

                ville_choix = st.selectbox("Commune / Ville de résidence", liste_communes)
                ville_autre = st.text_input("Si 'AUTRE' sélectionné, précisez la ville :").upper()

                st.markdown("---")
                st.markdown("##### 👪 Informations du parent & Statut")
                c3, c4 = st.columns(2)
                with c3:
                    nom_parent = st.text_input("Nom et prénoms du parent (Ex: KOUASSI MARC)").upper()
                    numero_tel = st.text_input("Numéro de téléphone du parent")
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
                        st.error("⚠️ Veuillez renseigner le nom de l'enfant et du parent.")

    # ==========================================
    # 3. MODIFIER / SUPPRIMER
    # ==========================================
    elif menu == "✏️ Modifier / Supprimer":
        st.subheader(f"✏️ Modifier ou Supprimer - {choix_zone_label}")

        if not df_f.empty and col_membre in df_f.columns:
            if "recherche_edit" not in st.session_state:
                st.session_state["recherche_edit"] = ""

            recherche_edit = st.text_input("🔍 Rechercher dans votre zone...", key="recherche_edit")
            if recherche_edit:
                mask_edit = df_f.astype(str).apply(lambda row: row.str.contains(recherche_edit, case=False, na=False).any(), axis=1)
                df_edit_filtered = df_f[mask_edit]
            else:
                df_edit_filtered = df_f

            if not df_edit_filtered.empty:
                liste_membres = df_edit_filtered[col_membre].astype(str).tolist()
                options_select = ["-- Sélectionnez un membre --"] + liste_membres

                choix_membre = st.selectbox(
                    "Sélectionner le membre", 
                    options_select, 
                    format_func=lambda m: m if m == "-- Sélectionnez un membre --" else f"{m} - {df_edit_filtered[df_edit_filtered[col_membre].astype(str) == m][col_enfant].values[0]}" if col_enfant in df_edit_filtered.columns else m
                )

                if choix_membre != "-- Sélectionnez un membre --":
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

                                btn_modifier = st.form_submit_button("💾 Mettre à jour")
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
                                        st.session_state["recherche_edit"] = ""
                                        st.cache_data.clear()
                                        st.session_state["toast_msg"] = f"✅ Membre {choix_membre} mis à jour !"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Erreur : {e}")
                        else:
                            st.warning(f"⚠️ Suppression définitive du membre {choix_membre}")
                            confirmer = st.checkbox("Je confirme la suppression définitive")
                            if st.button("🗑️ Confirmer la suppression", type="primary"):
                                if confirmer:
                                    try:
                                        cell = sheet.find(str(choix_membre))
                                        sheet.delete_rows(cell.row)
                                        st.session_state["recherche_edit"] = ""
                                        st.cache_data.clear()
                                        st.session_state["toast_msg"] = f"✅ Membre {choix_membre} supprimé !"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Erreur : {e}")
                                else:
                                    st.error("⚠️ Cochez la case de confirmation.")
                else:
                    st.info("ℹ️ Veuillez rechercher et sélectionner un membre dans la liste ci-dessus pour effectuer une modification ou une suppression.")
            else:
                st.warning("⚠️ Aucun membre trouvé.")
        else:
            st.info("Aucun membre disponible.")

  # ==========================================
  # 4. LISTE & REPERTOIRE + CARTES
  # ==========================================
    elif menu == "📋 Liste & Répertoire":
        st.subheader(f"📋 Répertoire & Cartes - {choix_zone_label}")
        recherche = st.text_input("🔍 Rechercher un membre...", key="recherche_liste")

        if not df_f.empty:
            if recherche:
                mask = df_f.astype(str).apply(lambda row: row.str.contains(recherche, case=False, na=False).any(), axis=1)
                df_affiche = df_f[mask]
                st.info(f"ℹ️ Résultats trouvés : {len(df_affiche)}")
            else:
                df_affiche = df_f

            tab_liste, tab_cartes = st.tabs(["📋 Liste Générale", "🪪 Cartes d'Adhérents (Modèles Thématiques ONG)"])

            with tab_liste:
                total_lignes = len(df_affiche)
                if total_lignes > 0:
                    col_pg1, col_pg2 = st.columns([1, 2])
                    with col_pg1:
                        lignes_par_page = st.selectbox("Lignes par page", [10, 25, 50, 100], index=0, key="lignes_page")
                    total_pages = math.ceil(total_lignes / lignes_par_page)
                    with col_pg2:
                        page_actuelle = st.selectbox("Sélectionner la page", range(1, total_pages + 1), format_func=lambda x: f"Page {x} / {total_pages}", key="select_page")

                    debut = (page_actuelle - 1) * lignes_par_page
                    fin = min(debut + lignes_par_page, total_lignes)
                    df_page = df_affiche.iloc[debut:fin]

                    with st.container(border=True):
                        cols_affichage = [c for c in df_page.columns if c != "Zone_Geographique"]
                        st.dataframe(df_page[cols_affichage], use_container_width=True)

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

            with tab_cartes:
                st.markdown("##### 🪪 Génération de Cartes aux couleurs officielles de l'ONG")
                if col_adh in df_affiche.columns:
                    df_ok = df_affiche[df_affiche[col_adh].astype(str).str.upper().str.strip() == "OK"]
                else:
                    df_ok = pd.DataFrame()

                if not df_ok.empty:
                    modele_carte = st.radio("🎨 Choisissez le modèle de carte officiel :", ["Modèle 1 : Classique Officiel avec Logo (Vert, Blanc & Orange)", "Modèle 2 : Moderne & Épuré avec En-tête Logo (Design épuré)"], horizontal=False)

                    c_sel, c_img = st.columns([2, 1])
                    with c_sel:
                        membre_selectionne = st.selectbox("1. Sélectionnez l'enfant :", df_ok[col_membre].astype(str).tolist(), format_func=lambda m: f"{m} - {df_ok[df_ok[col_membre].astype(str) == m][col_enfant].values[0]}")
                    with c_img:
                        photo_file = st.file_uploader("2. Photo de l'enfant", type=["jpg", "png", "jpeg"])

                    if membre_selectionne:
                        row_m = df_ok[df_ok[col_membre].astype(str) == membre_selectionne].iloc[0]
                        if photo_file is not None:
                            img_src = f"data:image/png;base64,{base64.b64encode(photo_file.getvalue()).decode()}"
                        else:
                            img_src = "https://via.placeholder.com/130x150/e9ecef/6c757d?text=PHOTO"

                        logo_path = "logo.png"
                        if os.path.exists(logo_path):
                            with open(logo_path, "rb") as f_logo:
                                logo_b64 = base64.b64encode(f_logo.read()).decode()
                            logo_src = f"data:image/png;base64,{logo_b64}"
                        else:
                            logo_src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="%231e7e34"/><path d="M50 25 L60 45 L80 45 L65 60 L70 80 L50 68 L30 80 L35 60 L20 45 L40 45 Z" fill="%23ff7f00"/></svg>'

                        nom_complet = str(row_m.get(col_enfant, "")).upper().split(" ", 1)
                        nom_e = nom_complet[0]
                        prenom_e = nom_complet[1] if len(nom_complet) > 1 else ""
                        nom_p = str(row_m.get(col_parent, "")).upper()
                        num_m = str(row_m.get(col_membre, ""))
                        date_adh = str(row_m.get(df.columns[8] if len(df.columns) > 8 else "", "")).split(" ")[0]
                        tel_p = str(row_m.get(col_tel, ""))

                        if modele_carte.startswith("Modèle 1"):
                            html_carte = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                            <meta charset="utf-8">
                            <style>
                                @media print {{
                                    body {{ background: none !important; }}
                                    .no-print {{ display: none !important; }}
                                    .card-box {{ box-shadow: none !important; border: 3px solid #1e7e34 !important; }}
                                }}
                                .print-btn {{
                                    background: linear-gradient(90deg, #28a745 0%, #1e7e34 100%);
                                    color: white;
                                    border: none;
                                    padding: 12px 28px;
                                    font-size: 14px;
                                    font-weight: bold;
                                    border-radius: 10px;
                                    cursor: pointer;
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                                    margin-top: 15px;
                                    transition: all 0.3s ease;
                                }}
                                .print-btn:hover {{
                                    background: linear-gradient(90deg, #1e7e34 0%, #155724 100%);
                                }}
                            </style>
                            </head>
                            <body style="background-color: transparent; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 5px;">
                                <div style="display: inline-block;">
                                    <div class="card-box" style="width: 620px; height: 390px; background: #ffffff; border-radius: 16px; border: 3px solid #1e7e34; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: left; overflow: hidden;">
                                        <div style="position: absolute; top: 0; left: 0; right: 0; height: 14px; background: linear-gradient(90deg, #1e7e34 0%, #28a745 50%, #ff7f00 100%);"></div>
                                        <div style="text-align: center; padding-top: 20px;">
                                            <div style="font-size: 18px; font-weight: 900; color: #1e7e34; letter-spacing: 1px;">ONG DIEU POURVOIRA</div>
                                            <div style="background: #1e7e34; color: white; padding: 3px 20px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-block; margin-top: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.15);">CARTE DE MEMBRE OFFICIELLE</div>
                                        </div>
                                        <div style="position: absolute; left: 35px; top: 85px; width: 130px; height: 150px; border: 3px solid #1e7e34; border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                                            <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
                                        </div>
                                        <div style="position: absolute; left: 65px; top: 242px; width: 70px; height: 70px;">
                                            <img src="{logo_src}" style="width: 100%; height: 100%; object-fit: contain;">
                                        </div>
                                        <div style="position: absolute; left: 185px; top: 85px; width: 415px; font-size: 13px; color: #212529; line-height: 25px;">
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">Nom de l'enfant :</span> <span style="font-weight: 800; color: #000;">{nom_e}</span></div>
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">Prénom de l'enfant :</span> <span style="font-weight: 800; color: #000;">{prenom_e}</span></div>
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">Parent :</span> <span style="font-weight: 700; color: #333; font-size: 12px;">{nom_p}</span></div>
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">N° Membre :</span> <span style="color: #1e7e34; font-weight: 900; font-size: 14px;">{num_m}</span></div>
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">Date d'adhésion :</span> <span style="font-weight: 700; color: #000;">{date_adh}</span></div>
                                            <div style="border-bottom: 1px dotted #ccc; padding-bottom: 1px;"><span style="color: #6c757d; display: inline-block; width: 145px;">Contact parent :</span> <span style="font-weight: 700; color: #000;">{tel_p}</span></div>
                                        </div>
                                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(90deg, #1e7e34 0%, #0b4d1d 100%); color: white; padding: 8px 12px; font-size: 10px; text-align: center; font-weight: bold;">
                                            ❤️ Ensemble aidons les enfants atteints de Paralysie cérébrale ❤️<br>
                                            <span style="font-weight: normal; color: #e2f0d9; font-size: 9px;">📞 Contact : +225 77 71 04 41 8 / 05 86 99 73 27</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="no-print">
                                    <button class="print-btn" onclick="window.print()">🖨️ Lancer l'impression / Enregistrer en PDF</button>
                                </div>
                            </body>
                            </html>
                            """
                        else:
                            html_carte = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                            <meta charset="utf-8">
                            <style>
                                @media print {{
                                    body {{ background: none !important; }}
                                    .no-print {{ display: none !important; }}
                                    .card-box {{ box-shadow: none !important; border: 3px solid #ff7f00 !important; }}
                                }}
                                .print-btn {{
                                    background: linear-gradient(90deg, #28a745 0%, #1e7e34 100%);
                                    color: white;
                                    border: none;
                                    padding: 12px 28px;
                                    font-size: 14px;
                                    font-weight: bold;
                                    border-radius: 10px;
                                    cursor: pointer;
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                                    margin-top: 15px;
                                    transition: all 0.3s ease;
                                }}
                                .print-btn:hover {{
                                    background: linear-gradient(90deg, #1e7e34 0%, #155724 100%);
                                }}
                            </style>
                            </head>
                            <body style="background-color: transparent; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 5px;">
                                <div style="display: inline-block;">
                                    <div class="card-box" style="width: 620px; height: 390px; background: linear-gradient(135deg, #f9fffb 0%, #f1f8f3 100%); border-radius: 16px; border: 3px solid #ff7f00; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: left; overflow: hidden;">
                                        <div style="background: #1e7e34; color: white; padding: 8px 15px; display: flex; align-items: center; justify-content: space-between; border-bottom: 4px solid #ff7f00;">
                                            <img src="{logo_src}" style="height: 42px; width: auto; background: #fff; padding: 2px; border-radius: 6px;">
                                            <div style="text-align: center; flex-grow: 1;">
                                                <div style="font-size: 17px; font-weight: 900; letter-spacing: 1.5px;">ONG DIEU POURVOIRA</div>
                                                <div style="font-size: 10px; color: #e2f0d9; font-weight: bold;">CARTE D'ADHÉRENT OFFICIELLE</div>
                                            </div>
                                            <div style="width: 42px;"></div>
                                        </div>
                                        <div style="position: absolute; left: 35px; top: 90px; width: 130px; height: 155px; border: 3px solid #ff7f00; border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                                            <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
                                        </div>
                                        <div style="position: absolute; left: 185px; top: 90px; width: 415px; font-size: 13px; color: #212529; line-height: 25px;">
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">Nom :</span> <span style="font-weight: 800; color: #000;">{nom_e}</span></div>
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">Prénom :</span> <span style="font-weight: 800; color: #000;">{prenom_e}</span></div>
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">Parent :</span> <span style="font-weight: 700; color: #333; font-size: 12px;">{nom_p}</span></div>
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">N° Membre :</span> <span style="color: #ff7f00; font-weight: 900; font-size: 14px;">{num_m}</span></div>
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">Adhésion :</span> <span style="font-weight: 700; color: #000;">{date_adh}</span></div>
                                            <div style="border-bottom: 1px solid #d4edda; padding-bottom: 1px;"><span style="color: #1e7e34; font-weight: bold; display: inline-block; width: 145px;">Contact :</span> <span style="font-weight: 700; color: #000;">{tel_p}</span></div>
                                        </div>
                                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: #1e7e34; color: white; padding: 8px 12px; font-size: 10px; text-align: center; font-weight: bold;">
                                            ❤️ Ensemble aidons les enfants atteints de Paralysie cérébrale ❤️<br>
                                            <span style="font-weight: normal; color: #ff7f00; font-size: 9px;">📞 Contact : +225 77 71 04 41 8 / 05 86 99 73 27</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="no-print">
                                    <button class="print-btn" onclick="window.print()">🖨️ Lancer l'impression / Enregistrer en PDF</button>
                                </div>
                            </body>
                            </html>
                            """

                        st.components.v1.html(html_carte, height=480)
                else:
                    st.warning("⚠️ Aucun membre actif (Adhésion OK) trouvé.")
        else:
            st.warning("⚠️ Aucune donnée disponible.")

    # ==========================================
    # 5. STOCK DES DONS
    # ==========================================
    elif menu == "📦 Stock des Dons":
        st.subheader("📦 Stock & Réception des Dons")
        tab_ajout_stock, tab_modif_stock = st.tabs(["➕ Enregistrer un Don", "✏️ Modifier / Supprimer un Don du Stock"])

        with tab_ajout_stock:
            with st.container(border=True):
                with st.form("form_entree_don", clear_on_submit=True):
                    type_don = st.selectbox("Type de Don", ["Matériel Médical / Fauteuil", "Produits d'Hygiène / Couches", "Vivres / Alimentation", "Vêtements", "Don Financier (FCFA)", "Autre"])
                    designation = st.text_input("Désignation (Ex: Fauteuils Roulants Enfant)").upper()
                    donateur = st.text_input("Donateur / Partenaire").upper()
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
                    choix_id_don = st.selectbox("Sélectionner le Don à modifier/supprimer", df_stock["ID_Don"].astype(str).tolist(), format_func=lambda d: f"{d} - {df_stock[df_stock['ID_Don'].astype(str) == d]['Designation'].values[0]}")
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
                        conf_sup = st.checkbox("Je confirme la suppression de ce don")
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
                st.info("Aucun stock enregistré pour le moment.")

        st.markdown("---")
        st.markdown("### 📊 État actuel des Stocks")
        with st.container(border=True):
            if not df_stock.empty:
                st.dataframe(df_stock, use_container_width=True)
            else:
                st.info("Aucun stock pour le moment.")

    # ==========================================
    # 6. REMISE DE DONS
    # ==========================================
    elif menu == "🎁 Remise de Dons":
        st.subheader("🎁 Attribution & Remise de Don aux Enfants")
        if not df.empty and not df_stock.empty:
            if "Stock_Actuel" in df_stock.columns:
                df_stock_dispo = df_stock[df_stock["Stock_Actuel"].apply(safe_int_convert) > 0]
            else:
                df_stock_dispo = df_stock

            if not df_stock_dispo.empty:
                with st.container(border=True):
                    with st.form("form_remise_don", clear_on_submit=True):
                        liste_enfants = df[col_membre].astype(str).tolist()
                        choix_enfant_don = st.selectbox("1. Enfant bénéficiaire", liste_enfants, format_func=lambda m: f"{m} - {df[df[col_membre].astype(str) == m][col_enfant].values[0]}")

                        liste_dons_dispo = df_stock_dispo["ID_Don"].astype(str).tolist()
                        choix_don = st.selectbox("2. Don à remettre", liste_dons_dispo, format_func=lambda d: f"{d} - {df_stock_dispo[df_stock_dispo['ID_Don'].astype(str) == d]['Designation'].values[0]} (Reste: {df_stock_dispo[df_stock_dispo['ID_Don'].astype(str) == d]['Stock_Actuel'].values[0]})")

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
                st.warning("⚠️ Aucun don disponible en stock.")
        else:
            st.warning("⚠️ Données insuffisantes pour effectuer une remise.")

        st.markdown("---")
        st.markdown("### 📋 Historique global des Remises")
        with st.container(border=True):
            if not df_distrib.empty:
                st.dataframe(df_distrib, use_container_width=True)
            else:
                st.info("Aucune distribution enregistrée pour le moment.")

    # ==========================================
    # 7. SUIVI DES COTISATIONS & CARTES
    # ==========================================
    elif menu == "💳 Suivi Cotisations":
        st.subheader("💳 Suivi des Cotisations et Frais de Carte")
        tab_cotiz_saisie, tab_cotiz_suivi, tab_cotiz_modif = st.tabs(["➕ Enregistrer un Paiement", "📊 Tableau de Bord & Impayés", "✏️ Modifier / Supprimer un Paiement"])

        with tab_cotiz_saisie:
            if not df.empty:
                with st.container(border=True):
                    with st.form("form_cotisation", clear_on_submit=True):
                        st.markdown("##### 💰 Saisie d'une cotisation ou d'un frais de carte")
                        liste_membres_cotiz = df[col_membre].astype(str).tolist()
                        membre_c = st.selectbox("Membre concerné", liste_membres_cotiz, format_func=lambda m: f"{m} - {df[df[col_membre].astype(str) == m][col_enfant].values[0]}")

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
                st.warning("⚠️ Aucun membre enregistré.")

        with tab_cotiz_suivi:
            st.markdown("### 📋 Historique & États des Cotisations")
            if not df_cotiz.empty and "ID_Cotiz" in df_cotiz.columns:
                st.dataframe(df_cotiz, use_container_width=True)
                output_c = BytesIO()
                with pd.ExcelWriter(output_c, engine="xlsxwriter") as writer:
                    df_cotiz.to_excel(writer, index=False, sheet_name="Cotisations")
                excel_c_data = output_c.getvalue()

                st.download_button(
                    label="📥 Exporter le rapport des cotisations (.xlsx)",
                    data=excel_c_data,
                    file_name="Rapport_Cotisations_ONG.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.info("Aucune cotisation enregistrée pour le moment.")

        with tab_cotiz_modif:
            st.markdown("### ✏️ Modifier ou Supprimer un Paiement de Cotisation")
            if not df_cotiz.empty and "ID_Cotiz" in df_cotiz.columns:
                with st.container(border=True):
                    choix_id_cotiz = st.selectbox("Sélectionner le paiement à modifier/supprimer", df_cotiz["ID_Cotiz"].astype(str).tolist(), format_func=lambda c: f"{c} - {df_cotiz[df_cotiz['ID_Cotiz'].astype(str) == c]['Nom_Enfant'].values[0]} ({df_cotiz[df_cotiz['ID_Cotiz'].astype(str) == c]['Type_Paiement'].values[0]} : {df_cotiz[df_cotiz['ID_Cotiz'].astype(str) == c]['Montant_Verse'].values[0]} FCFA)")
                    cotiz_ligne = df_cotiz[df_cotiz["ID_Cotiz"].astype(str) == choix_id_cotiz].iloc[0]

                    action_cotiz = st.radio("Action sur ce paiement", ["Modifier", "Supprimer définitivement"], horizontal=True, key="radio_act_cotiz")

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
                                    st.session_state["toast_msg"] = f"✅ Paiement {choix_id_cotiz} mis à jour avec succès !"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur : {e}")
                    else:
                        conf_sup_c = st.checkbox("Je confirme la suppression de ce paiement", key="chk_sup_cot")
                        if st.button("🗑️ Supprimer définitivement ce paiement", type="primary"):
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
                                st.error("⚠️ Veuillez cocher la case de confirmation.")
            else:
                st.info("Aucun paiement de cotisation enregistré pour le moment.")

    # ==========================================
    # 8. ARTICLES & GOODIES D'ÉVÉNEMENTS
    # ==========================================
    elif menu == "🛍️ Articles & Goodies":
        st.subheader("🛍️ Gestion des Articles, T-shirts et Goodies d'Événements")
        tab_art_vente, tab_art_suivi, tab_art_modif = st.tabs(["➕ Enregistrer une Vente / Attribution", "📊 Suivi & Inventaire", "✏️ Modifier / Supprimer un Article"])

        with tab_art_vente:
            if not df.empty:
                with st.container(border=True):
                    with st.form("form_article_event", clear_on_submit=True):
                        st.markdown("##### 🏷️ Attribuer un article ou goodies à un membre")
                        liste_membres_art = df[col_membre].astype(str).tolist()
                        membre_a = st.selectbox("Membre bénéficiaire / acheteur", liste_membres_art, format_func=lambda m: f"{m} - {df[df[col_membre].astype(str) == m][col_enfant].values[0]}")

                        nom_article = st.text_input("Nom de l'article / Goodies (Ex: T-shirt Gala 2026, Casquette, Badge...)").upper()
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
                                    st.session_state["toast_msg"] = f"✅ Article '{nom_article}' enregistré avec succès !"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur : {e}")
                            else:
                                st.error("⚠️ Veuillez saisir le nom de l'article.")
            else:
                st.warning("⚠️ Aucun membre enregistré.")

        with tab_art_suivi:
            st.markdown("### 📋 Suivi des Ventes & Goodies")
            if not df_articles.empty and "ID_Art" in df_articles.columns:
                st.dataframe(df_articles, use_container_width=True)
                output_a = BytesIO()
                with pd.ExcelWriter(output_a, engine="xlsxwriter") as writer:
                    df_articles.to_excel(writer, index=False, sheet_name="Articles")
                excel_a_data = output_a.getvalue()

                st.download_button(
                    label="📥 Exporter le suivi des articles (.xlsx)",
                    data=excel_a_data,
                    file_name="Rapport_Articles_Evenements.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.info("Aucun article enregistré pour le moment.")

        with tab_art_modif:
            st.markdown("### ✏️ Modifier ou Supprimer un Article / Goodies")
            if not df_articles.empty and "ID_Art" in df_articles.columns:
                with st.container(border=True):
                    choix_id_art = st.selectbox("Sélectionner l'article à modifier/supprimer", df_articles["ID_Art"].astype(str).tolist(), format_func=lambda a: f"{a} - {df_articles[df_articles['ID_Art'].astype(str) == a]['Nom_Enfant'].values[0]} ({df_articles[df_articles['ID_Art'].astype(str) == a]['Nom_Article'].values[0]})")
                    art_ligne = df_articles[df_articles["ID_Art"].astype(str) == choix_id_art].iloc[0]

                    action_art = st.radio("Action sur cet article", ["Modifier", "Supprimer définitivement"], horizontal=True, key="radio_act_art")

                    if action_art == "Modifier":
                        with st.form("form_modif_art"):
                            nouveau_nom_art = st.text_input("Nom de l'article", value=str(art_ligne.get("Nom_Article", ""))).upper()
                            nouvelle_qte = st.number_input("Quantité", min_value=1, value=safe_int_convert(art_ligne.get("Quantite", 1), default=1))
                            nouveau_montant_art = st.number_input("Montant Total (FCFA)", min_value=0, value=safe_int_convert(art_ligne.get("Montant_Total", 0)))
                            nouveau_stat_reg = st.selectbox("Statut du paiement", ["Payé", "Avance", "Impayé"], index=["Payé", "Avance", "Impayé"].index(str(art_ligne.get("Statut_Reglement", "Payé"))) if str(art_ligne.get("Statut_Reglement", "Payé")) in ["Payé", "Avance", "Impayé"] else 0)
                            nouveau_stat_liv = st.selectbox("Statut de remise", ["Livré / Remis", "En attente de retrait"], index=0 if str(art_ligne.get("Statut_Livraison", "")).startswith("Livré") else 1)

                            if st.form_submit_button("💾 Mettre à jour l'article"):
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
                                    st.session_state["toast_msg"] = f"✅ Article {choix_id_art} mis à jour avec succès !"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur : {e}")
                    else:
                        conf_sup_a = st.checkbox("Je confirme la suppression de cet article", key="chk_sup_art")
                        if st.button("🗑️ Supprimer définitivement cet article", type="primary"):
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
                                st.error("⚠️ Veuillez cocher la case de confirmation.")
            else:
                st.info("Aucun article enregistré pour le moment.")

    if "toast_msg" in st.session_state:
        st.toast(st.session_state["toast_msg"], icon="🎉")
        st.success(st.session_state["toast_msg"])
        del st.session_state["toast_msg"]
