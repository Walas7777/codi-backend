FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer el puerto (Railway inyecta PORT)
ENV PORT=8000
EXPOSE $PORT

# Comando de inicio
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
