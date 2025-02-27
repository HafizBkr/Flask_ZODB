from flask import Flask
from app.config import Config
from app.database import get_db

def create_app():
    # Créer l'application Flask
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser la base de données
    db = get_db()

    # Enregistrer les Blueprints
    from app.routes.user_routes import user_bp
    from app.routes.list_routes import list_bp
    from app.routes.todo_routes import todo_bp

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(list_bp, url_prefix='/api/lists')
    app.register_blueprint(todo_bp, url_prefix='/api/todos')

    return app