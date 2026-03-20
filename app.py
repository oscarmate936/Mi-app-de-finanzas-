import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CashBook Ultra", page_icon="💳", layout="centered")

# --- ESTILOS VISUALES (REDISEÑO DE ALTA GAMA) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #0f172a; } /* Slate 900 */
    
    /* Botones Estilo 'Tile' Profesional */
    div.stButton > button {
        width: 100% !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 30px 20px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: #1e293b !important; /* Slate 800 */
        color: #f8fafc !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    
    div.stButton > button:hover {
        border: 1px solid #38bdf8 !important; /* Sky 400 */
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2) !important;
    }

    /* Botón de Saldo Principal (Hero Button) */
    .hero-btn button {
        background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
        border: none !important;
        padding: 50px 20px !important;
    }

    /* Texto dentro de los botones */
    .btn-label { font-size: 14px; opacity: 0.7; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .btn-value { font-size: 32px; font-weight: 700; display: block; margin-top: 5px; }
    
    /* Pestañas */
    div[data-testid="stTabBar"] { background-color: transparent; }
    button[data-baseweb="tab"] { color: #94a3b8 !important; }
    button[aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }

    /* Estilo para los formularios de dialogo */
    div[role="dialog"] { background-color: #1e293b !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Configura los 'Secrets' en Streamlit.")
    st.stop()

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        if "settings" not in data: data["settings"] = {"sueldo": 0.0}
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- PROCESAMIENTO ---
df = pd.DataFrame(db["transactions"])
if df.empty:
    df = pd.DataFrame(columns=["id", "date", "type", "amount", "account"])
else:
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

sueldo = float(db["settings"].get("sueldo", 0))
ingresos = df[df['type']=='Ingreso']['amount'].sum()
gastos = df[df['type']=='Gasto']['amount'].sum()
saldo_total = sueldo + ingresos - gastos

# --- DIÁLOGOS (FORMULARIOS MÍNIMOS) ---
@st.dialog("🎯 CONFIGURAR SUELDO")
def sueldo_dialog():
    nuevo_sueldo = st.number_input("Establecer Sueldo Base ($)", value=sueldo, step=100.0)
    if st.button("ACTUALIZAR SALDO", use_container_width=True):
        db["settings"]["sueldo"] = nuevo_sueldo
        save_db(db); st.rerun()

@st.dialog("➕ MOVIMIENTO RÁPIDO")
def add_val_dialog(cuenta):
    st.markdown(f"### Cuenta: **{cuenta}**")
    tipo = st.radio("Acción", ["Gasto", "Ingreso"], horizontal=True)
    monto = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    
    if st.button("CONFIRMAR OPERACIÓN", use_container_width=True):
        if monto > 0:
            db["transactions"].append({
                "id": str(uuid.uuid4())[:8],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": tipo,
                "amount": monto,
                "account": cuenta
            })
            save_db(db); st.rerun()

# --- INTERFAZ PRINCIPAL ---

# 1. BOTÓN DE SALDO (Hero Section)
st.markdown('<div class="hero-btn">', unsafe_allow_html=True)
if st.button(f"DISPONIBLE TOTAL\n${saldo_total:,.2f}", key="main_balance"):
    sueldo_dialog()
st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown("<p style='color:#94a3b8; font-size:12px; text-align:center;'>Toca el saldo para ajustar tu sueldo base</p>", unsafe_allow_html=True)
st.write("")

# 2. SECCIÓN DE CUENTAS (Mosaico Interactivo)
st.subheader("🏦 Cuentas")
col1, col2 = st.columns(2, gap="medium")

# Calcular saldos individuales de forma simple
def get_bal(acc_name):
    i = df[(df['type']=='Ingreso') & (df['account']==acc_name)]['amount'].sum()
    g = df[(df['type']=='Gasto') & (df['account']==acc_name)]['amount'].sum()
    base = sueldo if acc_name == "Banco" else 0
    return base + i - g

with col1:
    if st.button(f"BANCO\n${get_bal('Banco'):,.2f}", key="btn_banco"):
        add_val_dialog("Banco")

with col2:
    if st.button(f"EFECTIVO\n${get_bal('Efectivo'):,.2f}", key="btn_efectivo"):
        add_val_dialog("Efectivo")

# 3. ÁREA DE DATOS
st.write("---")
tab_hist, tab_met = st.tabs(["📝 ACTIVIDAD", "📊 RESUMEN"])

with tab_hist:
    if not df.empty:
        # Mostramos una tabla minimalista
        df_view = df.sort_index(ascending=False).head(10)
        st.dataframe(df_view[['date', 'type', 'account', 'amount']], use_container_width=True, hide_index=True)
    else:
        st.info("Sin movimientos recientes.")

with tab_met:
    col_a, col_b = st.columns(2)
    col_a.metric("Total Ingresos", f"${ingresos:,.2f}")
    col_b.metric("Total Gastos", f"${gastos:,.2f}", delta=f"-{gastos:,.2f}", delta_color="inverse")
