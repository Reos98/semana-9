from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import csv
import os

app = Flask(__name__)

# --- 2.3 CONFIGURACIÓN DE SQLALCHEMY ---
# Creamos una nueva base de datos para la semana 12
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2.4 MODELO DE DATOS (POO) ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)

# Crear la base de datos y las tablas al iniciar
with app.app_context():
    db.create_all()

# --- 2.2 PERSISTENCIA EN ARCHIVOS LOCALES ---
DATA_DIR = "inventario/data"

def guardar_en_archivos(datos):
    # Asegurar que la carpeta exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 1. Guardar en TXT (Modo append)
    with open(os.path.join(DATA_DIR, "datos.txt"), "a") as f:
        f.write(f"Paciente: {datos['nombre']}, Especialidad: {datos['especialidad']}, Fecha: {datos['fecha']}\n")

    # 2. Guardar en JSON (Corregido para archivos vacíos)
    archivo_json = os.path.join(DATA_DIR, "datos.json")
    lista_json = []
    if os.path.exists(archivo_json) and os.path.getsize(archivo_json) > 0:
        with open(archivo_json, "r") as f:
            try:
                lista_json = json.load(f)
            except json.JSONDecodeError:
                lista_json = []
    
    lista_json.append(datos)
    with open(archivo_json, "w") as f:
        json.dump(lista_json, f, indent=4)

    # 3. Guardar en CSV
    with open(os.path.join(DATA_DIR, "datos.csv"), "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datos['nombre'], datos['especialidad'], datos['fecha']])

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    # Leer datos desde SQLite usando SQLAlchemy
    pacientes = Paciente.query.all()
    return render_template('index.html', pacientes=pacientes)

@app.route('/nuevo', methods=['POST'])
def nuevo():
    # Recibir datos del formulario
    nombre = request.form.get('nombre')
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')

    # Guardar en Base de Datos (SQLAlchemy)
    nuevo_paciente = Paciente(nombre=nombre, especialidad=especialidad, fecha=fecha)
    db.session.add(nuevo_paciente)
    db.session.commit()

    # Guardar en Archivos (TXT, JSON, CSV)
    datos_dict = {'nombre': nombre, 'especialidad': especialidad, 'fecha': fecha}
    guardar_en_archivos(datos_dict)

    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    paciente = Paciente.query.get(id)
    if paciente:
        db.session.delete(paciente)
        db.session.commit()
    return redirect(url_for('index'))

# NUEVA RUTA: Leer y mostrar datos de los archivos
@app.route('/datos')
def ver_datos():
    registros_txt = []
    ruta_txt = os.path.join(DATA_DIR, "datos.txt")
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r") as f:
            registros_txt = f.readlines()
    return render_template('datos.html', registros=registros_txt)

if __name__ == '__main__':
    app.run(debug=True)