from app import app, db, User

def init_db():
    with app.app_context():
        # Eliminar todas las tablas
        db.drop_all()
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario administrador
        admin = User(
            username='admin',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Base de datos inicializada y usuario administrador creado!")

if __name__ == '__main__':
    init_db() 