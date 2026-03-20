import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
header {visibility: hidden;}
button p { white-space: pre-wrap !important; text-align: center !important; line-height: 1.4 !important; }
button[kind="tertiary"] { background-color: #f8f9fa !important; border: 2px dashed #007bff !important; border-radius: 15px !important; padding: 15px !important; min-height: 90px !important; }
button[kind="secondary"] { background-color: #e8f5e9 !important; border: 2px solid #4CAF50 !important; border-radius: 15px !important; padding: 20px !important; min-height: 100px !important; box-shadow: 0 4px 6px rgba(76, 175, 80, 0.1) !important; }
button[kind="secondary"] p { color: #2e7d32 !important; font-weight: 700 !important; font-size: 16px !important; }
button[kind="primary"] { background-color: #ffebee !important; border: 2px solid #F44336 !important; border-radius: 15px !important; padding: 20px !important; min-height: 100px !important; box-shadow: 0 4px 6px rgba(244, 67, 54, 0.1) !important; }
button[kind="primary"] p { color: #c62828 !important; font-weight: 700 !important; font-size: 16px !important; }
.total-card { background: linear-gradient(135deg, #007bff, #0056b3); color: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 8px 15px rgba(0, 123, 255, 0.2); margin: 15px 0; }
.total-label { font-size: 14px; opacity: 0.9; margin-bottom: 5px; }
.total-value { font-size: 40px; font-weight: bold; margin: 0; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A JSONBIN ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
except:
    st.error("⚠️ Configura 'bin_id' y 'api_key' en los Secrets de Streamlit Cloud.")
    st.stop()

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

# --- LÓGICA ---
def add_trans(t_type, cat, amt, note):
    t_id = str(uuid.uuid4())[:8]
    nueva = {
        "id": t_id, 
        "date": datetime.now().strftime("%Y-%m-%d"), 
        "type": t_type, 
        "category": cat, 
        "amount": float(amt), 
        "note": note
    }
    db["transactions"].append(nueva)
    save_db(db)

def delete_trans(t_id):
    db["transactions"] = [t for t in db["transactions"] if t["id"] != str(t_id)]
    save_db(db)

# --- PROCESAMIENTO (Solución al KeyError) ---
# Forzamos las columnas para que Pandas no se pierda si la lista está vacía
columnas = ["id", "date", "type", "category", "amount", "note"]
df = pd.DataFrame(db["transactions"], columns=columnas)

sueldo_base = float(db["settings"].get("sueldo", 0))
fecha_pago = db["settings"].get("fecha", "No definida")

# Aseguramos que la columna amount sea numérica
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

ingresos_extras = df[df['type'] == 'Ingreso']['amount'].sum() if not df.empty else 0.0
gastos_totales = df[df['type'] == 'Gasto']['amount'].sum() if not df.empty else 0.0
saldo_total = sueldo_base + ingresos_extras - gastos_totales

# --- DIALOGS ---
@st.dialog("⚙️ Mi Sueldo")
def config_dialog():
    s = st.number_input("Monto de Sueldo Base ($)", value=sueldo_base, step=10.0)
    f = st.date_input("Fecha de pago")
    if st.button("Guardar", use_container_width=True):
        db["settings"]["sueldo"] = s
        db["settings"]["fecha"] = f.strftime("%d/%m/%Y")
        save_db(db)
        st.rerun()

@st.dialog("🟢 Registrar Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.01)
    note = st.text_input("Nota")
    if st.button("Añadir", use_container_width=True):
        add_trans("Ingreso", "Ingreso Extra", amt, note)
        st.rerun()

@st.dialog("🔴 Registrar Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Salud", "Ocio", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.01)
    note = st.text_input("Nota")
    if st.button("Registrar", use_container_width=True):
        add_trans("Gasto", cat, amt, note)
        st.rerun()

# --- INTERFAZ ---
tab_inicio, tab_historial, tab_graficos = st.tabs(["🏠 Inicio", "📝 Historial", "📊 Gráficos"])

with tab_inicio:
    st.write("")
    if st.button(f"⚙️ Sueldo: ${sueldo_base:,.2f}\n📅 Pago: {fecha_pago}", type="tertiary", use_container_width=True):
        config_dialog()
    
    st.write("")
    col_ing, col_gas = st.columns(2, gap="small")
    with col_ing:
        if st.button(f"↓ INGRESOS\n${ingresos_extras:,.2f}", type="secondary", use_container_width=True):
            ingreso_dialog()
    with col_gas:
        if st.button(f"↑ GASTOS\n${gastos_totales:,.2f}", type="primary", use_container_width=True):
            gasto_dialog()
            
    st.markdown(f"""
    <div class="total-card">
        <div class="total-label">Saldo Total Disponible</div>
        <div class="total-value">${saldo_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty and len(db["transactions"]) > 0:
        st.write("**Últimos movimientos**")
        for idx, row in df.iloc[::-1].head(3).iterrows():
            simbolo = "+" if row['type'] == 'Ingreso' else "-"
            color = "green" if row['type'] == 'Ingreso' else "red"
            st.markdown(f"**{row['category']}**: <span style='color:{color}'>{simbolo}${row['amount']}</span> <small>({row['note']})</small>", unsafe_allow_html=True)

with tab_historial:
    st.subheader("Historial Completo")
    if not df.empty and len(db["transactions"]) > 0:
        df_show = df[['date', 'type', 'category', 'amount', 'note']].copy()
        st.dataframe(df_show.iloc[::-1], use_container_width=True, hide_index=True)
        st.write("---")
        id_borrar = st.selectbox("Borrar registro (ID):", df['id'].tolist())
        if st.button("Confirmar Eliminación"):
            delete_trans(id_borrar)
            st.rerun()
    else:
        st.info("No hay datos registrados aún.")

with tab_graficos:
    st.subheader("Análisis de Gastos")
    df_gastos = df[df['type'] == 'Gasto']
    if not df_gastos.empty:
        fig_pie = px.pie(df_gastos, values='amount', names='category', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        df_diario = df_gastos.groupby('date')['amount'].sum().reset_index()
        fig_bar = px.bar(df_diario, x='date', y='amount', color_discrete_sequence=['#F44336'])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Registra algunos gastos para ver las gráficas.")
