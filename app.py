import streamlit as st
import pandas as pd
from datetime import datetime
import requests # <-- NUEVO: Para conectarnos a JSONBin

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CashBook", page_icon="💳", layout="centered")

# --- CONFIGURACIÓN JSONBIN ---
# Leemos las claves de forma segura desde los secrets de Streamlit
JSONBIN_KEY = st.secrets["JSONBIN_KEY"]
JSONBIN_BIN_ID = st.secrets["JSONBIN_BIN_ID"]

JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
JSONBIN_HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def guardar_en_jsonbin():
    """Guarda el estado actual en la nube silenciosamente."""
    df_save = st.session_state.transacciones.copy()
    if not df_save.empty:
        df_save['Fecha'] = df_save['Fecha'].astype(str) # Convertimos fechas a texto para que JSON lo entienda

    data = {
        "pago_fijo": float(st.session_state.pago_fijo),
        "fecha_pago": str(st.session_state.fecha_pago),
        "counter": int(st.session_state.counter),
        "transacciones": df_save.to_dict(orient="records")
    }
    try:
        requests.put(JSONBIN_URL, json=data, headers=JSONBIN_HEADERS)
    except:
        pass # Si hay error temporal de red, no rompemos la app

# --- CSS AVANZADO ---
st.markdown("""
<style>
    /* Fondo general más claro */
    .stApp { background-color: #f8f9fa; }
    
    /* Contenedor Flex para forzar lado a lado en móviles (Tarjetas superiores) */
    .flex-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    /* Tarjeta Pago Fijo (Gris oscuro) */
    .card-pago-fijo {
        background: linear-gradient(135deg, #343a40, #212529);
        color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(33, 37, 41, 0.15);
        margin-bottom: 10px;
        text-align: center;
    }
    
    /* Estilos de Tarjetas Métricas Blancas */
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
    
    /* Tarjeta Saldo Actual (Azul) */
    .card-balance {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        border-radius: 20px;
        padding: 25px 20px;
        box-shadow: 0 8px 20px rgba(0,123,255,0.2);
        margin-bottom: 30px;
    }
    
    /* Historial de transacciones */
    .transaction-row {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.01);
        border: 1px solid #f1f3f5;
    }

    /* === MAGIA CSS: ESTILIZAR BOTONES NATIVOS DE STREAMLIT === */
    
    /* Ocultar los marcadores invisibles */
    .ingreso-marker, .gasto-marker, .bottom-buttons-marker { display: none; }

    /* Forzar que las dos columnas inferiores se queden lado a lado en celular */
    div.element-container:has(.bottom-buttons-marker) + div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 15px !important;
    }
    div.element-container:has(.bottom-buttons-marker) + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        min-width: 0 !important;
    }

    /* Diseño del Botón de Ingreso (Verde) */
    div.element-container:has(.ingreso-marker) + div.element-container button {
        background: linear-gradient(135deg, #20c997, #12b886) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px !important;
        height: auto !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        transition: all 0.2s ease !important;
    }
    /* Texto del botón de ingreso */
    div.element-container:has(.ingreso-marker) + div.element-container button * {
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Diseño del Botón de Gasto (Rojo) */
    div.element-container:has(.gasto-marker) + div.element-container button {
        background: linear-gradient(135deg, #fa5252, #e03131) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px !important;
        height: auto !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        transition: all 0.2s ease !important;
    }
    /* Texto del botón de gasto */
    div.element-container:has(.gasto-marker) + div.element-container button * {
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Efecto al pasar el mouse por encima */
    div.element-container:has(.ingreso-marker) + div.element-container button:hover,
    div.element-container:has(.gasto-marker) + div.element-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
    }

</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS (Estado de Sesión + JSONBin) ---
if 'inicializado' not in st.session_state:
    try:
        # Intentamos descargar los datos desde la nube
        req = requests.get(JSONBIN_URL, headers=JSONBIN_HEADERS)
        if req.status_code == 200:
            datos_nube = req.json()['record']

            st.session_state.pago_fijo = datos_nube.get('pago_fijo', 1161.00)
            st.session_state.counter = datos_nube.get('counter', 0)

            # Formateamos la fecha correctamente
            fecha_str = datos_nube.get('fecha_pago', str(datetime.today().date()))
            try:
                st.session_state.fecha_pago = datetime.strptime(fecha_str[:10], '%Y-%m-%d').date()
            except:
                st.session_state.fecha_pago = datetime.today().date()

            # Formateamos el DataFrame
            df_nube = pd.DataFrame(datos_nube.get('transacciones', []))
            if not df_nube.empty:
                df_nube['Fecha'] = pd.to_datetime(df_nube['Fecha']).dt.date
            else:
                df_nube = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])

            st.session_state.transacciones = df_nube
        else:
            raise Exception("No hay datos")

    except:
        # Si algo falla (primer uso), iniciamos en blanco
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

# ==========================================
# VENTANAS MODALES INTERACTIVAS (Pop-ups)
# ==========================================

@st.dialog("⚙️ Configurar Pago Fijo")
def modal_pago_fijo():
    st.write("Establece tu pago base. Este valor será fijo.")
    nuevo_pago = st.number_input("Cantidad ($)", min_value=0.0, value=float(st.session_state.pago_fijo), step=50.0)
    nueva_fecha = st.date_input("Fecha de pago", value=st.session_state.fecha_pago)
    if st.button("Guardar Cambios", use_container_width=True, type="primary"):
        st.session_state.pago_fijo = nuevo_pago
        st.session_state.fecha_pago = nueva_fecha
        guardar_en_jsonbin() # <-- Guardamos en la nube
        st.rerun()

@st.dialog("↓ Registrar Nuevo Ingreso")
def modal_ingreso():
    monto = st.number_input("Monto del Ingreso ($)", min_value=0.1, step=10.0)
    desc = st.text_input("Descripción (Ej. Venta, Bono)")
    fecha = st.date_input("Fecha del ingreso")
    if st.button("Realmente Agregar Ingreso", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Ingreso', 'Monto': monto, 'Categoría': 'Ingreso Extra', 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
        guardar_en_jsonbin() # <-- Guardamos en la nube
        st.rerun()

@st.dialog("↑ Registrar Nuevo Gasto")
def modal_gasto():
    monto = st.number_input("Monto del Gasto ($)", min_value=0.1, step=5.0)

    cat = st.selectbox("Categoría", [
        "Alimentación", 
        "Transporte", 
        "Servicios Básicos", 
        "Vivienda", 
        "Entretenimiento", 
        "Salud", 
        "Educación", 
        "Otros"
    ])

    desc = st.text_input("Descripción (Ej. Netflix, Gasolina)")
    fecha = st.date_input("Fecha del gasto")
    if st.button("Realmente Agregar Gasto", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Gasto', 'Monto': monto, 'Categoría': cat, 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
        guardar_en_jsonbin() # <-- Guardamos en la nube
        st.rerun()


# ==========================================
# INTERFAZ VISUAL (DISEÑO PRINCIPAL)
# ==========================================

# NOMBRE DE LA APP
st.markdown("<h2 style='text-align: center; font-weight: 800; color: #1e1e1e; margin-bottom: 20px;'>CashBook</h2>", unsafe_allow_html=True)

# 1. TARJETA DE PAGO FIJO
st.markdown(f"""
<div class="card-pago-fijo">
    <div style="font-size: 13px; opacity: 0.8; margin-bottom: 5px;">Pago Fijo Base • Día {st.session_state.fecha_pago.strftime('%d/%m/%Y')}</div>
    <div style="font-size: 32px; font-weight: bold;">${st.session_state.pago_fijo:,.2f}</div>
</div>
""", unsafe_allow_html=True)

if st.button("⚙️ Modificar Pago Fijo", use_container_width=True, key="btn_pf"):
    modal_pago_fijo()

st.markdown("<hr style='margin: 20px 0 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

# 2 y 3. TARJETAS DE INGRESOS Y GASTOS (Lado a lado)
st.markdown(f"""
<div class="flex-container">
    <div class="card-metric">
        <div class="metric-title"><span style="color:#20c997;">↓</span> Ingresos Extra</div>
        <div class="metric-value text-green">${total_ingresos:,.2f}</div>
        <div class="metric-subtitle">Registrados</div>
    </div>
    <div class="card-metric">
        <div class="metric-title"><span style="color:#fa5252;">↑</span> Gastos</div>
        <div class="metric-value text-red">${total_gastos:,.2f}</div>
        <div class="metric-subtitle">Este Mes</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. TARJETA DE SALDO ACTUAL
st.markdown(f"""
<div class="card-balance">
    <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Saldo Actual</div>
    <div style="font-size: 38px; font-weight: bold;">${saldo_actual:,.2f}</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. BOTONES DE ACCIÓN 
# ==========================================

# Marcador para avisarle al CSS que aplique el diseño "Lado a Lado" a las siguientes columnas
st.markdown('<span class="bottom-buttons-marker"></span>', unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Marcador para avisarle al CSS que pinte el siguiente botón de Verde
    st.markdown('<span class="ingreso-marker"></span>', unsafe_allow_html=True)
    if st.button("↓ Ingreso", use_container_width=True):
        modal_ingreso()

with col_btn2:
    # Marcador para avisarle al CSS que pinte el siguiente botón de Rojo
    st.markdown('<span class="gasto-marker"></span>', unsafe_allow_html=True)
    if st.button("↑ Gasto", use_container_width=True):
        modal_gasto()

st.markdown("<hr style='margin: 30px 0 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)


# ==========================================
# 6. HISTORIAL DE TRANSACCIONES Y GRÁFICOS (REDISEÑO PROFESIONAL)
# ==========================================

tab1, tab2, tab3 = st.tabs(["📝 Historial", "📊 Gráficos", "📋 Resumen"])

with tab1:
    if st.session_state.transacciones.empty:
        st.info("No hay transacciones registradas todavía.")
    else:
        df_sorted = st.session_state.transacciones.sort_values(by='Fecha', ascending=False)

        # --- MAPEO PROFESIONAL DE ÍCONOS POR CATEGORÍA ---
        iconos_cat = {
            "Alimentación": "🍽️",
            "Transporte": "🚗",
            "Servicios Básicos": "⚡",
            "Vivienda": "🏠",
            "Entretenimiento": "🎫",
            "Salud": "⚕️",
            "Educación": "📚",
            "Ingreso Extra": "💰",
            "Otros": "📌"
        }

        for index, row in df_sorted.iterrows():
            with st.container(border=True):
                col_icono, col_info, col_monto, col_del = st.columns([1, 4, 3, 1], vertical_alignment="center")

                icono = iconos_cat.get(row['Categoría'], "💳")

                with col_icono:
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 50%; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.04);'>
                        {icono}
                    </div>
                    """, unsafe_allow_html=True)

                with col_info:
                    st.markdown(f"<div style='font-family: system-ui, sans-serif; font-weight: 700; font-size: 15px; color: #212529; margin-bottom: 2px;'>{row['Categoría']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-family: system-ui, sans-serif; font-size: 13px; color: #868e96;'>{row['Descripción']} • {row['Fecha'].strftime('%d %b %Y')}</div>", unsafe_allow_html=True)

                with col_monto:
                    color = "#fa5252" if row['Tipo'] == 'Gasto' else "#20c997"
                    signo = "-" if row['Tipo'] == 'Gasto' else "+"
                    st.markdown(f"<div style='font-family: monospace, sans-serif; color: {color}; font-weight: 800; font-size: 17px; text-align: right; letter-spacing: -0.5px;'>{signo}${row['Monto']:,.2f}</div>", unsafe_allow_html=True)

                with col_del:
                    if st.button("🗑️", key=f"del_{row['ID']}", help="Eliminar registro"):
                        st.session_state.transacciones = st.session_state.transacciones[st.session_state.transacciones['ID'] != row['ID']]
                        guardar_en_jsonbin() # <-- Guardamos en la nube la eliminación
                        st.rerun()

with tab2:
    st.markdown("<h4 style='color: #343a40; margin-bottom: 20px;'>Tus Gastos por Día</h4>", unsafe_allow_html=True)
    df_gastos = st.session_state.transacciones[st.session_state.transacciones['Tipo'] == 'Gasto']

    if not df_gastos.empty:
        # Agrupamos los montos de gasto por fecha
        gastos_diarios = df_gastos.groupby('Fecha')['Monto'].sum().reset_index()
        gastos_diarios.set_index('Fecha', inplace=True)

        # Mostramos el gráfico de barras nativo
        st.bar_chart(gastos_diarios, color="#fa5252", use_container_width=True)
    else:
        st.success("¡Excelente! Aún no tienes gastos registrados para graficar.")

with tab3:
    st.info(f"💰 **Total Dinero Restante:** ${saldo_actual:,.2f}")
    st.write(f"Pago Fijo Base: **${st.session_state.pago_fijo:,.2f}**")
    st.write(f"Total Ingresos Extra: **${total_ingresos:,.2f}**")
    st.write(f"Total Gastado: **${total_gastos:,.2f}**") 
