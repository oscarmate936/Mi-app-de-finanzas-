import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestor Financiero", page_icon="💳", layout="centered")

# --- CSS PERSONALIZADO (Diseño Profesional) ---
st.markdown("""
<style>
    .card-metric {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #f0f2f6;
    }
    .card-balance {
        background: linear-gradient(135deg, #0052D4, #4364F7, #6FB1FC);
        color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 20px rgba(0,82,212,0.2);
        margin-bottom: 25px;
    }
    .metric-value { font-size: 28px; font-weight: bold; margin: 5px 0; }
    .metric-label { font-size: 14px; color: #6c757d; font-weight: 500;}
    .balance-value { font-size: 36px; font-weight: bold; margin: 10px 0; color: white;}
    .balance-label { font-size: 16px; opacity: 0.9;}
    .text-green { color: #28a745; }
    .text-red { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN (Base de datos temporal) ---
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = pd.DataFrame(columns=['ID', 'Tipo', 'Monto', 'Categoría', 'Descripción', 'Fecha'])
if 'pago_fijo' not in st.session_state:
    st.session_state.pago_fijo = 0.0
if 'fecha_pago' not in st.session_state:
    st.session_state.fecha_pago = None
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# --- LÓGICA DE CÁLCULOS ---
df = st.session_state.transacciones
total_ingresos = df[df['Tipo'] == 'Ingreso']['Monto'].sum() + st.session_state.pago_fijo
total_gastos = df[df['Tipo'] == 'Gasto']['Monto'].sum()
saldo_actual = total_ingresos - total_gastos

# ==========================================
# ESTRUCTURA DE LA APP (Basada en tu imagen)
# ==========================================

# 1. BOTÓN/SECCIÓN DE PAGO FIJO
with st.expander("⚙️ Configurar Pago Fijo Mensual"):
    col_pf1, col_pf2 = st.columns(2)
    with col_pf1:
        nuevo_pago = st.number_input("Cantidad del pago", min_value=0.0, value=st.session_state.pago_fijo, step=10.0)
    with col_pf2:
        nueva_fecha = st.date_input("Fecha de pago", value=st.session_state.fecha_pago if st.session_state.fecha_pago else datetime.today())
    if st.button("Guardar Pago Fijo"):
        st.session_state.pago_fijo = nuevo_pago
        st.session_state.fecha_pago = nueva_fecha
        st.rerun()

st.write("") # Espacio

# 2 y 3. TARJETAS DE INGRESOS Y GASTOS (Misma posición, lado a lado)
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="card-metric">
        <div class="metric-label">↓ Ingresos</div>
        <div class="metric-value text-green">${total_ingresos:,.2f}</div>
        <div style="font-size:12px; color:#adb5bd;">Este Mes</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-metric">
        <div class="metric-label">↑ Gastos</div>
        <div class="metric-value text-red">${total_gastos:,.2f}</div>
        <div style="font-size:12px; color:#adb5bd;">Este Mes</div>
    </div>
    """, unsafe_allow_html=True)

# 4. TARJETA DE SALDO ACTUAL (Total)
st.markdown(f"""
<div class="card-balance">
    <div class="balance-label">Saldo Actual</div>
    <div class="balance-value">${saldo_actual:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 5. HISTORIAL DE TRANSACCIONES (Con pestaña y edición)
st.subheader("📋 Historial de Transacciones")
tab1, = st.tabs(["Detalle de Movimientos"])

with tab1:
    if not st.session_state.transacciones.empty:
        # st.data_editor permite borrar filas seleccionándolas y presionando 'Delete' o el ícono de papelera
        df_editado = st.data_editor(
            st.session_state.transacciones,
            use_container_width=True,
            num_rows="dynamic", # Permite agregar o borrar filas directamente
            hide_index=True,
            column_config={
                "Monto": st.column_config.NumberColumn(format="$%.2f"),
                "Fecha": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )
        # Actualizar el dataframe si el usuario borró o editó algo en la tabla
        if not df_editado.equals(st.session_state.transacciones):
            st.session_state.transacciones = df_editado
            st.rerun()
            
        st.info(f"💡 Dinero restante exacto (Balance): **${saldo_actual:,.2f}**")
    else:
        st.write("No hay transacciones registradas aún.")

st.divider()

# 6 y 7. BOTONES INFERIORES PARA AGREGAR INGRESOS Y GASTOS
st.write("### Registrar Nuevo Movimiento")
col_btn1, col_btn2 = st.columns(2)

# Botón 6: Ingresos
with col_btn1:
    with st.popover("↓ Añadir Ingreso", use_container_width=True):
        st.markdown("**Nuevo Ingreso**")
        ing_monto = st.number_input("Monto ($)", min_value=0.1, step=1.0, key="ing_monto")
        ing_desc = st.text_input("Descripción", key="ing_desc")
        ing_fecha = st.date_input("Fecha", key="ing_fecha")
        if st.button("Guardar Ingreso", type="primary", use_container_width=True):
            st.session_state.counter += 1
            nuevo_ingreso = pd.DataFrame([{
                'ID': st.session_state.counter, 'Tipo': 'Ingreso', 
                'Monto': ing_monto, 'Categoría': 'Ingreso Extra', 
                'Descripción': ing_desc, 'Fecha': ing_fecha
            }])
            st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo_ingreso], ignore_index=True)
            st.rerun()

# Botón 7: Gastos
with col_btn2:
    with st.popover("↑ Añadir Gasto", use_container_width=True):
        st.markdown("**Nuevo Gasto**")
        gasto_monto = st.number_input("Monto ($)", min_value=0.1, step=1.0, key="gasto_monto")
        gasto_cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Entretenimiento", "Otros"], key="gasto_cat")
        gasto_desc = st.text_input("Descripción breve", key="gasto_desc")
        gasto_fecha = st.date_input("Fecha", key="gasto_fecha2")
        if st.button("Guardar Gasto", type="primary", use_container_width=True):
            st.session_state.counter += 1
            nuevo_gasto = pd.DataFrame([{
                'ID': st.session_state.counter, 'Tipo': 'Gasto', 
                'Monto': gasto_monto, 'Categoría': gasto_cat, 
                'Descripción': gasto_desc, 'Fecha': gasto_fecha
            }])
            st.session_state.transacciones = pd.concat([st.session_state.transacciones, nuevo_gasto], ignore_index=True)
            st.rerun()
