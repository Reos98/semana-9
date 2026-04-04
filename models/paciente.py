from flask_sqlalchemy import SQLAlchemy

# Nota: Esto se inicializará en app.py, pero definimos la estructura aquí si se requiere
# Aunque el proyecto usa principalmente SQL Crudo para MySQL, mantenemos el modelo SQLITE por compatibilidad con la estructura actual.

def obtener_modelo_paciente(db):
    class Paciente(db.Model):
        __tablename__ = 'pacientes_sqlite' # Evitamos conflicto si se usa en la misma DB
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100))
        especialidad = db.Column(db.String(100))
        fecha = db.Column(db.String(20))
    return Paciente

# Para el SQL Crudo representamos el Paciente como un objeto simple
class PacienteData:
    def __init__(self, nombre, especialidad, fecha):
        self.nombre = nombre
        self.especialidad = especialidad
        self.fecha = fecha
