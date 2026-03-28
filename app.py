import streamlit as st
import random
from datetime import datetime

# --- 1. ZÁKLADNÍ NASTAVENÍ ---
st.set_page_config(page_title="Moje Cesta k Hlasu", page_icon="🦋", layout="centered")

# Stylizace pro 11letou slečnu
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3em; 
        background-color: #a06cd5; color: white; border: none; font-weight: bold;
    }
    .stTextInput>div>div>input { border-radius: 15px; }
    h1, h2, h3 { color: #6e44ff; font-family: 'Segoe UI', sans-serif; text-align: center; }
    .status-box { padding: 15px; border-radius: 15px; background: white; border: 2px solid #a06cd5; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACE DAT (PAMĚŤ APLIKACE) ---
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'trusted_people' not in st.session_state: st.session_state.trusted_people = []
if 'diary_entries' not in st.session_state: st.session_state.diary_entries = []
if 'weekly_plan' not in st.session_state:
    st.session_state.weekly_plan = {d: "Naplánuj si misi 📝" for d in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]}

# Seznam tipů na mise
mission_ideas = [
    "Usmát se na paní učitelku v šatně.", "Pustit spolužačce vtipné video na mobilu.",
    "Koupit si v papírnictví jednu tužku (použít TTS).", "Mávnout na kamarádku z dálky.",
    "Odpovědět 'Ano' nebo 'Ne' na otázku (i potichu).", "Půjčit si knížku v knihovně.",
    "Zastavit se v bufetu a jen se podívat.", "Poslat hlasovku babičce z appky.",
    "Zkusit oční kontakt s prodavačkou (2 sekundy).", "Pozdravit sousedku (i šeptem)."
]

# Funkce pro mluvení
def speak(text):
    url = f"https://translate.google.com{text.replace(' ', '%20')}&tl=cs"
    st.audio(url, format="audio/mp3", autoplay=True)

# --- 3. POSTRANNÍ PANEL (OKRUH DŮVĚRY) ---
with st.sidebar:
    st.header("👥 Okruh Důvěry")
    st.write("S kým už mluvíš v pohodě?")
    new_p = st.text_input("Přidej jméno:")
    if st.button("Přidat do seznamu"):
        if new_p and new_p not in st.session_state.trusted_people:
            st.session_state.trusted_people.append(new_p)
            st.session_state.xp += 10
            st.rerun()
    
    for p in st.session_state.trusted_people:
        st.success(f"✓ {p}")

# --- 4. HLAVNÍ MENU ---
tabs = st.tabs(["🏠 Domů", "🗣️ Hlas", "📅 Plánovač", "📓 Deník"])

# --- TAB 1: DOMŮ ---
with tabs[0]:
    st.title("Ahoj hrdinko! ✨")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com", width=80)
    with col2:
        level = st.session_state.xp // 100 + 1
        st.write(f"**Level:** {level}")
        st.progress(min((st.session_state.xp % 100) / 100, 1.0))
        st.caption(f"Celkem XP: {st.session_state.xp}")

    st.markdown(f"""<div class="status-box">Mluvím s <b>{len(st.session_state.trusted_people)}</b> lidmi.</div>""", unsafe_allow_html=True)
    
    # Zobrazení dnešní mise podle aktuálního dne
    czech_days = {"Monday": "Pondělí", "Tuesday": "Úterý", "Wednesday": "Středa", "Thursday": "Čtvrtek", "Friday": "Pátek", "Saturday": "Sobota", "Sunday": "Neděle"}
    today_eng = datetime.now().strftime("%A")
    today_cz = czech_days.get(today_eng, "Pondělí")
    st.info(f"**Dnešní mise ({today_cz}):**\n\n{st.session_state.weekly_plan.get(today_cz)}")

# --- TAB 2: HLAS (TTS) ---
with tabs[1]:
    st.subheader("Hlasový spojenec 🔊")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("ANO"): speak("Ano")
        if st.button("AHOJ"): speak("Ahoj")
    with c2:
        if st.button("NE"): speak("Ne")
        if st.button("DĚKUJI"): speak("Děkuji")
    with c3:
        if st.button("PROSÍM"): speak("Prosím")
        if st.button("DOBRÝ DEN"): speak("Dobrý den")
    
    custom = st.text_input("Napiš, co chceš říct:", placeholder="Třeba: Jednu zmrzlinu...")
    if st.button("PŘEČÍST NAHLAS", type="primary"):
        if custom: speak(custom); st.session_state.xp += 5

# --- TAB 3: PLÁNOVAČ ---
with tabs[2]:
    st.subheader("📅 Plánovač Odvahy")
    with st.expander("💡 Inspirace na mise"):
        if st.button("Vygeneruj náhodný tip"):
            st.info(random.choice(mission_ideas))
        st.write(mission_ideas)

    st.write("Co zkusíš tento týden?")
    c_left, c_right = st.columns(2)
    days = list(st.session_state.weekly_plan.keys())
    for i, day in enumerate(days):
        col = c_left if i < 4 else c_right
        st.session_state.weekly_plan[day] = col.text_input(f"{day}:", value=st.session_state.weekly_plan[day], key=f"plan_{day}")
    
    if st.button("Uložit můj týden 🔒"):
        st.session_state.xp += 20
        st.success("Plán uložen! Jsi připravená.")

# --- TAB 4: DENÍK ---
with tabs[3]:
    st.subheader("📓 Deník vítězství")
    with st.form("diary"):
        text = st.text_area("Co se ti dnes povedlo?")
        diff = st.select_slider("Obtížnost:", options=["Pohoda", "Úzkost", "Výzva", "Hrdinka!"])
        if st.form_submit_button("Uložit zápis"):
            if text:
                st.session_state.diary_entries.insert(0, {"date": datetime.now().strftime("%d.%m."), "text": text, "diff": diff})
                st.session_state.xp += 30
                st.balloons()
    
    for e in st.session_state.diary_entries:
        st.write(f"**{e['date']}** ({e['diff']}): {e['text']}")
        st.divider()
