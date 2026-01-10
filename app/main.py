from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import shutil
import sys
import logging

# Asegurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.orchestrator import Orchestrator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- CORS CONFIGURATION (NUCLEAR OPTION) ---
# Explicitly allow everything to ensure Railway connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow ALL methods
    allow_headers=["*"],  # Allow ALL headers
)

# --- CUSTOM MIDDLEWARE AS BACKUP ---
# In case the standard middleware is bypassed or fails
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

# Inicializar Orchestrator (Singleton)
orchestrator = Orchestrator()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process")
def process(objective: str):
    try:
        logger.info(f"Procesando objetivo: {objective}")
        # Simular usuario con permisos para MVP
        user_context = {"can_use_deepagent": True}
        report = orchestrator.process_objective(objective, user_context=user_context)
        return report.to_dict()
    except Exception as e:
        logger.error(f"Error procesando objetivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-with-files")
def process_with_files(objective: str = Form(...), files: List[UploadFile] = File(default=[])):
    try:
        # Guardar archivos
        saved_files = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        # TODO: Pasar archivos al contexto del usuario o pre-procesarlos
        # Por ahora, el Orchestrator no recibe archivos directos en process_objective,
        # pero podríamos pasarlos en user_context si se implementa.
        # Para MVP, asumimos que los archivos están en UPLOAD_DIR y el agente puede leerlos si se le indica.
        
        user_context = {"files": saved_files, "can_use_deepagent": True}
        report = orchestrator.process_objective(objective, user_context=user_context)
        return report.to_dict()
    except Exception as e:
        logger.error(f"Error procesando con archivos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    """Devuelve la lista de IDs de reportes disponibles."""
    return {"history": orchestrator.list_reports()}

@app.get("/history/{plan_id}")
def get_report(plan_id: str):
    """Devuelve un reporte específico por ID."""
    try:
        report = orchestrator.get_report(plan_id)
        return report.to_dict()
    except ValueError:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "mode": "FASE 7 (DeepAgent + LangGraph)",
        "deepagent_enabled": os.getenv("DEEPAGENT_ENABLED", "true")
    }
