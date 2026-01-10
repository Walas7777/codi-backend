import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Agregar el directorio actual al path para importar app.main
sys.path.insert(0, os.path.abspath("."))

# Importar la aplicación backend original
from app.main import app as backend_app

# Crear una aplicación "wrapper" que simule el servidor de producción
# Esta app servirá tanto el backend (API) como el frontend (archivos estáticos)
production_app = FastAPI()

# Configurar CORS para permitir que el frontend hable con el backend
production_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar el backend en /api (o mantenerlo en la raíz si así está diseñado)
# En este caso, como el frontend espera llamar a http://localhost:8000,
# montaremos las rutas del backend directamente en la raíz, pero con cuidado de no solapar.
# Sin embargo, para simular Plesk donde suelen estar separados o en rutas distintas,
# lo más limpio es servir el frontend en / y la API en sus rutas originales.
# Dado que app.main ya define rutas, las incluimos.
production_app.include_router(backend_app.router)

# Servir el frontend compilado (dist) como archivos estáticos
# Esto simula que Nginx/Apache sirve el index.html y los assets
frontend_dist = os.path.join(os.path.dirname(__file__), "codi-ui/dist")

if os.path.exists(frontend_dist):
    print(f"Serving frontend from: {frontend_dist}")
    production_app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    print("WARNING: Frontend dist folder not found. Run 'pnpm build' first.")

if __name__ == "__main__":
    # Ejecutar en puerto 8000 para simular el entorno de producción
    uvicorn.run(production_app, host="0.0.0.0", port=8000)
