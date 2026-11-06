# QA Automation Platform

Framework centralizado para implementar, ejecutar y gobernar automatización Web con Playwright a partir de artefactos funcionales y técnicos verificables.

El framework separa el razonamiento de los agentes de las operaciones determinísticas del Core y mantiene evidencia, conocimiento y trazabilidad dentro del proyecto.

---

## Objetivo

Recibir como entrada:

- Matriz de Pruebas.
- EF - Especificación Funcional.
- ET - Especificación Técnica.

Flujo principal:

    Matriz + EF + ET
           |
           v
    QA Orchestrator
           |
           v
    Playwright Engineer
           |
           v
    Automation Reviewer
           |
       FAIL / PASS
         |      |
         |      +----> LISTO
         |
         +----> Engineer -> Review

---

## Principios

### Evidencia antes que inferencia

Toda decisión relevante debe estar sustentada por una fuente verificable.

Fuentes válidas:

- Matriz de Pruebas.
- EF.
- ET.
- Código existente.
- Aplicación inspeccionada.
- Conocimiento verificable registrado por la plataforma.

Una interpretación no se convierte automáticamente en requisito confirmado.

### La Matriz contiene los casos

La Matriz es la fuente principal de los casos de prueba.

EF y ET aportan contexto funcional y técnico para comprender e implementar correctamente cada caso.

### Bloqueo parcial

Un GAP o CONFLICTO bloquea únicamente el caso afectado cuando sea posible.

### Quality Gate independiente

El Playwright Engineer no aprueba su propia implementación.

El Automation Reviewer realiza el review y el Core aplica gates determinísticos.

---

## Arquitectura

    QA AUTOMATION PLATFORM
    |
    +-- Agents
    |   +-- QA Orchestrator
    |   +-- Playwright Engineer
    |   +-- Automation Reviewer
    |
    +-- Skills
    |   +-- Artifact Analysis
    |   +-- QA Automation Workflow
    |   +-- Playwright Architecture
    |   +-- Playwright Implementation
    |   +-- Locator Strategy
    |   +-- Evidence Management
    |   +-- Playwright Quality Gate
    |
    +-- Deterministic Core
        +-- Artifact Engine
        +-- Knowledge Engine
        +-- Lifecycle
        +-- Intervention
        +-- Results
        +-- Quality Gate
        +-- Traceability
        +-- Evidence
        +-- Bootstrap

---

## Agentes

### QA Orchestrator

Responsable de gobernar el proceso.

- valida Matriz, EF y ET;
- consulta conocimiento vigente;
- registra conocimiento consultado, aplicado y descartado;
- cruza casos con evidencia funcional y técnica;
- detecta GAP y CONFLICTO;
- delega casos listos;
- coordina Engineer y Reviewer;
- mantiene trazabilidad;
- registra conocimiento reutilizable como PROVISIONAL.

No implementa Playwright y no aprueba código.

### Playwright Engineer

Responsable de construir y ejecutar la automatización.

- inspecciona el proyecto existente;
- reutiliza Pages, Components, Fixtures y Helpers;
- implementa tests;
- administra Test Data;
- utiliza locators verificables;
- utiliza waits determinísticos;
- ejecuta pruebas;
- captura evidencia;
- corrige findings del Reviewer.

No modifica el significado del caso para hacer pasar una prueba.

### Automation Reviewer

Quality Gate independiente.

Valida:

- Matriz / EF / ET vs implementación;
- cobertura;
- assertions;
- arquitectura;
- reutilización;
- locators;
- waits;
- datos;
- secretos y hardcodes;
- independencia;
- cleanup;
- paralelismo;
- flakiness;
- evidencia de ejecución.

Resultados: PASS o FAIL.

---

## Artifact Engine

Procesa Matriz XLSX, EF DOCX y ET DOCX.

Los originales no deben modificarse.

Cada artefacto normalizado conserva:

- archivo origen;
- SHA-256;
- extractor utilizado;
- versión de schema;
- contenido;
- referencias de procedencia.

Ejemplos de procedencia:

    matriz.xlsx#Casos!R2
    EF.docx#paragraph-4
    ET.docx#table-2-row-3

Esto permite mantener trazabilidad hasta la fuente original.

---

## Knowledge Engine

Memoria verificable almacenada dentro del repositorio.

Tipos:

    REGLA_DOCUMENTADA
    COMPORTAMIENTO_OBSERVADO
    SOLUCION_TECNICA_COMPROBADA
    DATO_DE_PRUEBA
    INTERVENCION_MANUAL
    DUDA_PENDIENTE

Estados:

    PROVISIONAL
    VERIFICADO
    INVALIDADO
    REEMPLAZADO

Una entrada nueva es PROVISIONAL por defecto.

VERIFICADO requiere una acción explícita.

Invalidar o reemplazar conocimiento conserva el historial.

El Knowledge Engine permite:

    add
    read
    search
    verify
    invalidate
    replace
    register_query
    read_query

Las consultas registran conocimiento consultado, aplicado, descartado y el motivo del descarte.

---

## Lifecycle

Estados actuales:

    DISCOVERED
        |
        v
    ANALYZED
        |
        v
    READY
        |
        v
    IMPLEMENTING
        |
        v
    EXECUTED
        |
        v
    IN_REVIEW
       / \
    FAIL PASS

También existe BLOCKED.

Las transiciones son validadas por el Core.

---

## Intervention

Permite registrar intervención humana cuando la automatización no puede continuar de forma confiable.

Registra caso, intento, hallazgo, necesidad, acción, observación, evidencia y timestamp.

La plataforma solicita intervención en lugar de fabricar un resultado.

---

## Results

Cada ejecución registra:

- run ID;
- case ID;
- intento;
- estado;
- duración;
- ambiente;
- browser;
- evidencia;
- error;
- timestamp.

Estados de ejecución:

    PASS
    FAIL
    BLOCKED
    ERROR
    TIMEOUT

---

## Canonical Paths

Las rutas persistentes son definidas por el Core.

Los agentes y demás componentes no deben construir manualmente rutas para resultados, evidencia o trazabilidad.

Funciones canónicas actuales:

    result_path()
    result_ref()
    evidence_attempt_dir()
    evidence_manifest_path()
    evidence_manifest_ref()
    traceability_case_path()

Esto evita divergencias entre Results, Evidence, Traceability, Integrity y Quality Gate.

---

## Execution Integrity

El Core correlaciona de forma determinística:

    Result
       +
    Evidence
       +
    Traceability
       =
    Execution Integrity

La identidad debe coincidir en:

    run_id
    case_id
    attempt

Una evidencia válida perteneciente a otra ejecución no puede utilizarse para aprobar un caso.

El Quality Gate verificado obtiene el estado real desde los artefactos persistidos y no depende únicamente de afirmaciones de un agente.

---

## Quality Gate

Un caso no queda listo solamente porque el Reviewer indique PASS.

El gate mínimo requiere:

    Execution = PASS
            +
    Reviewer = PASS
            +
    Traceability = COMPLETE
            +
    Evidence = COMPLETE
            +
    0 Critical Findings
            +
    0 High Findings
            =
           PASS

---

## Proyecto consumidor

Estructura objetivo:

    mi-proyecto/
    |
    +-- documents/
    |   +-- original/
    |   |   +-- matriz.xlsx
    |   |   +-- EF.docx
    |   |   +-- ET.docx
    |   +-- normalized/
    |       +-- matrix.normalized.json
    |       +-- ef.normalized.json
    |       +-- et.normalized.json
    |
    +-- tests/
    +-- pages/
    +-- components/
    +-- fixtures/
    +-- data/
    +-- utils/
    +-- knowledge/
    |   +-- entries/
    |   +-- queries/
    +-- traceability/
    +-- evidence/
    +-- results/
    +-- .env.example
    +-- playwright.config.ts
    +-- package.json
    +-- README.md

---

## Requisitos

Recomendado en macOS:

- Python 3.12+.
- Node.js LTS.
- Git.
- VS Code.

Baseline Python actual:

    >=3.12,<3.15

---

## Obtener el framework

### Opción 1 - ZIP

Descargar qa-automation-platform.zip.

Ejemplo:

    cd "/Users/<usuario>/proyectos_automation"
    unzip "$HOME/Downloads/qa-automation-platform.zip" -d "/Users/<usuario>/proyectos_automation"
    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"

### Opción 2 - Git

Cuando exista un repositorio remoto oficial:

    cd "/Users/<usuario>/proyectos_automation"
    git clone "<URL_REPOSITORIO>" qa-automation-platform
    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"

No reemplazar <URL_REPOSITORIO> hasta disponer de la URL oficial.

---

## Instalación

### 1. Entrar al framework

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"

### 2. Validar Python

    python3.12 --version

### 3. Crear entorno virtual

    python3.12 -m venv .venv

### 4. Instalar

    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -e ".[dev]"

### 5. Validar runtime

    .venv/bin/python --version

---

## Validar instalación

Suite completa:

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"
    .venv/bin/python -m pytest -v

Artifact Engine:

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"
    .venv/bin/python -m pytest tests/unit/test_artifacts.py -v -rs

Una instalación válida debe tener:

    0 failed
    0 errors
    0 skipped en tests críticos

---

## Desarrollo

Compilar Core:

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"
    .venv/bin/python -m compileall -q core tests

Ejecutar tests:

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"
    .venv/bin/python -m pytest -v

Estado Git:

    cd "/Users/<usuario>/proyectos_automation/qa-automation-platform"
    git status --short

---

## Gobierno de evidencia

Clasificaciones:

    CONFIRMADO
    POR_VALIDAR
    GAP
    CONFLICTO

POR_VALIDAR nunca se convierte automáticamente en requisito confirmado.

Un conflicto entre fuentes no se resuelve arbitrariamente.

---

## Seguridad

No almacenar passwords, tokens, API keys, secretos ni credenciales.

Utilizar variables de entorno y secret stores.

La memoria persistente nunca ejecuta contenido almacenado como código.

---

## Estándares Playwright

No utilizar waitForTimeout() como solución por defecto.

Prioridad de locators:

    1. data-testid / data-test
    2. role + accessible name
    3. label
    4. texto estable
    5. CSS/XPath solamente cuando esté justificado

Un locator debe ser verificable.

No inventar selectores.

---

## Inspiración Auto-LDS

Auto-LDS se utiliza como referencia funcional para identificar capacidades útiles de una plataforma autónoma de QA.

Se adoptan conceptualmente:

- memoria central verificable;
- registro de consultas;
- bootstrap de proyectos;
- extracción de Matriz;
- extracción de documentos;
- resultados;
- evidencia;
- intervención humana;
- manejo explícito de estados de ejecución.

No se copian como estándar general:

- decisiones específicas del dominio LDS;
- scripts CP autónomos;
- credenciales embebidas;
- waits fijos;
- acoplamiento a una herramienta de IA específica.

QA Automation Platform debe permanecer independiente de Claude, GitHub Copilot, ChatGPT y de un dominio funcional específico.

---

## Política de confiabilidad de agentes

Los agentes operan bajo contratos comunes de evidencia y toma de decisiones.

Clasificaciones:

    CONFIRMADO
    POR_VALIDAR
    GAP
    CONFLICTO

Principios:

- no completar información faltante mediante suposición;
- conservar referencias de procedencia;
- no convertir conocimiento PROVISIONAL en requisito confirmado;
- no inventar requisitos, datos, locators, endpoints o resultados;
- no declarar ejecución o evidencia sin respaldo persistido;
- respetar Traceability, Evidence, Execution Integrity y Quality Gate;
- mantener segregación entre Orchestrator, Engineer y Reviewer;
- bloquear únicamente el alcance afectado cuando sea posible.

Una afirmación de un agente no puede sobreescribir un resultado determinístico del Core.

---

## Estado actual

Implementado:

- [x] Foundation Core.
- [x] Lifecycle.
- [x] Intervention.
- [x] Results.
- [x] Deterministic Quality Gate.
- [x] Knowledge Engine.
- [x] Artifact Engine XLSX.
- [x] Artifact Engine DOCX.
- [x] Source SHA-256.
- [x] Source provenance.
- [x] Unit tests.
- [x] Execution Integrity.
- [x] Canonical Paths.

Próximas capas:

- [x] Traceability Engine.
- [x] Evidence Engine.
- [x] Bootstrap de proyectos.
- [ ] Case Mapping Matriz -> EF -> ET.
- [x] Agent Contracts y agentes endurecidos.
- [ ] Template Playwright endurecido.
- [ ] CLI.
- [ ] CI Quality Gates.

---

## Roadmap técnico

    Baseline
       |
       v
    Foundation v0.2
       |
       v
    Knowledge Engine v0.2
       |
       v
    Artifact Engine v0.2
       |
       v
    Traceability Engine
       |
       v
    Evidence Engine
       |
       v
    Bootstrap
       |
       v
    Agent Integration

Cada capa debe compilar, tener tests, mantener compatibilidad con las capas anteriores y pasar la suite completa antes de continuar.
