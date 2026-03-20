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
    # Tabla original de transacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT,
            categoria TEXT,
            monto REAL,
            descripcion TEXT
        )
    ''')
    # NUEVA TABLA: Para guardar los límites de presupuesto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            categoria TEXT PRIMARY KEY,
            limite REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_transaccion(fecha, tipo, categoria, monto, descripcion):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (fecha, tipo, categoria, monto, descripcion)
        VALUES (?, ?, ?, ?, ?)
    ''', (fecha, tipo, categoria, monto, descripcion))
    conn.commit()
    conn.close()

def get_transacciones():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transacciones ORDER BY fecha DESC", conn)
    conn.close()
    return df

# --- NUEVAS FUNCIONES PARA PRESUPUESTOS ---
def set_presupuesto(categoria, limite):
    """Guarda o actualiza el límite de una categoría."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # INSERT OR REPLACE actualiza si la categoría ya existe
    cursor.execute('''
        INSERT OR REPLACE INTO presupuestos (categoria, limite)
        VALUES (?, ?)
    ''', (categoria, limite))
    conn.commit()
    conn.close()

def get_presupuestos():
    """Obtiene todos los presupuestos configurados."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM presupuestos", conn)
    conn.close()
    return df
