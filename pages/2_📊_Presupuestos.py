import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import datetime
from db_manager import init_db, get_transacciones, set_presupuesto, get_presupuestos

st.set_page_config(page_title="Presupuestos", page_icon="📊", layout="wide")
init_db()

st.title("📊 Control de Presupuestos")
st.markdown("Establece límites mensuales y visualiza cuánto puedes gastar al estilo de las mejores apps premium.")

# --- 1. CONFIGURADOR DE PRESUPUESTOS ---
with st.expander("⚙️ Configurar Límite Mensual", expanded=False):
    col_cat, col_lim, col_btn = st.columns([2, 2, 1])
    
    with col_cat:
        categorias_gasto = ["🛒 Supermercado", "🚗 Transporte", "⚡ Servicios", "🍔 Restaurantes", "🎬 Ocio", "🏠 Vivienda", "Otros"]
        cat_seleccionada = st.selectbox("Categoría a limitar", categorias_gasto)
    with col_lim:
        limite_monto = st.number_input("Límite Mensual ($)", min_value=1.0, format="%.2f", step=10.0)
    with col_btn:
        st.write("") # Espaciado
        st.write("")
        if st.button("Guardar Límite", use_container_width=True, type="primary"):
            set_presupuesto(cat_seleccionada, limite_monto)
            st.success("¡Límite guardado!")
            st.rerun()

st.divider()

# --- 2. EL PANEL VISUAL (Estilo Budge) ---
st.subheader("Tu Progreso este Mes")

# Obtener datos de este mes
df_trans = get_transacciones()
df_presupuestos = get_presupuestos()

# Filtrar transacciones solo por el mes y año actual
mes_actual = datetime.datetime.now().strftime("%Y-%m")

if not df_trans.empty:
    # Extraer el mes de la fecha (YYYY-MM)
    df_trans['mes'] = df_trans['fecha'].str[:7]
    df_gastos_mes = df_trans[(df_trans['mes'] == mes_actual) & (df_trans['tipo'] == 'Gasto')]
else:
    df_gastos_mes = pd.DataFrame(columns=['categoria', 'monto'])

if df_presupuestos.empty:
    st.info("Aún no has configurado ningún límite. Usa el panel de arriba para empezar.")
else:
    # Recorrer cada presupuesto y dibujar su tarjeta
    for index, row in df_presupuestos.iterrows():
        categoria = row['categoria']
        limite = row['limite']
        
        # Calcular cuánto se ha gastado en esta categoría este mes
        gastado = df_gastos_mes[df_gastos_mes['categoria'] == categoria]['monto'].sum() if not df_gastos_mes.empty else 0.0
        disponible = limite - gastado
        
        # Calcular porcentaje para la barra (asegurando que no pase de 100 para que Streamlit no dé error)
        porcentaje = (gastado / limite) if limite > 0 else 1.0
        porcentaje_barra = min(porcentaje, 1.0)
        
        # UI de la Tarjeta
        col_texto, col_numeros = st.columns([3, 1])
        
        with col_texto:
            st.markdown(f"**{categoria}**")
        with col_numeros:
            st.markdown(f"<div style='text-align: right;'>${gastado:,.2f} / ${limite:,.2f}</div>", unsafe_allow_html=True)
            
        # Barra de progreso y mensajes de alerta
        st.progress(porcentaje_barra)
        
        if disponible > 0:
            if porcentaje < 0.75:
                st.markdown(f"*:green[Quedan ${disponible:,.2f} disponibles]*")
            else:
                st.markdown(f"*:orange[¡Cuidado! Solo quedan ${disponible:,.2f}]*")
        else:
            sobregiro = gastado - limite
            st.markdown(f"*:red[Te has pasado por ${sobregiro:,.2f}]*")
            
        st.write("") # Espacio entre tarjetas