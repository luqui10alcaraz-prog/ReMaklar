# Registro inicial de compatibilidad

El registro [services-0.04.json](services-0.04.json) se genera desde los logs
de los 23 casos que pasan en Linux y Darwin. Relaciona cada syscall/trap o
RPC observado con su proveedor y los casos que lo ejercitan. Una aparición
durante startup no acredita todas las variantes de esa interfaz.

| Capa o servicio | Proveedor actual | Evidencia y límites |
| --- | --- | --- |
| echo, cat, dyld, libSystem, libmathCommon | Original PPC traducido por CPU/TCG de QEMU | Entrada original y salida exacta; no hay reemplazo nativo de estas bibliotecas |
| printf y buffering/flush de stdio | Código original de libSystem PPC | Echo, incluidos cadenas largas y vacíos; evidencia de comportamiento, fuente e imports, sin instrumentación de todas las entradas de función |
| getopt, fopen, fprintf, warn | Código original de libSystem PPC | Cat con `-n`, lectura y ENOENT; subset funcional, no prueba completa de cada API |
| exit, read, write, open, close | Puente BSD al host | Datos como bytes, descriptores de lectura virtuales y errores Darwin; solo open de lectura y salida estándar/escritura de diagnóstico probados |
| stat/fstat/lstat | Puente al host con estructuras PPC32 big-endian | fstat observado; el registro distingue las otras variantes no observadas en estos casos |
| Identidad de proceso/usuario | Puente BSD al host | Valores del proceso ejecutor, no identidad independiente de un kernel PPC |
| sysctl | Sustitución por modelo de proceso | Solo HW_NCPU=1 y HW_VECTORUNIT=0, coherentes con PPC750 virtual |
| load_shared_file | Sustitución limitada | Solo consulta de disponibilidad; usa mappings privados, no región compartida real |
| vm_allocate/map/protect/deallocate, map_fd | Puente a memoria virtual del host y páginas QEMU | Subset de objetos/flags usado por dyld/libSystem; vm_region consulta el mapa del ejecutor |
| Puertos y mensajes Mach | Emulación en el proceso | Namespace virtual y RPC síncrono; no se exportan handles Mach nativos como si fueran puertos PPC |
| host_info, prioridades, reloj | Modelo parcial de host | Respuestas y endpoints mínimos para inicializar libSystem; no implica implementar el servicio de reloj completo |
| thread self, thread_policy | Emulación de un hilo | Puntero de hilo y prioridad virtual; no hay planificación de múltiples hilos PPC |
| Faults SMC del host | Puente legacy Darwin 6 de 0.03 | Recupera stores MOV TCG conocidos en páginas originalmente escribibles; no implementa señales Unix PPC |

Los imports de un Mach-O son interfaces posibles, no una lista de funciones
demostradas. Los inventarios completos conservan esa distinción. Los casos de
cat validan read/write a través de syscall y el comportamiento de stdio de la
biblioteca original; no se asegura que todas las funciones listadas como
imports se hayan llamado en cada caso.

Fuentes candidatas para futura reconstrucción nativa:

- echo: Apple shell_cmds-34, commit `c33c5559b9fe27af67ee00c6edd435568bc180dd`,
  archivo echo/echo.c, licencia BSD del archivo.
- cat: Apple text_cmds-18, commit `fa6544e9637325d16daa89d7c11e55afcc65c970`,
  archivo cat/cat.c, licencia BSD de cuatro cláusulas del archivo.
- libSystem: agregar fuentes por subcomponente; Libc-262 ya está en el
  laboratorio. No equivale al código completo de libSystem.

Se verificaron los tags y archivos en los repositorios de Apple y las versiones
de los RPM del CD. No se recompilaron estas utilidades ni se demostró identidad
binaria fuente/producto. El selector de proveedores sigue siendo una arquitectura
prevista: este checkpoint no implementa cambio automático a bibliotecas x86.
