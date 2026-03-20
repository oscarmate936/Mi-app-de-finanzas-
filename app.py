import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import requests
import uuid
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro 2.0", page_icon="🏦", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
    header {visibility: hidden;}
    .total-card { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 8px 15px rgba(0,0,0,0.1); margin: 10px 0; }
    .total-value { font-size: 35px; font-weight: bold; }
    .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN Y DATOS ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
except:
    st.error("⚠️ Configura 'bin_id' y 'api_key' en Secrets.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

@st.cache_data(ttl=600)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        # Inicialización de nuevas estructuras si no existen
        if "transactions" not in data: data["transactions"] = []
        if "settings" not in data: data["settings"] = {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}
        if "recurrentes" not in data: data["recurrentes"] = []
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "cuentas": ["Efectivo", "Banco"]}, "recurrentes": []}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA CORE ---
def add_trans(t_type, cat, amt, note, account, date=None):
    t_id = str(uuid.uuid4())[:8]
    nueva = {
        "id": t_id, 
        "date": date if date else datetime.now().strftime("%Y-%m-%d"), 
        "type": t_type, 
        "category": cat, 
        "amount": float(amt), 
        "note": note,
        "account": account
    }
    db["transactions"].append(nueva)
    save_db(db)

# --- PROCESAMIENTO ---
df = pd.DataFrame(db["transactions"])
if df.empty:
    df = pd.DataFrame(columns=["id", "date", "type", "category", "amount", "note", "account"])
else:
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])

# Filtros Temporales Sidebar
st.sidebar.header("🗓️ Período")
mes_actual = datetime.now().month
año_actual = datetime.now().year
sel_mes = st.sidebar.selectbox("Mes", range(1, 13), index=mes_actual-1)
sel_año = st.sidebar.number_input("Año", 2024, 2030, año_actual)

df_mes = df[(df['date'].dt.month == sel_mes) & (df['date'].dt.year == sel_año)]
# Datos mes anterior para comparativa MoM
prev_date = datetime(sel_año, sel_mes, 1) - timedelta(days=1)
df_prev = df[(df['date'].dt.month == prev_date.month) & (df['date'].dt.year == prev_date.year)]

# --- DIALOGS ---
@st.dialog("⚙️ Ajustes y Recurrentes")
def config_dialog():
    st.subheader("Configuración General")
    s = st.number_input("Sueldo Base ($)", value=float(db["settings"].get("sueldo", 0)))
    p = st.number_input("Presupuesto Gastos ($)", value=float(db["settings"].get("presupuesto", 0)))
    
    st.divider()
    st.subheader("🔄 Gastos Recurrentes (Suscripciones)")
    r_cat = st.selectbox("Categoría", ["Servicios", "Suscripciones", "Vivienda", "Otros"])
    r_amt = st.number_input("Monto Recurrente ($)", min_value=0.0)
    r_note = st.text_input("Nombre (ej. Netflix, Renta)")
    r_acc = st.selectbox("Cuenta de cargo", db["settings"]["cuentas"])
    
    if st.button("Añadir Recurrente"):
        db["recurrentes"].append({"category": r_cat, "amount": r_amt, "note": r_note, "account": r_acc})
        save_db(db)
        st.success("Añadido")

    if db["recurrentes"]:
        with st.expander("Ver suscripciones activas"):
            for i, r in enumerate(db["recurrentes"]):
                st.write(f"- {r['note']}: ${r['amount']} ({r['account']})")
                if st.button(f"Eliminar {i}", key=f"del_{i}"):
                    db["recurrentes"].pop(i)
                    save_db(db)
                    st.rerun()

    if st.button("Guardar Todo", use_container_width=True, type="primary"):
        db["settings"]["sueldo"] = s
        db["settings"]["presupuesto"] = p
        save_db(db)
        st.rerun()

@st.dialog("➕ Registrar Movimiento")
def trans_dialog(tipo):
    acc = st.selectbox("Cuenta", db["settings"]["cuentas"])
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Ocio", "Salud", "Sueldo", "Venta", "Otros"]) if tipo == "Gasto" else "Ingreso Extra"
    amt = st.number_input("Monto ($)", min_value=0.01)
    note = st.text_input("Nota")
    date = st.date_input("Fecha", datetime.now())
    if st.button("Guardar", use_container_width=True):
        add_trans(tipo, cat, amt, note, acc, date.strftime("%Y-%m-%d"))
        st.rerun()

# --- INTERFAZ ---
tab_dash, tab_hist, tab_analisis = st.tabs(["🏠 Inicio", "📝 Historial", "📊 Reportes"])

with tab_dash:
    # Métricas Comparativas
    g_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
    g_prev = df_prev[df_prev['type'] == 'Gasto']['amount'].sum()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Gastos Mes", f"${g_mes:,.2f}", f"{g_mes - g_prev:+,.2f} vs mes ant", delta_color="inverse")
    
    # Saldos por Cuenta
    st.write("### 🏦 Mis Cuentas")
    cols_acc = st.columns(len(db["settings"]["cuentas"]))
    for i, acc in enumerate(db["settings"]["cuentas"]):
        ing_acc = df[ (df['type']=='Ingreso') & (df['account']==acc) ]['amount'].sum()
        gas_acc = df[ (df['type']=='Gasto') & (df['account']==acc) ]['amount'].sum()
        # Sumamos sueldo solo si es "Banco" (puedes personalizar esto)
        balance = (float(db["settings"]["sueldo"]) if acc == "Banco" else 0) + ing_acc - gas_acc
        cols_acc[i].metric(acc, f"${balance:,.2f}")

    # Acciones
    col_b1, col_b2, col_b3 = st.columns(3)
    if col_b1.button("🔴 Gasto", use_container_width=True): trans_dialog("Gasto")
    if col_b2.button("🟢 Ingreso", use_container_width=True): trans_dialog("Ingreso")
    if col_b3.button("⚙️ Ajustes", use_container_width=True): config_dialog()

    # Botón Mágico: Gastos Recurrentes
    if db["recurrentes"]:
        if st.button("🔄 Aplicar Suscripciones del Mes", use_container_width=True, type="secondary"):
            for r in db["recurrentes"]:
                add_trans("Gasto", r["category"], r["amount"], f"RECURRENTE: {r['note']}", r["account"])
            st.success("¡Suscripciones aplicadas!")
            st.rerun()

with tab_hist:
    st.subheader("Importar desde CSV")
    uploaded_file = st.file_uploader("Sube tu archivo (Columnas: date, type, category, amount, note, account)", type="csv")
    if uploaded_file:
        new_data = pd.read_csv(uploaded_file)
        if st.button("Confirmar Importación Masiva"):
            for _, row in new_data.iterrows():
                add_trans(row['type'], row['category'], row['amount'], row['note'], row['account'], row['date'])
            st.success("Importación completada")
            st.rerun()

    st.divider()
    st.subheader("Movimientos")
    st.dataframe(df_mes.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exportar Todo a CSV", data=csv, file_name="finanzas.csv")

with tab_analisis:
    st.subheader("Análisis de Gastos")
    if not df_mes.empty:
        fig = px.sunburst(df_mes[df_mes['type']=='Gasto'], path=['account', 'category'], values='amount', title="Gastos por Cuenta y Categoría")
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparativa Ingresos vs Gastos
        resumen = df_mes.groupby('type')['amount'].sum().reset_index()
        fig_bar = px.bar(resumen, x='type', y='amount', color='type', color_discrete_map={'Gasto':'#ef5350','Ingreso':'#66bb6a'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay datos este mes.")
