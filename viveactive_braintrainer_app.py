
import streamlit as st
import pandas as pd
import random

# Laad vraagdata uit CSV (ingebakken fallback)
@st.cache_data
def laad_vragen(csv_path=None):
    if csv_path is not None:
        df = pd.read_csv(csv_path)
    else:
        data = {
            "categorie": [], "moeilijkheid": [], "vraag": [], "optie_a": [], "optie_b": [], "optie_c": [], "optie_d": [], "correcte_optie": []
        }
        basisvragen = [
            ("Logisch redeneren", 1, "Wat volgt logisch uit: alle X zijn Y en geen Y is Z?", "X zijn Z", "Sommige X zijn Z", "Geen X is Z", "Alle Z zijn X", "C"),
            ("Taalvaardigheid", 2, "Wat is het meervoud van 'crisis'?", "crisisen", "crisissen", "crisi", "crises", "D"),
            ("Rekenen", 1, "Wat is 25% van 240?", "60", "50", "55", "65", "A"),
            ("Algemene kennis", 3, "Wat is de hoofdstad van Noorwegen?", "Helsinki", "Oslo", "Stockholm", "Kopenhagen", "B")
        ]
        for _ in range(75):
            for vraag in basisvragen:
                cat, level, v, a, b, c, d, correct = vraag
                data["categorie"].append(cat)
                data["moeilijkheid"].append(level)
                data["vraag"].append(v)
                data["optie_a"].append(a)
                data["optie_b"].append(b)
                data["optie_c"].append(c)
                data["optie_d"].append(d)
                data["correcte_optie"].append(correct)
        df = pd.DataFrame(data)
    return df

# Selecteer willekeurige vragen op moeilijkheid
def selecteer_vragen(df, niveau, aantal=10):
    df_filtered = df[df['moeilijkheid'] == niveau]
    return df_filtered.sample(n=min(aantal, len(df_filtered))).reset_index(drop=True)

# Streamlit-app
st.title("🧠 Niveau 2 Braintrainer - Thema's & Moeilijkheidsniveaus")

# Upload-optie of standaard gebruiken
vragen_csv = st.file_uploader("Upload een aangepaste CSV (optioneel):", type="csv")
df_vragen = laad_vragen(vragen_csv if vragen_csv else None)

# Moeilijkheidsniveau kiezen
niveau = st.selectbox("Kies moeilijkheidsgraad:", [1, 2, 3], format_func=lambda x: {1: "Niveau 1", 2: "Niveau 2", 3: "Niveau 3"}[x])

# Quiz starten via knop
if st.button("Start nieuwe quiz"):
    st.session_state.vragen = selecteer_vragen(df_vragen, niveau)
    st.session_state.antwoorden = []
    st.session_state.score = 0
    st.session_state.quiz_actief = True

# Toon quiz als deze gestart is
if st.session_state.get("quiz_actief", False):
    vragen = st.session_state.vragen
    st.subheader("10 willekeurige vragen")
    for i, rij in vragen.iterrows():
        st.markdown(f"**Vraag {i+1} ({rij['categorie']}):** {rij['vraag']}")
        keuze = st.radio(
            label="",
            options=[rij['optie_a'], rij['optie_b'], rij['optie_c'], rij['optie_d']],
            key=f"vraag_{i}"
        )
        if len(st.session_state.antwoorden) <= i:
            st.session_state.antwoorden.append(keuze)
        else:
            st.session_state.antwoorden[i] = keuze
        if keuze == rij[f"optie_{rij['correcte_optie'].lower()}"]:
            st.session_state.score += 1

    # Resultaten tonen
    if st.button("Bekijk resultaat"):
        st.success(f"Je scoorde {st.session_state.score} van de {len(vragen)}!")
        if 'scoregeschiedenis' not in st.session_state:
            st.session_state.scoregeschiedenis = []
        st.session_state.scoregeschiedenis.append((niveau, st.session_state.score, len(vragen)))
        st.session_state.quiz_actief = False

# Toon geschiedenis
if 'scoregeschiedenis' in st.session_state:
    st.markdown("### 📊 Scoregeschiedenis")
    for i, (niveau, s, totaal) in enumerate(st.session_state.scoregeschiedenis):
        st.write(f"{i+1}. Niveau {niveau}: Score {s}/{totaal}")
