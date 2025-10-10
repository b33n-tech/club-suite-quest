import streamlit as st

st.set_page_config(page_title="Dashboard Quest for Change", layout="wide")
st.title("🚀 Dashboard Quest for Change")

st.markdown("""
Bienvenue sur le Dashboard Quest for Change !  
Cet outil vous permet de visualiser vos indicateurs clés à partir des fichiers de la marketplace et de l'incubateur.
""")

# --- Deux boîtes interactives ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="
            padding:30px; 
            background-color:#00796B; 
            color:white; 
            border-radius:15px; 
            text-align:center;
        ">
        <h2>📚 Découvrir comment ça marche</h2>
        <p>Consultez le tutoriel interactif pour comprendre le workflow et les fichiers à importer.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Découvrir le tutoriel"):
        st.experimental_set_query_params(page="tutorial")

with col2:
    st.markdown(
        """
        <div style="
            padding:30px; 
            background-color:#F57C00; 
            color:white; 
            border-radius:15px; 
            text-align:center;
        ">
        <h2>⚡ Produire vos KPIs</h2>
        <p>Importez vos fichiers et générez vos KPIs étape par étape.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Commencer"):
        st.experimental_set_query_params(page="workflow")

# --- Navigation basée sur query_params ---
query_params = st.experimental_get_query_params()
if "page" in query_params:
    page = query_params["page"][0]
    if page == "tutorial":
        import tutorial
    elif page == "workflow":
        import app
