import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vault Premium", page_icon="💎", layout="centered")

# --- REDISEÑO ULTRA-PREMIUM CORREGIDO (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #0F172A, #020617);
        font-family: 'Outfit', sans-serif;
        color: #F8FAFC;
    }
    header, footer {visibility: hidden;}
    .main .block-container { padding-top: 1.5rem; max-width: 480px; }

    /* 1. Glass Card - Balance */
    .premium-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 32px;
        padding: 40px 30px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    .balance-label { 
        font-size: 11px; 
        text-transform: uppercase; 
        letter-spacing: 4px; 
        color: #94A3B8; 
        margin-bottom: 8px;
    }
    .balance-val { 
        font-size: 52px; 
        font-weight: 800; 
        background: linear-gradient(to right, #F8FAFC, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
    }

    /* 2. Bento Grid Stats */
    .bento-container {
        display: grid;
        grid-template-columns: 1fr 1.2fr;
        gap: 15px;
        margin-bottom: 30px;
    }
    .bento-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 20px;
        transition: transform 0.3s ease;
    }
    .bento-item:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05);
    }
    .stat-n { font-size: 22px; font-weight: 700; margin-top: 5px; }
    .stat-t { font-size: 10px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 1px; }

    /* 3. Botones Neomorfistas (CORRECCIÓN DE VISIBILIDAD) */
    div.stButton > button {
        border-radius: 20px !important;
        padding: 20px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border: none !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    /* Esta regla fuerza a los hijos del botón a usar el color definido en el botón */
    div.stButton > button * {
        color: inherit !important;
    }

    /* Botón INGRESO: Fondo claro, texto oscuro */
    button[key="btn_ingreso"] {
        background: #F8FAFC !important;
        color: #020617 !important; /* Color de texto oscuro para fondo claro */
    }
    /* Asegurar que el texto dentro del botón de ingreso sea oscuro */
    button[key="btn_ingreso"] * {
        color: #020617 !important;
    }

    /* Botón GASTO: Fondo rosa suave, texto rosa */
    button[key="btn_gasto"] {
        background: rgba(244, 63, 94, 0.15) !important;
        color: #FB7185 !important;
        border: 1px solid rgba(244, 63, 94, 0.2) !important;
    }
    button[key="btn_gasto"] * {
        color: #FB7185 !important;
    }

    /* Botón CONFIGURAR: Fondo transparente, texto gris */
    button[key="btn_sueldo"] {
        background: transparent !important;
        color: #64748B !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        margin-top: 20px !important;
    }
    button[key="btn_sueldo"] * {
        color: #64748B !important;
    }

    /* 4. Transaction Feed */
    .feed-container { margin-top: 40px; }
    .transaction-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        margin-bottom: 12px;
        border-left: 4px solid transparent;
    }
    .tx-inc { border-left-color: #10B981; }
    .tx-exp { border-left-color: #F43F5E; }
    
    .tx-info { display: flex; flex-direction: column; }
    .tx-cat { font-size: 9px; font-weight: 800; text-transform: uppercase; color: #475569; }
    .tx-note { font-size: 15px; font-weight: 500; color: #E2E8F0; }
    .tx-amt { font-size: 16px; font-weight: 700; }

    /* Estilo para el botón Eliminar (más pequeño, discreto y legible) */
    div.stButton button[key^="del_"] {
        background: transparent !important;
        color: #64748B !important; /* Texto gris */
        font-size: 10px !important;
        padding: 5px 10px !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton button[key^="del_"]:hover {
        color: #F43F5E !important; /* Hover rojo */
        background: rgba(244, 63, 94, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND (Sin cambios en tu lógica) ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
    URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
except:
    st.error("⚠️ Configura los Secrets (bin_id y api_key).")
    st.stop()

@st.cache_data(ttl=60)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        if "settings" not in data: data["settings"] = {"sueldo": 0.0}
        if "transactions" not in data: data["transactions"] = []
        return data
    except:
        return {"transactions": [], "settings": {"sueldo": 0.0}}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()
df = pd.DataFrame(db["transactions"])
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount']).fillna(0.0)
    mes_actual = datetime.now().month
    df_mes = df[df['date_dt'].dt.month == mes_actual]
else:
    df_mes = pd.DataFrame(columns=["amount", "type"])

sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
saldo_total = sueldo_base + (df[df['type']=='Ingreso']['amount'].sum() if not df.empty else 0) - (df[df['type']=='Gasto']['amount'].sum() if not df.empty else 0)

# --- DIÁLOGOS ---
@st.dialog("🎯 Definir Presupuesto")
def sueldo_dialog():
    s = st.number_input("Salario base inicial", value=sueldo_base)
    if st.button("Actualizar Bóveda", use_container_width=True):
        db["settings"]["sueldo"] = s
        save_db(db); st.rerun()

@st.dialog("🚀 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto del ingreso ($)", min_value=0.0)
    note = st.text_input("Concepto")
    if st.button("Inyectar Capital", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Ingreso", "category": "Extra", "amount": amt, "note": note
        })
        save_db(db); st.rerun()

@st.dialog("💸 Registrar Gasto")
def gasto_dialog():
    cat = st.selectbox("Categoría", ["🍔 Comida", "🎬 Ocio", "🚗 Transporte", "🏠 Hogar", "💡 Servicios", "🌀 Otros"])
    amt = st.number_input("Monto gastado ($)", min_value=0.0)
    note = st.text_input("Nota")
    if st.button("Confirmar Gasto", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ ---

# Header Balance
st.markdown(f"""
<div class="premium-card">
    <div class="balance-label">Total Balance</div>
    <div class="balance-val">${saldo_total:,.2f}</div>
    <div style="margin-top:15px; font-size:10px; color:#10B981; letter-spacing:2px; font-weight:800;">
        <span style="opacity:0.5;">●</span> VAULT SECURED
    </div>
</div>
""", unsafe_allow_html=True)

# Bento Stats
st.markdown(f"""
<div class="bento-container">
    <div class="bento-item">
        <div class="stat-t">Mensual In</div>
        <div class="stat-n" style="color:#10B981;">+${ingresos_mes:,.0f}</div>
    </div>
    <div class="bento-item">
        <div class="stat-t">Mensual Out</div>
        <div class="stat-n" style="color:#F43F5E;">-${gastos_mes:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Actions
c1, c2 = st.columns(2)
with c1:
    if st.button("✚ INGRESO", key="btn_ingreso", use_container_width=True):
        ingreso_dialog()
with c2:
    if st.button("➖ GASTO", key="btn_gasto", use_container_width=True):
        gasto_dialog()

# Transactions
st.markdown("<div class='feed-container'><p style='font-size:12px; font-weight:800; color:#475569; letter-spacing:1px; margin-bottom:20px;'>RECUPERANDO ACTIVIDAD</p>", unsafe_allow_html=True)

if not df.empty:
    for _, row in df.sort_values('date', ascending=False).head(8).iterrows():
        is_inc = row['type'] == 'Ingreso'
        clase = "tx-inc" if is_inc else "tx-exp"
        simbolo = "+" if is_inc else "-"
        color = "#10B981" if is_inc else "#F43F5E"
        
        st.markdown(f"""
        <div class="transaction-item {clase}">
            <div class="tx-info">
                <span class="tx-cat">{row['category']}</span>
                <span class="tx-note">{row['note']}</span>
            </div>
            <div style="text-align:right">
                <div class="tx-amt" style="color:{color}">{simbolo}${row['amount']:,.2f}</div>
                <div style="font-size:9px; color:#475569;">{row['date']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # El botón de borrar se mantiene funcional pero discreto
        if st.button(f"🗑️ {row['id']}", key=f"del_{row['id']}", help="Remover"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()
else:
    st.info("Sin registros.")

if st.button("EDITAR PRESUPUESTO BASE", key="btn_sueldo", use_container_width=True):
    sueldo_dialog()

# Footer
st.markdown(f"""
<div style="margin-top:60px; text-align:center; opacity:0.2; font-size:9px; letter-spacing:5px; font-weight:800;">
    EST. {datetime.now().year} • PRIVATE ACCESS
</div>
""", unsafe_allow_html=True)