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

DATA_FILE = "moje_data_v4.json"

# --- 2. LOGIKA DAT ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                # Zajistíme, aby tam byly všechny klíče
                if "custom_missions" not in d: d["custom_missions"] = []
                return d
        except: pass
    return {
        "xp": 0, "trusted_people": [], "mission_history": [], 
        "completed_missions_ids": [], "custom_missions": []
    }

def save_data():
    data_to_save = {
        "xp": st.session_state.xp,
        "trusted_people": st.session_state.trusted_people,
        "mission_history": st.session_state.mission_history,
        "completed_missions_ids": st.session_state.completed_missions_ids,
        "custom_missions": st.session_state.custom_missions
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

if 'initialized' not in st.session_state:
    data = load_data()
    for k, v in data.items(): st.session_state[k] = v
    st.session_state.page = "Domů" # Pro navigaci na mobilu
    st.session_state.initialized = True

# --- 3. MOBILNÍ DESIGN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    .main-card {
        background: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px;
        border-left: 5px solid #A06CD5;
    }
    /* Velká tlačítka menu */
    .nav-btn {
        width: 100%; border-radius: 10px; padding: 10px;
        margin-bottom: 5px; background: white; border: 1px solid #ddd;
    }
    /* Horní lišta */
    .top-bar {
        background: white; padding: 10px; border-radius: 0 0 20px 20px;
        text-align: center; border-bottom: 2px solid #A06CD5; margin-top: -50px;
    }
    /* Tlačítka akcí */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em; font-weight: bold;
    }
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

# --- 5. NAVIGACE (Místo Tabs) ---
level = (st.session_state.xp // 100) + 1
st.markdown(f'<div class="top-bar"><b>Level {level}</b> • XP: {st.session_state.xp} 🦋</div>', unsafe_allow_html=True)

st.write("") # Mezera
cols = st.columns(4)
nav_icons = {"Domů": "🏠", "Mise": "🪜", "Rituál": "🌙", "Deník": "📊"}
for i, (name, icon) in enumerate(nav_icons.items()):
    if cols[i].button(f"{icon}\n{name}"):
        st.session_state.page = name
        st.rerun()

st.divider()

# --- STRÁNKA: DOMŮ ---
if st.session_state.page == "Domů":
    st.subheader("Rychlá slova 🗣️")
    c1, c2 = st.columns(2)
    slova = [("Ahoj 👋", "Ahoj"), ("Děkuji ❤️", "Děkuji"), ("Prosím 🙏", "Prosím"), ("Ano ✅", "Ano"), ("Ne ❌", "Ne"), ("Mám dotaz 🙋‍♀️", "Mám dotaz")]
    for i, (label, sound) in enumerate(slova):
        with (c1 if i % 2 == 0 else c2):
            if st.button(label): speak(sound)
    
    st.markdown('<div class="main-card"><b>Lidé, se kterými mluvím:</b></div>', unsafe_allow_html=True)
    new_p = st.text_input("Nové jméno:", key="p_in")
    if st.button("Přidat parťáka"):
        if new_p: 
            st.session_state.trusted_people.append(new_p)
            save_data(); st.rerun()
    st.write(", ".join(st.session_state.trusted_people))

# --- STRÁNKA: MISE (ŽEBŘÍK) ---
elif st.session_state.page == "Mise":
    st.subheader("🪜 Žebřík hrdinství")
    
    # Základní mise
    default_missions = [
        "Usmát se na učitelku", "Zamávat kamarádce", "Kývnout na otázku",
        "Šeptnout 'Ahoj'", "Půjčit si tužku", "Říct 'Dobrý den' nahlas",
        "Odpovědět celou větou", "Objednat si v obchodě", "Zvednout ruku ve třídě", "Vyprávět zážitek"
    ]
    
    # Spojíme základní a vlastní mise
    vsechny_mise = default_missions + st.session_state.custom_missions

    for i, m_text in enumerate(vsechny_mise):
        is_done = i in st.session_state.completed_missions_ids
        c1, c2, c3 = st.columns([6, 2, 2])
        
        with c1:
            st.markdown(f"**{i+1}.** {'✅' if is_done else '⚪'} {m_text}")
        with c2:
            if not is_done:
                if st.button("Splnit", key=f"done_{i}"):
                    st.session_state.completed_missions_ids.append(i)
                    st.session_state.xp += 50
                    save_data(); st.balloons(); st.rerun()
        with c3:
            # Mazání (u vlastních misí nebo všech)
            if st.button("🗑️", key=f"del_{i}"):
                if i < len(default_missions):
                    st.warning("Základní mise nelze smazat, ale můžeš ji ignorovat.")
                else:
                    # Smazání vlastní mise
                    custom_idx = i - len(default_missions)
                    st.session_state.custom_missions.pop(custom_idx)
                    # Vyčistit i z hotových, pokud tam byla
                    if i in st.session_state.completed_missions_ids:
                        st.session_state.completed_missions_ids.remove(i)
                    save_data(); st.rerun()

    st.divider()
    st.subheader("➕ Přidat vlastní misi")
    vlastni = st.text_input("Napiš svoji výzvu:")
    if st.button("Uložit novou misi"):
        if vlastni:
            st.session_state.custom_missions.append(vlastni)
            save_data(); st.rerun()

# --- STRÁNKA: RITUÁL ---
elif st.session_state.page == "Rituál":
    st.markdown('<div style="background:#2D3142; color:white; padding:20px; border-radius:15px; text-align:center;">', unsafe_allow_html=True)
    st.subheader("🌙 Večerní rituál")
    
    afirmace = ["Můj hlas je můj kamarád.", "Každý den jsem statečnější.", "Je v pořádku mluvit i mlčet.", "Jsem hrdinka svého příběhu."]
    dnesni = afirmace[datetime.now().day % len(afirmace)]
    
    st.write(f"### {dnesni}")
    if st.button("🔊 Poslechnout"): speak(dnesni)
    
    if st.button("✅ Splněno (20 XP)"):
        st.session_state.xp += 20
        save_data(); st.success("Krásnou noc!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- STRÁNKA: DENÍK ---
elif st.session_state.page == "Deník":
    st.subheader("📊 Můj deník")
    
    uzkost = st.select_slider("Jak ti bušilo srdíčko? (1=klid, 10=velký strach)", options=range(1,11))
    pozn = st.text_area("Co se dnes povedlo?")
    
    if st.button("Uložit záznam"):
        st.session_state.mission_history.append({
            "datum": datetime.now().strftime("%d.%m."),
            "u": uzkost, "p": pozn
        })
        save_data(); st.success("Uloženo!"); st.rerun()
    
    st.divider()
    if st.button("⚠️ Resetovat celý pokrok (XP i mise)"):
        st.session_state.xp = 0
        st.session_state.completed_missions_ids = []
        st.session_state.mission_history = []
        st.session_state.custom_missions = []
        save_data(); st.rerun()

    for h in reversed(st.session_state.mission_history):
        st.info(f"**{h['datum']}** | Strach: {h['u']}/10\n\n{h['p']}")

save_data()
