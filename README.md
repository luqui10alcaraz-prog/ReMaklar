# ReMaklar

Estado actual: **primera ventana auténtica del Installer original de Jaguar verificada en Darwin 6 i386**, ensayo102. La ventana muestra «Authorization» y «This software cannot be installed on this computer», con sus botones originales. La captura coincide píxel por píxel con la VRAM VESA; restaurar el checkpoint en otra VM reproduce exactamente la imagen. Ver [evidencia, regresiones y recuperación](docs/remaklar-0.11-continuacion.md). El [informe original de 0.11](docs/remaklar-0.11.md) conserva el estado histórico de direct66.

Para probarlo en Windows: doble clic en **[Probar-ReMaklar.bat](Probar-ReMaklar.bat)**. Abre una copia con ventana visible y registra CPU, memoria y capturas durante un máximo de tres minutos. Ver [uso y límites de la prueba](docs/probar-remaklar.md).

Continuación del 27 de octubre: **movimiento del cursor Aqua verificado contra la VRAM**, entrada USB real comparada entre i386 y PPC y nuevas correcciones de IOKit, descriptores y estructuras HID. El Installer todavía no completa su flujo. El checkpoint local `input141-publication` conserva el estado para retomar; la prueba de datos de una ranura HID consumida y el siguiente arranque gráfico siguen pendientes. Ver [estado exacto, resultados y recuperación](docs/remaklar-0.11-entrada-installer.md).

Investigación independiente de Mac OS X Jaguar 10.2 sobre Intel x86 de 32 bits, partiendo de Darwin 6. El objetivo es conservar comportamiento y componentes originales; la compatibilidad completa de Aqua y del Installer sigue en investigación.

## Avance 0.05: filesystem y preparación Objective-C

`ls`, `pwd` y un probe PPC propio pasan once casos nuevos en Linux y Darwin,
manteniendo todas las regresiones. Se añadieron puentes de directorios,
metadatos, cwd virtual y operaciones controladas de archivos. El primer
programa Objective-C propio ya compila como PPC con el toolchain original;
su ejecución sigue bloqueada en `ptrace(0xc000)`, sin saltarse la llamada.
Ver [resultados](docs/remaklar-0.05.md) y
[dependencias de CoreFoundation/libobjc](research/jaguar-runtimes.md).

## Avance 0.04: echo y cat originales

Pasan 23 casos compartidos en Linux y Darwin 6 i386: argumentos vacíos,
espacios, cadenas largas, stdio, lectura binaria de archivos, concatenación
y errores ENOENT. Se conservan las once fixtures nativas y las 16 regresiones
Linux. Funciona con el mismo ejecutor de 0.03, sin excepciones para estos
programas. Ver [resultados y reproducción](docs/remaklar-0.04.md) y
[registro de servicios y proveedores](research/services.md).

## Avance 0.03: ejecución dentro de Darwin i386

Los mismos `true` y `false` PPC de 0.02 funcionan dentro del Darwin instalado
en disco: entradas originales, dyld y bibliotecas originales, salidas 0 y 1.
El ejecutor se compiló en Darwin con GCC 2.95.2. Pasan once fixtures nativas
y las regresiones Linux (trece estáticas/main-only y tres dinámicas).
No se modificó XNU. Es un laboratorio monousuario, no un Jaguar completo.
Ver [reproducción y límites](docs/darwin6-native.md) e
[informe verificable](reports/remaklar-0.03.json).

## Estado inicial histórico — 23 de octubre de 2026

- Descargado el manifiesto oficial `mac-os-x-102` de Apple.
- Descargado XNU `xnu-344`, sin modificaciones.
- QEMU disponible en `C:\Program Files\qemu`; versión informada: `10.1.94 (v10.2.0-rc4-12104-gb2a6201393)`.
- Darwin 6.0.2 x86 descargado directamente de Apple y verificado contra el MD5 del servidor; SHA-256 registrados.
- Dos arranques en frío de QEMU confirmados hasta una consola i386 del CD. Ver [receta y evidencia](docs/darwin602-qemu.md).
- No se ha instalado Darwin en disco ni compilado el kernel. Pendientes Jaguar y la identificación del toolchain completo.

Consultar [la investigación inicial](docs/investigacion-inicial.md).

## Implementación 0.01

Ejecutor PPC basado en QEMU 0.10.6 compilado para Linux i386: once fixtures y dos pruebas main-only de true/false originales de Apple. Conserva CPU, TCG y loader Mach-O. La ejecución original completa con dyld y el port del ejecutor a Darwin 6 siguen pendientes. Ver [resultados, errores y reproducción](docs/remaklar-0.01.md).

## Avance 0.02: dyld y startup originales

`true` y `false` del CD Darwin 6.0.2 ejecutan su entrada original PPC y terminan
con 0 y 1 mediante `libSystem`. Se ejecutan el `dyld` original y sus dependencias,
sin saltar a `main`. Pasaron las pruebas con compilación incremental y limpia,
la prueba sin dyld y las trece regresiones anteriores. El laboratorio actual es
Linux i386 en WSL y necesita root para las direcciones bajas; el port del ejecutor
a Darwin 6 sigue pendiente. Ver [arquitectura, límites y reproducción](docs/dyld-startup.md).

## Hitos

Arquitectura vigente: [traducción basada en QEMU y reconstrucción nativa](docs/arquitectura-hibrida.md). La propuesta de intérprete propio del documento anterior queda sustituida por la evaluación de QEMU user-mode. Se aprovecha el kernel binario actual; reconstruir XNU no bloquea el trabajo de compatibilidad PPC.

1. Obtener e identificar una imagen Darwin 6.0.2 x86; registrar procedencia y SHA-256.
2. Arrancar el instalador y alcanzar una consola en QEMU; registrar hardware, comandos y fallos.
3. Instalar en un disco virtual y comprobar arranque desde disco, procesos, almacenamiento y herramientas.
4. Inventariar compiladores, headers, bibliotecas y utilidades; compilar un ejecutable Mach-O i386 mínimo.
5. En paralelo con el entorno persistente, inventariar Jaguar PPC y sus dependencias; comenzar por true/false y echo.
6. Demostrar ejecución de instrucciones PPC originales mediante un cargador e intérprete i386; después soportar el arranque completo del ejecutable.

Reconstruir XNU queda como tarea posterior, según necesidades concretas. No asumir que xnu-344 coincide exactamente con la ISO 6.0.2.

Los checkpoints deben conservar imagen base, cambios, logs y hashes. No mezclar versiones 10.2.x sin registrar la diferencia.
