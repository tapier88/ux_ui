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

## Fase 2 — Conectar el pipeline (EN PROGRESO — bloqueador actual)

- [x] `DesignPipelineNode` creado — corre las 5 etapas en secuencia contra un
      `project_path` real (`harness/nodes/design_pipeline_node.py`, rama
      `pipeline-orchestrator-and-fixes`, sin fusionar todavía)
- [x] Bug encontrado y arreglado: `redesign_intelligence` crasheaba cuando
      `website_intelligence` devuelve una sección como `None` en vez de omitirla
      (`profile.get("typography", {})` no aplica el default si el valor
      *existe* y es `None`). Fix: `_normalize_profile()` en `engine.py`.
- [x] Bug encontrado y arreglado: `site_builder/builder.py` nunca importaba
      `BuildError`/`ErrorType`/`ErrorSeverity`, así que el bloque `except` que
      reporta fallos de build agregaba `dict`s planos a `report.errors`, y
      `BuildReport.to_dict()` crasheaba esperando objetos con `.to_dict()`.
- [ ] **BLOQUEADOR ACTUAL**: con los 2 fixes de arriba, el pipeline ya
      "completa" y reporta el error real de fondo:
      `'DesignBuildPlan' object has no attribute 'get'`
      → `site_builder` espera `design_build_plan` como `dict`
        (`data.get("design_build_plan")` en `site_builder/__init__.py`,
        función `site_builder_func`), pero `design_execution_planner`
        devuelve un objeto `DesignBuildPlan` (no un dict).
      → **Cómo reproducir**: correr el bloque de Python de la sección
        "Cómo verificar" de más abajo.
      → **Fix sugerido** (no aplicado todavía): en `DesignPipelineNode`, pasar
        `build_plan.to_dict()` a `SiteBuilder.execute_build()`, o cambiar
        `execute_build()` para aceptar el objeto directamente — decidir cuál
        de los dos es el contrato correcto y aplicarlo consistentemente,
        porque probablemente el mismo patrón dict-vs-objeto se repite en los
        otros 3 empalmes entre skills (no auditados todavía uno por uno).
- [ ] Auditar los otros 3 empalmes del pipeline buscando el mismo patrón
      (website_intelligence→redesign_intelligence ya se arregló;
      redesign_intelligence→design_resource_hub,
      design_resource_hub→design_execution_planner, y
      design_execution_planner→site_builder faltan por revisar formalmente)
- [ ] Correr el pipeline completo contra un proyecto real (no el fixture
      mínimo de `/tmp/sample_project`) y verificar que produce cambios de
      código válidos
- [ ] Crear la carpeta `projects/` (no existe todavía) como destino estándar
      de los sitios que el agente genere/modifique
- [ ] Fusionar la rama `pipeline-orchestrator-and-fixes` a `main` una vez
      resuelto el bloqueador de arriba

**Cómo verificar/reproducir el bloqueador actual:**
```python
import sys; sys.path.insert(0, '.')
from harness.nodes.design_pipeline_node import DesignPipelineNode
from harness.core.state import TaskState

state = TaskState(task_id='test-pipeline')
state.inputs = {'project_path': '/tmp/sample_project', 'url': 'https://example.com', 'dry_run': False}
result = DesignPipelineNode().execute(state)
print(result['status'], result.get('report', {}).get('errors'))
```
(El fixture `/tmp/sample_project` es un directorio temporal, no está en el
repo — créalo con un `package.json` mínimo con React + Tailwind y una carpeta
`components/` con 1-2 archivos `.tsx` antes de correr esto, o usa un proyecto
real.)

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
  5 etapas del pipeline en secuencia. Encontrados y arreglados 2 bugs de
  integración (`typography=None`, `BuildError` no importado). Bloqueador
  actual identificado y documentado: `DesignBuildPlan` object vs dict en el
  empalme `design_execution_planner` → `site_builder`. Rama:
  `pipeline-orchestrator-and-fixes`, sin fusionar — pendiente resolver el
  bloqueador antes de fusionar.

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
