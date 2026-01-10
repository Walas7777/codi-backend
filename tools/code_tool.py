"""
CODI Core - CodeTool Module (FASE 3)
Herramienta para generar y modificar archivos de código.
"""

import os
from typing import Dict, Any
from .base_tool import Tool

class CodeTool(Tool):
    """
    Permite generar nuevos archivos de código y modificar archivos existentes.
    """
    
    name: str = "CodeTool"
    description: str = "Herramienta para generar y modificar archivos de código."
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Define la estructura de la herramienta para el LLM."""
        return {
            "type": "function",
            "function": {
                "name": "code_operation",
                "description": "Genera un nuevo archivo de código o modifica el contenido de un archivo existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["generate", "modify"],
                            "description": "Tipo de operación: 'generate' para crear un archivo, 'modify' para sobrescribir/reemplazar contenido."
                        },
                        "path": {
                            "type": "string",
                            "description": "Ruta del archivo de código."
                        },
                        "content": {
                            "type": "string",
                            "description": "Contenido completo del código a escribir (para 'generate' o 'modify')."
                        }
                    },
                    "required": ["operation", "path", "content"]
                }
            }
        }

    def execute(self, operation: str, path: str, content: str) -> Dict[str, Any]:
        """Ejecuta la operación de código."""
        try:
            if operation in ["generate", "modify"]:
                os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
                return {"status": "success", "message": f"Archivo de código {operation}do en: {path}", "path": path}
            
            else:
                return {"status": "error", "message": f"Operación de código no soportada: {operation}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Error al ejecutar CodeTool: {e}"}
