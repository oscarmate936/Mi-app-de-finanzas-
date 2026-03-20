import streamlit as st

# Configuración de la página para que parezca una app móvil
st.set_page_config(page_title="Finanzas App", layout="centered")

# --- CSS PERSONALIZADO (El "ADN" del diseño) ---
st.markdown("""
    <style>
    /* Fondo de la app */
    .stApp {
        background-color: #F8F9FB;
    }
    
    /* Estilo general de tarjetas blancas (2, 3 y transacciones) */
    .card-white {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #EAEAEA;
        margin-bottom: 10px;
    }

    /* Tarjeta Azul (4 - Saldo Actual) */
    .card-blue {
        background-color: #0071C1;
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-top: 10px;
        margin-bottom: 20px;
        position: relative;
    }

    /* Botones Inferiores (6 y 7) */
    .btn-footer-green {
        background-color: #008F39;
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        font-weight: bold;
    }
    .btn-footer-red {
        background-color: #E32636;
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        font-weight: bold;
    }

    /* Etiquetas de texto */
    .label-grey { color: #8A8A8A; font-size: 0.8rem; }
    .val-black { color: #1A1A1A; font-weight: bold; font-size: 1.1rem; }
    .val-red { color: #FF4B4B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUCTURA DE LA CUADRÍCULA ---

# 1. Encabezado (Billetera)
with st.container():
    c1, c2 = st.columns([1, 5])
    with c1:
        st.write("🟦") # Simulación de icono
    with c2:
        st.markdown("### 1,161 <br> <span class='val-red'>$-22.99</span> [1]", unsafe_allow_html=True)

st.write("") # Espaciador

# 2 y 3. Fila de Ingresos y Gastos (Cuadrícula de 2 columnas)
col_2, col_3 = st.columns(2)

with col_2:
    st.markdown("""
        <div class="card-white">
            <span style="color: green;">↓</span> <span class="label-grey">Ingresos</span><br>
            <span class="val-black">$0.00</span><br>
            <span class="label-grey">Este Mes</span> <span style="float:right"><b>2</b></span>
        </div>
    """, unsafe_allow_html=True)

with col_3:
    st.markdown("""
        <div class="card-white">
            <span style="color: red;">↑</span> <span class="label-grey">Gastos</span><br>
            <span class="val-black">$22.99</span><br>
            <span class="label-grey">Este Mes</span> <span style="float:right"><b>3</b></span>
        </div>
    """, unsafe_allow_html=True)

# 4. Saldo Actual (Gran contenedor azul)
st.markdown("""
    <div class="card-blue">
        <span style="font-size: 0.9rem; opacity: 0.9;">Saldo Actual</span><br>
        <span style="font-size: 2rem; font-weight: bold;">$-22.99</span>
        <span style="position: absolute; right: 20px; top: 40%; font-size: 1.5rem;">4</span>
    </div>
""", unsafe_allow_html=True)

# 5. Transacciones Recientes
st.markdown("#### Transacciones Recientes <span style='float:right; font-size: 0.8rem; color: #0071C1;'>Ver Todo [5]</span>", unsafe_allow_html=True)

# Ejemplo de fila de transacción
for _ in range(3):
    st.markdown("""
        <div class="card-white" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-weight: bold;">Entertainment</span><br>
                <span class="label-grey">Netflix / Recarga</span>
            </div>
            <div style="text-align: right;">
                <span class="val-red">-$8.99</span><br>
                <span class="label-grey">19 Mar 2026</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.write("") # Espaciador

# 6 y 7. Botones de Acción (Pie de página)
col_6, col_7 = st.columns(2)

with col_6:
    st.markdown('<div class="btn-footer-green">↓ Ingresos [6]</div>', unsafe_allow_html=True)

with col_7:
    st.markdown('<div class="btn-footer-red">↑ Gastos [7]</div>', unsafe_allow_html=True)
