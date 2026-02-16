from flask import Flask

app = Flask(__name__)

# Ruta Principal para tu Sistema de Turnos
@app.route('/')
def inicio():
    return "<h1>Bienvenido al Sistema de Turnos - Centro Médico</h1><p>Gestiona tus citas aquí.</p>"

# Ruta Dinámica para pacientes
@app.route('/cita/<paciente>')
def ver_cita(paciente):
    return f"Hola {paciente}, tu turno está confirmado."

# ESTO ES LO QUE FALTA: La instrucción para arrancar el servidor
if __name__ == '__main__':
    app.run(debug=True)