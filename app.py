from io import BytesIO
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="ONG DIEU POURVOIRA - Gestion des Membres", layout="centered"
)

# En-tête de l'application
st.markdown(
    "<h2 style='text-align: center; color: #008000;'>ONG DIEU POURVOIRA</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-style: italic;'>Ensemble aidons"
    " les enfants atteints de Paralysie cérébrale</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Option pour charger le fichier Excel existant
uploaded_file = st.file_uploader(
    "📂 Importer votre fichier Excel actuel (Optionnel)", type=["xlsx", "xls"]
)

if uploaded_file is not None:
  df = pd.read_excel(uploaded_file)
else:
  # Données de base basées sur votre capture si aucun fichier n'est chargé
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

# Menu latéral
menu = st.sidebar.selectbox(
    "Navigation", ["➕ Enregistrer un membre", "📋 Voir la liste complète"]
)

if menu == "➕ Enregistrer un membre":
  st.subheader("Formulaire d'enregistrement")

  with st.form("form_enregistrement"):
    # Calcul automatique du prochain numéro
    prochain_num = len(df) + 1
    matricule_defaut = f"ONG DP {prochain_num:03d}"

    col1, col2 = st.columns(2)
    with col1:
      numero_membre = st.text_input(
          "Numéro du membre", value=matricule_defaut
      )
      sexe = st.selectbox("Sexe", ["M", "F"])
      ville = st.text_input("Ville / Commune")
    with col2:
      date_naissance = st.text_input("Date de naissance (ex: 15/06/2018 ou Âge)")
      numero_tel = st.text_input("Numéro Tèl du parent")

    nom_enfant = st.text_input(
        "Nom et Prénom de l'enfant (Ex: KOUASSI JEAN)"
    ).upper()
    nom_parent = st.text_input(
        "Nom et prénoms du parent (Ex: KOUASSI MARC)"
    ).upper()
    adhesion = st.selectbox("Adhésion", ["OK", "En attente"])

    valider = st.form_submit_button("Enregistrer dans la base")

    if valider:
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
        # Ajout de la ligne au tableau
        df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        st.success(
            f"✅ {nom_enfant} a été enregistré avec succès sous le numéro"
            f" {numero_membre} !"
        )
      else:
        st.error(
            "Veuillez renseigner au moins le nom de l'enfant et du parent."
        )

elif menu == "📋 Voir la liste complète":
  st.subheader("Base de données des membres")
  st.dataframe(df, use_container_width=True)

  # Bouton de téléchargement du fichier Excel mis à jour
  output = BytesIO()
  with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Membres")
  excel_file = output.getvalue()

  st.download_button(
      label="📥 Télécharger le fichier Excel mis à jour (.xlsx)",
      data=excel_file,
      file_name="ONG_Dieu_Pourvoira_Membres.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )