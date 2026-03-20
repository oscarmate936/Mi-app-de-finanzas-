import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from datetime import date
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cash Book", page_icon="💰", layout="centered")

# --- ESTILOS CSS PERSONALIZADOS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Crear archivo CSS básico para la dashboard
css_style = """
<style>
/* Global styles */
body {
    background-color: #f8f9fa;
    color: #333;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] {
    background-color: transparent;
}
[data-testid="stSidebar"] {
    background-color: #ffffff;
}

/* Card styles */
.cashbook-card {
    background-color: white;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 25px;
    margin-bottom: 25px;
    display: flex;
    flex-direction: column;
}

/* Header style */
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0 30px 0;
}
.header-profile-icon {
    font-size: 24px;
    color: #007bff;
    background-color: rgba(0,123,255,0.1);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.header-balance-container {
    text-align: center;
}
.header-balance-value {
    font-size: 26px;
    font-weight: 700;
}
.header-month-value {
    font-size: 16px;
    color: #777;
    margin-top: 5px;
}
.header-arrow-icon {
    font-size: 18px;
    color: #555;
}

/* Summary cards */
.summary-container {
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
}
.summary-card {
    flex: 1;
    background-color: white;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 20px;
    display: flex;
    gap: 15px;
    align-items: center;
}
.icon-container {
    width: 45px;
    height: 45px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.icon-container.income {
    background-color: #d4edda;
    color: #155724;
}
.icon-container.expense {
    background-color: #f8d7da;
    color: #721c24;
}
.summary-text-container {
    display: flex;
    flex-direction: column;
}
.summary-label {
    font-size: 15px;
    color: #777;
}
.summary-value {
    font-size: 22px;
    font-weight: 700;
    margin: 5px 0;
}
.summary-period {
    font-size: 14px;
    color: #999;
}

/* Blue current balance card */
.blue-balance-card {
    background-color: #007bff;
    color: white;
    border-radius: 20px;
    box-shadow: 0 6px 16px rgba(0, 123, 255, 0.2);
    padding: 30px;
    margin-bottom: 30px;
    display: flex;
    flex-direction: column;
}
.blue-card-label {
    font-size: 16px;
    font-weight: 400;
    margin-bottom: 10px;
}
.blue-card-value {
    font-size: 40px;
    font-weight: 700;
}

/* Recent transactions section */
.recent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.recent-title {
    font-size: 18px;
    font-weight: 600;
}
.view-all-link {
    color: #007bff;
    text-decoration: none;
    font-size: 14px;
}
.view-all-link:hover {
    text-decoration: underline;
}

/* Transaction entries */
.transaction-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}
.transaction-entry {
    background-color: white;
    border-radius: 18px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    padding: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.transaction-left {
    display: flex;
    align-items: center;
    gap: 15px;
}
.transaction-icon-box {
    width: 45px;
    height: 45px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}
.transaction-icon-box.expense {
    background-color: rgba(220, 53, 69, 0.1);
    color: #dc3545;
}
.transaction-icon-box.income {
    background-color: rgba(40, 167, 69, 0.1);
    color: #28a745;
}
.transaction-text-container {
    display: flex;
    flex-direction: column;
}
.transaction-category {
    font-size: 16px;
    font-weight: 600;
}
.transaction-note {
    font-size: 14px;
    color: #777;
    margin-top: 2px;
}
.transaction-right {
    text-align: right;
    display: flex;
    flex-direction: column;
}
.transaction-amount {
    font-size: 16px;
    font-weight: 700;
}
.transaction-amount.expense {
    color: #dc3545;
}
.transaction-amount.income {
    color: #28a745;
}
.transaction-date {
    font-size: 13px;
    color: #aaa;
    margin-top: 2px;
}

/* Add Font Awesome for icons */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
</style>
"""

# Cargar estilos CSS
st.markdown(css_style, unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS (SQLite) ---
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

def get_recent_transactions(limit=3):
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Inicializar base de datos
init_db()

# --- LÓGICA DE DATOS ---
df_all = get_data()

# Obtener mes y año actual
today = date.today()
current_month = today.strftime("%Y-%m")
# Filtrar por mes actual para los resúmenes
if not df_all.empty:
    df_all['date'] = pd.to_datetime(df_all['date'])
    df_current_month = df_all[df_all['date'].dt.to_period('M') == current_month]
else:
    df_current_month = pd.DataFrame()

# Cálculos de métricas
total_ingresos_mes = df_current_month[df_current_month['type'] == 'Ingreso']['amount'].sum() if not df_current_month.empty else 0.00
total_gastos_mes = df_current_month[df_current_month['type'] == 'Gasto']['amount'].sum() if not df_current_month.empty else 0.00
saldo_actual_mes = total_ingresos_mes - total_gastos_mes

total_global_ingresos = df_all[df_all['type'] == 'Ingreso']['amount'].sum() if not df_all.empty else 0.00
total_global_gastos = df_all[df_all['type'] == 'Gasto']['amount'].sum() if not df_all.empty else 0.00
saldo_actual_global = total_global_ingresos - total_global_gastos

# --- INTERFAZ PRINCIPAL (HTML) ---
st.write("") # Espacio superior

# Header
header_html = f"""
<div class="header-container">
    <div class="header-profile-icon">
        <i class="fa-solid fa-wallet"></i>
    </div>
    <div class="header-balance-container">
        <div class="header-balance-value">${saldo_actual_global:,.2f}</div>
        <div class="header-month-value">${saldo_actual_mes:,.2f} {today.strftime("%B")}</div>
    </div>
    <div class="header-arrow-icon">
        <i class="fas fa-chevron-down"></i>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Summary Cards
summary_html = f"""
<div class="summary-container">
    <div class="summary-card">
        <div class="icon-container income">
            <i class="fas fa-arrow-down"></i>
        </div>
        <div class="summary-text-container">
            <div class="summary-label">Ingresos</div>
            <div class="summary-value">${total_ingresos_mes:,.2f}</div>
            <div class="summary-period">Este Mes</div>
        </div>
    </div>
    <div class="summary-card">
        <div class="icon-container expense">
            <i class="fas fa-arrow-up"></i>
        </div>
        <div class="summary-text-container">
            <div class="summary-label">Gastos</div>
            <div class="summary-value">${total_gastos_mes:,.2f}</div>
            <div class="summary-period">Este Mes</div>
        </div>
    </div>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)

# Blue Balance Card
blue_card_html = f"""
<div class="blue-balance-card">
    <div class="blue-card-label">Saldo Actual</div>
    <div class="blue-card-value">${saldo_actual_global:,.2f}</div>
</div>
"""
st.markdown(blue_card_html, unsafe_allow_html=True)

# Recent Transactions Header
recent_header_html = f"""
<div class="recent-header">
    <div class="recent-title">Transacciones Recientes</div>
    <a href="#" class="view-all-link">Ver Todo</a>
</div>
"""
st.markdown(recent_header_html, unsafe_allow_html=True)

# Loop over recent transactions
df_recent = get_recent_transactions(limit=3)

if not df_recent.empty:
    for index, row in df_recent.iterrows():
        # Formatear la fecha
        t_date = pd.to_datetime(row['date']).strftime("%d %b %Y")
        
        # Clase de icono y monto basada en el tipo
        icon_class = "income" if row['type'] == 'Ingreso' else "expense"
        icon_icon = "fas fa-arrow-down" if row['type'] == 'Ingreso' else "fas fa-arrow-up"
        amount_sign = "" if row['type'] == 'Ingreso' else "-"
        
        transaction_html = f"""
        <div class="transaction-list">
            <div class="transaction-entry">
                <div class="transaction-left">
                    <div class="transaction-icon-box {icon_class}">
                        <i class="{icon_icon}"></i>
                    </div>
                    <div class="transaction-text-container">
                        <div class="transaction-category">{row['category']}</div>
                        <div class="transaction-note">{row['note'] or row['category']}</div>
                    </div>
                </div>
                <div class="transaction-right">
                    <div class="transaction-amount {icon_class}">{amount_sign}${row['amount']:,.2f}</div>
                    <div class="transaction-date">{t_date}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(transaction_html, unsafe_allow_html=True)
else:
    st.info("👋 ¡Registra tu primer movimiento en la barra lateral!")

# --- BARRA LATERAL (ENTRADA DE DATOS) ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("transaction_form", clear_on_submit=True):
        date_input = st.date_input("Fecha", datetime.today())
        t_type = st.radio("Tipo", ["Gasto", "Ingreso"])
        
        # Categorías dinámicas según el tipo
        if t_type == "Gasto":
            category = st.selectbox("Categoría", ["Entretenimiento", "Comida", "Transporte", "Vivienda", "Servicios", "Salud", "Otros"])
        else:
            category = st.selectbox("Categoría", ["Salario", "Inversiones", "Recarga", "Otros"])
            
        amount = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
        note = st.text_input("Nota / Descripción")
        
        submit = st.form_submit_button("Guardar Registro")
        
        if submit:
            add_transaction(date_input.strftime("%Y-%m-%d"), t_type, category, amount, note)
            st.rerun() # Recargar para ver los cambios en la dashboard

# Pequeña barra flotante simulando botones inferiores (solo visual)
st.write("")
st.write("")
st.write("")
st.write("")
col_nav1, col_nav2 = st.columns([1,1])
with col_nav1:
    st.button("🟢 + Ingresos", disabled=True, use_container_width=True)
with col_nav2:
    st.button("🔴 + Gastos", disabled=True, use_container_width=True)
