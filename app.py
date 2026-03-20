import streamlit as st
import pandas as pd
import plotly.express as px
from db_manager import init_db, get_transacciones

# Configuración de la página
st.set_page_config(
    page_title="Gestor Financiero Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

st.title("🏠 Dashboard Principal")
st.markdown("Bienvenido a tu resumen financiero interactivo.")
st.divider()

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
    st.metric(label="📈 Ingresos Totales", value=f"${ingresos:,.2f}")
with col3:
    st.metric(label="📉 Gastos Totales", value=f"${gastos:,.2f}")

st.divider()

# --- SECCIÓN DE GRÁFICOS (PLOTLY) ---
st.subheader("📊 Análisis Visual")

if not df.empty:
    # Crear dos columnas para los gráficos en pantallas grandes
    # En móviles como el tuyo, Streamlit las apilará inteligentemente
    col_graf_1, col_graf_2 = st.columns(2)
    
    with col_graf_1:
        # 1. Gráfico de Dona: Distribución de Gastos
        df_gastos = df[df['tipo'] == 'Gasto']
        if not df_gastos.empty:
            gastos_por_categoria = df_gastos.groupby('categoria')['monto'].sum().reset_index()
            fig_dona = px.pie(
                gastos_por_categoria, 
                values='monto', 
                names='categoria', 
                hole=0.5, # Esto lo convierte en dona
                title="¿En qué estoy gastando?",
                color_discrete_sequence=px.colors.sequential.Greens_r # Paleta que combina con tu tema
            )
            # Hacer el fondo del gráfico transparente para que se funda con tu tema oscuro
            fig_dona.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_dona, use_container_width=True)
        else:
            st.info("No hay gastos registrados para mostrar la distribución.")

    with col_graf_2:
        # 2. Gráfico de Barras: Ingresos vs Gastos
        resumen_df = df.groupby('tipo')['monto'].sum().reset_index()
        fig_barras = px.bar(
            resumen_df, 
            x='tipo', 
            y='monto', 
            color='tipo',
            title="Comparativa de Flujo",
            text_auto='.2s', # Muestra el número sobre la barra
            color_discrete_map={'Ingreso': '#2ECC71', 'Gasto': '#E74C3C'} # Verde para ingreso, Rojo para gasto
        )
        fig_barras.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_barras, use_container_width=True)

else:
    st.info("Añade algunos movimientos para visualizar tus gráficos.")

st.divider()

# --- SECCIÓN DE VISTA PREVIA ---
st.subheader("Últimos Movimientos")
if not df.empty:
    st.dataframe(df.head(5), use_container_width=True, hide_index=True)