import streamlit as st

# --- Configuración de Estilo (CSS) ---
st.markdown("""
    <style>
    /* Estilo para las tarjetas generales */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        border: 1px solid #f0f2f6;
    }
    
    /* Tarjeta Azul (Saldo Actual) */
    .balance-card {
        background-color: #0077b6;
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: left;
        margin-bottom: 20px;
    }
    
    /* Botones inferiores */
    .btn-ingreso {
        background-color: #00a86b;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .btn-gasto {
        background-color: #ff3b30;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Ajustes de fuente */
    .label { color: #8e8e93; font-size: 0.9rem; }
    .amount { font-size: 1.5rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. Encabezado / Billetera ---
with st.container():
    col_icon, col_text = st.columns([1, 4])
    with col_text:
        st.markdown("**1,161**")
        st.markdown("<span style='color:red;'>$-22.99</span>", unsafe_allow_html=True)

st.divider()

# --- 2 y 3. Fila de Ingresos y Gastos ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="card">
            <span class="label">⬇️ Ingresos</span><br>
            <span class="amount">$0.00</span><br>
            <span class="label">Este Mes [2]</span>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="card">
            <span class="label">⬆️ Gastos</span><br>
            <span class="amount">$22.99</span><br>
            <span class="label">Este Mes [3]</span>
        </div>
    """, unsafe_allow_html=True)

# --- 4. Saldo Actual (Contenedor Azul) ---
st.markdown("""
    <div class="balance-card">
        <span style="font-size: 1rem; opacity: 0.9;">Saldo Actual</span><br>
        <span style="font-size: 2.2rem; font-weight: bold;">$-22.99</span>
        <div style="float: right; font-size: 1.5rem;">[4]</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. Transacciones Recientes ---
st.subheader("Transacciones Recientes [5]")
for i in range(3):
    with st.container():
        t_col1, t_col2 = st.columns([4, 1])
        with t_col1:
            st.markdown("**Entertainment**")
            st.caption("Categoría / Detalle")
        with t_col2:
            st.markdown("<span style='color:red;'>- $0.00</span>", unsafe_allow_html=True)
        st.divider()

# --- 6 y 7. Botones de Acción Inferiores ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    st.markdown('<div class="btn-ingreso">⬇️ Ingresos [6]</div>', unsafe_allow_html=True)

with col_btn2:
    st.markdown('<div class="btn-gasto">⬆️ Gastos [7]</div>', unsafe_allow_html=True)
