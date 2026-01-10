"""
CODI Core - SystemTool Module (FASE 3)
Herramienta para interactuar con el sistema (listar directorios, ejecutar comandos simulados).
"""

import os
import subprocess
from typing import Dict, Any
from .base_tool import Tool

class SystemTool(Tool):
    """
    Permite listar directorios y ejecutar comandos simples (simulados por seguridad).
    """
    
    name: str = "SystemTool"
    description: str = "Herramienta para interactuar con el sistema (listar directorios, ejecutar comandos simulados)."
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Define la estructura de la herramienta para el LLM."""
        return {
            "type": "function",
            "function": {
                "name": "system_operation",
                "description": "Realiza operaciones de sistema como listar directorios o ejecutar comandos simulados.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["list_dir", "run_command"],
                            "description": "Tipo de operación a realizar: 'list_dir' para listar contenido de un directorio, 'run_command' para ejecutar un comando simulado."
                        },
                        "path": {
                            "type": "string",
                            "description": "Ruta del directorio a listar (solo para 'list_dir')."
                        },
                        "command": {
                            "type": "string",
                            "description": "Comando a ejecutar (solo para 'run_command')."
                        }
                    },
                    "required": ["operation"]
                }
            }
        }

    def execute(self, operation: str, path: str = None, command: str = None) -> Dict[str, Any]:
        """Ejecuta la operación de sistema."""
        try:
            if operation == "list_dir":
                target_path = path if path else os.getcwd()
                if not os.path.isdir(target_path):
                    return {"status": "error", "message": f"Directorio no encontrado: {target_path}"}
                
                items = os.listdir(target_path)
                return {"status": "success", "message": f"Contenido de {target_path}", "items": items}
            
            elif operation == "run_command":
                # Simulación de comandos por seguridad
                if command.startswith("ls"):
                    return {"status": "success", "message": f"Comando simulado: {command}", "output": "Simulación de listado de archivos."}
                elif command.startswith("echo"):
                    return {"status": "success", "message": f"Comando simulado: {command}", "output": command[5:]}
                else:
                    return {"status": "error", "message": f"Comando no soportado/simulado: {command}"}
            
            else:
                return {"status": "error", "message": f"Operación de sistema no soportada: {operation}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Error al ejecutar SystemTool: {e}"}
