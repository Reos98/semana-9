from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cita/<paciente>')
def ver_cita(paciente):
    return render_template('turno.html', paciente=paciente)

if __name__ == '__main__':
    app.run(debug=True)