# ROADMAP — Agente Autónomo de Diseño Web (Tapiero UX/UI Agent)

**Estado del documento:** vivo, se actualiza tarea por tarea.
**Última actualización:** 2026-08-09

## 1. Visión

Un agente 100% autónomo que ejecuta el ciclo completo de un diseñador junior freelance:

```
PROSPECTAR → INSPECCIONAR → APRENDER → DECIDIR → CONSTRUIR → EMPAQUETAR → ENVIAR
```

1. **Prospectar**: buscar sitios web reales con diseño/tipografía anticuada que necesiten el servicio.
2. **Inspeccionar**: analizar código, arquitectura, SEO y UX del sitio encontrado.
3. **Aprender**: antes de diseñar, consultar repos open-source, librerías y referencias de diseño reales — nunca plantillas genéricas de IA.
4. **Decidir**: estrategia de rediseño que preserva identidad de marca y datos originales del cliente.
5. **Construir**: generar el rediseño real (código), manteniendo SEO y mejorando visualmente.
6. **Empaquetar**: preparar una propuesta de valor (antes/después, justificación, impacto SEO).
7. **Enviar**: entregar la propuesta al cliente potencial por Email/Gmail/Telegram.

## 2. Estado actual (auditado 2026-08-09)

### Ya construido (28 commits, 5 skills)
| Skill | Qué hace | Tests |
|---|---|---|
| `website_intelligence` | Inspecciona un sitio/proyecto existente | ✅ 8/8 |
| `redesign_intelligence` | Decide qué conservar/eliminar/mejorar | ✅ 45/45 |
| `design_resource_hub` | Cataloga y selecciona recursos de diseño | ❌ sin tests |
| `design_execution_planner` | Convierte decisiones en plan técnico de build | ❌ sin tests |
| `site_builder` | Ejecuta el plan y modifica código real (con rollback) | ❌ sin tests |
| `core/git` | Persistencia y publicación en GitHub con gates de validación | ✅ 17/17 |

### Infraestructura base
Graph engine, State engine, Runtime, Events, Tool/Skill registries — funcionales pero con bugs críticos conocidos (ver HARNESS_AUDIT.md): sin timeout, sin cancelación, bug de status en fallos, condicionales rotos, sin persistencia de checkpoints.

### Lo que NO existe todavía (gap vs. visión completa)
- ❌ Orquestación end-to-end: nada conecta los 5 skills en un solo flujo ejecutable
- ❌ Prospección de clientes (buscar sitios candidatos)
- ❌ Análisis SEO explícito (existe análisis de diseño, no de SEO)
- ❌ Aprendizaje por referencia externa: clonar/estudiar repos open-source antes de diseñar
- ❌ Conectores MCP (Higgsfield y similares) y librerías externas
- ❌ Generación de la propuesta de valor (documento cliente-facing)
- ❌ Envío por Email/Gmail/Telegram
- ❌ Ciclo de autonomía real: PLAN→EXECUTE→OBSERVE→EVALUATE→DECIDE (hoy es un ejecutor de workflows, no un agente que decide)
- ❌ Documentación desactualizada (README/ARCHITECTURE describen solo V0.1 base)

## 2B-bis. Gobernanza transversal (nuevo, ver ARCHITECTURE_PRINCIPLES.md)

Se tradujeron 12 principios de arquitectura de un sistema de trading cuantitativo (Gold Bridge) a este agente — ver `ARCHITECTURE_PRINCIPLES.md` para el detalle completo de cada mapeo. El principio central: **el LLM/skill nunca decide solo si un rediseño está listo para el cliente**; siempre pasa por un gate determinístico de puntuación, igual que un bot de trading serio nunca ejecuta la señal cruda de un LLM sin un sistema de riesgo y scoring de por medio.

- [x] Elevation Scorer + Governance Gate — `harness/core/governance/` (comentarios de código limpiados de referencias a "trading bot"; la lógica es 100% de diseño, la única referencia externa queda en `ARCHITECTURE_PRINCIPLES.md` como nota de origen de los principios)
- [x] **Motor de teoría del color real** — `harness/skills/redesign_intelligence/color_intelligence.py`. Reemplaza el `ColorStrategyEngine` anterior, que solo repetía colores ya existentes en el perfil y sugería en texto plano "define un color de marca" cuando faltaban. Ahora: conversión HEX↔HSL, cálculo real de contraste WCAG (fórmula de luminancia relativa), generación de armonía (complementaria/análoga/triádica/split-complementaria — split-complementaria por defecto porque se ve considerada, no genérica), rampa de tintes/sombras 50-900 anclada al hue real de marca, colores semánticos (éxito/advertencia/error/info) sintonizados con la saturación de la marca en vez de copiados de un kit de UI genérico, y `ensure_contrast()` que ajusta automáticamente la claridad hasta cumplir AA en vez de solo advertir. Si el color de marca es casi neutro (baja saturación), usa estrategia monocromática en vez de forzar una armonía artificial — evita el "look genérico de IA" en marcas minimalistas.
- [x] Tests: `harness/tests/test_color_intelligence.py` (27 tests) + integración verificada con `redesign_intelligence` (45 tests existentes siguen pasando)
- [x] Eventos estructurados de gobernanza (`GATE_APPROVED`, `GATE_BLOCKED`, `SCORE_TOO_LOW`, `HUMAN_REVIEW_REQUIRED`) — `harness/core/events`
- [x] Integración con `MemoryStore`: toda evaluación (aprobada o bloqueada) queda registrada — insumo para recalibrar pesos con datos reales más adelante
- [x] Tests: `harness/tests/test_governance.py` (13 tests)
- [ ] Conectar `GovernanceGate` como paso obligatorio antes de `Site Builder` y antes de la Fase 6 (envío al cliente) — pendiente hasta Fase 1 (orquestación end-to-end)
- [ ] Definir las señales reales (`brand_alignment`, `accessibility`, `visual_craft`, `performance`, `seo_impact`, `originality`) como salidas medibles de cada skill existente, no como números inventados — esto depende de que Website Intelligence / Brand DNA Extractor / Design Execution Planner expongan métricas concretas (ratios de contraste reales, Core Web Vitals reales, etc.)
- [ ] `BaseDesignJudgmentEngine`: generalizar el patrón ya existente del Qwen Adapter para que cualquier skill de "juicio creativo" sea intercambiable entre proveedores de IA (Fase 1/4)
- [ ] `performance.json` del agente: métricas acumuladas (propuestas generadas, tasa de aprobación del gate, Elevation Score promedio, tasa de aceptación del cliente una vez exista Fase 6)

## 3. Fases de trabajo

### FASE 0 — Estabilizar la base (bloquea todo lo demás)
Si el runtime tiene bugs de estado/timeout/cancelación, un agente autónomo que corre sin supervisión es peligroso (loops infinitos, tareas "completadas" que en realidad fallaron).

- [x] 0.1 Fix CRITICAL-005: bug de status en fallos (task marcado "completed" aunque falle) — `harness/core/runtime/__init__.py`
- [x] 0.2 Implementar timeout real por nodo (ThreadPoolExecutor + future.result(timeout=...), shutdown no bloqueante) — `harness/core/runtime/__init__.py`
- [x] 0.3 Añadir `max_steps` para evitar loops infinitos — `RuntimeConfig.max_steps`, default 1000
- [x] 0.4 Implementar cancelación cooperativa (`runtime.cancel(task_id)`, chequeo entre nodos) — `harness/core/runtime/__init__.py`
- [x] 0.5 Arreglar evaluación de condicionales (CRITICAL-006) + detección de ciclos en `validate()` — `harness/core/graph/__init__.py`
- [x] 0.5b Tests nuevos para los 5 fixes anteriores — `harness/tests/test_runtime_fixes.py` (9 tests, todos pasan)
- [x] 0.6b Persistencia de checkpoints (CRITICAL-003) — `harness/core/state/storage.py` (`CheckpointStorage`, `FileCheckpointStorage`), recuperación tras "reinicio" vía `restore_task_from_persistent_storage()`. Backward-compatible: opt-in, nadie pierde el comportamiento anterior si no lo activa.
- [x] 0.6c Fix MED-003 (restauración parcial de checkpoint) y MED-007 (IDs de checkpoint predecibles) en el mismo módulo — `harness/core/state/__init__.py`
- [x] 0.6d **Sistema de memoria persistente entre tareas** — `harness/memory/__init__.py` (`MemoryStore`, `MemoryRecord`, `MemoryCategory`). JSONL en disco, thread-safe, con `remember()`, `recall()`, `latest()`, `search_text()`, `forget_subject()`. Es la base de "aprendizaje continuo": permite que Brand DNA Extractor, Website Intelligence, Redesign Intelligence y Site Builder guarden y reutilicen conocimiento entre tareas y entre reinicios del proceso, en vez de partir de cero cada vez.
- [x] 0.6 Actualizar README/ARCHITECTURE/GRAPH.md para reflejar el pipeline real de 5 skills + memoria + checkpoints persistentes — README.md reescrito con el pipeline completo y el diagrama real; ARCHITECTURE.md marcado con nota de alcance (documenta el motor base, no el pipeline de producto) y referencia cruzada a README/ROADMAP
- [x] 0.7 Tests para site_builder, design_resource_hub, design_execution_planner — **cerrado el hueco más peligroso**: `test_site_builder.py` (12 tests) prueba explícitamente que un build fallido a mitad de camino dispara rollback automático y el proyecto queda exactamente como estaba (archivo modificado restaurado, archivo creado a medias eliminado), no solo que "no crashea". `test_design_execution_planner.py` (13 tests) y `test_design_resource_hub.py` (10 tests) cubren el resto de los orquestadores sin cobertura previa.
- [x] **Design Language Library (adelanto de Fase 3)** — `harness/skills/design_resource_hub/design_language.py`. Primer preset real (`editorial_grid_minimal`) construido a partir de metodología de diseño documentada (grillas editoriales estrictas, tipografía con reglas de line-height/tracking, física de resortes para movimiento, sistema de 8px, sombras casi invisibles) — consultable por `Design Resource Hub` y aplicable a `LayoutPlanner`/`PaletteGenerator`/`MotionPlanner` como parámetros, nunca como colores o copy literales de una marca ajena (ver ARCHITECTURE_PRINCIPLES.md §12). Tests: `test_design_language.py` (11 tests, incluye verificación de que se aplica de verdad a los planners reales, no solo que existe como dato).
- [ ] 0.8 Conectar memoria y checkpoints persistentes como default real (hoy son opt-in) una vez que el pipeline end-to-end (Fase 1) exista y se pueda probar de punta a punta

**Nota de diseño (0.5):** la evaluación de condicionales ahora funciona así: un nodo `CONDITIONAL` ejecuta su `condition_func(state)` una sola vez, y el resultado (string) debe coincidir con la etiqueta `condition` de una arista saliente. Si ninguna coincide, se usan las aristas sin etiqueta como fallback. Antes, el código buscaba el string de la condición como clave dentro de `state.outputs`, lo cual nunca podía funcionar para branching real — quedó confirmado con test `test_conditional_routes_to_matching_branch`.

**Nota de diseño (0.3):** por defecto `max_steps=1000`. Como la Fase 7 (loops reales) todavía no existe, hoy esto solo protege contra bugs de enrutamiento; cuando se implementen nodos `LOOP` con lógica real, cada uno deberá definir su propia condición de terminación además de este límite global.

### FASE 1 — Orquestación end-to-end
- [ ] 1.1 Crear nodos de grafo para cada skill (hoy solo existe `git_persistence_node.py`)
- [ ] 1.2 Construir el grafo maestro: Website Intelligence → Redesign Intelligence → Design Resource Hub → Design Execution Planner → Site Builder → Git Persistence
- [ ] 1.3 Probar el pipeline completo contra un proyecto real de ejemplo

### FASE 2 — Skill de Prospección (Lead Finder)
Nuevo skill: buscar sitios web candidatos (tipografía anticuada, diseño desactualizado, señales de necesitar el servicio).
- [ ] 2.1 Definir criterios objetivos de "candidato" (tipografías detectadas, antigüedad del CSS/framework, Core Web Vitals, mobile-first ausente, etc.)
- [ ] 2.2 Tool de búsqueda/scraping controlado (con límites de red y respeto a robots.txt)
- [ ] 2.3 Scoring de leads + priorización

### FASE 2B — Skill de Extracción de ADN de Marca (Brand DNA Extractor)
Objetivo: dado solo una URL y/o imágenes de la empresa, el agente debe identificar la esencia de marca del cliente **antes** de rediseñar — para que el rediseño final se sienta como una versión superior de la misma marca, no como una plantilla genérica encima. Esta es la diferencia entre un sitio de 500 USD y uno de 5.000–20.000 USD: coherencia de identidad + ejecución de nivel mundial, no solo "verse bonito".

- [ ] 2B.1 `BrandDNAProfile` (modelo de datos): paleta de color real extraída (no inventada), tipografía actual y su "personalidad" (clásica/moderna/artesanal/corporativa), tono de voz inferido del copy existente, estilo fotográfico/ilustrativo, símbolos y elementos gráficos recurrentes, sector/industria, público objetivo inferido
- [ ] 2B.2 Extractor de paleta y tipografía desde CSS/HTML real del sitio (no aproximaciones) — se apoya en `website_intelligence`
- [ ] 2B.3 Extractor de identidad visual desde imágenes (logo, fotografía de producto/equipo, iconografía) cuando el cliente las provee o están en el sitio
- [ ] 2B.4 Motor de "qué es genuinamente de esta marca vs. qué es ruido/plantilla heredada" — alimenta directamente a `redesign_intelligence` (que ya decide qué conservar/eliminar) con este perfil como insumo obligatorio, no opcional
- [ ] 2B.5 Checklist de técnicas de diseño de nivel mundial a aplicar sobre esa base: jerarquía tipográfica real, sistema de espaciado consistente (grid/8pt), contraste y accesibilidad AA/AAA, dirección de arte fotográfica coherente, micro-interacciones con propósito, patrones editoriales/asimétricos en vez de plantillas de bloques genéricas — esto conecta con `design_resource_hub` y `design_execution_planner`, que ya existen
- [ ] 2B.6 Métrica interna de "elevación": comparar antes/después contra esos criterios para poder justificar el precio en la propuesta de valor (Fase 6)

**Dónde encaja:** `Website Intelligence` (inspecciona) → **`Brand DNA Extractor` (nuevo)** → `Redesign Intelligence` (decide preservando ADN real) → `Design Resource Hub` → `Design Execution Planner` → `Site Builder`. No es un skill aislado, es el insumo que le faltaba a `Redesign Intelligence` para no producir resultados genéricos.

### FASE 3 — Skill de Aprendizaje por Referencia (Design Reference Learner)
Para que el agente no genere "plantillas de IA genéricas":
- [ ] 3.1 Tool para clonar/inspeccionar repos open-source de referencia (patrones reales, no plantillas)
- [ ] 3.2 Extracción de patrones de diseño reales (layout, tipografía, componentes) de esos repos
- [ ] 3.3 Integrar esta fuente de conocimiento en `design_resource_hub` antes de decidir

### FASE 4 — Conectores externos (MCP / librerías)
- [ ] 4.1 Capa de conectores MCP (Higgsfield y otros que definas)
- [ ] 4.2 Registro de librerías/frameworks de diseño permitidos
- [ ] 4.3 Sandboxing y permisos por herramienta (hoy no existe ningún control de seguridad — ver Sección 11 del audit)

### FASE 5 — Análisis SEO explícito
- [ ] 5.1 Nuevo módulo o extensión de `website_intelligence`: metadatos, performance, estructura semántica, accesibilidad
- [ ] 5.2 Traducir hallazgos SEO en recomendaciones accionables dentro de `redesign_intelligence`

### FASE 6 — Propuesta de valor + Entrega
- [ ] 6.1 Generador de propuesta cliente-facing (antes/después visual, justificación, impacto SEO estimado)
- [ ] 6.2 Conector de envío: Email/Gmail
- [ ] 6.3 Conector de envío: Telegram
- [ ] 6.4 Plantilla de mensaje "diseñador junior" — tono profesional, no genérico/spam

### FASE 7 — Ciclo de autonomía real
- [ ] 7.1 Nodo de planificación (goal decomposition)
- [ ] 7.2 Nodo de evaluación (criterios de éxito/calidad)
- [ ] 7.3 Nodo de decisión (branching real basado en evaluación)
- [ ] 7.4 Memoria entre tareas (aprender de rediseños anteriores)

## 4. Principio de seguridad no negociable

Este agente va a: navegar la web, clonar repos externos, modificar código de terceros, y **enviar comunicaciones no solicitadas a desconocidos**. Antes de la Fase 6 (envío real), se requiere:
- Revisión humana obligatoria de cada propuesta antes de enviarse (al menos en V1)
- Rate limiting y opt-out claro en cualquier mensaje
- Cumplimiento de leyes anti-spam (CAN-SPAM, GDPR si aplica, políticas de Telegram)

No se implementará envío automático sin supervisión humana en el primer release.

## 5. Convención de trabajo

- Cada tarea completada = commit atómico + tests pasando + changelog en este archivo.
- Yo (Claude) preparo el código y los archivos; tú revisas y haces el push de los archivos que te indique.
- Nada se marca `[x]` hasta que los tests correspondientes pasen.
