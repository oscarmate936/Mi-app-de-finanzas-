import streamlit as st

# Configuración de página para centrar el contenido como en un celular
st.set_page_config(page_title="UI Design Skeleton", layout="centered")

# --- CSS PARA EL DISEÑO DE TARJETAS (CARDS) ---
st.markdown("""
    <style>
    /* Fondo de la aplicación */
    .stApp { background-color: #F7F9FC; }

    /* Tarjeta Blanca (2, 3 y Transacciones) */
    .card-white {
        background-color: white;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #EDF0F5;
        margin-bottom: 10px;
        position: relative;
    }

    /* Tarjeta Azul (4) */
    .card-blue {
        background-color: #0078D4;
        color: white;
        padding: 25px;
        border-radius: 22px;
        margin: 15px 0;
        position: relative;
    }

    /* Botones de acción (6 y 7) */
    .btn-action {
        color: white;
        padding: 16px;
        border-radius: 14px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
    }

    /* Texto y Referencias */
    .label-muted { color: #8E8E93; font-size: 0.8rem; }
    .val-main { font-weight: 700; font-size: 1.2rem; color: #1C1C1E; }
    .ref-num { 
        position: absolute; right: 15px; bottom: 10px; 
        font-size: 1.4rem; color: #D1D1D6; font-weight: 800; opacity: 0.5;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. ENCABEZADO / BILLETERA ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown("""<div style="background:#0078D4; color:white; padding:15px; border-radius:12px; text-align:center;">💰</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("**1,161**<br><span style='color:#FF3B30;'>$-22.99</span> <span style='float:right; opacity:0.3;'>1</span>", unsafe_allow_html=True)

st.write("---")

# --- 2 y 3. CUADRÍCULA LADO A LADO (Ingresos y Gastos) ---
# Usamos columnas para que 2 esté a la izquierda y 3 a la derecha
col_left, col_right = st.columns(2, gap="small")

with col_left:
    st.markdown("""
        <div class="card-white">
            <span style="color:#34C759;">↓</span> <span class="label-muted">Ingresos</span><br>
            <div class="val-main">$0.00</div>
            <span class="label-muted">Este Mes</span>
            <div class="ref-num">2</div>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class="card-white">
            <span style="color:#FF3B30;">↑</span> <span class="label-muted">Gastos</span><br>
            <div class="val-main">$22.99</div>
            <span class="label-muted">Este Mes</span>
            <div class="ref-num">3</div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. SALDO ACTUAL (CONTENEDOR AZUL) ---
st.markdown("""
    <div class="card-blue">
        <span style="opacity: 0.8; font-size: 0.9rem;">Saldo Actual</span><br>
        <span style="font-size: 2.2rem; font-weight: bold;">$-22.99</span>
        <div style="position: absolute; right: 25px; top: 30%; font-size: 2.5rem; opacity: 0.3;">4</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. TRANSACCIONES RECIENTES ---
st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin: 15px 0 10px 0;">
        <b style="font-size:1.1rem;">Transacciones Recientes</b>
        <span style="color:#0078D4; font-size:0.85rem; font-weight:bold;">Ver Todo [5]</span>
    </div>
""", unsafe_allow_html=True)

# Mock de transacciones
for label, price, date in [("Entertainment", "-$11.00", "19 Mar"), ("Netflix", "-$8.99", "19 Mar")]:
    st.markdown(f"""
        <div class="card-white" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="background:#F2F2F7; padding:10px; border-radius:50%;">🎬</div>
                <div><b>{label}</b><br><span class="label-muted">GP</span></div>
            </div>
            <div style="text-align:right;">
                <span style="color:#FF3B30; font-weight:bold;">{price}</span><br>
                <span class="label-muted">{date}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 6 y 7. BOTONES INFERIORES LADO A LADO ---
st.write("")
b_left, b_right = st.columns(2, gap="small")

with b_left:
    st.markdown('<div class="btn-action" style="background:#34C759;">↓ Ingresos [6]</div>', unsafe_allow_html=True)

with b_right:
    st.markdown('<div class="btn-action" style="background:#FF3B30;">↑ Gastos [7]</div>', unsafe_allow_html=True)
