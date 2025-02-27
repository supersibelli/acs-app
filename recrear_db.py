from app import app, db
import os

def main():
    # Eliminar la base de datos existente
    db_path = 'cadastro.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Base de datos anterior eliminada: {db_path}")
    
    # Crear nueva base de datos con las tablas actualizadas
    with app.app_context():
        db.create_all()
        print("Nova base de dados criada com sucesso!")

if __name__ == '__main__':
    main() 