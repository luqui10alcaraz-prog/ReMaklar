# ReMaklar 0.01 — ejecutor PPC experimental

Fecha: 2026-10-23. Se implementó y compiló un ejecutor Linux i386 basado en QEMU 0.10.6, target `ppc-darwin-user`. Ejecuta fixtures Mach-O PPC32 estáticos mediante TCG y ejecuta el cuerpo main de true/false originales de Apple mediante un puente explícito de exit.

**No se completó todavía el hito de ejecutar un programa original desde su entrada normal con dyld e inicializadores. Tampoco se ha compilado ni ejecutado el adaptador dentro de Darwin 6.** Los originales utilizados provienen del CD oficial Darwin 6.0.2, no de una instalación Jaguar retail cotejada.

## Código y versiones

- Repositorio independiente: `experiments/qemu-0.10.6`.
- Rama: `remaklar/0.01`.
- Base upstream: `9eab386edbf8cf002a731f8204a156f243a47a57` (`v0.10.6`).
- Commit experimental: `8fedcc15ebe5ad48d831f97c8006ce50bbee04be`.
- Parche: `patches/qemu-0.10.6/0001-remaklar-0.01.patch`, con manifest y SHA-256. Se comprobó que puede revertirse limpiamente contra el árbol experimental.
- Implementaciones propias externas: `tools/`, `tests/ppc/`, `scripts/`. Los binarios extraídos se guardan en `research/samples-local/`, excluido por gitignore.

Se conservaron el frontend/decodificador PPC, helpers de CPU, softfloat, runtime y caché de bloques, TCG i386, cargador Mach-O y mmap de QEMU. No se implementó un decodificador ni intérprete PPC nuevo. No se modificó XNU, ni se agregaron máquinas PPC o dispositivos al ejecutor.

El adaptador Linux usa un main propio y definiciones Mach-O wire mínimas. El build Darwin conserva el main, syscalls, señales y commpage históricos como punto de partida, todavía sin validar. No se añadieron GLib, Meson ni otras bibliotecas nuevas.

## Entorno de compilación

Windows con Ubuntu 24.04 bajo WSL2, CPU host x86_64, GCC 13.3.0 con bibliotecas de desarrollo multilib ya instaladas y GNU make. El resultado es un **ELF i386 de 32 bits**, no un Mach-O i386; no puede copiarse a Darwin y ejecutarse directamente. Python 3 estándar se usa únicamente para herramientas y generación de pruebas en el host, no como dependencia del ejecutor.

El configure fija `--cpu=i386` y `-m32`, evita PIE y usa opciones de compatibilidad con este código antiguo. Se desactivan builtins, vectorización y protecciones de stack/FORTIFY del compilador moderno en este bootstrap; son opciones del laboratorio, no una configuración de distribución. El script nativo preparado no traslada esas opciones modernas a GCC histórico.

## Errores reales y adaptaciones

| Etapa | Fallo observado | Cambio |
|---|---|---|
| Preparación Windows/WSL | checkout con CRLF impedía ejecutar configure | Árbol de trabajo con LF; checkout reproducible con autocrlf desactivado |
| Primer configure | opciones modernas como disable-cocoa/disable-docs no existían | Usar únicamente las opciones presentes en 0.10.6 |
| Primer build | falta qemu-types.h y headers mach/message.h en Linux | Tipos ABI Darwin y adaptador Linux separado; conservar integración Darwin original |
| Loader | disas_symtab se había convertido en union y requería callback | Campo Mach-O y búsqueda de símbolos adaptados al runtime de esa revisión |
| Runtime | lock_user usaba firma de tres argumentos; faltaban last_brk y hooks mmap | Alinear API con el runtime de cuatro argumentos; controles de rango; ejecución declarada monohilo |
| glibc | struct ucontext ya no existe con ese nombre | Usar ucontext_t en las rutas Linux afectadas |
| Helper AltiVec | GCC: frame pointer required, but reserved | Opciones bootstrap sin expansión de builtins/hardening incompatibles con el registro EBP reservado; no se reescribió el helper |
| Depurador | TARGET_SIG* ausentes al construir gdbstub | Desactivar servidor GDB en el bootstrap Linux; conservar trazas TCG y breakpoints internos |
| Enlace | faltaban qemu_malloc, qemu_vmalloc, pstrcpy y registro de coprocessor del debugger | Enlazar objetos upstream qemu-malloc/osdep/libqemu_user y omitir solo el registro de descripción de GDB no utilizado |
| Verificación forzada | make -B propagado al submake recreaba libqemu_user.a mediante una regla genérica vacía | Forzar el archivo común desde su Makefile propietario y excluirlo de la reconstrucción forzada del submake; el build normal desde cero ya había pasado |

Se conservan los logs de los intentos en `logs/qemu-configure-*.log`, `logs/qemu-build-*.log` y la inspección del compilador en `logs/toolchain-inspect.log`. Algunos logs tempranos fueron capturados por PowerShell y contienen su formato/encoding; los actuales se escriben directamente desde el shell Linux.

Cambios funcionales adicionales: MAP_PRIVATE para segmentos de archivo, inicialización de cpu_model en el main histórico y controles básicos de tamaño/rango de Mach-O/FAT, segmentos, comandos, thread state y símbolos. Esto no convierte al cargador histórico ni al ejecutor en un sandbox para binarios arbitrarios.

## Pruebas verificadas

| Prueba | Resultado esperado y observado |
|---|---|
| exit42 | Salida de proceso 42 mediante SYS_exit Darwin |
| write | stdout exacto `ReMaklar PPC -> Intel` seguido de newline; exit 0 |
| write-ebadf | errno Darwin 9 y ruta de error posterior a sc; exit 0 del test |
| write-efault | errno Darwin 14 para buffer inválido; exit 0 del test |
| load-be | lwz interpreta los bytes ReMa como 0x52654d61; exit 0 |
| unsupported-syscall | Rechazo explícito de syscall 999; exit 125 |
| illegal-instruction | Excepción PPC y diagnóstico; exit 125 |
| memory-fault | Carga PPC desde memoria no mapeada termina con excepción PPC; exit 125 |
| truncated | Rechazo de header incompleto; exit 125 |
| bad-command | Rechazo de cmdsize cero; exit 125 |
| needs-dyld | Rechazo explícito de integración dinámica aún no implementada; exit 125 |
| Apple true, main-only | Instrucciones PPC originales llegan al puente exit con 0 |
| Apple false, main-only | Instrucciones PPC originales llegan al puente exit con 1 |

Los once fixtures son programas propios de prueba, no originales de Jaguar. Cada ejecución usa proceso separado, timeout y entorno controlado (locale C, TZ UTC). Se comprueban stdout, exit y un diagnóstico esperado para evitar que un fallo de carga pase por una excepción esperada.

Evidencia: `logs/ppc-fixtures/results.json`, stdout/stderr y trazas por caso; `logs/original-main/results.json` y sus trazas PPC/i386. Se repitieron las 13 pruebas con un build desde un directorio vacío, `build/qemu-linux32-clean`, sin reutilizar objetos. Las direcciones de stack/JIT pueden variar entre ejecuciones. El registro consolidado de toolchain, hashes y resultados está en `reports/remaklar-0.01.json`.

## Qué prueba realmente la muestra original

El ISO verificado contiene binarios universales PPC+i386, incluidos true, false, echo y dyld. Se extrajeron sin modificar el CD. Inventario: `research/inventory/*.json`; el CD también contiene `shell_cmds-34-1.ppc.rpm`, `Csu-45-1.ppc.rpm`, `Libc-262-1.ppc.rpm`, `Libsystem-60-1.ppc.rpm`, `cctools-435-1.ppc.rpm` y `gcc3-1151-1.ppc.rpm`.

true/false no conservan un símbolo main utilizable. La prueba identifica una secuencia completa y única de cinco instrucciones, contrasta su argumento 0/1 con el fuente y verifica que su branch relativo llega al stub de `_exit` identificado por la tabla de símbolos indirectos. No usa un offset adivinado como única evidencia.

En ambas muestras main está en 0x1d60 y el stub exit en 0x1d74. El loader selecciona el slice PPC del archivo FAT intacto y aplica slide 0x10000000 solo para esta prueba. No se aplican relocaciones generales: la ruta ejecutada no las necesita. Se omiten dyld y startup explícitamente, se inicia la CPU en main y un breakpoint interno en el stub despacha exit al host. Ninguna instrucción del main se sustituye ni se recompila desde C.

La traza de true muestra:

```text
0x10001d60: mflr r0
0x10001d64: li r3,0
0x10001d68: stw r0,8(r1)
0x10001d6c: stwu r1,-80(r1)
0x10001d70: bl 0x10001d74
```

Después registra el bloque i386 emitido por TCG y la llegada al puente con status 0. false ejecuta la variante original con `li r3,1`. Esto prueba traducción de código original, no funcionamiento de sus dependencias ni compatibilidad completa del proceso.

SHA-256 de los slices PPC:

- true: `9775ffe63f16a5b1fc89c599efe6d75e6a7749611cce06c25660a19457714653`.
- false: `a6773165fcb5124a8f230c7ad90714db1cfb9b1e14760fff4caf0bbf755bdfba`.

## Reproducir desde Windows

En `H:\ReMaklar`, con Ubuntu WSL y GCC multilib disponibles:

```powershell
# Solo si se necesita crear de nuevo el checkout experimental:
wsl.exe -d Ubuntu -- sh /mnt/h/ReMaklar/scripts/checkout-qemu.sh

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Prepare-PpcSamples.ps1
wsl.exe -d Ubuntu -- sh /mnt/h/ReMaklar/scripts/build-qemu-linux32.sh
wsl.exe -d Ubuntu -- sh /mnt/h/ReMaklar/scripts/test-qemu-linux32.sh
```

El checkout se niega a reemplazar una carpeta existente. El script de extracción verifica el hash de la ISO. Los fixtures se generan con la biblioteca estándar de Python, sin ensamblador PPC externo. `verify-clean-build.sh` sirve para una comprobación desde un directorio de build nuevo y se niega a reutilizarlo silenciosamente.

Ejecutor habitual: `build/qemu-linux32/ppc-darwin-user/qemu-ppc`. Ejecutar un fixture mediante WSL:

```powershell
wsl.exe -d Ubuntu -- /mnt/h/ReMaklar/build/qemu-linux32/ppc-darwin-user/qemu-ppc /mnt/h/ReMaklar/build/fixtures/write.macho
```

La reproducción conserva resultados semánticos y versiones; no se afirma reproducibilidad bit a bit del ELF entre rutas/toolchains diferentes.

## Límites y siguiente trabajo

La cobertura del adaptador Linux es SYS_write/SYS_exit y el puente exit del modo de prueba. Traps Mach, commpage, syscalls adicionales, dyld, bibliotecas PPC, señales del invitado, threading y relojes PPC no están implementados en ese adaptador. Los accesos a timebase terminan explícitamente con diagnóstico. Los hooks de locking son monohilo. La pila de arranque aún conserva supuestos del código histórico: no está validada como contrato completo Jaguar.

Próximo hito de compatibilidad: cargar dyld/dependencias en su espacio invitado, resolver startup/relocaciones y ejecutar true desde su LC_UNIXTHREAD normal, sin `--probe-main`. Antes deben resolverse también las direcciones bajas que usa el binario original frente a las restricciones de mmap del host Linux. El slide de la prueba aislada no es un relocador general.

Integración Darwin posterior:

1. Instalar el sistema persistente, inventariar GCC3-1151/cctools-435, headers y bibliotecas del CD. Compilar un programa i386 mínimo.
2. Transferir fuentes/parche y fixtures por un medio de solo lectura; Python no es necesario en el invitado.
3. Probar mmap/mprotect ejecutable y manejo de contexto de señales Darwin 6.
4. Intentar el configure preparado en `scripts/configure-qemu-darwin6.sh`; capturar errores reales. Revisar SDK posterior, GDB, commpage y el marshalling de syscalls del código histórico. No asumir que se arreglaron por haber construido el bootstrap Linux.
5. Repetir fixtures y main-only dentro de Darwin con el adaptador correspondiente. Solo después anunciar esa plataforma como soportada.

No es necesario modificar el kernel para comenzar estos pasos. Las versiones nativas de componentes siguen una vía separada, guiada por fuentes e interfaces, sin convertir automáticamente descompilados.

## Licencias

Se preservan COPYING, COPYING.LIB y avisos upstream. El adaptador y definiciones nuevas dentro de QEMU llevan GPL-2.0-or-later; los cambios a archivos existentes conservan sus avisos y condiciones. Las herramientas propias externas llevan MIT. Esto no relicencia QEMU completo ni los archivos de Apple. El parche no incluye los binarios originales extraídos.
