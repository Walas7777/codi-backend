"""
CODI Core - Orchestrator Module
Responsable de orquestar el flujo completo: análisis → planificación → ejecución → reporte.
Integra DeepAgent para tareas complejas.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import json
import uuid
import os

from .planner import Planner, Plan
from .executor import Executor, ExecutionResult
from tools.tool_manager import ToolManager
from tools.file_tool import FileTool
from tools.question_tool import QuestionTool
from .engines.deepagent.decision_gate import should_use_deepagent
from .engines.deepagent.deepagent_engine import DeepAgentEngine
from .engines.deepagent.security import deepagent_allowed
from .engines.deepagent.tool_proxy import ToolProxyFactory
from .engines.deepagent.langgraph_engine import LangGraphEngine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OrchestrationReport:
    """Reporte final de orquestación."""
    objective: str
    status: str  # "success", "partial", "failed"
    plan_id: str
    plan: Dict[str, Any]
    execution_results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    created_at: str
    completed_at: str
    duration_seconds: float
    engine: str = "standard"  # "standard" o "deepagent"

    def to_dict(self):
        return {
            "objective": self.objective,
            "status": self.status,
            "plan_id": self.plan_id,
            "plan": self.plan,
            "execution_results": self.execution_results,
            "summary": self.summary,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "engine": self.engine
        }


class Orchestrator:
    """
    Orquesta el flujo completo de CODI:
    1. Recibe objetivo
    2. Decide motor (Standard vs DeepAgent)
    3. Ejecuta
    4. Genera reporte final
    """

    def __init__(self):
        self.planner = Planner()
        
        # Inicializar ToolManager y registrar herramientas básicas
        self.tool_manager = ToolManager()
        self.tool_manager.register("FileTool", FileTool())
        
        # Registrar QuestionTool para responder preguntas
        try:
            self.tool_manager.register("QuestionTool", QuestionTool())
            logger.info("✅ QuestionTool registrada correctamente")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo registrar QuestionTool: {e}")
        
        self.executor = Executor(self.tool_manager)
        self.reports: Dict[str, OrchestrationReport] = {}
        self.current_plan_id: str = None
        
        # Inicializar DeepAgent con Feature Flag
        # FORZAR ACTIVACIÓN si existe OPENAI_API_KEY (Fix crítico para Railway)
        openai_key_exists = bool(os.getenv("OPENAI_API_KEY"))
        use_langgraph = openai_key_exists or (os.getenv("USE_LANGGRAPH", "false").lower() == "true")
        
        if use_langgraph:
            logger.info(">>> Inicializando DeepAgent con LangGraphEngine")
            # Usar ChatOpenAI real con la API Key de Railway
            try:
                from langchain_openai import ChatOpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY no configurada en variables de entorno")
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=api_key)
                logger.info("✅ ChatOpenAI inicializado correctamente con gpt-4o-mini")
            except Exception as e:
                logger.error(f"❌ Error al inicializar ChatOpenAI: {e}")
                logger.warning("🔄 Fallback a MockLLM")
                from core.mock_llm import MockLLM 
                llm = MockLLM()
            
            # Crear proxies de herramientas para LangGraph
            # LangGraphEngine espera un objeto que tenga método execute(intent)
            # Usamos el executor del core como base
            tool_proxy = ToolProxyFactory.create_proxies(self.executor, ["FileTool"])
            # Para simplificar MVP, pasamos el executor directamente envuelto en un adaptador simple
            # o usamos el primer proxy si es una lista.
            # Ajuste: LangGraphEngine espera 'tools' con método execute.
            # Creamos un adaptador simple.
            
            class ToolAdapter:
                def __init__(self, executor):
                    self.executor = executor
                
                def execute(self, intent_data):
                    # intent_data es dict con 'intent' y 'params'
                    if isinstance(intent_data, str):
                        try:
                            intent_data = json.loads(intent_data)
                        except json.JSONDecodeError:
                            # Si no es JSON válido, asumimos que es el nombre del intent o un error
                            logger.warning(f"ToolAdapter recibió string no JSON: {intent_data}")
                            return f"Error: Input must be a JSON object, got string: {intent_data}"

                    intent_name = intent_data.get("intent")
                    params = intent_data.get("params", {})
                    # Construir acción y ejecutar vía executor (que usa tool_manager)
                    # El executor espera una lista de intents en su método execute, 
                    # pero aquí queremos ejecutar uno solo y devolver resultado directo.
                    # Accedemos al tool_manager directamente para ejecución síncrona simple
                    # O mejor, usamos el executor para mantener validaciones.
                    
                    # Simulamos estructura de intent para executor
                    intent_full = {"name": intent_name, **params}
                    results = self.executor.execute([intent_full])
                    if results and results[0]["status"] == "success":
                        return results[0]["result"]
                    else:
                        raise Exception(results[0].get("error", "Unknown error"))

            engine = LangGraphEngine(llm, ToolAdapter(self.executor))
            
        else:
            logger.info(">>> Inicializando DeepAgent con MockAgentEngine")
            engine = self._create_mock_engine()
            
        self.deepagent_engine = DeepAgentEngine(engine)

    def _create_mock_engine(self):
        """Crea el motor mock para simulación."""
        class MockAgentEngine:
            def run(self, goal, context):
                return {
                    "steps": ["Step 1: Analyzed goal", "Step 2: Executed action"],
                    "warnings": [],
                    "errors": [],
                    "result": "Success via DeepAgent (Mock)"
                }
        return MockAgentEngine()

    def process_objective(self, objective: str, user_context: Dict[str, Any] = None) -> OrchestrationReport:
        """
        Procesa un objetivo completo desde análisis hasta reporte.
        
        Args:
            objective: Objetivo a procesar
            user_context: Contexto del usuario (permisos, preferencias)
            
        Returns:
            OrchestrationReport: Reporte final estructurado
        """
        start_time = datetime.now()
        logger.info(f"=== INICIANDO ORQUESTACIÓN ===")
        logger.info(f"Objetivo: {objective}")
        
        # Contexto de tarea para Decision Gate
        # Heurística mejorada para MVP
        requires_multi_step = " y " in objective or "," in objective or "analiza" in objective.lower() or "zip" in objective.lower()
        
        task_context = {
            "goal": objective,
            "requires_multi_step": requires_multi_step,
            "requires_multiple_tools": False 
        }
        
        # Decisión de Motor
        is_allowed = deepagent_allowed(user_context)
        
        # FIX CRÍTICO: Forzar DeepAgent si existe API Key, ignorando heurística
        openai_key_exists = bool(os.getenv("OPENAI_API_KEY"))
        use_deepagent = openai_key_exists and is_allowed
        
        # Si no hay API Key, usamos la lógica antigua (que probablemente dará False)
        if not openai_key_exists:
            should_use = should_use_deepagent(task_context)
            use_deepagent = should_use and is_allowed
        
        logger.info(f"Decision Gate: Force DeepAgent={openai_key_exists}, Allowed={is_allowed} -> Use DeepAgent={use_deepagent}")
        engine_used = "deepagent" if use_deepagent else "standard"
        
        execution_results = []
        plan_data = {}
        status = "failed"
        summary = {}

        try:
            if use_deepagent:
                logger.info(">>> Motor seleccionado: DeepAgent")
                execution_id = str(uuid.uuid4())
                self.current_plan_id = execution_id
                
                # Ejecutar DeepAgent
                result = self.deepagent_engine.run(
                    goal=objective,
                    context=user_context or {},
                    execution_id=execution_id
                )
                
                # Adaptar resultados de DeepAgent a formato de reporte
                status = "success" if not result.get("errors") else "failed"
                execution_results = [{"status": status, "output": result}]
                plan_data = {"engine": "DeepAgent", "steps": result.get("steps")}
                summary = {"engine": "DeepAgent", "details": result}
                
            else:
                logger.info(">>> Motor seleccionado: Standard (Planner + Executor)")
                
                # Paso 1: Análisis y Planificación
                logger.info("Paso 1: Analizando objetivo y generando plan...")
                plan = self.planner.analyze_objective(objective)
                self.current_plan_id = self._get_last_plan_id()
                logger.info(f"Plan generado con {plan.total_tasks} tareas")
                plan_data = plan.to_dict()

                # Paso 2: Ejecución
                logger.info("Paso 2: Ejecutando plan...")
                execution_results_objs = self.executor.execute_plan(plan)
                execution_results = [r.to_dict() for r in execution_results_objs]
                logger.info(f"Ejecución completada: {len(execution_results)} tareas ejecutadas")

                # Paso 3: Análisis de resultados
                logger.info("Paso 3: Analizando resultados...")
                status = self._determine_status(execution_results_objs)
                summary = self._generate_summary(plan, execution_results_objs)

            # Paso 4: Generar reporte
            completed_time = datetime.now()
            duration = (completed_time - start_time).total_seconds()

            report = OrchestrationReport(
                objective=objective,
                status=status,
                plan_id=self.current_plan_id or "unknown",
                plan=plan_data,
                execution_results=execution_results,
                summary=summary,
                created_at=start_time.isoformat(),
                completed_at=completed_time.isoformat(),
                duration_seconds=duration,
                engine=engine_used
            )

            # Almacenar reporte
            if self.current_plan_id:
                self.reports[self.current_plan_id] = report

            logger.info(f"=== ORQUESTACIÓN COMPLETADA ===")
            logger.info(f"Estado final: {status}")
            logger.info(f"Duración total: {duration:.2f}s")

            return report

        except Exception as e:
            logger.error(f"Error durante orquestación: {str(e)}")
            raise

    def _get_last_plan_id(self) -> str:
        """Obtiene el ID del último plan creado."""
        plans = self.planner.list_plans()
        return plans[-1] if plans else None

    def _determine_status(self, execution_results: List[ExecutionResult]) -> str:
        """
        Determina el estado general de la ejecución.
        
        Args:
            execution_results: Resultados de las tareas ejecutadas
            
        Returns:
            str: "success", "partial" o "failed"
        """
        if not execution_results:
            return "failed"

        success_count = sum(1 for r in execution_results if r.status == "success")
        total_count = len(execution_results)

        if success_count == total_count:
            return "success"
        elif success_count > 0:
            return "partial"
        else:
            return "failed"

    def _generate_summary(self, plan: Plan, execution_results: List[ExecutionResult]) -> Dict[str, Any]:
        """
        Genera un resumen de la ejecución.
        
        Args:
            plan: Plan ejecutado
            execution_results: Resultados de las tareas
            
        Returns:
            Dict: Resumen estructurado
        """
        success_count = sum(1 for r in execution_results if r.status == "success")
        failed_count = sum(1 for r in execution_results if r.status == "failed")
        total_duration = sum(r.duration_seconds for r in execution_results)

        return {
            "total_tasks": plan.total_tasks,
            "successful_tasks": success_count,
            "failed_tasks": failed_count,
            "success_rate": (success_count / plan.total_tasks * 100) if plan.total_tasks > 0 else 0,
            "total_duration_seconds": total_duration,
            "average_task_duration": total_duration / plan.total_tasks if plan.total_tasks > 0 else 0,
            "tasks_by_priority": self._group_tasks_by_priority(plan),
            "errors": [r.error for r in execution_results if r.error]
        }

    def _group_tasks_by_priority(self, plan: Plan) -> Dict[int, int]:
        """Agrupa tareas por prioridad."""
        priority_groups = {}
        for task in plan.tasks:
            if task.priority not in priority_groups:
                priority_groups[task.priority] = 0
            priority_groups[task.priority] += 1
        return priority_groups

    def get_report(self, plan_id: str) -> OrchestrationReport:
        """Obtiene un reporte previamente generado."""
        if plan_id not in self.reports:
            raise ValueError(f"Reporte no encontrado: {plan_id}")
        return self.reports[plan_id]

    def list_reports(self) -> List[str]:
        """Lista todos los reportes generados."""
        return list(self.reports.keys())

    def export_report_json(self, plan_id: str) -> str:
        """
        Exporta un reporte en formato JSON.
        
        Args:
            plan_id: ID del plan
            
        Returns:
            str: JSON del reporte
        """
        report = self.get_report(plan_id)
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)

    def get_last_report(self) -> OrchestrationReport:
        """Obtiene el último reporte generado."""
        if not self.reports:
            raise ValueError("No hay reportes disponibles")
        return self.reports[self.current_plan_id]
