from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, mail):
        self.id = id_usuario
        self.nombre = nombre
        self.email = mail
