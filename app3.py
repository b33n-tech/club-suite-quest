import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="KPI Generator", layout="wide")
st.title("⚡ Générateur de KPIs Quest for Change")

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

col1, col2, col3 = st.columns(3)

with col1:
    users_file = st.file_uploader(
        "📁 Profils Utilisateurs", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'extract_users_09-10-2025.csv' contenant #Id, Prénom, Nom, Statut, etc."
    )
with col2:
    entreprises_file = st.file_uploader(
        "🏢 Profils Entreprises", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'Profil entreprises.csv' avec #Id, Nom, Incubateurs, Statut, etc."
    )
with col3:
    relations_file = st.file_uploader(
        "🔗 Mises en relation", 
        type=["csv","xlsx"], 
        help="Fichier attendu : 'Historique des mises en relation.csv' contenant Utilisateur, goBetween, Statut, Dates simples"
    )

# -------------------------------
# Lecture des fichiers
# -------------------------------
users_df = load_file(users_file)
entreprises_df = load_file(entreprises_file)
relations_df = load_file(relations_file)

# -------------------------------
# Génération KPIs
# -------------------------------
if users_df is not None and entreprises_df is not None and relations_df is not None:
    st.header("📊 KPIs principaux")

    # KPI Utilisateurs
    total_users = len(users_df)
    active_users = users_df["Statut"].str.contains("actif", case=False).sum() if "Statut" in users_df.columns else "N/A"

    # KPI Entreprises
    total_entreprises = len(entreprises_df)
    entreprises_validees = entreprises_df["Statut"].str.contains("Validé", case=False).sum() if "Statut" in entreprises_df.columns else "N/A"

    # KPI Mises en relation
    total_relations = len(relations_df)
    taux_relation_par_user = round(total_relations / max(total_users,1),2) if total_users > 0 else "N/A"

    # Affichage KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Utilisateurs inscrits", total_users)
    c2.metric("Utilisateurs actifs", active_users)
    c3.metric("Entreprises inscrites", total_entreprises)
    c4.metric("Entreprises validées", entreprises_validees)
    c5.metric("Mises en relation", total_relations)
    st.metric("Taux de relation / utilisateur", taux_relation_par_user)

    # Graphiques
    st.subheader("📊 Répartition des entreprises par incubateur")
    if "Incubateurs" in entreprises_df.columns:
        fig, ax = plt.subplots()
        entreprises_df["Incubateurs"].value_counts().plot(kind="bar", ax=ax, color="skyblue")
        ax.set_xlabel("Incubateur")
        ax.set_ylabel("Nombre d'entreprises")
        st.pyplot(fig)
    else:
        st.info("Colonne 'Incubateurs' non trouvée dans le fichier entreprises. Graphique non généré.")

    st.subheader("📊 Répartition des mises en relation par statut")
    if "Statut" in relations_df.columns:
        fig2, ax2 = plt.subplots()
        relations_df["Statut"].value_counts().plot(kind="bar", ax=ax2, color="lightgreen")
        ax2.set_xlabel("Statut de la mise en relation")
        ax2.set_ylabel("Nombre")
        st.pyplot(fig2)
    else:
        st.info("Colonne 'Statut' non trouvée dans le fichier des mises en relation. Graphique non généré.")

    # Aperçu fichiers
    with st.expander("👀 Aperçu des fichiers importés"):
        st.write("**Utilisateurs :**", users_df.head())
        st.write("**Entreprises :**", entreprises_df.head())
        st.write("**Mises en relation :**", relations_df.head())
