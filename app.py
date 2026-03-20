import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Libro de Caja", page_icon="💰", layout="wide")

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('cashbook.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            category TEXT,
            amount REAL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(date, t_type, category, amount, note):
    conn = sqlite3.connect('cashbook.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions (date, type, category, amount, note) VALUES (?, ?, ?, ?, ?)',
              (date, t_type, category, amount, note))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('cashbook.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def delete_transaction(t_id):
    conn = sqlite3.connect('cashbook.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (t_id,))
    conn.commit()
    conn.close()

# Inicializar base de datos
init_db()

# --- INTERFAZ DE USUARIO ---
st.title("💰 Mi Libro de Caja Personal")

# BARRA LATERAL: Formulario de ingreso
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Fecha", datetime.today())
        t_type = st.radio("Tipo", ["Gasto", "Ingreso"])
        
        # Categorías dinámicas según el tipo
        if t_type == "Gasto":
            category = st.selectbox("Categoría", ["Comida", "Transporte", "Vivienda", "Servicios", "Entretenimiento", "Salud", "Otros"])
        else:
            category = st.selectbox("Categoría", ["Salario", "Negocio", "Inversiones", "Otros"])
            
        amount = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
        note = st.text_input("Nota / Descripción")
        
        submit = st.form_submit_button("Guardar Registro")
        
        if submit:
            add_transaction(date.strftime("%Y-%m-%d"), t_type, category, amount, note)
            st.success("¡Registro guardado con éxito!")

# --- PANEL PRINCIPAL: Datos y Gráficos ---
df = get_data()

if not df.empty:
    # Convertir monto a numérico por si acaso
    df['amount'] = pd.to_numeric(df['amount'])
    
    # Calcular métricas
    total_ingresos = df[df['type'] == 'Ingreso']['amount'].sum()
    total_gastos = df[df['type'] == 'Gasto']['amount'].sum()
    saldo_actual = total_ingresos - total_gastos

    # Mostrar métricas destacadas
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Actual", f"${saldo_actual:,.2f}")
    col2.metric("Total Ingresos", f"${total_ingresos:,.2f}")
    col3.metric("Total Gastos", f"${total_gastos:,.2f}")
    
    st.markdown("---")
    
    # Mostrar Gráficos y Tabla en columnas
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        st.subheader("Distribución de Gastos")
        df_gastos = df[df['type'] == 'Gasto']
        if not df_gastos.empty:
            fig = px.pie(df_gastos, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay gastos registrados para graficar.")
            
    with col_table:
        st.subheader("Historial de Transacciones")
        # Mostrar el dataframe ordenado por fecha de forma descendente
        st.dataframe(
            df.sort_values(by='id', ascending=False).drop(columns=['id']), 
            use_container_width=True,
            hide_index=True
        )
        
        # Pequeño sistema para eliminar registros si te equivocas
        st.write("¿Eliminar un registro?")
        del_id = st.selectbox("Selecciona el ID a eliminar", df['id'].tolist())
        if st.button("Eliminar Registro"):
            delete_transaction(del_id)
            st.rerun() # Recargar la página para actualizar los datos

else:
    st.info("👋 ¡Bienvenido a tu Libro de Caja! Utiliza el menú de la izquierda para registrar tu primer ingreso o gasto.")
