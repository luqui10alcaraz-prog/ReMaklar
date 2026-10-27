# Probar ReMaklar 0.11 en Windows

Hacé doble clic en **`Probar-ReMaklar.bat`**, en la carpeta del escritorio `ReMaklar`. También hay una copia del lanzador dentro del repositorio.

Se abrirá una ventana real de QEMU mediante WSLg. Primero verifica los hashes y restaura una copia del checkpoint `window102-first`; después reanuda Darwin y deja que los componentes originales completen el dibujo de la ventana del Installer. Usa 512 MB y el mismo Pentium III emulado de los ensayos. La preparación y la carga de la migración no se incluyen en el tiempo activo medido.

La prueba dura como máximo **180 segundos**. Podés cerrarla antes cerrando la ventana de QEMU o presionando Ctrl+C en la consola. El arnés original conserva además su propio presupuesto de ejecución y puede terminar los servicios antes de ese límite. Cada ejecución usa nombres y puerto nuevos, overlays nuevos y una copia del FAT. No reanuda las VMs de investigación ni escribe en los checkpoints preservados.

Para abrir directamente la ventana ya dibujada, desde una consola en esa carpeta:

```bat
Probar-ReMaklar.bat --estado final
```

Para cambiar el límite, entre 10 y 600 segundos:

```bat
Probar-ReMaklar.bat --limite 300
```

Para comprobar los requisitos sin abrir una VM:

```bat
Probar-ReMaklar.bat --comprobar
```

La consola muestra la ubicación de los resultados, dentro de `ReMaklar\logs\graphics-011-restore-prueba-*`. Allí se guardan:

- `rendimiento.csv`: segundos desde la reanudación, CPU de QEMU en el host (100% = un núcleo) y memoria residente del host en MB. Esa memoria incluye el proceso QEMU; no es la RAM libre de Darwin.
- `resumen.json`: duración, motivo de cierre y estadísticas de la sesión.
- Capturas del framebuffer al comenzar, al cambiar durante el muestreo y al terminar por tiempo/Ctrl+C; `final.vram` conserva los bytes VESA en esos cierres controlados. Cerrar directamente la ventana conserva las capturas periódicas anteriores.
- `diagnostico/`: procesos y colas finales de las trazas recuperadas con la copia detenida, cuando el cierre permite capturarlas.
- `command.json`, `qemu.log`, `serial.log` y los estados de restauración/reanudación. El restaurador espera que la migración termine y comprueba que PPM y VRAM coincidan con el checkpoint antes de ejecutar.

**Qué permite evaluar hoy:** el repintado real del Installer y el consumo del entorno actual. La compilación conserva trazas activas y usa dos capas de traducción (máquina i386 emulada y código PPC traducido); no representa una versión optimizada. Las capturas se muestrean cada cinco segundos: no son una medición de FPS.

**Límite de interacción:** teclado y mouse siguen siendo experimentales. Un evento HID puede detener WindowServer por un campo compartido aún sin traducir. Para observar el repintado, dejá la ventana sin entrada de teclado/mouse al principio. La pantalla original termina mostrando «This software cannot be installed on this computer»; no se habilitó la instalación ni se alteró esa respuesta.

Requiere el WSL, WSLg, Python/Pillow, QEMU y los archivos locales que ya están preparados en esta computadora. No necesita ejecutar el BAT como administrador. Las copias de prueba y sus logs se conservan para poder revisar los resultados; cada nueva ejecución comienza nuevamente desde el checkpoint original elegido.
