import sqlite3

def conectar_db():
    conexion = sqlite3.connect('turnos.db')
    return conexion

def crear_tabla():
    conexion = conectar_db()
    cursor = conexion.cursor()
    # Tabla para el "Inventario" de turnos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            especialidad TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

crear_tabla()