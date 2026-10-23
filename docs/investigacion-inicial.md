# Investigación inicial

## Fuentes obtenidas

Repositorios oficiales de Apple, descargados el 2026-10-23:

| Carpeta | Tag | Commit |
|---|---|---|
| `sources/distribution-macOS-10.2` | `mac-os-x-102` | `89d19a911010f887b57f4c6e2f61d43fa42739c5` |
| `sources/xnu-344` | `xnu-344` | `fad439e77835295998e796a2547c75c42f4bc623` |

Origen: https://github.com/apple-oss-distributions/distribution-macOS y https://github.com/apple-oss-distributions/xnu

`release.json` es el punto de partida para fijar versiones. Confirma XNU 344, cctools 435, gcc 937.2, Libc 262, IOKitUser 120 e IOKitTools 34. El manifiesto no es una distribución binaria ni garantiza contener todos los componentes de Jaguar. Todavía no se descargaron todos los proyectos.

El README de XNU 344 documenta `make ARCH_CONFIGS="PPC I386" exporthdrs all`. Esto acredita una configuración i386 existente, pero no que pueda compilarse con herramientas actuales ni que el árbol sea autosuficiente.

## Herramientas

Investigar las versiones Apple del compilador, ensamblador, linker, make, MIG, headers y utilidades de construcción. No sustituirlas automáticamente por GCC moderno o LLVM. Separar el entorno histórico de compilación del host Windows.

El manifiesto inicial enumera gcc-937.2: no confundirlo con una versión upstream de GCC. Examinar también los Developer Tools de Jaguar y los paquetes de la ISO x86 para determinar qué compilador soporta realmente el destino i386. GCC 3.1 es una pista de época, no una especificación de toolchain validada.

## Medios históricos

- Darwin 6.0.2 x86: el catálogo histórico de OpenDarwin conserva una entrada específica. La descarga y autenticidad del archivo siguen pendientes: https://docs.huihoo.com/darwin/opendarwin/downloads/index.html
- Alternativa: el MIT publica un índice de OpenDarwin 6.6.2 x86, `opendarwin-6.6.2.x86.iso.gz`, 374 MB y MD5 histórico `7e3241898f1541febf48d64eacbc244b`: https://www.mit.edu/~darwin/ . Se verificó el índice, no el archivo. Es otra distribución y otra revisión; no sustituye al objetivo 6.0.2.
- Jaguar: obtener medios originales PPC, preferentemente retail 10.2, junto con los Developer Tools. Conservar imagen de solo lectura, etiquetas, versión/build y hashes. No se ha localizado ni descargado una imagen autorizada en esta investigación.

Un SHA-256 calculado ahora permite detectar cambios posteriores; no prueba por sí mismo la autenticidad histórica. Mantener los medios y binarios propietarios fuera del repositorio público.

## Documentación

- Arquitectura de kernel y separación Darwin/OS X: https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Architecture/Architecture.html
- IOKit Fundamentals: https://developer.apple.com/library/archive/documentation/DeviceDrivers/Conceptual/IOKitFundamentals/Introduction/Introduction.html
- Mach-O: empezar por headers y loader del árbol exacto, especialmente `EXTERNAL_HEADERS/mach-o` y las interfaces Mach del kernel; contrastar con https://developer.apple.com/documentation/kernel/mach-o .
- QEMU x86: https://www.qemu.org/docs/master/system/target-i386.html
- Invocación QEMU: https://www.qemu.org/docs/master/system/qemu-manpage.html
- Pendiente: localizar manuales primarios de PowerPC de 32 bits y ABI Darwin PPC de la época. Registrar endianess, alineación, convención de llamadas, excepciones y operaciones atómicas.

Los documentos de Apple archivados pueden describir revisiones posteriores. El código y los headers de 2002 deben resolver diferencias.

## Laboratorio propuesto, aún sin validar

Partir de QEMU i386 con TCG, una CPU de 32 bits, chipset PC/i440fx y disco/CD IDE. Usar un disco pequeño, una CPU y 128–256 MB de RAM como hipótesis inicial; ajustar según resultados. Elegir tarjeta de red y vídeo después de cotejar sus IDs PCI con los drivers disponibles. Registrar la versión exacta de máquina QEMU; la instalada es una compilación de desarrollo.

Primer éxito verificable: consola del sistema con salida de `uname -a`, versión de kernel, listado de dispositivos y arranque repetible. No hay una receta de arranque validada todavía.

## Decisiones de arquitectura

Darwin x86 ofrece la base Unix, Mach e IOKit; no incorpora por sí solo Aqua, Finder, Dock ni el conjunto completo de Cocoa/Carbon/Quartz. La ausencia de fuentes de un componente impide tratarlo como un simple port recompilable.

Para binarios PPC, la traducción de instrucciones es solo una parte: hay que resolver carga Mach-O, ABI, endianess, llamadas Mach/BSD, señales, hilos, runtime Objective-C e interoperabilidad entre código PPC e i386. Comenzar con ejecutables PPC mínimos antes de frameworks gráficos. La emulación completa de una máquina PPC en QEMU puede servir de referencia separada; no constituye una capa de ejecución PPC dentro de Darwin i386.

ATI Rage 128 queda para una fase posterior: inventariar primero código y binarios existentes, interfaces framebuffer/aceleración y dispositivo físico o emulado que se pretende soportar. No asumir que un driver PPC funciona mediante traducción de aplicaciones ni que QEMU emula ese chip.
