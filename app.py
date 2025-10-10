import chardet
import io

def load_file(file):
    """Lecture tolérante CSV/Excel avec détection automatique de l'encodage."""
    if file is None:
        return None
    try:
        if file.name.endswith(".xlsx"):
            return pd.read_excel(file)

        # Lire les octets bruts
        raw = file.read()
        file.seek(0)

        # Détecter l'encodage
        detected = chardet.detect(raw)
        enc = detected["encoding"] or "latin1"

        # Essais multiples de séparateurs
        seps = [";", ",", "\t", "|"]

        for sep in seps:
            try:
                df = pd.read_csv(io.BytesIO(raw), sep=sep, encoding=enc, on_bad_lines="skip")
                if df.shape[1] > 1:
                    st.caption(f"✅ {file.name} lu avec encodage **{enc}**, séparateur **'{sep}'**")
                    return df
            except Exception:
                continue

        st.error(f"❌ Fichier {file.name} non lisible même après détection d'encodage ({enc}).")
        return None

    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier {file.name} : {e}")
        return None
