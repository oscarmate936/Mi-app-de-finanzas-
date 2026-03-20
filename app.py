import streamlit as st
import pandas as pd
# Importación directa ahora que el archivo está al lado
from db_manager import init_db, get_transacciones

st.set_page_config(
    page_title="Gestor Financiero Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

st.title("🏠 Dashboard Principal")
st.markdown("Bienvenido a tu resumen financiero.")
st.divider()

df = get_transacciones()

if not df.empty:
    ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
    gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
    saldo_actual = ingresos - gastos
else:
    ingresos, gastos, saldo_actual = 0.0, 0.0, 0.0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💰 Saldo Actual", value=f"${saldo_actual:,.2f}")
with col2:
    st.metric(label="📈 Ingresos del Mes", value=f"${ingresos:,.2f}")
with col3:
    st.metric(label="📉 Gastos del Mes", value=f"${gastos:,.2f}")

st.divider()

st.subheader("Últimos Movimientos")
if df.empty:
    st.info("Aún no tienes movimientos registrados. Ve a la sección 'Movimientos' para empezar.")
else:
    st.dataframe(df.head(5), use_container_width=True, hide_index=True)
