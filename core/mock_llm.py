class MockLLM:
    def plan(self, objective, files=None):
        # Determinístico para pruebas
        # Detectar intención basada en objetivo simple (simulación)
        
        if "test_tool.txt" in objective or "OK" in objective:
            return {
                "intents": [
                    {
                        "name": "create_file",
                        "params": {"filename": "test_tool.txt", "content": "OK"}
                    }
                ]
            }
        elif "analisis.txt" in objective or "código secreto" in objective:
             return {
                "intents": [
                    {
                        "name": "analyze_text",
                        "params": {"path": "analisis.txt"}
                    }
                ]
            }
        elif "test_code.zip" in objective or "ZIP" in objective:
             return {
                "intents": [
                    {
                        "name": "inspect_zip",
                        "params": {"zip_path": "test_code.zip"}
                    }
                ]
            }
            
        # Default fallback
        return {"intents": []}
