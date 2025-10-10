import streamlit as st

st.title("📚 Tutoriel - Comment ça marche ?")
st.markdown("""
Ce tutoriel vous présente **pas à pas** les fichiers à importer et l'objectif de chaque étape.
""")

steps = [
    {"title":"1️⃣ Profils individuels", "desc":"Contient tous les profils inscrits sur la marketplace."},
    {"title":"2️⃣ Profils entreprises", "desc":"Contient toutes les entreprises inscrites."},
    {"title":"3️⃣ Historique des mises en relation", "desc":"Suivi des interactions entre profils et entreprises."},
    {"title":"4️⃣ Base Globale Projets", "desc":"Base interne des projets incubés pour croiser les données."}
]

for step in steps:
    with st.expander(step["title"]):
        st.write(step["desc"])

st.markdown("🔙 Cliquez sur le bouton 'Retour à l'accueil' dans la barre du hub pour revenir à la page principale.")
