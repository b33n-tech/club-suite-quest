import streamlit as st

st.title("📚 Tutoriel - Comment ça marche ?")

steps = [
    {"title":"1️⃣ Profils individuels", "desc":"Contient tous les profils inscrits sur la marketplace."},
    {"title":"2️⃣ Profils entreprises", "desc":"Contient toutes les entreprises inscrites."},
    {"title":"3️⃣ Historique des mises en relation", "desc":"Suivi des interactions."},
    {"title":"4️⃣ Base Globale Projets", "desc":"Base interne des projets incubés."}
]

for step in steps:
    with st.expander(step["title"]):
        st.write(step["desc"])
