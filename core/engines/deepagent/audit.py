import logging

logger = logging.getLogger("deepagent.audit")
logger.setLevel(logging.INFO)

# Configurar handler si no existe
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def audit_execution(execution_id, goal, steps, warnings, errors):
    """
    Registra la auditoría de una ejecución de DeepAgent.
    """
    logger.info({
        "execution_id": execution_id,
        "goal": goal,
        "steps": steps,
        "warnings": warnings,
        "errors": errors
    })
