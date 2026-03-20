import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- MAGIA CSS PARA LOS BOTONES ---
st.markdown("""
<style>
/* 1. Estilo para el botón verde (Ingresos) usando 'secondary' */
button[kind="secondary"] {
    background-color: #4CAF50 !important;
    border-color: #4CAF50 !important;
    border-radius: 12px !important;
    height: 55px !important;
    box-shadow: 0 4px 6px rgba(76, 175, 80, 0.2) !important;
}
button[kind="secondary"] p {
    color: white !important;
    font-weight: 600 !important;
    font-size: 17px !important;
}
button[kind="secondary"]:hover {
    background-color: #43a047 !important;
    border-color: #43a047 !important;
}

/* 2. Estilo para el botón rojo (Gastos) usando 'primary' */
button[kind="primary"] {
    background-color: #F44336 !important;
    border-color: #F44336 !important;
    border-radius: 12px !important;
    height: 55px !important;
    box-shadow: 0 4px 6px rgba(244, 67, 54, 0.2) !important;
}
button[kind="primary"] p {
    color: white !important;
    font-weight: 600 !important;
    font-size: 17px !important;
}
button[kind="primary"]:hover {
    background-color: #e53935 !important;
    border-color: #e53935 !important;
}

/* Ocultar el header por defecto de Streamlit para que parezca app móvil */
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y FUNCIONES ---
DB_NAME = 'cashbook.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
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
@st.dialog("⚙️ Configurar Mi Sueldo")
def config_dialog():
    sueldo_actual = float(get_setting("sueldo_base"))
    dia_actual = int(get_setting("dia_pago"))
    
    nuevo_sueldo = st.number_input("Sueldo Base ($)", min_value=0.0, value=sueldo_actual, step=10.0)
    nuevo_dia = st.number_input("Día de pago (1-31)", min_value=1, max_value=31, value=dia_actual)
    
    if st.button("Guardar", use_container_width=True):
        update_setting("sueldo_base", str(nuevo_sueldo))
        update_setting("dia_pago", str(nuevo_dia))
        st.rerun()

@st.dialog("🔴 Registrar Gasto")
def gasto_dialog():
    categoria = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Entretenimiento", "Salud", "Ropa", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (opcional)")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar Gasto", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Gasto", categoria, monto, nota)
        st.rerun()

@st.dialog("🟢 Registrar Ingreso Extra")
def ingreso_dialog():
    monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (Ej. Venta, Regalo)")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar Ingreso", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Ingreso", "Ingreso Extra", monto, nota)
        st.rerun()

# --- LÓGICA DE DATOS ---
df_all = get_data()
sueldo_base = float(get_setting("sueldo_base"))
dia_pago = get_setting("dia_pago")

total_ingresos = df_all[df_all['type'] == 'Ingreso']['amount'].sum() if not df_all.empty else 0.00
total_gastos = df_all[df_all['type'] == 'Gasto']['amount'].sum() if not df_all.empty else 0.00
saldo_actual = sueldo_base + total_ingresos - total_gastos

# --- INTERFAZ PRINCIPAL ---
st.write("") 

# 1. Cabecera
col_top1, col_top2 = st.columns([1, 4])
with col_top1:
    # Usamos type="tertiary" para que no le afecten los colores verde/rojo
    if st.button("⚙️ Sueldo", type="tertiary"):
        config_dialog()
with col_top2:
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 0;'>${saldo_actual:,.2f}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray; margin-top: 0;'>Día de pago: {dia_pago}</p>", unsafe_allow_html=True)

st.write("")

# 2. Tarjetas de Resumen
col_ing, col_gas = st.columns(2)
with col_ing:
    st.markdown(f"<div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;'><p style='color: gray; margin: 0; font-size: 14px;'>Ingresos Extras</p><h3 style='margin: 0; color: #4CAF50;'>${total_ingresos:,.2f}</h3></div>", unsafe_allow_html=True)
with col_gas:
    st.markdown(f"<div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;'><p style='color: gray; margin: 0; font-size: 14px;'>Gastos</p><h3 style='margin: 0; color: #F44336;'>${total_gastos:,.2f}</h3></div>", unsafe_allow_html=True)

# 3. Tarjeta Azul
st.markdown(f"""
<div style="background-color: #007bff; color: white; padding: 25px; border-radius: 15px; margin-top: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,123,255,0.3);">
    <p style="margin: 0; font-size: 16px; opacity: 0.9;">Saldo Actual</p>
    <h1 style="margin: 0; font-size: 42px;">${saldo_actual:,.2f}</h1>
</div>
""", unsafe_allow_html=True)

# 4. Transacciones Recientes
st.markdown("**Transacciones Recientes**")
if not df_all.empty:
    df_recent = df_all.sort_values(by='id', ascending=False).head(5)
    for index, row in df_recent.iterrows():
        t_date = pd.to_datetime(row['date']).strftime("%d %b %Y")
        if row['type'] == 'Gasto':
            color = "#dc3545"
            signo = "-"
            icono = "↑"
        else:
            color = "#28a745"
            signo = "+"
            icono = "↓"
            
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="color: {color}; background-color: {color}15; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-weight: bold;">{icono}</div>
                <div>
                    <div style="font-weight: 600; font-size: 15px; color: #333;">{row['category']}</div>
                    <div style="color: #888; font-size: 13px;">{row['note'] or 'Sin descripción'} • {t_date}</div>
                </div>
            </div>
            <div style="color: {color}; font-weight: bold; font-size: 16px;">
                {signo}${row['amount']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No hay transacciones registradas aún.")

st.write("---")

# 5. BOTONES ESTILO APP
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    # Este usa type="secondary", el CSS lo vuelve VERDE
    if st.button("↓ Ingresos", type="secondary", use_container_width=True):
        ingreso_dialog()
with col_btn2:
    # Este usa type="primary", el CSS lo vuelve ROJO
    if st.button("↑ Gastos", type="primary", use_container_width=True):
        gasto_dialog()
