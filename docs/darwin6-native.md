# Laboratorio nativo Darwin 6 i386

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
`configure-baseline.log` y `build-baseline.log`. Se investigará primero el
preprocesador convencional del mismo GCC, sin instalar un compilador moderno.
