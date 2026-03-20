import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES ADAPTADOS (NUEVA UI MÓVIL) ---
st.markdown("""
<style>
    /* Ocultar elementos estándar de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* CSS para replicar la UI móvil de la imagen */
    
    /* Tarjeta superior (Estilo tarjeta de crédito) - Ahora es un botón */
    .stButton > button.salary-card {
        background: linear-gradient(135deg, #0d1e3a, #162f58); /* Azul oscuro degradado */
        color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 180px; /* Altura de tarjeta de crédito */
        border: none;
        text-align: left;
    }
    .salary-card .icon-row { display: flex; justify-content: space-between; align-items: center; width: 100%; }
    .salary-card .wallet-icon { font-size: 24px; }
    .salary-card .arrow-icon { font-size: 14px; }
    .salary-card .salary-title { font-size: 14px; color: #a5b4c7; }
    .salary-card .salary-value { font-size: 32px; font-weight: bold; }
    
    /* Mosaico de resumen (Ingresos/Gastos) */
    .summary-mosaic {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    /* Botones de resumen personalizados */
    .stButton > button.summary-btn {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 140px;
        border: 1px solid #f0f0f0;
        text-align: left;
    }
    .summary-btn .icon { font-size: 20px; margin-bottom: 10px; }
    .summary-btn .green-arrow { color: #4CAF50; }
    .summary-btn .red-arrow { color: #F44336; }
    .summary-btn .title { font-size: 14px; color: #666; margin-bottom: 5px; }
    .summary-btn .value { font-size: 24px; font-weight: bold; }
    .summary-btn .subtext { font-size: 12px; color: #999; }
    
    /* Tarjeta de saldo (Tarjeta azul) */
    .balance-card {
        background-color: #007bff; /* Azul sólido */
        color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .balance-card .title { font-size: 14px; color: #a0c4ff; margin-bottom: 10px; }
    .balance-card .value { font-size: 32px; font-weight: bold; }
    
    /* Sección de transacciones recientes */
    .stMarkdown .transaction-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; margin-top: 20px; }
    .transaction-list-item {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #f0f0f0;
    }
    .transaction-list-item .icon { font-size: 24px; margin-right: 15px; color: #F44336; } /* Por defecto, flecha roja */
    .transaction-list-item .green-arrow { color: #4CAF50; }
    .transaction-list-item .details { flex-grow: 1; }
    .transaction-list-item .details .name { font-size: 16px; font-weight: bold; margin-bottom: 2px; }
    .transaction-list-item .details .subtext { font-size: 12px; color: #999; }
    .transaction-list-item .value { font-size: 16px; font-weight: bold; text-align: right; }
    .transaction-list-item .value .negative { color: #F44336; }
    .transaction-list-item .date { font-size: 12px; color: #ccc; margin-top: 2px; }
    
    /* Botones de acción inferiores (Ingresos/Gastos) */
    .bottom-actions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-top: 30px;
    }
    /* Botones de acción grandes personalizados */
    .stButton > button.bottom-action-btn {
        border-radius: 10px;
        padding: 15px 25px;
        font-size: 16px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 60px;
    }
    .stButton > button.green-btn {
        background-color: #28a745; /* Verde sólido */
        color: white;
        border: none;
    }
    .stButton > button.red-btn {
        background-color: #dc3545; /* Rojo sólido */
        color: white;
        border: none;
    }
    .bottom-action-btn .icon { font-size: 18px; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A JSONBIN (Backend) ---
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

# --- LÓGICA CORE ---
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
columnas = ["id", "date", "type", "category", "amount", "note"]
df = pd.DataFrame(db["transactions"], columns=columnas)

# Aseguramos que la columna amount sea numérica
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

# Datos de configuración
sueldo_base = float(db["settings"].get("sueldo", 0))
fecha_pago = db["settings"].get("fecha", "No definida")

# Cálculos acumulados (originales)
ingresos_extras = df[df['type'] == 'Ingreso']['amount'].sum()
gastos_totales = df[df['type'] == 'Gasto']['amount'].sum()
saldo_acumulado = sueldo_base + ingresos_extras - gastos_totales

# Cálculos del mes actual (para visualización "Este Mes")
mes_actual = datetime.now().month
año_actual = datetime.now().year
df_mes = df[(df['date'].str.split('-').str[1].fillna('0').astype(int) == mes_actual) & (df['date'].str.split('-').str[0].fillna('0').astype(int) == año_actual)]
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()

# --- DIALOGS (Diálogos de Entrada) ---
@st.dialog("⚙️ Configurar Salario Base")
def config_dialog():
    s = st.number_input("Monto de Salario Base ($)", value=sueldo_base, step=100.0)
    f = st.date_input("Próxima fecha de pago", value=datetime.strptime(fecha_pago, "%d/%m/%Y") if fecha_pago != "No definida" else datetime.now())
    st.write("---")
    if st.button("Guardar Cambios", use_container_width=True):
        db["settings"]["sueldo"] = s
        db["settings"]["fecha"] = f.strftime("%d/%m/%Y")
        save_db(db)
        st.rerun()

@st.dialog("🟢 Añadir Ingreso Extra")
def ingreso_dialog():
    st.markdown("Replicando diseño de imagen")
    amt = st.number_input("Monto ($)", min_value=0.01)
    note = st.text_input("Nota / Concepto")
    if st.button("Añadir", use_container_width=True):
        if amt > 0:
            add_trans("Ingreso", "Ingreso Extra", amt, note)
            st.rerun()

@st.dialog("🔴 Registrar Gasto")
def gasto_dialog():
    st.markdown("Replicando diseño de imagen")
    cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Salud", "Ocio", "Otros"])
    amt = st.number_input("Monto ($)", min_value=0.01)
    note = st.text_input("Nota / Concepto")
    if st.button("Registrar", use_container_width=True):
        if amt > 0:
            add_trans("Gasto", cat, amt, note)
            st.rerun()

# --- INTERFAZ PRINCIPAL (tabs nativas) ---
tab_inicio, tab_historial, tab_graficos = st.tabs(["🏠 Inicio", "📝 Historial", "📊 Gráficos"])

with tab_inicio:
    # 1. Tarjeta superior (Salario) - Ahora es un botón interactivo
    st.markdown("<div>", unsafe_allow_html=True)
    if st.button(label="", key="salary_btn_full", help="Toca para configurar salario base"):
        st.markdown(f"""
            <div class="salary-card">
                <div class="icon-row">
                    <div class="wallet-icon">💳</div>
                    <div class="arrow-icon">▼</div>
                </div>
                <div class="salary-title">Salario Base</div>
                <div class="salary-value">${sueldo_base:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        config_dialog()
    else:
        st.markdown(f"""
            <div class="salary-card">
                <div class="icon-row">
                    <div class="wallet-icon">💳</div>
                    <div class="arrow-icon">▼</div>
                </div>
                <div class="salary-title">Salario Base</div>
                <div class="salary-value">${sueldo_base:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Mosaico de resumen (Ingresos/Gastos este mes) - Son botones interactivos
    st.markdown('<div class="summary-mosaic">', unsafe_allow_html=True)
    
    # Botón Ingresos Extra
    if st.button(label="", key="income_mosaic_btn", help="Toca para añadir ingresos extra"):
        st.markdown(f"""
            <div class="summary-btn">
                <div class="icon green-arrow">↓</div>
                <div>
                    <div class="title">Ingresos Extra</div>
                    <div class="value">${ingresos_mes:,.2f}</div>
                    <div class="subtext">Este Mes</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        ingreso_dialog()
    else:
        st.markdown(f"""
            <div class="summary-btn">
                <div class="icon green-arrow">↓</div>
                <div>
                    <div class="title">Ingresos Extra</div>
                    <div class="value">${ingresos_mes:,.2f}</div>
                    <div class="subtext">Este Mes</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Botón Gastos
    if st.button(label="", key="expense_mosaic_btn", help="Toca para registrar gastos"):
        st.markdown(f"""
            <div class="summary-btn">
                <div class="icon red-arrow">↑</div>
                <div>
                    <div class="title">Gastos</div>
                    <div class="value">${gastos_mes:,.2f}</div>
                    <div class="subtext">Este Mes</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        gasto_dialog()
    else:
        st.markdown(f"""
            <div class="summary-btn">
                <div class="icon red-arrow">↑</div>
                <div>
                    <div class="title">Gastos</div>
                    <div class="value">${gastos_mes:,.2f}</div>
                    <div class="subtext">Este Mes</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Tarjeta de saldo (Tarjeta azul) - Es una visualización, no un botón
    st.markdown(f"""
        <div class="balance-card">
            <div class="title">Saldo Actual (Acumulado)</div>
            <div class="value">${saldo_acumulado:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # 4. Sección de transacciones recientes
    st.markdown('<p class="transaction-title">Transacciones Recientes</p>', unsafe_allow_html=True)
    # Lista de transacciones recientes formateada como en la imagen
    if not df.empty and len(db["transactions"]) > 0:
        for idx, row in df.iloc[::-1].head(3).iterrows():
            simbolo_monto = "+" if row['type'] == 'Ingreso' else "-"
            clase_monto = "" if row['type'] == 'Ingreso' else "negative"
            emoji_flecha = "↓" if row['type'] == 'Ingreso' else "↑"
            clase_flecha = "green-arrow" if row['type'] == 'Ingreso' else ""
            
            # Formateo de fecha (asumimos formato YYYY-MM-DD para simplificar)
            try:
                fecha_formateada = datetime.strptime(row['date'], "%Y-%m-%d").strftime("%d %b %Y")
            except:
                fecha_formateada = row['date']

            st.markdown(f"""
                <div class="transaction-list-item">
                    <div class="icon {clase_flecha}">{emoji_flecha}</div>
                    <div class="details">
                        <div class="name">{row['category']}</div>
                        <div class="subtext">{row['note'] or 'Sin nota'}</div>
                    </div>
                    <div class="value">
                        <div class="{clase_monto}">{simbolo_monto}${row['amount']:,.2f}</div>
                        <div class="date">{fecha_formateada}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay datos registrados aún.")

    # 5. Botones de acción inferiores (Ingresos/Gastos) - Replicando el diseño inferior
    st.markdown('<div class="bottom-actions">', unsafe_allow_html=True)
    if st.button("↓ Ingresos", key="bottom_income_btn", help="Toca para añadir ingresos extra"):
        st.markdown('<button class="bottom-action-btn green-btn"><span class="icon">↓</span>Ingresos</button>', unsafe_allow_html=True)
        ingreso_dialog()
    else:
        st.markdown('<button class="bottom-action-btn green-btn"><span class="icon">↓</span>Ingresos</button>', unsafe_allow_html=True)
        
    if st.button("↑ Gastos", key="bottom_expense_btn", help="Toca para registrar gastos"):
        st.markdown('<button class="bottom-action-btn red-btn"><span class="icon">↑</span>Gastos</button>', unsafe_allow_html=True)
        gasto_dialog()
    else:
        st.markdown('<button class="bottom-action-btn red-btn"><span class="icon">↑</span>Gastos</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


with tab_historial:
    st.subheader("Historial Completo")
    if not df.empty and len(db["transactions"]) > 0:
        # Replicamos el formateo de fecha para la tabla de historial
        df_show = df[['date', 'type', 'category', 'amount', 'note']].copy()
        # Intentamos formatear la fecha para que se vea mejor
        try:
            df_show['date'] = pd.to_datetime(df_show['date'], format="%Y-%m-%d").dt.strftime("%d %b %Y")
        except:
            pass
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
        # Intentamos formatear la fecha para que se vea mejor en el gráfico de barras
        try:
            df_diario['date'] = pd.to_datetime(df_diario['date'], format="%Y-%m-%d").dt.strftime("%d %b %Y")
        except:
            pass
        fig_bar = px.bar(df_diario, x='date', y='amount', color_discrete_sequence=['#dc3545'])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Registra algunos gastos para ver las gráficas.")

