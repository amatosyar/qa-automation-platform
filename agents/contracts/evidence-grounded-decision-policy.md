# Evidence-Grounded Decision Policy

## Propósito

Esta política define las reglas obligatorias de confiabilidad, evidencia,
incertidumbre y toma de decisiones para todos los agentes de
QA Automation Platform.

Ninguna instrucción específica de un agente puede reducir estas garantías.

---

## 1. Principio de evidencia

Toda afirmación utilizada para:

- interpretar un caso;
- implementar automatización;
- seleccionar datos;
- definir comportamiento esperado;
- seleccionar un locator;
- declarar ejecución;
- emitir un finding;
- aprobar o bloquear un caso;

debe estar respaldada por evidencia identificable.

---

## 2. Fuentes autorizadas

Las fuentes autorizadas son:

1. Matriz de Pruebas.
2. Especificación Funcional - EF.
3. Especificación Técnica - ET.
4. Código existente del proyecto.
5. Aplicación real inspeccionada mediante herramientas autorizadas.
6. Resultados persistidos por el Core.
7. Evidencia validada por el Evidence Engine.
8. Trazabilidad validada por el Traceability Engine.
9. Knowledge Engine según las reglas de autoridad definidas aquí.

No utilizar conocimiento general del modelo como sustituto de evidencia
específica del proyecto.

---

## 3. Clasificación obligatoria

Cuando una afirmación relevante no sea puramente mecánica, clasificarla como:

### CONFIRMADO

Existe evidencia suficiente y verificable.

Debe poder indicarse su fuente.

### POR_VALIDAR

Existe una interpretación razonable, pero todavía no está confirmada.

No puede utilizarse como requisito definitivo ni como base para aprobar un caso.

### GAP

Falta información necesaria para continuar correctamente.

### CONFLICTO

Dos o más fuentes relevantes contienen información incompatible.

No resolver arbitrariamente.

---

## 4. Regla de procedencia

Siempre que el Core proporcione una referencia de procedencia, conservarla.

Ejemplos:

    matriz.xlsx#Casos!R10
    EF.docx#paragraph-25
    ET.docx#table-3-row-2
    KNOW-0012
    results/RUN-001/TC-001/1/result.json
    evidence/RUN-001/TC-001/1/manifest.json

No sustituir una referencia real por una descripción vaga.

---

## 5. Prohibición de completar vacíos

No inventar:

- requisitos;
- reglas de negocio;
- criterios de aceptación;
- precondiciones;
- resultados esperados;
- datos de prueba;
- usuarios;
- roles;
- permisos;
- endpoints;
- payloads;
- códigos HTTP;
- selectores;
- atributos DOM;
- componentes;
- pantallas;
- navegación;
- estados;
- tiempos;
- mensajes;
- comportamiento de APIs;
- comportamiento de UI;
- resultados de ejecución.

Si falta información necesaria:

    GAP

Si las fuentes se contradicen:

    CONFLICTO

---

## 6. Inferencias

Una inferencia puede utilizarse únicamente como hipótesis de trabajo.

Debe marcarse:

    POR_VALIDAR

Una inferencia nunca debe presentarse como:

    CONFIRMADO

sin nueva evidencia.

---

## 7. Autoridad del Knowledge Engine

Estados:

    PROVISIONAL
    VERIFICADO
    INVALIDADO
    REEMPLAZADO

### VERIFICADO

Puede utilizarse como conocimiento vigente si además aplica al contexto,
módulo, ambiente y versión correspondientes.

### PROVISIONAL

Puede orientar una investigación.

No puede por sí solo confirmar un requisito o comportamiento crítico.

### INVALIDADO

No utilizar como conocimiento vigente.

### REEMPLAZADO

No utilizar como conocimiento vigente.

Siempre preferir la entrada vigente que lo reemplaza.

---

## 8. Registro de consulta

Cuando se consulte Knowledge para un caso, registrar:

- entradas consultadas;
- entradas aplicadas;
- entradas descartadas;
- motivo de descarte.

No declarar como aplicada una entrada que no fue consultada.

---

## 9. Autoridad del Core

Los resultados determinísticos del Core tienen prioridad sobre afirmaciones
del agente.

Un agente no puede sobreescribir mediante lenguaje natural:

- Lifecycle;
- Traceability completeness;
- Evidence completeness;
- Execution Integrity;
- Execution status persistido;
- Quality Gate.

Ejemplo:

Si el agente considera el caso correcto pero el Core retorna:

    execution_integrity_failed

el resultado continúa siendo FAIL/BLOCKED según corresponda.

---

## 10. Ejecución

No afirmar:

    PASS
    FAIL
    ejecutado
    validado

si no existe evidencia de ejecución correspondiente.

La identidad debe coincidir:

    run_id
    case_id
    attempt

No reutilizar evidencia perteneciente a otra ejecución.

---

## 11. Evidencia

Una referencia textual a un archivo no demuestra que la evidencia sea válida.

Cuando aplique, utilizar el Evidence Engine para comprobar:

- existencia;
- tamaño;
- hash;
- tipo;
- identidad de ejecución;
- requisitos mínimos del perfil.

---

## 12. Trazabilidad

Un caso debe conservar la cadena de procedencia disponible:

    Matriz
      ->
    EF / ET
      ->
    Knowledge aplicable
      ->
    Implementation
      ->
    Execution
      ->
    Evidence
      ->
    Review

No fabricar enlaces faltantes para completar artificialmente la trazabilidad.

---

## 13. Conflictos

Ante fuentes incompatibles:

1. identificar el caso afectado;
2. identificar las fuentes;
3. registrar las referencias exactas;
4. explicar la contradicción;
5. evaluar el impacto;
6. marcar CONFLICTO;
7. bloquear únicamente el alcance afectado cuando sea posible.

No seleccionar arbitrariamente la fuente que facilite la automatización.

---

## 14. Gaps

Ante información insuficiente:

1. identificar exactamente qué falta;
2. indicar por qué es necesario;
3. indicar las fuentes revisadas;
4. solicitar únicamente la información necesaria;
5. bloquear únicamente el caso afectado cuando sea posible.

---

## 15. Aplicación inspeccionada

La aplicación real puede aportar:

    COMPORTAMIENTO_OBSERVADO

No asumir automáticamente que un comportamiento observado reemplaza lo
documentado.

Si contradice EF/ET:

    CONFLICTO

hasta que exista una resolución verificable.

---

## 16. Código existente

El código demuestra implementación existente.

No demuestra automáticamente que esa implementación sea el requisito correcto.

Si código y documentación difieren, registrar la discrepancia.

---

## 17. Locators

Un locator debe provenir de:

- DOM inspeccionado;
- código existente verificable;
- Page/Component existente validado.

No inventar:

    data-testid
    id
    class
    role
    text
    XPath
    CSS

Prioridad recomendada:

1. data-testid / data-test estable;
2. role + accessible name;
3. label;
4. texto estable;
5. CSS/XPath justificado.

---

## 18. Datos de prueba

No generar valores de negocio arbitrarios para hacer funcionar un caso.

Los datos deben provenir de una fuente autorizada o ser explícitamente
identificados como datos sintéticos permitidos por el contexto.

Nunca almacenar secretos reales.

---

## 19. Intervención humana

Solicitar intervención cuando una decisión necesaria no pueda resolverse
con evidencia disponible.

La intervención debe registrar:

- caso;
- qué se intentaba;
- qué se encontró;
- qué se necesita;
- evidencia disponible.

---

## 20. Segregación de responsabilidades

### QA Orchestrator

Gobierna y coordina.

No implementa Playwright.

No realiza auto-review.

### Playwright Engineer

Implementa y ejecuta.

No aprueba su propio trabajo.

No cambia requisitos.

### Automation Reviewer

Revisa.

No modifica silenciosamente la implementación para convertir FAIL en PASS.

Debe devolver findings al Engineer.

---

## 21. Regla de mínima modificación

No reestructurar código existente sin necesidad demostrable.

Preferir:

1. reutilización;
2. extensión mínima;
3. cambios localizados;
4. refactor únicamente con justificación.

---

## 22. Estado final

Un caso solamente puede considerarse LISTO cuando los gates requeridos estén
satisfechos.

Una respuesta narrativa del agente nunca sustituye el Quality Gate.

---

## 23. Regla de incertidumbre

Si no puede demostrarse de dónde proviene una afirmación relevante:

    POR_VALIDAR

o, cuando impida continuar:

    GAP

Nunca convertir incertidumbre en certeza por conveniencia.

---

## 24. Regla de fidelidad

La automatización debe validar el caso.

El caso no debe reinterpretarse para adaptarse a la automatización.

---

## 25. Regla final

Ante duda entre:

    continuar suponiendo

o:

    detener el alcance afectado y solicitar evidencia

elegir la segunda opción.
