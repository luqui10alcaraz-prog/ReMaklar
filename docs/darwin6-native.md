# Laboratorio nativo Darwin 6 i386

## Hito 0.03 conseguido

`true` y `false` originales del mismo CD usado en 0.02 terminan con 0 y 1
dentro del Darwin instalado. Se ejecutan el dyld PPC original, su
autorrelocalización, libSystem y libmathCommon, y la entrada original
`0x195c` de cada ejecutable. La salida es SYS_exit del código PPC; no se usa
`--probe-main`. Las once fixtures mínimas también pasan. El ejecutor es un
Mach-O i386 compilado en el huésped con GCC 2.95.2 y GNU make 3.79.

El runtime está en la rama `remaklar/0.03-darwin6` de su repositorio QEMU.
XNU y las cinco muestras originales permanecen sin modificar. Los hashes
MD5 calculados dentro de Darwin coinciden con los originales del host, cuyos
SHA-256 están registrados en los manifiestos.

## Instalación persistente

Se instaló el CD verificado Darwin 6.0.2 en `vm/darwin602.qcow2` (IDE, 2 GB),
con la opción 1 de particionado automático del instalador. Se instalaron los
216 RPM y el booter original. La imagen pasó `qemu-img check`. Se conserva
una copia offline anterior al primer arranque en
`vm/darwin602-installed-base.qcow2`. Ambas imágenes quedan fuera de Git.

El sistema arranca desde el disco, con raíz UFS `/dev/disk0s2`. El kernel del
RPM instalado informa Darwin 6.0, compilado el 21 de octubre de 2002,
`tmp/xnu-10-2-root.obj/RELEASE_I386`. El kernel del propio CD informaba 6.1 /
344.2.3. No son el mismo binario: no se modificó ni recompiló ninguno.

El arranque multiusuario encontró símbolos CoreFoundation ausentes en
SecurityServer y autodiskmount, y esperó indefinidamente la red. Para este
laboratorio se interrumpe la cuenta atrás del booter con Espacio y se usa
`-s`. Antes de escribir se ejecuta `fsck -y` y `mount -uw /`. No se sustituyen
los servicios ni las bibliotecas para ocultar esos errores.

## Herramientas observadas

La consola instalada informa GCC Apple 1151, basado en GCC 3.1 20020420
(prerelease), con specs en `/usr/libexec/gcc/darwin/i386/3.1/specs`. GNU make
informa 3.79. La cadena de configuración de make menciona PowerPC, por lo que
esa cadena por sí sola no demuestra la arquitectura del slice ejecutado.
El probe `scripts/darwin6-probe.sh` registra compilación, formato y ejecución
de un hello nativo, así como el mapeo bajo con el probe enlazado en dirección
alta para evitar sobrescribir su propio texto Mach-O.

## Intercambio offline

`tools/prepare_darwin_payload.py` genera `build/darwin-payload/source.tgz`
con QEMU, scripts y exactamente las cinco muestras originales utilizadas
en 0.02; registra hashes. No se publican esos binarios.

En WSL, las herramientas de host `mkfs.vfat` y mtools permiten crear un disco
de intercambio FAT16 de 64 MB y copiar `source.tgz`. Arrancar con
`Start-Darwin602.ps1 -Headless -BootDisk -Exchange`, siempre manteniendo el
disco de sistema como IDE 0 y el de intercambio como IDE 1. En el huésped:

```sh
mkdir -p /exchange
mount -t msdos /dev/disk1 /exchange
cd /var/tmp
gnutar xzf /exchange/source.tgz
sh remaklar/scripts/darwin6-baseline-build.sh
```

El script copia los logs a FAT y desmonta el volumen. Solo entonces se leen
o actualizan sus archivos desde el host con mtools. No deben escribir ambos
sistemas simultáneamente sobre el mismo FAT. La red es opcional: con Intel
82557 emulada el driver carga y aparece en0 al activar las personalidades de
IONetworkingFamily y configd, pero no resolvió ARP hacia 10.0.2.2. Se evita
hacer depender la compilación de ese problema.

`tools/guest_keys.py` y `tools/qemu_monitor.py` usan el monitor QEMU ligado
a localhost para teclado y capturas. No son una shell del anfitrión dentro
del invitado. Para apagar, usar `halt` dentro de Darwin y esperar la
sincronización antes de cerrar QEMU. Un reset forzado previo requirió fsck.

## Referencia

Las pruebas dinámicas Linux de 0.02 siguen pasando: true=0, false=1 y control
sin dyld. Se registraron aparte en `logs/linux-reference-0.03`, sin modificar
los informes históricos. El objetivo nativo exige repetir toda la ruta PPC
de dyld y las bibliotecas; un hello i386 o una compilación no acreditan ese
resultado.

## Primer intento real

El primer probe nativo no pudo compilar hello: GCC intenta ejecutar
`/usr/libexec/gcc/darwin/i386/cpp-precomp`, ausente en la instalación. La
primera configuración de QEMU imprime `gcc either does not exist or does not
work`, pero devuelve 0; make falla después porque no hay target generado.
No se debe interpretar ese retorno 0 como una configuración correcta.
Los registros originales están en `logs/darwin6/toolchain.log`,
`configure-baseline.log` y `build-baseline.log`. La resolución usa el preprocesador convencional del GCC2 instalado, como se
detalla a continuación.

## Adaptaciones verificadas

- GCC 3.1 prerelease instalado falla incluso con un hello. GCC 2.95.2 con
  `-no-cpp-precomp` funciona. Se usa PIC normal, `-arch i386` y dependencias
  `-MMD`; se evitan opciones modernas y el GDB stub opcional. El decoder PPC
  se compila con `-O0` para evitar el optimizador antiguo excesivamente lento.
- Se conserva el código CPU/TCG. Se adapta C a GCC2, `va_copy`, los campos
  Darwin de stat y el acceso a envp. Configure ahora conserva el error al salir.
- El ejecutor reserva las direcciones bajas con `__STD_PROG_ZONE`, antes de
  las asignaciones de dyld nativo, y coloca su texto en `0x20000000`. El probe
  confirma mmap en `0x1000`, sin cambiar XNU. La alineación de segmentos es 4 KB.
- GCC2 no respeta el regparm del puntero de función del prologue TCG. Una
  entrada asm específica de Darwin coloca el TB en EAX. Antes de corregirla,
  las once pruebas terminaban en fault; después pasan.
- Darwin 6 i386 no entrega un ucontext moderno con dirección de fault. Se
  usa su ABI real sigaction/sigcontext/sigreturn. Un puente mínimo reconoce
  exclusivamente stores MOV generados por TCG y recupera páginas originalmente
  escribibles protegidas por la caché de traducción, invalidando sus TB.
  Esto permite la autorrelocalización del dyld PPC desplazado por el dyld
  nativo. Otros faults terminan en 126 con registros diagnósticos.

El dyld PPC se desplaza en esta ejecución de `0x8fe190f0` a `0x8fe960f0`.
Su store sobre `0x8fe960fc` provocaba el fallo del intento 017. El intento 018
recupera esa escritura y completa ambas entradas originales en `0x195c`.
El intento 019 recompila desde un directorio nuevo el commit QEMU publicado
como parche 0003 y repite todas las pruebas correctamente.

## Reproducir el hito

En un checkout nuevo, `sh scripts/checkout-qemu.sh` aplica por defecto los
parches 0001, 0002 y 0003. Los checkpoints anteriores siguen seleccionables
con REMAKLAR_CHECKPOINT. Se necesitan localmente el CD verificado y las cinco
muestras de 0.02; no se redistribuyen en el repositorio.

1. Generar las fixtures con `python tests/ppc/make_fixtures.py` (ver el script
   de pruebas Linux si cambia su interfaz), y `python tools/prepare_darwin_payload.py`.
2. Copiar `build/darwin-payload/source.tgz` al FAT16 de intercambio con mcopy,
   mientras esté desmontado en Darwin. Conservar un solo escritor por volumen.
3. Arrancar con `scripts/Start-Darwin602.ps1 -BootDisk -Headless -Exchange`,
   interrumpir el booter y escribir `-s`; ejecutar fsck y montar raíz escribible.
4. Montar `/dev/disk1` en `/exchange`, extraer source.tgz en `/var/tmp`, y ejecutar
   `sh remaklar/scripts/darwin6-build.sh`. Configura, compila, ejecuta las once
   fixtures y true/false y copia los logs a FAT antes de desmontarlo.
5. Exigir `BUILD_ITERATION_COMPLETE status=0`, `failed=0`, true=0 y false=1.
   La prueba exige entrada original, SYS_exit y ambas bibliotecas, stdout vacío,
   y ausencia de puente main-only o llamadas sin implementar.

Para repetir sin recompilar: montar FAT, ejecutar
`sh /var/tmp/remaklar/scripts/darwin6-run-tests.sh`, sync y desmontar FAT.
Para una traza TCG copiar darwin6-trace.sh al disco raíz y ejecutarlo con
`exit42`, `true` o `false`; exporta también el ejecutor propio. No ejecutar
ese script directamente desde FAT porque su descriptor abierto impide desmontar.

El reloj del invitado puede atrasarse bajo TCG y make advertir clock skew.
El formato de date antiguo es YYmmddHHMM.SS; sincronizar después de extraer.
Un cierre forzado durante el desarrollo requirió fsck y reconstrucción en un
árbol nuevo por objetos dañados. Usar halt, esperar CPU halted y cerrar QEMU.
El qcow2 pasa qemu-img check. El launcher usa cache=writethrough para raíz:
cache=directsync produjo un falso rechazo de formato qcow2 en este QEMU Windows;
el FAT raw sí utiliza directsync. No se cambiaron datos para ocultar el error.

La repetición tras arranque en frío también pasa las once fixtures, true y false.
En ese fsck se corrigió un contador de enlaces de directorio; no se detectaron
de nuevo los objetos inválidos anteriores. El cierre final terminó en CPU halted.
Se guarda offline `vm/darwin602-native-003-verified.qcow2`, fuera de Git.

## Evidencia y límites

[Informe 0.03](../reports/remaklar-0.03.json),
[logs nativos](../reports/darwin6/tests-019.log),
[build limpio](../reports/darwin6/build-019.log) y
[manifiesto del parche](../patches/qemu-0.10.6/darwin6-manifest.json).
Se conservan los fallos 016/017 y el éxito 018 además del 019. Los logs Linux
registran trece regresiones estáticas/main-only y tres dinámicas correctas.

El cambio QEMU permanece separado del código propio y conserva su licencia.
La referencia del ABI de señales se cotejó con Apple Libc-262, commit
`e6868d771bc072eb29ebc069d4b7bb0cb027a2c2`. No se implementaron señales Unix
PPC generales, threads ni compatibilidad completa de aplicaciones. El fault
negativo de memoria devuelve 126 nativo y 125 en Linux: ambos rechazan la
muestra, por caminos distintos. Las muestras provienen del CD Darwin original;
no se ha cotejado todavía su identidad con un Jaguar retail.
