import persistent
import datetime
import uuid

class Todo(persistent.Persistent):
    """Modèle de tâche individuelle"""
    
    def __init__(self, title, description, list_id, user_id, due_date=None, priority=1):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.list_id = list_id
        self.user_id = user_id
        self.due_date = due_date
        self.priority = priority  # 1 = Basse, 2 = Moyenne, 3 = Haute
        self.is_completed = False
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.completed_at = None
    
    def to_dict(self):
        """Convertit la tâche en dictionnaire pour la sérialisation JSON"""
        todo_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'list_id': self.list_id,
            'user_id': self.user_id,
            'is_completed': self.is_completed,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if self.due_date:
            todo_dict['due_date'] = self.due_date.isoformat()
        else:
            todo_dict['due_date'] = None
            
        if self.completed_at:
            todo_dict['completed_at'] = self.completed_at.isoformat()
        else:
            todo_dict['completed_at'] = None
            
        return todo_dict
    
    def update(self, data):
        """Met à jour les attributs de la tâche"""
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'priority' in data:
            self.priority = data['priority']
        if 'due_date' in data and data['due_date']:
            if isinstance(data['due_date'], str):
                self.due_date = datetime.datetime.fromisoformat(data['due_date'])
            else:
                self.due_date = data['due_date']
        if 'is_completed' in data:
            # Si le statut de complétion change
            if self.is_completed != data['is_completed']:
                self.is_completed = data['is_completed']
                # Si marqué comme complété, enregistrer la date
                if self.is_completed:
                    self.completed_at = datetime.datetime.now()
                else:
                    self.completed_at = None
        
        self.updated_at = datetime.datetime.now()
        self._p_changed = True  # Marquer l'objet comme modifié pour ZODB