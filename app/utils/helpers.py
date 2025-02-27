from datetime import datetime

def format_datetime(value):
    """Formater une date en chaîne de caractères ISO"""
    if value is None:
        return None
    return value.isoformat()

def parse_datetime(value):
    """Convertir une chaîne de caractères ISO en objet datetime"""
    if value is None:
        return None
    return datetime.fromisoformat(value)