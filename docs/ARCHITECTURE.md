# Arquitectura

## Capas

### Agent Layer
Coordina decisiones. No concentra reglas tecnicas reutilizables.

### Skills Layer
Contiene workflows y politicas especializadas: analisis de artefactos, arquitectura Playwright, locators, implementacion, evidencia y quality gate.

### Core Layer
Implementa capacidades deterministas: parsing, memoria, trazabilidad, evidencia y bootstrap.

### Project Layer
Contiene artefactos y automatizacion de cada aplicacion. Nunca modifica el core central para resolver una particularidad local.

## Dependencias

```text
Agents -> Skills -> Core
                  ^
Project -----------+
```

Los agentes pueden leer un proyecto; el proyecto no debe depender de prompts de un proveedor concreto.

## Memoria

Dos scopes:

- Central: patrones tecnicos y estandares reutilizables.
- Proyecto: reglas funcionales, observaciones, datos y decisiones propias de la aplicacion.

La memoria complementa la evidencia actual; no reemplaza Matriz/EF/ET.

## Gates

- Gate 1: artefactos disponibles y legibles.
- Gate 2: caso suficientemente definido.
- Gate 3: implementacion ejecutable.
- Gate 4: review tecnico y funcional PASS.
