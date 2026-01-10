import os
from typing import Any

def deepagent_allowed(user: Any) -> bool:
    """
    Verifica si el uso de DeepAgent está permitido globalmente y para el usuario específico.
    """
    # Kill-switch global mediante variable de entorno
    if not os.getenv("DEEPAGENT_ENABLED", "false").lower() == "true":
        return False
    
    # Verificación de permisos del usuario (asumiendo objeto user con atributo can_use_deepagent)
    # Si user es un diccionario o None, manejar adecuadamente
    if hasattr(user, 'can_use_deepagent'):
        return user.can_use_deepagent
    elif isinstance(user, dict):
        return user.get('can_use_deepagent', False)
        
    return False
