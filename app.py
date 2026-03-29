import streamlit as st
import json
import os
import io
import base64
from gtts import gTTS
from datetime import datetime

# --- 1. ZÁKLADNÍ NASTAVENÍ A TRVALÁ PAMĚŤ ---
st.set_page_config(page_title="Moje Cesta k Hlasu", page_icon="🦋", layout="centered")
DATA_FILE = "moje_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ošetření starších verzí souboru
                if "mission_history" not in data: data["mission_history"] = []
                if "completed_days" not in data: data["completed_days"] = []
                return data
        except: pass
    return {
        "xp": 0, "trusted_people": [], "diary_entries": [], "mission_history": [], "completed_days": [],
        "weekly_plan": {d: "Naplánuj si misi 📝" for d in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]}
    }

def save_data():
    data = {
        "xp": st.session_state.xp, 
        "trusted_people": st.session_state.trusted_people,
        "diary_entries": st.session_state.diary_entries, 
        "weekly_plan": st.session_state.weekly_plan,
        "mission_history": st.session_state.mission_history,
        "completed_days": st.session_state.completed_days
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'initialized' not in st.session_state:
    saved = load_data()
    for k, v in saved.items(): st.session_state[k] = v
    st.session_state.initialized = True

# --- 2. FUNKCE PRO ZVUK ---
def speak(text):
    if text:
        try:
            tts = gTTS(text=text, lang='cs')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            b64 = base64.b64encode(fp.getvalue()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except: st.error("Chyba zvuku")

# --- 3. STYLIZACE ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    .status-box { padding: 15px; border-radius: 15px; background: white; border: 2px solid #a06cd5; text-align: center; margin-bottom: 10px;}
    .done-mission { text-decoration: line-through; color: #aaa; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HLAVNÍ MENU ---
tabs = st.tabs(["🏠 Domů", "🗣️ Hlas", "📅 Plánovač", "📈 Historie"])

# Pomocné dny
dny = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]

with tabs[0]:
    st.title("Moje Cesta 🦋")
    st.markdown(f'<div class="status-box"><b>Level {st.session_state.xp // 100 + 1}</b> | {st.session_state.xp} XP</div>', unsafe_allow_html=True)
    st.progress(min((st.session_state.xp % 100) / 100, 1.0))

with tabs[1]:
    st.subheader("Rychlá mluva 🔊")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("AHOJ 👋"): speak("Ahoj")
        if st.button("DĚKUJI ❤️"): speak("Děkuji")
    with c2:
        if st.button("PROSÍM 🙏"): speak("Prosím")
        if st.button("ANO ✅"): speak("Ano")

with tabs[2]:
    st.subheader("📅 Týdenní plán misí")
    
    for d in dny:
        col1, col2 = st.columns([3, 1])
        is_done = d in st.session_state.completed_days
        
        with col1:
            if is_done:
                st.markdown(f"**{d}:** <span class='done-mission'>{st.session_state.weekly_plan[d]}</span> ✅", unsafe_allow_html=True)
            else:
                st.session_state.weekly_plan[d] = st.text_input(f"Mise na {d}:", value=st.session_state.weekly_plan[d], key=f"in_{d}")
        
        with col2:
            if not is_done and st.button("HOTOVO 🏆", key=f"btn_{d}"):
                st.session_state.current_completing_day = d
                st.rerun()

    # Okno pro dokončení mise (Mood Tracker)
    if 'current_completing_day' in st.session_state:
        day_to_finish = st.session_state.current_completing_day
        st.divider()
        st.subheader(f"Dokončení mise: {st.session_state.weekly_plan[day_to_finish]}")
        
        m_before = st.select_slider("Nálada PŘED:", options=["😢", "😟", "😐", "🙂", "😊"], value="😐", key="mb")
        m_after = st.select_slider("Nálada PO:", options=["😢", "😟", "😐", "🙂", "😊"], value="😊", key="ma")
        
        if st.button("Potvrdit a uložit body! ✨"):
            # Uložit do historie
            st.session_state.mission_history.append({
                "date": datetime.now().strftime("%d.%m."),
                "day": day_to_finish,
                "text": st.session_state.weekly_plan[day_to_finish],
                "moods": f"{m_before} ➔ {m_after}"
            })
            # Přičíst XP a označit jako hotové
            st.session_state.xp += 50
            st.session_state.completed_days.append(day_to_finish)
            del st.session_state.current_completing_day
            save_data()
            st.balloons()
            st.rerun()

    if st.button("Uložit změny v plánu 🔒"):
        save_data()
        st.success("Plán uložen do paměti!")

with tabs[3]:
    st.subheader("📈 Historie úspěchů")
    if st.button("Smazat historii a resetovat týden (POZOR)"):
        st.session_state.completed_days = []
        st.session_state.mission_history = []
        save_data(); st.rerun()
        
    for h in reversed(st.session_state.mission_history):
        st.info(f"**{h['date']} ({h['day']})**: {h['text']} | Nálada: {h['moods']}")
