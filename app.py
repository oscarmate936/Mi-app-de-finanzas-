import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cash Book Premium", page_icon="💰", layout="centered")

# --- ESTILOS CSS (DISEÑO FIEL A LA IMAGEN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Globales */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .main .block-container { padding-top: 2rem; max-width: 450px; }

    /* 1. Tarjeta Superior (Header/Wallet) */
    .header-card {
        background: white;
        padding: 15px 20px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
    .wallet-info { display: flex; align-items: center; gap: 15px; }
    .wallet-icon { 
        background: #E0F2FE; color: #0369A1; 
        width: 45px; height: 45px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center; font-size: 20px;
    }
    .wallet-text { font-weight: 700; color: #1E293B; font-size: 18px; }
    .wallet-subtext { color: #F43F5E; font-size: 14px; font-weight: 500; }

    /* 2 & 3. Mosaico Ingresos/Gastos */
    .stat-box {
        background: white;
        padding: 18px;
        border-radius: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        text-align: left;
    }
    .stat-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; color: #64748B; font-size: 14px; font-weight: 500; }
    .stat-val { font-size: 22px; font-weight: 700; color: #1E293B; }
    .stat-footer { font-size: 12px; color: #94A3B8; margin-top: 4px; }
    .icon-circle { 
        width: 24px; height: 24px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; font-size: 12px;
    }

    /* 4. Tarjeta Azul Saldo Actual */
    .blue-card {
        background: #0284C7;
        color: white;
        padding: 25px 20px;
        border-radius: 24px;
        margin: 20px 0;
        box-shadow: 0 10px 20px rgba(2, 132, 199, 0.2);
    }
    .blue-label { font-size: 14px; font-weight: 500; opacity: 0.9; margin-bottom: 5px; }
    .blue-value { font-size: 38px; font-weight: 700; }

    /* 5. Transacciones */
    .section-title { font-size: 18px; font-weight: 700; color: #1E293B; margin: 20px 0 15px 5px; display: flex; justify-content: space-between; align-items: center; }
    .btn-all { font-size: 13px; color: #0284C7; background: #E0F2FE; padding: 4px 12px; border-radius: 8px; text-decoration: none; font-weight: 600; }
    
    .trans-card {
        background: white;
        padding: 14px 18px;
        border-radius: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #F1F5F9;
    }
    .trans-main { display: flex; align-items: center; gap: 12px; }
    .trans-cat { font-weight: 600; color: #1E293B; font-size: 15px; }
    .trans-note { font-size: 13px; color: #94A3B8; }
    .trans-amount { text-align: right; }
    .amt-val { font-weight: 700; font-size: 15px; }
    .amt-date { font-size: 11px; color: #94A3B8; margin-top: 2px; }

    /* 6 & 7. Botones Inferiores Flotantes */
    .stButton > button { transition: all 0.2s ease; }
    div.stButton > button[key="btn_6"] {
        background: #4ADE80 !important; color: white !important; border: none !important;
        border-radius: 16px !important; height: 55px !important; font-weight: 700 !important; font-size: 16px !important;
    }
    div.stButton > button[key="btn_7"] {
        background: #F43F5E !important; color: white !important; border: none !important;
        border-radius: 16px !important; height: 55px !important; font-weight: 700 !important; font-size: 16px !important;
    }
    
    /* Ajuste para que los botones de borrar no rompan el diseño */
    .delete-btn { font-size: 10px !important; padding: 2px 5px !important; }
</style>
""", unsafe_allow_html=True)

# --- BACKEND (Sin cambios) ---
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
        if "settings" not in data: data["settings"] = {"sueldo": 0.0, "pago": "---"}
        if "transactions" not in data: data["transactions"] = []
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "pago": "---"}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA DE DATOS ---
df = pd.DataFrame(db["transactions"])
if df.empty:
    df = pd.DataFrame(columns=["id", "date", "type", "category", "amount", "note"])
else:
    df['date_dt'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount']).fillna(0.0)

mes_actual = datetime.now().month
df_mes = df[df['date_dt'].dt.month == mes_actual] if not df.empty else df

sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
delta_mes = ingresos_mes - gastos_mes
saldo_real = sueldo_base + df[df['type']=='Ingreso']['amount'].sum() - df[df['type']=='Gasto']['amount'].sum()

# --- DIÁLOGOS ---
@st.dialog("💳 Ajustar Sueldo")
def sueldo_dialog():
    s = st.number_input("Monto de Salario", value=sueldo_base)
    if st.button("Guardar Salario", use_container_width=True):
        db["settings"]["sueldo"] = s
        save_db(db); st.rerun()

@st.dialog("🟢 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.0)
    note = st.text_input("Concepto", "Ingreso extra")
    if st.button("Confirmar Ingreso", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Extra", "amount": amt, "note": note
        })
        save_db(db); st.rerun()

@st.dialog("🔴 Nuevo Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Entertainment", "Comida", "Transporte", "Servicios", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.0)
    note = st.text_input("Nota (Ej: Netflix)")
    if st.button("Registrar Gasto", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ VISUAL ---

# 1. HEADER CARD (Estilo Wallet de la imagen)
st.markdown(f"""
<div class="header-card">
    <div class="wallet-info">
        <div class="wallet-icon">💳</div>
        <div>
            <div class="wallet-text">1,161</div>
            <div class="wallet-subtext">$-{gastos_mes:,.2f}</div>
        </div>
    </div>
    <div style="color: #64748B;">▼</div>
</div>
""", unsafe_allow_html=True)

# 2 & 3. COLUMNAS INGRESOS / GASTOS
col_inc, col_exp = st.columns(2)
with col_inc:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-header">
            <div class="icon-circle" style="background:#DCFCE7; color:#10B981;">↓</div> Ingresos
        </div>
        <div class="stat-val">$ {ingresos_mes:,.2f}</div>
        <div class="stat-footer">Este Mes</div>
    </div>
    """, unsafe_allow_html=True)

with col_exp:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-header">
            <div class="icon-circle" style="background:#FFE4E6; color:#F43F5E;">↑</div> Gastos
        </div>
        <div class="stat-val">$ {gastos_mes:,.2f}</div>
        <div class="stat-footer">Este Mes</div>
    </div>
    """, unsafe_allow_html=True)

# 4. SALDO ACTUAL (Tarjeta Azul Central)
st.markdown(f"""
<div class="blue-card">
    <div class="blue-label">Saldo Actual</div>
    <div class="blue-value">{'-' if delta_mes < 0 else ''}$ {abs(delta_mes):,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 5. TRANSACCIONES RECIENTES
st.markdown("""<div class="section-title">Transacciones Recientes <span class="btn-all">Ver Todo</span></div>""", unsafe_allow_html=True)

if not df.empty:
    # Mostramos solo las últimas 5 para mantener el diseño limpio
    for _, row in df.sort_values('date', ascending=False).head(10).iterrows():
        is_inc = row['type'] == 'Ingreso'
        bg_c = "#DCFCE7" if is_inc else "#FFE4E6"
        tx_c = "#10B981" if is_inc else "#F43F5E"
        icon = "↓" if is_inc else "↑"
        
        st.markdown(f"""
        <div class="trans-card">
            <div class="trans-main">
                <div class="icon-circle" style="background:{bg_c}; color:{tx_c}; width:35px; height:35px; font-size:16px;">{icon}</div>
                <div>
                    <div class="trans-cat">{row['category']}</div>
                    <div class="trans-note">{row['note']}</div>
                </div>
            </div>
            <div class="trans-amount">
                <div class="amt-val" style="color:{tx_c}">{'-' if not is_inc else ''}${row['amount']:,.2f}</div>
                <div class="amt-date">{datetime.strptime(row['date'], '%Y-%m-%d').strftime('%d %b %Y')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Botón discreto para borrar
        if st.button(f"Eliminar {row['id']}", key=f"del_{row['id']}", help="Borrar transacción"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()
else:
    st.info("No hay transacciones este mes.")

# BOTÓN DE CONFIGURACIÓN DE SALARIO (Sustituye al botón gigante anterior para no romper la estética)
if st.button("⚙️ Configurar Salario Base", use_container_width=True):
    sueldo_dialog()

# 6 & 7. BOTONES INFERIORES (Sticky-style)
st.write("<br><br><br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("↓ Ingresos", key="btn_6", use_container_width=True):
        ingreso_dialog()
with c2:
    if st.button("↑ Gastos", key="btn_7", use_container_width=True):
        gasto_dialog()

# Saldo total disponible al final
st.markdown(f"""<div style="text-align:center; color:#94A3B8; font-size:12px; margin-top:20px;">EFECTIVO TOTAL: ${saldo_real:,.2f}</div>""", unsafe_allow_html=True)
