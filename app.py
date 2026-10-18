from datetime import datetime
from io import BytesIO
import math
import re
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Application de Gestion",
    page_icon="logo.png",
    layout="wide",
)

# --- INJECTION CSS DESIGN MODERN & MOBILE-FRIENDLY ---
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
        spreadsheet.worksheet("Utilisateurs").get_all_records()
    )
  except Exception:
    df_users = pd.DataFrame()

  # 3. Stock des Dons
  try:
    df_stock = pd.DataFrame(
        spreadsheet.worksheet("Dons_Stock").get_all_records()
    )
  except Exception:
    df_stock = pd.DataFrame()

  # 4. Remise de Dons
  try:
    df_distrib = pd.DataFrame(
        spreadsheet.worksheet("Remise de Dons").get_all_records()
    )
  except Exception:
    df_distrib = pd.DataFrame()

  return data, df_users, df_stock, df_distrib


try:
  client = init_connection()
  spreadsheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira")
  sheet = spreadsheet.sheet1

  data, df_users, df_stock, df_distrib = charger_donnees_depuis_sheets()
  df = pd.DataFrame(data)
  df.columns = df.columns.str.strip()

  if not df_users.empty:
    df_users.columns = df_users.columns.str.strip()
  if not df_stock.empty:
    df_stock.columns = df_stock.columns.str.strip()
  if not df_distrib.empty:
    df_distrib.columns = df_distrib.columns.str.strip()

  col_tel_detect = (
      "Numero Tèl"
      if "Numero Tèl" in df.columns
      else (df.columns[6] if len(df.columns) > 6 else "")
  )
  if col_tel_detect in df.columns:
    df[col_tel_detect] = (
        df[col_tel_detect]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )
    df[col_tel_detect] = df[col_tel_detect].apply(
        lambda x: "0" + x if len(x) == 9 and x.isdigit() else x
    )

  if "Numéro du membre" in df.columns:
    df = df[df["Numéro du membre"].astype(str).str.startswith("ONG DP")]

except Exception as e:
  st.error(f"⚠️ Erreur de connexion à Google Sheets : {e}")
  df = pd.DataFrame()
  df_users = pd.DataFrame()
  df_stock = pd.DataFrame()
  df_distrib = pd.DataFrame()

# --- ZONES & COMMUNES ---
ZONES_SUD = [
    "TREICHVILLE",
    "MARCORY",
    "KOUMASSI",
    "PORT-BOUET",
    "PORTBOUET",
    "ADJAHUI",
    "MODESTE",
    "BASSAM",
    "GRAND-BASSAM",
    "YAOU",
    "BONOUA",
    "SAMO",
    "ABOISSO",
    "ADIAKE",
    "ASSINIE",
]
ZONES_NORD = [
    "YOPOUGON",
    "ADJAME",
    "ADJAMÉ",
    "ATTECOUBE",
    "ATTÉCOUBÉ",
    "ABOBO",
    "N'DOTRE",
    "NDOTRE",
    "WILLIAMS CIVIL",
    "WILLIAMSSVILLE",
    "SONGON",
    "DABOU",
]
ZONES_CENTRE = [
    "COCODY",
    "PLATEAU",
    "BINGERVILLE",
    "ANYAMA",
    "DOKUI",
]


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
  """Calcule le matricule suivant au format strict à 4 chiffres (ex: ONG DP 0036)."""
  if df_membres.empty or "Numéro du membre" not in df_membres.columns:
    return "ONG DP 0001"

  numeros = []
  for val in df_membres["Numéro du membre"].dropna().astype(str):
    m = re.search(r"(\d+)", val)
    if m:
      numeros.append(int(m.group(1)))

  if numeros:
    prochain_num = max(numeros) + 1
  else:
    prochain_num = len(df_membres) + 1

  return f"ONG DP {prochain_num:04d}"


col_membre = (
    "Numéro du membre"
    if "Numéro du membre" in df.columns
    else (df.columns[0] if len(df.columns) > 0 else "")
)
col_enfant = (
    "Nom et Prénom de l'enfant"
    if "Nom et Prénom de l'enfant" in df.columns
    else (df.columns[1] if len(df.columns) > 1 else "")
)
col_date = (
    "Date de naissance"
    if "Date de naissance" in df.columns
    else (df.columns[2] if len(df.columns) > 2 else "")
)
col_sexe = (
    "Sexe" if "Sexe" in df.columns else (df.columns[3] if len(df.columns) > 3 else "")
)
col_ville = (
    "Ville"
    if "Ville" in df.columns
    else (df.columns[4] if len(df.columns) > 4 else "")
)
col_parent = (
    "Nom et prénoms du parent"
    if "Nom et prénoms du parent" in df.columns
    else (df.columns[5] if len(df.columns) > 5 else "")
)
col_tel = (
    "Numero Tèl"
    if "Numero Tèl" in df.columns
    else (df.columns[6] if len(df.columns) > 6 else "")
)
col_adh = (
    [c for c in df.columns if "Adh" in c][0]
    if any("Adh" in c for c in df.columns)
    else (df.columns[7] if len(df.columns) > 7 else "")
)

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
  st.markdown(
      """
      <div class="info-card">
          Veuillez saisir vos identifiants pour accéder à votre espace de travail.
      </div>
  """,
      unsafe_allow_html=True,
  )

  col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
  with col_login2:
    with st.form("form_connexion"):
      identifiant = st.text_input("Identifiant utilisateur")
      mot_de_passe = st.text_input("Mot de passe", type="password")
      btn_connexion = st.form_submit_button("Se connecter")

      if btn_connexion:
        if not df_users.empty and "Identifiant" in df_users.columns:
          match = df_users[
              (df_users["Identifiant"].astype(str) == identifiant.strip())
              & (df_users["Mot_de_passe"].astype(str) == mot_de_passe.strip())
          ]
          if not match.empty:
            st.session_state["user_connected"] = True
            st.session_state["user_info"] = match.iloc[0].to_dict()
            st.toast(
                f"Bienvenue {st.session_state['user_info'].get('Nom_Responsable', '')} !",
                icon="👋",
            )
            st.rerun()
          else:
            st.error("❌ Identifiant ou mot de passe incorrect.")
        else:
          if identifiant == "admin" and mot_de_passe == "admin123":
            st.session_state["user_connected"] = True
            st.session_state["user_info"] = {
                "Nom_Responsable": "Direction DSI",
                "Zone": "Vue Globale",
            }
            st.rerun()
          else:
            st.error("❌ Identifiant ou mot de passe incorrect.")

# --- APPLICATION PRINCIPALE ---
else:
  user_info = st.session_state["user_info"]

  # Détection rôle / zone
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
  st.sidebar.markdown(
      '<div class="sidebar-menu-title">📂 MENU PRINCIPAL</div>',
      unsafe_allow_html=True,
  )
  st.sidebar.markdown(f"### 👤 **{user_nom}**")
  st.sidebar.caption(f"📌 **Espace : {user_zone}**")
  st.sidebar.markdown("---")

  if is_compta:
    pages = ["📦 Stock des Dons", "🎁 Remise de Dons"]
    if st.session_state["current_page"] not in pages:
      st.session_state["current_page"] = pages[0]
  elif is_dsi:
    pages = [
        "📊 Tableau de Bord",
        "➕ Enregistrer un Membre",
        "✏️ Modifier / Supprimer",
        "📋 Liste & Répertoire",
        "📦 Stock des Dons",
        "🎁 Remise de Dons",
    ]
  else:
    pages = [
        "📊 Tableau de Bord",
        "➕ Enregistrer un Membre",
        "✏️ Modifier / Supprimer",
        "📋 Liste & Répertoire",
    ]

  st.sidebar.markdown("**NAVIGATION**")
  for page in pages:
    is_selected = st.session_state["current_page"] == page
    btn_style = "nav-btn-active" if is_selected else "nav-btn-inactive"

    st.sidebar.markdown(f'<div class="{btn_style}">', unsafe_allow_html=True)
    if st.sidebar.button(page, key=f"nav_{page}", use_container_width=True):
      st.session_state["current_page"] = page
      st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

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
      total_garcons = (
          len(df_f[df_f[col_sexe].astype(str).str.upper() == "M"])
          if col_sexe in df_f.columns
          else 0
      )
      total_filles = (
          len(df_f[df_f[col_sexe].astype(str).str.upper() == "F"])
          if col_sexe in df_f.columns
          else 0
      )
      total_actifs = (
          len(df_f[df_f[col_adh].astype(str).str.upper() == "OK"])
          if col_adh in df_f.columns
          else 0
      )

      k1, k2, k3, k4 = st.columns(4)
      with k1:
        st.markdown(
            f'<div class="kpi-card"><div'
            ' class="kpi-title">Membres</div><div'
            f' class="kpi-value">{total_membres}</div></div>',
            unsafe_allow_html=True,
        )
      with k2:
        st.markdown(
            f'<div class="kpi-card" style="border-left-color: #17a2b8;"><div'
            ' class="kpi-title">Adhésions OK</div><div'
            f' class="kpi-value">{total_actifs}</div></div>',
            unsafe_allow_html=True,
        )
      with k3:
        st.markdown(
            f'<div class="kpi-card" style="border-left-color: #007bff;"><div'
            ' class="kpi-title">Garçons</div><div'
            f' class="kpi-value">{total_garcons}</div></div>',
            unsafe_allow_html=True,
        )
      with k4:
        st.markdown(
            f'<div class="kpi-card" style="border-left-color: #e83e8c;"><div'
            ' class="kpi-title">Filles</div><div'
            f' class="kpi-value">{total_filles}</div></div>',
            unsafe_allow_html=True,
        )

      st.markdown("---")
      with st.container(border=True):
        st.markdown("### 🕒 Derniers enfants enregistrés")
        cols_a_afficher = [
            c
            for c in df_f.columns
            if c != "Zone_Geographique"
            and c in df.columns
            and not df[c].isnull().all()
        ]
        st.dataframe(df_f[cols_a_afficher].tail(5), use_container_width=True)
    else:
      st.warning("⚠️ Aucun membre trouvé pour cette zone.")

  # ==========================================
  # 2. ENREGISTRER UN MEMBRE
  # ==========================================
  elif menu == "➕ Enregistrer un Membre":
    st.subheader("📝 Nouvel Enregistrement")

    st.markdown(
        f"""
        <div class="info-card">
            Saisie d'un nouvel enfant rattaché à l'espace : <strong>{choix_zone_label}</strong>.
        </div>
    """,
        unsafe_allow_html=True,
    )

    liste_communes = [
        "ABOISSO",
        "ABOBO",
        "ADIAKE",
        "ADJAME",
        "ADJAHUI",
        "ALÉPÉ",
        "ANYAMA",
        "ASSINIE",
        "ATTECOUBE",
        "BINGERVILLE",
        "BONOUA",
        "DABOU",
        "DALOA",
        "DIVO",
        "DOKUI",
        "GAGNOA",
        "GRAND-BASSAM",
        "GUIBEROUA",
        "ISSIA",
        "KOUMASSI",
        "MARCORY",
        "MODESTE",
        "N'DOTRE",
        "OUMÉ",
        "PLATEAU",
        "PORT-BOUET",
        "SAN-PÉDRO",
        "SAMO",
        "SONGON",
        "TREICHVILLE",
        "WILLIAMS CIVIL",
        "YAMOUSSOUKRO",
        "YAOU",
        "YOPOUGON",
        "AUTRE (Préciser ci-dessous)",
    ]

    matricule_auto = obtenir_prochain_matricule(df)

    with st.container(border=True):
      with st.form("form_membre_principal", clear_on_submit=True):
        st.markdown("##### 👶 Informations de l'enfant")
        c1, c2 = st.columns(2)
        with c1:
          numero_membre = st.text_input(
              "Numéro du membre (Auto)", value=matricule_auto, disabled=True
          )
          nom_enfant = st.text_input(
              "Nom et Prénom de l'enfant (Ex: KOUASSI JEAN)"
          ).upper()
        with c2:
          sexe = st.selectbox("Sexe", ["M", "F"])
          date_naissance = st.text_input("Date de naissance / Âge")

        ville_choix = st.selectbox(
            "Commune / Ville de résidence", liste_communes
        )
        ville_autre = st.text_input(
            "Si 'AUTRE' sélectionné, précisez la ville :"
        ).upper()

        st.markdown("---")
     