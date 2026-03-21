import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mi Billetera", page_icon="💳", layout="centered")

# --- CSS AVANZADO (Apariencia de App Móvil Nativa) ---
st.markdown("""
<style>
    /* Fondo general más claro para que resalten las tarjetas */
    .stApp { background-color: #f8f9fa; }
    
    /* Contenedor Flex para forzar lado a lado en móviles */
    .flex-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    /* Estilos de Tarjetas Métricas */
    .card-metric {
        flex: 1;
        background-color: #ffffff;
        border-radius: 20px;
        padding: 20px 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
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
        box-shadow: 0 8px 20px rgba(0,123,255,0.25);
        margin-bottom: 30px;
    }
    
    /* Historial de transacciones */
    .transaction-row {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        border: 1px solid #f1f3f5;
    }
    
    /* Forzar botones inferiores a estar en la misma línea */
    div[data-testid="column"] {
        min-width: 45% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS (Estado de Sesión) ---
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])
if 'pago_fijo' not in st.session_state:
    st.session_state.pago_fijo = 1161.00 # Valor de ejemplo basado en tu imagen
if 'fecha_pago' not in st.session_state:
    st.session_state.fecha_pago = datetime.today()
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# --- LÓGICA DE CÁLCULOS (ACTUALIZADA) ---
df = st.session_state.transacciones

# Los ingresos ahora SOLO reflejan los movimientos registrados con el botón de ingresos
total_ingresos = df[df['Tipo'] == 'Ingreso']['Monto'].sum()
total_gastos = df[df['Tipo'] == 'Gasto']['Monto'].sum()

# El saldo actual suma tu base (pago fijo) + lo extra que ingreses - los gastos
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
    if st.button("Agregar Ingreso", use_container_width=True, type="primary"):
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
    if st.button("Agregar Gasto", use_container_width=True, type="primary"):
        st.session_state.counter += 1
        nuevo = pd.DataFrame([{'ID': st.session_state.counter, 'Tipo': 'Gasto', 'Monto': monto, 'Categoría': cat, 'Descripción': desc, 'Fecha': fecha}])
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo], ignore_index=True)
        st.rerun()


# ==========================================
# INTERFAZ VISUAL (DISEÑO PRINCIPAL)
# ==========================================

# 1. BOTÓN DE PAGO FIJO (Interactivo)
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f"**Pago Fijo:** ${st.session_state.pago_fijo:,.2f} | **Día:** {st.session_state.fecha_pago.strftime('%d/%m/%Y')}")
with col_top2:
    if st.button("⚙️ Editar", use_container_width=True):
        modal_pago_fijo()

st.markdown("<hr style='margin: 10px 0 20px 0; opacity: 0.3;'>", unsafe_allow_html=True)

# 2 y 3. TARJETAS DE INGRESOS Y GASTOS (Lado a lado usando Flexbox)
st.markdown(f"""
<div class="flex-container">
    <div class="card-metric">
        <div class="metric-title"><span style="color:#20c997;">↓</span> Ingresos</div>
        <div class="metric-value text-green">${total_ingresos:,.2f}</div>
        <div class="metric-subtitle">Este Mes</div>
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


# 5. HISTORIAL DE TRANSACCIONES PROFESIONAL
st.subheader("Transacciones Recientes")
tab1, tab2 = st.tabs(["Movimientos", "Resumen"])

with tab1:
    if st.session_state.transacciones.empty:
        st.write("No hay transacciones registradas.")
    else:
        # Ordenar por fecha (más reciente primero)
        df_sorted = st.session_state.transacciones.sort_values(by='Fecha', ascending=False)
        
        # Iterar para crear una lista personalizada con botón de eliminar
        for index, row in df_sorted.iterrows():
            with st.container():
                col_icono, col_info, col_monto, col_del = st.columns([1, 4, 2, 1])
                
                # Icono según tipo
                with col_icono:
                    if row['Tipo'] == 'Gasto':
                        st.markdown("<div style='background:#ffe3e3; color:#fa5252; border-radius:50%; width:35px; height:35px; display:flex; align-items:center; justify-content:center; font-weight:bold;'>↑</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background:#d3f9d8; color:#20c997; border-radius:50%; width:35px; height:35px; display:flex; align-items:center; justify-content:center; font-weight:bold;'>↓</div>", unsafe_allow_html=True)
                
                # Información
                with col_info:
                    st.markdown(f"<div style='font-weight:600; font-size:14px; margin-bottom:-5px;'>{row['Categoría']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:12px; color:gray;'>{row['Descripción']} • {row['Fecha'].strftime('%d %b')}</div>", unsafe_allow_html=True)
                
                # Monto
                with col_monto:
                    color = "red" if row['Tipo'] == 'Gasto' else "green"
                    signo = "-" if row['Tipo'] == 'Gasto' else "+"
                    st.markdown(f"<div style='color:{color}; font-weight:bold; text-align:right; margin-top:8px;'>{signo}${row['Monto']:.2f}</div>", unsafe_allow_html=True)
                
                # Botón Eliminar
                with col_del:
                    if st.button("🗑️", key=f"del_{row['ID']}", help="Eliminar transacción"):
                        st.session_state.transacciones = st.session_state.transacciones[st.session_state.transacciones['ID'] != row['ID']]
                        st.rerun()
            
            st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)
            
with tab2:
    st.info(f"💰 **Total Dinero Restante:** ${saldo_actual:,.2f}")
    st.write(f"Pago Fijo Base: ${st.session_state.pago_fijo:,.2f}")
    st.write(f"Total Ingresos Extra: ${total_ingresos:,.2f}")
    st.write(f"Total Gastado: ${total_gastos:,.2f}")

st.write("")
st.write("")

# 6 y 7. BOTONES INFERIORES LADO A LADO
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("↓ Ingreso", use_container_width=True):
        modal_ingreso()

with col_btn2:
    if st.button("↑ Gasto", use_container_width=True):
        modal_gasto()
