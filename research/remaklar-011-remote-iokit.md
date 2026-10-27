# Continuacion de mapeos IOKit remotos

Run43: referencia i386 y ejecucion PPC pasan el mapa de cursor original en otra tarea, lectura de version 3, escrituras numericas bidireccionales sobre el objeto fisico y unmap remoto. Ambos exit=0, timeout=0. Los otros 15 probes positivos tambien pasan. Se mantienen tres controles negativos contra checkpoints previos. Linux pasa 11/11.

Se preservo el disco memory512 anterior y se creo un overlay independiente remote43, con una copia de su FAT. El primer arranque automatico entro en multiusuario; se reinicio exclusivamente esa copia y se arranco en single-user VESA 1024x768x32. fsck original marco limpio el filesystem. No se cambiaron componentes Apple.

El adaptador usa io_connect_map_memory original con la capacidad Mach de la tarea destino y comprueba vm_region en esa tarea. Los metadatos de proteccion y layout se publican en un mailbox MAP_SHARED propio de cada traductor; no contiene pixeles ni respuestas CGS. Al recuperar el gate de ejecucion, el cliente instala metadatos y activa los helpers tipados sobre la direccion del objeto original. El mapa y el unmap se notifican antes de continuar el intercambio del fixture. El formato visible de pixeles se deriva de las consultas originales existentes al framebuffer.

Limites por verificar: mapeo remoto concurrente mientras el cliente ejecuta un TB sin un punto de sincronizacion; modificacion remota posterior de protecciones; identidad frente a reciclado de PID/archivos de mailbox; variantes read-only y offsets de subvista. El protocolo actual tiene 256 eventos por proceso y falla explicitamente al agotarse. No se declara soporte general de todas las operaciones remotas.

El parche 0014 conserva el delta sobre 0013. Aplicacion en una copia aislada reproduce 17 fuentes; no se sobrescribieron los checkpoints anteriores. Validation44 repite la regresion y el arranque conjunto con WindowServer listo antes de los clientes. Installer aun no se declara verificado.

## Run48 y validation49

Pasaron las referencias i386/PPC de KERN_PROC_PID y Mach OOL de aplicacion (copia, deallocate, recepcion y unmap). El layout real de kinfo_proc es i386=488, PPC=492: se conserva la salida de ambos compiladores en kinfo47. Los campos publicos se convierten individualmente; la imagen privada del simple-lock del kernel se conserva como bytes opacos con extension PPC a cero, sin prometer semantica de lock entre arquitecturas.

Run48 pasa los 21 probes positivos y Linux 11/11. Validation49 pasa 18 estados de regresion, 23 utilidades y 11 filesystem. WindowServer consulta correctamente la cadena real de procesos y recibe OOL CGS 29320 de 124 bytes. Splash ya no falla al establecer la conexion CGS. Se detiene despues en una asercion porque falta BootPanel.pdf, y su hijo encuentra la guarda de herencia IOKit antes de ejecutar Installer.

## Run50/51 y direct52

El fixture i386 demuestra que cursor y VRAM usan VM_INHERIT_NONE. Run50 conserva su fallo PPC: el antiguo vm_region del puente devolvia herencia=1 fija, independientemente del kernel. Run51 consulta el vm_region real y mantiene la region limitada al espacio guest; el hijo consulta sus mapas reales y descarta metadatos solo de regiones efectivamente ausentes. Regiones IOKit heredadas que sobrevivan siguen rechazadas hasta validar su semantica. Pasan i386/PPC, incluyendo conservacion de mapas del padre, y los 23 probes positivos. Linux 11/11.

Se restauro BootPanel.pdf directamente del mismo CD original, sin alterar bytes (60346 bytes, SHA256 en resume-validation/bootpanel-original.json). No se sube el PDF original a Git ni se usa como sustituto del Installer.

Direct52 lanza el ejecutable original del Installer despues de WindowServer listo. Su regresion pasa 18 estados, 23 utilidades y 11 filesystem sin residuos. El nuevo bloqueo es syscall96 setpriority en un hijo de WindowServer; Installer termina con RegisterProcess failed (-308). Aun no se atribuye ese error exclusivamente a setpriority hasta repetir el ensayo con la llamada conectada.

Run53 conserva un error de compilacion del adaptador (nombre incorrecto del parametro de error), corregido en run55. Run55 compila el ejecutor, pero falla al compilar el fixture de prioridad porque el header Darwin6 requiere sys/time.h antes de sys/resource.h. La exportacion anterior fallo al incluir globs sin coincidencias y dejo el FAT montado; se recuperaron logs y se desmonto. Se preservo una imagen completa antes de inspeccionarla; fsck sin escritura solo informo el dirty bit. No se reparo el disco activo.

Run57 pasa las prioridades 10, -1 y 20, errores reales y padre intacto, con 25 probes positivos. El resultado -1 exitoso de getpriority conserva errno=0 y el carry guest limpio. Direct58 supera el registro de proceso y alcanza el siguiente RPC real: task_threads (3402).


## Run59 a run65: siguientes bloqueos resueltos

Run59 conecta task_threads con el kernel y conserva derechos reales, identidades self/worker y liberacion de arrays OOL. Pasan 27 probes positivos. Direct60 encuentra fcntl F_GETFL, implementado y verificado junto con F_SETFL en run61 (29 probes). Direct62 llega a RPC3202: mach_port_rename, no allocate_name. ATS usa nombres altos que representan punteros; run63 valida renombrado real, mensajes, pertenencia a port-set, colisiones y destruccion (31 probes). La tabla dispersa conserva la capacidad nativa, sin fabricar endpoints.

Direct64 llega a vm_copy RPC3808. Run65 lo conecta al kernel para rangos guest bajos verificados, comprueba copia superpuesta, aislamiento COW en ambos sentidos y KERN_PROTECTION_FAILURE=2 sobre destino read-only. Pasan los 33 probes positivos y script_exit=0. No se afirma soporte general para rangos altos, memoria tipada de dispositivo ni todos los casos de longitud cero. Los parches 0017-0021 y sus manifiestos reproducen cada paso en una copia aislada.

La ultima regresion completa sigue siendo direct52 (18 estados, 23 utilidades y 11 filesystem); las ampliaciones posteriores se validaron con los probes acumulados. No se ejecutaron nuevamente todas las regresiones despues de 0021.

## Direct66: barra Aqua real, sin ventana del Installer

El ensayo usa 512 MB y el arnes inicia ATS, espera el bucle de recepcion de WindowServer y solo despues inicia pbs e Installer originales. Aparecen la barra superior con textura y sombra originales y el cursor de espera multicolor. Las capturas estan en reports/graphics-011/direct66/. Debajo de la barra sigue el fondo azul: ninguna ventana del Installer esta verificada. No se reemplazaron componentes ni se simularon pixeles.

El ensayo no completo su limpieza/exportacion. Se inspecciono sin escribir el kernel mediante el monitor. La primera interpretacion de spin66-backtrace.json uso un EBP incorrecto; **spin66-backtrace-corrected.json** usa el EBP de los registros capturados y es la evidencia valida. No se declara un deadlock fijo de usimple_lock.

La pila real pasa por proc_exit, fdfree, vn_close, vm_object_terminate, vm_pageout_cluster, vnode_pageout, ffs_pageout y ubc_upl_abort_range. El proceso saliente es PID3846, qemu-ppc. Vnode 0x20d9c5c8, inode12953, tamano7180, modo0600 y nlink0 coinciden con la forma del mailbox interno, pero aun falta confirmar su identidad exacta y probar causalidad. Hay 90969 paginas libres y aproximadamente 100 MB libres en UFS: no hay evidencia de OOM o disco lleno.

El mailbox actual abre un archivo UFS MAP_SHARED de 7180 bytes sin FD_CLOEXEC. Al reinicializar tras exec puede desvincular una instancia aun abierta. Hipotesis de correccion pendiente: FD_CLOEXEC, backing alineado a 8192 bytes y msync explicito, con pruebas repetidas fork/exec/SIGKILL y de mapeo remoto. Esta correccion no esta implementada en 0021.

## Recuperacion preservada

Antes de reiniciar nada se detuvo QEMU y se completo la migracion a build/011-upl66-machine-state.bin (253068170 bytes). Se copiaron el overlay a vm/darwin602-graphics-011-upl66-preserved.qcow2 y el FAT a build/graphics011-upl66-preserved-exchange.img, y se guardo VRAM. Todos los hashes estan en resume-validation/upl66-machine-checkpoint.json. El overlay depende del checkpoint memory512 original: conservar tambien su backing. La VM permanece detenida tras la migracion.

Para continuar: crear un overlay nuevo sobre la copia preservada, copiar el FAT, arrancar single-user con 512 MB y VESA 1024x768x32, y recuperar los logs parciales de /var/tmp/graphics011-joint66 sin calificarlos como resultado completo. Las escrituras pendientes se conservan ademas en el estado completo de RAM; el disco copiado por si solo no promete incluirlas. No modificar las imagenes preservadas. Corregir y probar el mailbox antes del siguiente arranque conjunto. El objetivo sigue siendo la primera ventana autentica del Installer.
