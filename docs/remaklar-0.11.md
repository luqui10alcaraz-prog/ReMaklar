# ReMaklar 0.11: estado guardado

Continuación del 26 de octubre: **la primera ventana auténtica del Installer se verificó en el ensayo102**. El diagnóstico de direct66, las capturas, la comparación con VRAM y la restauración reproducible están en [remaklar-0.11-continuacion.md](remaklar-0.11-continuacion.md). Este documento conserva el estado histórico anterior a esa investigación.

Fecha: 26 de octubre de 2026, Buenos Aires.

El ensayo direct66, con 512 MB y WindowServer listo antes de iniciar Installer, llego a dibujar la barra original de Aqua y el cursor de espera. **Todavia no hay una ventana del Installer verificada.** No se simularon ventanas ni se sustituyeron componentes Apple.

La continuacion desde f3c3ef3 queda preservada en los parches 0014 a 0021, sus manifiestos y los resultados de `reports/graphics-011/`. Ver [investigacion y punto de recuperacion](../research/remaklar-011-remote-iokit.md).

## Cambios y pruebas actuales

- IOKit remoto sobre la capacidad real de tarea; metadatos del mapa compartidos entre traductores. Fixture i386/PPC con escrituras bidireccionales y unmap real.
- KERN_PROC_PID, mensajes Mach OOL, vm_region real y tratamiento de mapas IOKit ausentes en el hijo despues de fork.
- Prioridades reales, task_threads real, fcntl de estado, nombres Mach explicitos y vm_copy del kernel.
- Run65: script_exit=0; 33 probes positivos terminan con leader_exit=0 y timeout=0. Los controles negativos contra ejecutores anteriores se conservan por separado.
- Ultima regresion completa: direct52, 18 estados, 23 utilidades y 11 casos filesystem, sin residuos. Las ampliaciones posteriores pasan sus probes i386/PPC; no se declara una nueva regresion completa despues de 0021.
- Linux: 11/11 en los resultados conservados de runs43,48,51,55. No se declara una nueva prueba Linux posterior a 0021.

## Bloqueo y checkpoint actual

Direct66 no termino ni exporto su archivo final: no se cuenta como PASS. La pila corregida muestra un proceso qemu-ppc saliendo por proc_exit/fdfree y UFS pageout/ubc_upl_abort_range. El inode observado tiene 7180 bytes, modo 0600 y nlink=0, compatibles con el mailbox interno de metadatos. La atribucion exacta y la correccion todavia requieren prueba. No se demuestra falta de RAM ni disco lleno.

Se completo una migracion de la maquina detenida y se preservaron copias de disco, FAT y framebuffer. La VM queda detenida en ese estado; no se reescribieron las imagenes anteriores. [Manifiesto local con hashes](../reports/graphics-011/resume-validation/upl66-machine-checkpoint.json). Las imagenes grandes y los componentes originales permanecen fuera de Git en build/ y vm/.

Siguiente paso: recuperar en un overlay nuevo, conservar los logs parciales de direct66 y corregir el ciclo de vida del mailbox (FD_CLOEXEC, archivo alineado a pagina y sincronizacion por verificar). Probar fork/exec/terminacion y repetir regresiones y arranque ordenado. El checkpoint no incluye esa correccion propuesta.

## Reproduccion

Aplicar 0009 a 0021 en orden sobre el checkpoint 0.10, respetando las dependencias de cada manifiesto. 0021 reproduce los 18 archivos fuente actuales; los resultados de reproduccion aislada estan en resume-validation/*-patch-reproduction.txt.

Se conservan los generadores historicos exactos en tools/package_graphics011_vmcopy65.py y tools/package_graphics011_direct66.py, junto con el arnes tests/ppc/run_graphics_011_installer_joint.pl. Requieren los checkpoints locales indicados, el arbol build/qemu-011-source y BootPanel-original.pdf extraido del mismo CD. No contienen binarios originales de Apple. Son generadores de ensayos numerados y pueden reescribir sus scripts auxiliares: inspeccionarlos antes de reutilizarlos.

Lo siguiente describe el checkpoint publicado anterior; sus bloqueos y estado de VM no son el estado actual.

## Registro historico del checkpoint f3c3ef3

- Run41 termino antes de la reanudacion: script_exit=0. Sus resultados se recuperaron sin repetir las pruebas en reports/graphics-011/remote41/graphics011-run41.
- vm_map_64 sobre la tarea de otro proceso y escrituras bidireccionales sobre el backing real: PASS i386 nativo y PPC traducido, exit=0, timeout=0.
- Los 15 probes positivos de run41 pasan. Los tres controles negativos contra ejecutores anteriores fallan como se esperaba. pbs llega al timeout acotado; no se cuenta como PASS funcional.
- Regresion Linux41: 11/11 fixtures PASS.
- Validation42 completa: 18/18 estados exit=0 y timeout=0; utilidades 23/23; filesystem 11/11, leftover=0.
- Arranque conjunto con 512 MB: server_receive_loop_observed=1 antes de iniciar pbs y splash/Installer. El ensayo y su limpieza terminan: bounded_joint_trial_complete=1, script_exit=0.

## Bloqueo del checkpoint publicado (ya superado en la continuacion)

El despacho de capacidades de tarea usa pid_for_task real, cuya referencia i386 esta conservada en kobject40. No sondea un endpoint de aplicacion enviandole un RPC. Run41 conecta los RPC vm_map/vm_map_64 remotos con el kernel original.

En validation42, WindowServer obtiene dos mapas remotos reales de 32768 bytes, con result=0, para las tareas 43f y 441 (windowserver.stderr, lineas 3254 y 3266). Luego recibe CGS 29010 y solicita IOKit RPC 2819 al framebuffer 412, memory type 110, task descriptor 444. El adaptador exige todavia TASK_SELF y termina explicitamente en `invalid IOKit memory task descriptor` (linea 3283). Installer vuelve a registrar que no puede establecer la conexion con WindowServer.

Siguiente trabajo: admitir la capacidad de tarea real en IOConnectMapMemory/UnmapMemory, consultar y validar la region en la tarea destino, y propagar los metadatos de proteccion/layout al ejecutor del cliente. No basta con quitar la comprobacion TASK_SELF: las tablas page_set_flags/live_kind son privadas de cada proceso. La memoria de dispositivo debe seguir siendo el objeto fisico original, con conversion de campos verificada. Esta ruta aun no fue implementada ni probada.

## Fuentes y checkpoints

Aplicar en orden los parches 0009 a 0013 sobre el checkpoint 0.10, conservando sus manifiestos. 0013-remote-task-vm-map.patch reproduce los 16 archivos fuente sobre 0012; evidencia en resume-validation/remote41-patch-reproduction.txt. No sobrescribir checkpoints anteriores.

La VM sigue encendida en single-user, sin procesos traducidos del ensayo. El inventario leido del kernel esta en resume-validation/validation42-live-processes.json. Discos, ISO, RAM del checkpoint de presion de memoria y archivos completos de intercambio siguen locales en vm/ y build/, excluidos de Git como antes. No detener ni reescribir esas imagenes para continuar.

Paquetes reproducibles de esta continuacion: tools/package_graphics011_remote41.py y tools/package_graphics011_validation42.py. El segundo empaqueta la regresion y el arnes de arranque ordenado. Los resultados completos y fallos anteriores quedan bajo reports/graphics-011; el historial de investigacion se conserva en research/remaklar-011-shared-graphics.md.
