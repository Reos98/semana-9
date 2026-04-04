from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os

# Importamos servicios y modelos (la arquitectura modular requerida)
from models.usuario import Usuario
from services.usuario_service import cargar_usuario, validar_login, registrar_usuario
from services.paciente_service import (
    obtener_reporte_pacientes, 
    agendar_nuevo_paciente, 
    sincronizar_archivos_data,
    obtener_cita_id,
    actualizar_cita,
    eliminar_cita,
    generar_pdf_reporte
)
from forms.paciente_form import PacienteForm
from flask import send_file
import io
from conexion.conexion import obtener_conexion

# Reparación automática de base de datos al iniciar
def migrar_db():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DESCRIBE cita")
        columnas = [row[0] for row in cursor.fetchall()]
        
        # Asegurar columna 'especialidad'
        if 'especialidad' not in columnas:
            cursor.execute("ALTER TABLE cita ADD COLUMN especialidad VARCHAR(100) DEFAULT 'Medicina General'")
            print("DB MIGRADA: Columna 'especialidad' añadida.")
        
        # Asegurar columna 'id_usuario'
        if 'id_usuario' not in columnas:
            cursor.execute("ALTER TABLE cita ADD COLUMN id_usuario INT NULL")
            print("DB MIGRADA: Columna 'id_usuario' añadida.")

        # Asegurar columna 'estado'
        if 'estado' not in columnas:
            cursor.execute("ALTER TABLE cita ADD COLUMN estado VARCHAR(50) DEFAULT 'Programada'")
            print("DB MIGRADA: Columna 'estado' añadida.")
            
        # Asegurar AUTO_INCREMENT en id_cita
        try:
            # Intentamos activar el auto-incremento (asumiendo que ya es PK)
            cursor.execute("ALTER TABLE cita MODIFY id_cita INT AUTO_INCREMENT")
            print("DB MIGRADA: AI activado en cita.")
        except Exception as e:
            print(f"DEBUG: Intento 2 para cita: {e}")
            try:
                # Si falló, intentamos asegurar que sea PK primero y luego AI
                cursor.execute("ALTER TABLE cita MODIFY id_cita INT NOT NULL")
                cursor.execute("ALTER TABLE cita MODIFY id_cita INT AUTO_INCREMENT")
            except:
                pass

        # Asegurar AUTO_INCREMENT en id_paciente
        try:
            cursor.execute("ALTER TABLE paciente MODIFY id_paciente INT AUTO_INCREMENT")
            print("DB MIGRADA: AI activado en paciente.")
        except Exception as e:
            print(f"DEBUG: Intento 2 para paciente: {e}")
            try:
                cursor.execute("ALTER TABLE paciente MODIFY id_paciente INT AUTO_INCREMENT")
            except:
                pass

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"DEBUG: No se pudo migrar BD automáticamente: {e}")

# Ejecutamos migración al importar app
migrar_db()

@app.route('/debug-db')
def debug_db():
    res = "<h2>Diagnóstico de Base de Datos</h2>"
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Ver 'cita'
        cursor.execute("DESCRIBE cita")
        cita_cols = cursor.fetchall()
        res += "<h3>Tabla 'cita':</h3><table border='1'><tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th><th>Default</th><th>Extra</th></tr>"
        for col in cita_cols:
            res += f"<tr><td>{col['Field']}</td><td>{col['Type']}</td><td>{col['Null']}</td><td>{col['Key']}</td><td>{col['Default']}</td><td>{col['Extra']}</td></tr>"
        res += "</table>"
        
        # 2. Intentar fix manual
        try:
            cursor.execute("ALTER TABLE cita MODIFY id_cita INT AUTO_INCREMENT")
            res += "<p style='color:green'>¡ÉXITO: id_cita modificado a AI!</p>"
            conn.commit()
        except Exception as e_alt:
            res += f"<p style='color:red'>ERROR EN ALTER: {e_alt}</p>"
            
        cursor.close()
        conn.close()
    except Exception as e:
        res += f"<p style='color:red'>ERROR DE CONEXION: {e}</p>"
    return res

app = Flask(__name__)
app.secret_key = 'clave_secreta_medturnos_leo_modular' 

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return cargar_usuario(user_id)

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        
        user_obj = validar_login(email, password)
        if user_obj:
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
    
    registrar_usuario(nombre, mail, password)
    flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS DEL SISTEMA MÉDICO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendar')
@login_required
def pagina_agendar():
    # Ahora las vistas de turnos están en su subcarpeta propia
    return render_template('pacientes/turno.html')

@app.route('/reporte_citas')
@login_required
def reporte_citas():
    try:
        # Llamamos al servicio para obtener la lógica de negocio
        citas_para_tabla = obtener_reporte_pacientes()
        return render_template('pacientes/reporte.html', citas=citas_para_tabla)
    except Exception as e:
        print(f"Error en el reporte: {e}")
        return f"Error al cargar reportes: {e}", 500

@app.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    nombre = request.form.get('nombre')
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')
    
    # Usamos la clase de validación del formulario
    es_valido, mensaje = PacienteForm.validar_datos(nombre, especialidad, fecha)
    if not es_valido:
        flash(mensaje, 'danger')
        return redirect(url_for('pagina_agendar'))

    try:
        # Lógica de guardado en la nube delegada al servicio (usamos 3 tablas relacionadas)
        agendar_nuevo_paciente(nombre, especialidad, fecha, id_usuario=current_user.id)
        
        # Sincronización de archivos (JSON/TXT)
        try:
            sincronizar_archivos_data()
        except:
            pass 

        flash('Cita agendada con éxito Muchas Gracias...', 'success')
        return redirect(url_for('reporte_citas'))
            
    except Exception as e:
        print(f"Error base de datos: {e}")
        return f"Error al conectar con la base de datos: {e}", 500

@app.route('/editar/<int:id>')
@login_required
def editar(id):
    cita = obtener_cita_id(id)
    if not cita:
        flash("La cita no existe", "danger")
        return redirect(url_for('reporte_citas'))
    return render_template('pacientes/editar_turno.html', cita=cita)

@app.route('/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar(id):
    especialidad = request.form.get('especialidad')
    fecha = request.form.get('fecha')
    
    try:
        actualizar_cita(id, especialidad, fecha)
        flash("Cita actualizada con éxito", "success")
        return redirect(url_for('reporte_citas'))
    except Exception as e:
        flash(f"Error al actualizar: {e}", "danger")
        return redirect(url_for('reporte_citas'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    try:
        eliminar_cita(id)
        flash("Cita eliminada correctamente", "success")
        return redirect(url_for('reporte_citas'))
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
        return redirect(url_for('reporte_citas'))

@app.route('/descargar_reporte_pdf')
@login_required
def descargar_reporte_pdf():
    try:
        citas = obtener_reporte_pacientes()
        pdf_content = generar_pdf_reporte(citas)
        
        # Enviamos el PDF como archivo descargable
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte_citas_medicas.pdf'
        )
    except Exception as e:
        flash(f"Error al generar PDF: {e}", "danger")
        return redirect(url_for('reporte_citas'))

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/quejas', methods=['GET', 'POST'])
def quejas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        mensaje = request.form.get('mensaje')
        
        if not nombre or not mail or not mensaje:
            flash("Todos los campos son obligatorios para enviar tu mensaje", "danger")
            return redirect(url_for('quejas'))
            
        # Guardamos en un archivo de feedback
        import json
        from datetime import datetime
        feedback_file = 'data/feedback.json'
        # Aseguramos que la carpeta data existe
        os.makedirs('data', exist_ok=True)
        
        comentario = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombre": nombre,
            "mail": mail,
            "mensaje": mensaje
        }
        
        datos = []
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                try:
                    datos = json.load(f)
                except:
                    datos = []
        
        datos.append(comentario)
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
            
        flash("¡Gracias por tu mensaje! Tu opinión es muy importante para nosotros", "success")
        return redirect(url_for('index'))
        
    return render_template('quejas.html')

@app.route('/usuarios')
@login_required 
def pagina_usuarios():
    # Acceso simple para ver usuarios registrados
    from conexion.conexion import obtener_conexion
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=datos)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    from services.usuario_service import actualizar_datos_usuario
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        nueva_pass = request.form.get('password')
        
        if actualizar_datos_usuario(current_user.id, nuevo_nombre, nueva_pass if nueva_pass else None):
            flash("Perfil actualizado correctamente. Los cambios se verán reflejados en tu próxima sesión.", "success")
            return redirect(url_for('index'))
            
    return render_template('perfil.html')


if __name__ == '__main__':
    app.run(debug=True)