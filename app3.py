import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="KPI Generator", layout="wide")
st.title("⚡ Générateur de KPIs Quest for Change")

# -------------------------------
# Fonction de lecture CSV
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
    users_file = st.file_uploader("📁 Profils Utilisateurs", type=["csv","xlsx"])
with col2:
    entreprises_file = st.file_uploader("🏢 Profils Entreprises", type=["csv","xlsx"])
with col3:
    relations_file = st.file_uploader("🔗 Mises en relation", type=["csv","xlsx"])

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
    st.header("📊 KPIs")

    # KPI simples
    total_users = len(users_df)
    total_entreprises = len(entreprises_df)
    total_relations = len(relations_df)
    taux_relation = round(total_relations / max(total_users,1), 2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Utilisateurs", total_users)
    c2.metric("Entreprises", total_entreprises)
    c3.metric("Mises en relation", total_relations)
    c4.metric("Taux de relation / utilisateur", taux_relation)

    # -------------------------------
    # Graphique simple : Répartition entreprises par incubateur
    # -------------------------------
    st.subheader("🏗️ Répartition des entreprises par incubateur")
    if "Incubateurs" in entreprises_df.columns:
        fig, ax = plt.subplots()
        entreprises_df["Incubateurs"].value_counts().plot(kind="bar", ax=ax, color="skyblue")
        ax.set_xlabel("Incubateur")
        ax.set_ylabel("Nombre d'entreprises")
        st.pyplot(fig)
    else:
        st.info("La colonne 'Incubateurs' n'a pas été trouvée dans le fichier entreprises.")

    # -------------------------------
    # Aperçu des données
    # -------------------------------
    with st.expander("👀 Aperçu des fichiers importés"):
        st.write("**Utilisateurs :**", users_df.head())
        st.write("**Entreprises :**", entreprises_df.head())
        st.write("**Mises en relation :**", relations_df.head())
