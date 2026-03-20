import streamlit as st
import pandas as pd

# Configuración de la página (título y layout ancho)
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# Título principal
st.title("💰 Panel de Control Financiero")

# --- Tarjetas superiores (Ingresos, Gastos, Saldo) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Ingresos",
        value="$0.00",
        delta="Este Mes"
    )

with col2:
    st.metric(
        label="Gastos",
        value="$22.99",
        delta="Este Mes"
    )

with col3:
    st.metric(
        label="Saldo Actual",
        value="$-22.99",
        delta="",
        delta_color="inverse"   # para que el valor negativo se muestre en rojo
    )

st.divider()  # Línea separadora

# --- Sección: Transacciones Recientes ---
st.subheader("📋 Transacciones Recientes")

# Datos de ejemplo (basados en la imagen)
transacciones = [
    {"Categoría": "Entretenimiento", "Descripción": "GP", "Monto": "-$11.00", "Fecha": "19 Mar 2026"},
    {"Categoría": "Entretenimiento", "Descripción": "Netflix", "Monto": "-$8.99", "Fecha": "19 Mar 2026"},
    {"Categoría": "Entretenimiento", "Descripción": "Recarga", "Monto": "-$3.00", "Fecha": "19 Mar 2026"},
]

# Convertir a DataFrame para mejor visualización
df_transacciones = pd.DataFrame(transacciones)

# Mostrar tabla con anchura completa y sin índice
st.dataframe(df_transacciones, use_container_width=True, hide_index=True)

# Botón "Ver Todo" (por ahora solo un placeholder)
col_btn, _ = st.columns([1, 5])
with col_btn:
    if st.button("Ver Todo", type="primary"):
        st.info("Funcionalidad en desarrollo: aquí se mostrarán todas las transacciones.")

st.divider()

# --- Secciones inferiores: Ingresos y Gastos ---
col_ingresos, col_gastos = st.columns(2)

with col_ingresos:
    st.subheader("📈 Ingresos")
    st.write("No hay ingresos registrados este mes.")
    # Aquí podrías agregar una lista de ingresos o un gráfico

with col_gastos:
    st.subheader("📉 Gastos")
    st.write("**Total gastado:** $22.99")
    st.write("**Categorías:** Entretenimiento")
    # Puedes agregar más detalles o un gráfico circular

# Opcional: mostrar el total de transacciones al pie
st.caption(f"Últimas actualización: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")