from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

# Configuración de la base de datos para producción
if os.getenv('RENDER'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fisioterapia.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Activar logs de SQL

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'juahe66@gmail.com'
app.config['MAIL_PASSWORD'] = 'adnq kgox zswe ecpe'
app.config['MAIL_DEFAULT_SENDER'] = 'juahe66@gmail.com'
app.config['MAIL_DEBUG'] = True  # Activar modo debug para correo

# Configuración de seguridad
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
mail = Mail(app)

# Modelos de la base de datos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    confirmada = db.Column(db.Boolean, default=False)
    cancelada = db.Column(db.Boolean, default=False)
    fecha_reprogramacion = db.Column(db.Date, nullable=True)
    hora_reprogramacion = db.Column(db.Time, nullable=True)
    motivo_cancelacion = db.Column(db.String(200), nullable=True)

# Lista de especialidades disponibles
ESPECIALIDADES = [
    'Rehabilitación Física',
    'Terapia Manual',
    'Masaje Terapéutico',
    'Fisioterapia Deportiva',
    'Rehabilitación Post-operatoria',
    'Fisioterapia Neurológica'
]

# Horarios disponibles
HORARIOS_DISPONIBLES = [
    '09:00', '10:00', '11:00', '12:00',
    '14:00', '15:00', '16:00', '17:00'
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def enviar_email_confirmacion(cita):
    try:
        print("Iniciando envío de correo...")
        print(f"Destinatario: {cita.email}")
        print(f"Remitente: {app.config['MAIL_USERNAME']}")
        
        msg = Message(
            'Confirmación de Cita - Centro de Fisioterapia',
            sender=('Centro de Fisioterapia', app.config['MAIL_USERNAME']),
            recipients=[cita.email]
        )
        
        # Cuerpo del mensaje con formato HTML
        msg.html = f"""
        <html>
        <body>
            <h2 style="color: #2c3e50;">¡Cita Confirmada!</h2>
            <p>Estimado(a) {cita.nombre},</p>
            <p>Su cita ha sido reservada exitosamente con los siguientes detalles:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Fecha:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{cita.fecha.strftime('%d/%m/%Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Hora:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{cita.hora.strftime('%H:%M')}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Especialidad:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{cita.especialidad}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Dirección:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{cita.direccion}</td>
                </tr>
            </table>
            <p>Por favor, confirme su asistencia respondiendo a este correo o contactándonos por WhatsApp.</p>
            <p>Si necesita realizar algún cambio o cancelar su cita, no dude en comunicarse con nosotros.</p>
            <hr>
            <p style="color: #7f8c8d;">Centro de Fisioterapia<br>
            Teléfono: +573148548624<br>
            WhatsApp: <a href="https://wa.me/573148548624">+573148548624</a><br>
            Email: juahe66@gmail.com</p>
        </body>
        </html>
        """
        
        # También incluimos una versión en texto plano
        msg.body = f"""
        ¡Cita Confirmada!

        Estimado(a) {cita.nombre},

        Su cita ha sido reservada exitosamente con los siguientes detalles:

        Fecha: {cita.fecha.strftime('%d/%m/%Y')}
        Hora: {cita.hora.strftime('%H:%M')}
        Especialidad: {cita.especialidad}
        Dirección: {cita.direccion}

        Por favor, confirme su asistencia respondiendo a este correo o contactándonos por WhatsApp.

        Si necesita realizar algún cambio o cancelar su cita, no dude en comunicarse con nosotros.

        Centro de Fisioterapia
        Teléfono: +573148548624
        WhatsApp: https://wa.me/573148548624
        Email: juahe66@gmail.com
        """
        
        print("Intentando enviar el correo...")
        mail.send(msg)
        print("Correo enviado exitosamente!")
        return True
    except Exception as e:
        print(f"Error detallado al enviar el correo: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        print(f"Traceback completo: {traceback.format_exc()}")
        return False

def verificar_disponibilidad(fecha, hora):
    cita_existente = Cita.query.filter_by(fecha=fecha, hora=hora).first()
    return cita_existente is None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html', especialidades=ESPECIALIDADES)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        mensaje = request.form['mensaje']
        
        # Aquí podrías agregar lógica para enviar el mensaje por email
        flash('Gracias por tu mensaje. Nos pondremos en contacto contigo pronto.', 'success')
        return redirect(url_for('contacto'))
    
    return render_template('contacto.html')

@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        especialidad = request.form['especialidad']
        
        if not verificar_disponibilidad(fecha, hora):
            flash('Lo sentimos, ese horario ya está ocupado. Por favor, seleccione otro horario.', 'danger')
            return redirect(url_for('reservar'))
        
        nueva_cita = Cita(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            fecha=fecha,
            hora=hora,
            especialidad=especialidad
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        
        if enviar_email_confirmacion(nueva_cita):
            flash('¡Cita reservada exitosamente! Se ha enviado un correo de confirmación.', 'success')
        else:
            flash('¡Cita reservada exitosamente! Hubo un problema al enviar el correo de confirmación. Por favor, contáctenos por WhatsApp.', 'warning')
        
        return redirect(url_for('index'))
    
    return render_template('reservar.html', 
                         especialidades=ESPECIALIDADES,
                         horarios=HORARIOS_DISPONIBLES,
                         hoy=datetime.now().strftime('%Y-%m-%d'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin_dashboard')
            return redirect(next_page)
        flash('Credenciales inválidas', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('No tienes permisos de administrador', 'danger')
        return redirect(url_for('index'))
    
    # Obtener parámetros de filtro
    fecha_filtro = request.args.get('fecha')
    estado_filtro = request.args.get('estado')
    especialidad_filtro = request.args.get('especialidad')
    
    # Consulta base
    query = Cita.query
    
    # Aplicar filtros
    if fecha_filtro:
        fecha = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
        query = query.filter(Cita.fecha == fecha)
    
    if estado_filtro:
        if estado_filtro == 'confirmada':
            query = query.filter(Cita.confirmada == True, Cita.cancelada == False)
        elif estado_filtro == 'pendiente':
            query = query.filter(Cita.confirmada == False, Cita.cancelada == False)
        elif estado_filtro == 'cancelada':
            query = query.filter(Cita.cancelada == True)
    
    if especialidad_filtro:
        query = query.filter(Cita.especialidad == especialidad_filtro)
    
    # Obtener citas filtradas
    citas = query.order_by(Cita.fecha, Cita.hora).all()
    
    # Obtener citas de hoy
    hoy = datetime.now().date()
    citas_hoy = Cita.query.filter(Cita.fecha == hoy).all()
    
    return render_template('admin/dashboard.html',
                         citas=citas,
                         citas_hoy=citas_hoy,
                         especialidades=ESPECIALIDADES,
                         fecha_filtro=fecha_filtro,
                         estado_filtro=estado_filtro,
                         especialidad_filtro=especialidad_filtro)

@app.route('/admin/cita/<int:id>/confirmar')
@login_required
def confirmar_cita(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    cita = Cita.query.get_or_404(id)
    cita.confirmada = True
    db.session.commit()
    
    flash('Cita confirmada exitosamente', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cita/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
def cancelar_cita(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    try:
        cita = Cita.query.get_or_404(id)
        
        if request.method == 'POST':
            motivo = request.form.get('motivo', '')
            
            try:
                # Actualizar la cita
                cita.cancelada = True
                cita.motivo_cancelacion = motivo
                cita.confirmada = False
                
                # Guardar cambios en la base de datos
                db.session.commit()
                
                # Preparar el correo
                msg = Message(
                    'Cancelación de Cita - Centro de Fisioterapia',
                    sender=('Centro de Fisioterapia', app.config['MAIL_USERNAME']),
                    recipients=[cita.email]
                )
                
                # Contenido HTML del correo
                html_content = f"""
                <html>
                <body>
                    <h2 style="color: #e74c3c;">Cancelación de Cita</h2>
                    <p>Estimado(a) {cita.nombre},</p>
                    <p>Lamentamos informarle que su cita programada para el {cita.fecha.strftime('%d/%m/%Y')} a las {cita.hora.strftime('%H:%M')} ha sido cancelada.</p>
                    <p>Motivo: {motivo}</p>
                    <p>Si desea reprogramar su cita, por favor contáctenos por WhatsApp o responda a este correo.</p>
                    <hr>
                    <p style="color: #7f8c8d;">Centro de Fisioterapia<br>
                    Teléfono: +573148548624<br>
                    WhatsApp: <a href="https://wa.me/573148548624">+573148548624</a><br>
                    Email: juahe66@gmail.com</p>
                </body>
                </html>
                """
                
                # Contenido en texto plano
                text_content = f"""
                Cancelación de Cita

                Estimado(a) {cita.nombre},

                Lamentamos informarle que su cita programada para el {cita.fecha.strftime('%d/%m/%Y')} a las {cita.hora.strftime('%H:%M')} ha sido cancelada.

                Motivo: {motivo}

                Si desea reprogramar su cita, por favor contáctenos por WhatsApp o responda a este correo.

                Centro de Fisioterapia
                Teléfono: +573148548624
                WhatsApp: https://wa.me/573148548624
                Email: juahe66@gmail.com
                """
                
                msg.html = html_content
                msg.body = text_content
                
                # Enviar el correo
                mail.send(msg)
                flash('Cita cancelada y notificación enviada al paciente', 'success')
                
            except Exception as e:
                print(f"Error al procesar la cancelación: {str(e)}")
                db.session.rollback()  # Revertir cambios en caso de error
                flash('Error al procesar la cancelación', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/cancelar_cita.html', cita=cita)
        
    except Exception as e:
        print(f"Error en cancelar_cita: {str(e)}")
        flash('Error al procesar la solicitud', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/cita/<int:id>/reprogramar', methods=['GET', 'POST'])
@login_required
def reprogramar_cita(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    cita = Cita.query.get_or_404(id)
    
    if request.method == 'POST':
        nueva_fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        nueva_hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        
        if not verificar_disponibilidad(nueva_fecha, nueva_hora):
            flash('Lo sentimos, ese horario ya está ocupado. Por favor, seleccione otro horario.', 'danger')
            return redirect(url_for('reprogramar_cita', id=id))
        
        # Guardar la fecha y hora originales
        fecha_original = cita.fecha
        hora_original = cita.hora
        
        # Actualizar la cita
        cita.fecha = nueva_fecha
        cita.hora = nueva_hora
        cita.fecha_reprogramacion = fecha_original
        cita.hora_reprogramacion = hora_original
        db.session.commit()
        
        # Enviar email de reprogramación
        try:
            msg = Message(
                'Reprogramación de Cita - Centro de Fisioterapia',
                sender=('Centro de Fisioterapia', app.config['MAIL_USERNAME']),
                recipients=[cita.email]
            )
            
            msg.html = f"""
            <html>
            <body>
                <h2 style="color: #3498db;">Reprogramación de Cita</h2>
                <p>Estimado(a) {cita.nombre},</p>
                <p>Su cita ha sido reprogramada con los siguientes detalles:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Fecha Original:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{fecha_original.strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Hora Original:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{hora_original.strftime('%H:%M')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Nueva Fecha:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{nueva_fecha.strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Nueva Hora:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{nueva_hora.strftime('%H:%M')}</td>
                    </tr>
                </table>
                <p>Por favor, confirme su asistencia respondiendo a este correo o contactándonos por WhatsApp.</p>
                <hr>
                <p style="color: #7f8c8d;">Centro de Fisioterapia<br>
                Teléfono: +573148548624<br>
                WhatsApp: <a href="https://wa.me/573148548624">+573148548624</a><br>
                Email: juahe66@gmail.com</p>
            </body>
            </html>
            """
            
            mail.send(msg)
            flash('Cita reprogramada y notificación enviada al paciente', 'success')
        except Exception as e:
            flash('Cita reprogramada, pero hubo un error al enviar la notificación', 'warning')
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/reprogramar_cita.html', 
                         cita=cita,
                         horarios=HORARIOS_DISPONIBLES,
                         hoy=datetime.now().strftime('%Y-%m-%d'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

# Crear la base de datos y el usuario administrador al iniciar la aplicación
with app.app_context():
    try:
        # Eliminar todas las tablas existentes
        db.drop_all()
        # Crear todas las tablas con las nuevas columnas
        db.create_all()
        
        # Verificar si existe un administrador
        admin = User.query.filter_by(username='admin@fisioterapia.com').first()
        if not admin:
            admin = User(username='admin@fisioterapia.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")

if __name__ == '__main__':
    # En producción, usar un servidor WSGI como Gunicorn
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    




