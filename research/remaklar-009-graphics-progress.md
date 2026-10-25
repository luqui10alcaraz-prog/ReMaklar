# ReMaklar 0.09 — arranque gráfico original de Jaguar

Fecha: 2026-10-25. Base del proyecto: `4cf7b57` (0.08). Componentes originales Jaguar 10.2 build 6C115, kernel Darwin 6.0 RELEASE_I386 bajo QEMU de sistema x86 TCG.


## Resultado verificado al cerrar esta continuación

**Todavía no hay interfaz gráfica auténtica ni ventana del instalador.** Se superaron los tres bloqueos iniciales: statfs, registro/entrega/retorno real de señales PPC mediante el sigtramp original, e IOServiceOpen/Close con métodos escalares del user client real. Splash ya ejecuta el Installer original mediante fork/exec. Los límites finales son memoria compartida de WindowServer y conjuntos de puertos/IPC de Installer; no se sustituyeron por éxitos ficticios.

| Programa original | Avance final | Bloqueo verificable |
|---|---|---|
| WindowServer | sigaction, máscaras, setlogin y vm_map anónimo con máscara 0xfff/alias 42 | RPC 3825, mach_make_memory_entry_64: necesita un objeto de memoria compartida con derechos y alias reales |
| Installer | statfs, getfsstat y pathconf; sigue ejecutando Foundation/AppKit originales | RPC 3226: insertar un receive right en más de un conjunto de puertos |
| splash | IOServiceOpen/Close, scalar I/O, host_info y thread_switch reales; luego fork/exec del Installer original | El hijo Installer alcanza RPC 3226; sigue faltando el servicio bootstrap WindowServer |

## Preservación y alcance

En la sesión anterior se reutilizó la VM entonces activa PID 8709, su overlay `vm/darwin602-native-007-overlay-02.qcow2`, el intercambio FAT y los builds nativos existentes. En esa sesión no se crearon discos ni nuevas imágenes; la continuación descrita más abajo utiliza un ISO auxiliar de recuperación de solo lectura. El runtime 0.08 se conservó; las modificaciones 0.09 están aisladas en `build/qemu-009-source` y el parche incremental 0007. Las copias nativas nuevas usan `/var/tmp/graphics009-run*`, sin sustituir ejecutores, logs ni recursos anteriores. No se ejecutó `rc.cdrom` ni una instalación, ni se habilitaron discos destino del instalador. No se incorporaron componentes de Tiger ni reemplazos gráficos.

## Implementación

### statfs y atributos

BSD 157 (`statfs`) y 158 (`fstatfs`) convierten la estructura Jaguar PPC32 de 272 bytes desde el resultado real de Darwin: shorts, contadores, fsid, propietario, flags, tipo, nombres de filesystem/montaje/dispositivo y campos reservados. Los caracteres no se intercambian como enteros. La referencia i386 y el llamador PPC coinciden: `bsize=1024 iosize=4096 blocks=2023918 type=1 flags=5000 fsid=e000002:1 owner=0 name=ufs mount=/ from=/dev/disk0s2`. El volumen real de este entorno es UFS; no se presentó como HFS ni como un CD montado. Se prueban ruta válida, descriptor, ENOENT, EFAULT y EBADF.

Installer superó statfs y llegó a `getattrlist` 220. Se añadió la conversión de la attrlist de entrada y se consulta el kernel real con un buffer nativo privado. Se preservan sus errores, incluido ENOTSUP; se admite un resultado exitoso limitado a `ATTR_CMN_NAME` con conversión de attrreference. Cualquier otro resultado exitoso requiere una conversión tipada adicional y se detiene explícitamente antes de copiar datos de ABI i386 a PPC. No es una implementación general de atributos ni una tabla de volúmenes virtuales inventados.

### Señales PPC750

Se añadieron sigaction 46 (entrada kernel de 16 bytes, salida pública de 12), sigprocmask 48, sigpending 52, kill 37 y sigreturn 103, también a través de la llamada indirecta existente. El manejador nativo solo encola la señal e interrumpe TCG. La entrega se realiza desde el bucle del CPU a código PPC, pasando por el **sigtramp original de libSystem**, con ucontext PPC32 y mcontext de 456 bytes: GPR, CR, XER, LR, CTR, FPR y FPSCR, sin punteros i386 usados como manejadores PPC. Se protege la red zone y se restaura el estado, la máscara y el punto interrumpido en sigreturn. Las modificaciones válidas del contexto por el manejador se respetan.

Se manejan máscaras no bloqueables, disposición ignorada/default, deferencia, SA_SIGINFO, SA_RESTART, SA_RESETHAND, SA_NODEFER y SA_NOCLDSTOP. fork conserva acciones/máscara y limpia señales pendientes; exec resetea acciones capturadas y conserva ignoradas/máscara, además del estado IPC anterior. El cambio de versión del snapshot de exec evita confundir su formato con el de 0.08.

Límites explícitos: un CPU/hilo PPC750; no hay altstack, contexto vectorial, setcontext arbitrario ni conversión de fallos síncronos SEGV/BUS a señales PPC. Se rechazan las opciones que aún requieren esos mecanismos. El MSR restaurado debe coincidir con el del contexto entregado; no se permite cambiar privilegios. Darwin 6 i386 entrega un sigcontext nativo legado, no el ucontext PPC; la referencia i386 prueba ese mecanismo y las comprobaciones GPR/FPR editables corresponden al llamador PPC. Los campos de siginfo no disponibles para estas señales quedan a cero, como la ruta asíncrona de XNU 344; no se inventa un emisor.

### IOKit

RPC 2815 (`io_service_open`) valida descriptor y disposición COPY_SEND, traduce la capacidad de tarea actual a `mach_task_self()` i386 y llama al MIG original de IOKit i386. El objeto real recibido se registra como capacidad PPC con referencia send. RPC 2816 cierra realmente el user client; el IOServiceClose original libera después su derecho mediante la ruta de deallocate ya existente. Se conservan los errores del servicio real.

Tras superar open, splash solicitó RPC 2822 (`io_connect_method_scalarI_scalarO`). Se añadió conversión tipada de selector, contadores y arrays de hasta 16 enteros de 32 bits, y de la respuesta variable. El cliente real de IOPMrootDomain usa selector 0 para setAggressiveness y 1 para getAggressiveness, según `RootDomainUserClient.cpp` de XNU 344. No se simularon dispositivos ni se probaron métodos de sleep, shutdown o restart.

La primera prueba de open/close sí abrió y cerró el cliente real en i386/PPC, pero una aserción propia falló en ambos: suponía que un connect_type inusual debía rechazarse. El kernel original lo acepta. La prueba corregida registra ese resultado, cierra cualquier conexión que obtenga y usa un servicio/tipo de objeto incorrecto y un selector fuera de rango para los errores reales. Ese FAIL histórico se conserva, no se atribuye al puente.


## Continuación de la sesión: recuperación y correcciones

Se recuperó del FAT `res93.tgz`, que ya contenía la ejecución integrada terminada y no se había exportado al árbol del host. Se conserva como `logs/graphics-009/native-resume.tgz`; los datos extraídos están en `native-resume/graphics009-run3/`. En esa ejecución pasan statfs, getattrlist con los errores reales de UFS, IOServiceOpen/Close y scalar I/O, procesos/setsid, access, exec, IOKit, Objective-C i386, CoreFoundation i386, 23 utilidades y 11 pruebas de filesystem. La prueba de señales PPC falla realmente: el sigtramp original llama BSD **103**, mientras la implementación previa atendía 184. El número 184 es `nosys` en XNU 344. El resultado previo de la fixture propia usaba también 184 y no acreditaba el retorno del trampoline original.

Se corrigieron implementación y fixture propia a 103, comprobando `sources/xnu-344/bsd/sys/syscall.h`, `bsd/kern/syscalls.c` y `sources/Libc-262/sys/sigtramp.c`. En `native-run7/graphics009-run7/` pasan tanto la referencia i386 como la prueba PPC mediante libSystem original: máscara, pendiente, entrega de SIGUSR1/SIGUSR2, modificación/restauración de GPR/FPR, herencia mediante fork, reseteo de acciones capturadas y conservación de ignoradas/máscara mediante exec. Las fixtures Linux de señal propia y externa también pasan con 103; evidencia en `reports/graphics-009/signals-resumed-linux/`.

Installer pasó `statfs` y se detuvo después en `getfsstat` 18. Se incorporó enumeración real de montajes con conversión PPC32 de cada registro de 272 bytes. La prueba i386/PPC de run7 coincide en los cuatro montajes reales presentes: UFS raíz, devfs, cd9660 auxiliar y FAT de intercambio. Se comprueban consulta de cantidad, lista y EFAULT, además de statfs/fstatfs y sus errores. No se etiqueta como instalador montado la raíz Jaguar extraída. Después Installer alcanza `pathconf` 191.

WindowServer pasó sigaction y setlogin 50 (llamada real al kernel i386) y llegó a vm_map 3812 con máscara 0xfff y flags 0x2a000001. Se amplió el caso anónimo: la máscara de una página queda satisfecha por el mapeo de páginas; los bits altos son VM_FLAGS_ALIAS_MASK, una etiqueta de contabilidad de XNU. Se conserva el rechazo de objetos de memoria, offsets y alineaciones superiores no implementados. No hay mapeo de framebuffer implícito en esta ampliación.

Se añadieron pathconf/fpathconf 191/192 usando límites reales del filesystem. Para splash se incorporó HOST_SCHED_INFO, que en Jaguar es **flavor 3**, obtenido con host_info del kernel nativo y conversión de sus dos enteros. No debe confundirse con flavor 2 ni con tamaños de recursos. La referencia i386 informa `name_max=255`, `min_timeout=10`, `min_quantum=10`.

### Recuperación del entorno y fallos de preparación preservados

La VM anterior ya no estaba activa al retomar. Se arrancó el overlay existente con backing explícito en su ubicación Windows actual, sin rebase ni modificación del backing. El primer arranque hizo fsck automático y mostró correcciones en el overlay; la consola se conserva en `logs/graphics-009/resumed-boot.png`. Los directorios previos de /var/tmp no estaban disponibles. Se restauraron build y originales desde los archivos exportados existentes mediante `build/graphics009-recovery.iso`, CD auxiliar de solo lectura; no es un CD de instalación nuevo ni sustituye las imágenes originales. El modo monousuario evita depender del arranque del servidor de login nativo. Se restauró también el enlace a la ruta original de fuentes que usan los Makefiles archivados.

Los intentos run4/run5/run6 fallan por preparación (ruta ausente, finales CRLF de shell, enlaces del build); no son nuevos fallos de los programas originales. Run8 detectó una regresión propia: se validó erróneamente el campo copy de vm_map como offset adicional, bloqueando dyld. Run9 conserva el error de sintaxis de la primera corrección. Ambos quedan separados de run7 y de la validación posterior; no se ocultan ni se cuentan como progreso.

La comprobación SHA-256 de `reports/graphics-009/preservation-resumed.json` confirma que la ISO original Jaguar y `vm/darwin602.qcow2` conservan exactamente los hashes previos. No se ejecutaron instalaciones, commits ni push.

## Validación final y nuevos límites

La ejecución integrada `native-run10/graphics009-run10` completa con `runner_exit=0`. Todos los llamadores propios salen 0 sin timeout ni descendientes traducidos pendientes; los programas gráficos se clasifican por su bloqueo real, no por el exit 0 del padre de WindowServer.

| Prueba obligatoria | Resultado | Evidencia |
|---|---|---|
| Fixtures PPC anteriores | 11/11 PASS sobre el runtime Linux final | `reports/graphics-009/fixtures-linux-final-delivery.txt` |
| Utilidades originales | 23/23 PASS | `reports/graphics-009/native-final/utilities.txt` |
| Filesystem | 11/11 PASS, leftover=0 | `reports/graphics-009/native-final/filesystem.txt` |
| Objective-C original i386 | PASS, dispatch/super/estructura/free | `native-final/objc-native.stdout` |
| CoreFoundation original i386 | PASS, UTF-8/array/retain/release/time | `native-final/cf-native.stdout` |
| fork, setsid, access, execve | PASS; PID/argv/env/cwd/fd/CLOEXEC | `native-final/process-runtime.*`, `access-runtime.*`, `exec-runtime.*` |
| Señales PPC originales | PASS, GPR/FPR, máscaras, pendientes y fork/exec/sigreturn | `native-final/signals-runtime-jaguar.*`, con referencia i386 al lado |
| statfs/getfsstat | PASS y comparación exacta de registros impresos con i386 | `native-final/statfs-runtime-{native,jaguar}.*` |
| IOKit original | PASS, open/close, getAggressiveness, selector inválido y objeto incorrecto | `native-final/iokit-open-runtime-{native,jaguar}.*` y `iokit-runtime.*` |
| pathconf/host_info/thread_switch/puerto nulo | PASS, stdout idéntico i386/PPC | `native-scheduler-final/system-{native,jaguar}.*` |
| Serie de parches | PASS 0001..0007 sobre upstream 0.10.6 y fuentes reproducidas | `patch-verification-resumed.txt` |
| Preservación ISO y backing Darwin | PASS SHA-256 | `preservation-resumed.json` |

Las últimas modificaciones después de la suite integrada son dos rutas acotadas: trap -61 llama al thread_switch del kernel i386 para thread nulo y retorna su resultado; un envío RPC síncrono a puerto nulo/muerto devuelve MACH_SEND_INVALID_DEST sin fabricar una respuesta MIG. Se probaron específicamente en `native-run11` y `native-run12`, además de repetir los 11 fixtures Linux finales. No se afirma que toda la suite nativa se haya repetido sobre el binario run12.

La referencia i386 y el llamador PPC de run12 imprimen exactamente `PATHCONF name_max=255`, `HOST_SCHED_INFO kr=0 count=2 timeout=10 quantum=10`, `THREAD_SWITCH kr=0` y `MACH_NULL_DEST kr=268435459` (0x10000003). El test de puerto nulo usa mach_msg real en i386. No se creó ningún servidor WindowServer ficticio para alterar ese resultado.

Con el error correcto de envío, splash supera su RPC 29033 a destino nulo; después registra fork real y execve real replacement del Installer original (argc=1, envc=7). El hijo carga los componentes originales y termina en el mismo límite RPC 3226 de Installer directo. Splash sale 125, sin timeout ni descendientes vivos. **Esto acredita lanzamiento auténtico del programa, no una ventana.**

### Memoria e IPC que faltan

RPC 3825 corresponde a mach_make_memory_entry_64 en la definición MIG de Jaguar (`sources/xnu-344/osfmk/mach/vm_map.defs`). WindowServer solicita crear una entrada sobre su memoria con permiso 3 y tamaño 0x1000. Falta transportar esa entrada como capacidad real y permitir mapas compartidos, referencias, protecciones y liberación coherentes; copiar bytes a un buffer independiente rompería el alias y no resuelve este protocolo.

Installer usa mach_port_insert_member, RPC 3226, sobre un puerto receive ya miembro de otro set. XNU permite pertenencia múltiple (`osfmk/ipc/mach_port.c`, `ipc_pset.c`), mientras el modelo actual guarda un solo set por puerto. Resolverlo requiere ampliar la representación y su persistencia en exec, además de entrega/recepción real por conjuntos. Limitarse a devolver éxito perdería la semántica necesaria de comunicación.

Las trazas efectivamente solicitan bootstrap `WindowServer`, `lookup daemon v2` y `com.apple.coreservicesd`. Esto demuestra consultas, no que todos esos servicios sean requisitos obligatorios: los programas toleran algunos errores y siguen. El namespace actual sigue siendo local por proceso y carece de un servicio WindowServer registrado y accesible entre procesos originales. La integración gráfica requiere resolver esa comunicación junto con los objetos de memoria; aún no se alcanzó apertura/mapa del framebuffer por WindowServer.

No se sustituyeron WindowServer, Quartz, AppKit, Foundation ni Installer. La prueba Quartz fuera de pantalla preservada de run3 no se cuenta como salida gráfica ni como interfaz funcional.

## Evidencias y cómo retomar

- [Resultados estructurados](../reports/graphics-009/results.json), [manifiesto SHA-256](../reports/graphics-009/evidence-manifest.json) y [consola final](../reports/graphics-009/final-console.png).
- Suite integrada en `logs/graphics-009/native-run10.tgz`; seguimiento del planificador/puerto nulo y splash en `native-run12.tgz`. Los intentos anteriores permanecen intactos.
- Runtime nativo más reciente: `/var/tmp/graphics009-run12/qemu-ppc`, con copia operativa en `/var/tmp/graphics009-run2/build/ppc-darwin-user/qemu-ppc`; sus hashes constan en el manifiesto. El binario y los originales Apple permanecen en artefactos locales, no en los informes versionables.
- El parche 0007 y `graphics-009-manifest.json` contienen las fuentes finales. `REMAKLAR_CHECKPOINT=0.09-graphics sh scripts/checkout-qemu.sh` aplica la serie sin crear commits propios.
- `python tools/prepare_graphics_009_payload.py <archivo-nuevo.tgz>` empaqueta fuentes/pruebas y entradas locales. Extraer en el invitado y ejecutar `sh graphics009-followup/run.sh <payload> <salida-nueva> [fuentes-existentes] [build-existente]`. La receta reutiliza el build, conserva el ejecutor resultante en la salida y se niega a reemplazar un directorio de resultados. El build archivado contiene enlaces a `/var/tmp/remaklar/experiments/qemu-0.10.6`; tras recuperación se restauró ese enlace hacia `/var/tmp/graphics009-run2/source`.
- El FAT queda desmontado después de cada exportación. La VM queda en shell monousuario para continuar. No arrancar rc.cdrom ni ofrecer discos destino al instalador.
- No se hicieron commits ni push. La siguiente tarea concreta es el puente de mach_make_memory_entry_64 o la pertenencia múltiple a conjuntos de puertos, con pruebas de memoria/IPC auténticas antes de reintentar la interfaz.
