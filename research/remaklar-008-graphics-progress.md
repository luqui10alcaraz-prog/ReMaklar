# ReMaklar 0.08 — avance del arranque gráfico original

Fecha: 2026-10-25. Jaguar 10.2 build 6C115; Darwin 6.0 RELEASE_I386.

## Estado inicial y preservación

Se continuó desde `e83fe6c` (0.07), con Objective-C y CoreFoundation originales i386 ya verificados. El ejecutor nativo 0.06, Mach-O i386, permaneció intacto en `/var/tmp/remaklar/build/qemu-darwin6/ppc-darwin-user/qemu-ppc` (MD5 `90df4430f3f07be336d1f0e2387cb1c8`). Se reprodujo el bloqueo de WindowServer en BSD 2 (`fork`), salida 125: `logs/graphics-008/initial-native/`.

Se reutilizaron la VM activa, el overlay `vm/darwin602-native-007-overlay-02.qcow2` y el intercambio FAT existente. No se crearon discos ni imágenes de instalación. ISO y base Darwin se verifican por SHA-256 en [preserved-input-hashes.json](../reports/graphics-008/preserved-input-hashes.json). El repositorio experimental 0.06 se conservó; el runtime nuevo se desarrolló en el worktree aislado `build/qemu-008-source`, desde `2e4ce5b0d163c2a6882e43c20869f4363916cd48`.

## Ruta de arranque identificada

El `private/etc/rc` del CD deriva a `rc.cdrom` cuando existe `System/Installation`. Este arranca kextd, red local, volfs y autodiskmount; luego StartATSServer, WindowServer, pbs y los hooks del CD; finalmente CDIS/splash con Installer, `OS_INSTALL=1`, y una alternativa Minstaller según configuración. No se ejecutó ese script completo ni se lanzó una instalación.

WindowServer es un enlace al **Window Manager** original dentro de CoreGraphics. Installer está en `Applications/Utilities/Installer.app`, no en la secuencia de Finder. El loginwindow del CD es un archivo vacío: no se trató como ejecutable funcional. Los manifiestos de [componentes](../reports/graphics-008/installer-inventory.json) y [dependencias](../reports/graphics-008/library-closure.json) registran arquitecturas, rutas y hashes. Todos los componentes de Jaguar empleados proceden del mismo CD 6C115; no se añadieron componentes de Tiger.

Se extrajeron únicamente recursos seleccionados y dependencias faltantes. La clausura estática de Installer contiene 59 imágenes PPC, sin dependencias ausentes en el conjunto local. Esto no garantiza que estén resueltas todas las cargas dinámicas. En el invitado se añadieron solo archivos ausentes; no se reemplazaron bibliotecas existentes. El framework IOKit de la cohorte Darwin se obtuvo del propio Darwin instalado, separado de la cohorte Jaguar.

## Cambios implementados

- BSD `fork`, `getppid`, `setsid` y un subconjunto explícito de `wait4`: procesos reales del host, memoria COW, descriptores compartidos y resultados PPC de padre/hijo. El alcance es el arranque de un único hilo; opciones/rusage de wait no adaptadas se rechazan.
- BSD `execve`: reemplazo real por el ejecutor nativo y carga del Mach-O PPC solicitado, conservando PID, argv, entorno PPC, cwd, descriptores no CLOEXEC y estado del espacio de puertos modelado. El entorno PPC no configura el dyld i386. Los cursores DIR abiertos siguen bloqueados explícitamente.
- RPC 205: puerto maestro IOKit real de XNU. Puente tipado para RPC 2809 (registry path), 2804 (matching services) y 2802 (iterator next), con validación de mensajes PPC y traducción de capacidades; utiliza el IOKit **original i386** mediante un puente explícito. Las respuestas y errores proceden de Darwin, no de servicios gráficos inventados.
- BSD `access` mediante comprobación real del host sobre la ruta virtual traducida, y decodificación de `syscall(number, ...)` para los argumentos en registros PPC. No se instala un manejador de señales nativo apuntando a código PPC.
- Pruebas propias de procesos, exec y consultas IOKit; supervisor con tiempos acotados y separación entre salida del líder y descendientes.

El bootstrap y gran parte del espacio Mach previo siguen siendo un modelo local limitado: estos cambios no implementan un bootstrap global ni IPC completo entre procesos PPC. Consultar el registro IOKit no equivale a abrir un cliente del framebuffer ni a mapear su memoria.

El parche [0006-processes-iokit.patch](../patches/qemu-0.10.6/0006-processes-iokit.patch) y su [manifiesto](../patches/qemu-0.10.6/graphics-manifest.json) preservan todo el código del runtime. Se verificó su aplicación y la serie completa 0001–0006 desde QEMU v0.10.6, con igualdad byte a byte de los tres archivos modificados; no se reconstruyó 0.06 para esta comprobación. `scripts/checkout-qemu.sh` incorpora el checkpoint explícito `0.08-graphics`; conserva su valor predeterminado anterior.

## Pruebas y resultados

La ejecución integrada `graphics008-run5` se completó en la VM existente; sus estados individuales y trazas están en [native-final](../reports/graphics-008/native-final/). El `runner_exit=0` del wrapper significa que se recolectaron las pruebas, no que todos los lanzamientos funcionen. Los seguimientos posteriores recompilaron únicamente el objeto del kernel del traductor afectado y ejecutaron pruebas acotadas.

| Prueba | Resultado | Evidencia / alcance |
|---|---|---|
| Fixture PPC de fork/wait/COW | PASS | ABI estática en Linux, sin bajar `mmap_min_addr`; seguimiento añade setsid y su EPERM |
| fork con libSystem original | PASS | Referencia i386 y cohortes PPC Darwin/Jaguar; estado 37, COW y reap ECHILD |
| exec real | PASS | i386 y PPC Darwin/Jaguar: PID, argv0, entorno, cwd, FD heredado, CLOEXEC, ENOENT y ENOEXEC |
| setsid real | PASS | i386 y PPC Jaguar, éxito y segundo intento EPERM; [native-followup](../reports/graphics-008/native-followup/) |
| access directo/indirecto y ENOENT | PASS | i386 y PPC Jaguar; [native-access](../reports/graphics-008/native-access/) |
| IOKit de Jaguar PPC → IOKit i386 → XNU | PASS | Matching IOFramebuffer, iterador no nulo y primer objeto real; liberación de derechos |
| Consulta IOKit con raíz PPC de muestras Darwin | BLOCKED | Falta SystemConfiguration en esa raíz parcial; no se suplió con el framework de Jaguar |
| Utilidades originales | PASS | 23/23, bytes y salidas esperadas |
| Filesystem | PASS | 11/11, sin residuos |
| Quartz original PPC, bitmap fuera de pantalla | PASS | `Quartz PPC bitmap OK`, 64×48; no acredita una pantalla de WindowServer |
| Objective-C original i386 | PASS | Ejecutado directamente, sin traductor PPC |
| CoreFoundation original i386 | PASS | Ejecutado directamente, sin traductor PPC |
| Fixtures previos de arranque | PASS | 11 casos Linux, incluidos fallos controlados |
| Preparación inicial de DesktopServicesPriv | FAIL corregido | Ausente tras extracción selectiva; copia explícita original verificada y entrada de Installer alcanzada |
| Parche reproducible / preservación | PASS | Serie completa aplicable y hashes de ISO/base sin cambios |

Los MD5 de 58 imágenes originales presentes en la prueba integrada coincidieron con sus fuentes; la imagen restante, DesktopServicesPriv, se transfirió explícitamente en `run6` y su MD5 también coincidió. La extracción selectiva inicial con `gnutar -T` no la dejó disponible: ese fallo de preparación se conserva en los logs, se corrigió con copia del original ausente y el driver exige ahora verificar el archivo extraído. No se atribuyó ese fallo a AppKit ni se presentó la clausura preparada como prueba de carga efectiva.

## Mayor avance con WindowServer

El Window Manager original se cargó desde su entrada `0x2998`; ejecutó fork real y exec real de su propia imagen. El hijo volvió a cargar el dyld y las bibliotecas originales. Después de incorporar setsid, pasó a inicialización de preferencias y llegó a una llamada indirecta de libSystem: syscall 0, argumento 46 (`sigaction`). En `run7`, la decodificación indirecta ya probada deja visible el siguiente límite: no está implementada la entrega de señales PPC. La traza exterior aún imprime trap 0 y registra el destino 46 en r3; no indica una regresión de access. El padre sale 0 por la ruta de daemonización: **WindowServer continúa BLOCKED**. El supervisor siguió al hijo incluso tras su cambio de sesión, sin dejar procesos traducidos vivos.

El intento `run4` solo esperaba tres segundos al descendiente y lo terminaba durante la recarga de dyld: no representa un bloqueo nuevo del traductor. `run5` dejó completar esa recarga y encontró setsid; `run6` esperó 13 segundos al descendiente y encontró la llamada indirecta. Se conservan todos los intentos en `logs/graphics-008/native-step*/`, sin reemplazarlos por los resultados posteriores.

## Instalador y acceso gráfico

Installer original entró en `0x46ec` en `run6`, después de resolver la biblioteca DesktopServicesPriv y cargar Foundation, AppKit, CoreFoundation, libobjc y libSystem PPC originales. No se creó una ventana. Su bloqueo en BSD 33 (`access`) se resolvió y pasó una prueba directa/indirecta con referencia i386. En `run7` el instalador avanzó hasta **BSD 157 (`statfs`)**, salida 125 sin timeout. Sigue **BLOCKED**, sin ventana. Adaptar statfs exige conservar la ABI PPC32 y describir correctamente el sistema y los volúmenes visibles al instalador; no se respondió con éxito vacío.

`splash` obtuvo realmente el objeto de registro `IOPower:/IOPowerConnection/IOPMrootDomain` mediante RPC 2809. Se detiene en RPC **2815, io_service_open**: el mensaje incluye una capacidad de tarea y necesita un puente explícito a un user client. No se devolvió éxito ficticio.

`ioreg -l` del Darwin real confirma servicios `IONDRVFramebuffer` y `IODisplayWrangler`. La consulta PPC obtuvo un objeto IOFramebuffer, pero no se abrió/mapearon buffers gráficos ni se transportaron píxeles al display. No hubo interfaz del instalador, Aqua ni escritorio Finder. No se ejecutó una instalación ni se proporcionó un disco destino al instalador.

## Evidencia y reproducción

- [Resultados estructurados](../reports/graphics-008/results.json), trazas por ejecutable y comandos exactos: `reports/graphics-008/`.
- Archivo íntegro de resultados de la VM: `logs/graphics-008/native-final.tgz`, `native-followup.tgz`, `native-access.tgz` y sus directorios extraídos. Los ejecutores compilados y los llamadores propios se conservan localmente bajo `build/` y en el overlay; no se incluyen binarios Apple en los archivos versionables del informe.
- [Consola final](../reports/graphics-008/final-console.png): muestra `STEP87_EXPORT_COMPLETE`, sin interfaz gráfica. La VM sigue activa y el FAT quedó desmontado. El inventario [evidence-manifest.json](../reports/graphics-008/evidence-manifest.json) registra SHA-256 de la evidencia y de los archivos locales exportados.
- [Bitmap Quartz fuera de pantalla](../reports/graphics-008/quartz-offscreen.png): salida de la prueba propia usando Quartz original, no una captura de Aqua.
- La receta integrada es `scripts/darwin6-graphics-008-final.sh`, empaquetada por `tools/prepare_graphics_008_payload.py`. La revisión ejecutada antes de incorporar setsid/access se conserva literalmente como [executed-driver.sh](../reports/graphics-008/executed-driver.sh); la receta actual compila su propio probe de procesos y comprueba cada biblioteca añadida. `build/graphics008-current.tgz` contiene las fuentes actuales y los originales locales necesarios, sin sustituir los payloads anteriores.
- Los seguimientos son `scripts/darwin6-graphics-008-followup.sh` y `scripts/darwin6-graphics-008-access.sh`, con sus payloads preservados. Reutilizan las copias de build anteriores y solo recompilan el objeto modificado.
- Para rehacer la prueba hay que montar `/dev/disk1` en `/exchange` dentro del invitado, ejecutar el wrapper existente y esperar `STEP*_EXPORT_COMPLETE`. No escribir al FAT desde el host mientras esté montado por Darwin. No ejecutar `rc.cdrom` completo sobre este entorno de pruebas.

## Bloqueos pendientes y siguiente paso

El siguiente paso de WindowServer es implementar señales PPC con almacenamiento de acciones, captura del evento nativo y entrega al código traducido con contexto y retorno PPC correctos; debe probarse con un llamador propio, señal real y sigreturn. Devolver éxito a sigaction sin entregar señales no resuelve el problema. Después queda el bootstrap global y el IPC de sesión entre procesos; el modelo local actual sigue informando `bootstrap unavailable service=WindowServer`.

Para continuar Installer directamente, el siguiente caso acotado es `statfs` 157 con comparación contra i386, errores reales y metadatos del volumen coherentes. No se debe presentar la raíz extraída como una instalación montada completa.

En paralelo, el primer user client real de IOKit requiere adaptar `io_service_open` (descriptor de tarea, derechos y resultado) y después los métodos concretos del cliente, estructuras endian y memoria compartida/mapas. Consultar el registro o copiar un bitmap de la prueba de Quartz no sustituye ese trabajo.

El ejecutor final nativo es `/var/tmp/graphics008-run7/build/ppc-darwin-user/qemu-ppc`, MD5 `97545406ca149728385b0db865dbe4ee`. El IOKit original del Darwin instalado es FAT i386/PPC, MD5 `c95d76ef4ac6690e048fdd60e05dac35`; el puente comprueba que la imagen cargada en memoria sea CPU 7. Los componentes i386 ejecutaron código i386 directamente, sin traducción PPC; WindowServer, Installer y los frameworks de Jaguar continuaron siendo PPC traducido. El kernel Darwin i386 corre bajo emulación de sistema x86 TCG en esta VM.

Se preservaron 0.06/0.07 y los cambios nuevos. No se hicieron commits ni push automáticos.
