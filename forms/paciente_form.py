# Este archivo gestiona la validación de los datos que se reciben de los formularios de pacientes.

class PacienteForm:
    @staticmethod
    def validar_datos(nombre, especialidad, fecha):
        if not nombre or not especialidad or not fecha:
            return False, "Faltan datos obligatorios"
        # Aquí puedes agregar más validaciones (ej: formato de fecha, longitud de nombre)
        return True, ""
