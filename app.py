import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES (REDISEÑO MÓVIL PRO) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
    
    /* Botones Estilo Móvil */
    button[kind="tertiary"] {
        background-color: #ffffff !important;
        border: 2px dashed #007bff !important;
        border-radius: 15px !important;
        padding: 15px !important;
        min-height: 90px !important;
    }
    button[kind="tertiary"] p { color: #007bff !important; font-weight: 600 !important; }

    button[kind="secondary"] {
        background-color: #e8f5e9 !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 15px !important;
        min-height: 100px !important;
    }
    button[kind="secondary"] p { color: #2e7d32 !important; font-weight: 800 !important; font-size: 18px !important; }

    button[kind="primary"] {
        background-color: #ffebee !important;
        border: 2px solid #F44336 !important;
        border-radius: 15px !important;
        min-height: 100px !important;
    }
    button[kind="primary"] p { color: #c62828 !important; font-weight: 800 !important; font-size: 18px !important; }

    /* Tarjetas de Dashboard */
    .total-card {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0, 123, 255, 0.2);
        margin: 15px 0;
    }
    .total-value { font-size: 42px; font-weight: 800; }
    
    .account-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
        text-align: center;
        flex: 1;
        min-width: 140px;
        margin: 5px;
    }
    .account-name { font-size: 12px; color: #666; font-weight: 600; text-transform: uppercase; }
    .account-balance { font-size: 20px; font-weight: 700; color: #333; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Error en Secrets.")
    st.stop()

@st.cache_data(ttl=300)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        if "recurrentes" not in data: data["recurrentes"] = []
        default_set = {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}
        if "settings" not in data:
            data["settings"] = default_set
        else:
            for k, v in default_set.items():
                if k not in data["settings"]: data["settings"][k] = v
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}, "recurrentes": []}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA CORE ---
def add_trans(t_type, cat, amt, note, account, date_str=None):
    db["transactions"].append({
        "id": str(uuid.uuid4())[:8], 
        "date": date_str if date_str else datetime.now().strftime("%Y-%m-%d"), 
        "type": t_type, "category": cat, "amount": float(amt), "note": note, "account": account
    })
    save_db(db)

# --- PROCESAMIENTO (SOLUCIÓN AL KEYERROR) ---
df = pd.DataFrame(db["transactions"])
columnas_necesarias = ["id", "date", "type", "category", "amount", "note", "account"]

if df.empty:
    df = pd.DataFrame(columns=columnas_necesarias)
else:
    # Si existen datos pero faltan columnas (como 'account'), las creamos con valor por defecto
    for col in columnas_necesarias:
        if col not in df.columns:
            df[col] = "Banco" if col == "account" else "N/A"
    
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

# Sidebar
st.sidebar.title("🔍 FILTROS")
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
sel_mes = st.sidebar.selectbox("Mes", range(1, 13), index=datetime.now().month-1, format_func=lambda x: meses[x-1])
sel_año = st.sidebar.number_input("Año", 2024, 2030, datetime.now().year)

df_mes = df[(df['date'].dt.month == sel_mes) & (df['date'].dt.year == sel_año)]
sueldo = float(db["settings"].get("sueldo", 0))
ingresos_t = df[df['type'] == 'Ingreso']['amount'].sum()
gastos_t = df[df['type'] == 'Gasto']['amount'].sum()
saldo_neto = sueldo + ingresos_t - gastos_t

# --- DIALOGS ---
@st.dialog("⚙️ AJUSTES")
def config_dialog():
    s = st.number_input("Sueldo Base ($)", value=sueldo)
    p = st.number_input("Meta Gasto ($)", value=float(db["settings"].get("presupuesto", 0)))
    if st.button("GUARDAR", use_container_width=True, type="primary"):
        db["settings"]["sueldo"], db["settings"]["presupuesto"] = s, p
        save_db(db); st.rerun()

@st.dialog("➕ MOVIMIENTO")
def trans_dialog(tipo):
    acc = st.selectbox("Cuenta", db["settings"].get("cuentas", ["Banco", "Efectivo"]))
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Ocio", "Otros"]) if tipo == "Gasto" else "Ingreso Extra"
    amt = st.number_input("Monto", min_value=0.01)
    note = st.text_input("Nota")
    if st.button("REGISTRAR", use_container_width=True):
        add_trans(tipo, cat, amt, note, acc); st.rerun()

# --- INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:#007bff;'>CASHBOOK</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏠 INICIO", "📝 HISTORIAL", "📊 REPORTES"])

with tab1:
    st.markdown(f'<div class="total-card"><div style="opacity:0.8">Saldo Neto Total</div><div class="total-value">${saldo_neto:,.2f}</div></div>', unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("↑ GASTO\nRegistrar", type="primary", use_container_width=True): trans_dialog("Gasto")
    with col_b2:
        if st.button("↓ INGRESO\nRegistrar", type="secondary", use_container_width=True): trans_dialog("Ingreso")
    
    if st.button("⚙️ AJUSTES Y METAS\nConfigurar App", type="tertiary", use_container_width=True): config_dialog()

    st.write("### 🏦 Mis Cuentas")
    cuentas = db["settings"].get("cuentas", ["Efectivo", "Banco"])
    
    # Generación de HTML ultra-limpia
    html_cuentas = '<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">'
    for acc in cuentas:
        i_acc = df[(df['type']=='Ingreso') & (df['account']==acc)]['amount'].sum()
        g_acc = df[(df['type']=='Gasto') & (df['account']==acc)]['amount'].sum()
        bal = (sueldo if acc == "Banco" else 0) + i_acc - g_acc
        card = f'<div class="account-card"><div class="account-name">{acc}</div><div class="account-balance">${bal:,.2f}</div></div>'
        html_cuentas += card
    html_cuentas += '</div>'
    
    st.markdown(html_cuentas, unsafe_allow_html=True)

with tab2:
    st.subheader("Movimientos del Mes")
    if not df_mes.empty:
        st.dataframe(df_mes.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos este mes.")

with tab3:
    if not df_mes[df_mes['type']=='Gasto'].empty:
        st.plotly_chart(px.pie(df_mes[df_mes['type']=='Gasto'], values='amount', names='category', hole=0.4), use_container_width=True)
