ï»¿# ReMaklar 0.11 â€” Shared Graphics

## Estado de continuaciÃ³n

Se retomÃ³ el Ã¡rbol existente el 25 de octubre de 2026 (hora de Buenos Aires), conservando run1â€“run6, pruebas y fuentes. No se hizo commit ni push. El informe 0.11 solicitado no existÃ­a en este Ã¡rbol al retomarlo; este archivo documenta la continuaciÃ³n, sin reconstruir ni sustituir las evidencias previas.

**No hay interfaz Aqua ni ventana autÃ©ntica del Installer verificada.** La consola que cambia durante el arranque de WindowServer no constituye evidencia de pÃ­xeles de interfaz. Las imÃ¡genes originales y componentes Apple no se modificaron.

## Cursor original: progreso verificable

Run6 terminaba en `live shared write unsupported offset=240 width=8 errno=22`. El layout de IOGraphics-40 (`IOFramebufferShared.h`, `bm38Cursor`) declara pÃ­xeles `unsigned int`: un acceso PPC de ocho bytes que atraviesa dos pÃ­xeles debe traducir dos enteros de 32 bits en su orden lÃ³gico. Tratarlo como un Ãºnico entero nativo de 64 bits intercambiarÃ­a los pÃ­xeles.

Se aÃ±adiÃ³ en `build/qemu-011-source/darwin-user/remaklar/live-regions.inc` el acceso pareado, restringido al Ã¡rea de pÃ­xeles de un mapa framebuffer cuyo modo original fue comprobado como 32 bpp. Se comprueban lÃ­mites y protecciones antes del acceso. No se promete atomicidad conjunta para el par: los locks y CAS de 32 bits permanecen sobre el objeto fÃ­sico original. Las barreras `sync/eieio/isync` de la integraciÃ³n previa llaman a una barrera host real.

Run7 fallÃ³ al compilar con GCC2 por declaraciones despuÃ©s de sentencias; se conserva [la compilaciÃ³n fallida](../reports/graphics-011/resume7/graphics011-run7/build.txt). Se corrigiÃ³ en run8. WindowServer superÃ³ el cursor y llegÃ³ a **Mach RPC 3412**, `thread_create_running`, con flavor PPC y 40 palabras de estado. El fallo sigue siendo explÃ­cito; no se devuelve una creaciÃ³n de hilo ficticia. [Traza run8](../reports/graphics-011/resume8/graphics011-run8/windowserver.stderr).

## Alias fÃ­sicos IOKit

La prueba anterior exigÃ­a direcciones diferentes usando `kIOMapAnywhere`. XNU-344 permite reutilizar un mapping compatible (`IOMemoryDescriptor::makeMapping` y `_IOMemoryMap::copyCompatible`), de modo que aquella exigencia no probaba una incoherencia del dispositivo. Se conserva el fallo original de run6/run8.

Run9 reserva y libera una direcciÃ³n concreta antes de pedir allÃ­ un segundo mapa IOKit sin `kIOMapAnywhere`. Ambos mapas tienen direcciones distintas. Pasan en i386 nativo y PPC traducido:

- Lectura de versiÃ³n 3 y escrituras bidireccionales sobre el mismo objeto.
- PÃ­xeles de 32 bits y par `lfd/stfd` (double 1.0: palabras `3ff00000`, `00000000`), restaurando los valores originales.
- Locks originales, accesos parciales y vecinos intactos.
- ProtecciÃ³n de la segunda vista, unmap, cierre y globals IOHID originales.

Evidencias: [i386](../reports/graphics-011/resume9/graphics011-run9/shared-native.stdout), [PPC](../reports/graphics-011/resume9/graphics011-run9/shared-jaguar.stdout), [estado PPC](../reports/graphics-011/resume9/graphics011-run9/shared-jaguar.status). Esto valida alias fÃ­sicos IOKit; **no valida el alias creado mediante Mach memory entry**.

## Mach memory entry: pendiente

La referencia i386 tambiÃ©n obtiene `source=00000003 alias=00000000` para el objeto IOKit, aun con retorno de Ã©xito. No se clasifica ese resultado como alias coherente. XNU-344 `vm_user.c` conserva objeto y offset en la named entry y `vm_map_64` debe usar ese objeto; el dato vacÃ­o requiere aislar el comportamiento real del llamador/kernel. Se agregÃ³ un control de memoria anÃ³nima con sentinel y escritura bidireccional para la siguiente ejecuciÃ³n.

La propagaciÃ³n actual `live_object_kind` conserva procedencia, pero no demuestra identidad del backing: no se considera completa. Siguen sin validar offsets de subvista, COW, destrucciÃ³n/reutilizaciÃ³n de derechos y unmap parcial de regiones tipadas. Los eventos HID de uniÃ³n no verificada siguen fallando explÃ­citamente.

## Direccionamiento alto de pbs

Se conserva el prototipo `tests/memory/high-window.*`; no estÃ¡ integrado en el traductor. Su prueba i386 Linux pasa: direcciones guest ff000000/ff002000, backing bajo, MAP_FIXED interior con archivo y offset real, alias compartidos, fork, protecciÃ³n y reserva PROT_NONE despuÃ©s de unmap parcial. [Resultado](../reports/graphics-011/resume-validation/high-window-linux-i386.txt).

No se considera semÃ¡ntica MAP_FIXED completa: aÃºn requiere pruebas de rangos superpuestos que atraviesen regiones, huecos y mprotect sobre pÃ¡ginas sin mapping, traducciÃ³n de syscalls/seÃ±ales y TCG. No se devuelve otra direcciÃ³n guest para una peticiÃ³n fija.

## Regresiones y preservaciÃ³n

PasÃ³ la regresiÃ³n aislada i386 Linux de memoria tipada: accesos parciales 8/16/32/64, bitfields HID, alias MAP_SHARED reales, contenciÃ³n con proceso nativo (200000 incrementos), actualizaciÃ³n parcial concurrente (100000), solo lectura y limpieza. [Resultado](../reports/graphics-011/resume-validation/typed-live-linux-i386.txt).

Se encontraron FAT divergentes en el intercambio mientras aÃºn estaba montado por el guest. Se preservÃ³ una copia y se inspeccionÃ³; la reparaciÃ³n se aplicÃ³ exclusivamente sobre esa copia. DespuÃ©s de `sync; umount /exchange`, otra copia permitiÃ³ recuperar las exportaciones sin reparar el disco activo. Se conservan `build/exchange011-run8-unmounted.img`, `build/exchange011-run8-final.img` y `build/exchange011-run9-final.img`. El intercambio estÃ¡ cerca de su capacidad: no confundir fallos de exportaciÃ³n con resultados de programas.

## Trabajo aÃºn necesario

Resolver el control Mach y validar metadatos de alias; ampliar regresiones nativas; implementar ejecuciÃ³n real de hilos PPC para el RPC 3412 sin carreras sobre `cpu_single_env`, TLS, reservas y tablas globales; integrar y verificar direccionamiento alto; repetir el arranque conjunto de originales. Ninguna de estas tareas se declara completada por el avance del cursor.


## Recuperación del entorno y regresión ampliada

El proceso QEMU original terminó por SIGTERM de `systemd-shutdown` durante un apagado de WSL. [Log](../logs/graphics-010/graphics-boot-vm.log). No fue un apagado limpio de Darwin y no se pudo capturar RAM antes de la terminación. No se atribuye a la prueba nativa sin evidencia.

Se preservaron el overlay y FAT interrumpidos y se arrancaron copias nuevas: `vm/darwin602-graphics-011-recovery.qcow2`, `build/graphics011-recovery-exchange.img`. `qemu-img check` no encontró errores de formato; fsck FAT no requirió reparación. El guest arrancó en VESA 1024x768x32 y `fsck -p` corrigió una entrada sin referencia y contadores UFS en **la copia**. Las fuentes originales y el overlay interrumpido permanecen disponibles.

Se recuperó `graphics011-regression10`: **18 estados exit=0**, utilidades **23/23**, filesystem **11/11, leftover=0**. [Utilidades](../reports/graphics-011/recovered/graphics011-regression10/utilities.txt), [filesystem](../reports/graphics-011/recovered/graphics011-regression10/filesystem.txt), [sesión](../reports/graphics-011/recovered/graphics011-regression10/session.txt). La validación12 coincidió con el apagado: sus logs recuperados vacíos no son PASS y se repite con otro directorio.

Se exportó `patches/qemu-0.10.6/0009-shared-graphics.patch` contra el árbol 0.10 conservado, con manifiesto SHA-256. Aplicación en una copia aislada: los nueve archivos resultantes coinciden byte por byte con las fuentes 0.11. [Verificación](../reports/graphics-011/resume-validation/patch-reproduction.txt). No se hicieron operaciones de commit ni push.

Limitación atómica adicional: la implementación de `lwarx/stwcx.` usa CAS sobre la palabra original. Se probó contención de locks, pero no se validó equivalencia completa de reservas PPC ante ABA o escrituras externas de kernel. El estado de reserva global y `cpu_single_env` también deben cambiar antes de ejecutar varios hilos PPC. No es correcto añadir pthreads sin resolver esos estados compartidos y las esperas bloqueantes.


## Validación final de esta continuación

La compilación nativa del prototipo alto falló en validación13 por dependencias de headers de Darwin6 (`sys/types.h`, `sys/time.h`) y el nombre `MAP_ANON`. Se corrigieron los includes y la compatibilidad de la constante, conservando [el error](../reports/graphics-011/high15/graphics011-validation13/high-window-build.txt). La validación14 ejecutó el prototipo nativo con éxito.

Se corrigió además un error semántico en el prototipo: una reserva host PROT_NONE para un hueco guest no puede hacer que mprotect guest tenga éxito. Ahora cada región conserva un bitmap de páginas mapeadas; los huecos se distinguen de páginas válidas PROT_NONE. Se prueban tanto un hueco como un rango mixto. **High15 pasa en Darwin i386 nativo, exit=0, timeout=0**, y la misma prueba pasa en Linux i386. [Resultado Darwin](../reports/graphics-011/high15/graphics011-high15-results/native.stdout), [estado](../reports/graphics-011/high15/graphics011-high15-results/native.status). Esto sigue siendo un prototipo aislado; no resuelve todavía pbs en el ejecutor.

La regresión del ejecutor run11 repitió los **18 probes con exit=0 y timeout=0**, utilidades **23/23**, filesystem **11/11 sin residuos**. [Resumen estructurado](../reports/graphics-011/resume-validation/summary.json), [sesión](../reports/graphics-011/validation14/graphics011-regression11/session.txt).

El ensayo conjunto original terminó su intervalo acotado, con limpieza de los descendientes registrados. [Finalización](../reports/graphics-011/validation14/graphics011-joint11/completion.status). Sus resultados concretos son:

- ATS llega a una recepción Mach real y permanece vivo hasta la limpieza del ensayo.
- WindowServer vuelve a alcanzar la creación real de hilo PPC, RPC **3412**, sin superar todavía ese bloqueo. [Traza](../reports/graphics-011/validation14/graphics011-joint11/windowserver.stderr).
- pbs solicita MAP_FIXED `ff002000`, tamaño `00bfc000`, sobre su shm real. El ejecutor devuelve EINVAL; después se registra un fault host legacy al acceder a una dirección alta. No se cambió MAP_FIXED para devolver otra dirección. [Traza](../reports/graphics-011/validation14/graphics011-joint11/pbs.stderr).
- splash ejecuta el Installer original, que carga sus recursos y termina sin poder establecer su conexión por defecto con WindowServer. [Traza splash/Installer](../reports/graphics-011/validation14/graphics011-joint11/splash.stderr).

No se verificó dibujo de interfaz ni píxeles Aqua auténticos. El framebuffer se limpió visualmente durante WindowServer, pero esa observación no identifica un compositor ni una ventana y **no se cuenta como éxito gráfico**.

La ISO Jaguar y `vm/darwin602.qcow2` mantienen exactamente los hashes SHA-256 de 0.10. [Comprobación](../reports/graphics-011/resume-validation/preserved-originals.json). Para liberar espacio se retiraron únicamente copias de payloads del FAT después de conservar imágenes completas; los payloads y resultados host permanecen disponibles. La exportación final FAT desmontada pasó fsck sin reparación.

La VM de recuperación queda encendida en single-user, VESA, con sync y FAT desmontado. No quedan procesos traducidos: [inventario](../reports/graphics-011/resume-validation/final-processes.txt), [consola](../reports/graphics-011/resume-validation/final-console.png). No se hizo commit ni push. El objetivo gráfico sigue incompleto: faltan ejecución real de hilos PPC, reservas atómicas completas, metadatos de subregiones y traducción de direcciones altas dentro del ejecutor.

## Continuación solicitada: hilos PPC (26 de octubre)

Se continúa hacia el Installer, sin cerrar el trabajo en el bloqueo 3412. Se implementa una primera ruta de hilos nativos con contextos PPC separados y una exclusión global de ejecución TCG. Un helper al inicio de cada TB cede cada 64 bloques, incluso si el guest gira sin syscalls. Las esperas Mach liberan la exclusión mientras el kernel bloquea el hilo. El valor reservado de lwarx y el puntero de hilo pasan al contexto CPU; una cesión invalida la reserva.

Estado **experimental, aún no validado**: run16 detectó una integración en el entrypoint equivocado (`darwin-user/main.c`); el runner activo usa `remaklar/bootstrap-main.c`. Se conserva su fallo (fixture exit134). Run17 conecta la exclusión al runner activo. La prueba nueva usa thread_create_running original, bucle PPC sin syscalls, recepción Mach bloqueante y contención de lock entre hilos. Se corrige también su buffer de recepción para incluir espacio de trailer Mach. No se declara todavía soporte completo de pthreads, señales por hilo ni reservas ante escrituras externas.

El ensayo exploratorio encontró además host RPC 213 (processor_set_default). La siguiente variante conecta ese RPC al servicio real del kernel y convierte thread_policy a argumentos nativos. El parche exportado 0009 sigue representando el checkpoint verificado anterior; estas modificaciones en curso permanecen en `build/qemu-011-source` y payloads stage126/127/128 hasta verificarlas.

### Evidencias posteriores: memoria alta y recorrido real de servicios

Run18 corrigió los problemas de integración y su prueba de hilos terminó 0: creación Mach real, preempción de un bucle PPC sin syscalls, espera en cola Mach y 40000 incrementos protegidos. Se añadieron processor_set_default, host_processor_set_priv y las llamadas de política del processor set mediante APIs reales. Run20 añadió semáforos nativos; el fixture pasó con espera, señal y timeout. Las modificaciones posteriores agregan pipe y cesión del gate para read/write/waitpid; el fixture ampliado vuelve a comprobarse en run24.

La primera integración de memoria alta llegó a MAP_FIXED ff000000/ff002000, alias de archivo y syscalls, pero run20 falló en fork porque una guarda antigua confundía `remaklar_live_max` (helpers activos) con la presencia de IOKit compartido. Se conserva ese fallo; no es PASS. Run22 usa los descriptores IOKit reales para esa guarda y **el caso completo PPC pasó con exit=0 y timeout=0**, incluyendo alias Mach desde una dirección alta, propagación bidireccional de datos, fork, mprotect de huecos, remap y vm_protect. Referencia i386 también pasa. [PPC](../reports/graphics-011/shared22/graphics011-run22/high-jaguar.stdout), [estado](../reports/graphics-011/shared22/graphics011-run22/high-jaguar.status).

Los helpers TCG distinguen las direcciones guest altas, el backing privado bajo y los buffers que pertenecen al host. La primera regresión Linux detectó que los buffers host i386 pueden estar por encima de c0000000: se corrigió la ruta raw de buffers host, manteniendo estricta la ruta TCG de direcciones guest. Se conservan el fallo y las repeticiones; la última ejecutó **11/11 fixtures Linux PASS**. [Regresión](../reports/graphics-011/resume-validation/thread-high-linux-fixtures3.txt).

Run22 comprobó también, nativo y PPC, las coordenadas originales del cursor accedidas como palabra de dos shorts. La conversión conserva cada entero nativo de 16 bits mediante un único CAS host de 32 bits; no cambia el layout del objeto. Se probaron campos de bytes compuestos y accesos 64 de ABI i386 alineados a cuatro bytes. La prueba de contención nativa y los alias IOKit terminaron 0. La tabla gamma de identidad de 3×256 UInt16 se envió al método original 11, y ambas referencias devolvieron 0. [Shared PPC](../reports/graphics-011/shared22/graphics011-run22/shared-jaguar.stdout), [referencia](../reports/graphics-011/shared22/graphics011-run22/shared-native.stdout).

WindowServer superó la creación de semáforos y gamma. Run22 se detuvo al entrar en el encabezado de NXEvent dentro de IOHID. Run23 habilita solo los campos declarados previos a la unión: next/sema, tipo, coordenadas int32, tiempo uint64 alineado a cuatro, flags y ventana. La unión sigue bloqueada hasta validar el tipo activo. WindowServer avanzó hasta la llamada real de límites IOHID, selector6; se añade su conversión de cuatro shorts en run24.

pbs superó el bloqueo de dirección alta. Se añadieron clock_get_time, clock_sleep y mk_timer_create/destroy/arm/cancel, con conversión explícita de los tres uint64 de los mensajes de expiración. En run23 pbs permanece recibiendo en una cola Mach y termina por el límite de 45 segundos del arnés (timeout=1), sin el fault alto anterior. Esto es progreso de servicio, no éxito gráfico. [Estado pbs](../reports/graphics-011/events23/graphics011-run23/pbs.status), [traza](../reports/graphics-011/events23/graphics011-run23/pbs.stderr).

La exportación run21 agotó el FAT; se conserva el archivo vacío y se reexportan los logs completos como r131full. Para liberar espacio se extrajo step85.tgz de una imagen FAT preservada, se comprobó íntegramente su tar y SHA-256, y se retiró solo la copia del FAT activo. El archivo completo de 15275825 bytes queda en `build/exchange-preserved-step85.tgz`. [Manifiesto](../reports/graphics-011/resume-validation/exchange-reclaim.json). No se borraron pruebas ni resultados originales.

**Trabajo activo:** run24, con prueba i386/PPC de expiración/cancelación de timers, fixture de hilos con pipe y adaptador IOHID selector6. Falta revisar sus estados, repetir la regresión nativa completa y el ensayo conjunto, y continuar los nuevos bloqueos. No hay ventana del Installer verificada. La captura física VESA `build/011-vram22.bin` contiene solo valores 0/255 y texto de consola; no se interpreta como interfaz Aqua.


### Continuación: run26–32 y primer llenado real (26 octubre)

Run26 verificó ocho probes nativos/PPC de memoria alta, timers, hilos con pipe, regiones tipadas y alias compartidos. La regresión nativa de validation27 y validation31 pasó los 18 casos, las 23 utilidades y los 11 casos de filesystem. Se preservan las evidencias en `reports/graphics-011/validation27` y `validation31`.

Run30 corrige la conservación de reservas durante ultrafast TLS y el despacho por procedencia de capacidades: un mensaje de aplicación con ID 4003 no es una llamada de processor-set. Los nuevos controles negativos fallan en run26 y pasan en run30; el resultado real de policy_enable es 4 tanto i386 como PPC, no se sustituye por éxito. Regresión Linux 11/11 en `resume-validation/thread-high-linux-fixtures30.txt`.

WindowServer original llegó a llenar la VRAM VESA: `build/011-vram30.bin` contiene 786335 palabras con bytes 00426bad, más píxeles de cursor. SHA256 5d0824173089589fa162577de319288cc42364edeb9eb8d0dc7e58493ccd252a. La captura preservada en `resume-validation/windowserver-first-fill.png` aparece marrón: VESA interpreta esas palabras con endianidad i386. Es dibujo real, pero todavía no una ventana ni una interfaz verificadas.

Validation31 detectó un bloqueo nuevo en WindowServer: entrada indirecta syscall(180), kdebug_trace. La entrada indirecta ya existía; faltaba el destino 180. Run32 incorpora el syscall nativo real, conservando su errno, y campos de píxel uint32 solo dentro del área visible verificada mediante el modo y pixel information originales y VRAMMapOffset. El resto del mapa de 16MB sigue siendo bytes sin tipo. Está pendiente la comprobación nativa/PPC y el nuevo ensayo conjunto. No hay ventana del Installer verificada.


Run32 terminó sus once probes positivos con leader_exit=0 y timeout=0; los dos controles negativos contra run26 fallaron como se esperaba. pbs continúa vivo hasta timeout del arnés. WindowServer completa la inicialización, dibuja el fondo azul RGB(66,107,173) y el cursor original, y espera mensajes Mach. [Captura](../reports/graphics-011/resume-validation/windowserver-blue-cursor32.png). Su traza verifica offset visible 0, 3145728 bytes, 1024x768, máscaras ff0000/ff00/ff. No se cuenta como ventana del Installer.

La captura de VRAM run32 se tomó después de la limpieza del proceso y muestra la consola restaurada; NO es simultánea con la captura azul. Esta limitación queda explícita en su JSON. Para los siguientes ensayos se pausa la VM antes de tomar ambas muestras.

Validation33 y 34 conservaron fallos del nuevo fixture de alias VRAM: eligió direcciones fijas no disponibles (1b000000 reservada por el segmento host del ejecutor; 30000000 usada previamente por el alias del cursor). La referencia i386 de 33 pasó. Validation35 elige espacio con vm_allocate y lo libera antes de la llamada fija IOKit, sin cambiar la semántica del driver ni de MAP_FIXED. Solo continúa al ensayo conjunto si pasan ambos probes y la regresión.

Los checkpoints 0009 y 0010 permanecen íntegros. El delta actual se exporta como 0011-live-framebuffer-thread-progress.patch; su aplicación sobre el checkpoint run26 reproduce exactamente los 16 archivos fuente. [Verificación](../reports/graphics-011/resume-validation/progress32-patch-reproduction.txt).


### Validación35 interrumpida por presión de memoria; continuación con 512MB

La captura simultánea del ensayo conjunto confirma VRAM física VESA con **786335 palabras ad6b4200**, 54 palabras 000000ff y 43 ffffffff. La pantalla muestra azul RGB(66,107,173) y cursor original. [Captura](../reports/graphics-011/resume-validation/joint35-blue-cursor.png), [muestra y hash](../reports/graphics-011/resume-validation/joint35-blue-cursor.json). No aparece una ventana del Installer.

El arnés dejó de avanzar en ps. Se leyó el Mach-O del kernel residente y su tabla de símbolos, sin escribir en su memoria. El hilo del ps nativo tenía wait_event=003d83b0, identificado por los símbolos originales como vm_page_free_count. El kernel seguía en idle_thread_continue y sus IRQ0 y reloj avanzaban. Quedaban solo unos centenares de páginas libres en la VM de 128MB. Se conserva la lista de procesos y las lecturas en resume-validation/joint35-live-processes.json y build/011-proc-*.bin. El diagnóstico es presión de memoria nativa durante el arranque conjunto, no prueba de un bloqueo nuevo de la ABI gráfica.

Se preservó la VM completa mediante migración pausada: build/011-oom35-machine-state.bin, junto con el disco y FAT anteriores, antes de crear una copia independiente vm/darwin602-graphics-011-memory512.qcow2 y build/graphics011-memory512-exchange.img. [Checkpoint y hashes](../reports/graphics-011/resume-validation/joint35-memory-pressure-checkpoint.json). La nueva copia arrancó con 512MB y fsck original corrigió contadores, un archivo sin referencia y el directorio de regresión interrumpido. El disco anterior y el estado completo no se repararon ni sobrescribieron.

La exportación recuperada en validation35-partial contiene archivos vacíos: los datos no habían sido sincronizados al disco antes del bloqueo. No se usa como evidencia de PASS. El estado completo anterior conserva la RAM para investigación posterior. Run32 y sus resultados host previos permanecen completos. Ready36 repite los controles de syscall indirecta i386/PPC y la regresión nativa, y espera observar a WindowServer recibiendo mensajes antes de lanzar pbs y splash/Installer. En la nueva VM se comprobaron más de 116000 páginas libres. Trabajo en curso; no hay ventana del Installer verificada.


Ready36 completó la regresión nativa en la VM de 512MB: **18/18 exit=0 sin timeout, 23 utilidades, 11 filesystem y leftover=0**. La prueba de syscall indirecta dio exactamente la misma salida i386/PPC, incluido kdebug_trace=-1 errno=22. El arranque confirmó server_receive_loop_observed=1 antes de iniciar los clientes. WindowServer recibió solicitudes CGS y contestó; el Installer original terminó con «could not establish the default connection to the WindowServer». No hubo un nuevo unsupported ni ventana. [Resultados completos](../reports/graphics-011/ready36/).

La revisión encontró que native_message copiaba solo msgh_size y descartaba los trailers que el kernel había recibido realmente. WindowServer usa opciones 02000102: solicita MACH_RCV_TRAILER_SENDER. Run37 convierte y conserva el trailer formato0 original, incluidos seqno y security_token; admite exactamente los tamaños Darwin6 8/12/20 y respeta el límite del buffer. El cuerpo de aplicación permanece intacto. No se inventan credenciales. El fixture nuevo comprueba las tres variantes, secuencia, identidad efectiva y sentinelas tras el trailer, con referencia i386 y control negativo contra run32. Está en verificación. El delta se conserva en 0012-mach-receive-trailers.patch sobre 0011; los 16 fuentes se reprodujeron por aplicación del parche. No hay GUI del Installer verificada.


## Checkpoint run41 / validation42

La continuacion actual, resultados recuperados y el nuevo bloqueo IOKit remoto estan documentados en [docs/remaklar-0.11.md](../docs/remaklar-0.11.md). Run41 y validation42 terminaron; no hay ventana del Installer verificada. El usuario autorizo commit y push para conservar este estado.
