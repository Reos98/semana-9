from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuración de Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    fecha = db.Column(db.String(20))

with app.app_context():
    db.create_all()

def sincronizar_archivos():
    # Obtenemos todos los pacientes actuales de la base de datos
    pacientes = Paciente.query.all()
    
    # Definimos la ruta de la carpeta de datos
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "inventario", "data")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 1. Sincronizar TXT
    with open(os.path.join(data_dir, "datos.txt"), "w", encoding='utf-8') as f:
        for p in pacientes:
            f.write(f"Paciente: {p.nombre}, Especialidad: {p.especialidad}, Fecha: {p.fecha}\n")

    # 2. Sincronizar JSON
    import json
    lista_json = [{"nombre": p.nombre, "especialidad": p.especialidad, "fecha": p.fecha} for p in pacientes]
    with open(os.path.join(data_dir, "datos.json"), "w", encoding='utf-8') as f:
        json.dump(lista_json, f, indent=4)

    # 3. Sincronizar CSV
    import csv
    with open(os.path.join(data_dir, "datos.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Especialidad", "Fecha"]) # Encabezados
        for p in pacientes:
            writer.writerow([p.nombre, p.especialidad, p.fecha])
# RUTAS
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
    
    # ¡Sincronizamos con los archivos!
    sincronizar_archivos()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    paciente = Paciente.query.get(id)
    if paciente:
        db.session.delete(paciente)
        db.session.commit()
        
        # ¡Sincronizamos para que se borre también del TXT!
        sincronizar_archivos()
    return redirect(url_for('index'))

@app.route('/datos')
def ver_datos():
    registros_txt = []
    # ESTA ES LA RUTA QUE VIMOS EN TU GITHUB
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_txt = os.path.join(base_dir, "inventario", "data", "datos.txt")
    
    if os.path.exists(ruta_txt):
        print(ruta_txt)
        with open(ruta_txt, "r", encoding='latin1') as f:
            registros_txt = f.readlines()
    
    return render_template('datos.html', registros=registros_txt)

if __name__ == '__main__':
    app.run(debug=True)