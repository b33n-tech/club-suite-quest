import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Dashboard Quest for Change - Prototype UX Friendly")
st.markdown(
    "Suivez les étapes ci-dessous pour uploader vos fichiers et générer vos KPIs. "
    "Chaque étape est guidée pour que tout soit clair en une seconde."
)

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
# Paramètres des étapes + couleurs foncées pour dark mode
# -------------------------------
steps_info = [
    {"label": "📁 Profils individuels Le Club",
     "desc": "Importez le fichier 'extract_users_xxx.csv'. Contient tous les profils inscrits.",
     "bg_color": "#00796B", "text_color": "#ffffff"},
    {"label": "🏢 Profils Entreprises Le Club",
     "desc": "Importez le fichier 'Profil entreprises.csv'. Contient toutes les entreprises.",
     "bg_color": "#F57C00", "text_color": "#ffffff"},
    {"label": "🔗 Historique des mises en relation",
     "desc": "Importez le fichier 'Historique des mises en relation.csv'. Contient toutes les interactions.",
     "bg_color": "#D32F2F", "text_color": "#ffffff"},
    {"label": "🧭 Base Globale Projets",
     "desc": "Importez la base interne des projets incubés pour croiser les données.",
     "bg_color": "#512DA8", "text_color": "#ffffff"}
]

# -------------------------------
# Barre de progression
# -------------------------------
progress = st.progress(st.session_state.step / len(steps_info))

# -------------------------------
# Upload étape courante
# -------------------------------
if st.session_state.step < len(steps_info):
    step = steps_info[st.session_state.step]
    st.subheader(f"Étape {st.session_state.step + 1} sur {len(steps_info)}")

    # Card style
    st.markdown(
        f"""
        <div style="
            padding:20px; 
            background-color:{step['bg_color']}; 
            color:{step['text_color']}; 
            border-radius:10px; 
            margin-bottom:20px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        ">
        <h3>{step['label']}</h3>
        <p>{step['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("", type=["csv","xlsx"], key=f"upload_{st.session_state.step}")

    if uploaded_file is not None:
        with st.spinner("📂 Lecture du fichier..."):
            time.sleep(1)  # effet “animation” chargement
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
