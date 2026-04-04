from conexion.conexion import obtener_conexion
from models.usuario import Usuario

def cargar_usuario(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'], user_data.get('rol', 'usuario'))
    return None

def validar_login(email, password):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE mail = %s AND password = %s", (email, password))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'], user_data.get('rol', 'usuario'))
    return None

def registrar_usuario(nombre, mail, password):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)", (nombre, mail, password))
    conn.commit()
    cursor.close()
    conn.close()

def actualizar_datos_usuario(usuario_id, nuevo_nombre=None, nueva_pass=None):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    if nuevo_nombre and nueva_pass:
        query = "UPDATE usuarios SET nombre = %s, password = %s WHERE id_usuario = %s"
        cursor.execute(query, (nuevo_nombre, nueva_pass, usuario_id))
    elif nuevo_nombre:
        query = "UPDATE usuarios SET nombre = %s WHERE id_usuario = %s"
        cursor.execute(query, (nuevo_nombre, usuario_id))
    elif nueva_pass:
        query = "UPDATE usuarios SET password = %s WHERE id_usuario = %s"
        cursor.execute(query, (nueva_pass, usuario_id))
        
    conn.commit()
    cursor.close()
    conn.close()
    return True
