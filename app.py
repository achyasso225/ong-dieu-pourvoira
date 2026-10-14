from io import BytesIO
import math
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# --- CONFIGURATION DE LA PAGE & FAVICON ---
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Gestion des Membres",
    page_icon="logo.png",
    layout="wide",
)

# Styles CSS personnalisés
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #008000 0%, #228B22 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin-bottom: 5px;
        font-size: 24px;
    }
    .main-header p {
        color: #f1f1f1;
        font-size: 13px;
        margin: 0;
    }
    .info-box {
        background-color: #fdfefe;
        border-left: 5px solid #ff7f00;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 14px;
        color: #333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        background-color: #008000;
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #006400;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# En-tête officiel de l'ONG
st.markdown(
    """
    <div class="main-header">
        <h1>ONG DIEU POURVOIRA</h1>
        <p><strong>Ensemble aidons les enfants atteints de Paralysie cérébrale</strong></p>
        <hr style="border-color: rgba(255,255,255,0.3); margin: 8px 0;">
        <p style="font-size: 11px;">
            📞 +225 77 71 04 41 8 / 05 86 99 73 27 &nbsp;|&nbsp; 
            ✉️ dieupourvoira187@gmail.com &nbsp;|&nbsp; 
            📍 08 BP 2945 ABIDJAN 08
        </p>
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

  # Formatage des numéros de téléphone pour conserver le '0' initial
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

  # Lecture des utilisateurs / responsables depuis le 2nd onglet 'Utilisateurs'
  try:
    sheet_users = spreadsheet.worksheet("Utilisateurs")
    df_users = pd.DataFrame(sheet_users.get_all_records())
    df_users.columns = df_users.columns.str.strip()
  except Exception:
    # Création d'une table par défaut si l'onglet n'existe pas encore
    df_users = pd.DataFrame([{
        "Identifiant": "admin",
        "Mot_de_passe": "admin123",
        "Nom_Responsable": "Direction DSI",
        "Zone": "🌐 Vue Globale",
    }])

except Exception as e:
  st.error(
      "⚠️ Erreur de connexion à Google Sheets. Vérifiez vos secrets Streamlit."
      f" Détails : {e}"
  )
  df = pd.DataFrame()
  df_users = pd.DataFrame()

# --- DÉFINITION DES ZONES D'ABIDJAN ---
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
    "ATTECOUBE",
    "ATTÉCOUBÉ",
    "N'DOTRE",
    "NDOTRE",
    "ADJAME",
    "ADJAMÉ",
    "WILLIAMS CIVIL",
    "WILLIAMSSVILLE",
    "SONGON",
    "DABOU",
]


def attribuer_zone(ville):
  v = str(ville).upper().strip()
  if any(z in v for z in ZONES_SUD):
    return "📍 Zone Sud"
  elif any(z in v for z in ZONES_NORD):
    return "📍 Zone Nord"
  else:
    return "📍 Autres / Centre"


# Détection des colonnes principales
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
  df["Zone_Geographique"] = "📍 Autres / Centre"


# --- GESTION DE LA SESSION DE CONNEXION ---
if "user_connected" not in st.session_state:
  st.session_state["user_connected"] = False
  st.session_state["user_info"] = None

# --- ÉCRAN DE CONNEXION ---
if not st.session_state["user_connected"]:
  st.subheader("🔐 Connexion au Portail ONG DIEU POURVOIRA")
  st.markdown(
      """
      <div class="info-box">
          Veuillez saisir vos identifiants fournis par la DSI pour accéder à l'espace de votre zone.
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
          # Mode de secours si l'onglet Utilisateurs n'est pas rempli
          if identifiant == "admin" and mot_de_passe == "admin123":
            st.session_state["user_connected"] = True
            st.session_state["user_info"] = {
                "Nom_Responsable": "Direction DSI",
                "Zone": "🌐 Vue Globale",
            }
            st.rerun()
          else:
            st.error("❌ Identifiant ou mot de passe incorrect.")

# --- APPLICATION PRINCIPALE APRÈS CONNEXION ---
else:
  user_info = st.session_state["user_info"]
  user_zone = user_info.get("Zone", "🌐 Vue Globale")
  user_nom = user_info.get("Nom_Responsable", "Responsable")

  # Sidebar de session
  st.sidebar.markdown(f"### 👤 Connected : **{user_nom}**")
  st.sidebar.info(f"**Zone assignée :** {user_zone}")

  # Déconnexion
  if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["user_connected"] = False
    st.session_state["user_info"] = None
    st.rerun()

  # Application du filtrage strict selon la Zone du responsable
  if "Zone Sud" in user_zone:
    df_f = df[df["Zone_Geographique"] == "📍 Zone Sud"]
    choix_zone_label = "📍 Zone Sud"
  elif "Zone Nord" in user_zone:
    df_f = df[df["Zone_Geographique"] == "📍 Zone Nord"]
    choix_zone_label = "📍 Zone Nord"
  elif "Autres" in user_zone or "Centre" in user_zone:
    df_f = df[df["Zone_Geographique"] == "📍 Autres / Centre"]
    choix_zone_label = "📍 Autres / Centre"
  else:
    df_f = df  # Vue globale (Direction DSI)
    choix_zone_label = "🌐 Vue Globale (DSI)"

  # --- NAVIGATION PAR ONGLETS ---
  tab1, tab2, tab3, tab4 = st.tabs([
      "📊 Tableau de Bord",
      "➕ Enregistrer un Membre",
      "✏️ Modifier / Supprimer",
      "📋 Liste & Recherche",
  ])

  # ONGLET 1 : TABLEAU DE BORD
  with tab1:
    st.subheader(f"📈 Statistiques - {choix_zone_label}")

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

      col1, col2, col3, col4 = st.columns(4)
      col1.metric("Total Enfants", total_membres)
      col2.metric("Garçons", total_garcons)
      col3.metric("Filles", total_filles)
      col4.metric("Adhésions OK", total_actifs)

      st.markdown("---")
      st.markdown("### 🕒 Derniers ajouts dans votre zone")
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

  # ONGLET 2 : FORMULAIRE D'ENREGISTREMENT
  with tab2:
    st.subheader("📝 Formulaire d'Enregistrement")

    st.markdown(
        f"""
        <div class="info-box">
            ℹ️ Vous enregistrez un membre dans l'espace : <strong>{choix_zone_label}</strong>.
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("form_membre_principal"):
      prochain_num = len(df) + 1 if not df.empty else 1
      matricule_auto = f"ONG DP {prochain_num:03d}"

      st.markdown("##### 👶 Informations de l'enfant")
      c1, c2, c3 = st.columns(3)
      with c1:
        numero_membre = st.text_input(
            "Numéro du membre (Auto)", value=matricule_auto, disabled=True
        )
      with c2:
        sexe = st.selectbox("Sexe", ["M", "F"])
      with c3:
        date_naissance = st.text_input("Date de naissance / Âge")

      nom_enfant = st.text_input(
          "Nom et Prénom de l'enfant (Ex: KOUASSI JEAN)"
      ).upper()

      ville_options = [
          "MARCORY",
          "TREICHVILLE",
          "KOUMASSI",
          "PORT-BOUET",
          "YOPOUGON",
          "ADJAME",
          "ATTECOUBE",
          "COCODY",
          "ABOISSO",
          "GRAND-BASSAM",
          "BONOUA",
          "DABOU",
          "AUTRE",
      ]
      ville_choix = st.selectbox("Commune / Ville principale", ville_options)
      if ville_choix == "AUTRE":
        ville = st.text_input("Précisez la commune/ville").upper()
      else:
        ville = ville_choix

      st.markdown("---")
      st.markdown("##### 👪 Informations du parent & Statut")
      c4, c5 = st.columns(2)
      with c4:
        nom_parent = st.text_input(
            "Nom et prénoms du parent (Ex: KOUASSI MARC)"
        ).upper()
      with c5:
        numero_tel = st.text_input("Numéro de téléphone du parent")

      adhesion = st.selectbox("Statut d'Adhésion", ["OK", "En attente"])

      submitted = st.form_submit_button(
          "Enregistrer et envoyer dans Google Drive"
      )

      if submitted:
        if nom_enfant and nom_parent:
          try:
            nouvelle_ligne = [
                matricule_auto,
                nom_enfant,
                date_naissance,
                sexe,
                ville,
                nom_parent,
                str(numero_tel),
                adhesion,
            ]
            sheet.append_row(nouvelle_ligne)
            st.session_state["toast_msg"] = (
                f"✅ Succès : Enregistré ! Matricule : {matricule_auto}"
            )
            st.balloons()
            st.rerun()
          except Exception as e:
            st.error(f"❌ Erreur lors de l'enregistrement : {e}")
        else:
          st.error(
              "⚠️ Échec : Veuillez renseigner au moins le nom de l'enfant et du"
              " parent."
          )

  # ONGLET 3 : MODIFIER OU SUPPRIMER UN MEMBRE
  with tab3:
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

        if choix_action == "Modifier les informations":
          with st.form("form_modification"):
            st.markdown(f"**Modification pour le matricule : {choix_membre}**")

            m_nom_enfant = st.text_input(
                "Nom et Prénom de l'enfant",
                value=str(membre_actuel.get(col_enfant, "")),
            ).upper()
            m_date_nais = st.text_input(
                "Date de naissance / Âge",
                value=str(membre_actuel.get(col_date, "")),
            )

            val_sexe = str(membre_actuel.get(col_sexe, "M")).upper()
            index_sexe = 0 if val_sexe == "M" else 1
            m_sexe = st.selectbox("Sexe", ["M", "F"], index=index_sexe)

            m_ville = st.text_input(
                "Ville / Commune", value=str(membre_actuel.get(col_ville, ""))
            ).upper()
            m_nom_parent = st.text_input(
                "Nom et prénoms du parent",
                value=str(membre_actuel.get(col_parent, "")),
            ).upper()
            m_tel = st.text_input(
                "Numéro de téléphone du parent",
                value=str(membre_actuel.get(col_tel, "")),
            )

            val_adh = str(membre_actuel.get(col_adh, "OK")).upper()
            index_adh = 0 if "OK" in val_adh else 1
            m_adhesion = st.selectbox(
                "Statut d'Adhésion", ["OK", "En attente"], index=index_adh
            )

            btn_modifier = st.form_submit_button(
                "Mettre à jour les informations"
            )

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
                    f"✅ Succès : Membre {choix_membre} modifié avec succès !"
                )
                st.rerun()
              except Exception as e:
                st.error(f"❌ Erreur lors de la modification : {e}")
        else:
          st.warning(
              f"⚠️ Vous êtes sur le point de supprimer le membre **{choix_membre}"
              f" - {membre_actuel.get(col_enfant, '')}**."
          )
          confirmer_suppression = st.checkbox(
              "Je confirme vouloir supprimer définitivement ce membre"
          )
          if st.button(
              "🗑️ Confirmer la suppression",
              type="primary",
              use_container_width=True,
          ):
            if confirmer_suppression:
              try:
                cell = sheet.find(str(choix_membre))
                row_idx = cell.row
                sheet.delete_rows(row_idx)
                st.session_state["toast_msg"] = (
                    f"✅ Succès : Membre {choix_membre} supprimé avec succès !"
                )
                st.rerun()
              except Exception as e:
                st.error(f"❌ Erreur lors de la suppression : {e}")
            else:
              st.error(
                  "⚠️ Échec : Veuillez cocher la case de confirmation pour"
                  " procéder à la suppression."
              )
      else:
        st.warning(
            "⚠️ Aucun membre ne correspond à votre recherche dans votre zone."
        )
    else:
      st.info("Aucun membre disponible dans votre zone.")

  # ONGLET 4 : LISTE & RECHERCHE
  with tab4:
    st.subheader(f"📋 Répertoire - {choix_zone_label}")

    recherche = st.text_input(
        "🔍 Rechercher dans votre liste...", key="recherche_liste"
    )

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
              "Sélectionner la plage / page",
              range(1, total_pages + 1),
              format_func=lambda x: (
                  f"Affichage : { (x-1)*lignes_par_page + 1 } à"
                  f" {min(x*lignes_par_page, total_lignes)} (sur {total_lignes}"
                  " membres)"
              ),
              key="select_page",
          )

        debut = (page_actuelle - 1) * lignes_par_page
        fin = min(debut + lignes_par_page, total_lignes)
        df_page = df_affiche.iloc[debut:fin]

        cols_affichage = [
            c for c in df_page.columns if c != "Zone_Geographique"
        ]
        st.dataframe(df_page[cols_affichage], use_container_width=True)
      else:
        st.dataframe(df_affiche, use_container_width=True)

      st.markdown("---")
      st.markdown("### 📥 Télécharger une copie locale")
      output = BytesIO()
      with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_affiche.to_excel(writer, index=False, sheet_name="Membres_Zone")
      excel_data = output.getvalue()

      st.download_button(
          label="📥 Télécharger la base de données (.xlsx)",
          data=excel_data,
          file_name=f"Base_de_donnee_{choix_zone_label.split()[1] if len(choix_zone_label.split())>1 else 'Global'}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
    else:
      st.warning("⚠️ Aucune donnée à afficher pour cette zone.")

  # Affichage des notifications
  if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"], icon="🎉")
    st.success(st.session_state["toast_msg"])
    del st.session_state["toast_msg"]
