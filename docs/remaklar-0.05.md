# ReMaklar 0.05: filesystem y preparación Objective-C

`ls` y `pwd` originales pasan diez casos en Linux i386 y Darwin 6 i386.
Una prueba PPC propia añade 17 etapas de operaciones BSD controladas. Se
conservan los 23 casos de echo/cat, las 16 regresiones Linux y las once
fixtures más true/false nativos. XNU y los originales permanecen intactos.

La primera prueba Objective-C se compiló dentro de Darwin con su GCC2 y
produce un Mach-O PPC. Carga las bibliotecas originales y alcanza una llamada
no implementada: `ptrace`, syscall 26, petición `0xc000`. Se registra como
**ejecución bloqueada**, no como Objective-C funcional.

## Cobertura del sistema de archivos

| Prueba | Comportamiento verificado en ambos hosts |
| --- | --- |
| pwd, tres casos | Raíz virtual, ruta anidada, normalización de padre |
| ls, siete casos | Nombres, ocultos, tipos, 300 entradas, metadatos numéricos y fecha, symlink, inexistente |
| Probe PPC propio | mkdir, umask, creación exclusiva, write/read binarios, lseek, fstat/stat, chmod, append, close/EBADF, rename, chdir relativo, unlink/rmdir y ENOENT/ENOTEMPTY |

Las salidas deterministas se comparan byte a byte. Los metadatos variables se
comparan con stat/lstat del host sobre las mismas fixtures, incluidos modo,
enlaces, UID, GID y tamaño. La fecha de prueba se fija a 2001-01-01 UTC.
Linux ejecuta las pruebas de permisos en una copia temporal sobre su filesystem
nativo: los modos de archivos del montaje Windows no son una referencia Unix
equivalente. Esto verifica bits de permisos; no acredita todos los controles
de acceso para usuarios sin privilegios.

En Darwin el primer caso de symlink esperaba erróneamente 0777, pero UFS creó
el enlace con 0750. Se corrigió la expectativa para comparar lstat real en
ambos hosts, manteniendo la exigencia del tipo, tamaño y destino. Se conserva
el informe inicial fallido. El resultado final es once casos, cero fallos y
cero directorios de trabajo sobrantes creados por el probe.

El ls histórico imprime ENOENT y devuelve **0**: el fuente file_cmds-60/ls/ls.c
termina en exit(0). La prueba exige tanto ese estado como el diagnóstico.
No se cambió el ejecutable para darle el comportamiento de un ls moderno.

## Cambios del ejecutor

- Cwd virtual, `--cwd /ruta`, rutas relativas y normalización léxica de `.`
  y `..` con límite en la raíz. Getcwd sigue ejecutándose en libSystem PPC;
  no se sustituye por una cadena de respuesta del host.
- Un solo mapa de descriptores para read/write/open/close, también para
  archivos creados por el invitado. Traducción explícita de flags Darwin.
- Entradas de directorio PPC32: inode32, reclen16, type8, namelen8 y padding
  a cuatro bytes. No se copian estructuras dirent de Linux/i386 como PPC.
- Stat, timeval, readlink y consultas de terminal traducidos en la frontera
  BSD. La consulta termios en un archivo regular devuelve ENOTTY; no se
  simula un terminal completo.
- Fstatfs expone un perfil de filesystem invitado no union, con capacidad del
  host. No pretende reproducir todos los flags y tipos del filesystem real.
- Lseek usa el ABI Jaguar PPC32 observado: offset r4:r5 y whence r6, resultado
  r3:r4. La suposición inicial de un registro de padding era incorrecta.
- Las escrituras del puente sobre páginas originalmente escribibles
  desprotegen primero la caché TCG e invalidan sus traducciones. La prueba
  propia reproduce ese camino al leer en una página RWX ya traducida.

Persisten límites: resolución léxica, sin semántica completa para directorios
symlink seguidos de `..`; cursores de directorio locales y seek solo a inicio;
subset de open/fcntl/ioctl; sin hilos y señales generales. La raíz virtual es
un modelo de compatibilidad y no un chroot completo.

## Reproducción

`scripts/checkout-qemu.sh` aplica los parches 0001–0004 por defecto, conservando
los checkpoints anteriores. El parche de filesystem está separado del código
propio y conserva la licencia de QEMU.

```sh
python3 tests/ppc/make_fixtures.py
python3 tests/ppc/make_utility_cases.py
python3 tests/ppc/build_filesystem_probe.py
```

El último paso usa los cross-binutils PPC ya disponibles en el host para
ensamblar **solo código de prueba propio** y empaquetarlo como Mach-O. No se
convierten ni modifican los ejecutables originales. Para Linux, compilar con
los scripts habituales y ejecutar `tests/ppc/run_filesystem.pl executor
guest-root build/filesystem-probe.macho output-dir` sobre una copia temporal
del árbol de muestras en un filesystem Unix.

Para Darwin: extraer los originales con Prepare-PpcSamples.ps1, preparar
source.tgz con `tools/prepare_darwin_payload.py`, y usar el intercambio FAT
descrito en [0.03](darwin6-native.md). Con FAT montado y raíz escribible:

```sh
cd /var/tmp
gnutar xzf /exchange/source.tgz
sh remaklar/scripts/darwin6-filesystem.sh > /var/tmp/fs-run.log 2>&1 &
```

El script configura/compila, repite las regresiones, corre las pruebas nuevas
y el probe Objective-C, y exporta fs.tgz antes de desmontar FAT. El bloqueo
Objective-C se registra por separado y no se considera una regresión que pasa.
La compilación medida de 0.05 fue incremental sobre el build nativo de 0.03;
no se afirma una segunda compilación limpia de todo QEMU.

La copia `vm/darwin602-filesystem-005-verified.qcow2` se guardó después de halt.
Qemu-img check no encontró errores. Los respaldos 0.03 y 0.04 conservan sus
SHA-256 anteriores. Imágenes, bibliotecas y ejecutables Apple siguen fuera de Git.

## Evidencia

[Informe verificable](../reports/remaklar-0.05.json),
[pruebas finales Darwin](../reports/filesystem/native-filesystem.txt),
[registro de servicios](../research/services-0.05.json) e
[investigación Objective-C/CoreFoundation](../research/jaguar-runtimes.md).
La procedencia es el CD Darwin 6.0.2; todavía no se ha cotejado con Jaguar retail.
