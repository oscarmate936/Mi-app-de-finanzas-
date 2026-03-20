import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vault Premium", page_icon="💎", layout="centered")

# --- REDISEÑO ELITE V3 (CSS REFORZADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Fondo y Base */
    [data-testid="stAppViewContainer"] {
        background: #020617;
        background-image: radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.15) 0px, transparent 50%),
                          radial-gradient(at 100% 100%, rgba(15, 23, 42, 0.4) 0px, transparent 50%);
        font-family: 'Outfit', sans-serif;
    }
    header, footer {visibility: hidden;}
    .main .block-container { padding-top: 2rem; max-width: 450px; }

    /* Card Principal */
    .premium-card {
        background: linear-gradient(145deg, #0f172a, #1e293b);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 35px;
        padding: 45px 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8);
    }
    .balance-val { 
        font-size: 55px; font-weight: 800; color: #ffffff; 
        letter-spacing: -2px; margin: 10px 0;
    }
    .balance-label { font-size: 10px; text-transform: uppercase; letter-spacing: 5px; color: #64748b; }

    /* Bento Stats */
    .bento-grid { display: flex; gap: 15px; margin-bottom: 25px; }
    .bento-item {
        flex: 1; background: #0f172a; border-radius: 25px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }

    /* BOTONES: EL CORAZÓN DE LA SOLUCIÓN */
    /* Targeteamos el botón y CUALQUIER texto dentro (p, span, div) */
    div.stButton > button {
        width: 100% !important;
        height: 70px !important;
        border-radius: 22px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
    }

    /* FORZAR COLOR DE TEXTO (Para que no se vea blanco sobre blanco) */
    div.stButton > button p, div.stButton > button span, div.stButton > button div {
        color: white !important;
    }

    /* Estilo INGRESO (Esmeralda oscuro) */
    button[key="btn_ingreso"] {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%) !important;
        box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.2) !important;
    }

    /* Estilo GASTO (Carmesí oscuro) */
    button[key="btn_gasto"] {
        background: linear-gradient(135deg, #4c0519 0%, #881337 100%) !important;
        box-shadow: 0 10px 20px -5px rgba(244, 63, 94, 0.2) !important;
    }

    /* Estilo ELIMINAR (Minimalista) */
    div.stButton > button[key^="del_"] {
        background: rgba(255,255,255,0.05) !important;
        height: 35px !important;
        font-size: 10px !important;
        border-radius: 10px !important;
        margin-top: 5px !important;
    }
    
    /* Estilo CONFIGURAR */
    button[key="btn_sueldo"] {
        background: transparent !important;
        border: 1px dashed rgba(255,255,255,0.2) !important;
        color: #64748b !important;
        margin-top: 30px !important;
    }

    /* Feed de Transacciones */
    .tx-card {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255, 255, 255, 0.02);
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA (No cambia nada de tu backend) ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("Configura los Secrets.")
    st.stop()

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "settings" not in data: data["settings"] = {"sueldo": 0.0}
        if "transactions" not in data: data["transactions"] = []
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()
df = pd.DataFrame(db["transactions"])
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount']).fillna(0.0)
    df_mes = df[df['date_dt'].dt.month == datetime.now().month]
else:
    df_mes = pd.DataFrame(columns=["amount", "type"])

sueldo_base = db["settings"].get("sueldo", 0.0)
ing_m = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gst_m = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
saldo = sueldo_base + (df[df['type']=='Ingreso']['amount'].sum() if not df.empty else 0) - (df[df['type']=='Gasto']['amount'].sum() if not df.empty else 0)

# --- DIÁLOGOS ---
@st.dialog("Presupuesto")
def s_dial():
    s = st.number_input("Monto:", value=sueldo_base)
    if st.button("Guardar"): db["settings"]["sueldo"] = s; save_db(db); st.rerun()

@st.dialog("Ingreso")
def i_dial():
    a = st.number_input("Monto:", min_value=0.0); n = st.text_input("Nota")
    if st.button("Registrar"): 
        db["transactions"].append({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"), "type": "Ingreso", "category": "Extra", "amount": a, "note": n})
        save_db(db); st.rerun()

@st.dialog("Gasto")
def g_dial():
    c = st.selectbox("Categoría", ["🍔 Comida", "🎬 Ocio", "🏠 Hogar", "🚗 Viajes", "🌀 Otros"])
    a = st.number_input("Monto:", min_value=0.0); n = st.text_input("Nota")
    if st.button("Registrar"):
        db["transactions"].append({"id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"), "type": "Gasto", "category": c, "amount": a, "note": n})
        save_db(db); st.rerun()

# --- INTERFAZ ---

st.markdown(f'<div class="premium-card"><div class="balance-label">Vault Balance</div><div class="balance-val">${saldo:,.2f}</div><div style="font-size:9px; color:#10B981; letter-spacing:3px; font-weight:700;">ACTIVE SESSION</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="bento-grid"><div class="bento-item"><div class="balance-label" style="letter-spacing:1px">Ingresos</div><div style="color:#10B981; font-weight:700; font-size:18px;">+${ing_m:,.0f}</div></div><div class="bento-item"><div class="balance-label" style="letter-spacing:1px">Gastos</div><div style="color:#F43F5E; font-weight:700; font-size:18px;">-${gst_m:,.0f}</div></div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("✚ INGRESO", key="btn_ingreso"): i_dial()
with col2:
    if st.button("➖ GASTO", key="btn_gasto"): g_dial()

st.markdown("<p style='font-size:11px; font-weight:800; color:#475569; letter-spacing:2px; margin-top:30px;'>HISTORIAL RECIENTE</p>", unsafe_allow_html=True)

if not df.empty:
    for _, r in df.sort_values('date', ascending=False).head(5).iterrows():
        color = "#10B981" if r['type'] == 'Ingreso' else "#F43F5E"
        st.markdown(f'<div class="tx-card"><div><div style="font-size:14px; font-weight:600;">{r["note"]}</div><div style="font-size:9px; color:#475569;">{r["category"]} • {r["date"]}</div></div><div style="color:{color}; font-weight:700;">{" " if r["type"]=="Ingreso" else "-"}${r["amount"]:,.0f}</div></div>', unsafe_allow_html=True)
        if st.button(f"ELIMINAR {r['id']}", key=f"del_{r['id']}"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != r['id']]; save_db(db); st.rerun()

if st.button("CONFIGURAR SALARIO BASE", key="btn_sueldo"): s_dial()

st.markdown(f'<div style="text-align:center; opacity:0.2; font-size:8px; margin-top:40px; letter-spacing:4px;">VAULT v3.0 • {datetime.now().year}</div>', unsafe_allow_html=True)
