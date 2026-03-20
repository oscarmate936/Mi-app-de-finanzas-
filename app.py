import streamlit as st

# Configuración para que el diseño sea centrado y limpio
st.set_page_config(page_title="Dashboard Financiero", layout="centered")

# --- CSS PERSONALIZADO PARA COPIAR EL DISEÑO ---
st.markdown("""
    <style>
    /* Fondo general gris muy claro */
    .stApp {
        background-color: #F2F4F7;
    }
    
    /* Estilo para las tarjetas blancas (2 y 3) */
    .card-small {
        background-color: white;
        padding: 15px;
        border-radius: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #E6E8EB;
        height: 110px;
        position: relative;
    }

    /* Tarjeta Azul Grande (4) */
    .card-blue {
        background-color: #0077B6;
        color: white;
        padding: 20px;
        border-radius: 20px;
        margin: 15px 0px;
        position: relative;
        min-height: 120px;
    }

    /* Botones inferiores (6 y 7) */
    .btn-action {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* Tipografías y Colores */
    .label-secondary { color: #8E8E93; font-size: 0.85rem; }
    .price-black { color: #1C1C1E; font-size: 1.2rem; font-weight: 700; margin: 5px 0; }
    .price-red { color: #FF3B30; font-size: 0.9rem; font-weight: 600; }
    .badge-number { 
        position: absolute; right: 15px; bottom: 15px; 
        font-size: 1.5rem; color: #E5E5EA; font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CABECERA (Billetera) ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        # Icono de billetera simulado
        st.markdown("""<div style="background:#E1F0FF; padding:15px; border-radius:12px; text-align:center;">
            <span style="font-size:1.5rem;">💳</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<b>1,161</b><br><span class='price-red'>$-22.99</span> <span style='color:#E5E5EA; font-weight:bold; float:right;'>1</span>", unsafe_allow_html=True)

st.write(" ")

# --- 2 y 3. CUADRÍCULA DE INGRESOS Y GASTOS (Juntos) ---
# Usamos col_gap="small" para que estén bien pegados
col2, col3 = st.columns(2)

with col2:
    st.markdown(f"""
        <div class="card-small">
            <span style="color: #34C759;">↓</span> <span class="label-secondary">Ingresos</span><br>
            <div class="price-black">$0.00</div>
            <span class="label-secondary">Este Mes</span>
            <div class="badge-number">2</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card-small">
            <span style="color: #FF3B30;">↑</span> <span class="label-secondary">Gastos</span><br>
            <div class="price-black">$22.99</div>
            <span class="label-secondary">Este Mes</span>
            <div class="badge-number">3</div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. SALDO ACTUAL ---
st.markdown("""
    <div class="card-blue">
        <span style="font-size: 0.9rem; opacity: 0.8;">Saldo Actual</span><br>
        <span style="font-size: 2.5rem; font-weight: bold;">$-22.99</span>
        <div style="position: absolute; right: 30px; top: 35%; font-size: 2rem; opacity: 0.5;">4</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. TRANSACCIONES RECIENTES ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <b style="font-size: 1.1rem;">Transacciones Recientes</b>
        <span style="color: #0077B6; font-size: 0.8rem; font-weight: bold;">Ver Todo</span>
    </div>
""", unsafe_allow_html=True)

# Lista de transacciones (Esqueleto)
for _ in range(3):
    st.markdown("""
        <div style="background:white; padding:12px; border-radius:15px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; border: 1px solid #F0F0F0;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:#FFE7E7; padding:8px; border-radius:50%;">⬆️</div>
                <div>
                    <b>Entertainment</b><br><span style="font-size:0.7rem; color:grey;">Netflix / GP</span>
                </div>
            </div>
            <div style="text-align:right;">
                <span style="color:#FF3B30; font-weight:bold;">-$8.99</span><br><span style="font-size:0.7rem; color:grey;">19 Mar 2026</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#E5E5EA; font-weight:bold;'>5</div>", unsafe_allow_html=True)

# --- 6 y 7. BOTONES DE ACCIÓN ---
st.write(" ")
col6, col7 = st.columns(2)

with col6:
    st.markdown('<div class="btn-action" style="background-color: #34C759;">↓ Ingresos <span style="opacity:0.5;">6</span></div>', unsafe_allow_html=True)

with col7:
    st.markdown('<div class="btn-action" style="background-color: #FF3B30;">↑ Gastos <span style="opacity:0.5;">7</span></div>', unsafe_allow_html=True)
