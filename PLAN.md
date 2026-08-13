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
python -m harness.tests.test_agent_cycle
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

**El pipeline de diseño ya corre de punta a punta contra un proyecto real,
con `GovernanceGate` conectado como bloqueo obligatorio antes de `site_builder`
y artefactos reales para secciones, navegación, interacciones, accesibilidad,
performance y estilos. El siguiente bloqueador mayor es convertir los pasos
fijos del harness en un ciclo agente PLAN → EXECUTE → OBSERVE → EVALUATE → DECIDE.**

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
  - [x] `GovernanceGate` conectado como paso obligatorio antes de `site_builder`

## Fase 2 — Conectar el pipeline ✅ CERRADA — pipeline real funcionando

- [x] `DesignPipelineNode` creado — corre las 5 etapas en secuencia contra un
      `project_path` real (`harness/nodes/design_pipeline_node.py`)
- [x] Fixture de proyecto fijo y versionado en el repo:
      `harness/tests/fixtures/sample_project/` (package.json con React +
      Tailwind, componentes, página) — reemplaza los directorios ad hoc en
      `/tmp` que hacían las pruebas no reproducibles entre sesiones
- [x] Test de integración real: `harness/tests/test_design_pipeline_integration.py`
      — 5 tests, corre el pipeline completo (dry-run y build real) contra el
      fixture fijo, incluyendo una corrida doble consecutiva para atrapar
      no-determinismo. **5/5 pasan.**
- [x] **9 bugs de integración encontrados y arreglados** en esta fase (lista
      completa abajo) — todos verificados con el test de integración como
      guardia, no solo probados a mano una vez.
- [x] Pipeline completo verificado: corre 2 veces seguidas sobre el mismo
      proyecto, sin errores, escribiendo archivos reales cada vez
      (`src/styles/tokens.css` confirmado; más archivos una vez se
      implementen los métodos `_handle_*` que faltan, ver Fase 2B)
- [x] Fix de no-determinismo de `WebsiteInspector`: ahora excluye `.harness/`
      de sus recorridos, igual que ya excluía `node_modules`/`.git`/etc.

### Los 9 bugs encontrados en esta fase (todos arreglados, todos con test)

1. `redesign_intelligence` crasheaba si `website_intelligence` devolvía una
   sección como `None` en vez de omitirla. Fix: `_normalize_profile()`.
2. `site_builder/builder.py` no importaba `BuildError`/`ErrorType`/`ErrorSeverity`,
   el manejo de errores agregaba `dict`s donde se esperaban objetos.
3. `site_builder.execute_build()` recibía el objeto `DesignBuildPlan` en vez
   de un `dict` (su propia firma pide `Dict[str, Any]`).
4. `implementation_order` es una lista de `dict`s (`{"task": "Design tokens"}`),
   pero el despachador de `site_builder` comparaba `step == "dependencies"`
   contra strings — **ninguna rama se ejecutaba jamás, para ningún plan,
   nunca**, hasta este fix. El bug más crítico de los 9.
5. `RemoveEngine.analyze()` hacía `patterns.get("obsolete")` asumiendo dict;
   `patterns` es y siempre fue un `List[str]` de nombres de patrones.
   Reescrito para comparar contra una lista real de patrones obsoletos.
6. `SectionPlan.layout` se serializa como string (`LayoutType.value`);
   `section_builder` esperaba `layout.get("type")`. Adaptado en el nodo
   orquestador.
7. `SectionPlan.motion` es `List[str]`; `section_builder` esperaba
   `motion.get("enabled")`/`.get("initial")`/etc. Adaptado.
8. `responsive_behavior` viene hardcodeado en `planner.py` como
   `{"mobile": "stack"}` (string plano); `section_builder` esperaba
   `{"mobile": {"stack": True}}`. Adaptado — **nota**: esto también reveló
   que `responsive_planner.py` existe como módulo pero **no está conectado**
   a la generación real de secciones en `planner.py` (usa plantillas
   hardcodeadas de 2-3 secciones fijas, no genera dinámicamente). Pendiente
   real, ver Fase 2B.
9. `SectionPlan.components` es `List[str]` de nombres; `section_builder`
   esperaba una lista de dicts con clave `"name"`. Adaptado.
10. Bug de Python puro (no de contrato entre skills): en
    `section_builder.py`, un f-string generaba JSX con
    `({className}) => {{` usando llaves simples de Python en vez de escapadas
    (`{{className}}`), causando `NameError: name 'className' is not defined`
    porque Python intentaba evaluar `className` como variable propia en vez
    de emitirlo como texto literal de JSX.

**Dónde viven los fixes**: los bugs #1, #5 y #10 se arreglaron directamente
en el código fuente de los skills (`redesign_intelligence/engine.py`,
`site_builder/section_builder.py`) porque eran errores reales de ese código,
no diferencias de contrato. Los bugs #2, #3, #4, #6, #7, #8, #9 se resolvieron
en `DesignPipelineNode._adapt_build_plan_for_site_builder()`, como una capa
de adaptación en el punto de integración — deliberado, para no reescribir la
lógica interna de `design_execution_planner` ni de `site_builder` sin tests
propios que protejan esos cambios.

## Fase 2B — Lo que Fase 2 dejó pendiente

- [x] Implementados los 7 métodos `_handle_*` que estaban vacíos o eran no-op:
      `_handle_typography`, `_handle_layout`, `_handle_responsive`,
      `_handle_accessibility`, `_handle_performance`, `_handle_navigation`
      y `_handle_interactions`. Cada uno ahora escribe archivos reales
      (CSS de variables, checklists en Markdown, componente de navegación
      y contratos de navegación/interacciones) a partir de los datos que
      produce `design_execution_planner`. Verificado:
      `test_design_pipeline_integration.py`, 7/7 tests.
- [x] Bug encontrado y arreglado en el propio proceso: dos tareas del plan
      ("Hero section" y "Content sections") mapeaban ambas a la palabra
      clave `"sections"`, causando que `_handle_sections` corriera dos
      veces y duplicara cada componente. Deduplicado en el adaptador.
- [x] `design_execution_planner/planner.py`'s `_generate_sections()` ahora
      construye las 7 secciones que `home_page.sections` declara (antes solo
      3 de 7 existían realmente como `SectionPlan`: `product`,
      `testimonials`, `cta`, `footer` estaban referenciadas pero nunca
      creadas). Verificado: una corrida real ahora produce 14 archivos
      (antes: 10). Nota: siguen siendo secciones de plantilla fija, no
      generadas dinámicamente a partir de `redesign_strategy` — ese es un
      cambio de arquitectura más grande, no incluido aquí.
- [x] `_apply_resource_report()` implementado — ya no es un `pass` vacío.
      Mapea cada recurso seleccionado por `design_resource_hub`
      (`resources_selected`) a su paquete npm real (`tailwindcss`,
      `@radix-ui/react-slot`, `framer-motion`, `lucide-react`) y lo agrega a
      `plan.dependencies`. Recursos sin paquete npm real (shadcn/ui es
      código copiado, no un paquete; Google Fonts se carga por `<link>`, no
      npm) se omiten a propósito en vez de inventar un nombre de paquete
      incorrecto. Verificado con una corrida real: `dependencies` pasa de
      `[]` a `['tailwindcss', '@radix-ui/react-slot', 'framer-motion', 'lucide-react']`.
- [x] `navigation`/`interactions` agregados a `DesignBuildPlan.to_dict()` y
      generados por `planner.py`; `site_builder` ya consume ambos campos y
      escribe `src/components/Navigation.tsx`, `NAVIGATION_PLAN.md` e
      `INTERACTIONS_PLAN.md`.
- [ ] Fusionar `dynamic-sections-and-resource-report` a `main`
- [x] Crear la carpeta `projects/` como destino estándar de los sitios que
      el agente genere/modifique
- [ ] **Coordinar con el trabajo paralelo de Qwen** — su rama sigue sin
      aparecer en el remoto (verificado de nuevo hoy)




## Fase 3 — Que el agente piense de verdad (iniciada)

- [ ] Conectar `QwenAgentProvider` (`harness/agents/__init__.py`) a la API real
      — hoy `connect()`/`generate()` son placeholders, todo corre en
      `MockLLMProvider`. Instrucción ya redactada y entregada a Qwen dos veces,
      todavía no ejecutada.
- [x] Primer ciclo agente determinístico:
      `PLAN → EXECUTE → OBSERVE → EVALUATE → DECIDE`
      (`harness/agents/design_cycle.py`). Corre una planificación dry-run,
      observa etapas/gobernanza, evalúa si puede escribir y decide entre
      `blocked`, `ready_to_execute`, `complete` o `failed`. No requiere LLM ni
      credenciales externas todavía.
- [x] Definir las señales reales del `GovernanceGate`
      (`brand_alignment`, `accessibility`, `visual_craft`, `performance`,
      `seo_impact`, `originality`) como salidas medibles de cada skill, no
      números inventados. `DesignPipelineNode` ahora deriva señales
      determinísticas desde `profile_dict`, `redesign_result` y
      `DesignBuildPlan.to_dict()` con evidencia auditable por dimensión.
- [ ] `BaseDesignJudgmentEngine`: generalizar el patrón del Qwen Adapter para
      que cualquier skill de "juicio creativo" sea intercambiable entre
      proveedores de IA
- [x] Conectar `GovernanceGate` antes de `site_builder` en `DesignPipelineNode`
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
- [ ] Extender el ciclo PLAN → EXECUTE → OBSERVE → EVALUATE → DECIDE a
      autonomía multi-iteración/client-facing. La base determinística ya
      existe en Fase 3, pero todavía no prospecta, aprende de referencias
      externas ni decide nuevos objetivos por sí misma.
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
- **2026-08-09** — Implementada la metodología recomendada arriba: fixture
  fijo en `harness/tests/fixtures/sample_project/` + test de integración
  real (`test_design_pipeline_integration.py`, 5 tests). Usado como guía
  para encontrar y arreglar 5 bugs más (total 9 en Fase 2, ver lista
  completa en Fase 2 arriba): patterns list-vs-dict en `RemoveEngine`,
  `SectionPlan.layout`/`.motion`/`.responsive_behavior`/`.components`
  serializados en formas que `section_builder` no esperaba, y un `NameError`
  de Python puro por un f-string sin escapar (`{className}` vs
  `{{className}}`) en `section_builder.py`. **Resultado: 5/5 tests de
  integración pasan, pipeline corre 2 veces seguidas sin errores, 178 tests
  en total en el repo, todos en verde.** Fase 2 se marca cerrada. Fase 2B
  abierta con lo que quedó pendiente (7 métodos sin implementar en
  site_builder, secciones hardcodeadas en planner.py, resource_report nunca
  aplicado).
- **2026-08-09 — ALERTA DE COORDINACIÓN** — Mientras se hacía este trabajo,
  Qwen trabajaba en paralelo (fuera del prompt asignado) en su propia
  versión del orquestador: `design_pipeline_nodes.py` (varios nodos +
  `Graph` de bajo nivel, en vez de un solo `DesignPipelineNode`), y
  encontró independientemente el mismo bug de `typography=None`, arreglándolo
  con una normalización distinta **dentro de `RedesignIntelligenceEngine.analyze()`**
  (no en `redesign_intelligence_skill()` como se hizo aquí). También detectó
  el gap de `_apply_resource_report()` vacío (ya anotado en Fase 2B).
  **Verificado en este momento: esa rama todavía NO existe en el remoto**
  (`git branch -r` no la muestra) — el trabajo de Qwen sigue solo local a su
  sesión, sin push todavía. Antes de fusionar `pipeline-orchestrator-and-fixes`
  (esta rama, ya con 5/5 tests de integración pasando) a `main`, o antes de
  que Qwen haga push/PR de la suya: alguien tiene que decidir cuál
  orquestador es el definitivo. Fusionar ambos tal cual casi seguro duplica
  lógica de normalización de perfil y deja dos formas distintas de conectar
  el mismo pipeline compitiendo en `main`. **Acción recomendada**: correr
  `git branch -r` de nuevo antes de la próxima fusión para ver si ya apareció
  la rama de Qwen, y si aparece, compararla contra esta antes de fusionar
  cualquiera de las 2.
- **2026-08-09** — Fase 2B iniciada: implementados 5 de los 7 métodos
  `_handle_*` vacíos de `site_builder` (`typography`, `layout`,
  `responsive`, `accessibility`, `performance`), cada uno escribiendo
  archivos reales a partir de los datos ya calculados por
  `design_execution_planner`. Encontrado y arreglado un bug de duplicación
  (dos tareas del plan mapeaban a la misma palabra clave `"sections"`,
  corriendo el paso dos veces). Verificado: una corrida real ahora produce
  10 archivos (antes de Fase 2B: 1). `_handle_navigation`/`_handle_interactions`
  siguen vacíos porque `DesignBuildPlan` no tiene esos campos todavía — no
  es un bug de site_builder, es que `planner.py` nunca los genera. 178
  tests siguen en verde (5/5 de integración incluidos). Fusionado a main
  como PR #18.
- **2026-08-10** — Rama `dynamic-sections-and-resource-report`: completadas
  las 4 secciones (`product`, `testimonials`, `cta`, `footer`) que
  `home_page.sections` declaraba pero `_generate_sections()` nunca
  construía. Implementado `_apply_resource_report()` (antes `pass` vacío) —
  mapea recursos seleccionados por `design_resource_hub` a paquetes npm
  reales y los agrega a `plan.dependencies`. Verificado: 14 archivos por
  corrida (antes: 10), `dependencies` ahora tiene 4 paquetes reales (antes:
  vacío). 178 tests en verde. Rama de Qwen sigue sin aparecer en el remoto.
- **2026-08-13** — Auditoría local en Windows: corregidos runners no
  portables por salida Unicode (`run_all_tests.py` y
  `test_website_intelligence.py`), el runner base ahora marca grupos como
  FAIL si falla cualquier test interno, no como PASS fijo. Agregados
  `navigation` e `interactions` al contrato de `DesignBuildPlan`; `planner.py`
  ahora los genera y `site_builder` escribe artefactos reales para ambos
  pasos (`src/components/Navigation.tsx`, `NAVIGATION_PLAN.md`,
  `INTERACTIONS_PLAN.md`) en vez de no-op. Verificado:
  `python -m harness.tests.run_all_tests` (40/40),
  `python -m harness.tests.test_website_intelligence` (8/8) y batería
  documentada completa con salida 0; `test_design_pipeline_integration.py`
  ahora tiene 6/6 tests.
- **2026-08-13** — `GovernanceGate` conectado en `DesignPipelineNode` como
  etapa obligatoria antes de `site_builder`. Las señales
  `brand_alignment`, `accessibility`, `visual_craft`, `performance`,
  `seo_impact` y `originality` ahora se derivan de datos concretos del
  pipeline (`profile_dict`, `redesign_result`, `DesignBuildPlan.to_dict()`)
  con evidencia por dimensión. Si la puerta falla en build real, el nodo
  devuelve `status="blocked"` antes de que `site_builder` escriba archivos.
  Verificado: `python -m harness.tests.run_all_tests` (40/40),
  `python -m harness.tests.test_governance` (13/13) y
  `python -m harness.tests.test_design_pipeline_integration` (7/7).
- **2026-08-13** — Reemplazado `datetime.utcnow()` por timestamps UTC
  timezone-aware mediante `harness.core.time.utc_now_iso()`. Esto elimina
  `DeprecationWarning` en Python 3.13 sin cambiar el contrato externo de
  timestamps como strings ISO. Verificado con `-W error::DeprecationWarning`
  en `test_governance.py`, `test_runtime_fixes.py`, `test_memory.py` y
  `test_checkpoint_persistence.py`; batería documentada completa en verde.
- **2026-08-13** — Fase 3 iniciada con `DeterministicDesignAgent`
  (`harness/agents/design_cycle.py`): ciclo explícito
  `PLAN → EXECUTE → OBSERVE → EVALUATE → DECIDE` sobre `DesignPipelineNode`.
  El primer pase siempre es dry-run; si gobernanza o etapas fallan, decide
  `blocked` antes de escribir; si pasa sin `execute=True`, decide
  `ready_to_execute`; con `execute=True`, ejecuta build real y decide
  `complete`/`failed`. Verificado: `python -m harness.tests.test_agent_cycle`
  (3/3) y `python -m harness.tests.run_all_tests` (41/41).

---

## Para el próximo agente que lea esto

1. Corre los tests de la sección de arriba primero. Si algo que aquí dice
   `[x]` te falla, este documento está desactualizado — arréglalo y actualiza
   el Log, no asumas que el código está mal.
2. Fase 2/Fase 2B ya tienen el pipeline ejecutando build real con gobernanza
   previa a escritura. Fase 3 ya tiene un primer ciclo determinístico; el
   siguiente bloqueador es conectar decisión iterativa más rica y/o proveedor
   LLM real sin romper la ruta mock.
3. No fusiones ninguna rama sin correr su suite de tests aislada primero
   (`git worktree add /tmp/test_X origin/rama-x` es más seguro que hacer
   checkout directo, no ensucia tu working copy).
4. Si vas a tocar cualquier empalme entre dos skills, asume que puede haber
   un desajuste dict-vs-objeto hasta que lo pruebes — es el bug más repetido
   de este proyecto.
