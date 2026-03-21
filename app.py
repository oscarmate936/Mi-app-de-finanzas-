import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CashBook", page_icon="💳", layout="centered")

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
        display: flex;
        flex-direction: column;
        align-items: center; /* Centrar contenido de las tarjetas */
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
        text-align: center;
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

    /* === MAGIA CSS: ALINEACIÓN PERFECTA DE BOTONES NATIVOS === */
    
    /* Ocultar los marcadores invisibles */
    .ingreso-marker, .gasto-marker, .bottom-buttons-marker { display: none; }

    /* Forzar que las dos columnas inferiores sean idénticas al .flex-container de arriba */
    div.element-container:has(.bottom-buttons-marker) + div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 15px !important; /* Misma separación que las tarjetas */
    }
    div.element-container:has(.bottom-buttons-marker) + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 !important; /* Fuerza a que ocupen exactamente la mitad cada uno */
        min-width: 0 !important;
    }

    /* Diseño del Botón de Ingreso (Verde) */
    div.element-container:has(.ingreso-marker) + div.element-container button {
        background: linear-gradient(135deg, #20c997, #12b886) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important; /* Mismo radio que las tarjetas */
        padding: 15px !important;
        height: auto !important;
        width: 100% !important; /* Ocupa todo el espacio de su columna centrándolo con la tarjeta */
        display: flex !important;
        justify-content: center !important; /* Centra el texto */
        align-items: center !important;
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
        border-radius: 20px !important; /* Mismo radio que las tarjetas */
        padding: 15px !important;
        height: auto !important;
        width: 100% !important; /* Ocupa todo el espacio de su columna centrándolo con la tarjeta */
        display: flex !important;
        justify-content: center !important; /* Centra el texto */
        align-items: center !important;
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

# --- INICIALIZACIÓN DE DATOS (Estado de Sesión) ---
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])
if 'pago_fijo' not in st.session_state:
    st.session_state.pago_fijo = 1161.00
if 'fecha_pago' not in st.session_state:
    st.session_state.fecha_pago = datetime.today()
if 'counter' not in st.session_state:
    st.session_state.counter = 0

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
        st.rerun()

@st.dialog("↑ Registrar Nuevo Gasto")
def modal_gasto():
    monto = st.number_input("Monto del Gasto ($)", min_value=0.1, step=5.0)
    cat = st.selectbox("Categoría", ["Entertainment", "Comida", "Transporte", "Servicios", "Otros"])
    desc = st.text_input("Descripción (Ej. Netflix, Gasolina)")
    fecha = st.date_input("Fecha del gasto")
    if st.button("Realmente Agregar Gasto", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Gasto', 'Monto': monto, 'Categoría': cat, 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
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


# 5. HISTORIAL DE TRANSACCIONES
st.subheader("Transacciones Recientes")
tab1, tab2 = st.tabs(["Movimientos", "Resumen"])

with tab1:
    if st.session_state.transacciones.empty:
        st.write("No hay transacciones registradas.")
    else:
        df_sorted = st.session_state.transacciones.sort_values(by='Fecha', ascending=False)
        for index, row in df_sorted.iterrows():
            with st.container():
                col_icono, col_info, col_monto, col_del = st.columns([1, 4, 2, 1])
                with col_icono:
                    if row['Tipo'] == 'Gasto':
                        st.markdown("<div style='background:#ffe3e3; color:#fa5252; border-radius:50%; width:35px; height:35px; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-top:5px;'>↑</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background:#d3f9d8; color:#20c997; border-radius:50%; width:35px; height:35px; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-top:5px;'>↓</div>", unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"<div style='font-weight:600; font-size:14px; margin-bottom:-5px;'>{row['Categoría']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:12px; color:gray;'>{row['Descripción']} • {row['Fecha'].strftime('%d %b')}</div>", unsafe_allow_html=True)
                with col_monto:
                    color = "red" if row['Tipo'] == 'Gasto' else "green"
                    signo = "-" if row['Tipo'] == 'Gasto' else "+"
                    st.markdown(f"<div style='color:{color}; font-weight:bold; text-align:right; margin-top:8px;'>{signo}${row['Monto']:.2f}</div>", unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_{row['ID']}", help="Eliminar"):
                        st.session_state.transacciones = st.session_state.transacciones[st.session_state.transacciones['ID'] != row['ID']]
                        st.rerun()
            st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)
            
with tab2:
    st.info(f"💰 **Total Dinero Restante:** ${saldo_actual:,.2f}")
    st.write(f"Pago Fijo Base: ${st.session_state.pago_fijo:,.2f}")
    st.write(f"Total Ingresos Extra: ${total_ingresos:,.2f}")
    st.write(f"Total Gastado: ${total_gastos:,.2f}")

st.write("")

# ==========================================
# 6 y 7. BOTONES INFERIORES (Nativos y perfectamente alineados)
# ==========================================

# Marcador para avisarle al CSS que aplique el diseño "Lado a Lado Exacto" a las siguientes columnas
st.markdown('<span class="bottom-buttons-marker"></span>', unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Marcador para pintar verde y forzar ancho/centrado
    st.markdown('<span class="ingreso-marker"></span>', unsafe_allow_html=True)
    if st.button("↓ Ingreso"):
        modal_ingreso()

with col_btn2:
    # Marcador para pintar rojo y forzar ancho/centrado
    st.markdown('<span class="gasto-marker"></span>', unsafe_allow_html=True)
    if st.button("↑ Gasto"):
        modal_gasto()
