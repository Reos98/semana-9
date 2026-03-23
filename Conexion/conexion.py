import mysql.connector
import os

def obtener_conexion():
    # Estas variables las configuraremos en Render después
    # Si no existen (como en tu PC local), usará los valores que tú pongas aquí
    return mysql.connector.connect(
        host = os.getenv('DB_HOST', 'localhost'), 
        user = os.getenv('DB_USER', 'root'), 
        password = os.getenv('DB_PASSWORD', '123456'), 
        database = os.getenv('DB_NAME', 'consultorio_medico'),
        port = int(os.getenv('DB_PORT', 3306))
    )