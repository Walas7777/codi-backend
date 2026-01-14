from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
        "version": "7.1",
        "mode": "FASE 7.1 (Simplified + CORS Fix)",
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "mode": "FASE 7.1 (Simplified + CORS Fix)",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "CORS preflight handled"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
