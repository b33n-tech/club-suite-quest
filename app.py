import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Prototype Dashboard - Quest for Change")

# -------------------------------
# Fonction de chargement
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
# Gestion de la progression
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0

file_labels = [
    "📁 Profils individuels Le Club",
    "🏢 Profils Entreprises Le Club",
    "🔗 Historique des mises en relation",
    "🧭 Base Globale Projets"
]

uploaded_files = ["users_file", "entreprises_file", "relations_file", "projets_file"]
dataframes = ["users", "entreprises", "relations", "projets"]

# Barre de progression
progress = st.progress((st.session_state.step) / 4)

# Étape actuelle
current_label = file_labels[st.session_state.step]
uploaded_file = st.file_uploader(f"{current_label} (csv ou xlsx)")

# Si fichier uploadé → bouton Suivant
if uploaded_file is not None:
    st.session_state[uploaded_files[st.session_state.step]] = uploaded_file
    if st.button("➡️ Suivant"):
        st.session_state.step += 1
        st.experimental_rerun()

# Une fois tous les fichiers uploadés
if st.session_state.step == 4:
    progress.progress(1.0)
    # Charger tous les fichiers
    users = load_file(st.session_state.users_file)
    entreprises = load_file(st.session_state.entreprises_file)
    relations = load_file(st.session_state.relations_file)
    projets = load_file(st.session_state.projets_file)

    if all([users is not None, entreprises is not None, relations is not None, projets is not None]):
        st.success("✅ Tous les fichiers ont été importés avec succès.")

        # --- KPIs ---
        kpi1 = len(entreprises)
        kpi2 = len(users)
        kpi3 = len(relations)
        kpi4 = round(kpi3 / max(kpi2, 1), 2)
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
