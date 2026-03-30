import streamlit as st
import json
import os
import io
import base64
from gtts import gTTS
from datetime import datetime

# --- 1. NASTAVENÍ ---
st.set_page_config(page_title="Hrdinka 🦋", page_icon="🦋", layout="centered")

DATA_FILE = "moje_data_v7.json"

# --- 2. LOGIKA DAT ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                keys = ["xp", "trusted_people", "mission_history", "completed_missions_ids", "custom_missions", "completed_log"]
                for k in keys:
                    if k not in d: d[k] = [] if "ids" in k or "custom" in k or "people" in k or "history" in k else (0 if k=="xp" else {})
                return d
        except: pass
    return {"xp": 0, "trusted_people": [], "mission_history": [], "completed_missions_ids": [], "custom_missions": [], "completed_log": {}}

def save_data():
    data_to_save = {k: st.session_state[k] for k in ["xp", "trusted_people", "mission_history", "completed_missions_ids", "custom_missions", "completed_log"]}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

if 'initialized' not in st.session_state:
    data = load_data()
    for k, v in data.items(): st.session_state[k] = v
    st.session_state.page = "Domů"
    st.session_state.initialized = True

# --- 3. FUNKCE HLASU ---
def speak(text):
    if text:
        try:
            tts = gTTS(text=text, lang='cs')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            b64 = base64.b64encode(fp.getvalue()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except: st.error("Chyba hlasu.")

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    .mission-card {
        background: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 12px;
        border-left: 8px solid #A06CD5;
    }
    .top-bar {
        background: white; padding: 10px; border-radius: 0 0 20px 20px;
        text-align: center; border-bottom: 2px solid #A06CD5; margin-top: -50px;
    }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

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
    # --- NOVINKA: VLASTNÍ TEXT ---
    st.subheader("Řekni, co potřebuješ 💬")
    vlastni_text = st.text_input("Napiš sem text:", placeholder="Např. Potřebuji pomoct s úkolem...")
    if st.button("🔊 Vyslovit můj text"):
        speak(vlastni_text)
    
    st.divider()
    
    st.subheader("Rychlá slova 🗣️")
    slova = [("Ahoj 👋", "Ahoj"), ("Děkuji ❤️", "Děkuji"), ("Prosím 🙏", "Prosím"), ("Ano ✅", "Ano"), ("Ne ❌", "Ne"), ("Dotaz 🙋‍♀️", "Mám dotaz")]
    c1, c2 = st.columns(2)
    for i, (label, sound) in enumerate(slova):
        with (c1 if i % 2 == 0 else c2):
            if st.button(label): speak(sound)
    
    st.divider()
    st.markdown("<b>Moji parťáci:</b>", unsafe_allow_html=True)
    new_p = st.text_input("Přidat jméno parťáka:")
    if st.button("Uložit parťáka"):
        if new_p: 
            st.session_state.trusted_people.append(new_p)
            save_data(); st.rerun()
    st.write(", ".join(st.session_state.trusted_people))

# --- STRÁNKA: MISE ---
elif st.session_state.page == "Mise":
    st.subheader("🪜 Tvůj žebřík (s datem)")
    default_missions = ["Usmát se", "Zamávat", "Kývnout", "Pozdravit", "Půjčit si věc", "Odpovědět"]
    vsechny = default_missions + st.session_state.custom_missions

    for i, m_text in enumerate(vsechny):
        m_id = str(i)
        is_done = m_id in st.session_state.completed_missions_ids
        date_str = st.session_state.completed_log.get(m_id, "Zatím nesplněno")
        
        st.markdown(f"""
            <div class="mission-card" style="border-left-color: {'#4CAF50' if is_done else '#A06CD5'}">
                <b>{i+1}. {m_text}</b><br>
                <span style="font-size: 0.8em; color: gray;">📅 {date_str}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if not is_done:
            if st.button(f"Splněno! #{i+1}", key=f"btn_{i}"):
                now = datetime.now().strftime("%d.%m. %H:%M")
                st.session_state.completed_missions_ids.append(m_id)
                st.session_state.completed_log[m_id] = now
                st.session_state.xp += 50
                save_data(); st.balloons(); st.rerun()

    st.subheader("➕ Vlastní mise")
    nova_m = st.text_input("Nová výzva:")
    if st.button("Přidat misi"):
        if nova_m:
            st.session_state.custom_missions.append(nova_m)
            save_data(); st.rerun()

# --- STRÁNKA: RITUÁL ---
elif st.session_state.page == "Rituál":
    st.subheader("🌙 Večerní rituál")
    afirmace = "Každý den dělám malé krůčky, které mě vedou k velkým věcem."
    st.info(afirmace)
    if st.button("🔊 Poslechnout"): speak(afirmace)
    if st.button("✅ Hotovo (+20 XP)"):
        st.session_state.xp += 20
        save_data(); st.rerun()

# --- STRÁNKA: DENÍK ---
elif st.session_state.page == "Deník":
    st.subheader("📊 Historie úspěchů")
    default_missions = ["Usmát se", "Zamávat", "Kývnout", "Pozdravit", "Půjčit si věc", "Odpovědět"]
    vsechny = default_missions + st.session_state.custom_missions
    
    if not st.session_state.completed_log:
        st.write("Deník je zatím prázdný. První mise čeká! 💪")
    else:
        for mid, dtime in reversed(list(st.session_state.completed_log.items())):
            idx = int(mid)
            m_text = vsechny[idx] if idx < len(vsechny) else "Mise"
            st.success(f"**{dtime}**: {m_text}")

save_data()
