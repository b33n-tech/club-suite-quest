import pandas as pd
from rapidfuzz import process, fuzz
import unidecode

def normalize_str(s):
    s = str(s).lower().strip()
    s = unidecode.unidecode(s)  # retire accents
    s = s.replace(" ", "_")
    return s

# Prétraitement lexique et nouveau fichier
lexique_vals = [normalize_str(x) for x in lexique_nom_list]
new_vals = [normalize_str(x) for x in new_file_col]

mapping = []
for val, orig in zip(new_vals, new_file_col):
    match, score, idx = process.extractOne(val, lexique_vals, scorer=fuzz.ratio)
    if score >= 90:  # seuil de confiance
        mapping.append((orig, lexique_ids[idx]))
    else:
        # Nouvelle entrée
        new_id = generate_id(len(lexique))
        lexique.append({"ID_CLE": new_id, "Nom canonical": orig, "Variantes": [orig]})
        lexique_vals.append(val)
        lexique_ids.append(new_id)
        mapping.append((orig, new_id))
