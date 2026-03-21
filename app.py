import streamlit as st  # <-- Corregido: "import" en minúsculas
import pandas as pd
from datetime import datetime
import requests 

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CashBook", page_icon="💳", layout="centered")

# --- CONFIGURACIÓN JSONBIN ---
JSONBIN_KEY = "$2a$10$uGJHNDV9ckIhDrIMXIRzHOmemF1tr9LFHNstzIjMtjMUP7AxKbAJS"
JSONBIN_BIN_ID = "69bd5fa2aa77b81da901cfe3"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
JSONBIN_HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def guardar_en_jsonbin():
    """Guarda el estado actual en la nube silenciosamente."""
    df_save = st.session_state.transacciones.copy()
    if not df_save.empty:
        # Convertimos fechas a texto para que JSON lo entienda
        df_save['Fecha'] = df_save['Fecha'].astype(str) 

    data = {
        "pago_fijo": float(st.session_state.pago_fijo),
        "fecha_pago": str(st.session_state.fecha_pago),
        "counter": int(st.session_state.counter),
        "transacciones": df_save.to_dict(orient="records")
    }
    try:
        requests.put(JSONBIN_URL, json=data, headers=JSONBIN_HEADERS)
    except:
        pass 

# --- CSS AVANZADO ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .flex-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 15px;
    }
    .card-pago-fijo {
        background: linear-gradient(135deg, #343a40, #212529);
        color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(33, 37, 41, 0.15);
        margin-bottom: 10px;
        text-align: center;
    }
    .card-metric {
        flex: 1;
        background-color: #ffffff;
        border-radius: 20px;
        padding: 20px 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border: 1px solid #f1f3f5;
    }
    .metric-title { font-size: 14px; font-weight: 600; color: #868e96; margin-bottom: 8px;}
    .metric-value { font-size: 24px; font-weight: 700; }
    .text-green { color: #20c997; }
    .text-red { color: #fa5252; }
    .metric-subtitle { font-size: 11px; color: #adb5bd; margin-top: 5px;}
    .card-balance {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        border-radius: 20px;
        padding: 25px 20px;
        box-shadow: 0 8px 20px rgba(0,123,255,0.2);
        margin-bottom: 30px;
    }
    .ingreso-marker, .gasto-marker, .bottom-buttons-marker { display: none; }
    div.element-container:has(.bottom-buttons-marker) + div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 15px !important;
    }
    div.element-container:has(.ingreso-marker) + div.element-container button {
        background: linear-gradient(135deg, #20c997, #12b886) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px !important;
        height: auto !important;
    }
    div.element-container:has(.gasto-marker) + div.element-container button {
        background: linear-gradient(135deg, #fa5252, #e03131) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px !important;
        height: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if 'inicializado' not in st.session_state:
    try:
        req = requests.get(JSONBIN_URL, headers=JSONBIN_HEADERS)
        if req.status_code == 200:
            datos_nube = req.json()['record']
            st.session_state.pago_fijo = datos_nube.get('pago_fijo', 1161.00)
            st.session_state.counter = datos_nube.get('counter', 0)
            fecha_str = datos_nube.get('fecha_pago', str(datetime.today().date()))
            st.session_state.fecha_pago = datetime.strptime(fecha_str[:10], '%Y-%m-%d').date()
            
            df_nube = pd.DataFrame(datos_nube.get('transacciones', []))
            if not df_nube.empty:
                df_nube['Fecha'] = pd.to_datetime(df_nube['Fecha']).dt.date
            else:
                df_nube = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])
            st.session_state.transacciones = df_nube
        else:
            raise Exception()
    except:
        st.session_state.transacciones = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])
        st.session_state.pago_fijo = 1161.00
        st.session_state.fecha_pago = datetime.today().date()
        st.session_state.counter = 0
    st.session_state.inicializado = True

# --- LÓGICA DE CÁLCULOS ---
df = st.session_state.transacciones
total_ingresos = df[df['Tipo'] == 'Ingreso']['Monto'].sum()
total_gastos = df[df['Tipo'] == 'Gasto']['Monto'].sum()
saldo_actual = st.session_state.pago_fijo + total_ingresos - total_gastos

# --- MODALES ---
@st.dialog("⚙️ Configurar Pago Fijo")
def modal_pago_fijo():
    nuevo_pago = st.number_input("Cantidad ($)", min_value=0.0, value=float(st.session_state.pago_fijo), step=50.0)
    nueva_fecha = st.date_input("Fecha de pago", value=st.session_state.fecha_pago)
    if st.button("Guardar Cambios", use_container_width=True, type="primary"):
        st.session_state.pago_fijo = nuevo_pago
        st.session_state.fecha_pago = nueva_fecha
        guardar_en_jsonbin()
        st.rerun()

@st.dialog("↓ Registrar Nuevo Ingreso")
def modal_ingreso():
    monto = st.number_input("Monto ($)", min_value=0.1, step=10.0)
    desc = st.text_input("Descripción")
    fecha = st.date_input("Fecha")
    if st.button("Agregar Ingreso", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Ingreso', 'Monto': monto, 'Categoría': 'Ingreso Extra', 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
        guardar_en_jsonbin()
        st.rerun()

@st.dialog("↑ Registrar Nuevo Gasto")
def modal_gasto():
    monto = st.number_input("Monto ($)", min_value=0.1, step=5.0)
    cat = st.selectbox("Categoría", ["Alimentación", "Transporte", "Servicios Básicos", "Vivienda", "Entretenimiento", "Salud", "Educación", "Otros"])
    desc = st.text_input("Descripción")
    fecha = st.date_input("Fecha")
    if st.button("Agregar Gasto", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Gasto', 'Monto': monto, 'Categoría': cat, 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
        guardar_en_jsonbin()
        st.rerun()

# --- INTERFAZ ---
st.markdown("<h2 style='text-align: center;'>CashBook</h2>", unsafe_allow_html=True)

st.markdown(f"""
<div class="card-pago-fijo">
    <div style="font-size: 13px; opacity: 0.8;">Pago Fijo Base • {st.session_state.fecha_pago.strftime('%d/%m/%Y')}</div>
    <div style="font-size: 32px; font-weight: bold;">${st.session_state.pago_fijo:,.2f}</div>
</div>
""", unsafe_allow_html=True)

if st.button("⚙️ Modificar Pago Fijo", use_container_width=True):
    modal_pago_fijo()

st.markdown(f"""
<div class="flex-container">
    <div class="card-metric">
        <div class="metric-title"><span style="color:#20c997;">↓</span> Ingresos</div>
        <div class="metric-value text-green">${total_ingresos:,.2f}</div>
    </div>
    <div class="card-metric">
        <div class="metric-title"><span style="color:#fa5252;">↑</span> Gastos</div>
        <div class="metric-value text-red">${total_gastos:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="card-balance">
    <div style="font-size: 14px; opacity: 0.8;">Saldo Actual</div>
    <div style="font-size: 38px; font-weight: bold;">${saldo_actual:,.2f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<span class="bottom-buttons-marker"></span>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<span class="ingreso-marker"></span>', unsafe_allow_html=True)
    if st.button("↓ Ingreso", use_container_width=True): modal_ingreso()
with c2:
    st.markdown('<span class="gasto-marker"></span>', unsafe_allow_html=True)
    if st.button("↑ Gasto", use_container_width=True): modal_gasto()

# --- TABS ---
t1, t2, t3 = st.tabs(["📝 Historial", "📊 Gráficos", "📋 Resumen"])
with t1:
    if st.session_state.transacciones.empty:
        st.info("Sin transacciones.")
    else:
        df_sorted = st.session_state.transacciones.sort_values(by='Fecha', ascending=False)
        for _, row in df_sorted.iterrows():
            with st.container(border=True):
                col_info, col_monto, col_del = st.columns([5, 3, 1])
                col_info.markdown(f"**{row['Categoría']}**\n{row['Descripción']} ({row['Fecha']})")
                color = "#fa5252" if row['Tipo'] == 'Gasto' else "#20c997"
                col_monto.markdown(f"<div style='color:{color}; font-weight:bold; text-align:right;'>${row['Monto']:,.2f}</div>", unsafe_allow_html=True)
                if col_del.button("🗑️", key=f"del_{row['ID']}"):
                    st.session_state.transacciones = st.session_state.transacciones[st.session_state.transacciones['ID'] != row['ID']]
                    guardar_en_jsonbin()
                    st.rerun()
with t2:
    df_gastos = st.session_state.transacciones[st.session_state.transacciones['Tipo'] == 'Gasto']
    if not df_gastos.empty:
        st.bar_chart(df_gastos.groupby('Fecha')['Monto'].sum(), color="#fa5252")
with t3:
    st.write(f"Saldo: **${saldo_actual:,.2f}**")
