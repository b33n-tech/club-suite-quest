import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# ⚙️ CONFIGURATION DE LA PAGE
# -------------------------------
st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Prototype Dashboard - Quest for Change")
st.markdown("**Importez les 4 fichiers exportés de la marketplace** (.csv ou .xlsx, sans modification nécessaire).")

# -------------------------------
# 🧩 FONCTION DE CHARGEMENT ROBUSTE
# -------------------------------
def load_file(file):
    """Charge un fichier CSV ou Excel avec détection automatique de l'encodage"""
    if file is None:
        return None
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            # tentative avec encodages courants
            for enc in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
                try:
                    df = pd.read_csv(file, sep=";", encoding=enc)
                    break
                except Exception:
                    df = None
            if df is None:
                raise ValueError("Aucun encodage compatible détecté pour ce fichier.")
        if df.empty:
            st.warning(f"⚠️ Le fichier {file.name} est vide ou ne contient pas de données.")
            return None
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier {file.name} : {e}")
        return None

# -------------------------------
# 📂 ZONES D'IMPORT
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
# 📊 TRAITEMENT & VISUALISATION
# -------------------------------
users = load_file(users_file)
entreprises = load_file(entreprises_file)
relations = load_file(relations_file)
projets = load_file(projets_file)

if all([users is not None, entreprises is not None, relations is not None, projets is not None]):
    st.success("✅ Tous les fichiers ont été importés avec succès.")

    # --- Calcul des KPIs ---
    kpi1 = len(entreprises)
    try:
        kpi2 = len(users[users["Statut"].astype(str).str.lower() == "active"])
    except KeyError:
        kpi2 = len(users)
    kpi3 = len(relations)
    kpi4 = round(kpi3 / max(kpi2, 1), 2)
    try:
        kpi5 = projets["Incubateur territorial"].nunique()
    except KeyError:
        kpi5 = 0

    # --- Affichage des KPIs ---
    st.subheader("📊 Indicateurs clés")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Entreprises", kpi1)
    c2.metric("Utilisateurs actifs", kpi2)
    c3.metric("Mises en relation", kpi3)
    c4.metric("Taux de conversion", f"{kpi4}")
    c5.metric("Incubateurs distincts", kpi5)

    # --- Visualisation ---
    st.subheader("🏗️ Répartition des projets par incubateur")
    try:
        incub_count = projets["Incubateur territorial"].value_counts()
        fig, ax = plt.subplots()
        incub_count.plot(kind="bar", ax=ax)
        ax.set_xlabel("Incubateur")
        ax.set_ylabel("Nombre de projets")
        ax.set_title("Projets par incubateur")
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Impossible d’afficher le graphique : {e}")

else:
    st.info("🕐 En attente de l’importation des 4 fichiers (.csv ou .xlsx) pour générer le dashboard.")
