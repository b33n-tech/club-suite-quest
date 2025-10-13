import streamlit as st
import pandas as pd
import json
from io import StringIO
from rapidfuzz import process, fuzz
import unidecode

st.set_page_config(page_title="Lexique Dynamique", layout="wide")
st.title("🗂 Lexique Dynamique - ID CLE / Mapping")

# -------------------------------
# Fonctions
# -------------------------------

def normalize_str(s):
    """ Normalise une string pour comparaison flexible """
    s = str(s).lower().strip()
    s = unidecode.unidecode(s)  # retire accents
    s = s.replace(" ", "_")
    return s

def generate_id(index):
    """ Génère un ID type ID001 """
    return f"ID{str(index+1).zfill(3)}"

def create_lexique(df, col_name):
    """ Crée un lexique initial à partir d'une colonne sélectionnée """
    lexique = []
    uniques = df[col_name].dropna().unique()
    for i, val in enumerate(uniques):
        lexique.append({"ID_CLE": generate_id(i), "Nom canonical": val, "Variantes": [val]})
    return lexique

def update_lexique_fuzzy(lexique, df, col_name, threshold=90):
    """ Met à jour un lexique existant avec un nouveau fichier, mapping fuzzy """
    lexique_vals = [normalize_str(entry["Nom canonical"]) for entry in lexique]
    lexique_ids  = [entry["ID_CLE"] for entry in lexique]
    
    new_file_col = df[col_name].fillna("")
    new_vals = [normalize_str(x) for x in new_file_col]
    
    mapping = []
    start_index = len(lexique)
    
    for val, orig in zip(new_vals, new_file_col):
        match, score, idx = process.extractOne(val, lexique_vals, scorer=fuzz.ratio)
        if score >= threshold:
            # Correspondance trouvée
            mapping.append((orig, lexique_ids[idx]))
        else:
            # Nouvelle entrée
            new_id = generate_id(start_index)
            lexique.append({"ID_CLE": new_id, "Nom canonical": orig, "Variantes": [orig]})
            lexique_vals.append(val)
            lexique_ids.append(new_id)
            mapping.append((orig, new_id))
            start_index += 1
    return lexique, mapping

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
        try:
            if ref_file.name.endswith(".xlsx"):
                df_ref = pd.read_excel(ref_file)
            else:
                df_ref = pd.read_csv(ref_file, sep=None, engine="python", encoding="cp1252")
            
            col_name = st.selectbox("Sélectionnez la colonne à utiliser pour générer les IDs", df_ref.columns)
            
            if st.button("Générer lexique"):
                lexique = create_lexique(df_ref, col_name)
                st.success("✅ Lexique créé !")
                
                st.write(pd.DataFrame(lexique))
                
                st.download_button("💾 Télécharger lexique JSON", json.dumps(lexique, ensure_ascii=False, indent=2), file_name="lexique.json")
                st.download_button("💾 Télécharger lexique CSV", pd.DataFrame(lexique).to_csv(index=False, sep=";"), file_name="lexique.csv")
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

elif mode == "Mettre à jour un lexique existant":
    st.subheader("1️⃣ Upload lexique existant (JSON)")
    lex_file = st.file_uploader("Lexique JSON existant", type=["json"])
    
    st.subheader("2️⃣ Upload nouveau fichier à mapper")
    new_file = st.file_uploader("Fichier à mapper (csv/xlsx)", type=["csv","xlsx"])
    
    if lex_file and new_file:
        try:
            lexique = json.load(lex_file)
            
            if new_file.name.endswith(".xlsx"):
                df_new = pd.read_excel(new_file)
            else:
                df_new = pd.read_csv(new_file, sep=None, engine="python", encoding="cp1252")
            
            col_name = st.selectbox("Sélectionnez la colonne du fichier à mapper sur le lexique", df_new.columns)
            
            threshold = st.slider("Seuil de correspondance fuzzy (%)", 80, 100, 90)
            
            if st.button("Mapper et mettre à jour lexique"):
                lexique, mapping = update_lexique_fuzzy(lexique, df_new, col_name, threshold)
                df_mapped = df_with_ids(df_new, col_name, mapping)
                
                st.success("✅ Fichier mappé et lexique mis à jour !")
                
                st.write("### Aperçu fichier mappé")
                st.write(df_mapped.head())
                
                st.write("### Aperçu lexique mis à jour")
                st.write(pd.DataFrame(lexique))
                
                st.download_button("💾 Télécharger lexique JSON mis à jour", json.dumps(lexique, ensure_ascii=False, indent=2), file_name="lexique_updated.json")
                st.download_button("💾 Télécharger fichier mappé CSV", df_mapped.to_csv(index=False, sep=";"), file_name="fichier_mappé.csv")
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
