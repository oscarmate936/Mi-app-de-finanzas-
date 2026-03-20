import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- BASE DE DATOS Y FUNCIONES ---
DB_NAME = 'cashbook.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabla de transacciones
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
    # Tabla de configuraciones (para guardar el sueldo y día de pago)
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Valores por defecto si está vacía
    c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("sueldo_base", "0")')
    c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("dia_pago", "1")')
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "0"

def update_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
    conn.commit()
    conn.close()

def add_transaction(date, t_type, category, amount, note):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO transactions (date, type, category, amount, note) VALUES (?, ?, ?, ?, ?)',
              (date, t_type, category, amount, note))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

init_db()

# --- VENTANAS EMERGENTES (DIALOGS) ---

@st.dialog("⚙️ Configurar Mi Sueldo y Pago")
def config_dialog():
    st.write("Configura tu sueldo base. Este monto será tu punto de partida.")
    sueldo_actual = float(get_setting("sueldo_base"))
    dia_actual = int(get_setting("dia_pago"))
    
    nuevo_sueldo = st.number_input("Sueldo Base ($)", min_value=0.0, value=sueldo_actual, step=10.0)
    nuevo_dia = st.number_input("Día del mes que te pagan (1-31)", min_value=1, max_value=31, value=dia_actual)
    
    if st.button("Guardar Configuración", use_container_width=True):
        update_setting("sueldo_base", str(nuevo_sueldo))
        update_setting("dia_pago", str(nuevo_dia))
        st.success("¡Guardado!")
        st.rerun() # Recarga la app para aplicar cambios

@st.dialog("🔴 Registrar Nuevo Gasto")
def gasto_dialog():
    categoria = st.selectbox("Categoría", [
        "Comida", "Transporte", "Servicios", "Vivienda", 
        "Entretenimiento", "Salud", "Ropa", "Otros"
    ])
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (Ej. Cine, Supermercado)")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar Gasto", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Gasto", categoria, monto, nota)
        st.rerun()

@st.dialog("🟢 Registrar Ingreso Extra")
def ingreso_dialog():
    st.write("Suma ingresos adicionales a tu sueldo base.")
    monto = st.number_input("Monto del ingreso ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (Ej. Venta, Bono, Regalo)")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar Ingreso", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Ingreso", "Ingreso Extra", monto, nota)
        st.rerun()

# --- LÓGICA DE DATOS ---
df_all = get_data()
sueldo_base = float(get_setting("sueldo_base"))
dia_pago = get_setting("dia_pago")

# Cálculos
total_ingresos = df_all[df_all['type'] == 'Ingreso']['amount'].sum() if not df_all.empty else 0.00
total_gastos = df_all[df_all['type'] == 'Gasto']['amount'].sum() if not df_all.empty else 0.00

# El saldo actual es tu Sueldo + Ingresos Extras - Gastos
saldo_actual = sueldo_base + total_ingresos - total_gastos

# --- INTERFAZ PRINCIPAL ---

# 1. Cabecera (Botón de configuración y Saldo superior)
col_top1, col_top2 = st.columns([1, 4])
with col_top1:
    st.write("") # Espaciador
    if st.button("⚙️ Sueldo", help="Configurar Sueldo y Pago"):
        config_dialog()
with col_top2:
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 0;'>${saldo_actual:,.2f}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray; margin-top: 0;'>Saldo Actual (Día de pago: {dia_pago})</p>", unsafe_allow_html=True)

st.write("")

# 2. Tarjetas de Resumen (Ingresos y Gastos)
col_ing, col_gas = st.columns(2)
with col_ing:
    st.success(f"**Ingresos Extras**\n\n### ${total_ingresos:,.2f}")
with col_gas:
    st.error(f"**Gastos Totales**\n\n### ${total_gastos:,.2f}")

# 3. Tarjeta Azul Principal
st.markdown(f"""
<div style="background-color: #007bff; color: white; padding: 25px; border-radius: 15px; margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <p style="margin: 0; font-size: 16px; opacity: 0.9;">Mi Saldo (Sueldo incluido)</p>
    <h1 style="margin: 0; font-size: 42px;">${saldo_actual:,.2f}</h1>
</div>
""", unsafe_allow_html=True)

# 4. Transacciones Recientes
st.subheader("Transacciones Recientes")
if not df_all.empty:
    # Mostrar las últimas 5 transacciones
    df_recent = df_all.sort_values(by='id', ascending=False).head(5)
    for index, row in df_recent.iterrows():
        t_date = pd.to_datetime(row['date']).strftime("%d %b")
        if row['type'] == 'Gasto':
            color = "#dc3545" # Rojo
            signo = "-"
        else:
            color = "#28a745" # Verde
            signo = "+"
            
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: bold; font-size: 16px;">{row['category']}</div>
                <div style="color: gray; font-size: 13px;">{row['note']} • {t_date}</div>
            </div>
            <div style="color: {color}; font-weight: bold; font-size: 18px;">
                {signo}${row['amount']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No hay transacciones registradas aún.")

st.write("---")

# 5. Botones de Acción (Reemplazan la barra lateral)
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🟢 + Ingreso Extra", use_container_width=True):
        ingreso_dialog()
with col_btn2:
    if st.button("🔴 - Registrar Gasto", use_container_width=True):
        gasto_dialog()

