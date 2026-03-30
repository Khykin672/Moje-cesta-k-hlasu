import streamlit as st
import json
import os
import io
import base64
from gtts import gTTS
from datetime import datetime
import random

# --- 1. NASTAVENÍ ---
st.set_page_config(page_title="Hrdinka 🦋", page_icon="🦋", layout="centered")

DATA_FILE = "moje_data_v5.json" # Verze 5 kvůli změně struktury misí

# --- 2. LOGIKA DAT ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                # Inicializace nových klíčů, pokud chybí
                if "custom_missions" not in d: d["custom_missions"] = []
                if "completed_log" not in d: d["completed_log"] = {} # ID mise: datum splnění
                return d
        except: pass
    return {
        "xp": 0, "trusted_people": [], "mission_history": [], 
        "completed_missions_ids": [], "custom_missions": [],
        "completed_log": {}
    }

def save_data():
    data_to_save = {
        "xp": st.session_state.xp,
        "trusted_people": st.session_state.trusted_people,
        "mission_history": st.session_state.mission_history,
        "completed_missions_ids": st.session_state.completed_missions_ids,
        "custom_missions": st.session_state.custom_missions,
        "completed_log": st.session_state.completed_log
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

if 'initialized' not in st.session_state:
    data = load_data()
    for k, v in data.items(): st.session_state[k] = v
    st.session_state.page = "Domů"
    st.session_state.initialized = True

# --- 3. MOBILNÍ DESIGN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    /* Styl pro kartu mise - aby byla čitelná na mobilu */
    .mission-card {
        background: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 12px;
        border-left: 8px solid #A06CD5;
    }
    .mission-done { border-left: 8px solid #4CAF50; background: #f0fff0; }
    .date-label { color: #888; font-size: 0.8em; margin-top: 5px; }
    
    .top-bar {
        background: white; padding: 10px; border-radius: 0 0 20px 20px;
        text-align: center; border-bottom: 2px solid #A06CD5; margin-top: -50px;
    }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HLAS ---
def speak(text):
    if text:
        try:
            tts = gTTS(text=text, lang='cs')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            b64 = base64.b64encode(fp.getvalue()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except: st.error("Hlas momentálně nefunguje.")

# --- 5. NAVIGACE ---
level = (st.session_state.xp // 100) + 1
st.markdown(f'<div class="top-bar"><b>Level {level}</b> • {st.session_state.xp} XP 🦋</div>', unsafe_allow_html=True)

cols = st.columns(4)
nav = {"Domů": "🏠", "Mise": "🪜", "Rituál": "🌙", "Deník": "📊"}
for i, (name, icon) in enumerate(nav.items()):
    if cols[i].button(f"{icon}\n{name}"):
        st.session_state.page = name
        st.rerun()

st.divider()

# --- STRÁNKA: DOMŮ ---
if st.session_state.page == "Domů":
    st.subheader("Rychlá slova 🗣️")
    slova = [("Ahoj 👋", "Ahoj"), ("Děkuji ❤️", "Děkuji"), ("Prosím 🙏", "Prosím"), ("Ano ✅", "Ano"), ("Ne ❌", "Ne"), ("Mám dotaz 🙋‍♀️", "Mám dotaz")]
    c1, c2 = st.columns(2)
    for i, (label, sound) in enumerate(slova):
        with (c1 if i % 2 == 0 else c2):
            if st.button(label): speak(sound)
    
    st.markdown('<br><div style="font-weight:bold;">Moji parťáci:</div>', unsafe_allow_html=True)
    new_p = st.text_input("Přidat jméno:", key="p_in")
    if st.button("Uložit parťáka"):
        if new_p: 
            st.session_state.trusted_people.append(new_p)
            save_data(); st.rerun()
    st.write(", ".join(st.session_state.trusted_people))

# --- STRÁNKA: MISE (UPRAVENO PRO MOBIL A KALENDÁŘ) ---
elif st.session_state.page == "Mise":
    st.subheader("🪜 Tvůj žebřík pokroku")
    
    default_missions = [
        "Usmát se na učitelku", "Zamávat kamarádce", "Kývnout na otázku",
        "Šeptnout 'Ahoj'", "Půjčit si tužku", "Říct 'Dobrý den' nahlas",
        "Odpovědět celou větou", "Objednat si v obchodě", "Zvednout ruku ve třídě"
    ]
    vsechny_mise = default_missions + st.session_state.custom_missions

    for i, m_text in enumerate(vsechny_mise):
        m_id = str(i) # Unikátní ID pro logování
        is_done = m_id in st.session_state.completed_missions_ids
        
        # Vizuální karta mise
        card_class = "mission-card mission-done" if is_done else "mission-card"
        done_date = st.session_state.completed_log.get(m_id, "")
        
        st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 1.1em; font-weight: bold;">
                    {'✅' if is_done else '⚪'} {i+1}. {m_text}
                </div>
                {f'<div class="date-label">Splněno: {done_date}</div>' if is_done else '<div class="date-label">Stav: Čeká na hrdinku</div>'}
            </div>
            """, unsafe_allow_html=True)
        
        # Ovládací tlačítka pod kartou (vždy na celou šířku pro mobil)
        if not is_done:
            if st.button(f"Splnit misi {i+1}", key=f"btn_done_{i}"):
                now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                st.session_state.completed_missions_ids.append(m_id)
                st.session_state.completed_log[m_id] = now_str
                st.session_state.xp += 50
                save_data(); st.balloons(); st.rerun()
        
        # Možnost smazání pouze u vlastních misí na konci seznamu
        if i >= len(default_missions):
            if st.button(f"🗑️ Odstranit vlastní misi {i+1}", key=f"del_{i}"):
                custom_idx = i - len(default_missions)
                st.session_state.custom_missions.pop(custom_idx)
                if m_id in st.session_state.completed_missions_ids:
                    st.session_state.completed_missions_ids.remove(m_id)
                    st.session_state.completed_log.pop(m_id, None)
                save_data(); st.rerun()

    st.divider()
    st.subheader("➕ Nová výzva")
    vlastni = st.text_input("Co dnes zkusíš?")
    if st.button("Přidat do seznamu"):
        if vlastni:
            st.session_state.custom_missions.append(vlastni)
            save_data(); st.rerun()

# --- STRÁNKA: RITUÁL ---
elif st.session_state.page == "Rituál":
    st.subheader("🌙 Večerní rituál")
    afirmace = ["Můj hlas je můj kamarád.", "Každý den jsem statečnější.", "Je v pořádku mluvit i mlčet."]
    dnesni = afirmace[datetime.now().day % len(afirmace)]
    
    st.info(f"### {dnesni}")
    if st.button("🔊 Přečíst nahlas"): speak(dnesni)
    
    if st.button("✅ Mám hotovo (20 XP)"):
        st.session_state.xp += 20
        save_data(); st.success("Krásnou noc!"); st.rerun()

# --- STRÁNKA: DENÍK ---
elif st.session_state.page == "Deník":
    st.subheader("📊 Kalendář úspěchů")
    
    # Zde vidíme historii zapsanou v sekci Mise
    if st.session_state.completed_log:
        for m_id, d_time in reversed(st.session_state.completed_log.items()):
            m_idx = int(m_id)
            # Získání textu mise podle ID
            vsechny = default_missions + st.session_state.custom_missions
            m_text = vsechny[m_idx] if m_idx < len(vsechny) else "Smazaná mise"
            st.write(f"📅 **{d_time}** - {m_text}")
    else:
        st.write("Zatím žádné splněné mise. Do toho!")

    st.divider()
    if st.button("⚠️ Smazat vše a začít znovu"):
        st.session_state.xp = 0
        st.session_state.completed_missions_ids = []
        st.session_state.completed_log = {}
        st.session_state.custom_missions = []
        save_data(); st.rerun()

save_data()
