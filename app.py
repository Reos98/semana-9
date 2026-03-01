from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --- CLASES (POO) ---
class Paciente:
    def __init__(self, id, nombre, especialidad, fecha):
        self.id = id
        self.nombre = nombre
        self.especialidad = especialidad
        self.fecha = fecha

class GestionTurnos:
    def __init__(self):
        self.coleccion_dict = {} # Diccionario para búsqueda rápida por ID

    def obtener_todos(self):
        conexion = sqlite3.connect('turnos.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM pacientes")
        datos = cursor.fetchall()
        conexion.close()
        
        lista_objetos = []
        for d in datos:
            obj = Paciente(d[0], d[1], d[2], d[3])
            lista_objetos.append(obj)
            self.coleccion_dict[d[0]] = obj # Sincroniza el diccionario
        return lista_objetos

# --- RUTAS ---
@app.route('/')
def index():
    gestion = GestionTurnos()
    lista_pacientes = gestion.obtener_todos()
    return render_template('index.html', pacientes=lista_pacientes)

@app.route('/nuevo_turno', methods=['POST'])
def nuevo_turno():
    nombre = request.form['nombre']
    especialidad = request.form['especialidad']
    fecha = request.form['fecha']
    
    conexion = sqlite3.connect('turnos.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO pacientes (nombre, especialidad, fecha) VALUES (?, ?, ?)", 
                   (nombre, especialidad, fecha))
    conexion.commit()
    conexion.close()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    conexion = sqlite3.connect('turnos.db')
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)