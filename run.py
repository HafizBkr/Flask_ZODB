from app import create_app
import atexit
import argparse
import os
import sys
import shutil
import signal

def force_unlock():
    """Supprime les fichiers de verrouillage pour débloquer la base ZODB."""
    lock_files = ['data/todoapp.fs.lock', 'data/todoapp.fs.lock.tmp']
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            os.remove(lock_file)
            print(f"Fichier de verrouillage supprimé: {lock_file}")

def reset_data():
    """Réinitialise les fichiers de données après sauvegarde."""
    if os.path.exists('data'):
        # Créer un dossier de backup s'il n'existe pas
        os.makedirs('backup', exist_ok=True)
        
        # Sauvegarde des fichiers avant suppression
        for file in os.listdir('data'):
            src = os.path.join('data', file)
            dst = os.path.join('backup', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
        
        print("Sauvegarde des données effectuée dans 'backup/'")

        # Suppression des fichiers de la base de données
        for file in os.listdir('data'):
            os.remove(os.path.join('data', file))
    
    print("Données réinitialisées")

def parse_args():
    """Analyse les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(description="Serveur d'application Todo")
    parser.add_argument('--force-unlock', action='store_true', help="Forcer le déverrouillage de la base de données")
    parser.add_argument('--reset-data', action='store_true', help="Réinitialiser les données avec sauvegarde")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    if args.force_unlock:
        force_unlock()
        sys.exit(0)

    if args.reset_data:
        reset_data()
        sys.exit(0)

    try:
        app = create_app()

        # Fermeture propre de la base de données
        def close_db():
            from app.database import get_db
            try:
                db = get_db()
                db.close()
            except Exception as e:
                print(f"Erreur lors de la fermeture de la base: {str(e)}")

        atexit.register(close_db)

        # Gestion de l'arrêt propre avec Ctrl+C
        def signal_handler(sig, frame):
            print("\nArrêt en cours...")
            close_db()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Lancer l'application Flask
        app.run(debug=True)

    except Exception as e:
        print(f"Erreur au démarrage de l'application: {str(e)}")
        sys.exit(1)
