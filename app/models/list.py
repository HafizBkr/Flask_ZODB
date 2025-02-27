import persistent
import BTrees.OOBTree
import datetime
import uuid

class TodoList(persistent.Persistent):
    """Modèle de liste de tâches"""
    
    def __init__(self, title, description, user_id):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.user_id = user_id
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.todos = BTrees.OOBTree.BTree()  # Collection de todos dans cette liste
    
    def to_dict(self, include_todos=False):
        """Convertit la liste en dictionnaire pour la sérialisation JSON"""
        list_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'todo_count': len(self.todos)
        }
        
        if include_todos:
            list_dict['todos'] = [todo.to_dict() for todo in self.todos.values()]
            
        return list_dict
    
    def update(self, data):
        """Met à jour les attributs de la liste"""
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        
        self.updated_at = datetime.datetime.now()
        self._p_changed = True  # Marquer l'objet comme modifié pour ZODB