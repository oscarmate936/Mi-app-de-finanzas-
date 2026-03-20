import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS CSS (REDISEÑO FINTECH IDÉNTICO A IMAGEN) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
    
    /* 1. Tarjeta de Salario (Botón Superior Estilo Card) */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #0d1e3a, #1a3a5f) !important;
        color: white !important;
        border-radius: 18px !important;
        border: none !important;
        padding: 30px 20px !important;
        height: 160px !important;
        text-align: left !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    /* 2, 3. Tarjetas de Resumen Blancas */
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        height: 100px;
    }
    .stat-label { font-size: 13px; color: #6c757d; font-weight: 500; }
    .stat-value { font-size: 20px; font-weight: 700; color: #333; margin-top: 5px; }
    
    /* 4. Tarjeta Azul de Saldo Actual */
    .delta-card {
        background: #007bff;
        color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        margin: 20px 0;
        text-align: left;
    }

    /* 5. Transacciones Recientes */
    .trans-item {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #f0f0f0;
    }
    .trans-info { display: flex; align-items: center; gap: 12px; }
    .trans-icon { 
        width: 35px; height: 35px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; font-size: 16px;
    }
    .trans-cat { font-weight: 700; color: #333; font-size: 14px; }
    .trans-note { font-size: 12px; color: #999; display: block; }
    .amount-val { font-weight: 700; font-size: 15px; }

    /* 6 y 7. Botones Inferiores */
    .stButton > button[kind="primary"] { /* GASTOS */
        background-color: #ff3b30 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    /* El botón de ingresos lo manejaremos con una columna custom */
    .green-btn {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 55px !important;
        width: 100% !important;
        font-weight: 700 !important;
        border: none !important;
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
        
        # --- SOLUCIÓN AL KEYERROR (REPARACIÓN AUTOMÁTICA) ---
        default_settings = {"sueldo": 0.0, "pago": "---"}
        if "settings" not in data:
            data["settings"] = default_settings
        else:
            # Si settings existe pero le faltan llaves, las agregamos
            for k, v in default_settings.items():
                if k not in data["settings"]:
                    data["settings"][k] = v
                    
        if "transactions" not in data: data["transactions"] = []
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

# Datos Mes Actual
mes_actual = datetime.now().month
df_mes = df[df['date_dt'].dt.month == mes_actual] if not df.empty else df

sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
delta_mes = ingresos_mes - gastos_mes

# Saldo Final Acumulado
saldo_final = sueldo_base + df[df['type']=='Ingreso']['amount'].sum() - df[df['type']=='Gasto']['amount'].sum()

# --- DIÁLOGOS ---
@st.dialog("🎯 Editar Sueldo")
def sueldo_dialog():
    s = st.number_input("Monto fijo", value=sueldo_base)
    f = st.date_input("Fecha de pago")
    if st.button("Actualizar", use_container_width=True):
        db["settings"]["sueldo"] = s
        db["settings"]["pago"] = f.strftime("%d %b")
        save_db(db); st.rerun()

@st.dialog("🟢 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.0)
    if st.button("Guardar", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Ingreso Extra", "amount": amt, "note": "Ingreso adicional"
        })
        save_db(db); st.rerun()

@st.dialog("🔴 Registrar Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Entertainment", "Comida", "Transporte", "Servicios", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.0)
    note = st.text_input("Descripción")
    if st.button("Registrar", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ (ORDEN SEGÚN IMAGEN) ---

# 1. Botón Salario (Tarjeta)
pago_txt = db["settings"].get("pago", "---")
if st.button(f"💳 {pago_txt} \n\n SALARIO: ${sueldo_base:,.2f}", key="btn_salary", use_container_width=True, kind="secondary"):
    sueldo_dialog()

# 2 y 3. Fila de Mosaicos (Ingresos y Gastos del mes)
st.write("")
col_ing, col_gas = st.columns(2)
with col_ing:
    st.markdown(f'<div class="stat-card"><div class="stat-label">↓ Ingresos</div><div class="stat-value">${ingresos_mes:,.2f}</div><div class="stat-label">Este Mes</div></div>', unsafe_allow_html=True)
with col_gas:
    st.markdown(f'<div class="stat-card"><div class="stat-label">↑ Gastos</div><div class="stat-value">${gastos_mes:,.2f}</div><div class="stat-label">Este Mes</div></div>', unsafe_allow_html=True)

# 4. Saldo Actual (Azul)
color_delta = "#ffffff"
st.markdown(f"""<div class="delta-card">
    <div style="font-size:14px; opacity:0.8">Saldo Actual (Mes)</div>
    <div style="font-size:36px; font-weight:bold">${delta_mes:,.2f}</div>
</div>""", unsafe_allow_html=True)

# 5. Lista de Transacciones con Borrado
st.write("### Transacciones Recientes")
if not df.empty:
    for _, row in df.sort_values('date', ascending=False).iterrows():
        c_icon = "#e8f5e9" if row['type'] == 'Ingreso' else "#ffebee"
        c_txt = "#28a745" if row['type'] == 'Ingreso' else "#ff3b30"
        
        # Estructura de item
        st.markdown(f"""
        <div class="trans-item">
            <div class="trans-info">
                <div class="trans-icon" style="background:{c_icon}; color:{c_txt}">{'↓' if row['type'] == 'Ingreso' else '↑'}</div>
                <div class="trans-text"><span class="trans-cat">{row['category']}</span><span class="trans-note">{row['note']}</span></div>
            </div>
            <div style="text-align:right">
                <div class="amount-val" style="color:{c_txt}">{'+' if row['type'] == 'Ingreso' else '-'}${row['amount']:,.2f}</div>
                <div style="font-size:10px; color:#ccc">{row['date']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Botón de borrar integrado
        if st.button("🗑️ Borrar", key=f"del_{row['id']}", use_container_width=True):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()

# Resumen Final (Sueldo + Neto)
st.divider()
st.success(f"**TOTAL NETO DISPONIBLE: ${saldo_final:,.2f}**")

# 6 y 7. Botones Inferiores (Flotantes visualmente)
st.write("<br><br>", unsafe_allow_html=True)
c6, c7 = st.columns(2)
with c6:
    if st.button("↓ Ingresos", key="btn_ing", use_container_width=True):
        ingreso_dialog()
with c7:
    if st.button("↑ Gastos", key="btn_gas", use_container_width=True, type="primary"):
        gasto_dialog()