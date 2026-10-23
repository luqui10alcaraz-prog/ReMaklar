# Darwin 6.0.2 x86: consola reproducida

Fecha de prueba: 2026-10-23. Resultado: dos arranques en frío hasta una shell del CD, con la imagen original sin parches. No se realizó instalación en disco.

## Obtención y verificación

Se descargó directamente por HTTPS desde Apple:

https://opensource.apple.com/static/iso/darwinx86-602.iso.gz

El servidor devolvió HTTP 200, 330284411 bytes y `x-amz-meta-s3cmd-attrs: md5:d4e9a94c48d900736fa9f77d42707d50`. El MD5 local coincide. Se conservaron las cabeceras en `logs/darwin-download-headers.txt`.

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| `media/darwinx86-602.iso.gz` | 330284411 | `db18cb67aab1caab3bd420faf4f956f909be9ead9f2b5e19757429321084b807` |
| `media/darwinx86-602.iso` | 558481408 | `d2c4668dcd4ca4a7498acffaf703a19862f53ab9b58b06c51745bd33e58a584f` |

La procedencia directa de Apple y la coincidencia con su metadato MD5 respaldan la identificación de esta copia. No se encontró una firma digital ni se cotejó con un checksum publicado en 2002. El gzip se descomprimió y la ISO se pudo listar con `tar`; inventario en `logs/iso-files.txt`.

Importante: aunque el archivo se llama 6.0.2, el kernel incluido informa Darwin 6.1 / XNU 344.2.3. Además, `Release Notes.txt` conserva texto de Darwin 1.4.1; esas notas obsoletas no deben usarse como identificación del medio. Ambos hechos se observaron directamente en la imagen servida por Apple.

## Repetir

Desde PowerShell, en `H:\ReMaklar`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-Darwin602.ps1
```

El bypass se aplica solo a ese proceso, sin cambiar la política persistente de Windows. El lanzador verifica el SHA-256 de la ISO y crea el disco de 2 GB únicamente si no existe. Para ejecución sin ventana, agregar `-Headless` (modalidad usada en las dos pruebas).

1. Esperar el arranque automático del CD y el prompt `Which device would you like to install Darwin onto?`. Puede demorar varios minutos con TCG y los timeouts PS/2.
2. Escribir `shell` y pulsar Enter. Esta opción está implementada en el script original `private/etc/rc.cdrom`; evita comenzar la instalación.
3. Ejecutar `uname -a`, `arch`, `mount` e `iofindwholemedia`.
4. Cerrar QEMU al finalizar. El disco de laboratorio todavía está vacío.

La configuración validada es `pc-i440fx-5.0`, TCG, Pentium III, 1 CPU, 128 MB, VGA estándar, disco IDE índice 0, CD IDE índice 2 y sin tarjeta de red. No fue necesario especificar `rd=` ni modificar la ISO. El puerto de monitor 4444 está ligado únicamente a localhost; no lanzar dos instancias simultáneamente.

QEMU instalado: `10.1.94 (v10.2.0-rc4-12104-gb2a6201393)`. Versiones y hashes están en `darwin602-artifacts.json`. QEMU advierte que la máquina 5.0 está obsoleta; no se probó todavía una versión estable alternativa. Un intento preliminar con máquina 2.0 fue rechazado porque esta versión de QEMU ya no la incluye.

## Resultados observados en ambos arranques

```text
sh-2.05a# uname -a
Darwin localhost 6.1 Darwin Kernel Version 6.1: Fri Sep 13 13:57:44 PDT 2002; root:xnu/xnu-344.2.3.obj~3/RELEASE_I386  x86 i386
sh-2.05a# arch
i386
sh-2.05a# mount
root_device on / (local, read-only)
devfs on /dev (local)
sh-2.05a# iofindwholemedia
1. QEMU HARDDISK 0 ( disk0 (2.0 GB))
```

Evidencia visual: `logs/console-devices.png` y `logs/console-repeat.png`. El kernel identificó el CD como `disk1s0` y los canales IDE como PIIX3. Hubo advertencias `Unrecognized processor` y `ApplePS2Controller: Timed out on mouse input stream`; la consola siguió funcionando. No se validó el mouse. La consola usa VGA: `logs/serial.log` quedó vacío y no es evidencia de salida del invitado.

`scripts/Send-DarwinKeys.ps1` permite enviar texto mediante el monitor local en modo headless, con un conjunto limitado de caracteres. Fue usado para la segunda prueba; las capturas se obtuvieron con el comando de monitor `screendump ... -f png`.

## Siguiente hito

Instalar en el disco virtual, comprobar arranque sin CD y registrar las herramientas disponibles. La consola actual ejecuta el entorno del instalador desde CD; no acredita todavía un sistema instalado ni una compilación propia de XNU.
