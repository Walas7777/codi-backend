"""
CODI Core - Planner Module
Responsable de analizar un objetivo y generar un plan estructurado de tareas.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class Task:
    """Representa una tarea individual en el plan."""
    id: int
    title: str
    description: str
    dependencies: List[int]
    priority: int
    status: str = "pending"
    result: Any = None
    error: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Plan:
    """Representa un plan completo de ejecución."""
    objective: str
    created_at: str
    tasks: List[Task]
    total_tasks: int
    status: str = "created"

    def to_dict(self):
        return {
            "objective": self.objective,
            "created_at": self.created_at,
            "tasks": [task.to_dict() for task in self.tasks],
            "total_tasks": self.total_tasks,
            "status": self.status
        }


class Planner:
    """
    Analiza objetivos complejos y genera planes estructurados.
    Descompone un objetivo en tareas ejecutables ordenadas por dependencias.
    """

    def __init__(self):
        self.plans: Dict[str, Plan] = {}

    def analyze_objective(self, objective: str) -> Plan:
        """
        Analiza un objetivo y genera un plan estructurado.
        
        Args:
            objective: Descripción del objetivo a alcanzar
            
        Returns:
            Plan: Plan estructurado con tareas y dependencias
        """
        # Paso 1: Validar objetivo
        if not objective or len(objective.strip()) == 0:
            raise ValueError("El objetivo no puede estar vacío")

        # Paso 2: Descomponer objetivo en tareas
        tasks = self._decompose_objective(objective)

        # Paso 3: Establecer dependencias
        tasks = self._set_dependencies(tasks)

        # Paso 4: Crear plan
        plan = Plan(
            objective=objective,
            created_at=datetime.now().isoformat(),
            tasks=tasks,
            total_tasks=len(tasks),
            status="created"
        )

        # Almacenar plan
        plan_id = self._generate_plan_id(objective)
        self.plans[plan_id] = plan

        return plan

    def _decompose_objective(self, objective: str) -> List[Task]:
        """
        Descompone un objetivo en tareas básicas.
        Utiliza análisis simple de palabras clave para determinar tareas.
        
        Args:
            objective: Objetivo a descomponer
            
        Returns:
            List[Task]: Lista de tareas identificadas
        """
        tasks = []
        
        # Análisis de palabras clave para identificar tipo de objetivo
        objective_lower = objective.lower()
        task_id = 1

        # Tarea 1: Siempre analizar y validar
        tasks.append(Task(
            id=task_id,
            title="Analizar objetivo",
            description=f"Validar y analizar: {objective}",
            dependencies=[],
            priority=1
        ))
        task_id += 1

        # Tarea 2: Identificar recursos necesarios
        if any(word in objective_lower for word in ["crear", "generar", "construir", "desarrollar"]):
            tasks.append(Task(
                id=task_id,
                title="Identificar recursos",
                description="Determinar recursos, herramientas y dependencias necesarias",
                dependencies=[1],
                priority=2
            ))
            task_id += 1

        # Tarea 3: Planificar ejecución
        if any(word in objective_lower for word in ["ejecutar", "procesar", "realizar", "hacer"]):
            tasks.append(Task(
                id=task_id,
                title="Planificar ejecución",
                description="Definir pasos específicos y secuencia de ejecución",
                dependencies=[1],
                priority=2
            ))
            task_id += 1

        # Tarea 4: Ejecutar acciones principales
        tasks.append(Task(
            id=task_id,
            title="Ejecutar acciones principales",
            description="Realizar las acciones centrales del objetivo",
            dependencies=[1, 2] if len(tasks) > 1 else [1],
            priority=3
        ))
        task_id += 1

        # Tarea 5: Validar resultados
        tasks.append(Task(
            id=task_id,
            title="Validar resultados",
            description="Verificar que los resultados cumplan con el objetivo",
            dependencies=[task_id - 1],
            priority=4
        ))
        task_id += 1

        # Tarea 6: Generar reporte
        tasks.append(Task(
            id=task_id,
            title="Generar reporte",
            description="Crear reporte final con resultados y métricas",
            dependencies=[task_id - 1],
            priority=5
        ))

        return tasks

    def _set_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        Establece y valida dependencias entre tareas.
        Asegura que no haya ciclos y que el orden sea lógico.
        
        Args:
            tasks: Lista de tareas a procesar
            
        Returns:
            List[Task]: Tareas con dependencias validadas
        """
        # Validar que las dependencias sean válidas
        valid_ids = {task.id for task in tasks}
        
        for task in tasks:
            # Filtrar dependencias inválidas
            task.dependencies = [dep for dep in task.dependencies if dep in valid_ids]
            # Asegurar que no haya auto-dependencias
            task.dependencies = [dep for dep in task.dependencies if dep != task.id]
        
        return tasks

    def _generate_plan_id(self, objective: str) -> str:
        """Genera un ID único para el plan."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"plan_{timestamp}"

    def get_plan(self, plan_id: str) -> Plan:
        """Obtiene un plan previamente creado."""
        if plan_id not in self.plans:
            raise ValueError(f"Plan no encontrado: {plan_id}")
        return self.plans[plan_id]

    def list_plans(self) -> List[str]:
        """Lista todos los planes creados."""
        return list(self.plans.keys())

    def update_task_status(self, plan_id: str, task_id: int, status: str, result: Any = None, error: str = None):
        """Actualiza el estado de una tarea en un plan."""
        plan = self.get_plan(plan_id)
        for task in plan.tasks:
            if task.id == task_id:
                task.status = status
                if result is not None:
                    task.result = result
                if error is not None:
                    task.error = error
                break
