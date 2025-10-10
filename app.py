import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")

st.title("🚀 Prototype Dashboard - Quest for Change")

st.markdown("**Importez les 4 fichiers exportés de la marketplace** (.csv ou .xlsx, sans modification nécessaire).")

# Fonction de chargement universelle
def load_file(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        # CSV par défaut avec séparateur détection
        try:
            return pd.read_csv(file, sep=";")
        except:
            return pd.read_csv(file)
        
# Uploaders
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

# Vérification que tout est chargé
if all([users_file, entreprises_file, relations_file, projets_file]):
    st.success("✅ Tous les fichiers ont été importés avec succès.")

    # Chargement automatique
    users = load_file(users_file)
    entreprises = load_file(entreprises_file)
    relations = load_file(relations_file)
    projets = load_file(projets_file)

    # --- KPIs ---
    kpi1 = len(entreprises)
    kpi2 = len(users[users["Statut"].astype(str).str.lower() == "active"])
    kpi3 = len(relations)
    kpi4 = round(kpi3 / max(kpi2, 1), 2)  # taux de conversion
    kpi5 = projets["Incubateur territorial"].nunique()

    st.subheader("📊 Indicateurs clés")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Entreprises", kpi1)
    col2.metric("Utilisateurs actifs", kpi2)
    col3.metric("Mises en relation", kpi3)
    col4.metric("Taux de conversion", f"{kpi4}")
    col5.metric("Incubateurs distincts", kpi5)

    # --- Visualisation ---
    st.subheader("🏗️ Répartition des projets par incubateur")
    incub_count = projets["Incubateur territorial"].value_counts()
    fig, ax = plt.subplots()
    incub_count.plot(kind="bar", ax=ax)
    ax.set_xlabel("Incubateur")
    ax.set_ylabel("Nombre de projets")
    ax.set_title("Projets par incubateur")
    st.pyplot(fig)

else:
    st.info("🕐 En attente de l’importation des 4 fichiers (.csv ou .xlsx) pour générer le dashboard.")
