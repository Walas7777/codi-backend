from typing import Dict, Any

def should_use_deepagent(task: Dict[str, Any]) -> bool:
    """
    Decide si una tarea debe ser procesada por DeepAgent.
    Criterios: requiere múltiples pasos o múltiples herramientas.
    """
    return bool(
        task.get("requires_multi_step") or
        task.get("requires_multiple_tools")
    )
