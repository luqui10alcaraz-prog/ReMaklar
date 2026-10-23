# Ejecutor experimental ReMaklar 0.01

El árbol QEMU se mantiene en un repositorio Git independiente: `qemu-0.10.6`, rama `remaklar/0.01`. Base upstream: tag `v0.10.6`, commit `9eab386edbf8cf002a731f8204a156f243a47a57`.

Los cambios al runtime, loader y adaptador host residen dentro de ese repositorio. Las herramientas propias de inventario, generación de fixtures y comparación están en `../tools`, `../tests` y `../scripts`. Los binarios originales extraídos no deben versionarse.

El target conserva CPU PPC, helpers, softfloat, runtime de bloques, TCG i386, cargador Mach-O y soporte mmap de QEMU. Para Linux i386 usa un main de bootstrap y definiciones wire Mach-O mínimas; para host Darwin conserva el main y las integraciones históricas. La rama nativa Darwin aún requiere su propia compilación y validación.

No se implementan Linux syscalls para el invitado: el bootstrap reconoce números y retorno de Darwin. Su cobertura inicial es exit/write, con un puente de exit explícito en el modo de prueba main-only. El modo main-only carga el archivo original y aplica un slide en memoria; no ejecuta dyld ni inicializadores y no demuestra arranque completo del programa.

Consultar `../docs/remaklar-0.01.md` para comandos, resultados y límites. Los parches exportados permiten reproducir el árbol sin tratar toda la copia de QEMU como código propio.
