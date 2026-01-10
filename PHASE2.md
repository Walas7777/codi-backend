# CODI Core - Documentación de la FASE 2: Integración con LLMs

## 1. Resumen
La **FASE 2** del proyecto CODI Core se centra en la integración de capacidades de **Large Language Models (LLMs)** para mejorar significativamente el análisis de objetivos, la generación de planes y la validación de resultados. Esta fase se ha implementado siguiendo estrictamente el principio de **no modificar el código de la FASE 1**, asegurando la compatibilidad hacia atrás y la funcionalidad continua de los componentes originales.

## 2. Componentes Agregados

| Módulo | Archivo | Descripción |
| :--- | :--- | :--- |
| **LLMIntegration** | `core/llm_integration.py` | Clase que encapsula la comunicación con la API de OpenAI (o compatible). Contiene métodos para el análisis de objetivos, la generación de planes y la validación de resultados, utilizando el modo `chat` para optimizar el uso de créditos. |
| **AIPlannerEnhanced** | `core/ai_planner.py` | Clase que hereda de `Planner` (FASE 1). Sobrescribe el método `analyze_objective` para utilizar la lógica de LLMIntegration, generando planes más inteligentes y detallados. Mantiene la funcionalidad de FASE 1 como *fallback* en caso de fallo de la IA. |

## 3. Actualizaciones de la API (app/main.py)

Se han añadido tres nuevos *endpoints* para exponer las nuevas funcionalidades de IA:

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/process-ai` | Procesa un objetivo completo utilizando el flujo de orquestación mejorado con **AIPlannerEnhanced** y **Executor** (FASE 1). Genera un plan inteligente, lo ejecuta y retorna un reporte. |
| `GET` | `/ai-plans/{plan_id}` | Obtiene un plan generado previamente por el **AIPlannerEnhanced**. |
| `POST` | `/validate-ai` | Envía los resultados de una ejecución al **LLMIntegration** para una validación y *feedback* inteligente por parte de la IA. |

**Nota Importante:** El *endpoint* original `/process` (FASE 1) permanece **intacto y completamente funcional**, utilizando el `Orchestrator` y `Planner` originales.

## 4. Configuración y Variables de Entorno

La integración con LLMs requiere la configuración de variables de entorno, detalladas en el archivo `.env.example`:

| Variable | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Clave de API para OpenAI o un servicio compatible. | `sk-tu_clave_aqui` |
| `OPENAI_MODEL` | Modelo de LLM a utilizar para las tareas de IA. | `gpt-4o-mini` |
| `LLM_TIMEOUT` | Tiempo máximo de espera para la respuesta del LLM (segundos). | `30` |
| `LLM_MAX_RETRIES` | Número máximo de reintentos en caso de fallo de la API. | `3` |

## 5. Pruebas

Se han incluido pruebas unitarias (`test_llm_integration.py` y `test_ai_planner.py`) para validar la funcionalidad de los nuevos módulos.

*   **Validación de FASE 1:** Se confirma que los tests de FASE 1 deben seguir pasando sin modificaciones.
*   **Validación de FASE 2:** Los nuevos tests verifican la conexión con el LLM, la estructura de los planes generados por IA y la correcta herencia en `AIPlannerEnhanced`.
