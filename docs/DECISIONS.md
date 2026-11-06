# Decisiones arquitectonicas iniciales

- Tres agentes, no un agente por tarea pequena.
- La Matriz es la fuente de casos de prueba.
- EF/ET no generan casos por defecto; sustentan y complementan los existentes.
- Page/Component Objects son el baseline general; excepciones requieren evidencia y decision documentada.
- Prohibidos secretos versionados.
- Prohibidos waits fijos como solucion por defecto.
- Un selector no verificable se registra como gap, no se inventa.
- Reviewer independiente del Engineer.
