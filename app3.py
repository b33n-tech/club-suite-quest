import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="KPI Generator - Croisé", layout="wide")
st.title("⚡ Générateur de KPIs Quest for Change (4 fichiers)")

# -------------------------------
# Fonction de lecture CSV / Excel
# -------------------------------
def load_file(file):
    if file is None:
        return None
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            try:
                df = pd.read_csv(file, sep=";", encoding="cp1252", on_bad_lines="skip")
            except Exception:
                file.seek(0)
                df = pd.read_csv(file, sep=",", encoding="cp1252", on_bad_lines="skip")
        st.success(f"✅ {file.name} chargé avec succès")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier {file.name} : {e}")
        return None

# -------------------------------
# Upload fichiers
# -------------------------------
st.header("1️⃣ Importez vos fichiers")

col1, col2, col3, col4 = st.columns(4)

with col1:
    users_file = st.file_uploader(
        "📁 Profils Utilisateurs", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'extract_users_09-10-2025.csv'"
    )
with col2:
    entreprises_file = st.file_uploader(
        "🏢 Profils Entreprises", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'Profil entreprises.csv'"
    )
with col3:
    relations_file = st.file_uploader(
        "🔗 Mises en relation", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'Historique des mises en relation.csv'"
    )
with col4:
    incubes_file = st.file_uploader(
        "🚀 Profils Incubés", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'Base Globale Projets.csv'"
    )

# -------------------------------
# Lecture des fichiers
# -------------------------------
users_df = load_file(users_file)
entreprises_df = load_file(entreprises_file)
relations_df = load_file(relations_file)
incubes_df = load_file(incubes_file)

# -------------------------------
# Vérification avant génération KPIs
# -------------------------------
if all([users_df is not None, entreprises_df is not None, relations_df is not None, incubes_df is not None]):
    st.header("📊 KPIs principaux")

    # --------- Utilisateurs ---------
    total_users = len(users_df)
    active_users = users_df["Statut"].str.contains("actif", case=False).sum() if "Statut" in users_df.columns else "N/A"

    # --------- Entreprises ---------
    total_entreprises = len(entreprises_df)
    entreprises_validees = entreprises_df["Statut"].str.contains("Validé", case=False).sum() if "Statut" in entreprises_df.columns else "N/A"

    # --------- Mises en relation ---------
    total_relations = len(relations_df)
    taux_relation_par_user = round(total_relations / max(total_users,1),2) if total_users > 0 else "N/A"

    # --------- Affichage KPIs ---------
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Utilisateurs inscrits", total_users)
    c2.metric("Utilisateurs actifs", active_users)
    c3.metric("Entreprises inscrites", total_entreprises)
    c4.metric("Entreprises validées", entreprises_validees)
    c5.metric("Mises en relation", total_relations)
    st.metric("Taux de relation / utilisateur", taux_relation_par_user)

    # -------------------------------
    # KPIs croisés
    # -------------------------------
    st.subheader("📌 KPIs croisés")

    # Merge utilisateurs et mises en relation
    if "Prénom" in users_df.columns and "Nom" in users_df.columns and "Utilisateur" in relations_df.columns:
        # créer une colonne "FullName" pour merge approximatif
        users_df["FullName"] = users_df["Prénom"].str.strip() + " " + users_df["Nom"].str.strip()
        relations_df["Utilisateur"] = relations_df["Utilisateur"].str.strip()
        merged_users_rel = relations_df.merge(users_df[["FullName"]], left_on="Utilisateur", right_on="FullName", how="left")
        top_users = merged_users_rel["Utilisateur"].value_counts().head(5)
        st.write("Top 5 utilisateurs avec le plus de mises en relation :")
        st.bar_chart(top_users)
    else:
        st.info("Colonnes nécessaires pour croisement utilisateurs ↔ relations manquantes")

    # Merge utilisateurs et projets incubés
    if "Prénom" in users_df.columns and "Nom" in users_df.columns and "Name" in incubes_df.columns:
        users_df["FullName"] = users_df["Prénom"].str.strip() + " " + users_df["Nom"].str.strip()
        incubes_df["FullName"] = incubes_df["Name"].str.strip() + " " + incubes_df["Nom"].str.strip()
        merged_users_incubes = users_df.merge(incubes_df[["FullName","Projet","Statut d'incubation"]], on="FullName", how="left")
        nb_users_with_project = merged_users_incubes["Projet"].notna().sum()
        st.metric("Nombre d'utilisateurs avec projet incubé", nb_users_with_project)
    else:
        st.info("Colonnes nécessaires pour croisement utilisateurs ↔ projets incubés manquantes")

    # -------------------------------
    # Graphiques
    # -------------------------------
    st.subheader("📊 Répartition par Statut d'incubation")
    if "Statut d'incubation" in incubes_df.columns:
        fig, ax = plt.subplots()
        incubes_df["Statut d'incubation"].value_counts().plot(kind="bar", ax=ax, color="orange")
        ax.set_xlabel("Statut d'incubation")
        ax.set_ylabel("Nombre")
        st.pyplot(fig)
    else:
        st.info("Colonne 'Statut d'incubation' non trouvée dans le fichier incubés")

    st.subheader("📊 Répartition des mises en relation par Statut")
    if "Statut" in relations_df.columns:
        fig2, ax2 = plt.subplots()
        relations_df["Statut"].value_counts().plot(kind="bar", ax=ax2, color="lightgreen")
        ax2.set_xlabel("Statut de la mise en relation")
        ax2.set_ylabel("Nombre")
        st.pyplot(fig2)
    else:
        st.info("Colonne 'Statut' non trouvée dans le fichier des mises en relation")

    # -------------------------------
    # Aperçu fichiers
    # -------------------------------
    with st.expander("👀 Aperçu des fichiers importés"):
        st.write("**Utilisateurs :**", users_df.head())
        st.write("**Entreprises :**", entreprises_df.head())
        st.write("**Mises en relation :**", relations_df.head())
        st.write("**Profils incubés :**", incubes_df.head())
