import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cash Book Premium", page_icon="💎", layout="centered")

# --- ESTILOS CSS (EL HÍBRIDO PERFECTO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }

    /* 1. Tarjeta de Salario (Botón Indigo Estilo Card) */
    div.stButton > button[key="btn_1"] {
        background: linear-gradient(135deg, #1e1b4b, #312e81) !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 35px 25px !important;
        height: 160px !important;
        text-align: left !important;
        box-shadow: 0 10px 20px rgba(30, 27, 75, 0.2) !important;
    }

    /* 2, 3. Mosaico de Tarjetas Blancas */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #F1F5F9;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stat-label { font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .stat-value { font-size: 24px; font-weight: 800; color: #1E293B; margin-top: 5px; }
    
    /* 4. Tarjeta Azul de Saldo Actual */
    .balance-card {
        background: #2563EB;
        color: white;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0 10px 15px rgba(37, 99, 235, 0.2);
        margin: 20px 0;
    }

    /* 5. Transacciones Recientes */
    .trans-item {
        background: white;
        padding: 16px;
        border-radius: 18px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #F1F5F9;
    }
    .trans-icon { 
        width: 40px; height: 40px; border-radius: 12px; 
        display: flex; align-items: center; justify-content: center; font-size: 18px;
    }

    /* 6 y 7. Botones Inferiores */
    div.stButton > button[key="btn_6"] {
        background-color: #10B981 !important; /* Verde */
        color: white !important;
        border-radius: 15px !important;
        height: 60px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    div.stButton > button[key="btn_7"] {
        background-color: #F43F5E !important; /* Rojo */
        color: white !important;
        border-radius: 15px !important;
        height: 60px !important;
        font-weight: 700 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        # Reparación automática de llaves
        default_s = {"sueldo": 0.0, "pago": "---"}
        if "settings" not in data: data["settings"] = default_s
        else:
            for k, v in default_s.items():
                if k not in data["settings"]: data["settings"][k] = v
        if "transactions" not in data: data["transactions"] = []
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "pago": "---"}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- CÁLCULOS ---
df = pd.DataFrame(db["transactions"])
if df.empty:
    df = pd.DataFrame(columns=["id", "date", "type", "category", "amount", "note"])
else:
    df['date_dt'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount']).fillna(0.0)

mes_actual = datetime.now().month
df_mes = df[df['date_dt'].dt.month == mes_actual] if not df.empty else df

# Lógica solicitada:
# Casilla 2: Solo ingresos del mes
# Casilla 3: Solo gastos del mes
# Casilla 4: Diferencia (Ingresos - Gastos) del mes
sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
delta_mes = ingresos_mes - gastos_mes

# Saldo Final (Sueldo + todos los ingresos - todos los gastos)
saldo_real = sueldo_base + df[df['type']=='Ingreso']['amount'].sum() - df[df['type']=='Gasto']['amount'].sum()

# --- DIÁLOGOS ---
@st.dialog("💳 Mi Pago")
def sueldo_dialog():
    s = st.number_input("Monto fijo", value=sueldo_base)
    f = st.date_input("Fecha de pago")
    if st.button("Guardar", use_container_width=True):
        db["settings"]["sueldo"] = s
        db["settings"]["pago"] = f.strftime("%d %b")
        save_db(db); st.rerun()

@st.dialog("🟢 Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.0)
    if st.button("Confirmar", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Extra", "amount": amt, "note": "Ingreso"
        })
        save_db(db); st.rerun()

@st.dialog("🔴 Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Ocio", "Servicios", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.0)
    note = st.text_input("Nota")
    if st.button("Registrar", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ (ESTRUCTURA 1-7) ---

# 1. BOTÓN SUPERIOR (Sueldo)
pago_txt = db["settings"].get("pago", "---")
if st.button(f"✨ MI PAGO · {pago_txt} \n\n SALARIO: ${sueldo_base:,.2f}", key="btn_1", use_container_width=True):
    sueldo_dialog()

# 2 y 3. MOSAICO (Grid)
st.write("")
col2, col3 = st.columns(2)
with col2:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-label">Ingresos</div>
        <div class="stat-value" style="color:#10B981;">+${ingresos_mes:,.2f}</div>
        <div class="stat-label">Este Mes</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-label">Gastos</div>
        <div class="stat-value" style="color:#F43F5E;">-${gastos_mes:,.2f}</div>
        <div class="stat-label">Este Mes</div>
    </div>""", unsafe_allow_html=True)

# 4. TARJETA AZUL (Balance Mes)
color_delta = "#FFFFFF" # El texto siempre blanco sobre azul
st.markdown(f"""<div class="balance-card">
    <div style="font-size:14px; opacity:0.8; font-weight:600;">BALANCE DEL MES (+/-)</div>
    <div style="font-size:36px; font-weight:800;">{'+' if delta_mes >= 0 else ''}${delta_mes:,.2f}</div>
</div>""", unsafe_allow_html=True)

# 5. TRANSACCIONES RECIENTES
st.markdown("### Transacciones Recientes")
if not df.empty:
    for _, row in df.sort_values('date', ascending=False).iterrows():
        c_bg = "#DCFCE7" if row['type'] == 'Ingreso' else "#FFE4E6"
        c_tx = "#10B981" if row['type'] == 'Ingreso' else "#F43F5E"
        st.markdown(f"""
        <div class="trans-item">
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="trans-icon" style="background:{c_bg}; color:{c_tx}">{'↓' if row['type'] == 'Ingreso' else '↑'}</div>
                <div>
                    <span class="trans-cat">{row['category']}</span>
                    <span class="trans-note" style="display:block;">{row['note']}</span>
                </div>
            </div>
            <div style="text-align:right">
                <div class="amount-val" style="color:{c_tx}">{'+' if row['type'] == 'Ingreso' else '-'}${row['amount']:,.2f}</div>
                <div style="font-size:10px; color:#94A3B8">{row['date']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ Borrar", key=f"del_{row['id']}", use_container_width=True):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()

# 💰 SALDO TOTAL (Sueldo + Todo lo demás)
st.write("---")
st.success(f"**EFECTIVO TOTAL DISPONIBLE: ${saldo_real:,.2f}**")

# 6 y 7. BOTONES INFERIORES
st.write("<br><br>", unsafe_allow_html=True)
col6, col7 = st.columns(2)
with col6:
    if st.button("↓ Ingresos", key="btn_6", use_container_width=True):
        ingreso_dialog()
with col7:
    if st.button("↑ Gastos", key="btn_7", use_container_width=True):
        gasto_dialog()
