from flask import Blueprint, request, jsonify
from app.database import get_db
from app.models.user import User

# Créer un Blueprint pour les routes utilisateur
user_bp = Blueprint('user', __name__)

@user_bp.route('', methods=['GET'])
def get_users():
    """Récupérer tous les utilisateurs"""
    db = get_db()
    users_list = [user.to_dict() for user in db.root.users.values()]
    return jsonify(users_list)

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Récupérer un utilisateur par son ID"""
    db = get_db()
    user = db.root.users.get(user_id)

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Détermine si on doit inclure les listes de todo
    include_lists = request.args.get('include_lists', 'false').lower() == 'true'

    return jsonify(user.to_dict(include_lists=include_lists))

@user_bp.route('', methods=['POST'])
def create_user():
    """Créer un nouvel utilisateur"""
    data = request.get_json()
    db = get_db()

    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Données insuffisantes'}), 400

    # Vérifier si l'utilisateur existe déjà
    for user in db.root.users.values():
        if user.username == data['username']:
            return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 409
        if user.email == data['email']:
            return jsonify({'error': 'Email déjà utilisé'}), 409

    # Ici, vous devriez hacher le mot de passe avant de le stocker
    # password_hash = generate_password_hash(data['password'])
    password_hash = data['password']  # Ne pas faire ça en production!

    new_user = User(data['username'], data['email'], password_hash)

    try:
        db.root.users[new_user.id] = new_user
        db.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Erreur lors de la création : {str(e)}'}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Mettre à jour un utilisateur"""
    db = get_db()
    user = db.root.users.get(user_id)

    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    data = request.get_json()
    
    # Vérifier si le nom d'utilisateur ou l'email est déjà utilisé
    if 'username' in data or 'email' in data:
        for u in db.root.users.values():
            if u.id != user_id:
                if 'username' in data and u.username == data['username']:
                    return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 409
                if 'email' in data and u.email == data['email']:
                    return jsonify({'error': 'Email déjà utilisé'}), 409

    try:
        user.update(data)
        db.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour : {str(e)}'}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Supprimer un utilisateur"""
    db = get_db()
    
    if user_id not in db.root.users:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    try:
        # Supprimer l'utilisateur
        del db.root.users[user_id]

        # Supprimer également ses listes et todos
        lists_to_delete = [list_id for list_id, todo_list in db.root.todo_lists.items() if todo_list.user_id == user_id]
        for list_id in lists_to_delete:
            del db.root.todo_lists[list_id]

        todos_to_delete = [todo_id for todo_id, todo in db.root.todos.items() if todo.user_id == user_id]
        for todo_id in todos_to_delete:
            del db.root.todos[todo_id]

        db.commit()
        return jsonify({'message': 'Utilisateur et ses données supprimés'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Erreur lors de la suppression : {str(e)}'}), 500
