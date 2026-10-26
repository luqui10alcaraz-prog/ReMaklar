# ReMaklar 0.11: checkpoint para continuar

Fecha: 26 de octubre de 2026, Buenos Aires.

No hay una ventana autentica del Installer verificada. WindowServer original dibuja el fondo azul y el cursor; Installer original sigue fallando al establecer su conexion. No se sustituyeron componentes Apple.

## Ultima validacion completada

- Run41 termino antes de la reanudacion: script_exit=0. Sus resultados se recuperaron sin repetir las pruebas en reports/graphics-011/remote41/graphics011-run41.
- vm_map_64 sobre la tarea de otro proceso y escrituras bidireccionales sobre el backing real: PASS i386 nativo y PPC traducido, exit=0, timeout=0.
- Los 15 probes positivos de run41 pasan. Los tres controles negativos contra ejecutores anteriores fallan como se esperaba. pbs llega al timeout acotado; no se cuenta como PASS funcional.
- Regresion Linux41: 11/11 fixtures PASS.
- Validation42 completa: 18/18 estados exit=0 y timeout=0; utilidades 23/23; filesystem 11/11, leftover=0.
- Arranque conjunto con 512 MB: server_receive_loop_observed=1 antes de iniciar pbs y splash/Installer. El ensayo y su limpieza terminan: bounded_joint_trial_complete=1, script_exit=0.

## Bloqueo actual comprobado

El despacho de capacidades de tarea usa pid_for_task real, cuya referencia i386 esta conservada en kobject40. No sondea un endpoint de aplicacion enviandole un RPC. Run41 conecta los RPC vm_map/vm_map_64 remotos con el kernel original.

En validation42, WindowServer obtiene dos mapas remotos reales de 32768 bytes, con result=0, para las tareas 43f y 441 (windowserver.stderr, lineas 3254 y 3266). Luego recibe CGS 29010 y solicita IOKit RPC 2819 al framebuffer 412, memory type 110, task descriptor 444. El adaptador exige todavia TASK_SELF y termina explicitamente en `invalid IOKit memory task descriptor` (linea 3283). Installer vuelve a registrar que no puede establecer la conexion con WindowServer.

Siguiente trabajo: admitir la capacidad de tarea real en IOConnectMapMemory/UnmapMemory, consultar y validar la region en la tarea destino, y propagar los metadatos de proteccion/layout al ejecutor del cliente. No basta con quitar la comprobacion TASK_SELF: las tablas page_set_flags/live_kind son privadas de cada proceso. La memoria de dispositivo debe seguir siendo el objeto fisico original, con conversion de campos verificada. Esta ruta aun no fue implementada ni probada.

## Fuentes y checkpoints

Aplicar en orden los parches 0009 a 0013 sobre el checkpoint 0.10, conservando sus manifiestos. 0013-remote-task-vm-map.patch reproduce los 16 archivos fuente sobre 0012; evidencia en resume-validation/remote41-patch-reproduction.txt. No sobrescribir checkpoints anteriores.

La VM sigue encendida en single-user, sin procesos traducidos del ensayo. El inventario leido del kernel esta en resume-validation/validation42-live-processes.json. Discos, ISO, RAM del checkpoint de presion de memoria y archivos completos de intercambio siguen locales en vm/ y build/, excluidos de Git como antes. No detener ni reescribir esas imagenes para continuar.

Paquetes reproducibles de esta continuacion: tools/package_graphics011_remote41.py y tools/package_graphics011_validation42.py. El segundo empaqueta la regresion y el arnes de arranque ordenado. Los resultados completos y fallos anteriores quedan bajo reports/graphics-011; el historial de investigacion se conserva en research/remaklar-011-shared-graphics.md.
