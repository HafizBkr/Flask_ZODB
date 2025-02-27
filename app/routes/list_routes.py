from flask import Blueprint, request, jsonify
from app.database import get_db
from app.models.list import TodoList

# Créer un Blueprint pour les routes de listes
list_bp = Blueprint('list', __name__)

@list_bp.route('', methods=['GET'])
def get_lists():
    """Récupérer toutes les listes, avec filtrage optionnel par utilisateur"""
    db = get_db()
    
    user_id = request.args.get('user_id')
    
    if user_id:
        # Filtrer les listes par utilisateur
        lists = [todo_list.to_dict() for todo_list in db.root.todo_lists.values() 
                if todo_list.user_id == user_id]
    else:
        # Toutes les listes
        lists = [todo_list.to_dict() for todo_list in db.root.todo_lists.values()]
    
    return jsonify(lists)

@list_bp.route('/<list_id>', methods=['GET'])
def get_list(list_id):
    """Récupérer une liste par son ID"""
    db = get_db()
    
    if list_id not in db.root.todo_lists:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    include_todos = request.args.get('include_todos', 'false').lower() == 'true'
    
    return jsonify(db.root.todo_lists[list_id].to_dict(include_todos=include_todos))

@list_bp.route('', methods=['POST'])
def create_list():
    """Créer une nouvelle liste de tâches"""
    data = request.get_json()
    db = get_db()
    
    if not data or not all(k in data for k in ('title', 'user_id')):
        return jsonify({'error': 'Données insuffisantes'}), 400
    
    # Vérifier si l'utilisateur existe
    if data['user_id'] not in db.root.users:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    description = data.get('description', '')
    
    new_list = TodoList(data['title'], description, data['user_id'])
    
    # Stocker la liste dans ZODB
    db.root.todo_lists[new_list.id] = new_list
    
    # Ajouter la liste à la collection de l'utilisateur
    user = db.root.users[data['user_id']]
    user.todo_lists[new_list.id] = new_list
    user._p_changed = True
    
    db.commit()
    
    return jsonify(new_list.to_dict()), 201

@list_bp.route('/<list_id>', methods=['PUT'])
def update_list(list_id):
    """Mettre à jour une liste de tâches"""
    db = get_db()
    
    if list_id not in db.root.todo_lists:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    todo_list = db.root.todo_lists[list_id]
    data = request.get_json()
    
    todo_list.update(data)
    db.commit()
    
    return jsonify(todo_list.to_dict())

@list_bp.route('/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    """Supprimer une liste de tâches"""
    db = get_db()
    
    if list_id not in db.root.todo_lists:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    todo_list = db.root.todo_lists[list_id]
    user_id = todo_list.user_id
    
    # Supprimer la liste de la base de données principale
    del db.root.todo_lists[list_id]
    
    # Supprimer la liste de la collection de l'utilisateur
    if user_id in db.root.users:
        if list_id in db.root.users[user_id].todo_lists:
            del db.root.users[user_id].todo_lists[list_id]
            db.root.users[user_id]._p_changed = True
    
    # Supprimer tous les todos appartenant à cette liste
    todos_to_delete = []
    for todo_id, todo in db.root.todos.items():
        if todo.list_id == list_id:
            todos_to_delete.append(todo_id)
    
    for todo_id in todos_to_delete:
        del db.root.todos[todo_id]
    
    db.commit()
    
    return jsonify({'message': 'Liste et ses tâches supprimées'})