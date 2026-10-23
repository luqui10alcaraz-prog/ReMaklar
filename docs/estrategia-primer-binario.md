# Estrategia: primer código original de Jaguar en Intel

## Objetivo y alcance

Usar Darwin x86 y su kernel binario funcional como plataforma. Recompilar XNU no es un requisito del próximo hito. Dos frentes de trabajo: instalación persistente y herramientas mínimas; análisis de binarios PPC originales. Se pueden alternar sin que la reconstrucción del sistema bloquee el análisis.

Estado: aún no hay medios Jaguar PPC en `media/`; no se han inspeccionado sus ejecutables. Las dependencias binarias concretas, slices y símbolos deben verificarse, no inferirse del nombre del programa.

## Fuentes confirmadas

El manifiesto Apple `mac-os-x-102` identifica Csu-45, Libc-262, Libsystem-60, Libm-40.2, Libinfo-129, objc4-222, shell_cmds-34, file_cmds-60, text_cmds-18 y system_cmds-230. Tener fuentes no garantiza recompilación inmediata: pueden faltar headers, assembly i386, herramientas o proyectos auxiliares.

Se descargaron además:

- shell_cmds-34: commit `c33c5559b9fe27af67ee00c6edd435568bc180dd`.
- Csu-45: commit `f35b5862caaed325d40270dcf43d5303bf11d08b`.

Origen: repositorios homónimos de https://github.com/apple-oss-distributions . El código de `echo/echo.c` usa strcmp, printf, putchar y exit; el binario puede incluir más dependencias por optimizaciones y código de arranque. El proyecto también contiene true y false.

No se confirmó aquí la publicación completa de dyld de Jaguar ni de CoreFoundation de esa versión. El manifiesto consultado no enumera proyectos con esos nombres. Investigar la organización histórica de cctools antes de concluir ausencia; un dyld moderno no sustituye al de Jaguar.

## Qué necesitamos primero

Para una utilidad C: cargador Mach-O PPC, ejecución de instrucciones PPC, memoria big-endian, pila/argumentos compatibles y las funciones importadas realmente usadas. Para ejecutar desde su entrada original hay que resolver además Csu, dyld, bibliotecas e inicializadores. Cocoa, Carbon, Objective-C, IOKit de usuario y servicios gráficos no son requisitos del primer experimento.

Darwin ya proporciona las funciones i386 del host. No reconstruir Libc y Libsystem completas antes de comprobar si basta un pequeño puente tipado a las funciones existentes. El puente no puede compartir directamente estructuras internas como FILE o buffers de punteros.

Las capas gráficas y de aplicaciones propietarias no están incluidas como conjunto completo en Darwin. Los binarios PPC sin slice i386 necesitan ejecución PPC o una implementación de sus interfaces; recompilarlos requiere disponer de sus fuentes. Confirmar por archivo qué arquitectura y qué fuentes existen. Una biblioteca abierta también puede distribuirse como binario PPC: disponibilidad de fuentes y arquitectura son ejes distintos.

## Cómo cargar sin modificar XNU

Un ejecutable nativo i386, `remaklar-run`, abre el archivo PPC como datos. El cargador de XNU 344 rechaza arquitecturas distintas (`bsd/kern/mach_loader.c`, LOAD_BADARCH); dlopen/dyld nativos no traducen instrucciones.

1. Validar límites y endianess de Mach-O 32 bits y seleccionar slice PPC si es FAT.
2. Crear un espacio virtual invitado separado lógicamente: tabla de segmentos y backing buffers. Traducir cada dirección PPC a memoria del host; no asumir direcciones idénticas en un proceso i386.
3. Cargar LC_SEGMENT, inicializar datos/zerofill y conservar permisos lógicos. Evitar aplicar relocaciones innecesarias cuando la imagen pueda mantenerse en sus direcciones virtuales originales.
4. Interpretar PPC con GPR, PC, LR, CTR, CR y XER; añadir FPR/FPSCR cuando lo exijan las instrucciones. Fallar explícitamente ante una instrucción desconocida. Empezar con intérprete; JIT queda para después.
5. Para el proceso completo, implementar LC_UNIXTHREAD y pila inicial de la época; resolver LC_LOAD_DYLINKER, LC_LOAD_DYLIB, símbolos, stubs y punteros lazy/non-lazy. No asumir LC_MAIN, chained fixups o caché dyld moderna.
6. Implementar importaciones como trampolines invitados a puentes i386 con firmas explícitas. Los callbacks requieren trampolines inversos. No hacer cast de una dirección PPC a un puntero de función i386.

Primera iteración: invocar la función main original en la imagen cargada, identificada por símbolos o análisis contrastado con fuente; construir argc/argv PPC y simular un retorno controlado. Esto demuestra ejecución del cuerpo original, pero omite arranque e inicializadores y NO equivale a soportar el ejecutable completo. Si el archivo no permite localizar main con certeza, no adivinar offsets.

Alternativa posterior: ejecutar dyld y bibliotecas PPC originales en el intérprete, interceptando syscalls/traps. Conserva más código original pero amplía mucho la superficie inicial. Elegirla cuando los puentes de biblioteca dejen de ser manejables, no antes de medir dependencias.

## ABI e interfaces a resolver

- PPC big-endian frente a i386 little-endian: bytes de texto se conservan; enteros, punteros, tablas y estructuras se convierten campo por campo. Los punteros invitados son valores de 32 bits, no punteros host.
- Llamadas C PPC: registros de argumentos, pila alineada y área de enlace/guardado, LR y registros preservados. Contrastar Csu y el ABI Darwin de 2002; no usar el ABI ELF/Linux PPC como sustituto.
- i386: construir una llamada host según el ABI de sus herramientas. Resolver aparte enteros de 64 bits, estructuras devueltas por valor, flotantes y varargs. printf necesita un puente consciente del formato y argumentos invitados; no reenviar un va_list PPC.
- BSD: interceptar sc y despachar una tabla específica. Leer r0 y argumentos PPC, convertir buffers/estructuras, invocar funciones host y reconstruir resultados/errores. XNU 344 tiene una convención importante de avance del PC para omitir el salto a cerror al retornar con éxito; no basta con devolver errno ni copiar una convención Linux. Ver `bsd/dev/ppc/systemcalls.c` y contrastar con 344.2.3 antes de ampliar cobertura.
- Mach: distinguir traps y mensajes, convertir headers, descriptores, datos out-of-line, derechos/puertos y estructuras MIG según la interfaz. Una conversión global de palabras no es válida. No son necesarios para la primera llamada aislada si la ruta no los usa.
- Aplazar señales, pthreads, fork/exec, excepciones y callbacks hasta que la prueba los requiera. Registrar claramente qué falta; no ocultar llamadas sin implementar devolviendo éxito.
- Objective-C requiere más adelante runtime y metadatos compatibles, mensajería y callbacks cruzados. No empezar con una aplicación Cocoa.

## Plan de ejecución y criterios de éxito

1. Instalar Darwin, arrancar sin CD y guardar disco base. Inventariar cc/gcc, as, ld, make, headers, crt, bibliotecas, otool, nm y lipo; MIG no es un bloqueo del intérprete inicial. Compilar un programa C i386 y comprobar entrada/salida y código de retorno.
2. Obtener los medios originales Jaguar PPC. Conservar build, procedencia y hashes; extraer true, false y echo, además de dyld y sus bibliotecas transitivas. Inventariar con file/lipo/otool/nm: slices, load commands, entrada, segmentos, imports, versión de bibliotecas e inicializadores. Analizar una copia sin sustituir archivos del host.
3. Prueba del núcleo del intérprete con fixtures PPC propios pequeños. Es una prueba técnica, no el resultado de preservación.
4. Cargar el main original de true y false sin recompilar sus instrucciones. Confirmar retorno 0/1 y guardar traza de PCs e instrucciones procedentes del archivo cuyo SHA-256 se registró. Su selección definitiva depende del análisis binario: si el compilador incorporó llamadas de salida, implementar el puente correspondiente.
5. Ejecutar el main original de echo con argumentos y comprobar salida exacta y opción -n. Instrumentar cada puente; no implementar echo en el host y presentar esa salida como ejecución PPC.
6. Extender el cargador para ejecutar desde la entrada original al menos una de esas utilidades, preservando intacto el archivo, con startup, imports e inicialización correctos. Comparar salida, stderr y exit status con un Jaguar PPC de referencia cuando esté disponible.

Éxito inicial honesto: instrucciones originales de un componente identificado de Jaguar ejecutadas por un proceso i386 en Darwin. Éxito de compatibilidad de ejecutable: el archivo original completo corre desde su entrada. Recompilar el fuente de echo para i386 es útil como control, pero no demuestra traducción del binario original.

Sin medios PPC se puede completar instalación, inventario, parser y fixtures; no se puede afirmar que se ejecutó un binario original de Jaguar. La recompilación del kernel queda para cuando aparezca una limitación concreta que la justifique.
