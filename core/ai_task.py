from typing import List, Dict, Any
from .planner import Task

class AITask(Task):
    """
    Extensión de Task (FASE 1) para soportar herramientas y argumentos de IA (FASE 2).
    """
    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        dependencies: List[int] = None,
        priority: int = 3,
        status: str = "pending",
        tool: str = None,
        tool_args: Dict[str, Any] = None
    ):
        # Inicializar la clase base (Task)
        super().__init__(
            id=id,
            title=title,
            description=description,
            dependencies=dependencies,
            priority=priority,
            status=status
        )
        
        # Nuevos atributos específicos de IA
        self.tool = tool
        self.tool_args = tool_args or {}

    def to_dict(self) -> Dict[str, Any]:
        """Extiende to_dict para incluir tool y tool_args."""
        data = super().to_dict()
        data["tool"] = self.tool
        data["tool_args"] = self.tool_args
        return data
