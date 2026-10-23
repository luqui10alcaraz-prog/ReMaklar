# Investigación de componentes

Usar copias de `component.template.json` y `case.template.json` para empezar a registrar componentes y casos. Las plantillas no constituyen un inventario de binarios ya obtenidos. Guardar los originales fuera de esta carpeta.

Estados de evidencia: `unknown`, `candidate`, `verified`. Toda correspondencia fuente/binario o conclusión de compatibilidad debe tener evidencia. Conservar metadatos por build y por slice, incluso cuando las rutas coincidan.

El perfil de ejecución seleccionará proveedor por componente: `original-ppc`, `native-source` o `native-reimplementation`. Si una interfaz carece de puente probado, mantener el proveedor PPC y registrar la limitación. No hay cambio automático de proveedor durante una llamada.
