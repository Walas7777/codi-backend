# ACTION_INTENT_CONTRACT_v1

**Estado:** CONGELADO ❄️
**Versión:** 1.0
**Fecha:** 2026-01-06

Este documento define el contrato estricto de comunicación entre la Capa de Inteligencia (IA) y el Core de Ejecución en CODI. Cualquier desviación de este contrato debe resultar en un error explícito.

---

## 1. Definiciones

### 1.1 Intent (Intención)
Es una estructura de datos abstracta generada por la IA que representa "qué se quiere hacer" sin detallar "cómo se hace técnicamente".

**Formato JSON:**
```json
{
  "name": "string (obligatorio, snake_case)",
  "params": "dict (obligatorio, puede estar vacío)"
}
```

### 1.2 Action (Acción)
Es una estructura de datos concreta y ejecutable generada por el Core (`ActionBuilder`) a partir de un Intent. Representa una instrucción directa para una Herramienta específica.

**Clase Python (`core.action.Action`):**
```python
@dataclass
class Action:
    type: str          # Identificador único de tipo de acción (ej: CREATE_FILE)
    tool: str          # Nombre de la herramienta registrada (ej: FileTool)
    params: Dict       # Parámetros validados para la herramienta
```

---

## 2. Catálogo de Intents Soportados

Cualquier `intent.name` que no esté en esta lista debe lanzar `ValueError` en `ActionBuilder`.

| Intent Name | Params Requeridos | Tool Mapeada | Action Type |
|-------------|-------------------|--------------|-------------|
| `create_file` | `filename`, `content` | `FileTool` | `CREATE_FILE` |
| `analyze_text` | `path` | `FileTool` | `ANALYZE_TEXT` |
| `inspect_zip` | `zip_path` | `FileTool` | `INSPECT_ZIP` |

---

## 3. Reglas de Validación (Hardening)

1. **Prohibido Fallback Silencioso:** Si un Intent no es reconocido, el sistema DEBE fallar inmediatamente. No se permite intentar "adivinar" o degradar a un plan básico.
2. **Validación de Parámetros:** Si faltan parámetros obligatorios para un Intent, `ActionBuilder` DEBE lanzar error.
3. **Existencia de Herramientas:** Si la `tool` mapeada en una Action no está registrada en `ToolManager`, la ejecución DEBE fallar.

---

## 4. Flujo de Datos

1. **Input:** Objetivo (str) + Archivos (opcional)
2. **AIPlanner:** Genera `List[Intent]`
3. **ActionBuilder:** Transforma `Intent` -> `Action` (Valida contrato)
4. **Executor:** Recibe `List[Action]` -> Ejecuta en `ToolManager`
5. **Output:** Resultado estructurado o Error Explícito.

---

**FIN DEL CONTRATO**
Cualquier modificación requiere un proceso de revisión de arquitectura (RFC).
