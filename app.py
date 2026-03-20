import streamlit as st
from utils.db_manager import init_db, get_transacciones
import pandas as pd

# Configuración de la página (DEBE ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Gestor Financiero Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar la base de datos
init_db()

st.title("🏠 Dashboard Principal")
st.markdown("Bienvenido a tu resumen financiero.")
st.divider()

# Obtener datos
df = get_transacciones()

# Calcular métricas básicas
if not df.empty:
    ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
    gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
    saldo_actual = ingresos - gastos
else:
    ingresos, gastos, saldo_actual = 0.0, 0.0, 0.0

# --- SECCIÓN DE MÉTRICAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💰 Saldo Actual", value=f"${saldo_actual:,.2f}")
with col2:
    st.metric(label="📈 Ingresos del Mes", value=f"${ingresos:,.2f}")
with col3:
    st.metric(label="📉 Gastos del Mes", value=f"${gastos:,.2f}")

st.divider()

# --- SECCIÓN DE VISTA PREVIA ---
st.subheader("Últimos Movimientos")
if df.empty:
    st.info("Aún no tienes movimientos registrados. Ve a la sección 'Movimientos' para empezar.")
else:
    # Mostramos solo los últimos 5 movimientos para no saturar el Dashboard
    st.dataframe(
        df.head(5),
        use_container_width=True,
        hide_index=True
    )
