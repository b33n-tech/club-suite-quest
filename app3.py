import streamlit as st

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")

# --- Initialisation page ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Page d'accueil ---
if st.session_state.page == "home":
    st.title("🚀 Dashboard Quest for Change")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<div style='padding:30px; background-color:#00796B; color:white; border-radius:15px; text-align:center;'>"
            "<h2>📚 Découvrir comment ça marche</h2>"
            "<p>Consultez le tutoriel interactif pour comprendre le workflow et les fichiers à importer.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("Découvrir le tutoriel"):
            st.session_state.page = "tutorial"

    with col2:
        st.markdown(
            "<div style='padding:30px; background-color:#F57C00; color:white; border-radius:15px; text-align:center;'>"
            "<h2>⚡ Produire vos KPIs</h2>"
            "<p>Importez vos fichiers et générez vos KPIs étape par étape.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("Commencer"):
            st.session_state.page = "workflow"

# --- Tutoriel ---
if st.session_state.page == "tutorial":
    import tutorial  # ton script tutoriel
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "home"

# --- Workflow KPI ---
if st.session_state.page == "workflow":
    import app  # ton script KPI
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "home"
