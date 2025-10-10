import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Prototype Dashboard - Quest for Change")
st.markdown("**Importez les 4 fichiers exportés de la marketplace (.csv ou .xlsx)** — sans les modifier.")

# -------------------------------
# FONCTION DE CHARGEMENT SIMPLE ET ROBUSTE
# -------------------------------
def load_file(file):
    if file is None:
        return None

    try:
        # Excel
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
            st.caption(f"✅ {file.name} lu (Excel)")
            return df

        # CSV (principalement export Excel Windows)
        try:
            df = pd.read_csv(file, sep=";", encoding="cp1252", on_bad_lines="skip")
        except Exception:
            file.seek(0)
            df = pd.read_csv(file, sep=",", encoding="cp1252", on_bad_lines="skip")

        st.caption(f"✅ {file.name} lu avec encodage CP1252")
        return df

    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier {file.name} : {e}")
        return None

# -------------------------------
# ZONES D’IMPORT
# -------------------------------
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    users_file = st.file_uploader("📁 Profils individuels Le Club", type=["csv", "xlsx"])
with col2:
    entreprises_file = st.file_uploader("🏢 Profils Entreprises Le Club", type=["csv", "xlsx"])
with col3:
    relations_file = st.file_uploader("🔗 Historique des mises en relation", type=["csv", "xlsx"])
with col4:
    projets_file = st.file_uploader("🧭 Base Globale Projets", type=["csv", "xlsx"])

# -------------------------------
# TRAITEMENT & VISUALISATION
# -------------------------------
users = load_file(users_file)
entreprises = load_file(entreprises_file)
relations = load_file(relations_file)
projets = load_file(projets_file)

if all([users is not None, entreprises is not None, relations is not None, projets is not None]):
    st.success("✅ Tous les fichiers ont été importés avec succès.")

    # --- KPIs de base ---
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

else:
    st.info("🕐 En attente de l’importation des 4 fichiers (.csv ou .xlsx) pour générer le dashboard.")
