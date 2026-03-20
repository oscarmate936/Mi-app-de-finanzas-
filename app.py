import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES (MÓVIL) ---
st.markdown("""
<style>
header {visibility: hidden;}
button p { white-space: pre-wrap !important; text-align: center !important; line-height: 1.4 !important; }

/* Botón Sueldo */
button[kind="tertiary"] {
    background-color: #f8f9fa !important;
    border: 2px dashed #007bff !important;
    border-radius: 15px !important;
    padding: 15px !important;
    min-height: 90px !important;
}

/* Botón Ingresos (Verde) */
button[kind="secondary"] {
    background-color: #e8f5e9 !important;
    border: 2px solid #4CAF50 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    min-height: 100px !important;
}
button[kind="secondary"] p { color: #2e7d32 !important; font-weight: 700 !important; font-size: 16px !important; }

/* Botón Gastos (Rojo) */
button[kind="primary"] {
    background-color: #ffebee !important;
    border: 2px solid #F44336 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    min-height: 100px !important;
}
button[kind="primary"] p { color: #c62828 !important; font-weight: 700 !important; font-size: 16px !important; }

/* Tarjeta Azul Saldo */
.total-card {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 8px 15px rgba(0, 123, 255, 0.2);
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A JSONBIN ---
BIN_ID = st.secrets["bin_id"]
API_KEY = st.secrets["api_key"]
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        if "settings" not in data: data["settings"] = {}
        return data
    except:
        return {"transactions": [], "settings": {}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)

db = get_db()

# --- FUNCIONES DE LÓGICA ---
def add_trans(date, t_type, cat, amt, note):
    t_id = str(uuid.uuid4())[:8]
    db["transactions"].append({"id": t_id, "date": date, "type": t_type, "category": cat, "amount": float(amt), "note": note})
    save_db(db)

def delete_trans(t_id):
    db["transactions"] = [t for t in db["transactions"] if t["id"] != str(t_id)]
    save_db(db)

# --- DATOS PARA MOSTRAR ---
df = pd.DataFrame(db["transactions"])
sueldo = float(db["settings"].get("sueldo", 0))
fecha_pago = db["settings"].get("fecha", "No definida")

if not df.empty:
    ingresos_totales = df[df['type'] == 'Ingreso']['amount'].sum()
    gastos_totales = df[df['type'] == 'Gasto']['amount'].sum()
else:
    ingresos_totales = gastos_totales = 0.0

saldo_final = sueldo + ingresos_totales - gastos_totales

# --- VENTANAS (DIALOGS) ---
@st.dialog("⚙️ Configurar Sueldo")
def config():
    s = st.number_input("Sueldo Base", value=sueldo)
    f = st.date_input("Fecha de Pago")
    if st.button("Guardar"):
        db["settings"]["sueldo"] = s
        db["settings"]["fecha"] = f.strftime("%d/%m/%Y")
        save_db(db)
        st.rerun()

@st.dialog("🟢 Nuevo Ingreso")
def ingreso():
    amt = st.number_input("Monto", min_value=0.01)
    note = st.text_input("Nota")
    if st.button("Añadir"):
        add_trans(datetime.now().strftime("%Y-%m-%d"), "Ingreso", "Ingreso Extra", amt, note)
        st.rerun()

@st.dialog("🔴 Nuevo Gasto")
def gasto():
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Ocio", "Salud", "Otros"])
    amt = st.number_input("Monto", min_value=0.01)
    note = st.text_input("Nota")
    if st.button("Registrar"):
        add_trans(datetime.now().strftime("%Y-%m-%d"), "Gasto", cat, amt, note)
        st.rerun()

# --- INTERFAZ ---
t1, t2, t3 = st.tabs(["🏠 Inicio", "📝 Historial", "📊 Gráficos"])

with t1:
    if st.button(f"⚙️ Sueldo: ${sueldo:,.2f}\n📅 Pago: {fecha_pago}", type="tertiary", use_container_width=True):
        config()
    
    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button(f"↓ INGRESOS\n${ingresos_totales:,.2f}", type="secondary", use_container_width=True):
            ingreso()
    with col2:
        if st.button(f"↑ GASTOS\n${gastos_totales:,.2f}", type="primary", use_container_width=True):
            gasto()
            
    st.markdown(f'<div class="total-card"><small>Saldo Total</small><div class="total-value">${saldo_total:,.2f}</div></div>', unsafe_allow_html=True)

with t2:
    st.subheader("Historial")
    if not df.empty:
        st.dataframe(df[['date', 'category', 'amount', 'note']].iloc[::-1], use_container_width=True, hide_index=True)
        sel = st.selectbox("Borrar registro (ID):", df['id'].tolist())
        if st.button("🗑️ Eliminar Seleccionado"):
            delete_trans(sel)
            st.rerun()

with t3:
    st.subheader("Análisis")
    if not df.empty and (df['type'] == 'Gasto').any():
        fig = px.pie(df[df['type'] == 'Gasto'], values='amount', names='category', hole=0.4, title="Gastos por Categoría")
        st.plotly_chart(fig, use_container_width=True)
        
        df['date'] = pd.to_datetime(df['date'])
        fig2 = px.bar(df[df['type'] == 'Gasto'].groupby('date')['amount'].sum().reset_index(), x='date', y='amount', title="Gastos por Día")
        st.plotly_chart(fig2, use_container_width=True)
