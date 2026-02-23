from flask import Flask, render_template

app = Flask(__name__)

# 1. RUTA PRINCIPAL (Renderiza index.html)
@app.route('/')
def index():
    return render_template('index.html')

# 2. RUTA SOBRE NOSOTROS (Renderiza about.html)
@app.route('/about')
def about():
    return render_template('about.html')

# 3. RUTA DINÁMICA PARA TURNOS (Renderiza turno.html)
@app.route('/cita/<paciente>')
def ver_cita(paciente):
    # Pasamos la variable 'paciente' a la plantilla
    return render_template('turno.html', paciente=paciente)

# 4. EJECUCIÓN DEL SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)