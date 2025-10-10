import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")

st.title("🚀 Prototype Dashboard - Quest for Change")

st.markdown("**Importez les 4 fichiers CSV exportés de la marketplace** (aucune modification nécessaire).")

# Uploaders
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    users_file = st.file_uploader("📁 Profils individuels Le Club (.csv)", type=["csv"])
with col2:
    entreprises_file = st.file_uploader("🏢 Profils Entreprises Le Club (.csv)", type=["csv"])
with col3:
    relations_file = st.file_uploader("🔗 Historique des mises en relation (.csv)", type=["csv"])
with col4:
    projets_file = st.file_uploader("🧭 Base Globale Projets (.csv)", type=["csv"])

if all([users_file, entreprises_file, relations_file, projets_file]):
    st.success("✅ Tous les fichiers ont été importés avec succès.")

    # Chargement
    users = pd.read_csv(users_file, sep=";")
    entreprises = pd.read_csv(entreprises_file, sep=";")
    relations = pd.read_csv(relations_file, sep=";")
    projets = pd.read_csv(projets_file, sep=";")

    # KPIs
    kpi1 = len(entreprises)
    kpi2 = len(users[users["Statut"].str.lower() == "active"])
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

    # Visualisation : répartition par incubateur
    st.subheader("🏗️ Répartition des projets par incubateur")
    incub_count = projets["Incubateur territorial"].value_counts()
    fig, ax = plt.subplots()
    incub_count.plot(kind="bar", ax=ax)
    ax.set_xlabel("Incubateur")
    ax.set_ylabel("Nombre de projets")
    ax.set_title("Projets par incubateur")
    st.pyplot(fig)

else:
    st.info("🕐 En attente de l’importation des 4 fichiers pour générer le dashboard.")
