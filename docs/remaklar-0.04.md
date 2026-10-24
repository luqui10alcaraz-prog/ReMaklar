# ReMaklar 0.04: argumentos, stdio y lectura de archivos

Los `echo` y `cat` originales del CD Darwin 6.0.2 pasan 23 casos compartidos
en Linux i386 y dentro de Darwin 6 i386. Se conserva el ejecutor de 0.03,
commit QEMU `f80cd4a91e77dbc132eb0d974003851847b3cd39`: no fue necesario
añadir una llamada al sistema ni una excepción por nombre de programa.
Los binarios, dyld y bibliotecas originales permanecen intactos. No se
modificó XNU. La procedencia sigue siendo el CD Darwin, no un Jaguar retail
cotejado; no se amplía esa afirmación por el nombre del checkpoint.

## Resultados

| Grupo | Linux i386 | Darwin 6 i386 |
| --- | --- | --- |
| echo: argumentos y salida | 12/12 | 12/12 |
| cat: entrada estándar y archivos | 11/11 | 11/11 |
| Fixtures mínimas anteriores | 11/11 | 11/11 |
| true/false main-only de 0.01 | 2/2 | No corresponde al hito nativo |
| true/false completos y control sin dyld | 3/3 | true=0, false=1 |

Las 16 regresiones Linux y las once fixtures nativas se conservaron sin
modificar sus expectativas. Las entradas originales observadas son `0x1744`
para echo y `0x1ab0` para cat. Todos los casos exigen una única observación
de esa entrada, SYS_exit, carga de libSystem y libmathCommon y ausencia de
puente main-only, llamadas sin implementar o faults del host.

Echo cubre ausencia de argumentos, argumentos vacíos, vacíos intercalados,
espacios consecutivos, caracteres literales de shell, tabs, saltos de línea,
UTF-8 tratado como bytes, `-n`, 513 argumentos, un argumento de 32 KiB y cinco
de 8 KiB. Se compara stdout byte a byte, incluida la ausencia de newline.
El ejecutor recibe argv directamente mediante exec, sin expansión de shell.

Cat cubre stdin vacío y binario, archivos vacíos y de texto, nombres con
espacios, concatenación, un archivo de 131.328 bytes con NUL y valores 0–255,
stdin entre dos archivos, error ENOENT, continuación después de ese error y
`-n`. Los errores esperados terminan en 1 y contienen el diagnóstico original;
no se cuentan como fallos del ejecutor. El archivo largo fuerza múltiples
lecturas y escrituras. No se usó el cat del host para producir la salida.
Stdin está redirigido desde archivos de prueba; todavía no se acredita
comportamiento con pipes o FIFOs.

El primer probe Linux ya funcionó con el ejecutor de 0.03, tanto echo como
cat por stdin. No hubo nuevos errores de portabilidad que adaptar en estos
caminos. Los controles negativos ENOENT, EFAULT y EBADF sí se ejecutan y
quedan registrados; no equivalen a implementar todos los errores posibles.

## Repetir

Con los originales extraídos por `scripts/Prepare-PpcSamples.ps1`:

```sh
python3 tests/ppc/make_fixtures.py
python3 tests/ppc/make_utility_cases.py
perl tests/ppc/run_utilities.pl \
  "$PWD/build/qemu-linux32-0.03/ppc-darwin-user/qemu-ppc" \
  "$PWD/research/samples-local" "$PWD/build/utility-cases.tsv" \
  "$PWD/logs/utilities-linux-001"
```

Sustituir la ruta del ejecutor si se compiló en el directorio Linux por
defecto. Linux conserva el requisito de permisos para mapear direcciones
bajas del laboratorio; las ejecuciones registradas se hicieron como root
en WSL. No se cambia la configuración global para ocultar ese requisito.

La misma matriz TSV se ejecuta con el Perl 5 ya instalado en Darwin: no se
necesitan Python, JSON para Perl ni bibliotecas adicionales en el invitado.
Se usan archivos para stdin/stdout/stderr y fork/exec con timeout, evitando
que un pipe de diagnóstico lleno bloquee el proceso hijo.

Para Darwin, generar primero los vectores y luego ejecutar
`python tools/prepare_darwin_payload.py`. Copiar source.tgz a FAT solo
mientras esté desmontado en el invitado. Seguir el [arranque de 0.03](darwin6-native.md)
y, con raíz escribible y FAT montado:

```sh
cd /var/tmp
gnutar xzf /exchange/source.tgz
sh remaklar/scripts/darwin6-utilities.sh > /var/tmp/utility-run.log 2>&1 &
```

El wrapper primero repite las pruebas nativas de 0.03 y luego los 23 casos.
Exigir `UTILITIES_COMPLETE baseline=0 utilities=0`. Exporta `utils.tgz`,
los logs anteriores y MD5 de ambos programas, sincroniza y desmonta FAT.
Extraer `utils.tgz` en `logs/utilities-native-001` quitando el primer
componente de ruta (`tar --strip-components=1`). Copiar también TESTS.LOG,
MD5.LOG y RUN.MD5 como `logs/utilities-native-baseline-001.log`,
`logs/utilities-native-original-md5.log` y `logs/utilities-native-runner-md5.txt`.
RUN.MD5 se obtiene con `md5` del ejecutor nativo; es una comprobación adicional
de identidad con el build 019. Hacerlo antes de ejecutar
`python tools/export_utility_checkpoint.py`; ese exportador valida ambos
hosts, los hashes originales y las regresiones y publica solo informes.

## Evidencia y conservación

- [Informe y hashes por caso](../reports/remaklar-0.04.json).
- [Resultados Darwin](../reports/utilities/native-console.txt) y
  [Linux](../reports/utilities/linux-results.tsv).
- [Registro de servicios](../research/services-0.04.json) y
  [explicación de proveedores](../research/services.md).
- [Inventario echo](../research/inventory/bin_echo.json) y
  [cat](../research/inventory/bin_cat.json).

El ejecutor nativo tiene el mismo MD5 y SHA-256 que el build 019 de 0.03.
La copia `vm/darwin602-native-003-verified.qcow2` conserva su SHA-256 original.
Después de `halt` y CPU halted, qemu-img check no encontró errores. Se guarda
otra copia offline `vm/darwin602-utilities-004-verified.qcow2`. Las imágenes y
los originales Apple siguen fuera de Git. No se afirma un nuevo build del
runtime: 0.04 es una ampliación medida de cobertura con el mismo código.

## Alcance de compatibilidad

libSystem sigue siendo PPC y se traduce con TCG, incluidas sus funciones de
stdio y de lectura de archivos. Solo la frontera BSD/Mach usa proveedores del
ejecutor; no se sustituyeron printf, read ni el programa completo por versiones
especiales. Las pruebas verifican comportamientos y llamadas al sistema; no
son cobertura exhaustiva de cada función importada.

Quedan pendientes rutas relativas con cwd virtual, otros flags de open,
escritura de archivos, seek, señales generales, concurrencia y servicios Mach
reales. Write solo está probado aquí para stdout/stderr; todavía no se acredita
un modelo completo de escritura por descriptores virtuales. La consola sigue
siendo monousuario y el puente de señales conserva los límites de 0.03.
