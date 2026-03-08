from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json, csv, os

app = Flask(__name__)

# Configuración de SQLite con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos_v2.db'
db = SQLAlchemy(app)

# --- 2.4 DEFINICIÓN DEL MODELO (POO + ORM) ---
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)

# Crear la base de datos automáticamente
with app.app_context():
    db.create_all()

# --- 2.2 PERSISTENCIA EN ARCHIVOS (Funciones auxiliares) ---
DATA_DIR = "inventario/data/"

def guardar_en_archivos(datos):
    # Guardar en TXT (open mode 'a' para agregar)
    with open(os.path.join(DATA_DIR, "datos.txt"), "a") as f:
        f.write(f"{datos['nombre']}, {datos['especialidad']}, {datos['fecha']}\n")
    
    # Guardar en JSON
    archivo_json = os.path.join(DATA_DIR, "datos.json")
    lista_json = []
    if os.path.exists(archivo_json):
        with open(archivo_json, "r") as f:
            lista_json = json.load(f)
    lista_json.append(datos)
    with open(archivo_json, "w") as f:
        json.dump(lista_json, f, indent=4)

    # Guardar en CSV
    with open(os.path.join(DATA_DIR, "datos.csv"), "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datos['nombre'], datos['especialidad'], datos['fecha']])

# --- RUTAS ---
@app.route('/')
def index():
    # Leer desde SQLite usando el ORM
    pacientes = Paciente.query.all()
    return render_template('index.html', pacientes=pacientes)

@app.route('/nuevo', methods=['POST'])
def nuevo():
    datos_form = {
        'nombre': request.form['nombre'],
        'especialidad': request.form['especialidad'],
        'fecha': request.form['fecha']
    }
    
    # 1. Guardar en SQLite (SQLAlchemy)
    nuevo_p = Paciente(nombre=datos_form['nombre'], 
                       especialidad=datos_form['especialidad'], 
                       fecha=datos_form['fecha'])
    db.session.add(nuevo_p)
    db.session.commit()
    
    # 2. Guardar en Archivos Locales
    guardar_en_archivos(datos_form)
    
    return redirect(url_for('index'))

@app.route('/ver_archivos')
def ver_archivos():
    # Leer TXT para mostrar en la nueva plantilla datos.html
    registros_txt = []
    with open(os.path.join(DATA_DIR, "datos.txt"), "r") as f:
        registros_txt = f.readlines()
    return render_template('datos.html', registros=registros_txt)

@app.route('/datos')
def ver_datos():
    registros = []
    # Leemos el archivo TXT para demostrar la persistencia
    if os.path.exists("inventario/data/datos.txt"):
        with open("inventario/data/datos.txt", "r") as f:
            registros = f.readlines()
    return render_template('datos.html', registros=registros)

if __name__ == '__main__':
    app.run(debug=True)