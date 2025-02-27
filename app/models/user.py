import persistent
import BTrees.OOBTree
import datetime
import uuid

class User(persistent.Persistent):
    """Modèle d'utilisateur"""
    
    def __init__(self, username, email, password_hash):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash  # En production, utilisez un hash sécurisé
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.todo_lists = BTrees.OOBTree.BTree()  # Collection de listes de todos
    
    def to_dict(self, include_lists=False):
        """Convertit l'utilisateur en dictionnaire pour la sérialisation JSON"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'list_count': len(self.todo_lists)
        }
        
        if include_lists:
            user_dict['todo_lists'] = [todo_list.to_dict() for todo_list in self.todo_lists.values()]
            
        return user_dict
    
    def update(self, data):
        """Met à jour les attributs de l'utilisateur"""
        if 'username' in data:
            self.username = data['username']
        if 'email' in data:
            self.email = data['email']
        
        self.updated_at = datetime.datetime.now()
        self._p_changed = True  # Marquer l'objet comme modifié pour ZODB