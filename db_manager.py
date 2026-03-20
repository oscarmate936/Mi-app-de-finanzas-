import sqlite3
import pandas as pd
import os

# Ruta absoluta basada en la ubicación de ESTE archivo (la raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Crear la carpeta data si no existe
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "finanzas.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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
