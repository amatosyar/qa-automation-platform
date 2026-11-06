# Artifact adapters

Contrato de salida recomendado:

- `matrix.cases.json`: casos existentes de la Matriz, sin reinterpretarlos.
- `ef.sections.json`: secciones/reglas funcionales con referencia de origen.
- `et.sections.json`: componentes/contratos/consideraciones tecnicas con referencia de origen.

Cada registro debe conservar `source_file` y `source_location`. Los parsers concretos dependen del formato real de los artefactos y deben agregarse como adapters, no hardcodearse en los agentes.
