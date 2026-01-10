"""
CODI Core - Memory Store Module (FASE 3)
Implementa una memoria persistente simple (JSON) para almacenar objetivos, planes y resultados.
"""

import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MemoryStore:
    """
    Almacén de memoria persistente basado en un archivo JSON.
    Guarda objetivos, planes y resultados para consulta futura.
    """
    
    # Ruta del archivo de memoria
    MEMORY_FILE = os.path.join(os.path.dirname(__file__), "codi_memory.json")
    
    def __init__(self):
        self.memory: Dict[str, List[Dict[str, Any]]] = {
            "objectives": [],
            "plans": [],
            "results": []
        }
        self._load_memory()
        logger.info(f"MemoryStore inicializado. {len(self.memory['objectives'])} objetivos cargados.")

    def _load_memory(self):
        """Carga la memoria desde el archivo JSON si existe."""
        if os.path.exists(self.MEMORY_FILE):
            try:
                with open(self.MEMORY_FILE, 'r') as f:
                    self.memory = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error al decodificar el archivo de memoria: {e}. Se inicializará una memoria vacía.")
            except Exception as e:
                logger.error(f"Error al cargar el archivo de memoria: {e}")
        else:
            logger.info("Archivo de memoria no encontrado. Se creará uno nuevo al guardar.")

    def _save_memory(self):
        """Guarda la memoria en el archivo JSON."""
        try:
            with open(self.MEMORY_FILE, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar el archivo de memoria: {e}")

    def add_objective(self, objective: str, timestamp: str):
        """Agrega un objetivo ejecutado a la memoria."""
        self.memory["objectives"].append({
            "objective": objective,
            "timestamp": timestamp
        })
        self._save_memory()

    def add_plan(self, plan_id: str, plan_data: Dict[str, Any]):
        """Agrega un plan generado a la memoria."""
        self.memory["plans"].append({
            "plan_id": plan_id,
            "data": plan_data
        })
        self._save_memory()

    def add_result(self, plan_id: str, result_data: Dict[str, Any]):
        """Agrega un resultado final a la memoria."""
        self.memory["results"].append({
            "plan_id": plan_id,
            "data": result_data
        })
        self._save_memory()

    def get_recent_objectives(self, count: int = 5) -> List[Dict[str, Any]]:
        """Obtiene los N objetivos más recientes."""
        return self.memory["objectives"][-count:][::-1] # Últimos N, en orden descendente

    def get_plan_by_id(self, plan_id: str) -> Dict[str, Any] | None:
        """Obtiene un plan por su ID."""
        for item in self.memory["plans"]:
            if item["plan_id"] == plan_id:
                return item["data"]
        return None

    def get_memory_summary(self) -> Dict[str, int]:
        """Retorna un resumen del contenido de la memoria."""
        return {
            "total_objectives": len(self.memory["objectives"]),
            "total_plans": len(self.memory["plans"]),
            "total_results": len(self.memory["results"])
        }

# Ejemplo de uso (solo para pruebas internas)
if __name__ == "__main__":
    store = MemoryStore()
    
    # Simulación de uso
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    store.add_objective("Implementar FASE 3 de CODI", timestamp)
    
    mock_plan = {
        "objective": "Implementar FASE 3 de CODI",
        "tasks": [{"id": 1, "title": "Crear memoria"}],
        "status": "created"
    }
    store.add_plan("plan_fase3_001", mock_plan)
    
    mock_result = {
        "status": "success",
        "summary": "Fase 3 completada"
    }
    store.add_result("plan_fase3_001", mock_result)
    
    print(store.get_memory_summary())
    print(store.get_recent_objectives(1))
    print(store.get_plan_by_id("plan_fase3_001"))
