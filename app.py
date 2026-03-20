import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vault Premium", page_icon="💎", layout="centered")

# --- ESTILOS CSS (DISEÑO PREMIUM ASIMÉTRICO Y NEO-BENTO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    /* Configuración Base */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] {
        background-color: #0A0C10;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #E2E8F0;
    }
    .main .block-container { padding-top: 2rem; max-width: 500px; }

    /* 1. Tarjeta de Balance Principal (Asimétrica) */
    .balance-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 35px 25px;
        border-radius: 20px 80px 20px 20px; /* Bordes asimétricos */
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 25px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }
    .balance-label { font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #94A3B8; margin-bottom: 5px; }
    .balance-val { font-size: 42px; font-weight: 800; color: #F8FAFC; letter-spacing: -1px; }

    /* 2. Stats Bento (Tamaños desiguales) */
    .stat-card {
        background: #161B22;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .inc-card { border-radius: 40px 15px 15px 15px; border-top: 3px solid #10B981; }
    .exp-card { border-radius: 15px 15px 40px 15px; border-bottom: 3px solid #F43F5E; }
    
    .stat-title { font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; }
    .stat-amt { font-size: 20px; font-weight: 700; margin-top: 10px; }

    /* 3. Lista de Transacciones */
    .trans-box {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 24px;
        padding: 10px;
        margin-top: 20px;
    }
    .trans-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .cat-badge {
        background: #1E293B;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        color: #94A3B8;
    }
    
    /* Botones Custom */
    div.stButton > button {
        border-radius: 18px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    /* Botón Ingreso */
    button[key="btn_ingreso"] { background: #10B981 !important; color: white !important; height: 60px !important; }
    /* Botón Gasto */
    button[key="btn_gasto"] { background: #F43F5E !important; color: white !important; height: 60px !important; }
    /* Botón Sueldo */
    button[key="btn_sueldo"] { background: #334155 !important; color: #94A3B8 !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# --- BACKEND (Respetando tu lógica original) ---
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

# Cálculos
sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
saldo_total = sueldo_base + (df[df['type']=='Ingreso']['amount'].sum() if not df.empty else 0) - (df[df['type']=='Gasto']['amount'].sum() if not df.empty else 0)

# --- DIÁLOGOS (ENTRADAS) ---
@st.dialog("🎯 Definir Presupuesto")
def sueldo_dialog():
    s = st.number_input("Salario base inicial", value=sueldo_base, help="Este monto se suma al balance total.")
    if st.button("Actualizar Bóveda", use_container_width=True):
        db["settings"]["sueldo"] = s
        save_db(db); st.rerun()

@st.dialog("🚀 Nuevo Ingreso")
def ingreso_dialog():
    amt = st.number_input("Monto del ingreso ($)", min_value=0.0)
    note = st.text_input("¿De qué se trata?", placeholder="Ej: Venta de garage")
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
    note = st.text_input("Nota breve", placeholder="Ej: Cena con amigos")
    if st.button("Confirmar Gasto", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Gasto", "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ VISUAL ---

# 1. BALANCE PRINCIPAL (Asimétrico)
st.markdown(f"""
<div class="balance-card">
    <div class="balance-label">Disponible Total</div>
    <div class="balance-val">${saldo_total:,.2f}</div>
    <div style="color:#10B981; font-size:12px; font-weight:600; margin-top:10px;">
        ⚡ Bóveda Activa
    </div>
</div>
""", unsafe_allow_html=True)

# 2. STATS ASIMÉTRICOS (Columna 1:2)
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.markdown(f"""
    <div class="stat-card inc-card">
        <div class="stat-title">Ingresos</div>
        <div class="stat-amt" style="color:#10B981;">+${ingresos_mes:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
    <div class="stat-card exp-card">
        <div class="stat-title">Gastos del Mes</div>
        <div class="stat-amt" style="color:#F43F5E;">-${gastos_mes:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# 3. BOTONES DE ACCIÓN (Todos son botones que abren diálogos)
c1, c2 = st.columns(2)
with c1:
    if st.button("✚ INGRESO", key="btn_ingreso", use_container_width=True):
        ingreso_dialog()
with c2:
    if st.button("➖ GASTO", key="btn_gasto", use_container_width=True):
        gasto_dialog()

if st.button("⚙️ CONFIGURAR SALARIO BASE", key="btn_sueldo", use_container_width=True):
    sueldo_dialog()

# 4. HISTORIAL PREMIUM
st.markdown("<h3 style='font-size:18px; margin-top:30px;'>Movimientos Recientes</h3>", unsafe_allow_html=True)

if not df.empty:
    st.markdown('<div class="trans-box">', unsafe_allow_html=True)
    for _, row in df.sort_values('date', ascending=False).head(10).iterrows():
        is_inc = row['type'] == 'Ingreso'
        color = "#10B981" if is_inc else "#F43F5E"
        prefix = "+" if is_inc else "-"
        
        st.markdown(f"""
        <div class="trans-row">
            <div>
                <span class="cat-badge">{row['category']}</span>
                <div style="font-size:14px; font-weight:600; margin-top:4px;">{row['note']}</div>
                <div style="font-size:10px; color:#475569;">{row['date']}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:{color}; font-weight:800; font-size:16px;">{prefix}${row['amount']:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de eliminar (Mantenido por lógica)
        if st.button(f"🗑️", key=f"del_{row['id']}", help="Eliminar registro"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay movimientos registrados.")

# Footer asimétrico
st.markdown(f"""
<div style="margin-top:50px; text-align:center; opacity:0.3; font-size:10px; letter-spacing:3px;">
    VAULT PREMIUM v2.0 • {datetime.now().year}
</div>
""", unsafe_allow_html=True)
