import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import uuid
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
    header {visibility: hidden;}
    .total-card { background: linear-gradient(135deg, #007bff, #0056b3); color: white; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 8px 15px rgba(0, 123, 255, 0.2); margin: 15px 0; }
    .total-value { font-size: 40px; font-weight: bold; margin: 0; }
    button[kind="tertiary"] { background-color: #f8f9fa !important; border: 2px dashed #007bff !important; border-radius: 15px !important; padding: 15px !important; }
    button[kind="secondary"] { background-color: #e8f5e9 !important; border: 2px solid #4CAF50 !important; border-radius: 15px !important; color: #2e7d32 !important; font-weight: bold !important; }
    button[kind="primary"] { background-color: #ffebee !important; border: 2px solid #F44336 !important; border-radius: 15px !important; color: #c62828 !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A JSONBIN CON CACHING ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
except:
    st.error("⚠️ Configura 'bin_id' y 'api_key' en los Secrets de Streamlit Cloud.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

@st.cache_data(ttl=600) # Cache por 10 min o hasta que se guarde algo
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "transactions" not in data: data["transactions"] = []
        if "settings" not in data: data["settings"] = {"sueldo": 0.0, "fecha": "No definida", "presupuesto": 0.0}
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0, "fecha": "No definida", "presupuesto": 0.0}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear() # Limpiamos cache para forzar recarga de datos nuevos

db = get_db()

# --- LÓGICA DE TRANSACCIONES ---
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

# --- PROCESAMIENTO DE DATOS ---
df = pd.DataFrame(db["transactions"], columns=["id", "date", "type", "category", "amount", "note"])
df['date'] = pd.to_datetime(df['date'])
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

# Sidebar para Filtros Temporales
st.sidebar.header("🔍 Filtros")
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_actual = datetime.now().month
año_actual = datetime.now().year

sel_mes = st.sidebar.selectbox("Mes", range(1, 13), index=mes_actual-1, format_func=lambda x: meses[x-1])
sel_año = st.sidebar.number_input("Año", min_value=2024, max_value=2030, value=año_actual)

# Filtrado de DataFrame
df_filtrado = df[(df['date'].dt.month == sel_mes) & (df['date'].dt.year == sel_año)]

# Cálculos basados en el filtro
sueldo_base = float(db["settings"].get("sueldo", 0))
presupuesto_limite = float(db["settings"].get("presupuesto", 0))
ingresos_extras = df_filtrado[df_filtrado['type'] == 'Ingreso']['amount'].sum()
gastos_totales = df_filtrado[df_filtrado['type'] == 'Gasto']['amount'].sum()
saldo_mensual = sueldo_base + ingresos_extras - gastos_totales

# --- DIALOGS (Validación añadida) ---
@st.dialog("⚙️ Configuración")
def config_dialog():
    s = st.number_input("Sueldo Base ($)", value=sueldo_base, min_value=0.0, step=50.0)
    p = st.number_input("Meta de Gasto Mensual ($)", value=presupuesto_limite, min_value=0.0, help="Límite visual para tus gastos")
    f = st.date_input("Fecha de pago próxima")
    if st.button("Guardar Cambios", use_container_width=True):
        db["settings"].update({"sueldo": s, "presupuesto": p, "fecha": f.strftime("%d/%m/%Y")})
        save_db(db)
        st.rerun()

@st.dialog("🟢 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto ($)", min_value=0.01, step=1.0, format="%.2f")
    note = st.text_input("Concepto", placeholder="Ej. Bono, Venta...")
    if st.button("Añadir Ingreso", use_container_width=True):
        add_trans("Ingreso", "Ingreso Extra", amt, note)
        st.rerun()

@st.dialog("🔴 Nuevo Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Salud", "Ocio", "Suscripciones", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.01, step=1.0, format="%.2f")
    note = st.text_input("Nota (opcional)")
    if st.button("Registrar Gasto", use_container_width=True):
        add_trans("Gasto", cat, amt, note)
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
tab_inicio, tab_historial, tab_graficos = st.tabs(["🏠 Dashboard", "📝 Movimientos", "📊 Análisis"])

with tab_inicio:
    # Header Info
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        if st.button(f"⚙️ Sueldo: ${sueldo_base:,.2f}", use_container_width=True): config_dialog()
    with col_info2:
        st.info(f"📅 Pago: {db['settings'].get('fecha')}")

    # Acciones rápidas
    col_ing, col_gas = st.columns(2)
    with col_ing:
        if st.button(f"↓ INGRESOS\n${ingresos_extras:,.2f}", type="secondary", use_container_width=True): ingreso_dialog()
    with col_gas:
        if st.button(f"↑ GASTOS\n${gastos_totales:,.2f}", type="primary", use_container_width=True): gasto_dialog()

    # Card Principal
    st.markdown(f"""<div class="total-card"><div style="opacity:0.8">Saldo Estimado {meses[sel_mes-1]}</div>
    <div class="total-value">${saldo_mensual:,.2f}</div></div>""", unsafe_allow_html=True)

    # Barra de Presupuesto
    if presupuesto_limite > 0:
        progreso = min(gastos_totales / presupuesto_limite, 1.0)
        st.write(f"**Presupuesto Gastado:** {progreso*100:.1f}% de ${presupuesto_limite:,.0f}")
        color_bar = "red" if progreso >= 0.9 else "orange" if progreso >= 0.7 else "green"
        st.progress(progreso)

    # Últimos 5 movimientos (del mes filtrado)
    st.write("---")
    st.subheader("Movimientos Recientes")
    if not df_filtrado.empty:
        for _, row in df_filtrado.sort_values('date', ascending=False).head(5).iterrows():
            c1, c2 = st.columns([0.7, 0.3])
            color = "#2e7d32" if row['type'] == 'Ingreso' else "#c62828"
            simbolo = "+" if row['type'] == 'Ingreso' else "-"
            c1.markdown(f"**{row['category']}** \n<small>{row['note']}</small>", unsafe_allow_html=True)
            c2.markdown(f"<div style='text-align:right; color:{color}; font-weight:bold'>{simbolo}${row['amount']}</div>", unsafe_allow_html=True)
    else:
        st.info("Sin movimientos en este período.")

with tab_historial:
    st.subheader("Historial de Transacciones")
    if not df.empty:
        # Buscador simple
        search = st.text_input("🔍 Buscar en notas o categorías")
        df_display = df.copy()
        if search:
            df_display = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        st.dataframe(df_display.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
        
        # Exportación
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar todo (CSV)", data=csv, file_name=f"backup_cashbook_{año_actual}.csv", mime="text/csv")

        # Zona de Borrado Optimizada
        with st.expander("🗑️ Gestionar / Borrar Registros"):
            opciones = df.sort_values('date', ascending=False).apply(
                lambda x: f"{x['id']} | {x['date'].strftime('%d/%m')} | {x['category']} (${x['amount']})", axis=1
            ).tolist()
            seleccion = st.selectbox("Selecciona un registro para eliminar:", opciones)
            if st.button("Confirmar Eliminación", type="primary", use_container_width=True):
                id_a_borrar = seleccion.split(" | ")[0]
                delete_trans(id_a_borrar)
                st.success("Eliminado correctamente")
                st.rerun()
    else:
        st.info("No hay datos registrados.")

with tab_graficos:
    st.subheader(f"Análisis de {meses[sel_mes-1]} {sel_año}")
    df_gastos_f = df_filtrado[df_filtrado['type'] == 'Gasto']
    
    if not df_gastos_f.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_pie = px.pie(df_gastos_f, values='amount', names='category', title="Distribución por Categoría", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_g2:
            df_diario = df_gastos_f.groupby(df_gastos_f['date'].dt.day)['amount'].sum().reset_index()
            fig_bar = px.bar(df_diario, x='date', y='amount', title="Gastos por Día", labels={'date':'Día del Mes', 'amount':'Monto ($)'})
            fig_bar.update_traces(marker_color='#F44336')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay gastos registrados en este mes para generar gráficos.")