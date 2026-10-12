from io import BytesIO
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Gestion des Membres",
    page_icon="💚",
    layout="wide",
)

# Styles CSS personnalisés pour une interface moderne et élégante
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #008000 0%, #228B22 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin-bottom: 5px;
        font-size: 26px;
    }
    .main-header p {
        color: #f1f1f1;
        font-size: 14px;
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

# En-tête officiel inspiré de votre document
st.markdown(
    """
    <div class="main-header">
        <h1>ONG DIEU POURVOIRA</h1>
        <p><strong>Ensemble aidons les enfants atteints de Paralysie cérébrale</strong></p>
        <hr style="border-color: rgba(255,255,255,0.3); margin: 10px 0;">
        <p style="font-size: 12px;">
            📞 +225 77 71 04 41 8 / 05 86 99 73 27 &nbsp;|&nbsp; 
            ✉️ dieupourvoira187@gmail.com &nbsp;|&nbsp; 
            📍 08 BP 2945 ABIDJAN 08
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Chargement du fichier Excel ou utilisation des données d'origine
uploaded_file = st.sidebar.file_uploader(
    "📂 Importer votre fichier Excel", type=["xlsx", "xls"]
)

if uploaded_file is not None:
  df = pd.read_excel(uploaded_file)
else:
  data = {
      "Numéro du membre": [
          "ONG DP 001",
          "ONG DP 002",
          "ONG DP 003",
          "ONG DP 004",
          "ONG DP 005",
          "ONG DP 006",
          "ONG DP 007",
          "ONG DP 008",
          "ONG DP 009",
          "ONG DP 010",
          "ONG DP 011",
          "ONG DP 012",
      ],
      "Nom et Prénom de l'enfant": [
          "KOUAME SEM ARON ELIE",
          "Tralou Calista Maria Espoir",
          "OSSIN CHRIST JOSUÉ YVANN",
          "KOUASSI MARIE AHÉLA COUAMÉH",
          "KOUASSI MARIE KASSANDRE COUAM",
          "DEMBELE M'BIMBA MAHIL",
          "Akitikpa Larah",
          "Felix-Tchicaya Aliya Lourdes Naima",
          "Ouattara Yabilé karidja",
          "Danho Damo Elie-Psalmodia",
          "Camara Mariam Maéva",
          "KOUAKOU Mien N'zrama Bomithéel Elis",
      ],
      "Date de naissance": [
          "19/7/2014",
          "3 ANS",
          "2/7/2017",
          "6/9/2016",
          "6/9/2016",
          "10/10/2022",
          "15 ANS",
          "12 ANS",
          "12/4/1997",
          "4 ANS",
          "22/2/2015",
          "17/6/2023",
      ],
      "Sexe": ["M", "F", "M", "F", "F", "M", "F", "F", "F", "M", "F", "F"],
      "Ville": [
          "Cocody",
          "ISSIA",
          "Alépé",
          "Guiberoua",
          "",
          "Divo",
          "DOKUI",
          "COCODY",
          "Ferké",
          "COCODY",
          "COCODY",
          "DABOU",
      ],
      "Nom et prénoms du parent": [
          "KOUAME GUY ROGER",
          "Corole",
          "N'GBO BROU MARGUERITE AUDREY N'G",
          "BOLOU SENEPLÉ MARIE-JOSÉE",
          "",
          "BAKAYOKO FANIAN MATOGOMA",
          "Bah Caroline",
          "Felix-Tchicaya Andrée-Isabelle",
          "Coulibaly maimouna",
          "Danho",
          "Haby Alidou Fatouma",
          "Maman KOUAKOU Emilie",
      ],
      "Numero Tèl": [
          "777104418",
          "757979094",
          "789765169",
          "778698522",
          "",
          "778435839",
          "707731282",
          "747400276",
          "707144614",
          "709205218",
          "708117644",
          "778362422",
      ],
      "Adhésion": ["OK", "OK", "OK", "OK", "OK", "OK", "", "", "", "", "", ""],
  }
  df = pd.DataFrame(data)

# Navigation latérale
st.sidebar.markdown("### 🧭 Menu Principal")
menu = st.sidebar.radio(
    "Aller à :", ["📊 Tableau de Bord", "➕ Enregistrer", "📋 Liste & Recherche"]
)

if menu == "📊 Tableau de Bord":
  st.subheader("📈 Statistiques de l'ONG")

  total_membres = len(df)
  total_garcons = len(df[df["Sexe"].str.upper() == "M"])
  total_filles = len(df[df["Sexe"].str.upper() == "F"])
  total_actifs = len(df[df["Adhésion"].str.upper() == "OK"])

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Enfants", total_membres)
  col2.metric("Garçons", total_garcons)
  col3.metric("Filles", total_filles)
  col4.metric("Adhésions OK", total_actifs)

  st.markdown("---")
  st.markdown("### 🕒 Derniers ajouts")
  st.dataframe(df.tail(5), use_container_width=True)

elif menu == "➕ Enregistrer":
  st.subheader("📝 Formulaire d'Enregistrement")

  st.markdown(
      """
      <div class="info-box">
          ℹ️ Le numéro de membre est incrémenté automatiquement. Remplissez les informations de l'enfant et du parent.
      </div>
  """,
      unsafe_allow_html=True,
  )

  with st.form("form_membre"):
    prochain_num = len(df) + 1
    matricule_auto = f"ONG DP {prochain_num:03d}"

    st.markdown("##### 👶 Informations de l'enfant")
    col1, col2, col3 = st.columns(3)
    with col1:
      numero_membre = st.text_input("Numéro du membre", value=matricule_auto)
    with col2:
      sexe = st.selectbox("Sexe", ["M", "F"])
    with col3:
      date_naissance = st.text_input("Date de naissance / Âge")

    nom_enfant = st.text_input(
        "Nom et Prénom de l'enfant (Ex: KOUASSI JEAN)"
    ).upper()
    ville = st.text_input("Ville / Commune (Ex: COCODY)").upper()

    st.markdown("---")
    st.markdown("##### 👪 Informations du parent & Statut")
    col4, col5 = st.columns(2)
    with col4:
      nom_parent = st.text_input(
          "Nom et prénoms du parent (Ex: KOUASSI MARC)"
      ).upper()
    with col5:
      numero_tel = st.text_input("Numéro de téléphone du parent")

    adhesion = st.selectbox("Statut d'Adhésion", ["OK", "En attente"])

    submitted = st.form_submit_button("Enregistrer le membre")

    if submitted:
      if nom_enfant and nom_parent:
        nouvelle_ligne = {
            "Numéro du membre": numero_membre,
            "Nom et Prénom de l'enfant": nom_enfant,
            "Date de naissance": date_naissance,
            "Sexe": sexe,
            "Ville": ville,
            "Nom et prénoms du parent": nom_parent,
            "Numero Tèl": numero_tel,
            "Adhésion": adhesion,
        }
        df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        st.success(
            f"✅ Enregistré avec succès ! Matricule attribué :"
            f" **{numero_membre}**"
        )
      else:
        st.error(
            "⚠️ Veuillez renseigner au moins le nom de l'enfant et du parent."
        )

elif menu == "📋 Liste & Recherche":
  st.subheader("📋 Répertoire Général des Membres")

  recherche = st.text_input(
      "🔍 Rechercher (Nom d'enfant, Parent, Ville ou Matricule)..."
  )

  if recherche:
    mask = (
        df["Numéro du membre"].str.contains(recherche, case=False, na=False)
        | df["Nom et Prénom de l'enfant"].str.contains(
            recherche, case=False, na=False
        )
        | df["Nom et prénoms du parent"].str.contains(
            recherche, case=False, na=False
        )
        | df["Ville"].str.contains(recherche, case=False, na=False)
    )
    df_affiche = df[mask]
    st.info(f"Résultats trouvés : {len(df_affiche)}")
  else:
    df_affiche = df

  st.dataframe(df_affiche, use_container_width=True)

  # Export Excel
  output = BytesIO()
  with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Membres")
  excel_data = output.getvalue()

  st.download_button(
      label="📥 Télécharger le fichier Excel mis à jour",
      data=excel_data,
      file_name="ONG_Dieu_Pourvoira_Membres.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
