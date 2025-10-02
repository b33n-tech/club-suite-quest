
# Streamlit app: QfC Marketplace KPI Tool
# Single-file Streamlit application to upload 3-4 CSV exports, auto-detect columns,
# produce quick KPIs and allow simple cross-database joins with minimal user actions.
# Usage: pip install -r requirements.txt
# requirements.txt suggestions: streamlit pandas altair python-dateutil

import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime
import altair as alt
import difflib
import base64

st.set_page_config(page_title="QfC Marketplace KPI Tool", layout="wide")

# ---------- Helper functions ----------
POSSIBLE_PROFILE_COLS = {
    'id': ['id', 'profile_id', 'user_id', 'uid'],
    'email': ['email', 'e-mail', 'mail'],
    'name': ['name', 'full_name', 'fullname', 'nom', 'prenom_nom'],
    'firstname': ['first_name', 'prenom'],
    'lastname': ['last_name', 'nom'],
    'company_id': ['company_id', 'startup_id', 'organisation_id', 'organisation', 'entreprise_id']
}

POSSIBLE_STARTUP_COLS = {
    'id': ['id', 'startup_id', 'company_id', 'organisation_id'],
    'name': ['name', 'company_name', 'startup_name', 'entreprise'],
    'sector': ['sector', 'secteur', 'industry'],
    'status': ['status', 'stage', 'etat']
}

POSSIBLE_MATCH_COLS = {
    'id': ['id', 'match_id', 'relation_id'],
    'profile_id': ['profile_id', 'user_id', 'uid'],
    'startup_id': ['startup_id', 'company_id', 'organisation_id'],
    'date': ['date', 'created_at', 'timestamp', 'match_date']
}


def read_csv_infer(uploaded_file):
    """Read CSV robustly and return df. If reading fails, try different encodings."""
    try:
        return pd.read_csv(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding='latin1')


def guess_columns(df, mapping_candidates):
    """Return a dict mapping standardized keys to actual df columns (or None)."""
    cols = {c.lower(): c for c in df.columns}
    result = {}
    for key, candidates in mapping_candidates.items():
        found = None
        for cand in candidates:
            cand_lower = cand.lower()
            if cand_lower in cols:
                found = cols[cand_lower]
                break
        if not found:
            # try fuzzy match
            close = difflib.get_close_matches(key, list(cols.keys()), n=1, cutoff=0.8)
            if close:
                found = cols[close[0]]
        result[key] = found
    return result


def summarize_df(df):
    return pd.DataFrame({
        'columns': df.columns,
        'non_null_count': df.notnull().sum().values,
        'unique_values': [df[c].nunique(dropna=True) for c in df.columns]
    })


def safe_parse_dates(ser):
    try:
        return pd.to_datetime(ser, errors='coerce')
    except Exception:
        return pd.to_datetime(ser.astype(str), errors='coerce')


def fuzzy_join(left_df, right_df, left_on, right_on, thresh=0.85):
    """Perform a fuzzy join by matching strings between two columns using difflib.
    Returns merged df where match_score >= thresh.
    This is a best-effort for non-technical users; primary keys (id/email) are used first."""
    left = left_df.copy()
    right = right_df.copy()
    left_series = left[left_on].fillna('').astype(str)
    right_series = right[right_on].fillna('').astype(str)
    right_vals = right_series.unique().tolist()
    matches = []
    for i, val in enumerate(left_series):
        if val == '':
            matches.append((i, None, 0.0))
            continue
        # try exact first
        if val in right_vals:
            matches.append((i, val, 1.0))
            continue
        close = difflib.get_close_matches(val, right_vals, n=1, cutoff=thresh)
        if close:
            matches.append((i, close[0], difflib.SequenceMatcher(None, val, close[0]).ratio()))
        else:
            matches.append((i, None, 0.0))
    # Build mapping and merge
    match_map = {}
    for i, matched_val, score in matches:
        if matched_val is not None:
            match_map[left.index[i]] = matched_val
    left['_fuzzy_matched_value'] = pd.Series(match_map)
    merged = left.merge(right, left_on='_fuzzy_matched_value', right_on=right_on, how='left', suffixes=('_l', '_r'))
    return merged, pd.Series([m[2] for m in matches], index=left.index)


# ---------- UI ----------
st.title("QfC Marketplace — Outil KPI rapide")
st.write("Chargez simplement les exports CSV (pas besoin d'ouvrir/éditer). L'outil détectera les colonnes et produira un reporting basique.")

st.markdown("---")

col1, col2 = st.columns([1,1])
with col1:
    st.header("1) Profils (profiles)")
    profiles_file = st.file_uploader("Glisser/déposer le CSV Profils", type=['csv'], key='profiles')
    st.write("Exemples de colonnes attendues: email, name, id, company_id")
with col2:
    st.header("2) Startups / Entreprises (startups)")
    startups_file = st.file_uploader("Glisser/déposer le CSV Startups", type=['csv'], key='startups')
    st.write("Exemples: id, name, sector, status")

col3, col4 = st.columns([1,1])
with col3:
    st.header("3) Mises en relation (matches)")
    matches_file = st.file_uploader("Glisser/déposer le CSV Mises en relation", type=['csv'], key='matches')
    st.write("Exemples: profile_id, startup_id, date")
with col4:
    st.header("(Optionnel) 4) Base interne startups incubées")
    internal_file = st.file_uploader("Glisser/déposer le CSV Startups internes (optionnel)", type=['csv'], key='internal')
    st.write("Permet de croiser qui est incubé vs marketplace")

st.markdown("---")

if st.button('Générer le rapport (1 clic)'):
    # Read files (if present)
    dfs = {}
    try:
        if profiles_file is not None:
            profiles_file.seek(0)
            df_profiles = read_csv_infer(profiles_file)
            dfs['profiles'] = df_profiles
        else:
            dfs['profiles'] = None
        if startups_file is not None:
            startups_file.seek(0)
            df_startups = read_csv_infer(startups_file)
            dfs['startups'] = df_startups
        else:
            dfs['startups'] = None
        if matches_file is not None:
            matches_file.seek(0)
            df_matches = read_csv_infer(matches_file)
            dfs['matches'] = df_matches
        else:
            dfs['matches'] = None
        if internal_file is not None:
            internal_file.seek(0)
            df_internal = read_csv_infer(internal_file)
            dfs['internal'] = df_internal
        else:
            dfs['internal'] = None
    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers: {e}")
        st.stop()

    st.success('Fichiers lus — détection des colonnes en cours...')

    # Infer columns
    mappings = {}
    if dfs['profiles'] is not None:
        mappings['profiles'] = guess_columns(dfs['profiles'], POSSIBLE_PROFILE_COLS)
    if dfs['startups'] is not None:
        mappings['startups'] = guess_columns(dfs['startups'], POSSIBLE_STARTUP_COLS)
    if dfs['matches'] is not None:
        mappings['matches'] = guess_columns(dfs['matches'], POSSIBLE_MATCH_COLS)
    if dfs.get('internal') is not None:
        mappings['internal'] = guess_columns(dfs['internal'], POSSIBLE_STARTUP_COLS)

    st.write("### Résumé des imports")
    for k, df in dfs.items():
        if df is None:
            st.write(f"- {k}: pas fourni")
        else:
            st.write(f"- {k}: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    st.markdown("---")

    # Show column inference and allow minimal override
    st.write("### Détection automatique des colonnes (vérifiez / corrigez si nécessaire)")
    overrides = {}
    for key, mapping in mappings.items():
        if mapping is None:
            continue
        st.write(f"**{key}**")
        df = dfs[key]
        cols = df.columns.tolist()
        cols_display = {c: c for c in cols}
        for std_key, guessed in mapping.items():
            guessed_display = guessed if guessed is not None else "(non détecté)"
            chosen = st.selectbox(f"{key} → {std_key}", options=["(aucun)"] + cols, index=(cols.index(guessed) + 1 if guessed in cols else 0), key=f"sel_{key}_{std_key}")
            if chosen == "(aucun)":
                overrides[(key, std_key)] = None
            else:
                overrides[(key, std_key)] = chosen
    st.markdown("---")

    # Build standardized views
    prof = dfs['profiles']
    stp = dfs['startups']
    mct = dfs['matches']
    internal = dfs.get('internal')

    def get_col(key_name, std_key):
        val = overrides.get((key_name, std_key))
        return val

    # KPI computations
    st.write("## KPIs — Aperçu rapide")
    k1, k2, k3, k4 = st.columns(4)
    # total profiles
    total_profiles = prof.shape[0] if prof is not None else 0
    k1.metric("Profiles importés", str(total_profiles))
    total_startups = stp.shape[0] if stp is not None else 0
    k2.metric("Startups importées", str(total_startups))
    total_matches = mct.shape[0] if mct is not None else 0
    k3.metric("Mises en relation", str(total_matches))
    incubated = "—"
    if internal is not None and stp is not None:
        incubated = f"{internal.shape[0]} (internes)"
    k4.metric("Startups incubées (fichier interne)", incubated)

    st.markdown("---")

    # Matches time series if date exists
    if mct is not None:
        date_col = get_col('matches', 'date') or mappings['matches'].get('date')
        if date_col:
            try:
                mct['_parsed_date'] = safe_parse_dates(mct[date_col])
                ts = mct.groupby(pd.Grouper(key='_parsed_date', freq='W'))['id' if 'id' in mct.columns else mct.columns[0]].count().reset_index(name='count')
                ts = ts.dropna()
                if not ts.empty:
                    st.write('### Série temporelle: mises en relation')
                    chart = alt.Chart(ts).mark_line(point=True).encode(x=' _parsed_date:T', y='count:Q').properties(width=700, height=300)
                    st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.write('Impossible de produire la série temporelle:', e)

    # Cross-database join examples
    st.write('## Croisements simples')

    # 1) Matches enriched with profiles and startups via IDs or fuzzy matching
    if mct is not None:
        st.write('### Enrichir les mises en relation')
        # Try exact id join first
        mp = mct.copy()
        p_id_col = get_col('profiles', 'id') or mappings['profiles'].get('id')
        p_email_col = get_col('profiles', 'email') or mappings['profiles'].get('email')
        s_id_col = get_col('startups', 'id') or mappings['startups'].get('id')
        s_name_col = get_col('startups', 'name') or mappings['startups'].get('name')

        joined = mp.copy()
        # attach profiles by profile_id
        if mappings['matches'].get('profile_id') and p_id_col and mappings['profiles'].get('id'):
            try:
                joined = joined.merge(prof, left_on=overrides.get(('matches', 'profile_id')) or mappings['matches'].get('profile_id'), right_on=overrides.get(('profiles', 'id')) or mappings['profiles'].get('id'), how='left', suffixes=('_match','_profile'))
            except Exception:
                pass
        # attach startups by startup_id
        if mappings['matches'].get('startup_id') and s_id_col:
            try:
                joined = joined.merge(stp, left_on=overrides.get(('matches', 'startup_id')) or mappings['matches'].get('startup_id'), right_on=overrides.get(('startups', 'id')) or mappings['startups'].get('id'), how='left', suffixes=('','_startup'))
            except Exception:
                pass

        st.write('Aperçu des relations enrichies (quelques lignes):')
        st.dataframe(joined.head(10))

        # compute top startups by number of matches
        try:
            startup_name_col = overrides.get(('startups','name')) or mappings['startups'].get('name')
            agg = joined.groupby(startup_name_col).size().reset_index(name='matches_count').sort_values('matches_count', ascending=False).head(10)
            st.write('Top startups par nombre de mises en relation:')
            st.table(agg)
        except Exception:
            st.write('Impossible de calculer le top startups — vérifiez les colonnes détectées.')

    # 2) Cross between marketplace startups and internal incubated startups
    if stp is not None and internal is not None:
        st.write('### Croisement: marketplace vs interne (fuzzy si besoin)')
        # try matching by id first
        stp_id = overrides.get(('startups','id')) or mappings['startups'].get('id')
        int_id = overrides.get(('internal','id')) or mappings['internal'].get('id')
        stp_name = overrides.get(('startups','name')) or mappings['startups'].get('name')
        int_name = overrides.get(('internal','name')) or mappings['internal'].get('name')

        if stp_id and int_id and stp_id == int_id:
            merged_internal = stp.merge(internal, on=stp_id, how='left', indicator=True)
        else:
            # fuzzy join on name
            merged_internal, scores = fuzzy_join(stp, internal, stp_name, int_name, thresh=0.85)
            merged_internal['_match_score'] = scores
        st.write('Extrait du croisement (quelques lignes):')
        st.dataframe(merged_internal.head(10))
        try:
            count_incubated = merged_internal['_match_score'].notnull().sum() if '_match_score' in merged_internal.columns else (merged_internal['_merge']=='both').sum()
            st.write(f'Startups appariées (estimation): {count_incubated} / {stp.shape[0]}')
        except Exception:
            pass

    # Provide download of a cleaned merged CSV for directors
    if mct is not None:
        try:
            csv_bytes = joined.to_csv(index=False).encode('utf-8')
            b64 = base64.b64encode(csv_bytes).decode()
            href = f"data:file/csv;base64,{b64}"
            st.markdown(f"[Télécharger les mises en relation enrichies](%s){'' % href}")
        except Exception:
            pass

    st.write('---')
    st.write('Fin du rapport. Si certaines colonnes n\'ont pas été détectées correctement, rechargez le CSV ou corrigez les sélections puis relancez.')

    st.success('Rapport généré.')

else:
    st.info('Chargez les fichiers puis cliquez sur "Générer le rapport (1 clic)".')

# Footer
st.markdown("---")
st.caption("Outil initial (MVP) — améliorable : ajout d'auth, de sauvegarde, de mapping persistant, et d'algorithmes de matching avancés.")
