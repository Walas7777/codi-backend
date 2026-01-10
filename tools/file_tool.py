"""
CODI Core - FileTool Module (FASE 3)
Herramienta para crear y leer archivos.
"""

import os
import json
from typing import Dict, Any
from .base_tool import Tool

class FileTool(Tool):
    """
    Permite crear y leer archivos en el sistema de archivos.
    """
    
    name: str = "FileTool"
    description: str = "Herramienta para gestionar archivos (crear, leer)."
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Define la estructura de la herramienta para el LLM."""
        return {
            "type": "function",
            "function": {
                "name": "file_operation",
                "description": "Realiza operaciones de archivo como crear o leer contenido.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["create", "read"],
                            "description": "Tipo de operación a realizar: 'create' para crear/sobrescribir, 'read' para leer."
                        },
                        "path": {
                            "type": "string",
                            "description": "Ruta absoluta o relativa del archivo."
                        },
                        "content": {
                            "type": "string",
                            "description": "Contenido a escribir en el archivo (solo para operación 'create')."
                        }
                    },
                    "required": ["operation", "path"]
                }
            }
        }

    def write(self, path: str, content: str) -> Dict[str, Any]:
        return self.execute(action="write", path=path, content=content)

    def read(self, path: str) -> Dict[str, Any]:
        return self.execute(action="read", path=path)

    def extract_zip(self, zip_path: str, target_dir: str) -> Dict[str, Any]:
        # Nota: execute usa lógica interna para target_dir, pero aceptamos el param para compatibilidad
        return self.execute(action="unzip", path=zip_path)

    def execute(self, action: str = None, operation: str = None, path: str = None, content: str = None) -> Dict[str, Any]:
        """Ejecuta la operación de archivo."""
        # Normalizar parámetros (action vs operation)
        op = action or operation
        if not op:
             return {"status": "error", "message": "Se requiere 'action' o 'operation'"}
             
        try:
            if op == "create" or op == "write":
                os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content or "")
                return {"status": "success", "message": f"Archivo creado/sobrescrito en: {path}", "path": path}
            
            elif op == "read":
                if not os.path.exists(path):
                    return {"status": "error", "message": f"Archivo no encontrado: {path}"}
                with open(path, 'r') as f:
                    file_content = f.read()
                return {"status": "success", "message": f"Contenido del archivo {path} leído.", "content": file_content}
            
            elif op == "unzip":
                import zipfile
                if not os.path.exists(path):
                    return {"status": "error", "message": f"Archivo ZIP no encontrado: {path}"}
                
                target_dir = os.path.splitext(path)[0] + "_extracted"
                os.makedirs(target_dir, exist_ok=True)
                
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                    file_list = zip_ref.namelist()
                
                return {
                    "status": "success", 
                    "message": f"Archivo ZIP extraído en {target_dir}", 
                    "files": file_list,
                    "target_dir": target_dir
                }

            else:
                return {"status": "error", "message": f"Operación de archivo no soportada: {op}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Error al ejecutar FileTool: {e}"}
