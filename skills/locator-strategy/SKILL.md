---
name: locator-strategy
description: Selecciona locators Playwright estables y verificables, priorizando contratos de test y accesibilidad sobre selectores fragiles.
---
# locator-strategy
Priorizar data-testid/data-test, role+name, label y texto estable. Evitar IDs dinamicos, indices y XPath/CSS fragil. Exigir evidencia de que el locator existe y es unico; si no puede verificarse, registrar GAP.
