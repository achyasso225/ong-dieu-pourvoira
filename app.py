from datetime import datetime
from io import BytesIO
import math
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
    
    /* Transformer le bouton natif du menu en haut (hamburger/croix) en un joli petit carré stylisé */
    [data-testid="collapsedControl"] {
        background-color: #1a1f2c !important;
        border: 2px solid #28a745 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #28a745 !important;
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

    /* Boutons personnalisés de la Sidebar */
    div[data-testid="stSidebar"] {
        background-color: #131722;
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

# --- SCRIPT JAVASCRIPT POUR FERMER AUTOMATIQUEMENT LE MENU SUR MOBILE ---
st.markdown(
    """
    <script>
    // Écoute les clics sur les boutons de la barre latérale pour refermer le menu sur smartphone
    const observer = new MutationObserver(() => {
        const sidebarButtons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
        sidebarButtons.forEach(btn => {
            if (!btn.hasAttribute('data-auto-close-bound')) {
                btn.setAttribute('data-auto-close-bound', 'true');
                btn.addEventListener('click', () => {
                    // Si on est sur un écran mobile (largeur <= 768px), on simule un clic sur l'arrière-plan pour fermer la sidebar
                    if (window.innerWidth <= 768) {
                        setTimeout(() => {
                            const mainOverlay = window.parent.document.querySelector('.main');
                            if (mainOverlay) mainOverlay.click();
                        }, 150);
                    }
                });
            }
        });
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


# --- CONNEXION AUTOMATIQUE À GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


try:
  client = init_connection()
  spreadsheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira")
  sheet = spreadsheet.sheet1

  # Lecture des membres
  data = sheet.get_all_records(head=9)
  df = pd.DataFrame(data)
  df.columns = df.columns.str.strip()

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

  # Lecture des utilisateurs
  try:
    sheet_users = spreadsheet.worksheet("Utilisateurs")
    df_users = pd.DataFrame(sheet_users.get_all_records())
    df_users.columns = df_users.columns.str.strip()
  except Exception:
    df_users = pd.DataFrame([{
        "Identifiant": "admin",
        "Mot_de_passe": "admin123",
        "Nom_Responsable": "Direction DSI",
        "Zone": "Vue Globale",
    }])

  # Lecture de la feuille Dons_Stock
  try:
    sheet_stock = spreadsheet.worksheet("Dons_Stock")
    df_stock = pd.DataFrame(sheet_stock.get_all_records())
    df_stock.columns = df_stock.columns.str.strip()
  except Exception:
    df_stock = pd.DataFrame()

  # Lecture de la feuille Dons_Distributions
  try:
    sheet_distrib = spreadsheet.worksheet("Dons_Distributions")
    df_distrib = pd.DataFrame(sheet_distrib.get_all_records())
    df_distrib.columns = df_distrib.columns.str.strip()
  except Exception:
    df_distrib = pd.DataFrame()

except Exception as e:
  st.error(f"⚠️ Erreur de connexion à Google Sheets : {e}")
  df = pd.DataFrame()
  df_users = pd.DataFrame()
  df_stock = pd.DataFrame()
  df_distrib = pd.DataFrame()

# --- DÉFINITION DES ZONES & COMMUNES ---
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

  # Détection du rôle / zone
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

  # --- BARRE LATÉRALE - DESIGN MODERNE ---
  st.sidebar.markdown(f"### 👤 **{user_nom}**")
  st.sidebar.caption(f"📌 **Espace : {user_zone}**")
  st.sidebar.markdown("---")

  # Liste des menus selon le profil
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

  # Affichage sous forme de cartes/boutons interactifs
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

  # Détermination de la zone géographique
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

    with st.container(border=True):
      with st.form("form_membre_principal", clear_on_submit=True):
        prochain_num = len(df) + 1 if not df.empty else 1
        matricule_auto = f"ONG DP {prochain_num:03d}"

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
        st.markdown("##### 👪 Informations du parent & Statut")
        c3, c4 = st.columns(2)
        with c3:
          nom_parent = st.text_input(
              "Nom et prénoms du parent (Ex: KOUASSI MARC)"
          ).upper()
          numero_tel = st.text_input("Numéro de téléphone du parent")
        with c4:
          adhesion = st.selectbox("Statut d'Adhésion", ["OK", "En attente"])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "💾 Valider et enregistrer le membre", use_container_width=True
        )

        if submitted:
          ville_finale = (
              ville_autre
              if ville_choix.startswith("AUTRE") and ville_autre
              else ville_choix
          )

          if nom_enfant and nom_parent:
            try:
              date_heure_actuelle = datetime.now().strftime(
                  "%Y-%m-%d %H:%M:%S"
              )
              auteur_enregistrement = f"{user_nom} ({user_zone})"

              nouvelle_ligne = [
                  matricule_auto,
                  nom_enfant,
                  date_naissance,
                  sexe,
                  ville_finale,
                  nom_parent,
                  str(numero_tel),
                  adhesion,
                  date_heure_actuelle,
                  auteur_enregistrement,
              ]
              sheet.append_row(nouvelle_ligne)
              st.session_state["toast_msg"] = (
                  f"✅ Membre {matricule_auto} enregistré avec succès !"
              )
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
      recherche_edit = st.text_input(
          "🔍 Rechercher dans votre zone...", key="recherche_edit"
      )

      if recherche_edit:
        mask_edit = df_f.astype(str).apply(
            lambda row: row.str.contains(
                recherche_edit, case=False, na=False
            ).any(),
            axis=1,
        )
        df_edit_filtered = df_f[mask_edit]
      else:
        df_edit_filtered = df_f

      if not df_edit_filtered.empty:
        liste_membres = df_edit_filtered[col_membre].astype(str).tolist()
        choix_membre = st.selectbox(
            "Sélectionner le membre",
            liste_membres,
            format_func=lambda m: (
                f"{m} - "
                f"{df_edit_filtered[df_edit_filtered[col_membre].astype(str) == m][col_enfant].values[0]}"
                if col_enfant in df_edit_filtered.columns
                else m
            ),
        )

        membre_actuel = df[df[col_membre].astype(str) == choix_membre].iloc[0]

        st.markdown("---")
        choix_action = st.radio(
            "Action à effectuer",
            ["Modifier les informations", "Supprimer le membre"],
            horizontal=True,
        )

        with st.container(border=True):
          if choix_action == "Modifier les informations":
            with st.form("form_modification", clear_on_submit=True):
              m_nom_enfant = st.text_input(
                  "Nom et Prénom",
                  value=str(membre_actuel.get(col_enfant, "")),
              ).upper()
              m_date_nais = st.text_input(
                  "Date de naissance",
                  value=str(membre_actuel.get(col_date, "")),
              )
              val_sexe = str(membre_actuel.get(col_sexe, "M")).upper()
              m_sexe = st.selectbox(
                  "Sexe", ["M", "F"], index=0 if val_sexe == "M" else 1
              )
              m_ville = st.text_input(
                  "Ville", value=str(membre_actuel.get(col_ville, ""))
              ).upper()
              m_nom_parent = st.text_input(
                  "Parent", value=str(membre_actuel.get(col_parent, ""))
              ).upper()
              m_tel = st.text_input(
                  "Téléphone", value=str(membre_actuel.get(col_tel, ""))
              )
              val_adh = str(membre_actuel.get(col_adh, "OK")).upper()
              m_adhesion = st.selectbox(
                  "Adhésion",
                  ["OK", "En attente"],
                  index=0 if "OK" in val_adh else 1,
              )

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
                  st.session_state["toast_msg"] = (
                      f"✅ Membre {choix_membre} mis à jour !"
                  )
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
                  st.session_state["toast_msg"] = (
                      f"✅ Membre {choix_membre} supprimé !"
                  )
                  st.rerun()
                except Exception as e:
                  st.error(f"❌ Erreur : {e}")
              else:
                st.error("⚠️ Cochez la case de confirmation.")
      else:
        st.warning("⚠️ Aucun membre trouvé.")
    else:
      st.info("Aucun membre disponible.")

  # ==========================================
  # 4. LISTE & REPERTOIRE (AVEC PAGINATION)
  # ==========================================
  elif menu == "📋 Liste & Répertoire":
    st.subheader(f"📋 Répertoire - {choix_zone_label}")

    recherche = st.text_input("🔍 Rechercher un membre...", key="recherche_liste")

    if not df_f.empty:
      if recherche:
        mask = df_f.astype(str).apply(
            lambda row: row.str.contains(recherche, case=False, na=False).any(),
            axis=1,
        )
        df_affiche = df_f[mask]
        st.info(f"ℹ️ Résultats trouvés : {len(df_affiche)}")
      else:
        df_affiche = df_f

      total_lignes = len(df_affiche)

      if total_lignes > 0:
        col_pg1, col_pg2 = st.columns([1, 2])
        with col_pg1:
          lignes_par_page = st.selectbox(
              "Lignes par page", [10, 25, 50, 100], index=0, key="lignes_page"
          )

        total_pages = math.ceil(total_lignes / lignes_par_page)

        with col_pg2:
          page_actuelle = st.selectbox(
              "Sélectionner la page / plage",
              range(1, total_pages + 1),
              format_func=lambda x: (
                  f"Page {x} / {total_pages} (Membres { (x-1)*lignes_par_page + 1 } à"
                  f" {min(x*lignes_par_page, total_lignes)} sur {total_lignes})"
              ),
              key="select_page",
          )

        debut = (page_actuelle - 1) * lignes_par_page
        fin = min(debut + lignes_par_page, total_lignes)
        df_page = df_affiche.iloc[debut:fin]

        with st.container(border=True):
          cols_affichage = [
              c for c in df_page.columns if c != "Zone_Geographique"
          ]
          st.dataframe(df_page[cols_affichage], use_container_width=True)
      else:
        st.warning("⚠️ Aucun membre ne correspond à votre recherche.")

      st.markdown("---")
      output = BytesIO()
      with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_affiche.to_excel(writer, index=False, sheet_name="Membres")
      excel_data = output.getvalue()

      st.download_button(
          label="📥 Exporter la liste filtrée en Excel (.xlsx)",
          data=excel_data,
          file_name=f"Membres_{choix_zone_label.replace(' ', '_')}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
    else:
      st.warning("⚠️ Aucune donnée à afficher.")

  # ==========================================
  # 5. STOCK DES DONS
  # ==========================================
  elif menu == "📦 Stock des Dons":
    st.subheader("📦 Stock & Réception des Dons")

    with st.container(border=True):
      with st.form("form_entree_don", clear_on_submit=True):
        type_don = st.selectbox(
            "Type de Don",
            [
                "Matériel Médical / Fauteuil",
                "Produits d'Hygiène / Couches",
                "Vivres / Alimentation",
                "Vêtements",
                "Don Financier (FCFA)",
                "Autre",
            ],
        )
        designation = st.text_input(
            "Désignation (Ex: Fauteuils Roulants Enfant)"
        ).upper()
        donateur = st.text_input("Donateur / Partenaire").upper()
        quantite_recue = st.number_input(
            "Quantité reçue", min_value=1, value=1, step=1
        )
        valeur_estimee = st.number_input(
            "Valeur estimée globale (FCFA)", min_value=0, value=0, step=5000
        )

        btn_save_don = st.form_submit_button(
            "📥 Enregistrer en Stock", use_container_width=True
        )

        if btn_save_don:
          if designation:
            try:
              ws_stock = spreadsheet.worksheet("Dons_Stock")
              date_du_jour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              id_don = f"DON-{datetime.now().strftime('%Y%m%d%H%M%S')}"

              nouvelle_ligne_don = [
                  id_don,
                  date_du_jour,
                  type_don,
                  designation,
                  quantite_recue,
                  quantite_recue,
                  valeur_estimee,
                  donateur if donateur else "ANONYME",
                  user_zone,
                  f"{user_nom}",
              ]
              ws_stock.append_row(nouvelle_ligne_don)
              st.session_state["toast_msg"] = (
                  f"✅ Don '{designation}' enregistré en stock !"
              )
              st.rerun()
            except Exception as e:
              st.error(f"❌ Erreur : {e}")
          else:
            st.error("⚠️ Saisissez une désignation.")

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
  elif menu == "🎁 Remise de Dons" or menu == "🎁 Remise & Traçabilité":
    st.subheader("🎁 Attribution & Remise de Don aux Enfants")

    if not df.empty and not df_stock.empty:
      if "Stock_Actuel" in df_stock.columns:
        df_stock_dispo = df_stock[
            pd.to_numeric(df_stock["Stock_Actuel"], errors="coerce").fillna(0)
            > 0
        ]
      else:
        df_stock_dispo = df_stock

      if not df_stock_dispo.empty:
        with st.container(border=True):
          with st.form("form_remise_don", clear_on_submit=True):
            liste_enfants = df[col_membre].astype(str).tolist()
            choix_enfant_don = st.selectbox(
                "1. Enfant bénéficiaire",
                liste_enfants,
                format_func=lambda m: (
                    f"{m} - "
                    f"{df[df[col_membre].astype(str) == m][col_enfant].values[0]}"
                ),
            )

            liste_dons_dispo = df_stock_dispo["ID_Don"].astype(str).tolist()
            choix_don = st.selectbox(
                "2. Don à remettre",
                liste_dons_dispo,
                format_func=lambda d: (
                    f"{d} - "
                    f"{df_stock_dispo[df_stock_dispo['ID_Don'].astype(str) == d]['Designation'].values[0]} "
                    f"(Reste: {df_stock_dispo[df_stock_dispo['ID_Don'].astype(str) == d]['Stock_Actuel'].values[0]})"
                ),
            )

            quantite_remise = st.number_input(
                "3. Quantité remise", min_value=1, value=1, step=1
            )

            btn_remettre = st.form_submit_button(
                "🎁 Valider la Remise du Don", use_container_width=True
            )

            if btn_remettre:
              try:
                enfant_info = df[
                    df[col_membre].astype(str) == choix_enfant_don
                ].iloc[0]
                nom_e = enfant_info.get(col_enfant, "")
                nom_p = enfant_info.get(col_parent, "")

                don_info = df_stock_dispo[
                    df_stock_dispo["ID_Don"].astype(str) == choix_don
                ].iloc[0]
                designation_d = don_info.get("Designation", "")
                stock_actuel = int(don_info.get("Stock_Actuel", 1))

                if quantite_remise <= stock_actuel:
                  ws_distrib = spreadsheet.worksheet("Dons_Distributions")
                  ws_stock = spreadsheet.worksheet("Dons_Stock")

                  id_distrib = (
                      f"DIST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                  )
                  date_remise = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                  ligne_distrib = [
                      id_distrib,
                      date_remise,
                      choix_enfant_don,
                      nom_e,
                      nom_p,
                      designation_d,
                      quantite_remise,
                      user_zone,
                      f"{user_nom}",
                  ]
                  ws_distrib.append_row(ligne_distrib)

                  cell = ws_stock.find(str(choix_don))
                  nouv_stock = stock_actuel - quantite_remise
                  ws_stock.update_cell(cell.row, 6, nouv_stock)

                  st.session_state["toast_msg"] = (
                      f"🎁 Don remis à {nom_e} avec succès !"
                  )
                  st.rerun()
                else:
                  st.error(f"⚠️ Stock insuffisant (Reste : {stock_actuel})")
              except Exception as e:
                st.error(f"❌ Erreur : {e}")
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

  if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"], icon="🎉")
    st.success(st.session_state["toast_msg"])
    del st.session_state["toast_msg"]
