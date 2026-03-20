import streamlit as st
import pandas as pd
import plotly.express as px
from db_manager import init_db, get_transacciones, get_config, update_config

st.set_page_config(page_title="Gestor Financiero Pro", page_icon="💼", layout="wide")
init_db()

# Cargar configuración del usuario
config = get_config()

st.title("💼 Mi Resumen Financiero")
st.markdown("Control total de tu patrimonio y flujo de caja.")

# --- PANEL DE CONFIGURACIÓN DE SUELDO ---
# Se abre automáticamente si el sueldo es 0 (primera vez)
with st.expander("⚙️ Mi Sueldo y Fecha de Pago", expanded=(config['salario'] == 0)):
    st.markdown("Configura tu ingreso principal. Los ingresos adicionales que registres se sumarán a este monto.")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        nuevo_salario = st.number_input("Sueldo Mensual Fijo ($)", min_value=0.0, value=config['salario'], step=100.0)
    with col2:
        nuevo_dia = st.number_input("Día de Pago (1-31)", min_value=1, max_value=31, value=config['dia_pago'], step=1)
    with col3:
        st.write("")
        st.write("")
        if st.button("Guardar Datos", use_container_width=True, type="primary"):
            update_config(nuevo_salario, nuevo_dia)
            st.success("¡Configuración guardada!")
            st.rerun()

st.divider()

# --- CÁLCULO DE SALDOS ---
df = get_transacciones()
if not df.empty:
    ingresos_extra = df[df['tipo'] == 'Ingreso']['monto'].sum()
    gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
else:
    ingresos_extra, gastos = 0.0, 0.0

# MATEMÁTICA PRO: Sueldo + Ingresos Extras - Gastos
saldo_actual = config['salario'] + ingresos_extra - gastos

# --- MÉTRICAS PREMIUM ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

col_m1.metric("💰 Saldo Disponible", f"${saldo_actual:,.2f}", f"Sueldo Base: ${config['salario']:,.0f}")
col_m2.metric("💵 Ingresos Extras", f"${ingresos_extra:,.2f}")
col_m3.metric("📉 Gastos Realizados", f"${gastos:,.2f}")

# Calcular porcentaje gastado del total (Sueldo + Extras)
ingreso_total = config['salario'] + ingresos_extra
porcentaje_gasto = (gastos / ingreso_total) * 100 if ingreso_total > 0 else 0
col_m4.metric("🔥 Dinero Gastado", f"{porcentaje_gasto:.1f}%", delta_color="inverse")

st.divider()

# --- GRÁFICOS INTERACTIVOS (PLOTLY) ---
st.subheader("📊 Análisis Visual")
if not df.empty and gastos > 0:
    col_graf_1, col_graf_2 = st.columns(2)
    
    with col_graf_1:
        df_gastos = df[df['tipo'] == 'Gasto']
        if not df_gastos.empty:
            gastos_por_categoria = df_gastos.groupby('categoria')['monto'].sum().reset_index()
            fig_dona = px.pie(gastos_por_categoria, values='monto', names='categoria', hole=0.5, 
                              title="Distribución de tus Gastos", color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_dona.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_dona, use_container_width=True)

    with col_graf_2:
        resumen_df = df.groupby('tipo')['monto'].sum().reset_index()
        fig_barras = px.bar(resumen_df, x='tipo', y='monto', color='tipo', title="Ingresos Extras vs Gastos",
                            text_auto='.2s', color_discrete_map={'Ingreso': '#2ECC71', 'Gasto': '#E74C3C'})
        fig_barras.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_barras, use_container_width=True)
else:
    st.info("Añade algunos movimientos para ver tus gráficos.")
