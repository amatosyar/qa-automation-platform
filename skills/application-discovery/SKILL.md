---
name: application-discovery
description: Inspecciona una aplicacion Web real antes de implementar automatizacion, obteniendo evidencia verificable del DOM y locators candidatos sin inventar selectores.
---

# application-discovery

## Objetivo

Obtener evidencia tecnica verificable de la aplicacion real antes de crear o modificar automatizacion Playwright.

Esta skill no define requisitos funcionales.

La existencia de un elemento en Matriz, EF, ET o evidencia visual no confirma por si sola su locator tecnico.

## Fuentes permitidas

El discovery puede utilizar:

- aplicacion real inspeccionada;
- DOM real;
- accessibility tree;
- codigo existente verificable;
- locators existentes previamente verificados.

No utilizar conocimiento general del modelo como sustituto de inspeccion.

## Flujo

Para cada elemento requerido por el caso:

1. abrir la aplicacion autorizada;
2. navegar hasta el estado requerido;
3. inspeccionar el DOM real;
4. identificar elementos candidatos;
5. seleccionar una estrategia de locator;
6. comprobar el numero de coincidencias;
7. registrar procedencia;
8. clasificar el resultado.

## Prioridad de locator

Preferir:

1. `data-testid` / `data-test`;
2. role + accessible name;
3. label;
4. texto estable;
5. CSS justificado;
6. XPath justificado como ultimo recurso.

La prioridad puede cambiar cuando exista evidencia tecnica que justifique una alternativa mas estable.

## Clasificacion

`VERIFIED`

El locator proviene de evidencia verificable y produce exactamente una coincidencia en el estado inspeccionado.

`NOT_FOUND`

El elemento requerido no pudo localizarse en el estado inspeccionado.

`AMBIGUOUS`

El locator candidato produce mas de una coincidencia.

Un resultado `NOT_FOUND` o `AMBIGUOUS` no puede promocionarse artificialmente a `VERIFIED`.

## Evidencia minima

Registrar como minimo:

- elemento funcional;
- URL o contexto de pagina observado;
- estrategia;
- valor;
- `match_count`;
- fuente;
- role cuando exista;
- accessible name cuando exista;
- label cuando exista;
- atributos relevantes cuando aporten estabilidad.

La fuente de un locator descubierto mediante navegador debe ser:

`DOM_INSPECTION`

## Restricciones

No:

- inventar IDs;
- inventar `data-testid`;
- inventar labels;
- asumir estructura DOM desde screenshots;
- utilizar indices para forzar unicidad sin justificacion;
- utilizar XPath absoluto;
- transformar un locator ambiguo en valido escogiendo arbitrariamente el primer match;
- registrar secretos presentes en el DOM;
- almacenar tokens, passwords, cookies o datos sensibles como conocimiento reusable.

## Handoff

Solo locators `VERIFIED` pueden entregarse como nuevos locators candidatos para Pages o Components.

`NOT_FOUND` y `AMBIGUOUS` deben mantenerse como hallazgos pendientes y escalarse segun el contrato del Engineer.
