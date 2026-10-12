from io import BytesIO
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


# --- CONNEXION AUTOMATIQUE À GOOGLE SHEETS PAR NOM ---
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
  # Ouverture directe par le nom exact du fichier partagé sur Google Drive
  sheet = client.open("Base_de_donnee_ONG_Dieu_Pourvoira").sheet1

  # head=9 lit les en-têtes à la ligne 9 et ignore l'en-tête graphique du haut
  data = sheet.get_all_records(head=9)
  df = pd.DataFrame(data)

  # Nettoyage des espaces et filtrage des lignes valides
  df.columns = df.columns.str.strip()
  if "Numéro du membre" in df.columns:
    df = df[df["Numéro du membre"].astype(str).str.startswith("ONG DP")]
except Exception as e:
  st.error(
      "⚠️ Erreur de connexion à Google Sheets. Vérifiez vos secrets Streamlit."
      f" Détails : {e}"
  )
  df = pd.DataFrame()


# --- NAVIGATION PAR ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau de Bord",
    "➕ Enregistrer un Membre",
    "✏️ Modifier un Membre",
    "📋 Liste & Recherche",
])

# Détection sécurisée des colonnes
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

# ONGLET 1 : TABLEAU DE BORD
with tab1:
  st.subheader("📈 Statistiques de l'ONG")

  if not df.empty:
    total_membres = len(df)
    total_garcons = (
        len(df[df[col_sexe].astype(str).str.upper() == "M"])
        if col_sexe in df.columns
        else 0
    )
    total_filles = (
        len(df[df[col_sexe].astype(str).str.upper() == "F"])
        if col_sexe in df.columns
        else 0
    )
    total_actifs = (
        len(df[df[col_adh].astype(str).str.upper() == "OK"])
        if col_adh in df.columns
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Enfants", total_membres)
    col2.metric("Garçons", total_garcons)
    col3.metric("Filles", total_filles)
    col4.metric("Adhésions OK", total_actifs)

    st.markdown("---")
    st.markdown("### 🕒 Derniers ajouts dans la base Google Drive")
    st.dataframe(df.tail(5), use_container_width=True)
  else:
    st.warning("Aucune donnée trouvée dans le fichier Google Sheets.")

# ONGLET 2 : FORMULAIRE D'ENREGISTREMENT
with tab2:
  st.subheader("📝 Formulaire d'Enregistrement (Synchronisé en direct)")

  st.markdown(
      """
      <div class="info-box">
          ℹ️ Le numéro de membre s'incrémente automatiquement et est verrouillé. En validant, l'enfant est enregistré instantanément dans Google Drive !
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
    ville = st.text_input("Ville / Commune de résidence (Ex: COCODY)").upper()

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

    submitted = st.form_submit_button("Enregistrer et envoyer dans Google Drive")

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
              numero_tel,
              adhesion,
          ]
          sheet.append_row(nouvelle_ligne)
          st.success(
              f"✅ Enregistré avec succès dans Google Drive ! Matricule attribué"
              f" : **{matricule_auto}**"
          )
          st.balloons()
          st.rerun()
        except Exception as e:
          st.error(
              f"Erreur lors de l'enregistrement dans Google Sheets : {e}"
          )
      else:
        st.error(
            "⚠️ Veuillez renseigner au moins le nom de l'enfant et du parent."
        )

# ONGLET 3 : MODIFIER UN MEMBRE EXISTANT
with tab3:
  st.subheader("✏️ Modifier ou Corriger un Enregistrement")

  if not df.empty and col_membre in df.columns:
    st.markdown(
        """
        <div class="info-box">
            ℹ️ Sélectionnez un membre par son numéro pour modifier ses informations en cas d'erreur. La mise à jour sera reportée directement dans Google Drive.
        </div>
    """,
        unsafe_allow_html=True,
    )

    liste_membres = df[col_membre].astype(str).tolist()
    choix_membre = st.selectbox(
        "Sélectionner le membre à modifier", liste_membres
    )

    membre_actuel = df[df[col_membre].astype(str) == choix_membre].iloc[0]

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

      btn_modifier = st.form_submit_button("Mettre à jour les informations")

      if btn_modifier:
        try:
          cell = sheet.find(str(choix_membre))
          row_idx = cell.row

          sheet.update_cell(row_idx, 2, m_nom_enfant)
          sheet.update_cell(row_idx, 3, m_date_nais)
          sheet.update_cell(row_idx, 4, m_sexe)
          sheet.update_cell(row_idx, 5, m_ville)
          sheet.update_cell(row_idx, 6, m_nom_parent)
          sheet.update_cell(row_idx, 7, m_tel)
          sheet.update_cell(row_idx, 8, m_adhesion)

          st.success(
              f"✅ Les informations de {choix_membre} ont été modifiées avec"
              " succès dans Google Drive !"
          )
          st.balloons()
          st.rerun()
        except Exception as e:
          st.error(f"Erreur lors de la modification dans Google Sheets : {e}")
  else:
    st.info("Aucun membre disponible pour modification.")

# ONGLET 4 : LISTE, RECHERCHE & TÉLÉCHARGEMENT
with tab4:
  st.subheader("📋 Répertoire Général des Membres")

  recherche = st.text_input(
      "🔍 Rechercher un enfant, un parent, une ville ou un matricule..."
  )

  if not df.empty:
    if recherche:
      mask = df.astype(str).apply(
          lambda row: row.str.contains(recherche, case=False, na=False).any(),
          axis=1,
      )
      df_affiche = df[mask]
      st.info(f"Résultats trouvés : {len(df_affiche)}")
    else:
      df_affiche = df

    st.dataframe(df_affiche, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📥 Télécharger une copie locale")
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
      df.to_excel(writer, index=False, sheet_name="Membres")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Télécharger la base de données actuelle (.xlsx)",
        data=excel_data,
        file_name="Base_de_donnee_ONG_Dieu_Pourvoira.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
  else:
    st.info("Aucune donnée à afficher.")
