from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

class LangGraphEngine:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.graph = self._build_graph()

    def _build_graph(self):
        # Definir el estado como un diccionario
        graph = StateGraph(dict)

        # Agregar nodos
        graph.add_node("plan", self._plan)
        graph.add_node("execute", self._execute)

        # Definir flujo
        graph.set_entry_point("plan")
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    def _plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fase de planificación: El LLM decide qué acciones tomar.
        Produce una lista de intents (no ejecuta nada aún).
        """
        goal = state["goal"]
        context = state.get("context", {})
        
        # Prompt simple para el LLM (MVP)
        # En producción, esto sería un prompt más elaborado o un chain
        # Aquí simulamos que el LLM devuelve una estructura JSON válida
        # Para el MVP y pruebas, si self.llm es un mock, devolverá lo esperado.
        # Si es real, necesitaríamos parsear la salida.
        
        # Asumimos que self.llm.plan es un método que abstrae la llamada al modelo
        # y devuelve una lista de diccionarios con 'intent' y 'params'.
        intents = self.llm.plan(goal, context)
        
        return {"intents": intents}

    def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fase de ejecución: Itera sobre los intents y usa los proxies de herramientas.
        """
        results = []
        warnings = []
        errors = []
        
        for intent in state.get("intents", []):
            try:
                # self.tools es un objeto que maneja la ejecución segura (ToolProxy)
                # Asumimos que tiene un método execute(intent_data)
                result = self.tools.execute(intent)
                results.append(f"Executed {intent.get('intent')}: {result}")
            except Exception as e:
                errors.append(str(e))
                # Decidir si detener o continuar. Para MVP, registramos error y continuamos.
        
        return {
            "steps": results,
            "warnings": warnings,
            "errors": errors,
            "result": "Execution completed"
        }

    def run(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el grafo con el objetivo dado.
        """
        # Invocar el grafo compilado
        final_state = self.graph.invoke({
            "goal": goal,
            "context": context
        })
        
        # Extraer resultados del estado final
        # Nota: LangGraph devuelve el estado final acumulado
        return {
            "steps": final_state.get("steps", []),
            "warnings": final_state.get("warnings", []),
            "errors": final_state.get("errors", []),
            "result": final_state.get("result")
        }
