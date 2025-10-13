import streamlit as st
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="Lexique dynamique", layout="wide")
st.title("🗂 Lexique Dynamique - ID CLE / Mapping")

# -------------------------------
# Fonctions
# -------------------------------
def generate_id(index):
    """ Génère un ID type ID001, ID002 """
    return f"ID{str(index+1).zfill(3)}"

def create_lexique(df, col_name):
    """ Crée un lexique initial à partir d'une colonne sélectionnée """
    lexique = []
    uniques = df[col_name].dropna().unique()
    for i, val in enumerate(uniques):
        lexique.append({"ID_CLE": generate_id(i), "Nom canonical": val, "Variantes": [val]})
    return lexique

def update_lexique(lexique, df, col_name):
    """ Met à jour un lexique existant avec un nouveau fichier """
    new_lexique = lexique.copy()
    existing_variants = {v for entry in lexique for v in entry["Variantes"]}
    start_index = len(lexique)
    
    # Mapping automatique
    mapping = []
    for val in df[col_name].fillna("").unique():
        if val in existing_variants:
            # Trouve l'ID existant
            for entry in new_lexique:
                if val in entry["Variantes"]:
                    mapping.append((val, entry["ID_CLE"]))
                    break
        else:
            # Nouvelle entrée
            new_id = generate_id(start_index)
            new_lexique.append({"ID_CLE": new_id, "Nom canonical": val, "Variantes": [val]})
            mapping.append((val, new_id))
            start_index += 1
    return new_lexique, mapping

def df_with_ids(df, col_name, mapping):
    """ Ajoute une colonne ID_CLE en colonne A basée sur mapping """
    id_map = dict(mapping)
    df.insert(0, "ID_CLE", df[col_name].map(id_map).fillna("NOT_FOUND"))
    return df

# -------------------------------
# Choix du mode
# -------------------------------
mode = st.radio("Que souhaitez-vous faire ?", ["Créer un nouveau lexique", "Mettre à jour un lexique existant"])

if mode == "Créer un nouveau lexique":
    st.subheader("1️⃣ Upload fichier de référence")
    ref_file = st.file_uploader("Fichier de référence (csv/xlsx)", type=["csv","xlsx"])
    
    if ref_file:
        if ref_file.name.endswith(".xlsx"):
            df_ref = pd.read_excel(ref_file)
        else:
            df_ref = pd.read_csv(ref_file, sep=None, engine="python", encoding="cp1252")
        
        col_name = st.selectbox("Sélectionnez la colonne à utiliser pour générer les IDs", df_ref.columns)
        
        if st.button("Générer lexique"):
            lexique = create_lexique(df_ref, col_name)
            st.success("✅ Lexique créé !")
            
            # Affichage
            st.write(pd.DataFrame(lexique))
            
            # Export
            st.download_button("💾 Télécharger lexique JSON", json.dumps(lexique, ensure_ascii=False, indent=2), file_name="lexique.json")
            st.download_button("💾 Télécharger lexique CSV", pd.DataFrame(lexique).to_csv(index=False, sep=";"), file_name="lexique.csv")

elif mode == "Mettre à jour un lexique existant":
    st.subheader("1️⃣ Upload lexique existant (JSON)")
    lex_file = st.file_uploader("Lexique JSON existant", type=["json"])
    
    st.subheader("2️⃣ Upload nouveau fichier à mapper")
    new_file = st.file_uploader("Fichier à mapper (csv/xlsx)", type=["csv","xlsx"])
    
    if lex_file and new_file:
        lexique = json.load(lex_file)
        
        if new_file.name.endswith(".xlsx"):
            df_new = pd.read_excel(new_file)
        else:
            df_new = pd.read_csv(new_file, sep=None, engine="python", encoding="cp1252")
        
        col_name = st.selectbox("Sélectionnez la colonne du fichier à mapper sur le lexique", df_new.columns)
        
        if st.button("Mapper et mettre à jour lexique"):
            lexique, mapping = update_lexique(lexique, df_new, col_name)
            df_mapped = df_with_ids(df_new, col_name, mapping)
            
            st.success("✅ Fichier mappé et lexique mis à jour !")
            
            # Affichage
            st.write(df_mapped.head())
            st.write(pd.DataFrame(lexique))
            
            # Export
            st.download_button("💾 Télécharger lexique JSON mis à jour", json.dumps(lexique, ensure_ascii=False, indent=2), file_name="lexique_updated.json")
            st.download_button("💾 Télécharger fichier mappé CSV", df_mapped.to_csv(index=False, sep=";"), file_name="fichier_mappé.csv")
