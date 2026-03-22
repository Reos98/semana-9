from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import csv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from Conexion.conexion import obtener_conexion 

app = Flask(__name__)
app.secret_key = 'clave_secreta_medturnos_leo' 

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'])
    return None

# --- CONFIGURACIÓN SQLITE (Semana 12) ---
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

# --- RUTAS DE AUTENTICACIÓN (Semana 14) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE mail = %s AND password = %s", (email, password))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            user_obj = Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/registro')
def pagina_registro():
    return render_template('registro.html')

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    nombre = request.form.get('nombre')
    mail = request.form.get('mail')
    password = request.form.get('password')
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)", (nombre, mail, password))
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS PROTEGIDAS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendar')
@login_required
def pagina_agendar():
    return render_template('turno.html')

@app.route('/reporte_citas')
@login_required
def reporte_citas():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT e.nombres AS Medico, p.nombre AS Paciente, c.fecha AS Fecha_Cita FROM empleado AS e JOIN cita AS c ON e.id_empleado = c.id_empleado JOIN paciente AS p ON c.id_paciente = p.id_paciente"
    cursor.execute(query)
    citas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reporte.html', citas=citas)

@app.route('/usuarios')
@login_required 
def pagina_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=datos)


if __name__ == '__main__':
    app.run(debug=True)