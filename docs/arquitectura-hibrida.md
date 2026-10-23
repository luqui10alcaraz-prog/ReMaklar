# ReMaklar: arquitectura híbrida y reconstrucción nativa

Documento de diseño del 2026-10-23. Ya comenzó la [implementación 0.01](remaklar-0.01.md) sobre QEMU 0.10.6, con build Linux i386 y pruebas de código original aislado. Continúan pendientes la ejecución original completa, el build del ejecutor dentro de Darwin y los medios Jaguar retail.

## Decisión propuesta

Evaluar primero QEMU v0.10.6, target ppc-darwin-user, como base de un ejecutable de compatibilidad i386 independiente. Conservar coherentes el frontend PPC, helpers, TCG y runtime de esa revisión. No desarrollar un intérprete PPC propio ni extraer únicamente el decodificador. La selección definitiva depende de pruebas de compilación y ejecución en Darwin 6.

Este motor ejecutará procesos de usuario; no incluirá una placa PPC, firmware, MMU de sistema, controladores ni un kernel PPC. El QEMU externo que hoy arranca Darwin x86 cumple una función distinta y mantiene su versión independiente.

## Evaluación de versiones

| Candidato | Evidencia y ventaja | Coste / decisión |
|---|---|---|
| v0.10.6 | configure enumera ppc-darwin-user; darwin-user tiene Mach-O, llamadas BSD/Mach/thread, señales y commpage; existe TCG i386 | Base de evaluación preferida. Código antiguo, incompleto y posterior a Jaguar: necesita auditoría y port, no se considera compatible todavía |
| v2.5.1 | Frontend PPC y TCG i386; arquitectura más evolucionada | configure exige GLib >=2.22; no aporta el frontend Darwin histórico en esta revisión. Reserva si el núcleo antiguo bloquea la ejecución; exige rehacer integración Darwin y portar dependencias |
| QEMU actual | Mejor mantenimiento y referencia de semántica PPC/TCG | Documentación actual de user-mode enumera Linux/BSD, no Darwin. Toolchain y dependencias alejados de 2002. Usarlo como referencia y oráculo de CPU en un host moderno, no primera base para Darwin 6 |

La comparación se basa en los archivos consultados, no en builds. No se verificó cuál fue la última versión con darwin-user ni se supone que 0.10.6 sea la única viable. Antes de incorporar fuentes: resolver tag a commit, registrar hash del tarball y fijar una revisión inmutable. No mezclar frontend de una revisión con TCG de otra sin un port explícito.

## Qué reutilizar y qué acompaña a cada pieza

| Pieza | Dependencias que no pueden ignorarse |
|---|---|
| target-ppc/translate.c: decodificación y generación de IR | CPUPPCState, tablas/modelo de CPU, macros de helpers, TCG, accesos a memoria y excepciones; no es una biblioteca de decodificación autónoma |
| Operaciones/helpers PPC | Estado de CPU, reservas atómicas, softfloat y estado FP, excepciones y servicios de memoria; seleccionar CPU PPC32 de usuario, sin prometer AltiVec inicialmente |
| tcg y backend i386 | Asignación de registros, ABI de llamadas a helpers, generación y parcheo de código, alineación, buffer ejecutable y flush de caché |
| Runtime de ejecución | cpu-exec/exec, caché de translation blocks, búsqueda/encadenamiento, invalidación, salida por excepciones, señales host y traducción de PC host a invitado |
| darwin-user | Cargador Mach-O, pila inicial y bucle CPU como antecedente; syscalls, MIG, señales, commpage y headers deben contrastarse con Jaguar, no adoptarse como especificación |

Extraer un núcleo mínimo conserva una fracción significativa del runtime. Primero construir un target user-only coherente; reducirlo después mediante el grafo real de símbolos y dependencias. Deshabilitar dispositivos o GUI no elimina por sí solo todas las dependencias internas.

## Port al host Darwin 6 i386

Dificultad alta, todavía sin estimación fiable de tiempo. Verificar:

- Compilador y extensiones GNU C/assembly requeridas, linker Mach-O, make, generadores y headers. Compilar en host moderno con sysroot histórico puede evitar herramientas nuevas dentro del invitado, pero no elimina requisitos del runtime ni garantiza cross-build.
- mmap/mprotect o equivalentes Mach, protección ejecutable, buffer JIT, calling convention i386 y preservación de registros en helpers. Probar estas primitivas antes del build grande.
- Layout de ucontext/sigcontext, SIGSEGV/SIGBUS y recuperación de fallos; la adaptación para macOS Intel posterior no garantiza compatibilidad con Darwin x86 previo a 2006.
- Espacio virtual de 32 bits: código JIT, stack host, librerías host y mapas PPC compiten. Probar guest_base/ventana y límites. El acceso directo usado por QEMU user-mode no acepta automáticamente una memoria invitada segmentada arbitraria; introducir callbacks o traducción software exige adaptar generación de accesos y caché de bloques.
- Endianess y tamaños de estructuras, atomicidad lwarx/stwcx., invalidación al escribir código y al cambiar mappings. Empezar con un hilo; no declarar correctos hilos/señales por haber ejecutado true.
- El código histórico de syscalls incluye headers posteriores como sys/xattr.h: ejemplo concreto de dependencias que deben retirarse, suplirse o aislarse para Jaguar.

Si no es viable el mapa de memoria user-mode en i386, medir una ruta de memoria software dentro del proceso, conservando semántica user-only. Eso no obliga a emular una computadora PPC, pero sí puede requerir cambios sustanciales al runtime.

## Capas y límites

```text
Aplicación PPC original
        |
Cargador Mach-O + resolución de dependencias según perfil
        |
Adaptación Darwin PPC (startup / BSD / Mach / señales)
        |
Frontend PPC + helpers + TCG i386 + runtime QEMU
        |                         |
memoria invitada             puentes ABI tipados
                                  |
                         bibliotecas/servicios i386
                                  |
                         kernel Darwin x86 existente
```

La implementación puede atravesar varias capas del dibujo: TCG llama helpers y la memoria participa en las excepciones. El diagrama define responsabilidades, no supone que sean bibliotecas independientes disponibles upstream.

Interfaz propia del adaptador de CPU: crear/destruir contexto, mapear/proteger/desmapear, leer/escribir memoria y registros, ejecutar hasta evento, invalidar código y obtener traza. Eventos: trap, fallo de memoria, instrucción no soportada, puente registrado, límite de ejecución y salida. No exponer CPUPPCState al resto del proyecto. El backend puede cambiar sin alterar contratos de componentes.

Implementar el cargador y la personalidad Darwin con trazas verificables. Comparar primero el cargador histórico con LC_SEGMENT, LC_UNIXTHREAD y LC_LOAD_DYLINKER de los binarios reales. Evitar asumir formatos modernos. Para el primer main aislado puede usarse un subconjunto; ejecutar un proceso completo requiere startup e inicializadores correctos.

## Sustitución progresiva

Dos mecanismos distintos:

1. Sustitución de procesos completos: un perfil elige utilidad/daemon PPC o ejecutable i386 con el mismo contrato observable. Es la primera opción y evita puentes dentro de un proceso.
2. Sustitución de bibliotecas: el cargador invitado redirige símbolos concretos hacia trampolines y marshalling i386. No puede cargar directamente una dylib i386 con dyld PPC ni compartir objetos ABI incompatibles.

Cada componente tiene identidad y versión, proveedor PPC original, proveedor nativo, contrato y pruebas. La selección es explícita por perfil; el rootfs original es inmutable. Nunca sustituir silenciosamente según el resultado de una llamada: eso puede duplicar efectos. El fallback se selecciona antes de crear el proceso o instancia, y su estado no se migra automáticamente.

Los puentes convierten escalares/estructuras campo por campo, punteros invitados, ownership, callbacks y errores. Usar handles para FILE, objetos y recursos opacos cuando corresponda. printf/varargs, Objective-C, excepciones y APIs con callbacks no son puentes triviales. Un API C estrecho es la primera frontera razonable. Los mensajes Mach requieren contratos de cada protocolo; no un byteswap global.

## Infraestructura de investigación

Separar artefactos originales de resultados reproducibles:

- `media/` y futuros rootfs: privados, originales, hashes y procedencia.
- `research/inventory/`: metadatos de binarios; una fila/registro por archivo y slice.
- `research/interfaces/`: contratos documentados con evidencia, comportamiento y dudas.
- `research/cases/`: entradas y oráculos comparativos, sin incorporar binarios propietarios.
- `profiles/`: selección explícita de proveedores y overrides versionados.
- `logs/`: trazas de carga, imports resueltos, traps, llamadas puente y resultados.

Inventario mínimo: build del sistema, ruta, SHA-256, slices, tipo Mach-O, segmentos/entrada, load commands, install name, versiones, dependencias directas/transitivas, símbolos definidos/importados, relocaciones, inicializadores, recursos y servicios requeridos. Conservar salida cruda de herramientas y su versión. Enlazar las fuentes Apple por proyecto/tag/commit y marcar nivel de correspondencia: confirmado por evidencia, candidato o desconocido. Un nombre de proyecto no prueba equivalencia con un binario.

Orden de implementación nativa: fuente publicada de versión apropiada -> port/recompilación -> contrato observado y reimplementación compatible -> traducción como proveedor de compatibilidad. El descompilado ayuda a investigar; no se tratará como una conversión automática a código mantenible.

Contratos: firmas, ABI/layouts/endianness, ownership, errores, estado global, threading, callbacks, archivos/configuración y efectos externos. Cada afirmación referencia fuente, header, traza o experimento; separar hechos de hipótesis. Para ingeniería basada en comportamiento, conservar especificaciones y pruebas separadas del análisis de implementación.

Pruebas diferenciales: misma entrada y entorno controlado en Jaguar PPC original, binario PPC traducido y reconstrucción i386. Comparar stdout/stderr en bytes, exit status, archivos generados y respuestas API normalizadas según reglas explícitas. Fijar locale, timezone, reloj cuando sea necesario, permisos y fixtures de filesystem. Ejecutar cada caso desde snapshot limpio. Para bibliotecas agregar layouts, callbacks, errores y estado; documentar diferencias permitidas. Si no hay Jaguar PPC de referencia, marcar oráculo pendiente: comparar contra fuente recompilada no lo reemplaza.

## Licencias y distribución

QEMU es un conjunto de licencias. En v0.10.6 LICENSE describe núcleo virtual LGPL y TCG BSD; main.c y syscall.c de darwin-user llevan GPL-2.0-or-later, machload.c LGPL-2.0-or-later. El encabezado de tcg/i386/tcg-target.c contiene una licencia permisiva de estilo MIT pese a la descripción general BSD. Registrar la licencia exacta de cada archivo seleccionado y sus dependencias, preservando avisos.

Plan de empaquetado: ejecutable de compatibilidad derivado de QEMU con su fuente correspondiente y modificaciones bajo las condiciones aplicables; componentes nativos separados con licencia y procedencia propias; binarios Apple aportados por el usuario en rootfs aparte. No asumir que un wrapper, una biblioteca dinámica o separar carpetas elimina obligaciones de copyleft. Una frontera de procesos/protocolo facilita separación técnica, pero no resuelve automáticamente la clasificación jurídica de una obra combinada. Revisar las condiciones exactas antes de distribuir una combinación con componentes propietarios.

La auditoría de licencias es un requisito de incorporación, no una afirmación de que todo el conjunto puede relicenciarse como BSD/LGPL. No se necesita decidir una licencia única para todo Jaguar reconstruido en esta etapa.

## Experimentos y puertas de decisión

1. Instalar Darwin x86 y verificar C, memoria ejecutable, señales, mmap/mprotect y ABI de helpers. Snapshot del sistema y toolchain.
2. Fijar revisión QEMU 0.10.6 y auditar build/licencias/dependencias. Build user-only sin dispositivos. Resultado: lista concreta de incompatibilidades; todavía no importar un gran árbol al proyecto principal.
3. Ejecutar un fixture PPC32 que retorne un valor, otro con cargas big-endian y uno con write/exit. Registrar estado, trazas y fallo de memoria controlado. Debe ejecutarse dentro de Darwin i386; una ejecución externa en Windows/Linux solo sirve como control.
4. Decidir si continuar 0.10.6 o portar un núcleo posterior. Criterios: compilación reproducible, JIT/retorno a helpers, mapa de memoria estable, traps correctos y ausencia de bloqueos estructurales. No seleccionar versión por antigüedad solamente.
5. Inventariar Jaguar y ejecutar true/false originales; luego echo, primero main aislado si hace falta, después entrada completa con dependencias. Hash del archivo y cobertura del arranque deben acompañar el resultado.
6. Compilar versiones nativas desde shell_cmds-34, comparar en los tres entornos y seleccionarlas por perfil. El experimento PPC de echo permanece como prueba de compatibilidad; la versión nativa pasa a ser el proveedor normal cuando cumpla el contrato.

Este último paso demuestra la evolución híbrida: cambiar el proveedor de un componente no exige modificar el kernel ni retirar el motor de compatibilidad de los componentes restantes.

## Fuentes primarias consultadas

- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/configure
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/darwin-user/main.c
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/darwin-user/machload.c
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/darwin-user/syscall.c
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/target-ppc/translate.c
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/tcg/i386/tcg-target.c
- https://raw.githubusercontent.com/qemu/qemu/v0.10.6/LICENSE
- https://raw.githubusercontent.com/qemu/qemu/v2.5.1/configure
- https://raw.githubusercontent.com/qemu/qemu/v2.5.1/target-ppc/translate.c
- https://raw.githubusercontent.com/qemu/qemu/v2.5.1/LICENSE
- https://www.qemu.org/docs/master/devel/tcg.html
- https://www.qemu.org/docs/master/user/main.html

La documentación master es mutable y no especifica el comportamiento exacto de v0.10.6. La versión histórica se evalúa por su código; las pruebas futuras fijarán las conclusiones de compatibilidad.
