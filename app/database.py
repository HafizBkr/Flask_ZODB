import ZODB
import ZODB.FileStorage
import ZODB.DemoStorage
import persistent
import transaction
import os

# Vérification de l'import BTrees
try:
    import BTrees.OOBTree
    print("BTrees.OOBTree importé avec succès")
except ImportError as e:
    print(f"Erreur lors de l'import de BTrees.OOBTree : {str(e)}")
    raise

class Database:
    def __init__(self, path='data/todoapp.fs', use_memory=False):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        self.path = path
        self.use_memory = use_memory

        if use_memory:
            self.storage = ZODB.DemoStorage.DemoStorage()
            print("Utilisation du stockage en mémoire (données non persistantes)")
        else:
            self._clean_lock_files()
            self.storage = ZODB.FileStorage.FileStorage(path)
            print(f"Utilisation du stockage persistant : {path}")

        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        self._initialize_collections()

    def _clean_lock_files(self):
        """Supprime les fichiers de verrouillage pour éviter les conflits."""
        for suffix in [".lock", ".lock.tmp"]:
            lock_file = f"{self.path}{suffix}"
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"Fichier verrouillage supprimé: {lock_file}")
                except Exception as e:
                    print(f"Erreur suppression {lock_file}: {str(e)}")

    def _initialize_collections(self):
        """Initialise les collections s'il n'existe pas déjà dans la base."""
        if not hasattr(self.root, 'users'):
            self.root.users = BTrees.OOBTree.BTree()
        if not hasattr(self.root, 'todo_lists'):
            self.root.todo_lists = BTrees.OOBTree.BTree()
        if not hasattr(self.root, 'todos'):
            self.root.todos = BTrees.OOBTree.BTree()
        
        print("Collections initialisées avec succès")
        self.commit()

    def commit(self):
        """Enregistre les changements dans la base."""
        transaction.commit()

    def close(self):
        """Ferme proprement la base de données."""
        try:
            transaction.abort()
            self.connection.close()
            self.db.close()
            self.storage.close()
            print("Connexion à la base de données fermée")
        except Exception as e:
            print(f"Erreur lors de la fermeture de la base: {str(e)}")

# Singleton pour obtenir la DB
def get_db():
    if not hasattr(get_db, 'instance'):
        get_db.instance = Database(use_memory=False)
    return get_db.instance