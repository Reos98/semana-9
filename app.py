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
    # Traemos las citas de SQLite
    citas_db = Paciente.query.all()
    
    # Mapa de médicos por especialidad
    medicos_especialistas = {
        "Odontología": "Dr. Ricardo Javier",
        "Medicina General": "Dra. Valeria Sofía",
        "Pediatría": "Dr. Andrés Felipe",
        "Cardiología": "Dra. Marlene Tipán"
    }

    # Creamos una lista nueva con el nombre del médico incluido
    citas_completas = []
    for cita in citas_db:
        # Buscamos el médico. Si no hay, ponemos 'Por asignar'
        medico = medicos_especialistas.get(cita.especialidad, "Médico de Turno")
        
        citas_completas.append({
            "nombre": cita.nombre,
            "especialidad": cita.especialidad,
            "fecha": cita.fecha,
            "medico": medico # <-- Aquí añadimos el nombre del médico
        })

    return render_template('reporte.html', citas=citas_completas)

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

# --- SINCRONIZACIÓN DE ARCHIVOS CORREGIDA ---
def sincronizar_archivos():
    # 1. Obtenemos los datos actuales de la base de datos SQLite
    pacientes = Paciente.query.all()
    
    # 2. Definimos las rutas de guardado
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "inventario", "data")
    
    # Si la carpeta no existe, la creamos
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 3. Guardar en TXT
    with open(os.path.join(data_dir, "datos.txt"), "w", encoding='utf-8') as f:
        for p in pacientes:
            f.write(f"Paciente: {p.nombre}, Especialidad: {p.especialidad}, Fecha: {p.fecha}\n")

    # 4. Guardar en JSON
    import json
    lista_json = [{"nombre": p.nombre, "especialidad": p.especialidad, "fecha": p.fecha} for p in pacientes]
    with open(os.path.join(data_dir, "datos.json"), "w", encoding='utf-8') as f:
        json.dump(lista_json, f, indent=4)

    # 5. Guardar en CSV
    import csv
    with open(os.path.join(data_dir, "datos.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Especialidad", "Fecha"]) # Encabezados
        for p in pacientes:
            writer.writerow([p.nombre, p.especialidad, p.fecha])

@app.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    nombre = request.form.get('nombre')
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')
    
    if nombre and especialidad and fecha:
        # CONEXIÓN A LA NUBE (Aiven)
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Insertamos en la tabla de la nube (asegúrate de que la tabla 'paciente' exista en Aiven)
        sql = "INSERT INTO paciente (nombre, especialidad, fecha) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, especialidad, fecha))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # (Opcional) Sigues sincronizando archivos planos si el profesor lo pide
        sincronizar_archivos()
        
        flash('¡Cita guardada permanentemente en la nube!', 'success')
        return redirect(url_for('index'))
    
    return "Error al agendar", 400


if __name__ == '__main__':
    app.run(debug=True)