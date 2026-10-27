# ReMaklar 0.11: entrada e Installer después de window102

El estado window102 conserva la primera ventana auténtica, con el rechazo «This software cannot be installed on this computer». La investigación posterior usa copias nuevas; el BAT de prueba sigue apuntando a window102 hasta verificar un checkpoint interactivo nuevo.

## Installer y entorno original

El árbol parcial de Jaguar no contenía `/System/Installation/Packages/OSInstall.mpkg`. Se extrajo el árbol **completo y original** del CD Jaguar: 1113 entradas, 401831062 bytes de archivos, con permisos y enlaces. `tools/prepare_graphics011_packages104.py` crea el ISO de datos de solo lectura. El manifiesto por archivo está en `reports/graphics-011/resume-validation/packages104-original-cd-manifest.json`.

Con el paquete disponible, el Installer llega a la enumeración real de discos y expone dos llamadas IOKit pendientes: `io_make_matching` (2835) y `io_registry_entry_get_name_in_plane` (2843). Los parches0040/0042 delegan ambas al IOKit y kernel originales. Pruebas nativa/PPC y ejecutores anteriores negativos: matching112, build113 y setup130. El nombre BSD del disco de trabajo cambia en el arranque frío: setup130 pasa `disk2s1` explícitamente al oráculo, en lugar del `disk1s1` antiguo.

Además faltaba `/dev` en el árbol de Jaguar. Se montó el **devfs original del kernel** en ese directorio mediante `tests/native/mount-devfs011.c`; el CD Darwin carece del ayudante `/sbin/mount_devfs`. No se fabricaron nodos ni contenido de dispositivos. Setup127 falló por directorio ausente; setup129 montó devfs y luego falló al compilar con cabeceras incompletas; setup130 completó la preparación y la comparación de nombres.

Con `/dev/null` real, WindowServer alcanza `dup2` (syscall90), antes ausente. El parche0044 duplica descriptores reales dentro de la tabla de descriptores invitados sin reemplazar descriptores internos del ejecutor. La prueba dup131 verifica reemplazo, offsets compartidos, CLOEXEC, EBADF sin dañar el destino, cierre del origen y redirección de stdin/stdout/stderr. Nativa y PPC terminan0 con salida idéntica; el ejecutor122 anterior termina125. La duplicación de un cursor de directorio abierto sigue cerrándose con un diagnóstico explícito.

## Entrada real

En el estado inicial faltaba cargar ApplePS2Mouse original. Cargarlo produjo IRQ12 y eventos reales, pero el oráculo i386 también mostró deltas incorrectos y liberaciones perdidas. La descarga nativa del kext quedó bloqueada: checkpoint `input120-kextunload` preservado. No se atribuye ese fallo al traductor.

Se ensayó un OHCI y mouse USB reales emulados, con AppleUSBOHCI/IOUSBHIDDriver originales. El primer oráculo i386 (input123/n1, VMusb121) produjo un trap0 en IOHIDFamily1.2: EIP31a1866f. Se conserva RAM comprimida, discos inmóviles, captura, bytes del kext cargado y hashes en `usb121-native-panic-preserved.json`. La pila y el código sitúan el divisor cero en la construcción de segmentos de aceleración; la tabla USB contiene valores de16bits en orden big endian y `Fetch32` del driver i386 los lee directamente. La interpretación incorrecta de la tabla es la causa probable; no se modificó el driver.

En la copia fría usb126 se fijaron las preferencias reales `HIDPointerAcceleration`, `HIDMouseAcceleration`, `HIDScrollAcceleration` a -65536 mediante `IORegistryEntrySetCFProperties` original. Esto desactiva la aceleración por la vía admitida por el controlador. La herramienta usa declaraciones públicas del ABI de CoreFoundation porque el SDK Darwin instalado omite cabeceras Carbon.

Los parches0039/0041/0043 tipan las variantes reales del anillo IOHID: teclado, mouse y evento auxiliar type14/subtype7. No publican eventos inventados. Los subtipos desconocidos permanecen sin admitir.

Input123 verifica, después de observar READY, hardware QEMU real: tecla a, movimiento(10,5), botón abajo, arrastre(1,0), botón arriba, movimiento(1,0). Resultados:

- n2, i386 original: exit0, cursor(16,16)→(28,21), dos eventos de teclado, cinco de mouse y dos auxiliares.
- p1, PPC con ejecutor113 anterior a0043: exit125 ante la unión auxiliar, offset606/width2.
- j1, PPC con ejecutor122/0043: exit0, cursor(38,26)→(50,31), misma secuencia y datos que el oráculo nativo salvo la ubicación inicial.

`tools/verify_graphics011_input123.py` comprueba los resultados guardados y dup131. **Esto acredita entrada real en el traductor; el movimiento del cursor visible en Aqua se verifica por separado.**

La cadena0022–0043 se reprodujo desde `build/011-vmcopy-patch-check`, verificando18 hashes (`chain21-through43-reproduction.txt`). Cada delta tiene manifiesto y copia aislada.

## Estado de recuperación

VM activa usb126, monitor4454, 512MB, Darwin6 original, OHCI original. Discos nuevos `vm/darwin602-graphics-011-usb126.qcow2`, `vm/graphics011-usb126-work.qcow2`; FAT `build/graphics011-usb126-exchange.img`; CD `build/packages011-104.iso`. Raíz disk0s2, trabajo disk2s1, FAT disk1, CD disk3s0. Montaje de paquetes `/var/tmp/jaguar/Volumes/CD104`, devfs `/var/tmp/jaguar/dev`. Los hashes MD5 del kernel y del Installer siguen siendo56da829d60b6b4353c25cca8b060b5f8 y1496d181829e74bd60de5fd3f9222185.

Joint125 se detuvo por syscall90 sin admitir; harness terminó y exportó trazas. Joint132 repite los servicios originales con ejecutor131/0044, presupuesto72 muestras de5segundos invitados y capturas acotadas. Su resultado debe consultarse en `reports/graphics-011/joint132`, sin inferir una ventana a partir de la heurística del capturador.

## Avance hasta los ensayos138–140

Joint132 terminó por un error real ENXIO al abrir `/dev/tty` en una sesión sin terminal de control; faltaba mapear ese errno. El parche0045 conserva ENXIO6. Enxio133 compara la apertura nativa/PPC de devfs: `/dev/null` abre, `/dev/tty` falla con ENXIO dos veces; ambos terminan0, el ejecutor previo termina125.

En joint134 el puntero Aqua original **se movió realmente** al enviar `mouse_move 40 30`. `pointer134-framebuffer-verification.json` verifica los97 píxeles originales desplazados exactamente40,30 y la igualdad de los786432 píxeles de cada captura con la VRAM física. Las capturas están en `joint134/captures/1793076709806847518.png` y `1793076731754132378.png`. Moverlo expuso otra lectura de unión sin tipar y el harness terminó. No se publicó aún un checkpoint interactivo actualizado para el BAT.

El parche0046 corrige los cinco flags con nombre de EvGlobals: la implementación anterior rotaba el grupo, pero el ABI exige invertir el orden de esos cinco bits y preservar el valor del reservado27. Un oráculo compilado con GCC2 i386 usa los campos C originales por nombre. Se agregó también la unión tracking de eventos8/9. Build135 pasa seis pruebas nativas, incluida la prueba concurrente de memoria compartida. Input136 n1/j1 produce la misma secuencia real con evento9 de salida del rectángulo, clic completo y flags liberados; el ejecutor133 anterior produce cero salidas y termina8. `tools/verify_graphics011_input136.py` verifica esa comparación. La cadena0022–0046 reproduce18 hashes.

Joint137 diagnosticó concretamente una ranura **type0**, no un evento9: `native HID unsupported union slot=1 type=0 subtype16=0`, seguido del rechazo de offset352/width4. El Installer abortó después de perder el servidor gráfico; no alcanzó una comprobación nueva de instalación. El proceso557 era el **DMProxy original** creado por WindowServer, con ruta y execve en la traza.

El parche0047 permite leer una unión type0 únicamente cuando los48 bytes nativos son cero; no genera un evento ni inventa su contenido. Los type0 no cero y las variantes desconocidas siguen rechazándose. Build138 compila el parche y comprueba la unión de una ranura inicializada por el **IOHIDSystem original**, con oráculos i386/PPC y negativo del ejecutor135. Joint140 está preparado para repetir los servicios con ejecutor138 una vez aceptada esa prueba. Consultar sus resultados antes de asumir que completaron.

Los diagnósticos nuevos se comprimieron con NTFS, sin borrar archivos ni cambiar sus bytes, para recuperar espacio. Los checkpoints originales no se modificaron.

## Cierre para publicación: 27 de octubre de 2026

El usuario autorizó commit y push y pidió dejar el trabajo para descansar. La VM quedó detenida después de una migración completa en **`input141-publication`**, con512MB, OHCI/mouse USB, el CD de paquetes y los discos nuevos. El manifiesto `reports/graphics-011/resume-validation/input141-publication-machine-checkpoint.json` registra los seis hashes, los dispositivos BSD correctos y el hardware adicional. El disco de trabajo qcow2 se comprimió sin cambiar el contenido virtual; `qemu-img check` no encontró errores. Este checkpoint nuevo aún no se restauró en una segunda VM.

Joint140 volvió a detenerse en una ranura HID type0 cuyo contenido no era completamente cero; el filtro conservador de0047 resultó insuficiente. El parche0048 conserva los bytes opacos reales de NX_NULLEVENT, que no tiene una variante activa de la unión, y agrega una traza acotada de los bytes observados. No sustituye datos por ceros ni publica eventos nuevos.

Build141 compila0048 y pasa las siete pruebas nativas de memoria, además de la comparación i386/PPC de la ranura inicializada por el kernel y el negativo del ejecutor135. Su ejecutor tiene MD5 **8ea0af3748c5c6dbe19be84f4db5e9c3**. **Quedan pendientes** los probes142 de reutilización de datos de una tecla real y el arranque conjunto143. No se afirma que0048 haya resuelto todavía el bloqueo gráfico.

Para retomar sin arrancar en frío ni escribir en el checkpoint:

```sh
python3 tools/restore_graphics011_checkpoint.py --from-label input141-publication --as-label continuacion-nueva --port 4455
python3 tools/qemu_monitor.py --port 4455 cont
python3 tools/drive_graphics011_hid_probe.py --port 4455 --fat build/graphics011-continuacion-nueva-restored-exchange.img --trial 142 --mode n --attempt 1 --mouse --tracking
python3 tools/drive_graphics011_hid_probe.py --port 4455 --fat build/graphics011-continuacion-nueva-restored-exchange.img --trial 142 --mode p --attempt 1 --mouse --tracking
python3 tools/drive_graphics011_hid_probe.py --port 4455 --fat build/graphics011-continuacion-nueva-restored-exchange.img --trial 142 --mode j --attempt 1 --mouse --tracking
```

Los tres probes consumen entrada de hardware real. El nativo y el nuevo deben terminar0, conservar el clic y el evento9 y leer dos payloads de teclas consumidas; el ejecutor138 anterior debe terminar125. Después de revisar sus resultados, el comando invitado preparado es `sh /var/tmp/graphics011-stage143/run.sh`. Usar capturas con límite de tiempo y verificar la ventana contra la VRAM antes de actualizar el BAT.

El repositorio publica código, parches, manifiestos, capturas verificadas y trazas seleccionadas. Los discos, RAM, medios originales, archivos de intercambio y ejecutables compilados permanecen locales; clonar el repositorio por sí solo no proporciona esas dependencias del laboratorio.
