import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Vault Premium", page_icon="💎", layout="centered")

# --- ESTILOS CSS (DISEÑO PREMIUM ASIMÉTRICO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    /* Configuración Base */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }
    .main .block-container { padding-top: 1rem; max-width: 500px; }

    /* Tarjeta Principal Asimétrica (Balance) */
    .hero-card {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        padding: 40px 30px;
        border-radius: 40px 40px 80px 40px; /* Asimetría en bordes */
        margin-bottom: 25px;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
        position: relative;
        overflow: hidden;
    }
    .hero-card::after {
        content: ""; position: absolute; top: -20px; right: -20px;
        width: 100px; height: 100px; background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }
    .hero-label { font-size: 12px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8; }
    .hero-val { font-size: 48px; font-weight: 800; margin: 5px 0; }

    /* Stat Boxes Asimétricas */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 24px;
        margin-bottom: 15px;
    }
    .stat-inc { border-left: 4px solid #4ade80; border-radius: 12px 30px 30px 12px; }
    .stat-exp { border-right: 4px solid #f43f5e; border-radius: 30px 12px 12px 30px; text-align: right; }

    /* Transacciones List */
    .trans-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .trans-item:hover { transform: scale(1.02); background: rgba(255, 255, 255, 0.05); }
    
    .icon-box {
        width: 45px; height: 45px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }

    /* Botones Premium */
    div.stButton > button {
        border-radius: 20px !important;
        padding: 20px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    
    /* Botón Ingreso (Verde Neón) */
    button[key="btn_inc"] { background: #4ade80 !important; color: #064e3b !important; }
    /* Botón Gasto (Rosa Eléctrico) */
    button[key="btn_exp"] { background: #f43f5e !important; color: #fff !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- BACKEND ---
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
    df['amount'] = pd.to_numeric(df['amount'])
    mes_actual = datetime.now().month
    df_mes = df[df['date_dt'].dt.month == mes_actual]
else:
    df_mes = pd.DataFrame(columns=["amount", "type"])

# Cálculos
sueldo_base = db["settings"].get("sueldo", 0.0)
ingresos = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
gastos = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
balance_neto = ingresos - gastos
total_disponible = sueldo_base + (df[df['type']=='Ingreso']['amount'].sum() if not df.empty else 0) - (df[df['type']=='Gasto']['amount'].sum() if not df.empty else 0)

# --- DIÁLOGOS ---
@st.dialog("⚙️ Ajustes")
def settings_dialog():
    s = st.number_input("Salario Base Mensual", value=sueldo_base)
    if st.button("Actualizar Bóveda", use_container_width=True):
        db["settings"]["sueldo"] = s
        save_db(db); st.rerun()

@st.dialog("➕ Nueva Operación")
def operation_dialog(tipo):
    st.markdown(f"### Registro de {tipo}")
    amt = st.number_input("Cantidad ($)", min_value=0.0, step=10.0)
    note = st.text_input("Concepto / Nota")
    cat = st.selectbox("Categoría", ["Fijo", "Comida", "Ocio", "Transporte", "Inversión", "Otro"])
    if st.button(f"Confirmar {tipo}", use_container_width=True):
        db["transactions"].append({
            "id": str(uuid.uuid4())[:6], "date": datetime.now().strftime("%Y-%m-%d"),
            "type": tipo, "category": cat, "amount": amt, "note": note
        })
        save_db(db); st.rerun()

# --- INTERFAZ DE USUARIO ---

# 1. HERO SECTION (Balance Asimétrico)
st.markdown(f"""
<div class="hero-card">
    <div class="hero-label">Balance del Mes</div>
    <div class="hero-val">${balance_neto:,.2f}</div>
    <div style="font-size: 14px; opacity: 0.9;">
        {'+' if balance_neto >= 0 else ''}{ (balance_neto/(sueldo_base if sueldo_base>0 else 1))*100:.1f}% respecto al sueldo
    </div>
</div>
""", unsafe_allow_html=True)

# 2. STATS ASIMÉTRICOS (Layout 2:1 y 1:2)
c1, c2 = st.columns([2, 1.2])
with c1:
    st.markdown(f"""
    <div class="glass-card stat-inc">
        <div style="color: #4ade80; font-size: 12px; font-weight: 800; text-transform: uppercase;">Ingresos Extra</div>
        <div style="font-size: 24px; font-weight: 700;">+ ${ingresos:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="glass-card stat-exp" style="background: rgba(244, 63, 94, 0.05);">
        <div style="color: #f43f5e; font-size: 12px; font-weight: 800; text-transform: uppercase;">Gastos</div>
        <div style="font-size: 20px; font-weight: 700;">- ${gastos:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# 3. ACCIONES RÁPIDAS
st.write(" ")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("✚ INGRESO", key="btn_inc", use_container_width=True):
        operation_dialog("Ingreso")
with col_b:
    if st.button("➖ GASTO", key="btn_exp", use_container_width=True):
        operation_dialog("Gasto")

# 4. TRANSACCIONES (Diseño de lista limpia)
st.markdown("<br><div style='display:flex; justify-content:space-between; align-items:center;'><h3>Historial</h3><p style='color:#6366f1; font-size:12px;'>Ver todo</p></div>", unsafe_allow_html=True)

if not df.empty:
    for _, row in df.sort_values('date', ascending=False).head(8).iterrows():
        is_inc = row['type'] == 'Ingreso'
        icon = "💸" if is_inc else "🛍️"
        color = "#4ade80" if is_inc else "#f43f5e"
        bg_icon = "rgba(74, 222, 128, 0.1)" if is_inc else "rgba(244, 63, 94, 0.1)"
        
        st.markdown(f"""
        <div class="trans-item">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="icon-box" style="background: {bg_icon}; color: {color};">{icon}</div>
                <div>
                    <div style="font-weight: 600; font-size: 14px;">{row['category']}</div>
                    <div style="font-size: 11px; opacity: 0.5;">{row['note']} • {row['date']}</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 700; color: {color};">{'+' if is_inc else '-'}${row['amount']:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Eliminar muy pequeño abajo
        if st.button(f"Borrar {row['id']}", key=f"del_{row['id']}", type="secondary"):
            db["transactions"] = [t for t in db["transactions"] if t["id"] != row['id']]
            save_db(db); st.rerun()
else:
    st.info("Bóveda vacía. Registra tu primera transacción.")

# 5. FOOTER (Información de Salario Real)
st.markdown("---")
cf1, cf2 = st.columns([1, 1])
with cf1:
    st.markdown(f"**Efectivo Total:** <span style='color:#6366f1'>${total_disponible:,.2f}</span>", unsafe_allow_html=True)
with cf2:
    if st.button("⚙️ Configuración", use_container_width=True):
        settings_dialog()

