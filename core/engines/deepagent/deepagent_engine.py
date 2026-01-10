from typing import Dict, List, Any, Optional
from core.engines.deepagent.audit import audit_execution

class DeepAgentEngine:
    def __init__(self, engine):
        """
        Inicializa DeepAgentEngine con un motor subyacente (Mock o LangGraph).
        El motor debe tener un método run(goal, context).
        """
        self.engine = engine

    def run(self, goal: str, context: Dict, execution_id: str) -> Dict[str, Any]:
        """
        Ejecuta el agente con el objetivo y contexto dados, delegando al motor interno
        y asegurando la auditoría.
        """
        try:
            # Delegar ejecución al motor inyectado
            # El motor ya debe estar configurado con sus herramientas y LLM
            result = self.engine.run(goal, context)
        except Exception as e:
            # Captura de errores de último recurso para asegurar auditoría
            result = {
                "steps": [],
                "warnings": [],
                "errors": [str(e)],
                "result": None
            }

        # Auditoría obligatoria
        audit_execution(
            execution_id=execution_id,
            goal=goal,
            steps=result.get("steps", []),
            warnings=result.get("warnings", []),
            errors=result.get("errors", [])
        )
        
        return result
