import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Premium", page_icon="💎", layout="centered")

# --- ESTILOS CSS (DISEÑO MOBILE PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fondo General Slate */
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }

    /* 1. Tarjeta de Salario (Estilo Card de Lujo) */
    div.stButton > button[key="btn_salary"] {
        background: linear-gradient(135deg, #4338CA, #6366F1) !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        padding: 40px 25px !important;
        height: 180px !important;
        text-align: left !important;
        box-shadow: 0 20px 25px -5px rgba(67, 56, 202, 0.2) !important;
        margin-bottom: 20px !important;
    }

    /* 2, 3. Tarjetas de Resumen (Mosaico) */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #F1F5F9;
        margin-bottom: 10px;
    }
    .stat-label { font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 22px; font-weight: 800; color: #1E293B; margin-top: 5px; }
    
    /* 4. Tarjeta Azul de Saldo Actual (Mes) */
    .delta-card {
        background: #FFFFFF;
        color: #1E293B;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 2px solid #E2E8F0;
        margin: 20px 0;
    }
    .delta-title { font-size: 14px; color: #64748B; font-weight: 600; }
    .delta-value { font-size: 36px; font-weight: 800; color: #4338CA; }

    /* 5. Transacciones Recientes */
    .trans-item {
        background: white;
        padding: 16px;
        border-radius: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #F1F5F9;
        transition: transform 0.2s;
    }
    .trans-icon { 
        width: 44px; height: 44px; border-radius: 14px; 
        display: flex; align-items: center; justify-content: center; font-size: 20px;
    }
    .trans-cat { font-weight: 700; color: #1E293B; font-size: 15px; }
    .trans-note { font-size: 12px; color: #94A3B8; }
    .amount-val { font-weight: 800; font-size: 16px; }

    /* 6 y 7. Botones Inferiores (Premium Look) */
    div.stButton > button[key="btn_ing"], div.stButton > button[key="btn_gas"] {
        border-radius: 18px !important;
        height: 65px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Color Verde Premium */
    div.stButton > button[key="btn_ing"] {
        background-color: #10B981 !important;
        color: white !important;
    }
    
    /* Color Rojo Premium */
    div.stButton > button[key="btn_gas"] {
        background-color: #F43F5E !important;
        color: white !important;
    }

    /* Estilo del botón eliminar */
    div.stButton > button[key^="del_"] {
        background-color: #F1F5F9 !important;
        color: #64748B !important;
        border: none !important;
        font-size: 11px !important;
        height: 30px !important;
        margin-top: -10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS (Auto-reparable) ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Configura los Secrets.")
    st.stop()

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        # Reparar estructura si es necesario
        default_settings = {"sueldo": 0.0, "pago": "---"}
        if "settings" not in data: data["settings"] = default_settings
        else:
            for k, v in default_settings.items():
                if k not in data["settings"]: data["settings"][k] = v
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

# Cálculos del Mes
mes_actual = datetime.now().month
df_mes = df[df['date_dt'].dt.month == mes_actual] if not df.empty else df

sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
delta_mes = ingresos_mes - gastos_mes

# Saldo Final Acumulado
saldo_final = sueldo_base + df[df['type']=='Ingreso']['amount'].sum() - df[df['type']=='Gasto']['amount'].sum()

# --- DIÁLOGOS ---
@st.dialog("💎 Configurar Mi Salario")
def sueldo_dialog():
    s = st.number_input("Monto Salario Fijo", value=sueldo_base, step=100.0)
    f = st.date_input("Fecha de cobro")
    if st.button("Actualizar Wallet", use_container_width=True, type="primary"):
        db["settings"]["sueldo"] = s
        db["settings"]["pago"] = f.strftime("%d %b")
        save_db(db); st.rerun()

@st.dialog("💰 Nuevo Ingreso Extra")
def ingreso_dialog():
    amt = st.number_input("Monto del Ingreso", min_value=0.0, step=10.0)
    if st.button("Guardar Ingreso", use_container_width=True, type="primary"):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Ingreso Extra", "amount": amt, "note": "Entrada extra"
        })
        save_db(db); st.rerun()

@st.dialog("💸 Registrar Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Suscripciones", "Servicios", "Ocio", "Otros"])
    amt = st.number_input("Monto Gastado", min_value=0.0, step=1.0)
    note = st.text_input("Descripción breve")
    if st.button("Confirmar Gasto", use_container_width=True, type="primary"):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:8], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ PREMIUM ---

# 1. Tarjeta de Salario (Botón Superior)
pago_txt = db["settings"].get("pago", "---")
if st.button(f"✨ MI SALARIO · {pago_txt}\n\n${sueldo_base:,.2f}\nDisponible Fijo", key="btn_salary", use_container_width=True):
    sueldo_dialog()

# 2 y 3. Mosaicos de Mes
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

# 4. Saldo Mensual (Delta)
color_delta = "#10B981" if delta_mes >= 0 else "#F43F5E"
st.markdown(f"""<div class="delta-card">
    <div class="delta-title">BALANCE DEL MES</div>
    <div class="delta-value" style="color:{color_delta};">
        {'+' if delta_mes >= 0 else ''}${delta_mes:,.2f}
    </div>
</div>""", unsafe_allow_html=True)

# 5. Lista de Transacciones
st.markdown("### Actividad Reciente")
if not df.empty:
    for _, row in df.sort_values('date', ascending=False).iterrows():
        c_bg = "#DCFCE7" if row['type'] == 'Ingreso' else "#FFE4E6"
        c_tx = "#10B981" if row['type'] == 'Ingreso' else "#F43F5E"
        
        st.markdown(f"""
        <div class="trans-item">
            <div style="display:flex; align-items:center; gap:15px;">
                <div class="trans-icon" style="background:{c_bg}; color:{c_tx}">
                    {'󰠭' if row['type'] == 'Ingreso' else '󰠭'}
                </div>
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
        # Botón borrar sutil
        if st.button(f"Eliminar Movimiento", key=f"del_{row['id']}", use_container_width=True):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()

# Resultado Neto Final
st.write("---")
st.markdown(f"""<div style="text-align:center; padding:20px; background:#EEF2FF; border-radius:15px;">
    <span style="color:#4338CA; font-weight:800; font-size:18px;">WALLET TOTAL: ${saldo_final:,.2f}</span>
</div>""", unsafe_allow_html=True)

# 6 y 7. Botones de Acción Inferiores
st.write("<br><br>", unsafe_allow_html=True)
col6, col7 = st.columns(2)
with col6:
    if st.button("↓ Ingreso", key="btn_ing", use_container_width=True):
        ingreso_dialog()
with col7:
    if st.button("↑ Gasto", key="btn_gas", use_container_width=True):
        gasto_dialog()
