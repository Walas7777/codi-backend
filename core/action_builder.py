import logging
from core.action import Action

logger = logging.getLogger(__name__)

INTENT_MAP = {
    "create_file": lambda p: Action(
        type="CREATE_FILE",
        tool="FileTool",
        params={"filename": p["filename"], "content": p.get("content", "")}
    ),
    "analyze_text": lambda p: Action(
        type="ANALYZE_TEXT",
        tool="FileTool",
        params={"path": p["path"]}
    ),
    "inspect_zip": lambda p: Action(
        type="INSPECT_ZIP",
        tool="FileTool",
        params={"zip_path": p["zip_path"]}
    ),
    "answer_question": lambda p: Action(
        type="ANSWER_QUESTION",
        tool="QuestionTool",
        params={"question": p.get("question") or p.get("query") or p.get("text") or p.get("objective")}
    ),
}

class ActionBuilder:
    def build(self, intent: dict) -> Action:
        name = intent.get("name")
        params = intent.get("params", {})
        
        logger.info(f"[ActionBuilder] Procesando intent: {name}")
        
        if not name:
            error_msg = "[ActionBuilder] Intent sin nombre"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if name not in INTENT_MAP:
            error_msg = f"[ActionBuilder] Intent desconocido: {name} - Violación de Contrato v1"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            action = INTENT_MAP[name](params)
            logger.info(f"[ActionBuilder] Acción construida: {action.type} -> {action.tool}")
            return action
        except KeyError as e:
            error_msg = f"[ActionBuilder] Faltan parámetros obligatorios para {name}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
