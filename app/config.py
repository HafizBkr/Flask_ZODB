import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    """Configuration de base pour l'application"""
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    DEBUG = False
    ZODB_STORAGE = os.environ.get('ZODB_STORAGE') 

class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False

# Dictionnaire pour sélectionner la configuration selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retourne la configuration appropriée selon l'environnement"""
    env = os.environ.get('FLASK_ENV') or 'default'
    return config[env]