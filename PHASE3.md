# CODI Core - Documentación de la FASE 3: Memoria y Herramientas

## 1. Resumen
La **FASE 3** introduce dos capacidades fundamentales para la autonomía de CODI: **Memoria Persistente** y **Herramientas (Tools)**. Estos componentes permiten a CODI aprender de ejecuciones previas y realizar acciones concretas en el entorno (simulado), mejorando la toma de decisiones del planificador de IA.

## 2. Memoria Persistente

Se ha implementado un módulo de memoria simple basado en un archivo JSON (`memory/codi_memory.json`) para persistir datos clave.

| Módulo | Archivo | Descripción |
| :--- | :--- | :--- |
| **MemoryStore** | `memory/memory_store.py` | Clase que gestiona la lectura y escritura de la memoria. Almacena objetivos ejecutados, planes generados y resultados finales. |

**Integración:**
*   **Orchestrator:** Ahora guarda el objetivo, el plan y el resultado final en `MemoryStore` después de cada ejecución.
*   **AIPlannerEnhanced:** Consulta `MemoryStore` para obtener un resumen de la experiencia previa, que se inyecta en el *prompt* del LLM para mejorar la planificación.
*   **API:** Se han añadido los *endpoints* `/memory/summary` y `/memory/objectives` para consultar el estado de la memoria.

## 3. Herramientas (Tools)

Se ha implementado un sistema de herramientas que permite al LLM generar planes con pasos de acción concretos que el Executor puede ejecutar.

| Módulo | Archivo | Descripción |
| :--- | :--- | :--- |
| **Tool** | `tools/base_tool.py` | Clase base para todas las herramientas y `ToolManager` para su registro. |
| **FileTool** | `tools/file_tool.py` | Permite crear, sobrescribir y leer archivos. |
| **SystemTool** | `tools/system_tool.py` | Permite listar directorios y ejecutar comandos simples (simulados por seguridad). |
| **CodeTool** | `tools/code_tool.py` | Permite generar y modificar archivos de código. |

**Integración:**
*   **LLMIntegration:** El método `generate_plan` ahora habilita la funcionalidad de *tools* de la API de OpenAI, permitiendo al LLM seleccionar una herramienta y sus argumentos.
*   **Planner:** La clase `Task` ahora incluye los campos `tool` y `tool_args` para almacenar la herramienta seleccionada por el LLM.
*   **Executor:** El método `_execute_task` ahora verifica si la tarea tiene una herramienta asignada. Si es así, utiliza el `ToolManager` para obtener la herramienta y ejecutar su método `execute()` con los argumentos proporcionados.

## 4. Estructura de Directorios (FASE 3)

```
codi-core/
├── core/
├── agents/                 <-- Nuevo (vacío, para futura expansión)
├── memory/                 <-- Nuevo
│   └── memory_store.py
├── tools/                  <-- Nuevo
│   ├── base_tool.py
│   ├── file_tool.py
│   ├── system_tool.py
│   └── code_tool.py
├── app/
├── requirements.txt
├── PHASE2.md
└── PHASE3.md               <-- Nuevo
```

## 5. Criterios de Éxito Verificados

*   ✅ **Memoria Persistente:** Implementada y funcional, integrada en Orchestrator y AIPlannerEnhanced.
*   ✅ **Herramientas:** Implementadas y registradas en `ToolManager`, listas para ser usadas por el LLM.
*   ✅ **Compatibilidad:** Los flujos de FASE 1 y FASE 2 siguen funcionando.
*   ✅ **Integración:** El Executor puede ejecutar tareas que invocan herramientas.
*   ✅ **API:** Nuevos *endpoints* para consultar la memoria.
