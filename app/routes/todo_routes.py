from flask import Blueprint, request, jsonify
from app.database import get_db
from app.models.todo import Todo
import datetime

# Créer un Blueprint pour les routes de todos
todo_bp = Blueprint('todo', __name__)

@todo_bp.route('', methods=['GET'])
def get_todos():
    """Récupérer toutes les tâches, avec filtrage optionnel"""
    db = get_db()
    
    user_id = request.args.get('user_id')
    list_id = request.args.get('list_id')
    completed = request.args.get('completed')
    
    todos = db.root.todos.values()
    result = []
    
    # Appliquer les filtres
    for todo in todos:
        if user_id and todo.user_id != user_id:
            continue
        if list_id and todo.list_id != list_id:
            continue
        if completed is not None:
            is_completed = completed.lower() == 'true'
            if todo.is_completed != is_completed:
                continue
                
        result.append(todo.to_dict())
    
    return jsonify(result)

@todo_bp.route('/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Récupérer une tâche par son ID"""
    db = get_db()
    
    if todo_id not in db.root.todos:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    
    return jsonify(db.root.todos[todo_id].to_dict())

@todo_bp.route('', methods=['POST'])
def create_todo():
    """Créer une nouvelle tâche"""
    data = request.get_json()
    db = get_db()
    
    if not data or not all(k in data for k in ('title', 'list_id', 'user_id')):
        return jsonify({'error': 'Données insuffisantes'}), 400
    
    # Vérifier si l'utilisateur existe
    if data['user_id'] not in db.root.users:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier si la liste existe
    if data['list_id'] not in db.root.todo_lists:
        return jsonify({'error': 'Liste non trouvée'}), 404
    
    # Vérifier que la liste appartient à l'utilisateur
    todo_list = db.root.todo_lists[data['list_id']]
    if todo_list.user_id != data['user_id']:
        return jsonify({'error': 'Cette liste n\'appartient pas à cet utilisateur'}), 403
    
    # Traiter la date d'échéance si elle existe
    due_date = None
    if 'due_date' in data and data['due_date']:
        try:
            due_date = datetime.datetime.fromisoformat(data['due_date'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Format de date invalide, utilisez ISO 8601'}), 400
    
    description = data.get('description', '')
    priority = data.get('priority', 1)
    
    new_todo = Todo(
        data['title'], 
        description, 
        data['list_id'], 
        data['user_id'],
        due_date=due_date,
        priority=priority
    )
    
    # Stocker la tâche dans ZODB
    db.root.todos[new_todo.id] = new_todo
    
    # Ajouter la tâche à la liste
    todo_list.todos[new_todo.id] = new_todo
    todo_list._p_changed = True
    
    db.commit()
    
    return jsonify(new_todo.to_dict()), 201

@todo_bp.route('/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Mettre à jour une tâche"""
    db = get_db()
    
    if todo_id not in db.root.todos:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    
    todo = db.root.todos[todo_id]
    data = request.get_json()
    
    # Si on change la liste, vérifions que la nouvelle liste existe et appartient à l'utilisateur
    if 'list_id' in data and data['list_id'] != todo.list_id:
        # La nouvelle liste doit exister
        if data['list_id'] not in db.root.todo_lists:
            return jsonify({'error': 'Nouvelle liste non trouvée'}), 404
            
        # La nouvelle liste doit appartenir au même utilisateur
        new_list = db.root.todo_lists[data['list_id']]
        if new_list.user_id != todo.user_id:
            return jsonify({'error': 'Cette liste n\'appartient pas à cet utilisateur'}), 403
            
        # Supprimer la tâche de l'ancienne liste
        old_list = db.root.todo_lists[todo.list_id]
        if todo_id in old_list.todos:
            del old_list.todos[todo_id]
            old_list._p_changed = True
            
        # Ajouter la tâche à la nouvelle liste
        new_list.todos[todo_id] = todo
        new_list._p_changed = True
        
        # Mettre à jour l'ID de liste dans la tâche
        todo.list_id = data['list_id']
    
    todo.update(data)
    db.commit()
    
    return jsonify(todo.to_dict())

@todo_bp.route('/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Supprimer une tâche"""
    db = get_db()
    
    if todo_id not in db.root.todos:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    
    todo = db.root.todos[todo_id]
    
    # Supprimer la tâche de la base de données principale
    del db.root.todos[todo_id]
    
    # Supprimer la tâche de sa liste
    if todo.list_id in db.root.todo_lists:
        if todo_id in db.root.todo_lists[todo.list_id].todos:
            del db.root.todo_lists[todo.list_id].todos[todo_id]
            db.root.todo_lists[todo.list_id]._p_changed = True
    
    db.commit()
    
    return jsonify({'message': 'Tâche supprimée'})

@todo_bp.route('/<todo_id>/complete', methods=['PUT'])
def toggle_todo_complete(todo_id):
    """Marquer une tâche comme complétée ou non"""
    db = get_db()
    
    if todo_id not in db.root.todos:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    
    todo = db.root.todos[todo_id]
    
    # Inverser l'état de complétion
    todo.is_completed = not todo.is_completed
    
    # Mettre à jour la date de complétion
    if todo.is_completed:
        todo.completed_at = datetime.datetime.now()
    else:
        todo.completed_at = None
    
    todo.updated_at = datetime.datetime.now()
    todo._p_changed = True
    
    db.commit()
    
    return jsonify(todo.to_dict())