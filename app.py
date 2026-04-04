from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import io

# Importamos arquitectura modular
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
from conexion.conexion import obtener_conexion

# Inicialización
os.makedirs('data', exist_ok=True)
app = Flask(__name__)
app.secret_key = 'clave_secreta_medturnos_leo_modular' 

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return cargar_usuario(user_id)
    except:
        return None

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')



# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        
        user_obj = validar_login(email, password)
        
        # Sistema Auto-Reparable (Admin)
        if not user_obj and email == 'admin@gmail.com' and password == '123456Byron.':
            try:
                registrar_usuario('Administrador Maestro', email, password)
                conn = obtener_conexion()
                cursor = conn.cursor()
                try: cursor.execute("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) DEFAULT 'usuario'")
                except: pass
                cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE mail = %s", (email,))
                conn.commit()
                cursor.close()
                conn.close()
                user_obj = validar_login(email, password)
            except:
                pass

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

# --- RUTAS DE GESTIÓN MÉDICA ---

@app.route('/agendar')
@login_required
def pagina_agendar():
    return render_template('pacientes/turno.html')

@app.route('/reporte_citas')
@login_required
def reporte_citas():
    try:
        es_admin = (getattr(current_user, 'rol', 'usuario') == 'admin')
        citas = obtener_reporte_pacientes(id_usuario=current_user.id, es_admin=es_admin)
        return render_template('pacientes/reporte.html', citas=citas, es_admin=es_admin)
    except Exception as e:
        return f"Error al cargar reportes: {e}", 500

@app.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    try:
        agendar_nuevo_paciente(
            request.form.get('nombre'),
            request.form.get('especialidad'),
            request.form.get('fecha'),
            id_usuario=current_user.id
        )
        flash('Cita agendada exitosamente', 'success')
        return redirect(url_for('reporte_citas'))
    except Exception as e:
        flash(f'Error al agendar: {e}', 'danger')
        return redirect(url_for('pagina_agendar'))

@app.route('/editar/<int:id>')
@login_required
def editar(id):
    cita = obtener_cita_id(id)
    if not cita:
        return "Cita no encontrada", 404
    # Seguridad: solo el dueño o admin edita
    if getattr(current_user, 'rol', 'usuario') != 'admin' and cita['id_usuario'] != current_user.id:
        return "No tienes permiso para editar esta cita", 403
    return render_template('pacientes/editar.html', cita=cita)

@app.route('/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar(id):
    actualizar_cita(id, request.form.get('nombre'), request.form.get('especialidad'), request.form.get('fecha'))
    flash('Cita actualizada correctamente', 'success')
    return redirect(url_for('reporte_citas'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    eliminar_cita(id)
    flash('Cita eliminada correctamente', 'success')
    return redirect(url_for('reporte_citas'))

@app.route('/reporte_pdf')
@login_required
def descargar_reporte_pdf():
    try:
        es_admin = (getattr(current_user, 'rol', 'usuario') == 'admin')
        citas = obtener_reporte_pacientes(id_usuario=current_user.id, es_admin=es_admin)
        pdf_content = generar_pdf_reporte(citas)
        return send_file(io.BytesIO(pdf_content), mimetype='application/pdf', as_attachment=True, download_name='reporte_citas.pdf')
    except Exception as e:
        return f"Error al generar PDF: {e}", 500

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