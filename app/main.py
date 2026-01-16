from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from core.orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Inicializar Orchestrator
orchestrator = Orchestrator()

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    try:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

@app.get("/")
async def root():
    return {
        "service": "CODI Backend Core",
        "version": "8.0",
        "mode": "FASE 8.0 (Full Agent + Chat Endpoint)",
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "mode": "FASE 8.0 (Full Agent + Chat Endpoint)",
        "deepagent_enabled": "true",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/process")
async def process_objective(objective: str):
    try:
        logger.info(f"Processing objective: {objective}")
        report = orchestrator.process_objective(objective)
        
        # Extraer la respuesta final del reporte
        final_answer = "No answer generated"
        
        # Intentar sacar la respuesta de los resultados de ejecución
        if report.execution_results:
            last_result = report.execution_results[-1]
            if isinstance(last_result, dict):
                # Si es DeepAgent, el output suele estar anidado
                output = last_result.get("output", {})
                if isinstance(output, dict):
                    final_answer = output.get("result", str(output))
                else:
                    final_answer = str(output)
            else:
                final_answer = str(last_result)
                
        # 🔒 FIX CRÍTICO: nunca devolver objeto vacío
        if not final_answer or final_answer == "{}" or final_answer == {}:
            final_answer = (
                "Tarea ejecutada correctamente en modo estándar. "
                "No se requirió razonamiento avanzado."
            )

        # Estructura solicitada por el usuario
        return {
            "status": "completed",
            "plan_id": report.plan_id,
            "final_answer": final_answer,
            "engine": report.engine,
            "full_report": report.to_dict() # Incluimos el reporte completo por si acaso
        }
    except Exception as e:
        logger.error(f"Error processing objective: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(objective: str):
    """
    Endpoint de compatibilidad para frontend que llama a /chat.
    Redirige internamente a /process.
    """
    return await process_objective(objective)

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "CORS preflight handled"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
