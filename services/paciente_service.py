from conexion.conexion import obtener_conexion
import os
import json

def obtener_reporte_pacientes():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    # Ahora hacemos un JOIN entre 'cita' y 'paciente' para traer los datos relacionados (3 tablas: cita, paciente y médico-hardcoded)
    query = """
        SELECT p.nombre, c.especialidad, c.fecha, c.id_cita 
        FROM cita c
        JOIN paciente p ON c.id_paciente = p.id_paciente
        ORDER BY c.id_cita DESC
    """
    cursor.execute(query)
    citas_db = cursor.fetchall()
    cursor.close()
    conn.close()
    
    medicos_especialistas = {
        "Odontología": "Dr. Ricardo Javier",
        "Medicina General": "Dra. Valeria Sofía",
        "Pediatría": "Dr. Andrés Felipe",
        "Cardiología": "Dra. Marlene Tipán"
    }

    citas_para_tabla = []
    for cita in citas_db:
        especialidad = cita.get('especialidad') or "Medicina General"
        medico = medicos_especialistas.get(especialidad, "Médico de Turno")
        citas_para_tabla.append({
            "id_cita": cita['id_cita'],
            "nombre": cita['nombre'],
            "especialidad": especialidad,
            "fecha": str(cita.get('fecha')) or "Sin fecha",
            "medico": medico
        })
    return citas_para_tabla

def agendar_nuevo_paciente(nombre, especialidad, fecha, id_usuario=None):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # 1. Verificar si el paciente ya existe por nombre
    cursor.execute("SELECT id_paciente FROM paciente WHERE nombre = %s", (nombre,))
    res = cursor.fetchone()
    
    if res:
        id_paciente = res[0]
    else:
        # 2. Si no existe, crear el paciente (Tabla 1)
        cursor.execute("INSERT INTO paciente (nombre) VALUES (%s)", (nombre,))
        id_paciente = cursor.lastrowid
        
    # 3. Crear la cita (Tabla 2) relacionada con el paciente y el usuario (Tabla 3)
    # Esto cumple con el requisito de 3 tablas relacionadas: Usuarios -> Cita <- Paciente
    cursor.execute("""
        INSERT INTO cita (fecha, especialidad, id_paciente, id_usuario, estado) 
        VALUES (%s, %s, %s, %s, 'Programada')
    """, (fecha, especialidad, id_paciente, id_usuario))
    
    conn.commit()
    cursor.close()
    conn.close()
    
def sincronizar_archivos_data():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        # Sincronizamos los datos unidos para el archivo
        query = "SELECT p.nombre, c.especialidad, c.fecha FROM cita c JOIN paciente p ON c.id_paciente = p.id_paciente"
        cursor.execute(query)
        pacientes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        data_dir = os.path.join(os.getcwd(), "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        with open(os.path.join(data_dir, "datos.txt"), "w", encoding='utf-8') as f:
            for p in pacientes:
                f.write(f"Paciente: {p['nombre']}, Especialidad: {p['especialidad']}, Fecha: {p['fecha']}\n")

        # El JSON usa los strings de fecha
        with open(os.path.join(data_dir, "datos.json"), "w", encoding='utf-8') as f:
            json.dump([ {k: str(v) for k, v in item.items()} for item in pacientes ], f, indent=4)
            
    except Exception as e:
        print(f"DEBUG - Error en sincronización: {str(e)}")

def generar_pdf_reporte(citas):
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Reporte de Citas MedTurnos Leo', 0, 1, 'C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Encabezados de tabla
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(50, 10, 'Médico', 1, 0, 'C', 1)
    pdf.cell(50, 10, 'Paciente', 1, 0, 'C', 1)
    pdf.cell(50, 10, 'Especialidad', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Fecha', 1, 1, 'C', 1)
    
    # Datos
    for cita in citas:
        pdf.cell(50, 10, cita['medico'][:25], 1)
        pdf.cell(50, 10, cita['nombre'][:25], 1)
        pdf.cell(50, 10, cita['especialidad'][:25], 1)
        pdf.cell(40, 10, cita['fecha'], 1, 1)
        
    return pdf.output()

def obtener_cita_id(id_cita):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    # Join para traer el nombre del paciente también
    query = """
        SELECT c.*, p.nombre 
        FROM cita c
        JOIN paciente p ON c.id_paciente = p.id_paciente
        WHERE c.id_cita = %s
    """
    cursor.execute(query, (id_cita,))
    cita = cursor.fetchone()
    cursor.close()
    conn.close()
    return cita

def actualizar_cita(id_cita, especialidad, fecha):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cita 
        SET especialidad = %s, fecha = %s 
        WHERE id_cita = %s
    """, (especialidad, fecha, id_cita))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_cita(id_cita):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cita WHERE id_cita = %s", (id_cita,))
    conn.commit()
    cursor.close()
    conn.close()
