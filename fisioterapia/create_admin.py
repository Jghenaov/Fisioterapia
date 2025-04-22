from app import app, db, User

with app.app_context():
    # Crear las tablas si no existen
    db.create_all()
    
    # Verificar si ya existe un administrador
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Crear el usuario administrador
        admin = User(
            username='admin',
            is_admin=True
        )
        admin.set_password('admin123')  # Usar el nuevo método set_password
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado exitosamente!")
    else:
        print("El usuario administrador ya existe.") 