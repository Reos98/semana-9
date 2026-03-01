from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --- 1. CLASE PACIENTE (POO) ---
class Paciente:
    def __init__(self, id, nombre, especialidad, fecha):
        self.id = id
        self.nombre = nombre
        self.especialidad = especialidad
        self.fecha = fecha

# --- 2. CONEXIÓN Y CREACIÓN DE TABLA (SQLITE) ---
def conectar_db():
    conexion = sqlite3.connect('turnos.db')
    conexion.row_factory = sqlite3.Row
    # IMPORTANTE: Crear la tabla si no existe para evitar el error 500 en Render
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            especialidad TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conexion.commit()
    return conexion

# --- 3. RUTAS (CRUD) ---
@app.route('/')
def index():
    db = conectar_db()
    # READ: Usamos colecciones (lista de objetos)
    pacientes_db = db.execute('SELECT * FROM pacientes').fetchall()
    db.close()
    
    # Transformamos los datos de la DB en objetos de la clase Paciente
    lista_pacientes = [Paciente(p['id'], p['nombre'], p['especialidad'], p['fecha']) for p in pacientes_db]
    
    return render_template('index.html', pacientes=lista_pacientes)

@app.route('/nuevo', methods=['POST'])
def nuevo():
    nombre = request.form['nombre']
    especialidad = request.form['especialidad']
    fecha = request.form['fecha']
    
    db = conectar_db()
    db.execute('INSERT INTO pacientes (nombre, especialidad, fecha) VALUES (?, ?, ?)',
               (nombre, especialidad, fecha))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = conectar_db()
    db.execute('DELETE FROM pacientes WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)