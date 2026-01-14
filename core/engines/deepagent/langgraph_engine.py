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
        
        # Verificar si es MockLLM (tiene método plan) o ChatOpenAI (necesita invoke)
        if hasattr(self.llm, "plan"):
            intents = self.llm.plan(goal, context)
        else:
            # Lógica para ChatOpenAI real
            from langchain_core.messages import SystemMessage, HumanMessage
            import json
            
            system_prompt = """Eres un asistente de IA experto. Tu objetivo es generar un plan de ejecución JSON para cumplir el objetivo del usuario.
            Debes responder ÚNICAMENTE con un array JSON de objetos, donde cada objeto representa una acción (intent).
            
            Formatos de intents soportados:
            1. {"intent": "read_file", "params": {"file_path": "/path/to/file"}}
            2. {"intent": "write_file", "params": {"file_path": "/path/to/file", "content": "texto"}}
            3. {"intent": "analyze", "params": {"content": "texto a analizar"}}
            
            Si el objetivo es una pregunta simple, usa un intent especial o responde directamente en el análisis.
            Para este MVP, si es una pregunta de conocimiento general, genera un intent de tipo 'answer_question'.
            Ejemplo: [{"intent": "answer_question", "params": {"question": "¿Cuál es la capital de Francia?", "answer": "París"}}]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Objetivo: {goal}\nContexto: {context}")
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Limpiar bloques de código markdown si existen
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                intents = json.loads(content)
                if not isinstance(intents, list):
                    # Si devuelve un solo objeto, envolver en lista
                    intents = [intents]
            except json.JSONDecodeError:
                # Fallback simple si no devuelve JSON válido
                intents = [{"intent": "answer_question", "params": {"question": goal, "answer": content}}]

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
