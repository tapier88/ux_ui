# ARCHITECTURE_PRINCIPLES.md — Principios de Gobernanza Transversal

**Origen:** estos principios vienen de una auditoría de arquitectura sobre un sistema de trading cuantitativo (Gold Bridge) del mismo operador de este proyecto. No es casualidad que apliquen aquí: un sistema de trading serio y un agente de diseño autónomo serio comparten el mismo problema de fondo — **cómo dejar que un modelo probabilístico (LLM) aporte juicio, sin dejar que decida solo, sin red, sin medición.**

Cada principio de trading se traduce abajo a su equivalente exacto en este proyecto. Esto no es documentación decorativa: son restricciones de diseño obligatorias para **todas las fases futuras del ROADMAP**.

## 1. El LLM/skill no decide solo — solo aporta opinión de contexto

**Trading:** Gemini solo devuelve BUY/SELL/HOLD/CLOSE. Todo lo demás (riesgo, tamaño de posición, ejecución) es determinístico.

**Diseño:** `Redesign Intelligence` y `Design Execution Planner` pueden sugerir dirección creativa (paleta, tipografía, layout), pero **nunca deciden solos si un diseño está listo para salir al cliente**. Eso lo decide el `GovernanceGate` (ver §5) con reglas determinísticas: contraste WCAG, preservación de colores de marca reales, coherencia con el `BrandDNAProfile`, performance mínimo. Ninguna "opinión creativa" del sistema puede saltarse estas reglas.

## 2. Pipeline único, cada etapa testeable por separado

**Trading:** MT5 → OHLC → Indicators → Features → LLM → Risk Manager → MT5.

**Diseño:** Website Intelligence → Brand DNA Extractor → Redesign Intelligence → Design Resource Hub → Design Execution Planner → Site Builder → Governance Gate → Git Persistence. Ya existe la mayoría; falta conectarlo (Fase 1 del ROADMAP) y el Gate nuevo.

## 3. Separación estricta entre "extracción de features" y "motor de decisión"

**Trading:** `market_features.py` (qué es el mercado ahora) separado de `llm_engine.py` (qué hacer con eso).

**Diseño:** ya está en el plan (Fase 2B): `Brand DNA Extractor` (qué es esta marca) es un módulo aparte de `Redesign Intelligence` (qué hacer con esa marca). Un `RedesignIntelligence` nunca debe extraer datos de marca por su cuenta — siempre los recibe ya normalizados.

## 4. Todo se registra: prompt/insumo → decisión → resultado real

**Trading:** logs JSON de cada ciclo (prompt, respuesta, mercado, resultado) para poder entrenar, hacer RAG, medir.

**Diseño:** esto es exactamente lo que ya construimos como `MemoryStore` (Fase 0.6d), pero hay que usarlo con esta disciplina: cada tarea debe grabar `insumo → decisión → resultado`, no solo el resultado final. Si más adelante un cliente rechaza un rediseño, esa razón debe quedar en memoria (`MemoryCategory.LESSON_LEARNED`) ligada al `BrandDNAProfile` que se usó, para que la próxima decisión de `Redesign Intelligence` sobre una marca similar pueda consultarlo.

## 5. Sistema de puntuación (confluencia) antes de actuar — NO ejecutar la salida del modelo directamente

**Trading:** no se opera solo porque Gemini dijo BUY. Se construye un score ponderado (Gemini +30, M15 +25, H1 +20, spread +15, confianza +15) y solo se opera si `score >= 80`.

**Diseño — esta es la pieza que implementé hoy:** un rediseño no se considera "listo para el cliente" solo porque `Design Execution Planner` terminó. Se calcula un **Elevation Score** ponderado (alineación de marca, accesibilidad, artesanía visual, performance, impacto SEO, originalidad) y solo pasa el gate si supera el umbral configurado — igual que el trading bot no opera con score bajo. Ver `harness/core/governance/`.

## 6. Pesos configurables, no hardcodeados

**Trading:** `SCORING_WEIGHTS` en config, no en código — así se optimiza con datos históricos sin tocar código.

**Diseño:** el `ElevationScorer` recibe sus pesos desde configuración (dict/YAML), no están quemados en la lógica. Cuando tengamos suficientes rediseños con resultado conocido (aceptado/rechazado por cliente), esos pesos se pueden re-calibrar con datos reales, igual que en trading.

## 7. Motor de reemplazo/replay del modelo de juicio (pluggable engine)

**Trading:** `BaseDecisionEngine` → Gemini / OpenAI / DeepSeek / modelo propio, intercambiables sin tocar el resto del pipeline.

**Diseño:** el harness ya tiene el patrón correcto para esto (Qwen Adapter en `harness/skills`). Hay que generalizarlo: cualquier skill que necesite "juicio creativo" (Redesign Intelligence, Design Execution Planner) debe consumir una interfaz `BaseDesignJudgmentEngine`, no un proveedor específico. Esto es tarea de Fase 1/4 — lo dejo anotado en el ROADMAP.

## 8. Replay para comparar versiones

**Trading:** re-ejecutar el mismo log histórico contra un modelo/prompt nuevo, comparar resultados.

**Diseño:** dado que `MemoryStore` guarda inspecciones y perfiles de marca (Fase 0.6d), un "replay de diseño" es re-correr `Redesign Intelligence` + `Design Execution Planner` contra un `BrandDNAProfile` ya guardado, con una versión nueva del motor de juicio, y comparar el `Elevation Score` resultante. Esto es cómo mejoramos el agente con evidencia, no por intuición — anotado como tarea futura en Fase 7.

## 9. Caché de decisiones cuando el insumo casi no cambió

**Trading:** no volver a llamar al LLM si las features son casi idénticas a la última vela.

**Diseño:** antes de re-extraer el ADN de marca de un dominio, `Brand DNA Extractor` debe consultar `MemoryStore.latest(subject=dominio, category=BRAND_PROFILE)` — si es reciente y el sitio no cambió, reusarlo. Ya está anotado en el ROADMAP (Fase 2B), pero ahora queda explícito como principio general, no solo como optimización de un skill.

## 10. Métricas acumuladas del sistema completo, no solo del último resultado

**Trading:** `performance.json` con Win Rate, Profit Factor, Drawdown — para medir si una versión nueva del bot es objetivamente mejor.

**Diseño:** el agente necesita su propio `performance.json` equivalente: cuántas propuestas se generaron, cuántas pasaron el Governance Gate a la primera, Elevation Score promedio, tasa de aceptación del cliente (cuando exista Fase 6 de envío), rondas de revisión promedio. Sin esto, "mejoramos el agente" es una opinión, no un hecho medible — igual que en trading.

## 11. Backtesting reutilizando exactamente el mismo pipeline

**Trading:** el backtester no duplica lógica; corre el mismo código que producción.

**Diseño:** cuando existan sitios de referencia con resultado conocido (antes/después reales, no inventados), deben poder correr por el pipeline real (`Website Intelligence → ... → Governance Gate`) para validar que el Elevation Score se mueve en la dirección correcta — no un script aparte que reimplementa la lógica.

## 12. El modelo es un clasificador de contexto, no un oráculo

**Trading:** no asumir que el LLM predice el mercado; es una opinión adicional sobre contexto ya estructurado, gobernada después por reglas objetivas.

**Diseño:** este es el principio más importante de todos, y responde directamente a tu preocupación de "salir de los diseños genéricos de IA". El agente **no le pregunta a un LLM "hazme un diseño bonito"**. Le da contexto ya estructurado y verificado (`BrandDNAProfile` real extraído del sitio, referencias reales de `Design Resource Hub`, reglas de accesibilidad, sistema de espaciado) y el LLM opina *dentro de esa estructura*. La estructura gana siempre; el LLM nunca improvisa sin ella. Eso es lo que separa un resultado de 500 USD (LLM improvisando libre) de uno de 5.000-20.000 USD (LLM operando dentro de un sistema de diseño real, con reglas de nivel mundial y datos reales de la marca).

---

## Nuevos artefactos creados a partir de este documento

- `harness/core/governance/` — `ElevationScorer` (scoring configurable) y `GovernanceGate` (bloquea/aprueba, con evento estructurado), con tests.
- Ampliación de `EventType` (`harness/core/events`) con eventos estructurados de gobernanza (`SCORE_TOO_LOW`, `GATE_APPROVED`, `GATE_BLOCKED`, `HUMAN_REVIEW_REQUIRED`) — equivalente a `SCORE_TOO_LOW`/`NEWS_BLOCK`/`CIRCUIT_BREAKER` del trading bot.
- Este documento, referenciado desde `ROADMAP.md`.
