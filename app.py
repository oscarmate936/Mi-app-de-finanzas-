import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES (MÁXIMO NIVEL MÓVIL) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #f1f3f6; }
    
    /* Contenedor General */
    .main { padding-top: 0rem; }

    /* Estilo para los botones de Streamlit (Transformados en Tiles de App) */
    div.stButton > button {
        width: 100% !important;
        border-radius: 20px !important;
        padding: 20px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        display: block !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    
    /* Botón de GASTO (Rojo) */
    div.stButton > button[kind="primary"] {
        background: #ffebee !important;
        border: 2px solid #ef5350 !important;
        color: #c62828 !important;
    }
    
    /* Botón de INGRESO (Verde) */
    div.stButton > button[kind="secondary"] {
        background: #e8f5e9 !important;
        border: 2px solid #66bb6a !important;
        color: #2e7d32 !important;
    }

    /* Botón de AJUSTES (Azul Punteado) */
    div.stButton > button[kind="tertiary"] {
        background: #ffffff !important;
        border: 2px dashed #007bff !important;
        color: #007bff !important;
    }

    /* Hover effects para que se sienta táctil */
    div.stButton > button:active {
        transform: scale(0.96) !important;
        background-color: #eee !important;
    }

    /* Tarjeta de Saldo Principal */
    .balance-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 25px;
        padding: 35px 20px;
        text-align: center;
        box-shadow: 0 12px 20px rgba(30, 60, 114, 0.2);
        margin-bottom: 25px;
    }
    .balance-label { font-size: 14px; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; }
    .balance-value { font-size: 44px; font-weight: 800; }

    /* Estilo de los nombres de cuenta dentro de los botones */
    .button-subtext { font-size: 12px; font-weight: normal; opacity: 0.7; display: block; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Revisa tus Secrets en Streamlit Cloud.")
    st.stop()

@st.cache_data(ttl=300)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        default_set = {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}
        if "settings" not in data: data["settings"] = default_set
        else:
            for k, v in default_set.items():
                if k not in data["settings"]: data["settings"][k] = v
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA DE DATOS (BLINDADA) ---
df = pd.DataFrame(db["transactions"])
columnas = ["id", "date", "type", "category", "amount", "note", "account"]

if df.empty:
    df = pd.DataFrame(columns=columnas)
else:
    for col in columnas:
        if col not in df.columns:
            df[col] = "Banco" if col == "account" else "N/A"
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

sueldo = float(db["settings"].get("sueldo", 0))
saldo_total = sueldo + df[df['type']=='Ingreso']['amount'].sum() - df[df['type']=='Gasto']['amount'].sum()

# --- DIÁLOGOS DE ENTRADA (OVERLAYS) ---
@st.dialog("⚙️ CONFIGURACIÓN")
def config_dialog():
    s = st.number_input("Sueldo Base Mensual", value=sueldo)
    p = st.number_input("Meta de Gasto Mensual", value=float(db["settings"].get("presupuesto", 0)))
    if st.button("GUARDAR CAMBIOS", type="primary"):
        db["settings"]["sueldo"], db["settings"]["presupuesto"] = s, p
        save_db(db); st.rerun()

@st.dialog("➕ NUEVO REGISTRO")
def trans_dialog(tipo, cuenta_predefinida=None):
    st.markdown(f"### Registrar {tipo}")
    cuentas = db["settings"].get("cuentas", ["Banco", "Efectivo"])
    
    # Si tocaste un botón de cuenta, ya viene seleccionada
    idx_cuenta = cuentas.index(cuenta_predefinida) if cuenta_predefinida in cuentas else 0
    acc = st.selectbox("Cuenta", cuentas, index=idx_cuenta)
    
    cat_list = ["Comida", "Transporte", "Servicios", "Ocio", "Salud", "Educación", "Otros"] if tipo == "Gasto" else ["Ingreso Extra", "Bono", "Venta"]
    cat = st.selectbox("Categoría", cat_list)
    amt = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    note = st.text_input("Nota (opcional)")
    fecha = st.date_input("Fecha", datetime.now())
    
    if st.button(f"CONFIRMAR {tipo.upper()}", use_container_width=True):
        if amt > 0:
            db["transactions"].append({
                "id": str(uuid.uuid4())[:8], "date": fecha.strftime("%Y-%m-%d"),
                "type": tipo, "category": cat, "amount": amt, "note": note, "account": acc
            })
            save_db(db); st.rerun()

# --- INTERFAZ DE APP MÓVIL ---
st.markdown(f"""
<div class="balance-card">
    <div class="balance-label">Disponible Total</div>
    <div class="balance-value">${saldo_total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 1. BOTONES DE ACCIÓN RÁPIDA
col1, col2 = st.columns(2, gap="small")
with col1:
    if st.button("🔴 GASTO\nNuevo registro", type="primary", key="btn_gasto"):
        trans_dialog("Gasto")
with col2:
    if st.button("🟢 INGRESO\nNuevo registro", type="secondary", key="btn_ingreso"):
        trans_dialog("Ingreso")

st.write("")
if st.button("⚙️ AJUSTES Y METAS\nConfigurar moneda y sueldo", type="tertiary"):
    config_dialog()

st.write("---")

# 2. SECCIÓN DE CUENTAS (BOTONES DINÁMICOS)
st.subheader("🏦 Mis Cuentas")
st.caption("Toca una cuenta para añadir un movimiento rápido")

cuentas = db["settings"].get("cuentas", ["Banco", "Efectivo"])
cols_cuentas = st.columns(len(cuentas))

for i, acc in enumerate(cuentas):
    with cols_cuentas[i]:
        # Calcular saldo individual
        i_acc = df[(df['type']=='Ingreso') & (df['account']==acc)]['amount'].sum()
        g_acc = df[(df['type']=='Gasto') & (df['account']==acc)]['amount'].sum()
        bal_acc = (sueldo if acc == "Banco" else 0) + i_acc - g_acc
        
        # El botón mismo muestra el nombre y el saldo
        if st.button(f"{acc.upper()}\n${bal_acc:,.2f}", key=f"acc_{acc}"):
            trans_dialog("Gasto", cuenta_predefinida=acc)

# 3. PESTAÑAS DE APOYO (HISTORIAL Y REPORTES)
st.write("---")
tab_h, tab_r = st.tabs(["📝 Historial", "📊 Análisis"])

with tab_h:
    mes_actual = datetime.now().month
    df_mes = df[df['date'].dt.month == mes_actual] if not df.empty else df
    if not df_mes.empty:
        st.dataframe(df_mes.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos este mes.")

with tab_r:
    if not df.empty:
        fig = px.pie(df[df['type']=='Gasto'], values='amount', names='category', hole=0.5, title="Gastos por Categoría")
        fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
