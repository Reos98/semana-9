from conexion.conexion import obtener_conexion
import mysql.connector

def migrar_admin():
    print("Iniciando migración para Usuario Maestro...")
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        # 1. Añadir columna 'rol' a tabla usuarios
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) DEFAULT 'usuario'")
            print("- Columna 'rol' añadida a 'usuarios'.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column
                print("- Columna 'rol' ya existe.")
            else:
                print(f"- Error al añadir 'rol': {err}")

        # 2. Insertar/Actualizar Usuario Maestro (admin@gmail.com / 123456Byron.)
        # Buscamos si existe
        cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", ('admin@gmail.com',))
        admin = cursor.fetchone()
        
        if admin:
            # Si existe, actualizamos rol y contraseña
            cursor.execute("""
                UPDATE usuarios 
                SET rol = 'admin', password = %s, nombre = 'Administrador Maestro' 
                WHERE mail = %s
            """, ('123456Byron.', 'admin@gmail.com'))
            print("- Usuario admin@gmail.com actualizado como Administrador.")
        else:
            # Si no existe, lo creamos
            cursor.execute("""
                INSERT INTO usuarios (nombre, mail, password, rol) 
                VALUES (%s, %s, %s, %s)
            """, ('Administrador Maestro', 'admin@gmail.com', '123456Byron.', 'admin'))
            print("- Usuario admin@gmail.com creado como Administrador.")

        # 3. Limpieza: Asegurar que las citas tengan un id_usuario (por si hay huérfanas)
        # Obtenemos el ID del admin para las huérfanas
        cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", ('admin@gmail.com',))
        id_admin = cursor.fetchone()[0]
        
        cursor.execute("UPDATE cita SET id_usuario = %s WHERE id_usuario IS NULL OR id_usuario = 0", (id_admin,))
        print(f"- Citas huérfanas asignadas al Administrador (ID: {id_admin}).")

        conn.commit()
        cursor.close()
        conn.close()
        print("¡Migración completada exitosamente!")
        
    except Exception as e:
        print(f"Error crítico en la migración: {e}")

if __name__ == "__main__":
    migrar_admin()
