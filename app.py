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
    page_title="Hrdinská Cesta 🦋", 
    page_icon="🦋", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "moje_data_v3.json"

# --- 2. LOGIKA DAT (BEZ CHYB PŘI UKLÁDÁNÍ) ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        "xp": 0,
        "trusted_people": [], 
        "mission_history": [], 
        "completed_missions_ids": [],
        "weekly_plan": {d: "" for d in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]}
    }

def save_data():
    # Ukládáme jen čistá data, ne celý session_state (to byla ta chyba v obrázku)
    data_to_save = {
        "xp": st.session_state.xp,
        "trusted_people": st.session_state.trusted_people,
        "mission_history": st.session_state.mission_history,
        "completed_missions_ids": st.session_state.completed_missions_ids,
        "weekly_plan": st.session_state.weekly_plan
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# Inicializace session_state
if 'initialized' not in st.session_state:
    data = load_data()
    st.session_state.xp = data.get("xp", 0)
    st.session_state.trusted_people = data.get("trusted_people", [])
    st.session_state.mission_history = data.get("mission_history", [])
    st.session_state.completed_missions_ids = data.get("completed_missions_ids", [])
    st.session_state.weekly_plan = data.get("weekly_plan", {d: "" for d in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]})
    st.session_state.initialized = True

# --- 3. PROFI MOBILNÍ DESIGN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6ff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Karty a boxíky */
    .main-card {
        background: white; padding: 15px; border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px;
        border-left: 6px solid #A06CD5;
    }
    
    /* Statistiky nahoře */
    .stats-container {
        display: flex; justify-content: space-around;
        background: white; padding: 10px; border-radius: 15px;
        margin-bottom: 20px; border: 1px solid #E0E0E0;
    }

    /* Tlačítka pro mobil */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em; 
        font-weight: bold; font-size: 16px !important;
        border: 2px solid #F0F0F0; transition: 0.3s;
    }
    
    /* Vylepšení pro písmo */
    h1, h2, h3 { color: #4A4A4A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Skrytí menu Streamlitu pro čistý vzhled */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. POMOCNÉ FUNKCE ---
def speak(text):
    if text:
        try:
            tts = gTTS(text=text, lang='cs')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            b64 = base64.b64encode(fp.getvalue()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except: st.error("Chyba hlasového výstupu.")

# --- 5. OBSAH APLIKACE ---

# Horní panel (Levely a XP)
level = (st.session_state.xp // 100) + 1
st.markdown(f"""
    <div class="stats-container">
        <div style="text-align:center"><b>Level</b><br><span style="font-size:1.5rem; color:#A06CD5;">{level}</span></div>
        <div style="text-align:center"><b>XP Hrdinky</b><br><span style="font-size:1.5rem; color:#A06CD5;">{st.session_state.xp}</span></div>
    </div>
    """, unsafe_allow_html=True)

tabs = st.tabs(["🏠 Domů", "🪜 Mise", "🌙 Rituál", "📈 Deník"])

# --- TAB 1: DOMŮ (HLAS A LIDÉ) ---
with tabs[0]:
    st.markdown('<div class="main-card"><h3>Moje hlasová kouzla ✨</h3><p>Klikni na tlačítko a já to řeknu za tebe.</p></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    slova = [("AHOJ 👋", "Ahoj"), ("DĚKUJI ❤️", "Děkuji"), ("PROSÍM 🙏", "Prosím"), ("ANO ✅", "Ano"), ("NE ❌", "Ne"), ("MÁM DOTAZ 🙋‍♀️", "Mám dotaz")]
    for i, (label, sound) in enumerate(slova):
        with (c1 if i % 2 == 0 else c2):
            if st.button(label, key=f"voice_{i}"): speak(sound)
    
    st.divider()
    st.subheader("👥 Moje bezpečná skupina")
    new_person = st.text_input("Přidej někoho, s kým už mluvíš:", key="add_p", placeholder="Jméno...")
    if st.button("Přidat do týmu ✨"):
        if new_person and new_person not in st.session_state.trusted_people:
            st.session_state.trusted_people.append(new_person)
            save_data()
            st.rerun()
    
    if st.session_state.trusted_people:
        st.info("Tým hrdinky: " + ", ".join(st.session_state.trusted_people))

# --- TAB 2: ŽEBŘÍK STATEČNOSTI (10 LEVELŮ) ---
with tabs[1]:
    st.markdown('<div class="main-card"><h3>🪜 Žebřík statečnosti</h3><p>Tady jsou tvoje mise. Zvládneš je všechny?</p></div>', unsafe_allow_html=True)
    
    zebrik = [
        "1. Usmát se na někoho ve škole",
        "2. Zamávat na pozdrav (beze slov)",
        "3. Kývnout 'Ano/Ne' na otázku učitele",
        "4. Šeptnout 'Ahoj' své kamarádce",
        "5. Půjčit si od někoho věc (ukázáním nebo šeptem)",
        "6. Říct 'Dobrý den' nahlas při příchodu",
        "7. Odpovědět učitelce celou větou",
        "8. V obchodě si sama objednat (např. jeden rohlík)",
        "9. Zvednout ruku a odpovědět na otázku ve třídě",
        "10. Vyprávět krátký zážitek před celou třídou"
    ]

    for i, mise in enumerate(zebrik):
        is_completed = i in st.session_state.completed_missions_ids
        # Kontejner pro každou misi
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                text_style = "color: #2E7D32; font-weight: bold;" if is_completed else "color: #555;"
                st.markdown(f"<div style='padding:10px; {text_style}'>{'✅' if is_completed else '⚪'} {mise}</div>", unsafe_allow_html=True)
            with col2:
                if not is_completed:
                    if st.button("Hotovo", key=f"m_{i}"):
                        st.session_state.completed_missions_ids.append(i)
                        st.session_state.xp += 50
                        save_data()
                        st.balloons()
                        st.rerun()

# --- TAB 3: VEČERNÍ RITUÁL (AFIRMACE) ---
with tabs[2]:
    st.markdown("""
        <div style="background: linear-gradient(180deg, #2D3142 0%, #4F5D75 100%); color: white; padding: 25px; border-radius: 25px; text-align: center;">
            <h2 style="color: white;">🌙 Večerní rituál</h2>
            <p>Přečti si dnešní afirmaci a odpočiň si.</p>
        </div>
        """, unsafe_allow_html=True)
    
    afirmace_list = [
        "Jsem v bezpečí. Můžu mluvit, když chci, a je to v pořádku.",
        "Každý den jsem o kousek statečnější. Jsem hrdá na sebe.",
        "Můj hlas je silný a já ho mám ráda.",
        "Všichni mě mají rádi takovou, jaká jsem."
    ]
    
    # Vybere afirmaci podle dne v měsíci, aby se měnila denně
    daily_idx = datetime.now().day % len(afirmace_list)
    dnesni_afirmace = afirmace_list[daily_idx]
    
    st.markdown(f"<div style='font-size: 20px; font-style: italic; text-align: center; padding: 30px;'>\"{dnesni_afirmace}\"</div>", unsafe_allow_html=True)
    
    if st.button("🔊 Poslechnout si můj vnitřní hlas"):
        speak(dnesni_afirmace)
        
    st.divider()
    st.write("🧘 **Krátká relaxace:** Zavři oči a 3x se zhluboka nadechni. Představ si, jak jsi zítra v klidu a usmíváš se.")
    
    if st.button("✨ Splněno - Odměna 20 XP"):
        st.session_state.xp += 20
        save_data()
        st.success("Skvělá práce! Krásnou noc.")

# --- TAB 4: DENÍK POCITŮ ---
with tabs[3]:
    st.subheader("📊 Jak se dnes cítíš?")
    
    feeling = st.select_slider("Moje nálada:", options=["😢", "😟", "😐", "🙂", "😊"], value="😐")
    anxiety = st.select_slider("Jak moc bušilo srdíčko? (1 = klid, 10 = strach)", options=list(range(1, 11)), value=1)
    note = st.text_area("Co se mi dneska povedlo?", placeholder="Dneska jsem se usmála na paní učitelku...")
    
    if st.button("Uložit do deníku 🔒"):
        new_entry = {
            "datum": datetime.now().strftime("%d.%m. %H:%M"),
            "nalada": feeling,
            "uzkost": anxiety,
            "poznamka": note
        }
        st.session_state.mission_history.append(new_entry)
        save_data()
        st.success("Zapsáno! Jsi šikula.")

    st.divider()
    if st.toggle("Zobrazit historii pro psychologa"):
        for h in reversed(st.session_state.mission_history):
            with st.container():
                st.markdown(f"""
                <div class="main-card">
                    <b>{h['datum']}</b> | Nálada: {h['nalada']} | Strach: {h['uzkost']}/10 <br>
                    <i>{h['poznamka']}</i>
                </div>
                """, unsafe_allow_html=True)

# Finální uložení při každé akci
save_data()
