# QA Automation Platform

Framework centralizado y agnostico de proveedor de IA para convertir una Matriz de Pruebas + EF + ET en automatizacion Web Playwright trazable, revisada y reutilizable.

## Objetivo

Separar tres responsabilidades: gobernar el trabajo, implementar la automatizacion y revisar su calidad. El conocimiento comun vive en el framework; cada proyecto conserva solo sus artefactos, codigo, evidencia y conocimiento local.

## Arquitectura

```text
MATRIZ + EF + ET
       |
       v
+-------------------+
|  QA ORCHESTRATOR  |
+---------+---------+
          |
          | caso listo
          v
+---------------------+       FAIL
| PLAYWRIGHT ENGINEER |<------------------+
+----------+----------+                   |
           |                              |
           v                              |
+---------------------+                   |
| AUTOMATION REVIEWER |-------------------+
+----------+----------+
           |
          PASS
           v
        LISTO
```

## Agentes

- `qa-orchestrator`: analiza Matriz/EF/ET, consulta conocimiento, gestiona gaps/conflictos y coordina el flujo. No implementa Playwright.
- `playwright-engineer`: crea/reutiliza arquitectura, implementa casos, ejecuta pruebas y corrige findings.
- `automation-reviewer`: quality gate independiente. Contrasta artefactos vs codigo y devuelve PASS/FAIL.

## Principios

1. Evidencia antes que inferencia.
2. La Matriz define los casos; EF y ET aportan contexto funcional y tecnico.
3. Un gap critico bloquea solo el caso afectado.
4. Ningun agente se autoaprueba.
5. Conocimiento central y conocimiento de proyecto se mantienen separados.
6. No almacenar secretos en codigo, memoria ni evidencia.
7. Selectores y comportamiento de UI deben provenir de evidencia inspeccionable.
8. El framework debe poder ejecutarse con Claude, GitHub Copilot u otro runtime de agentes.

## Estructura

```text
qa-automation-platform/
├── agents/                 # definiciones de agentes
├── skills/                 # capacidades reutilizables
├── core/
│   ├── artifacts/          # normalizacion Matriz/EF/ET
│   ├── knowledge/          # memoria verificable
│   ├── traceability/       # Matriz -> EF/ET -> test -> evidencia
│   ├── evidence/           # resultados y evidencias
│   └── bootstrap/          # creacion de proyectos consumidores
├── templates/playwright/   # baseline de proyecto Web
└── docs/
```

## Flujo operativo

1. Ingestar Matriz, EF y ET sin alterar los originales.
2. Normalizar los artefactos a una representacion consultable.
3. Consultar conocimiento central y conocimiento local vigente.
4. Validar cada caso: CONFIRMADO, POR_VALIDAR, GAP o CONFLICTO.
5. Delegar solo casos implementables al Playwright Engineer.
6. Implementar/reutilizar pages, components, fixtures, data y helpers.
7. Ejecutar y guardar evidencia estructurada.
8. Automation Reviewer revisa trazabilidad, cobertura y calidad tecnica.
9. FAIL vuelve al Engineer con findings; PASS cierra el caso.
10. Registrar conocimiento reutilizable como PROVISIONAL; la verificacion es explicita.

## Proyecto consumidor

```text
mi-proyecto/
├── documents/
│   ├── matriz.xlsx
│   ├── EF.docx
│   └── ET.docx
├── tests/
├── pages/
├── components/
├── fixtures/
├── data/
├── evidence/
├── results/
├── knowledge/
└── playwright.config.ts
```

## Gobierno de evidencia

Fuentes validas: Matriz, EF, ET, codigo existente, aplicacion inspeccionada y conocimiento verificable. Una interpretacion no se convierte en requisito confirmado. Los conflictos documentales no se resuelven arbitrariamente.

Estados de conocimiento recomendados: `PROVISIONAL`, `VERIFICADO`, `INVALIDADO`, `REEMPLAZADO`.

Tipos recomendados: `REGLA_DOCUMENTADA`, `COMPORTAMIENTO_OBSERVADO`, `SOLUCION_TECNICA_COMPROBADA`, `DATO_DE_PRUEBA`, `INTERVENCION_MANUAL`, `DUDA_PENDIENTE`.

## Quality Gate minimo

Un caso solo queda LISTO si: implementacion ejecutada, trazabilidad completa, sin secretos/hardcodes indebidos, locators justificables, waits deterministas, assertions alineadas al caso y Reviewer = PASS.

## Inspiracion Auto-LDS

Se reutilizan conceptualmente: memoria central verificable, registro de consultas, bootstrap, resultados/evidencia e intervencion humana. No se copian decisiones especificas de LDS, scripts CP autonomos, credenciales embebidas ni waits fijos como estandar.
