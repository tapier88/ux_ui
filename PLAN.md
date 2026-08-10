# PLAN.md — Plan de trabajo vivo

**Este archivo es la fuente de verdad del estado del proyecto.** Antes de empezar
cualquier tarea nueva (humano o agente), léelo completo. Al terminar una tarea,
marca su checkbox `[x]` y agrega una línea en el Log con fecha, qué se hizo, qué
comando lo verifica, y qué PR/commit lo contiene. No borres entradas viejas del
log — es el historial de decisiones.

**Cómo verificar el estado real del código en cualquier momento** (no confíes
solo en este documento, corre esto):
```bash
python -m harness.tests.run_all_tests          # suite núcleo del harness
python -m harness.tests.test_website_intelligence
python -m harness.tests.test_redesign_intelligence
python -m harness.tests.test_git_persistence
python -m harness.tests.test_color_intelligence
python -m harness.tests.test_governance
python -m harness.tests.test_runtime_fixes
python -m harness.tests.test_memory
python -m harness.tests.test_checkpoint_persistence
```
Si alguno falla, este documento está desactualizado en ese punto — confía en el
test, actualiza el documento, no al revés.

---

## Visión (heredada de ROADMAP.md, sin cambios)

Un agente 100% autónomo que ejecuta el ciclo completo de un diseñador junior
freelance:

```
PROSPECTAR → INSPECCIONAR → APRENDER → DECIDIR → CONSTRUIR → EMPAQUETAR → ENVIAR
```

---

## Dónde estamos ahora mismo (resumen de una línea)

**Las 5 etapas del pipeline de diseño ya están conectadas en un solo nodo
ejecutable (`DesignPipelineNode`) y corren de punta a punta contra un proyecto
real, pero el build final todavía falla por un desajuste de tipos entre
`design_execution_planner` y `site_builder`. Ese es el bloqueador #1.**

---

## Fase 0 — Infraestructura base

- [x] Motor de grafos, estado, eventos, checkpoints — 39/39 tests
- [x] Git Persistence (commit/sync/publish/verify) — 17/17 tests — `harness/core/git/`
- [x] `GitPersistenceNode` conecta Git Persistence al grafo — antes no lo llamaba nadie
- [x] Fix causa raíz de conflictos de PR: sync/rebase contra main antes de publicar (PR #11)
- [x] Fix causa raíz de conflictos binarios: `.pyc`/`__pycache__` sacados del control de versiones (PR #12)
- [x] Memoria persistente + checkpoints en disco — 15 tests (`test_memory.py` + `test_checkpoint_persistence.py`) — PR #17
- [x] Fixes críticos de runtime (timeout, cancelación, bug de status en fallos, condicionales) — `test_runtime_fixes.py`, 9 tests — PR #17

## Fase 1 — Los 5 skills del pipeline de diseño

- [x] `website_intelligence` — inspecciona un proyecto/sitio existente — 8/8 tests (arreglé 1 fixture faltante)
- [x] `redesign_intelligence` — decide qué conservar/eliminar/mejorar — 45/45 tests
  - [x] Motor de color reemplazado por uno real (HSL, WCAG, armonías) — `color_intelligence.py`, 27 tests — PR #17
- [x] `design_resource_hub` — cataloga y selecciona recursos de diseño — sin tests propios todavía
- [x] `design_execution_planner` — convierte decisiones en plan técnico — sin tests propios todavía (**pendiente, ver Fase 2**)
- [x] `site_builder` — ejecuta el plan y modifica código real, con rollback — sin tests propios todavía
- [x] Gobernanza transversal: `GovernanceGate` + `ElevationScorer` — 13 tests — `harness/core/governance/` — PR #17
  - [ ] **Conectar `GovernanceGate` como paso obligatorio antes de `site_builder`** — existe pero nadie lo llama todavía

## Fase 2 — Conectar el pipeline (EN PROGRESO — sistémico, no un bug puntual)

- [x] `DesignPipelineNode` creado — corre las 5 etapas en secuencia contra un
      `project_path` real (`harness/nodes/design_pipeline_node.py`, rama
      `pipeline-orchestrator-and-fixes`, sin fusionar todavía)
- [x] Bug #1 arreglado: `redesign_intelligence` crasheaba cuando
      `website_intelligence` devuelve una sección como `None` en vez de omitirla.
      Fix: `_normalize_profile()` en `redesign_intelligence/engine.py`.
- [x] Bug #2 arreglado: `site_builder/builder.py` nunca importaba
      `BuildError`/`ErrorType`/`ErrorSeverity`, el `except` que reporta fallos
      agregaba `dict`s planos donde se esperaban objetos con `.to_dict()`.
- [x] Bug #3 arreglado (adaptador en `DesignPipelineNode`, no en los skills):
      `site_builder.execute_build()` espera `design_build_plan` como `dict`
      (tipado explícito en su firma), pero se le pasaba el objeto
      `DesignBuildPlan` crudo. Además las claves no coinciden:
      `design_execution_planner` emite `typography_plan`, `layout_plan`,
      `performance_plan`, `accessibility_plan`; `site_builder` lee
      `typography`, `layout`, `performance`, `accessibility` (sin sufijo).
      → `_adapt_build_plan_for_site_builder()` traduce ambas cosas sin tocar
      el código interno de ninguno de los 2 skills.
- [x] Bug #4 arreglado (mismo adaptador): `implementation_order` es una lista
      de **dicts** (`{"task": "Design tokens", ...}`), pero el despachador de
      `site_builder` (`_execute_step`) hace `if step == "dependencies":`
      comparando directo contra strings — un dict nunca es igual a un string,
      así que **ninguna rama se ejecutaba jamás, para ningún build, con
      cualquier plan que se le pasara** (bug crítico, silencioso, probablemente
      presente desde que se escribió `site_builder`). Fix: mapeo por
      coincidencia de palabras clave del texto libre de `task` hacia las 14
      palabras clave exactas que espera el despachador.
- [x] Con los 4 fixes de arriba, el pipeline **por primera vez escribe un
      archivo real en disco** (`src/styles/tokens.css`) en una corrida.
- [ ] **HALLAZGO NUEVO, NO ARREGLADO — bug #5**: dentro de
      `redesign_intelligence/engine.py`, `RemoveEngine.analyze()` hace
      `patterns.get("obsolete")` asumiendo que `patterns` es un `dict`, pero en
      al menos una corrida real llegó como `list` → mismo patrón de bug que
      #1, en un lugar distinto del mismo archivo. Probablemente hay más
      instancias de este patrón sin descubrir todavía en los otros 12 motores
      de `redesign_intelligence/engine.py` y en los 3 empalmes de skills sin
      auditar (ver abajo).
- [ ] **HALLAZGO NUEVO, MÁS IMPORTANTE — `site_builder` tiene 7 de 13 métodos
      `_handle_*` sin implementar** (`typography`, `layout`, `navigation`,
      `interactions`, `responsive`, `accessibility`, `performance` son
      literalmente `if x: pass`). Solo `dependencies`, `tokens`,
      `global_styles`, `sections`, `components`, `assets` hacen trabajo real.
      Aunque se resuelvan todos los bugs de contrato, **la mayoría del
      trabajo de diseño calculado nunca se escribe a código** hasta que
      alguien implemente esos 7 métodos.
- [ ] **HALLAZGO NUEVO — `WebsiteInspector` no es determinista sobre el mismo
      directorio entre corridas**: cada build dejó `.harness/checkpoints/` y
      `src/` en el proyecto, y la siguiente inspección los detecta como parte
      del proyecto a analizar, cambiando la forma del perfil resultante y
      disparando ramas de código distintas (así apareció el bug #5, que no
      salió en la corrida anterior con el mismo fixture). Esto significa que
      **correr el pipeline dos veces seguidas sobre el mismo proyecto puede
      dar resultados distintos** — hay que decidir si el inspector debe
      ignorar sus propios artefactos (`.harness/`, quizás `src/` generado) o
      si el diseño correcto es inspeccionar un snapshot congelado del "antes".
- [ ] Auditar sistemáticamente (no ad hoc) los 4 empalmes entre skills +
      los ~13 motores internos de `redesign_intelligence` en busca del mismo
      patrón `.get()`/comparación de tipo — ver "Metodología recomendada"
      abajo en vez de seguir reproduciendo bugs uno por uno a mano
- [ ] Implementar los 7 métodos `_handle_*` vacíos de `site_builder`
- [ ] Resolver la no-determinismo de `WebsiteInspector`
- [ ] Correr el pipeline completo contra un proyecto real y verificar que
      produce cambios de código válidos y **repetibles**
- [ ] Crear la carpeta `projects/` (no existe todavía) como destino estándar
- [ ] Fusionar `pipeline-orchestrator-and-fixes` a `main` una vez el pipeline
      sea confiable, no solo "no crashea"

### Metodología recomendada para lo que sigue (en vez de seguir a mano)

El patrón que se repite (5 veces ya) es: un skill produce una forma de dato
(`None` en vez de `{}`, `dict` en vez de `str`, sufijo `_plan` en vez de sin
sufijo, objeto en vez de dict) y el siguiente skill asume otra forma, sin que
ningún test lo hubiera detectado porque cada skill solo se probó aislado con
fixtures hechos a mano que "adivinaban bien" la forma esperada.

**Recomendación para la siguiente sesión/agente**: en vez de seguir
reproduciendo bugs manualmente uno por uno,
1. Crear un **fixture de proyecto fijo y versionado** en el repo (ej.
   `harness/tests/fixtures/sample_project/`), no en `/tmp`, para que las
   corridas sean reproducibles entre sesiones y agentes.
2. Escribir **un test de integración real** en
   `harness/tests/test_design_pipeline_integration.py` que corra
   `DesignPipelineNode` contra ese fixture fijo, con `dry_run=False`, y
   aserciones concretas (qué archivos debe crear, qué debe contener
   `report.errors` — debe ser `[]`).
3. Correrlo, dejar que falle, arreglar el primer bug que aparezca, volver a
   correr — y dejar el test en el repo así queda como guardia de regresión
   permanente, en vez de que cada bug se descubra y arregle una sola vez de
   forma manual sin quedar protegido contra que vuelva a pasar.
4. Repetir hasta que el test pase con `report.errors == []` **y** archivos
   reales creados, corriendo dos veces seguidas con el mismo resultado
   (ataca directamente el hallazgo de no-determinismo).



## Fase 3 — Que el agente piense de verdad (no iniciada)

- [ ] Conectar `QwenAgentProvider` (`harness/agents/__init__.py`) a la API real
      — hoy `connect()`/`generate()` son placeholders, todo corre en
      `MockLLMProvider`. Instrucción ya redactada y entregada a Qwen dos veces,
      todavía no ejecutada.
- [ ] Definir las señales reales del `GovernanceGate`
      (`brand_alignment`, `accessibility`, `visual_craft`, `performance`,
      `seo_impact`, `originality`) como salidas medibles de cada skill, no
      números inventados — depende de que los skills expongan métricas
      concretas (ratios de contraste reales ya existen en
      `color_intelligence.py`; Core Web Vitals reales, no)
- [ ] `BaseDesignJudgmentEngine`: generalizar el patrón del Qwen Adapter para
      que cualquier skill de "juicio creativo" sea intercambiable entre
      proveedores de IA
- [ ] Conectar `GovernanceGate` antes de `site_builder` en `DesignPipelineNode`
      (ver Fase 1, ya marcado ahí también)

## Fase 4 — La visión completa (no iniciada)

- [ ] Prospección: buscar sitios candidatos con diseño anticuado
- [ ] Análisis SEO explícito (hoy solo hay análisis de diseño/UX)
- [ ] Aprendizaje por referencia externa: consultar repos/diseños reales antes
      de decidir (evita el "look genérico de IA")
- [ ] Conectores MCP (Higgsfield y similares) y librerías externas
- [ ] Generación de la propuesta de valor cliente-facing (antes/después,
      justificación, impacto SEO)
- [ ] Envío por Email/Gmail/Telegram
- [ ] Ciclo real de autonomía PLAN → EXECUTE → OBSERVE → EVALUATE → DECIDE
      (hoy el harness es un ejecutor de pasos fijos, no un agente que decide)
- [ ] Actualizar README/ARCHITECTURE.md (describen solo la V0.1 base, ya
      desactualizados frente a lo que existe hoy)

---

## Decisiones de diseño tomadas (para que no se repitan discusiones)

- **Nunca usar `git push --force`, siempre `--force-with-lease`** — ver
  `harness/core/git/publication.py`
- **`.pyc`/`__pycache__` nunca se versionan** — causaron conflictos binarios en
  cadena en 7 de 8 PRs antiguos. Si reaparecen tracked, es un regreso del bug,
  no un caso nuevo.
- **Ante 2 ramas que implementan lo mismo, gana la que tenga tests reales y
  pasen** — no el tamaño del archivo. Precedente: `redesign_intelligence`
  6ebfe (45 tests) ganó sobre 2ebbf (tests rotos, ni corrían).
- **Cuando un skill recibe el output de otro, verificar si espera `dict` u
  objeto antes de asumir** — es el bug más repetido del proyecto hasta ahora
  (2 casos confirmados en Fase 2).

## Log

- **2026-08-09** — Corregida causa raíz de conflictos de PR (sync antes de
  publicar) + creado `GitPersistenceNode`. PR #11. Verificado: 17/17 tests
  git_persistence.
- **2026-08-09** — Eliminados `.pyc` versionados, causa de conflictos binarios
  en cadena. PR #12. Verificado: 39/39 tests núcleo.
- **2026-08-09** — Auditoría de las 5 ramas de tareas pendientes: 3 fusionadas
  (website_intelligence, redesign_intelligence v6ebfe, design_execution_planner),
  2 cerradas por ser versiones inferiores con tests rotos o inexistentes
  (PRs #13, #14, #15 fusionados; #7, #4 cerrados). Verificado: 8/8 + 45/45
  tests de los skills fusionados.
- **2026-08-09** — Qwen entregó (sin que fuera la tarea asignada) la rama
  `feature/fase0-runtime-fixes-and-memory`: Governance Gate, Elevation Scorer,
  motor de color real, memoria persistente, checkpoints, fixes de runtime.
  103 tests nuevos, todos pasando. Fusionada a main como PR #17.
- **2026-08-09** — Creado `DesignPipelineNode`, primer intento de correr las
  5 etapas del pipeline en secuencia. Encontrados y arreglados 4 bugs de
  integración en cadena (typography=None, BuildError no importado, objeto vs
  dict + claves con sufijo `_plan`, implementation_order como lista de dicts
  contra comparación de strings). Primera escritura real de archivo lograda
  (`src/styles/tokens.css`). Encontrado un 5to bug (`patterns` list vs dict
  en `RemoveEngine`) y un hallazgo mayor: 7 de 13 métodos `_handle_*` de
  `site_builder` son placeholders sin implementar, y `WebsiteInspector` no es
  determinista entre corridas sobre el mismo directorio. Se detiene el
  arreglo manual bug-por-bug aquí y se documenta metodología recomendada
  (fixture fijo + test de integración real) para la siguiente sesión. Rama:
  `pipeline-orchestrator-and-fixes`, sin fusionar.

---

## Para el próximo agente que lea esto

1. Corre los tests de la sección de arriba primero. Si algo que aquí dice
   `[x]` te falla, este documento está desactualizado — arréglalo y actualiza
   el Log, no asumas que el código está mal.
2. El bloqueador activo ahora mismo está en **Fase 2**. Es la tarea de mayor
   prioridad — todo lo de Fase 3 y 4 depende de que el pipeline complete un
   build real primero.
3. No fusiones ninguna rama sin correr su suite de tests aislada primero
   (`git worktree add /tmp/test_X origin/rama-x` es más seguro que hacer
   checkout directo, no ensucia tu working copy).
4. Si vas a tocar cualquier empalme entre dos skills, asume que puede haber
   un desajuste dict-vs-objeto hasta que lo pruebes — es el bug más repetido
   de este proyecto.
