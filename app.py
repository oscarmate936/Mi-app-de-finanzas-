import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS CSS (REDISEÑO FINTECH) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
    
    /* 1. Tarjeta de Salario (Botón Superior) */
    .stButton > button.salary-btn {
        background: linear-gradient(135deg, #0d1e3a, #1a3a5f) !important;
        color: white !important;
        border-radius: 18px !important;
        border: none !important;
        padding: 25px !important;
        height: auto !important;
        text-align: left !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    /* 2, 3 y 4. Tarjetas de Resumen */
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        text-align: left;
    }
    .stat-label { font-size: 13px; color: #6c757d; font-weight: 500; }
    .stat-value { font-size: 22px; font-weight: 700; color: #333; margin: 5px 0; }
    
    /* 4. Tarjeta Azul de Saldo Actual */
    .delta-card {
        background: #007bff;
        color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        margin: 20px 0;
    }

    /* 5. Transacciones Recientes */
    .trans-item {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #f0f0f0;
    }
    .trans-info { display: flex; align-items: center; gap: 12px; }
    .trans-icon { 
        width: 40px; height: 40px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; font-size: 18px;
    }
    .trans-text { display: flex; flex-direction: column; }
    .trans-cat { font-weight: 700; color: #333; font-size: 15px; }
    .trans-note { font-size: 12px; color: #999; }
    .trans-amount { text-align: right; }
    .amount-val { font-weight: 700; font-size: 16px; }
    .amount-date { font-size: 11px; color: #bbb; }

    /* 6 y 7. Botones Inferiores */
    .bottom-bar {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        padding: 0 20px;
        display: flex;
        gap: 15px;
        z-index: 99;
    }
    .stButton > button.ingreso-btn {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: 700 !important;
    }
    .stButton > button.gasto-btn {
        background-color: #ff3b30 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: 700 !important;
    }
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

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        if "settings" not in data: data["settings"] = {"sueldo": 0.0, "pago": "---"}
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "pago": "---"}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- PROCESAMIENTO ---
df = pd.DataFrame(db["transactions"])
if df.empty:
    df = pd.DataFrame(columns=["id", "date", "type", "category", "amount", "note"])
else:
    df['date_dt'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount']).fillna(0.0)

# Cálculos
mes_actual = datetime.now().month
df_mes = df[df['date_dt'].dt.month == mes_actual] if not df.empty else df

sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
delta_mes = ingresos_mes - gastos_mes

# Saldo Final (Sueldo + Todos los Ingresos - Todos los Gastos)
total_ingresos = df[df['type'] == 'Ingreso']['amount'].sum()
total_gastos = df[df['type'] == 'Gasto']['amount'].sum()
saldo_final = sueldo_base + total_ingresos - total_gastos

# --- DIÁLOGOS DE ENTRADA ---
@st.dialog("🎯 Configurar Sueldo")
def sueldo_dialog():
    s = st.number_input("Monto del pago fijo", value=sueldo_base)
    f = st.date_input("Fecha de pago")
    if st.button("Guardar Configuración", use_container_width=True):
        db["settings"]["sueldo"] = s
        db["settings"]["pago"] = f.strftime("%d %b")
        save_db(db); st.rerun()

@st.dialog("🟢 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    if st.button("Confirmar Ingreso", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Ingreso Extra", "amount": amt, "note": "Ingreso adicional"
        })
        save_db(db); st.rerun()

@st.dialog("🔴 Registrar Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Entertainment", "Comida", "Transporte", "Servicios", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    note = st.text_input("Breve descripción")
    if st.button("Registrar Gasto", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ ---

# 1. Tarjeta de Salario (Botón)
if st.button(f"💳 {db['settings']['pago']} \n\n SALARIO: ${sueldo_base:,.2f}", key="btn_1", help="Toca para editar tu sueldo", use_container_width=True):
    sueldo_dialog()

# 2 y 3. Fila de Ingresos y Gastos del mes
st.write("")
c2, c3 = st.columns(2)
with c2:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-label">↓ Ingresos</div>
        <div class="stat-value">${ingresos_mes:,.2f}</div>
        <div class="stat-label">Este Mes</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-label">↑ Gastos</div>
        <div class="stat-value">${gastos_mes:,.2f}</div>
        <div class="stat-label">Este Mes</div>
    </div>""", unsafe_allow_html=True)

# 4. Saldo Actual (Delta del mes)
color_delta = "#28a745" if delta_mes >= 0 else "#ff3b30"
st.markdown(f"""<div class="delta-card">
    <div style="font-size:14px; opacity:0.8">Saldo Actual (Mes)</div>
    <div style="font-size:36px; font-weight:bold; color:white">
        {'+' if delta_mes >= 0 else ''}${delta_mes:,.2f}
    </div>
</div>""", unsafe_allow_html=True)

# 5. Transacciones Recientes
st.write("### Transacciones Recientes")
if not df.empty:
    for idx, row in df.sort_values('date', ascending=False).iterrows():
        color_icon = "#e8f5e9" if row['type'] == 'Ingreso' else "#ffebee"
        color_arrow = "#28a745" if row['type'] == 'Ingreso' else "#ff3b30"
        symbol = "+" if row['type'] == 'Ingreso' else "-"
        
        # Item de la lista
        st.markdown(f"""
        <div class="trans-item">
            <div class="trans-info">
                <div class="trans-icon" style="background:{color_icon}; color:{color_arrow}">
                    {'↓' if row['type'] == 'Ingreso' else '↑'}
                </div>
                <div class="trans-text">
                    <span class="trans-cat">{row['category']}</span>
                    <span class="trans-note">{row['note']}</span>
                </div>
            </div>
            <div class="trans-amount">
                <span class="amount-val" style="color:{color_arrow}">{symbol}${row['amount']:,.2f}</span><br>
                <span class="amount-date">{row['date']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Botón de borrar pequeño para cada una
        if st.button(f"Eliminar {row['id']}", key=f"del_{row['id']}"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()

# Mostrar Saldo Final Total al final de la lista
st.success(f"**TOTAL DISPONIBLE (Sueldo + Neto): ${saldo_final:,.2f}**")

# Espacio para que el scroll no tape el contenido con los botones fijos
st.write("<br><br><br><br>", unsafe_allow_html=True)

# 6 y 7. Botones Inferiores Fijos
col6, col7 = st.columns(2)
with col6:
    if st.button("↓ Ingresos", key="btn_6", type="secondary", use_container_width=True):
        ingreso_dialog()
with col7:
    if st.button("↑ Gastos", key="btn_7", type="primary", use_container_width=True):
        gasto_dialog()
