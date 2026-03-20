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

# --- CONEXIÓN Y DATOS (CON AUTOCURACIÓN) ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
except:
    st.error("⚠️ Configura 'bin_id' y 'api_key' en los Secrets de Streamlit.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

@st.cache_data(ttl=600)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        
        # Estructura base por defecto
        default_settings = {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"], "fecha": "No definida"}
        
        # Validar y reparar estructura
        if "transactions" not in data: data["transactions"] = []
        if "recurrentes" not in data: data["recurrentes"] = []
        
        if "settings" not in data:
            data["settings"] = default_settings
        else:
            # Si 'settings' existe, aseguramos que tenga todas las llaves nuevas (evita el KeyError)
            for k, v in default_settings.items():
                if k not in data["settings"]:
                    data["settings"][k] = v
        
        return data
    except Exception as e:
        st.warning(f"Error de conexión: {e}")
        return {"transactions": [], "settings": {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}, "recurrentes": []}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA CORE ---
def add_trans(t_type, cat, amt, note, account, date_str=None):
    t_id = str(uuid.uuid4())[:8]
    nueva = {
        "id": t_id, 
        "date": date_str if date_str else datetime.now().strftime("%Y-%m-%d"), 
        "type": t_type, 
        "category": cat, 
        "amount": float(amt), 
        "note": note,
        "account": account
    }
    db["transactions"].append(nueva)
    save_db(db)

# --- PROCESAMIENTO DE DATOS ---
df = pd.DataFrame(db["transactions"])
columnas_necesarias = ["id", "date", "type", "category", "amount", "note", "account"]

if df.empty:
    df = pd.DataFrame(columns=columnas_necesarias)
else:
    # Asegurar que todas las columnas existan en el DF
    for col in columnas_necesarias:
        if col not in df.columns: df[col] = "N/A"
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

# Filtros Temporales Sidebar
st.sidebar.header("🗓️ Período")
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_actual = datetime.now().month
año_actual = datetime.now().year
sel_mes = st.sidebar.selectbox("Mes", range(1, 13), index=mes_actual-1, format_func=lambda x: meses_nombres[x-1])
sel_año = st.sidebar.number_input("Año", 2024, 2030, año_actual)

df_mes = df[(df['date'].dt.month == sel_mes) & (df['date'].dt.year == sel_año)]
prev_date = datetime(sel_año, sel_mes, 1) - timedelta(days=1)
df_prev = df[(df['date'].dt.month == prev_date.month) & (df['date'].dt.year == prev_date.year)]

# --- DIALOGS ---
@st.dialog("⚙️ Ajustes y Recurrentes")
def config_dialog():
    st.subheader("Configuración General")
    s = st.number_input("Sueldo Base ($)", value=float(db["settings"].get("sueldo", 0)))
    p = st.number_input("Presupuesto de Gastos ($)", value=float(db["settings"].get("presupuesto", 0)))
    
    st.divider()
    st.subheader("🔄 Gastos Recurrentes")
    r_cat = st.selectbox("Categoría", ["Servicios", "Suscripciones", "Vivienda", "Ocio", "Otros"])
    r_amt = st.number_input("Monto Fijo ($)", min_value=0.0)
    r_note = st.text_input("Nombre (ej. Netflix, Renta)")
    r_acc = st.selectbox("Cuenta de cargo", db["settings"].get("cuentas", ["Banco"]))
    
    if st.button("Añadir Suscripción"):
        db["recurrentes"].append({"category": r_cat, "amount": r_amt, "note": r_note, "account": r_acc})
        save_db(db)
        st.success(f"Añadido {r_note}")
        st.rerun()

    if db.get("recurrentes"):
        with st.expander("Ver suscripciones activas"):
            for i, r in enumerate(db["recurrentes"]):
                col_r1, col_r2 = st.columns([0.8, 0.2])
                col_r1.write(f"**{r['note']}**: ${r['amount']} ({r['account']})")
                if col_r2.button("🗑️", key=f"del_rec_{i}"):
                    db["recurrentes"].pop(i)
                    save_db(db)
                    st.rerun()

    if st.button("Guardar Cambios", use_container_width=True, type="primary"):
        db["settings"]["sueldo"] = s
        db["settings"]["presupuesto"] = p
        save_db(db)
        st.rerun()

@st.dialog("➕ Registrar Movimiento")
def trans_dialog(tipo):
    acc = st.selectbox("Cuenta", db["settings"].get("cuentas", ["Banco", "Efectivo"]))
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Ocio", "Salud", "Educación", "Otros"]) if tipo == "Gasto" else "Ingreso Extra"
    amt = st.number_input("Monto ($)", min_value=0.01, step=1.0)
    note = st.text_input("Nota / Concepto")
    date = st.date_input("Fecha", datetime.now())
    if st.button(f"Registrar {tipo}", use_container_width=True):
        add_trans(tipo, cat, amt, note, acc, date.strftime("%Y-%m-%d"))
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
tab_dash, tab_hist, tab_analisis = st.tabs(["🏠 Dashboard", "📝 Historial", "📊 Reportes"])

with tab_dash:
    # 1. Métricas Comparativas
    g_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
    g_prev = df_prev[df_prev['type'] == 'Gasto']['amount'].sum()
    dif_gasto = g_mes - g_prev
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Gasto este Mes", f"${g_mes:,.2f}", f"{dif_gasto:+,.2f} vs mes ant", delta_color="inverse")
    with col_m2:
        presupuesto = db["settings"].get("presupuesto", 0)
        restante = presupuesto - g_mes
        st.metric("Presupuesto Restante", f"${restante:,.2f}", f"Meta: ${presupuesto:,.0f}")

    # 2. Saldos por Cuenta
    st.write("### 🏦 Mis Cuentas")
    cuentas_activas = db["settings"].get("cuentas", ["Efectivo", "Banco"])
    cols_acc = st.columns(len(cuentas_activas))
    
    for i, acc in enumerate(cuentas_activas):
        ing_acc = df[ (df['type']=='Ingreso') & (df['account']==acc) ]['amount'].sum()
        gas_acc = df[ (df['type']=='Gasto') & (df['account']==acc) ]['amount'].sum()
        # El sueldo se suma a la cuenta "Banco" por defecto
        balance = (float(db["settings"].get("sueldo", 0)) if acc == "Banco" else 0) + ing_acc - gas_acc
        cols_acc[i].metric(acc, f"${balance:,.2f}")

    # 3. Acciones rápidas
    st.write("---")
    col_b1, col_b2, col_b3 = st.columns(3)
    if col_b1.button("🔴 Registrar Gasto", use_container_width=True): trans_dialog("Gasto")
    if col_b2.button("🟢 Registrar Ingreso", use_container_width=True): trans_dialog("Ingreso")
    if col_b3.button("⚙️ Ajustes / Metas", use_container_width=True): config_dialog()

    # 4. Botón de Recurrentes
    if db.get("recurrentes"):
        if st.button("🔄 Aplicar Suscripciones del Mes", use_container_width=True):
            for r in db["recurrentes"]:
                add_trans("Gasto", r["category"], r["amount"], f"AUTO: {r['note']}", r["account"])
            st.success("¡Suscripciones aplicadas!")
            st.rerun()

with tab_hist:
    st.subheader("Carga Masiva")
    uploaded_file = st.file_uploader("Sube CSV (date, type, category, amount, note, account)", type="csv")
    if uploaded_file:
        try:
            new_data = pd.read_csv(uploaded_file)
            if st.button("Confirmar Importación"):
                for _, row in new_data.iterrows():
                    add_trans(row['type'], row['category'], row['amount'], row['note'], row['account'], str(row['date']))
                st.success("Importado con éxito")
                st.rerun()
        except:
            st.error("Formato de CSV no válido.")

    st.divider()
    st.subheader(f"Movimientos de {meses_nombres[sel_mes-1]}")
    if not df_mes.empty:
        st.dataframe(df_mes.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos este mes.")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Backup Completo (CSV)", data=csv, file_name="mis_finanzas_backup.csv")

with tab_analisis:
    st.subheader(f"Análisis {meses_nombres[sel_mes-1]} {sel_año}")
    df_gastos_f = df_mes[df_mes['type']=='Gasto']
    
    if not df_gastos_f.empty:
        # Gráfico Sunburst (Cuenta -> Categoría)
        fig = px.sunburst(df_gastos_f, path=['account', 'category'], values='amount', 
                          title="Gastos: ¿De dónde y en qué?", color='account',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparativa Diaria
        df_diario = df_gastos_f.groupby(df_gastos_f['date'].dt.day)['amount'].sum().reset_index()
        fig_bar = px.bar(df_diario, x='date', y='amount', title="Gasto Diario", labels={'date':'Día', 'amount':'Monto'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sin datos para graficar en este período.")
