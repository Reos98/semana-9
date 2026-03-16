from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
# Importamos tu conexión real de la carpeta Conexion
from Conexion.conexion import obtener_conexion 

app = Flask(__name__)

# --- CONFIGURACIÓN SQLITE (Semana 12 - Agendar Citas) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    fecha = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# --- SINCRONIZACIÓN DE ARCHIVOS (.txt, .json, .csv) ---
def sincronizar_archivos():
    pacientes = Paciente.query.all()
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "inventario", "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # TXT
    with open(os.path.join(data_dir, "datos.txt"), "w", encoding='utf-8') as f:
        for p in pacientes:
            f.write(f"Paciente: {p.nombre}, Especialidad: {p.especialidad}, Fecha: {p.fecha}\n")

    # JSON
    import json
    lista_json = [{"nombre": p.nombre, "especialidad": p.especialidad, "fecha": p.fecha} for p in pacientes]
    with open(os.path.join(data_dir, "datos.json"), "w", encoding='utf-8') as f:
        json.dump(lista_json, f, indent=4)

    # CSV
    import csv
    with open(os.path.join(data_dir, "datos.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Especialidad", "Fecha"])
        for p in pacientes:
            writer.writerow([p.nombre, p.especialidad, p.fecha])

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    # La página principal ahora muestra tu Misión y Visión
    return render_template('index.html')

@app.route('/agendar')
def pagina_agendar():
    # Esta función sirve para MOSTRAR el formulario de citas
    return render_template('turno.html')

# --- RUTAS DE PROCESAMIENTO (SQLITE) ---

@app.route('/nuevo', methods=['POST'])
def nuevo():
    nombre = request.form.get('nombre')
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')
    
    nuevo_p = Paciente(nombre=nombre, especialidad=especialidad, fecha=fecha)
    db.session.add(nuevo_p)
    db.session.commit()
    sincronizar_archivos()
    return redirect(url_for('ver_datos')) # Te lleva a ver los archivos

@app.route('/datos')
def ver_datos():
    registros_txt = []
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_txt = os.path.join(base_dir, "inventario", "data", "datos.txt")
    
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r", encoding='utf-8') as f:
            registros_txt = f.readlines()
    return render_template('datos.html', registros=registros_txt)

# --- RUTAS MARIADB / MYSQL (Semana 13) ---

@app.route('/usuarios')
def pagina_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=datos)

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    nombre = request.form.get('nombre')
    mail = request.form.get('mail')
    password = request.form.get('password')
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
    cursor.execute(sql, (nombre, mail, password))
    conn.commit() # ¡Importante para HeidiSQL!
    cursor.close()
    conn.close()
    return redirect(url_for('pagina_usuarios'))

@app.route('/reporte_citas')
def reporte_citas():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT e.nombres AS Medico, p.nombre AS Paciente, c.fecha AS Fecha_Cita
        FROM empleado AS e
        JOIN cita AS c ON e.id_empleado = c.id_empleado
        JOIN paciente AS p ON c.id_paciente = p.id_paciente
    """
    cursor.execute(query)
    citas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reporte.html', citas=citas)

if __name__ == '__main__':
    app.run(debug=True)