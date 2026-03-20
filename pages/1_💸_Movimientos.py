import sys
import os
# --- CORRECCIÓN DE IMPORTACIÓN ---
# Agregamos la ruta raíz al sistema para que Python encuentre la carpeta 'utils'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.db_manager import add_transaccion, get_transacciones
import datetime

st.set_page_config(page_title="Movimientos", page_icon="💸", layout="wide")

st.title("💸 Registro de Movimientos")
st.markdown("Añade tus ingresos y gastos aquí.")

# Dividimos la pantalla en dos columnas
col_form, col_tabla = st.columns([1, 2])

# --- COLUMNA 1: FORMULARIO ---
with col_form:
    st.subheader("Nuevo Movimiento")
    with st.form("form_movimiento", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
        fecha = st.date_input("Fecha", datetime.date.today())
        
        # Categorías dinámicas según el tipo
        if tipo == "Gasto":
            categorias = ["🛒 Supermercado", "🚗 Transporte", "⚡ Servicios", "🍔 Restaurantes", "🎬 Ocio", "🏠 Vivienda", "Otros"]
        else:
            categorias = ["💼 Salario", "📈 Inversiones", "🎁 Regalo", "Otros"]
            
        categoria = st.selectbox("Categoría", categorias)
        monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
        descripcion = st.text_input("Descripción (Opcional)")
        
        submitted = st.form_submit_button("Guardar Movimiento", type="primary")
        
        if submitted:
            add_transaccion(fecha.strftime("%Y-%m-%d"), tipo, categoria, monto, descripcion)
            st.success("¡Movimiento guardado con éxito!")
            st.rerun() # Recarga la página para actualizar la tabla

# --- COLUMNA 2: TABLA COMPLETA ---
with col_tabla:
    st.subheader("Historial Completo")
    df = get_transacciones()
    
    if not df.empty:
        # Filtro de búsqueda básico
        busqueda = st.text_input("🔍 Buscar por descripción o categoría...")
        if busqueda:
            df = df[df['descripcion'].str.contains(busqueda, case=False, na=False) | 
                    df['categoria'].str.contains(busqueda, case=False, na=False)]
            
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "monto": st.column_config.NumberColumn(format="$%.2f")
            }
        )
    else:
        st.write("No hay movimientos para mostrar.")
