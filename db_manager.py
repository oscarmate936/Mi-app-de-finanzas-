import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "finanzas.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Tabla de Transacciones
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tipo TEXT, categoria TEXT, monto REAL, descripcion TEXT
    )''')
    
    # 2. Tabla de Presupuestos
    cursor.execute('''CREATE TABLE IF NOT EXISTS presupuestos (
        categoria TEXT PRIMARY KEY, limite REAL
    )''')
    
    # 3. NUEVA: Configuración de usuario (Sueldo y día de pago)
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracion (
        id INTEGER PRIMARY KEY CHECK (id = 1), salario REAL, dia_pago INTEGER
    )''')
    # Insertar valores por defecto (Sueldo 0, Día 1) si no existen
    cursor.execute('''INSERT OR IGNORE INTO configuracion (id, salario, dia_pago) VALUES (1, 0.0, 1)''')

    # 4. NUEVA: Categorías personalizables
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorias (
        nombre TEXT PRIMARY KEY, tipo TEXT
    )''')
    # Insertar categorías por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("🛒 Supermercado", "Gasto"), ("🚗 Transporte", "Gasto"), ("⚡ Servicios", "Gasto"),
            ("🍔 Restaurantes", "Gasto"), ("🎬 Ocio", "Gasto"), ("🏠 Vivienda", "Gasto"),
            ("💼 Salario Extra", "Ingreso"), ("📈 Inversiones", "Ingreso"), ("🎁 Regalo", "Ingreso")
        ]
        cursor.executemany('INSERT INTO categorias (nombre, tipo) VALUES (?, ?)', defaults)

    conn.commit()
    conn.close()

# --- FUNCIONES DE TRANSACCIONES ---
def add_transaccion(fecha, tipo, categoria, monto, descripcion):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transacciones (fecha, tipo, categoria, monto, descripcion) VALUES (?, ?, ?, ?, ?)', 
                   (fecha, tipo, categoria, monto, descripcion))
    conn.commit()
    conn.close()

def get_transacciones():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transacciones ORDER BY fecha DESC", conn)
    conn.close()
    return df

def delete_transaccion(id_trans):
    """NUEVO: Elimina una transacción por su ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transacciones WHERE id = ?', (id_trans,))
    conn.commit()
    conn.close()

# --- FUNCIONES DE CONFIGURACIÓN (SUELDO) ---
def get_config():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT salario, dia_pago FROM configuracion WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return {"salario": row[0], "dia_pago": row[1]} if row else {"salario": 0.0, "dia_pago": 1}

def update_config(salario, dia_pago):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE configuracion SET salario = ?, dia_pago = ? WHERE id = 1', (salario, dia_pago))
    conn.commit()
    conn.close()

# --- FUNCIONES DE CATEGORÍAS ---
def get_categorias(tipo):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT nombre FROM categorias WHERE tipo = '{tipo}'", conn)
    conn.close()
    return df['nombre'].tolist()

def add_categoria(nombre, tipo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO categorias (nombre, tipo) VALUES (?, ?)', (nombre, tipo))
    conn.commit()
    conn.close()

# --- FUNCIONES DE PRESUPUESTOS ---
def set_presupuesto(categoria, limite):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO presupuestos (categoria, limite) VALUES (?, ?)', (categoria, limite))
    conn.commit()
    conn.close()

def get_presupuestos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM presupuestos", conn)
    conn.close()
    return df