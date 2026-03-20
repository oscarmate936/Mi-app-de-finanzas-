import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- MAGIA CSS ---
st.markdown("""
<style>
header {visibility: hidden;}

button p {
    white-space: pre-wrap !important;
    text-align: center !important;
    line-height: 1.4 !important;
}

/* 1. Botón SUELDO (tertiary) */
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

/* 2. Botón INGRESOS (secondary -> Verde) */
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

/* 3. Botón GASTOS (primary -> Rojo) */
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

/* Tarjeta Saldo Total */
.total-card {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 8px 15px rgba(0, 123, 255, 0.3);
    margin-top: 15px;
    margin-bottom: 20px;
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

# Asegurarnos de que el sueldo sea un número válido
try:
    sueldo_base = float(get_setting("sueldo_base"))
except ValueError:
    sueldo_base = 0.0

fecha_pago_db = get_setting("fecha_pago")

try:
    if fecha_pago_db:
        fecha_obj = datetime.strptime(fecha_pago_db, "%Y-%m-%d").date()
        fecha_mostrar = fecha_obj.strftime("%d/%m/%Y")
        fecha_obj_default = fecha_obj
    else:
        fecha_mostrar = "Sin fecha configurada"
        fecha_obj_default = datetime.today()
except ValueError:
    fecha_mostrar = "Sin fecha configurada"
    fecha_obj_default = datetime.today()

total_ingresos = df_all[df_all['type'] == 'Ingreso']['amount'].sum() if not df_all.empty else 0.00
total_gastos = df_all[df_all['type'] == 'Gasto']['amount'].sum() if not df_all.empty else 0.00
saldo_total = sueldo_base + total_ingresos - total_gastos

# --- VENTANAS EMERGENTES (DIALOGS) ---
@st.dialog("⚙️ Configurar Sueldo y Fecha")
def config_dialog():
    nuevo_sueldo = st.number_input("Sueldo Base ($)", min_value=0.0, value=sueldo_base, step=10.0)
    nueva_fecha = st.date_input("Fecha de pago", value=fecha_obj_default)
    
    if st.button("Guardar Datos", use_container_width=True):
        update_setting("sueldo_base", str(nuevo_sueldo))
        update_setting("fecha_pago", nueva_fecha.strftime("%Y-%m-%d"))
        st.rerun()

@st.dialog("🟢 Añadir Ingreso")
def ingreso_dialog():
    monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción (Ej. Venta, Bono)")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Ingreso", "Ingreso", monto, nota)
        st.rerun()

@st.dialog("🔴 Añadir Gasto")
def gasto_dialog():
    categoria = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Vivienda", "Entretenimiento", "Salud", "Ropa", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
    nota = st.text_input("Descripción")
    fecha = st.date_input("Fecha", datetime.today())
    
    if st.button("Guardar", use_container_width=True):
        add_transaction(fecha.strftime("%Y-%m-%d"), "Gasto", category=categoria, amount=monto, note=nota)
        st.rerun()

# ==========================================
# ESTRUCTURA DE PESTAÑAS (TABS)
# ==========================================
tab1, tab2 = st.tabs(["🏠 Inicio", "📊 Historial y Gráficos"])

# --- PESTAÑA 1: INICIO (BOTONES Y SALDO) ---
with tab1:
    st.write("")
    
    # Botón Sueldo Superior
    texto_sueldo = f"⚙️ Sueldo Base: ${sueldo_base:,.2f}\n📅 Fecha de Pago: {fecha_mostrar}"
    if st.button(texto_sueldo, type="tertiary", use_container_width=True):
        config_dialog()

    st.write("")
    
    # Botones Ingresos/Gastos (gap="small" asegura que estén pegados)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        texto_ingresos = f"↓ INGRESOS\n${total_ingresos:,.2f}"
        if st.button(texto_ingresos, type="secondary", use_container_width=True):
            ingreso_dialog()

    with col2:
        texto_gastos = f"↑ GASTOS\n${total_gastos:,.2f}"
        if st.button(texto_gastos, type="primary", use_container_width=True):
            gasto_dialog()

    # Cuadro de Saldo Total
    st.markdown(f"""
    <div class="total-card">
        <div style="font-size: 16px; opacity: 0.9;">Saldo Total Disponible</div>
        <div class="total-value">${saldo_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Historial rápido (solo los 3 más recientes)
    if not df_all.empty:
        st.markdown("**Últimos 3 movimientos**")
        df_recent = df_all.sort_values(by='id', ascending=False).head(3)
        for index, row in df_recent.iterrows():
            color = "#dc3545" if row['type'] == 'Gasto' else "#28a745"
            signo = "-" if row['type'] == 'Gasto' else "+"
            st.markdown(f"""
            <div style="border-bottom: 1px solid #eee; padding: 10px 0; display: flex; justify-content: space-between;">
                <span style="color: #555; font-weight: 500;">{row['category']} <span style="color: #999; font-size: 13px;">({row['note']})</span></span>
                <span style="color: {color}; font-weight: bold;">{signo}${row['amount']:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

# --- PESTAÑA 2: HISTORIAL Y GRÁFICOS ---
with tab2:
    st.header("Análisis de Gastos")
    
    if not df_all.empty:
        # Convertir columna de fecha a formato datetime de Pandas para poder agruparla
        df_all['date'] = pd.to_datetime(df_all['date'])
        
        # Filtrar solo los gastos para los gráficos
        df_gastos = df_all[df_all['type'] == 'Gasto'].copy()
        
        if not df_gastos.empty:
            # Crear columnas extra para agrupar por semana y mes
            df_gastos['Día'] = df_gastos['date'].dt.date
            df_gastos['Semana'] = df_gastos['date'].dt.strftime('%Y - Sem %U')
            df_gastos['Mes'] = df_gastos['date'].dt.strftime('%Y - %B')
            
            # --- SECCIÓN DE GRÁFICOS ---
            st.subheader("📊 Mis Gastos en el Tiempo")
            
            # Sub-pestañas internas solo para cambiar de gráfico rápidamente
            graf_dia, graf_sem, graf_mes = st.tabs(["Por Día", "Por Semana", "Por Mes"])
            
            with graf_dia:
                gastos_diarios = df_gastos.groupby('Día')['amount'].sum().reset_index()
                fig1 = px.bar(gastos_diarios, x='Día', y='amount', text_auto='.2f', color_discrete_sequence=['#F44336'])
                fig1.update_layout(xaxis_title="Día", yaxis_title="Monto ($)", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig1, use_container_width=True)
                
            with graf_sem:
                gastos_semanales = df_gastos.groupby('Semana')['amount'].sum().reset_index()
                fig2 = px.bar(gastos_semanales, x='Semana', y='amount', text_auto='.2f', color_discrete_sequence=['#FF9800'])
                fig2.update_layout(xaxis_title="Semana", yaxis_title="Monto ($)", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig2, use_container_width=True)
                
            with graf_mes:
                gastos_mensuales = df_gastos.groupby('Mes')['amount'].sum().reset_index()
                fig3 = px.bar(gastos_mensuales, x='Mes', y='amount', text_auto='.2f', color_discrete_sequence=['#9C27B0'])
                fig3.update_layout(xaxis_title="Mes", yaxis_title="Monto ($)", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig3, use_container_width=True)

            st.write("---")
            
            # Gráfico de Categorías (Extra, muy útil)
            st.subheader("🥧 ¿En qué gasto más?")
            gastos_cat = df_gastos.groupby('category')['amount'].sum().reset_index()
            fig_pie = px.pie(gastos_cat, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.info("No tienes gastos registrados para mostrar en los gráficos.")

        st.write("---")
        
        # --- SECCIÓN DE HISTORIAL COMPLETO ---
        st.subheader("📝 Historial Completo")
        
        # Preparamos el dataframe para mostrarlo bonito
        df_mostrar = df_all.copy()
        df_mostrar['Fecha'] = df_mostrar['date'].dt.strftime('%d/%m/%Y')
        df_mostrar['Tipo'] = df_mostrar['type']
        df_mostrar['Categoría'] = df_mostrar['category']
        df_mostrar['Monto ($)'] = df_mostrar['amount']
        df_mostrar['Nota'] = df_mostrar['note']
        
        # Mostrar la tabla interactiva ordenando los más nuevos primero
        st.dataframe(
            df_mostrar[['Fecha', 'Tipo', 'Categoría', 'Monto ($)', 'Nota']].sort_values(by='Fecha', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Aún no tienes movimientos. ¡Ve a la pestaña de 'Inicio' para registrar tu primer ingreso o gasto!")
