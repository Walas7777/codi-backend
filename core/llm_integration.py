"""
CODI Core - LLM Integration Module (FASE 2)
Responsable de la comunicación con el Large Language Model (LLM) para tareas de IA.
"""

import os
import logging
import json
from typing import Dict, Any, List
from openai import OpenAI, APIError, Timeout
# from dotenv import load_dotenv # No se puede instalar en el sandbox

# Las variables de entorno se leen directamente del entorno del sandbox

# Configuración de Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LLMIntegration:
    """
    Clase para manejar la integración con el LLM (OpenAI o compatible).
    Utiliza variables de entorno para la configuración.
    """

    def __init__(self):
        # Configuración desde variables de entorno
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini") # Usar un modelo más reciente y eficiente
        self.timeout = int(os.environ.get("LLM_TIMEOUT", 30))
        self.max_retries = int(os.environ.get("LLM_MAX_RETRIES", 3))
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no está configurada. La integración con LLM no funcionará.")
            self.client = None
        else:
            # Inicializar cliente de OpenAI
            self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
            logger.info(f"LLMIntegration inicializado con modelo: {self.model}")

    def _call_llm(self, system_prompt: str, user_prompt: str, json_output: bool = False) -> str:
        """
        Método privado para realizar la llamada a la API del LLM con reintentos.
        """
        if not self.client:
            raise ConnectionError("Cliente LLM no inicializado. OPENAI_API_KEY no configurada.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_format = {"type": "json_object"} if json_output else {"type": "text"}
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format=response_format,
                    temperature=0.1
                )
                
                content = response.choices[0].message.content
                logger.debug(f"LLM Response (Attempt {attempt + 1}): {content[:100]}...")
                return content

            except (APIError, Timeout) as e:
                logger.warning(f"LLM API Error (Attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt + 1 == self.max_retries:
                    raise RuntimeError(f"Fallo al comunicarse con el LLM después de {self.max_retries} intentos.") from e
                # Esperar antes de reintentar (simple backoff)
                import time
                time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error inesperado al llamar al LLM: {e}")
                raise

    def analyze_objective(self, objective: str) -> Dict[str, Any]:
        """
        Mejora el análisis de objetivos utilizando el LLM.
        """
        system_prompt = (
            "Eres un analista de objetivos experto. Tu tarea es tomar un objetivo "
            "y descomponerlo en un análisis estructurado en formato JSON. "
            "El análisis debe incluir: 'summary', 'keywords', 'required_components' (e.g., Planner, Executor), "
            "y 'risk_assessment'."
        )
        user_prompt = f"Analiza el siguiente objetivo: '{objective}'"
        
        try:
            json_response = self._call_llm(system_prompt, user_prompt, json_output=True)
            return json.loads(json_response)
        except Exception as e:
            logger.error(f"Fallo en analyze_objective: {e}")
            # Retornar un análisis de fallback
            return {
                "summary": f"Análisis fallido por IA. Objetivo original: {objective}",
                "keywords": ["fallback", "error"],
                "required_components": ["Planner", "Executor"],
                "risk_assessment": "High (AI failure)"
            }

    def generate_plan(self, objective: str, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera un plan inteligente de tareas utilizando el LLM.
        """
        system_prompt = (
            "Eres un planificador de proyectos experto. Basado en el análisis proporcionado, "
            "genera una lista de tareas estructuradas en formato JSON. "
            "Cada tarea debe ser un objeto con las claves: 'id' (int), 'title' (str), 'description' (str), "
            "'dependencies' (List[int]), y 'priority' (int). "
            "Asegúrate de que las dependencias sean válidas y el plan sea lógico y ejecutable."
        )
        user_prompt = (
            f"Objetivo: {objective}\n"
            f"Análisis de IA: {json.dumps(analysis_result, indent=2)}\n"
            "Genera la lista de tareas (List[Task])."
        )
        
        try:
            json_response = self._call_llm(system_prompt, user_prompt, json_output=True)
            # El LLM debe retornar una lista de tareas, no un objeto que contenga la lista
            data = json.loads(json_response)
            # A veces el LLM envuelve la lista en un objeto, intentar extraerla
            if isinstance(data, dict) and "tasks" in data:
                return data["tasks"]
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Fallo en generate_plan: {e}")
            # Retornar un plan de fallback (similar al de FASE 1)
            return [
                {"id": 1, "title": "Analizar objetivo (Fallback)", "description": "Análisis básico por fallo de IA", "dependencies": [], "priority": 1},
                {"id": 2, "title": "Ejecutar acciones principales (Fallback)", "description": "Acciones centrales basadas en el objetivo", "dependencies": [1], "priority": 3},
                {"id": 3, "title": "Validar resultados (Fallback)", "description": "Verificación de resultados", "dependencies": [2], "priority": 4},
            ]

    def validate_results(self, plan_id: str, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida los resultados de la ejecución utilizando el LLM.
        """
        system_prompt = (
            "Eres un validador de resultados experto. Tu tarea es revisar los resultados de la ejecución "
            "de un plan y determinar si el objetivo fue alcanzado. "
            "Retorna un objeto JSON con las claves: 'validation_status' ('SUCCESS', 'PARTIAL', 'FAILURE'), "
            "'confidence_score' (0.0 a 1.0), y 'feedback' (un resumen de la validación)."
        )
        user_prompt = (
            f"Plan ID: {plan_id}\n"
            f"Resultados de la ejecución: {json.dumps(execution_results, indent=2)}\n"
            "Realiza la validación."
        )
        
        try:
            json_response = self._call_llm(system_prompt, user_prompt, json_output=True)
            return json.loads(json_response)
        except Exception as e:
            logger.error(f"Fallo en validate_results: {e}")
            # Retornar una validación de fallback
            return {
                "validation_status": "FAILURE",
                "confidence_score": 0.0,
                "feedback": "Validación fallida por IA. Revisar resultados manualmente."
            }

# Ejemplo de uso (solo para pruebas internas)
if __name__ == "__main__":
    # Esto requiere que OPENAI_API_KEY esté configurada en el entorno
    # Para la prueba, asumiremos que está configurada en el sandbox
    
    # Simulación de variables de entorno para la prueba
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key" # La clave real se usa internamente
    os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
    
    llm_integration = LLMIntegration()
    
    test_objective = "Crear un reporte de ventas trimestral para la región norte."
    
    print(f"--- Analizando Objetivo: {test_objective} ---")
    analysis = llm_integration.analyze_objective(test_objective)
    print(json.dumps(analysis, indent=2))
    
    print("\n--- Generando Plan ---")
    plan_tasks = llm_integration.generate_plan(test_objective, analysis)
    print(json.dumps(plan_tasks, indent=2))
    
    # Simulación de resultados de ejecución
    mock_results = [
        {"task_id": 1, "title": "Recopilar datos", "status": "success", "result": "Datos de 3 meses obtenidos"},
        {"task_id": 2, "title": "Generar gráficos", "status": "success", "result": "5 gráficos generados"},
        {"task_id": 3, "title": "Redactar resumen", "status": "failed", "error": "Error de conexión a la base de datos"},
    ]
    
    print("\n--- Validando Resultados ---")
    validation = llm_integration.validate_results("plan_test_123", mock_results)
    print(json.dumps(validation, indent=2))
