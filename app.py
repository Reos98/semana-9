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
    return redirect(url_for('index'))

@app.route('/datos')
def ver_datos():
    registros_txt = []
    # ESTA ES LA RUTA QUE VIMOS EN TU GITHUB
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_txt = os.path.join(base_dir, "inventario", "data", "datos.txt")
    
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r", encoding='utf-8') as f:
            registros_txt = f.readlines()
    
    return render_template('datos.html', registros=registros_txt)

if __name__ == '__main__':
    app.run(debug=True)