import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import datetime
from db_manager import add_transaccion, get_transacciones, init_db, get_categorias, add_categoria, delete_transaccion

st.set_page_config(page_title="Movimientos", page_icon="💸", layout="wide")
init_db()

st.title("💸 Gestión de Movimientos")
st.markdown("Añade transacciones, elimina errores o crea nuevas categorías.")

# --- DISEÑO PROFESIONAL CON PESTAÑAS (TABS) ---
tab_registro, tab_historial, tab_categorias = st.tabs(["➕ Registrar", "📜 Historial y Edición", "🏷️ Mis Categorías"])

# ----------------- PESTAÑA 1: REGISTRAR -----------------
with tab_registro:
    st.subheader("Nuevo Movimiento")
    # El tipo se elige fuera del formulario para actualizar las categorías dinámicamente
    tipo_movimiento = st.radio("Tipo de Movimiento", ["Gasto", "Ingreso"], horizontal=True)
    categorias_dinamicas = get_categorias(tipo_movimiento)
    
    with st.form("form_movimiento", clear_on_submit=True):
        fecha = st.date_input("Fecha", datetime.date.today())
        categoria = st.selectbox("Categoría", categorias_dinamicas)
        monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
        descripcion = st.text_input("Descripción (Opcional)")
        
        if st.form_submit_button("Guardar Movimiento", type="primary"):
            add_transaccion(fecha.strftime("%Y-%m-%d"), tipo_movimiento, categoria, monto, descripcion)
            st.success("¡Movimiento guardado con éxito!")
            st.rerun()

# ----------------- PESTAÑA 2: HISTORIAL Y BORRADO -----------------
with tab_historial:
    df = get_transacciones()
    
    if not df.empty:
        # Tabla estilizada
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "ID",
                "monto": st.column_config.NumberColumn(format="$%.2f")
            }
        )
        
        st.divider()
        st.subheader("🗑️ Eliminar un Movimiento")
        st.markdown("¿Te equivocaste? Selecciona el movimiento que deseas borrar.")
        
        # Diccionario para que el menú desplegable sea legible
        opciones = {row['id']: f"{row['fecha']} | {row['categoria']} | ${row['monto']} | {row['descripcion']}" for index, row in df.iterrows()}
        
        col_del_1, col_del_2 = st.columns([3, 1])
        with col_del_1:
            trans_a_borrar = st.selectbox("Selecciona el registro:", options=list(opciones.keys()), format_func=lambda x: opciones[x])
        with col_del_2:
            st.write("")
            st.write("")
            if st.button("Eliminar Registro", type="primary"):
                delete_transaccion(trans_a_borrar)
                st.error("Registro eliminado correctamente.")
                st.rerun()
    else:
        st.info("No tienes movimientos registrados en el historial.")

# ----------------- PESTAÑA 3: CREAR CATEGORÍAS -----------------
with tab_categorias:
    st.subheader("Crear Categoría Personalizada")
    st.markdown("Añade tus propias categorías. Te sugerimos usar Emojis (ej: 🎮 Videojuegos, 🐶 Mascota).")
    
    with st.form("form_cat", clear_on_submit=True):
        nuevo_tipo = st.selectbox("¿Es un gasto o un ingreso?", ["Gasto", "Ingreso"])
        nueva_cat = st.text_input("Nombre de la nueva categoría")
        
        if st.form_submit_button("Guardar Categoría"):
            if nueva_cat.strip() == "":
                st.warning("El nombre no puede estar vacío.")
            else:
                add_categoria(nueva_cat, nuevo_tipo)
                st.success(f"¡Categoría '{nueva_cat}' añadida!")
                st.rerun()
