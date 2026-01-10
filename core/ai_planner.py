class AIPlannerEnhanced:
    def __init__(self, llm):
        self.llm = llm

    def plan(self, objective: str, files=None):
        # La IA SOLO devuelve intenciones abstractas
        # Ejemplo esperado:
        # {"intents":[{"name":"create_file","params":{"filename":"test.txt","content":"OK"}}]}
        plan = self.llm.plan(objective, files)
        if "intents" not in plan:
            raise RuntimeError("Planner did not return intents")
        return plan["intents"]
