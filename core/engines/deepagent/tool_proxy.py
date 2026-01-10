from typing import Dict, Any

class CodiFileToolProxy:
    """
    Proxy seguro para FileTool que delega la ejecución al Core de CODI.
    No expone acceso directo al sistema de archivos.
    """
    name = "FileTool"

    def __init__(self, core_executor):
        self.core_executor = core_executor

    def run(self, **params: Dict[str, Any]) -> Any:
        """
        Ejecuta una acción de archivo a través del Executor de CODI.
        """
        # Validación CODI implícita en el Executor
        # Delegación al Core (Action / Executor)
        # Asumimos que core_executor tiene un método execute_action o similar
        # que acepta un tipo de acción y parámetros.
        
        # Mapeo de parámetros a la estructura de acción de CODI
        # Esto dependerá de cómo el Executor espera recibir la acción
        # Por ahora, simulamos una llamada genérica basada en el ejemplo
        
        # Identificar la intención basada en los parámetros o un parámetro 'intent' explícito
        intent = params.get("intent", "create_file") # Default a create_file si no se especifica
        
        # Construir el objeto de acción o llamar directamente
        # Aquí asumimos que execute_action toma (intent_name, parameters)
        return self.core_executor.execute_action(intent, params)

class ToolProxyFactory:
    @staticmethod
    def create_proxies(core_executor, allowed_tool_names):
        proxies = []
        if "FileTool" in allowed_tool_names:
            proxies.append(CodiFileToolProxy(core_executor))
        # Agregar más proxies según sea necesario
        return proxies
