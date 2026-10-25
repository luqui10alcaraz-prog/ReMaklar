# ReMaklar 0.07 — primer resultado nativo i386

Fecha: 25 de octubre de 2026. Continuación de la sesión interrumpida; alcance de esta continuación: ejecutar únicamente Objective-C y CoreFoundation y conservar su evidencia.

**Resultado: ambas pruebas compilaron y se ejecutaron directamente en Darwin i386 con bibliotecas originales de Apple, sin traducción PPC.** Es una comprobación acotada de runtime y APIs; no acredita compatibilidad completa de los frameworks ni un entorno gráfico.

| Prueba | Estado | Evidencia |
|---|---|---|
| Intento anterior, `native007-run2` | BLOCKED, compilación | Faltaba `mach-o/dyld.h`; no se habían ejecutado los tests. Sus logs se conservaron. |
| Objective-C, `native007-run3` | **PASS**, salida 0 | Clase propia, creación de instancia, dispatch, método que devuelve 42 mediante `super`, retorno de estructura de cinco enteros y liberación del objeto. |
| CoreFoundation, `native007-run3` | **PASS**, salida 0 | CFString UTF-8, cadena vacía y no ASCII, longitud y recuperación, CFArray, CFRetain/CFRelease, elemento retenido por array, rechazo de buffer insuficiente, CFAbsoluteTime y reloj Mach. |

## Entorno y demostración de arquitectura

La VM seguía activa, PID 8709, en consola monousuario. Se reutilizó `vm/darwin602-native-007-overlay-02.qcow2` y `build/native-007-exchange.img`; no se crearon imágenes ni se reconstruyó 0.06 en esta continuación. La VM permanece activa y el volumen de intercambio terminó desmontado.

Darwin 6.0, kernel `RELEASE_I386` del 21/10/2002; GCC2 Apple gcc-7 basado en GCC 2.95.2. Compilación con `gcc2 -no-cpp-precomp -arch i386`. La máquina PC x86 está emulada por QEMU 8.2.2 con TCG: «nativo» describe el ISA/ABI i386 del huésped, no una prueba sobre hardware físico.

Los ejecutables recuperados tienen cabecera Mach-O little-endian, CPU 7, tipo EXECUTE. `file` y `otool -arch i386 -hv -L` del huésped confirman su formato y dependencias. Las propias pruebas inspeccionaron las cabeceras **cargadas en memoria**, y exigieron `cpu=7` y `magic=feedface` en todas las imágenes:

- Objective-C: ejecutable, libobjc, CoreFoundation, libSystem y libmathCommon.
- CoreFoundation: ejecutable, CoreFoundation, libSystem y libmathCommon.
- Ambas localizaron la cabecera de dyld en memoria: `DYLD_MEMORY address=8fe00000 cpu=7 filetype=7`.

Los comandos fueron `./objc` y `./cf`; el runner usa Perl exclusivamente para timeout y `exec`. Los logs incluyen inicialmente la carga de Perl y después la del ejecutable que lo reemplaza. No se invocó `qemu-ppc`. Las pruebas llegaron a `main` mediante CRT/dyld normales, sin saltos a una entrada de prueba ni sustitución del runtime.

Versiones instaladas: **CoreFoundation 262.0.0, libobjc 218.0.0 y libSystem 60.0.0**. Los MD5 calculados dentro del huésped para esas bibliotecas y dyld coinciden con los originales conservados en `research/samples-local/`; [originals.json](../reports/native-007/originals.json) registra también sus SHA-256. libobjc declara una dependencia de CF con current_version 263 y compatibility_version 150; la CF realmente instalada y ejecutada es 262. Este resultado no demuestra equivalencia con CF 263 retail.

## Corrección y evidencia conservada

Se corrigió solo la instrumentación de pruebas: `images.h` declara el header Mach-O32 y las tres funciones de consulta de imágenes que faltan en el SDK instalado. Se cotejaron con `sources/cctools-435/include/mach-o/{loader,dyld}.h`; no se añadió implementación de loader o runtime. El test comprueba tamaños de 32 bits. Las declaraciones CF se cotejaron con los headers históricos recuperados del huésped (`build/native007-headers/`); su CFBase remite a MacTypes de CarbonCore, ausente del conjunto de desarrollo. No se reemplazó ninguna biblioteca.

Se añadió el modo `--runtimes-only` al runner existente. Las pruebas C/dylib de la sesión anterior no se repitieron ni se dan por aprobadas. El informe y los artefactos 0.06 existentes permanecen conservados.

Evidencia publicada: [resultados y hashes](../reports/native-007/results.json), [sesión con comandos de compilación](../reports/native-007/session.txt), [bibliotecas instaladas](../reports/native-007/installed-images.txt), [stdout Objective-C](../reports/native-007/objc.stdout), [imágenes Objective-C en memoria](../reports/native-007/objc.stderr), [stdout CF](../reports/native-007/cf.stdout) e [imágenes CF en memoria](../reports/native-007/cf.stderr). También se guardaron estados, comandos directos, builds y salida de otool por caso.

Los ejecutables propios y la exportación original permanecen en `logs/native-007-session/export3/native007-run3/` y `logs/native-007-session/result3.tgz`, fuera de Git. SHA-256:

| Ejecutable | SHA-256 |
|---|---|
| `objc` | `605ed20a3a271e9b09aa85f6703f1d2d6eb9e12ebb15f3c9bf1ea99906763869` |
| `cf` | `d2d53e406c129072863ade75df8037d3462487e7e5c25bc1b9a4427cab41631d` |

Reproducción dentro del huésped, usando un directorio de salida nuevo:

```sh
sh native007c/scripts/darwin6-native-007.sh \
  /var/tmp/native007c /var/tmp/native007-run-next --runtimes-only
```

Verificación de la evidencia exportada, sin volver a ejecutar pruebas y con destino nuevo:

```sh
python3 tools/verify_native_007.py \
  logs/native-007-session/export3/native007-run3 reports/native-007-next
```

El verificador se ejecutó correctamente: exige stdout exacto, estado 0, CPU i386 del binario y de cada imagen requerida, dyld i386 en memoria y comando directo. Se comprobó además que las fuentes transferidas coinciden con las actuales. No quedan fallos de estas dos pruebas; quedan fuera de alcance C/dylib, runloops, concurrencia, compatibilidad CF 263 y entorno gráfico. El siguiente trabajo requiere revisión de este resultado; no se avanzó a otra etapa.
