# CODI Core - Documentación de la FASE 4: Interfaz Web (UI)

## 1. Resumen
La **FASE 4** dota a CODI de una interfaz web moderna y funcional, similar a la experiencia de Manus.im. Esta interfaz permite a los usuarios interactuar con el agente de manera visual, cargar archivos como contexto y monitorear la ejecución de tareas en tiempo real.

## 2. Arquitectura Frontend-Backend

### Frontend (codi-ui)
- **Stack:** Next.js + Tailwind CSS + Shadcn UI
- **Diseño:** Estilo profesional con Sidebar oscuro y Tabs (Mockup 2)
- **Características:**
  - Carga de archivos Drag & Drop (PDF, TXT, ZIP, Code)
  - Visualización de logs tipo terminal
  - Renderizado de resultados JSON
  - Diseño responsivo y modo oscuro/claro

### Backend (codi-core API)
- **Stack:** FastAPI (Python)
- **Nuevos Endpoints:**
  - `POST /upload`: Recepción de archivos multipart
  - `POST /process-with-files`: Ejecución de objetivos con contexto de archivos
- **Integración:** Conecta directamente con `AIPlannerEnhanced` (FASE 2) y `Executor` (FASE 1)

## 3. Estructura de Archivos

```
codi-core/
├── app/
│   └── main.py                 # API actualizada con soporte de archivos
├── core/                       # Componentes FASE 1-3 (intactos)
├── codi-ui/                    # NUEVO: Frontend completo
│   ├── client/
│   │   ├── src/
│   │   │   ├── components/     # FileUploader, Layout, etc.
│   │   │   ├── pages/          # Home.tsx
│   │   │   └── ...
│   └── ...
├── uploads/                    # Directorio temporal de archivos
├── PHASE4.md                   # Esta documentación
└── ...
```

## 4. Guía de Uso

### Prerrequisitos
- Node.js 18+
- Python 3.11+

### Ejecución Backend
```bash
cd codi-core
source venv/bin/activate
uvicorn app.main:app --reload
```

### Ejecución Frontend
```bash
cd codi-ui
pnpm dev
```

## 5. Flujo de Datos
1. Usuario sube archivos en la UI -> Backend los guarda en `/uploads`
2. Usuario envía objetivo -> Backend recibe texto + referencias a archivos
3. `AIPlannerEnhanced` analiza objetivo + contenido de archivos
4. `Executor` realiza tareas
5. Resultados se muestran en la UI en tiempo real

## 6. Criterios de Éxito Verificados
- ✅ Interfaz similar a Manus implementada
- ✅ Carga de archivos funcional
- ✅ Ejecución end-to-end validada
- ✅ Backend extendido sin romper FASE 1-3
