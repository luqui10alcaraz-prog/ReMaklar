# Cargador original y startup PPC

Trabajo experimental en `remaklar/0.02-dyld`, sobre el commit de 0.01
`8fedcc15ebe5ad48d831f97c8006ce50bbee04be`. El ejecutor sigue siendo un
ELF Linux i386 basado en QEMU 0.10.6. No es todavía un ejecutable Darwin.

Checkpoint: commit `df60a2e0f20ccbeb9c37868b23cdf1f4f2edcedf`,
[parche incremental](../patches/qemu-0.10.6/0002-dyld-startup.patch),
[manifiesto](../patches/qemu-0.10.6/dyld-manifest.json) e
[informe de resultados](../reports/remaklar-dyld.json). Aplicar el parche
después de `0001-remaklar-0.01.patch` sobre el tag v0.10.6.

## Ruta de ejecución

Verificado el 23 de octubre de 2026 con compilación incremental y compilación
desde un directorio nuevo: true sale con 0, false con 1, stdout vacío, una
entrada original observada por proceso y `SYS_exit` PPC. Pasan además las
once fixtures estáticas, los dos controles main-only de 0.01 y el control sin
dyld. Los hashes de los cinco archivos originales permanecen iguales.

`qemu-ppc --root research/samples-local research/samples-local/usr/bin/true`
carga el slice PowerPC del archivo FAT, respeta `LC_LOAD_DYLINKER` y empieza
en el `LC_UNIXTHREAD` del `/usr/lib/dyld` original. El propio dyld PPC abre,
mapea, relocaliza y enlaza `libSystem.B.dylib`, que depende de
`/usr/lib/system/libmathCommon.A.dylib`. No se reemplaza el enlazador con un
resolutor de símbolos propio.

El ejecutable conserva su dirección original: entrada `0x195c` para true.
Un breakpoint de observación registra la entrada y se retira antes de
continuar; se vacía la caché TCG para evitar reutilizar el bloque vacío del
breakpoint de QEMU antiguo. La opción `--probe-main` queda separada y no se
utiliza en estas pruebas. La salida se procesa mediante `SYS_exit` emitido
por código PPC, sin interceptar el stub importado de `_exit`.

## Personalidad Darwin mínima

`darwin-user/remaklar/darwin-kernel.c` concentra las adaptaciones Linux:

- Mensajes MIG con campos PPC32 big endian y nombres de puertos virtuales.
- Puertos de tarea, hilo, host, bootstrap, reloj y reply; registro inicial de
  tres puertos nulos. Este modelo no implementa servicios externos.
- Asignación, consulta, protección y liberación de memoria; `map_fd` para
  los segmentos originales. Las asignaciones son privadas, sin shared cache.
- Información del host y de prioridades, política timeshare de un único hilo
  virtual, `HW_NCPU=1` y `HW_VECTORUNIT=0` para PPC750.
- Acceso de lectura a archivos, descriptores de huésped, `stat` de 96 bytes,
  identidad del proceso y traducción explícita de errores BSD.
- Fast traps de thread-self y facilities-used: este último marca FPRs usados
  de forma conservadora para que dyld preserve esos registros; no hay AltiVec.
  Las interfaces desconocidas fallan con un
  diagnóstico; no devuelven éxito genérico.

No es una implementación completa de Mach ni de los syscalls Darwin. Faltan
hilos, señales, muchas políticas VM, servicios bootstrap, escritura general
de archivos y aislamiento de rutas. `--root` sirve para localizar recursos;
no es un sandbox. La pila heredada de QEMU aún referencia cadenas del proceso
anfitrión y requiere revisión antes de ampliar la compatibilidad.

## Reproducir

En PowerShell, `scripts/Prepare-PpcSamples.ps1` comprueba el SHA-256 del CD
y extrae true, false, echo, dyld y las dos bibliotecas. Las muestras proceden
del CD oficial Darwin 6.0.2, no de una imagen retail Jaguar cotejada.

En Ubuntu/WSL con GCC multilib:

```sh
sh scripts/build-qemu-linux32.sh
sh scripts/test-qemu-linux32.sh
sudo python3 tests/ppc/test_dynamic.py
```

El laboratorio dinámico necesita mapear direcciones desde `0x1000` y utiliza
un proceso root en WSL. No se cambia `mmap_min_addr` ni otra configuración del
sistema. Ejecutar únicamente las muestras conocidas. Resolver el espacio de
direcciones sin privilegios es trabajo pendiente. La versión nativa para
Darwin 6 i386 también queda pendiente.

`logs/dynamic-regression/results.json` contiene códigos de salida, hashes de
los cinco archivos originales y comprobación de que no cambiaron. Los logs
por programa registran syscalls, entrada original y traducción PPC→i386.
La prueba negativa usa un root temporal sin dyld y debe fallar antes de la
entrada del ejecutable. `tests/ppc/run_dynamic.py` es un probe de desarrollo;
el verificador que determina éxito o fracaso es `test_dynamic.py`.

## Referencias de implementación

Se consultó código original de Apple en `sources/cctools-435` (tag
`cctools-435`, commit `1b2a137b4ef532a0119577607f67f915e525440a`), especialmente
`dyld`, junto con `sources/xnu-344/osfmk/mach/*.defs`, `vm_statistics.h`,
`host_info.h`, `thread_policy.h`, `bsd/sys/stat.h` y `bsd/sys/sysctl.h`.
No se modificó XNU. Las adaptaciones QEMU mantienen su repositorio y licencia
separados de los scripts y pruebas propios de ReMaklar.

## Fallos encontrados y resueltos

El loader de QEMU omitía `MAP_PRIVATE` al mapear BSS anónimo, rechazado por
Linux. Tras corregirlo, las ejecuciones fueron revelando traps y RPC no
implementados: puertos de Mach, consulta de shared region (solo la consulta),
`vm_region`, `vm_map`, prioridades del host, `thread_policy`, los sysctls de
CPU y el fast trap de facilities-used. Se añadieron sus respuestas explícitas
según las interfaces de XNU; las operaciones fuera del subconjunto siguen
fallando. El breakpoint de entrada también produjo un bucle por reutilizar un
TB vacío: quitar el breakpoint y vaciar los TB resolvió el problema.

Un timeout inicial de 20 segundos interrumpía la prueba al escribir trazas TCG
en el volumen Windows. El verificador final escribe las trazas en un directorio
temporal Linux y las copia al terminar; mantiene un timeout de 120 segundos.
No se alteró código PPC para evitar ninguna de estas etapas.
