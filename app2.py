import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Dashboard Quest for Change - Prototype Ludique")

# -------------------------------
# Fonction de lecture CSV / Excel
# -------------------------------
def load_file(file):
    if file is None:
        return None
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
            st.caption(f"✅ {file.name} lu (Excel)")
            return df
        try:
            df = pd.read_csv(file, sep=";", encoding="cp1252", on_bad_lines="skip")
        except Exception:
            file.seek(0)
            df = pd.read_csv(file, sep=",", encoding="cp1252", on_bad_lines="skip")
        st.caption(f"✅ {file.name} lu (CSV CP1252)")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier {file.name} : {e}")
        return None

# -------------------------------
# Initialisation session_state
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "files" not in st.session_state:
    st.session_state.files = [None]*4
if "dfs" not in st.session_state:
    st.session_state.dfs = [None]*4

# -------------------------------
# Paramètres des étapes
# -------------------------------
steps_info = [
    {"label": "📁 Profils individuels Le Club",
     "desc": "Importez le fichier 'extract_users_xxx.csv'. Contient tous les profils inscrits.",
     "color": "#A3E4D7"},
    {"label": "🏢 Profils Entreprises Le Club",
     "desc": "Importez le fichier 'Profil entreprises.csv'. Contient toutes les entreprises.",
     "color": "#F9E79F"},
    {"label": "🔗 Historique des mises en relation",
     "desc": "Importez le fichier 'Historique des mises en relation.csv'. Contient toutes les interactions.",
     "color": "#F5B7B1"},
    {"label": "🧭 Base Globale Projets",
     "desc": "Importez la base interne des projets incubés pour croiser les données.",
     "color": "#D2B4DE"}
]

# -------------------------------
# Barre de progression
# -------------------------------
progress = st.progress(st.session_state.step / len(steps_info))

# -------------------------------
# Affichage de l'étape courante
# -------------------------------
if st.session_state.step < len(steps_info):
    step = steps_info[st.session_state.step]
    st.markdown(
        f"""
        <div style="padding:20px; background-color:{step['color']}; border-radius:10px; margin-bottom:20px;">
        <h3>{step['label']}</h3>
        <p>{step['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("", type=["csv","xlsx"], key=f"upload_{st.session_state.step}")

    if uploaded_file is not None:
        # Animation de chargement simulée
        with st.spinner("📂 Lecture du fichier..."):
            time.sleep(1)
            df = load_file(uploaded_file)
        if df is not None:
            st.session_state.files[st.session_state.step] = uploaded_file
            st.session_state.dfs[st.session_state.step] = df
            if st.button("➡️ Suivant"):
                st.session_state.step += 1

# -------------------------------
# Quand toutes les étapes sont terminées
# -------------------------------
if st.session_state.step == len(steps_info):
    progress.progress(1.0)
    st.success("✅ Tous les fichiers ont été uploadés et lus avec succès !")

    users, entreprises, relations, projets = st.session_state.dfs

    # --- KPIs ---
    kpi1 = len(entreprises)
    kpi2 = len(users)
    kpi3 = len(relations)
    kpi4 = round(kpi3 / max(kpi2,1),2)
    kpi5 = projets["Incubateur territorial"].nunique() if "Incubateur territorial" in projets.columns else 0

    st.subheader("📊 Indicateurs clés")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Entreprises", kpi1)
    c2.metric("Utilisateurs", kpi2)
    c3.metric("Mises en relation", kpi3)
    c4.metric("Taux de conversion", f"{kpi4}")
    c5.metric("Incubateurs distincts", kpi5)

    # --- Graphique ---
    st.subheader("🏗️ Répartition des projets par incubateur")
    if "Incubateur territorial" in projets.columns:
        fig, ax = plt.subplots()
        projets["Incubateur territorial"].value_counts().plot(kind="bar", ax=ax)
        ax.set_xlabel("Incubateur")
        ax.set_ylabel("Nombre de projets")
        st.pyplot(fig)
    else:
        st.info("Aucune colonne 'Incubateur territorial' trouvée dans la base des projets.")

    # --- Aperçu ---
    with st.expander("👀 Aperçu des données importées"):
        st.write("**Profils individuels :**", users.head())
        st.write("**Entreprises :**", entreprises.head())
        st.write("**Mises en relation :**", relations.head())
        st.write("**Projets :**", projets.head())
