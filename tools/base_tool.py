"""
CODI Core - Base Tool Module (FASE 3)
Define la clase base para todas las herramientas de CODI.
"""

from typing import Dict, Any, Callable, List
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Tool:
    """
    Clase base para todas las herramientas de CODI.
    Define la interfaz básica que deben implementar las herramientas.
    """
    
    name: str = "BaseTool"
    description: str = "Herramienta base abstracta."
    
    def __init__(self):
        pass

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Retorna la definición de la herramienta en un formato que el LLM pueda entender
        (similar a la especificación de funciones de OpenAI).
        """
        raise NotImplementedError("El método get_tool_definition debe ser implementado por las subclases.")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la funcionalidad de la herramienta.
        
        Args:
            **kwargs: Argumentos específicos para la función de la herramienta.
            
        Returns:
            Dict[str, Any]: Resultado de la ejecución.
        """
        raise NotImplementedError("El método execute debe ser implementado por las subclases.")

class ToolManager:
    """
    Gestor de herramientas para registrar y acceder a ellas.
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tool_definitions: List[Dict[str, Any]] = []
        
    def register_tool(self, tool: Tool):
        """Registra una herramienta en el gestor."""
        if tool.name in self.tools:
            logger.warning(f"Herramienta {tool.name} ya registrada. Sobrescribiendo.")
        self.tools[tool.name] = tool
        self.tool_definitions.append(tool.get_tool_definition())
        logger.info(f"Herramienta {tool.name} registrada.")

    def get_tool(self, name: str) -> Tool:
        """Obtiene una herramienta por su nombre."""
        if name not in self.tools:
            raise ValueError(f"Herramienta no encontrada: {name}")
        return self.tools[name]

    def get_all_definitions(self) -> List[Dict[str, Any]]:
        """Retorna todas las definiciones de herramientas para el LLM."""
        return self.tool_definitions

# Instancia global del ToolManager
tool_manager = ToolManager()
