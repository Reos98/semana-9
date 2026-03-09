from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import csv
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE PERSISTENCIA (Semana 12) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)

# Crear tablas automáticamente
with app.app_context():
    db.create_all()

# --- PERSISTENCIA EN ARCHIVOS ---
DATA_DIR = "inventario/data"

def guardar_en_archivos(datos):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # A. Guardar en TXT
    with open(os.path.join(DATA_DIR, "datos.txt"), "a") as f:
        f.write(f"Paciente: {datos['nombre']} | Especialidad: {datos['especialidad']} | Fecha: {datos['fecha']}\n")

    # B. Guardar en JSON
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

    # C. Guardar en CSV
    with open(os.path.join(DATA_DIR, "datos.csv"), "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datos['nombre'], datos['especialidad'], datos['fecha']])

# --- RUTAS ---

@app.route('/')
def index():
    pacientes = Paciente.query.all()
    return render_template('index.html', pacientes=pacientes)

@app.route('/nuevo', methods=['POST'])
def nuevo():
    nombre = request.form.get('nombre')
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')

    nuevo_p = Paciente(nombre=nombre, especialidad=especialidad, fecha=fecha)
    db.session.add(nuevo_p)
    db.session.commit()

    guardar_en_archivos({'nombre': nombre, 'especialidad': especialidad, 'fecha': fecha})
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    paciente = Paciente.query.get(id)
    if paciente:
        db.session.delete(paciente)
        db.session.commit()
    return redirect(url_for('index'))

# RUTA ÚNICA PARA VER ARCHIVOS (Sin duplicados)
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