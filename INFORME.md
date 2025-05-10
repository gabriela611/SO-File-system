# 📚 Informe Técnico - Sistema de Archivos Versionado Copy-On-Write (COW)

## 🛠️ Arquitectura General

El sistema desarrollado implementa una biblioteca de manejo de archivos versionados basada en la técnica de **Copy-On-Write (COW)**. Cada modificación genera una nueva versión comprimida del archivo sin alterar las versiones anteriores.

**Estructuras clave:**
- **Inodo (`inodo`)**: Controla nombre, versiones, bloques (FAT) y la versión actual.
- **Versiones**: Conjunto de bloques con offsets que representan cada snapshot del archivo.
- **Bloques**: Almacenan el contenido de cada versión en fragmentos de hasta 4KB.

**Operaciones principales:**
- `create()`, `open()`, `write()`, `read()`, `close()`
- `listar_versiones()`, `mostrar_uso_memoria()`, `recolectar_bloques_huerfanos()`
