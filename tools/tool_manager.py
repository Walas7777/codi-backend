class ToolManager:
    def __init__(self):
        self.tools = {}

    def register(self, name, tool):
        self.tools[name] = tool

    def execute(self, name, params):
        if name not in self.tools:
            raise ValueError(f"Tool not registered: {name}")
        
        tool = self.tools[name]
        
        # Adaptador simple para FileTool basado en params (FASE 1.5)
        if name == "FileTool":
            if "filename" in params and "content" in params:
                return tool.write(params["filename"], params["content"])
            elif "path" in params:
                return tool.read(params["path"])
            elif "zip_path" in params:
                return tool.extract_zip(params["zip_path"], "extracted_zip")
        
        # Adaptador para QuestionTool
        if name == "QuestionTool":
            if "question" in params:
                return tool.run(question=params["question"])
            
        # Fallback genérico si la tool tiene método run
        if hasattr(tool, 'run'):
            return tool.run(**params)
        
        raise ValueError(f"Cannot execute tool {name} with params {params}")
