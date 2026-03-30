import streamlit as st
import json
import os
import io
import base64
from gtts import gTTS
from datetime import datetime
import random

# --- 1. KONFIGURACE PRO MOBIL ---
st.set_page_config(
    page_title="Hrdinská Cesta", 
    page_icon="🦋", 
    layout="centered", # Centrování pro úzké displeje
    initial_sidebar_state="collapsed"
)

DATA_FILE = "moje_data_v2.json"

# --- 2. LOGIKA DAT ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        "xp": 0, "level": 1, "trusted_people": [], 
        "mission_history": [], "completed_missions_ids": [],
        "weekly_plan": {d: "" for d in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]}
    }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.to_dict(), f, ensure_ascii=False, indent=4)

if 'initialized' not in st.session_state:
    data = load_data()
    for k, v in data.items(): st.session_state[k] = v
    st.session_state.initialized = True

# Helper pro uložení stavu session do diktátu
def to_dict():
    return {k: v for k, v in st.session_state.items() if k not in ['initialized', 'current_tab']}
st.session_state.to_dict = to_dict

# --- 3. PROFI DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Mobilní optimalizace */
    .stApp { background-color: #F8F9FA; }
    .main-card {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 5px solid #A06CD5;
    }
    .level-badge {
        background: linear-gradient(135deg, #A06CD5, #6247AA);
        color: white; padding: 10px 20px; border-radius: 50px;
        font-weight: bold; font-size: 1.2rem; display: inline-block;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em; 
        background-color: white; border: 2px solid #E0E0E0;
        font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { border-color: #A06CD5; color: #A06CD5; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0; border-radius: 10px 10px 0 0; padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKCE ---
def speak(text):
    if text:
        tts = gTTS(text=text, lang='cs')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)

# --- 5. OBSAH APLIKACE ---

# Horní stavová lišta (vždy viditelná)
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f'<div class="level-badge">Level {st.session_state.xp // 100 + 1}</div>', unsafe_allow_html=True)
with col2:
    st.metric("Hvězdy ✨", st.session_state.xp)

tabs = st.tabs(["🏠 Domů", "🪜 Mise", "🌙 Rituál", "📊 Deník"])

# --- TAB 1: DOMŮ ---
with tabs[0]:
    st.markdown('<div class="main-card"><h3>Ahoj Hrdinko! 👋</h3><p>Dneska je krásný den na jeden malý krůček.</p></div>', unsafe_allow_html=True)
    
    st.subheader("Rychlá mluva 🔊")
    c1, c2 = st.columns(2)
    words = [("Ahoj 👋", "Ahoj"), ("Děkuji ❤️", "Děkuji"), ("Prosím 🙏", "Prosím"), ("Ano ✅", "Ano"), ("Ne ❌", "Ne"), ("Mám dotaz 🙋‍♀️", "Mám dotaz")]
    for i, (label, sound) in enumerate(words):
        with (c1 if i % 2 == 0 else c2):
            if st.button(label): speak(sound)

# --- TAB 2: ŽEBŘÍK STATEČNOSTI (10 LEVELŮ) ---
with tabs[1]:
    st.subheader("🪜 Žebřík statečnosti")
    st.caption("Postupuj od nejlehčího po největší výzvy.")
    
    zebrik = [
        "1. Usmát se na někoho ve škole",
        "2. Zamávat na pozdrav",
        "3. Kývnout 'Ano/Ne' na otázku",
        "4. Šeptnout 'Ahoj' kamarádce",
        "5. Půjčit si od někoho tužku (beze slov)",
        "6. Říct 'Dobrý den' nahlas",
        "7. Odpovědět celou větou učitelce",
        "8. Zeptat se v obchodě: 'Kolik to stojí?'",
        "9. Zvednout ruku a odpovědět ve třídě",
        "10. Vyprávět krátký příběh skupince lidí"
    ]

    for i, mise in enumerate(zebrik):
        is_completed = i in st.session_state.completed_missions_ids
        col1, col2 = st.columns([4, 1])
        with col1:
            color = "green" if is_completed else "black"
            st.markdown(f"<p style='color:{color}; font-size:1.1rem;'>{'✅' if is_completed else '⚪'} {mise}</p>", unsafe_allow_html=True)
        with col2:
            if not is_completed:
                if st.button("Splnit", key=f"zeb_{i}"):
                    st.session_state.completed_missions_ids.append(i)
                    st.session_state.xp += 30
                    save_data()
                    st.balloons()
                    st.rerun()

# --- TAB 3: VEČERNÍ RITUÁL ---
with tabs[2]:
    st.markdown('<div style="background: #2D3142; color: white; padding: 20px; border-radius: 20px;">', unsafe_allow_html=True)
    st.subheader("🌙 Večerní rituál hrdinky")
    
    afirmace = [
        "Jsem v bezpečí a můžu mluvit, když chci.",
        "Každý den jsem o kousek statečnější.",
        "Můj hlas je krásný a důležitý.",
        "Jsem na sebe hrdá za každý dnešní krůček."
    ]
    
    selected_af = random.choice(afirmace)
    st.markdown(f"### *{selected_af}*")
    
    if st.button("🔊 Poslechnout si afirmaci"):
        speak(selected_af)
    
    st.divider()
    st.write("🧘 **Krátká relaxace:** Zavři oči a představ si, jak zítra s úsměvem zvládneš další misi. Jsi hvězda!")
    
    if st.button("✅ Splnit rituál a jít spát (+20 XP)"):
        st.session_state.xp += 20
        save_data()
        st.success("Krásné sny, hrdinko!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: DENÍK A REPORT ---
with tabs[3]:
    st.subheader("📈 Tvůj pokrok")
    
    # Úzkost - škála
    st.write("Jak ti dneska bušilo srdíčko?")
    anxiety = st.select_slider("1 = Klid, 10 = Velký strach", options=range(1, 11), value=5)
    
    note = st.text_area("Co se ti dneska povedlo? (i maličkost)")
    
    if st.button("Uložit do deníku"):
        st.session_state.mission_history.append({
            "datum": datetime.now().strftime("%d.%m. %H:%M"),
            "uzkost": anxiety,
            "poznamka": note
        })
        save_data()
        st.success("Uloženo!")

    st.divider()
    if st.checkbox("Zobrazit historii pro psychologa"):
        for h in reversed(st.session_state.mission_history):
            st.write(f"**{h['datum']}** | Strach: {h['uzkost']}/10")
            st.write(f"*{h['poznamka']}*")
            st.write("---")

# Uložení na konci každého cyklu
save_data()
