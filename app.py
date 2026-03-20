import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- MAGIA CSS PARA CONVERTIR BOTONES EN TARJETAS ---
st.markdown("""
<style>
/* Ocultar el header por defecto para look de app móvil */
header {visibility: hidden;}

/* Permite múltiples líneas de texto en los botones */
button p {
    white-space: pre-wrap !important;
    text-align: center !important;
    line-height: 1.4 !important;
}

/* 1. Botón SUELDO (Usando 'tertiary') */
button[kind="tertiary"] {
    background-color: #f8f9fa !important;
    border: 2px dashed #007bff !important;
    border-radius: 15px !important;
    padding: 15px !important;
    min-height: 90px !important;
}
button[kind="tertiary"] p {
    color: #007bff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}
button[kind="tertiary"]:hover {
    background-color: #e2eafc !important;
}

/* 2. Botón INGRESOS (Usando 'secondary' -> Verde) */
button[kind="secondary"] {
    background-color: #e8f5e9 !important;
    border: 2px solid #4CAF50 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    min-height: 120px !important;
    box-shadow: 0 4px 6px rgba(76, 175, 80, 0.1) !important;
}
button[kind="secondary"] p {
    color: #2e7d32 !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}
button[kind="secondary"]:hover {
    background-color: #c8e6c9 !important;
}

/* 3. Botón GASTOS (Usando 'primary' -> Rojo) */
button[kind="primary"] {
    background-color: #ffebee !important;
    border: 2px solid #F44336 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    min-height: 120px !important;
    box-shadow: 0 4px 6px rgba(244, 67, 54, 0.1) !important;
}
button[kind="primary"] p {
    color: #c62828 !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}
button[kind="primary"]:hover {
    background-color: #ffcdd2 !important;
}

/* 4. Tarjeta de Saldo Total (HTML puro, no clickeable) */
.total-card {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 8px 15px rgba(0, 123, 255, 0.3);
    margin-top: 15px;
    margin-bottom: 25px;
}
.total-label {
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 5px;
}
.total-value {
    font-size: 48px;
    font-weight: bold;
    margin: 0;
}
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
    # Guardamos la fecha completa en lugar de solo el día
    c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("fecha_pago", "")')
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else ("0" if key == "sueldo_base" else "")

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

# --- PREPARACIÓN DE DATOS ---
df_all = get_data()
sueldo_base = float(get_setting("sueldo_base"))
fecha_pago_db = get_setting("fecha_pago")

# Formatear la fecha para mostrarla de forma legible (ej. 15/03/2026)
if fecha_pago_db == "":
    fecha_mostrar = "Sin fecha"
    fecha_obj_default = datetime.today()
else:
    fecha_obj = datetime.strptime(fecha_pago_db, "%Y-%m-%d").date()
    fecha_mostrar = fecha_obj.strftime("%d/%m/%Y")
    fecha_obj_default = fecha_obj

total_ingresos = df_all[df_all['type'] == 'Ingreso']['amount'].sum() if not df_all.empty else 0.00
total_gastos = df_all[df_all['type'] == 'Gasto']['amount'].sum() if not df_all.empty else 0.00
saldo_total = sueldo_base + total_ingresos - total_gastos

# --- VENTANAS EMERGENTES (DIALOGS) ---
@st.dialog("⚙️ Configurar Sueldo y Fecha de Pago")
def config_dialog():
    nuevo_sueldo = st.number_input("Sueldo Base ($)", min_value=0.0, value=sueldo_base, step=10.0)
    nueva_fecha = st.date_input("Fecha exacta de pago", value=fecha_obj_default)
    
    if st.button("Guardar Datos", use_container_width=True):
        update_setting("sueldo_base", str(nuevo_sueldo))
        update_setting("fecha_pago", nueva_fecha.strftime("%Y-%m-%d"))
        st.rerun()

@st.dialog("🟢 Añadir Ingreso")
def ingreso_dialog():
    monto = st.number_input("Monto del ingreso ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (Ej. Venta, Bono)")
    fecha = st.date_input("Fecha del ingreso", datetime.today())
    
    if st.button("Guardar Ingreso", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Ingreso", "Ingreso", monto, nota)
        st.rerun()

@st.dialog("🔴 Añadir Gasto")
def gasto_dialog():
    categoria = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Entretenimiento", "Salud", "Ropa", "Otros"])
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (opcional)")
    fecha = st.date_input("Fecha del gasto", datetime.today())
    
    if st.button("Guardar Gasto", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Gasto", categoria, monto, nota)
        st.rerun()


# --- INTERFAZ PRINCIPAL ---
st.write("")

# 1. BOTÓN SUPERIOR: Sueldo y Fecha (Abre configuración al hacer clic)
texto_sueldo = f"⚙️ Sueldo Base: ${sueldo_base:,.2f}\n📅 Fecha de Pago: {fecha_mostrar}"
if st.button(texto_sueldo, type="tertiary", use_container_width=True):
    config_dialog()

st.write("")

# 2. BOTONES MEDIOS: Ingresos y Gastos
col1, col2 = st.columns(2)
with col1:
    texto_ingresos = f"↓ INGRESOS\n${total_ingresos:,.2f}"
    if st.button(texto_ingresos, type="secondary", use_container_width=True):
        ingreso_dialog()

with col2:
    texto_gastos = f"↑ GASTOS\n${total_gastos:,.2f}"
    if st.button(texto_gastos, type="primary", use_container_width=True):
        gasto_dialog()

# 3. CUADRO INFERIOR: Saldo Total (Visualización)
st.markdown(f"""
<div class="total-card">
    <div class="total-label">Saldo Total Disponible</div>
    <div class="total-value">${saldo_total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# 4. HISTORIAL RÁPIDO (Opcional, para que veas lo que introdujiste)
if not df_all.empty:
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Últimos movimientos</p>", unsafe_allow_html=True)
    df_recent = df_all.sort_values(by='id', ascending=False).head(3)
    for index, row in df_recent.iterrows():
        color = "#dc3545" if row['type'] == 'Gasto' else "#28a745"
        signo = "-" if row['type'] == 'Gasto' else "+"
        st.markdown(f"""
        <div style="border-bottom: 1px solid #eee; padding: 10px 0; display: flex; justify-content: space-between;">
            <span style="color: #555;">{row['category']} <small>({row['note']})</small></span>
            <span style="color: {color}; font-weight: bold;">{signo}${row['amount']:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
