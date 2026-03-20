import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import requests
import uuid
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cash Book Pro", page_icon="💰", layout="centered")

# --- ESTILOS VISUALES (REDISEÑO COMPLETO 'PRO' Y MÓVIL) ---
st.markdown("""
<style>
    /* Ocultar elementos estándar de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    [data-testid="stSidebar"] {border-radius: 20px; padding: 20px; background-color: #f1f3f6;}

    /* Fuente y General */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Titulares Profresionales */
    h1, h2, h3 {
        color: #333;
        font-weight: 700;
        letter-spacing: -1px;
    }

    /* --- Botones Móviles (del prompt original, unificados) --- */
    /* Botón Terciario (Config / Ajustes) - Borde punteado gris */
    button[kind="tertiary"] {
        background-color: #f8f9fa !important;
        border: 2px dashed #007bff !important;
        border-radius: 15px !important;
        padding: 15px !important;
        min-height: 90px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    button[kind="tertiary"]:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,123,255,0.15); }
    button[kind="tertiary"] p { white-space: pre-wrap !important; text-align: center !important; line-height: 1.4 !important; color: #007bff !important; font-weight: 600 !important;}

    /* Botón Secundario (Ingresos) - Verde sólido */
    button[kind="secondary"] {
        background-color: #e8f5e9 !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        min-height: 100px !important;
        box-shadow: 0 4px 6px rgba(76, 175, 80, 0.1) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    button[kind="secondary"]:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(76, 175, 80, 0.2); }
    button[kind="secondary"] p { color: #2e7d32 !important; font-weight: 800 !important; font-size: 18px !important; white-space: pre-wrap !important; text-align: center !important;}

    /* Botón Primario (Gastos) - Rojo sólido */
    button[kind="primary"] {
        background-color: #ffebee !important;
        border: 2px solid #F44336 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        min-height: 100px !important;
        box-shadow: 0 4px 6px rgba(244, 67, 54, 0.1) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    button[kind="primary"]:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(244, 67, 54, 0.2); }
    button[kind="primary"] p { color: #c62828 !important; font-weight: 800 !important; font-size: 18px !important; white-space: pre-wrap !important; text-align: center !important;}

    /* --- Tarjetas Profesionales --- */
    /* Tarjeta Total Card (Saldo Neto) */
    .total-card {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 123, 255, 0.25);
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .total-label { font-size: 16px; opacity: 0.8; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;}
    .total-value { font-size: 48px; font-weight: 800; margin: 0; }
    
    /* Tarjeta de Cuenta Individual */
    .account-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #007bff;
        text-align: center;
    }
    .account-name { font-size: 14px; color: #6c757d; font-weight: 600; text-transform: uppercase; margin-bottom: 3px;}
    .account-balance { font-size: 24px; font-weight: 700; color: #333;}

    /* Tarjetas Métricas Comparativas MoM */
    .mom-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .mom-label { font-size: 12px; color: #6c757d; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .mom-value { font-size: 20px; font-weight: 700; color: #333;}
    .mom-delta-up { font-size: 12px; color: #F44336; font-weight: 600;}
    .mom-delta-down { font-size: 12px; color: #4CAF50; font-weight: 600;}
    
    /* --- Estilo de Pestañas --- */
    div[data-testid="stTabs"] { border: 0;}
    div[data-testid="stTabBar"] button { font-weight: 600; font-size: 16px; color: #6c757d;}
    div[data-testid="stTabBar"] button[aria-selected="true"] { color: #007bff; border-bottom: 3px solid #007bff !important;}
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN Y DATOS (CON AUTOCURACIÓN DEL PROBLEMA KEYERROR) ---
try:
    BIN_ID = st.secrets["bin_id"]
    API_KEY = st.secrets["api_key"]
except Exception as e:
    st.error("⚠️ Configura 'bin_id' y 'api_key' en los Secrets de Streamlit.")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

@st.cache_data(ttl=600)
def get_db():
    try:
        res = requests.get(URL, headers={"X-Master-Key": API_KEY})
        data = res.json().get('record', {})
        
        # Estructura base por defecto
        default_settings = {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"], "fecha": "No definida"}
        
        # Validar y reparar estructura (SOLUCIÓN AL KEYERROR ANTERIOR)
        if "transactions" not in data: data["transactions"] = []
        if "recurrentes" not in data: data["recurrentes"] = []
        
        if "settings" not in data:
            data["settings"] = default_settings
        else:
            # Si 'settings' existe, aseguramos que tenga todas las llaves nuevas (evita el KeyError)
            for k, v in default_settings.items():
                if k not in data["settings"]:
                    data["settings"][k] = v
        
        return data
    except Exception as e:
        st.warning(f"Error de conexión: Usando datos de respaldo. {e}")
        return {"transactions": [], "settings": {"sueldo": 0.0, "presupuesto": 0.0, "cuentas": ["Efectivo", "Banco"]}, "recurrentes": []}

def save_db(data):
    requests.put(URL, json=data, headers=HEADERS)
    st.cache_data.clear()

db = get_db()

# --- LÓGICA CORE ---
def add_trans(t_type, cat, amt, note, account, date_str=None):
    t_id = str(uuid.uuid4())[:8]
    nueva = {
        "id": t_id, 
        "date": date_str if date_str else datetime.now().strftime("%Y-%m-%d"), 
        "type": t_type, 
        "category": cat, 
        "amount": float(amt), 
        "note": note,
        "account": account
    }
    db["transactions"].append(nueva)
    save_db(db)

# --- PROCESAMIENTO DE DATOS ---
df = pd.DataFrame(db["transactions"])
columnas_necesarias = ["id", "date", "type", "category", "amount", "note", "account"]

if df.empty:
    df = pd.DataFrame(columns=columnas_necesarias)
else:
    for col in columnas_necesarias:
        if col not in df.columns: df[col] = "N/A"
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

# Filtros Temporales Sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>🔍 FILTRO</h2>", unsafe_allow_html=True)
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_actual = datetime.now().month
año_actual = datetime.now().year
sel_mes = st.sidebar.selectbox("Mes", range(1, 13), index=mes_actual-1, format_func=lambda x: meses_nombres[x-1])
sel_año = st.sidebar.number_input("Año", 2024, 2030, año_actual)

df_mes = df[(df['date'].dt.month == sel_mes) & (df['date'].dt.year == sel_año)]
prev_date = datetime(sel_año, sel_mes, 1) - timedelta(days=1)
df_prev = df[(df['date'].dt.month == prev_date.month) & (df['date'].dt.year == prev_date.year)]

# Cálculos Totales
# Sueldo se suma al total disponible por defecto
total_sueldo = float(db["settings"].get("sueldo", 0))
ingresos_hist = df[df['type'] == 'Ingreso']['amount'].sum()
gastos_hist = df[df['type'] == 'Gasto']['amount'].sum()
saldo_neto_total = total_sueldo + ingresos_hist - gastos_hist

# Métricas del mes para MoM
g_mes = df_mes[df_mes['type'] == 'Gasto']['amount'].sum()
i_mes = df_mes[df_mes['type'] == 'Ingreso']['amount'].sum()
g_prev = df_prev[df_prev['type'] == 'Gasto']['amount'].sum()
dif_gasto_mom = g_mes - g_prev

# --- DIALOGS (Blindados) ---
@st.dialog("⚙️ AJUSTES PRO")
def config_dialog():
    st.subheader("Configuración General")
    s = st.number_input("Sueldo Base Mensual ($)", value=float(db["settings"].get("sueldo", 0)))
    p = st.number_input("Meta de Gasto Mensual ($)", value=float(db["settings"].get("presupuesto", 0)))
    
    st.divider()
    st.subheader("🔄 Gastos Recurrentes (Suscripciones)")
    r_cat = st.selectbox("Categoría", ["Servicios", "Suscripciones", "Vivienda", "Ocio", "Otros"])
    r_amt = st.number_input("Monto Fijo ($)", min_value=0.0)
    r_note = st.text_input("Nombre (ej. Netflix, Renta)", placeholder="Ej. Spotify")
    cuentas_conf = db["settings"].get("cuentas", ["Banco"])
    r_acc = st.selectbox("Cuenta de cargo", cuentas_conf)
    
    if st.button("➕ Añadir Gasto Fijo", use_container_width=True):
        if r_note and r_amt > 0:
            db["recurrentes"].append({"category": r_cat, "amount": r_amt, "note": r_note, "account": r_acc})
            save_db(db)
            st.success(f"{r_note} añadido")
            st.rerun()

    if db.get("recurrentes"):
        with st.expander("Ver suscripciones activas"):
            for i, r in enumerate(db["recurrentes"]):
                col_r1, col_r2 = st.columns([0.8, 0.2])
                col_r1.write(f"**{r['note']}**: ${r['amount']} ({r['account']})")
                if col_r2.button("🗑️", key=f"del_rec_{i}"):
                    db["recurrentes"].pop(i)
                    save_db(db)
                    st.rerun()

    st.write("---")
    if st.button("💾 GUARDAR TODOS LOS CAMBIOS", use_container_width=True, type="primary"):
        db["settings"]["sueldo"] = s
        db["settings"]["presupuesto"] = p
        save_db(db)
        st.success("Configuración actualizada")
        st.rerun()

@st.dialog("➕ NUEVO MOVIMIENTO")
def trans_dialog(tipo):
    st.subheader(f"Registrar {tipo}")
    cuentas_trans = db["settings"].get("cuentas", ["Banco", "Efectivo"])
    acc = st.selectbox("Selecciona Cuenta", cuentas_trans)
    
    if tipo == "Gasto":
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Servicios", "Ocio", "Salud", "Educación", "Suscripción", "Otros"])
    else:
        cat = "Ingreso Extra"

    amt = st.number_input("Monto ($)", min_value=0.01, step=1.0)
    note = st.text_input("Nota o Concepto", placeholder="Ej. Compra supermercado")
    date = st.date_input("Fecha", datetime.now())
    
    st.write("---")
    if st.button(f"REGISTRAR {tipo.upper()}", use_container_width=True):
        if amt > 0:
            add_trans(tipo, cat, amt, note, acc, date.strftime("%Y-%m-%d"))
            st.success("Registrado correctamente")
            st.rerun()

# --- INTERFAZ PRINCIPAL (REDISENO PRO) ---
st.markdown("<h1 style='text-align: center; color: #007bff; margin-bottom: 0px;'>CASHBOOK</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #6c757d; margin-top: -10px; font-weight: 500;'>Control Financiero · {meses_nombres[sel_mes-1]} {sel_año}</p>", unsafe_allow_html=True)

tab_dash, tab_hist, tab_analisis = st.tabs(["🏠 DASHBOARD", "📝 HISTORIAL", "📊 REPORTES PRO"])

with tab_dash:
    # 1. Card Principal Neto Total (PRO)
    st.markdown(f"""
    <div class="total-card">
        <div class="total-label">Saldo Neto Disponible</div>
        <div class="total-value">${saldo_neto_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # 2. Métricas Comparativas MoM (PRO HTML cards)
    col_mom1, col_mom2, col_mom3 = st.columns(3, gap="small")
    
    presupuesto = db["settings"].get("presupuesto", 0)
    with col_mom1:
        st.markdown(f"""<div class="mom-card"><div class="mom-label">INGRESOS {meses_nombres[sel_mes-1]}</div>
        <div class="mom-value">${i_mes:,.2f}</div></div>""", unsafe_allow_html=True)
    with col_mom2:
        icon_delta = "<span class='mom-delta-up'>↑</span>" if dif_gasto_mom > 0 else "<span class='mom-delta-down'>↓</span>"
        st.markdown(f"""<div class="mom-card"><div class="mom-label">GASTOS {meses_nombres[sel_mes-1]}</div>
        <div class="mom-value">${g_mes:,.2f}</div><div style="font-size:12px; color:#666;">{icon_delta} ${dif_gasto_mom:+,.0f} vs mes ant.</div></div>""", unsafe_allow_html=True)
    with col_mom3:
        gasto_progreso = f"({g_mes/presupuesto*100:.0f}%)" if presupuesto > 0 else ""
        border_pres = "5px solid #F44336" if g_mes > presupuesto and presupuesto > 0 else "1px solid #eee"
        st.markdown(f"""<div class="mom-card" style="border-left: {border_pres}"><div class="mom-label">METAS {meses_nombres[sel_mes-1]}</div>
        <div class="mom-value">${presupuesto:,.0f}</div><div style="font-size:12px; color:#666;">{gasto_progreso} Gastado</div></div>""", unsafe_allow_html=True)

    st.write("---")

    # 3. Acciones rápidas (Botones Móviles PRO del prompt original con \n)
    col_b1, col_b2 = st.columns(2, gap="small")
    with col_b1:
        if st.button(f"↑ GASTOS\nRegistrar Nuevo", type="primary", use_container_width=True): trans_dialog("Gasto")
    with col_b2:
        if st.button(f"↓ INGRESOS\nRegistrar Nuevo", type="secondary", use_container_width=True): trans_dialog("Ingreso")
    
    st.write("")
    col_b3 = st.columns(1)[0]
    with col_b3:
        if st.button(f"⚙️ AJUSTES Y METAS\nConfigurar App", type="tertiary", use_container_width=True): config_dialog()

    # 4. Saldos por Cuenta (PRO HTML cards)
    st.write("")
    st.subheader("🏦 Mis Cuentas")
    cuentas_activas = db["settings"].get("cuentas", ["Efectivo", "Banco"])
    
    # Crear dinámicamente el HTML para las tarjetas de cuenta
    html_cuentas = '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'
    for acc in cuentas_activas:
        ing_acc = df[ (df['type']=='Ingreso') & (df['account']==acc) ]['amount'].sum()
        gas_acc = df[ (df['type']=='Gasto') & (df['account']==acc) ]['amount'].sum()
        # Sueldo se suma a Banco por defecto
        bal = (total_sueldo if acc == "Banco" else 0) + ing_acc - gas_acc
        
        html_cuentas += f"""
        <div class="account-card" style="flex: 1; min-width: 150px;">
            <div class="account-name">{acc}</div>
            <div class="account-balance">${bal:,.2f}</div>
        </div>
        """
    html_cuentas += '</div>'
    st.markdown(html_cuentas, unsafe_allow_html=True)

    # 5. Botón Mágico Recurrentes
    if db.get("recurrentes"):
        st.write("")
        if st.button(f"🔄 APLICAR AUTOMÁTICAMENTE SUSCRIPCIONES ({len(db.get('recurrentes'))})", use_container_width=True):
            with st.spinner("Registrando gastos..."):
                for r in db["recurrentes"]:
                    add_trans("Gasto", r["category"], r["amount"], f"AUTO: {r['note']}", r["account"])
                st.success("Suscripciones del mes registradas")
                st.rerun()

with tab_hist:
    st.markdown("### 📝 Historial Completo")
    
    st.dataframe(df_mes.sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR BACKUP COMPLETO (CSV)", data=csv, file_name=f"cashbook_backup_{datetime.now().strftime('%Y%m%d')}.csv", use_container_width=True)

    st.divider()
    with st.expander("📥 Carga Masiva desde CSV"):
        st.write("Sube tu archivo con columnas: date, type, category, amount, note, account")
        uploaded_file = st.file_uploader("Sube CSV", type="csv")
        if uploaded_file:
            try:
                new_data = pd.read_csv(uploaded_file)
                if st.button("CONFIRMAR IMPORTACIÓN MASIVA"):
                    for _, row in new_data.iterrows():
                        add_trans(row['type'], row['category'], row['amount'], row['note'], row['account'], str(row['date']))
                    st.success("Importado con éxito")
                    st.rerun()
            except:
                st.error("Formato de CSV no válido.")

with tab_analisis:
    st.markdown(f"### 📊 Reporte de {meses_nombres[sel_mes-1]}")
    df_gastos_f = df_mes[df_mes['type']=='Gasto']
    
    if not df_gastos_f.empty:
        # Gráfico Sunburst PRO (Cuenta -> Categoría)
        fig = px.sunburst(df_gastos_f, path=['account', 'category'], values='amount', 
                          title="Gastos: Distribución por Cuenta y Categoría",
                          color_discrete_sequence=px.colors.qualitative.Plotly,
                          template="plotly_white")
        fig.update_layout(title_font_size=18)
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparativa Diaria
        df_diario = df_gastos_f.groupby(df_gastos_f['date'].dt.day)['amount'].sum().reset_index()
        fig_bar = px.bar(df_diario, x='date', y='amount', title="Monto de Gasto por Día del Mes", labels={'date':'Día', 'amount':'Monto ($)'}, template="plotly_white")
        fig_bar.update_traces(marker_color='#F44336')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay gastos registrados para graficar en este período.")
