import os  # Módulo para operaciones del sistema de archivos
import json  # Módulo para trabajar con datos en formato JSON
import zlib  # Módulo para compresión y descompresión de datos
import base64  # Módulo para codificación y decodificación en Base64
from datetime import datetime  # Módulo para trabajar con fechas y horas
from colorama import Fore, Style  # Módulo para agregar colores al texto en la terminal
import time  # Módulo para medir tiempos de ejecución
import concurrent.futures  # Módulo para ejecutar tareas en paralelo
import io  # Módulo para manejar flujos de datos en memoria
from tqdm import tqdm  # Módulo para mostrar barras de progreso
import mimetypes  # Módulo para detectar tipos MIME de archivos


"""
    Gestor de archivos versionados utilizando bloques de 4KB y compresión de datos.

    Permite crear, abrir, leer, escribir versiones de archivos, manejar el uso de memoria,
    y realizar operaciones de recolección de bloques huérfanos.

    Atributos:
        ruta_archivo (str): Ruta del archivo a gestionar.
        nombre_archivo (str): Nombre del archivo.
        directorio_base (str): Carpeta base para almacenar datos.
        directorio_archivos (str): Carpeta para archivos originales.
        directorio_versiones_base (str): Carpeta base para versiones de archivos.
        directorio_inodos (str): Carpeta para metadatos de archivos (inodos).
        directorio_logs (str): Carpeta para registros de cambios.
        inodo (dict): Estructura que guarda la información de versiones y bloques.
        current_version (int): Índice de la versión actual activa.
    """
class GestorArchivos:


    """
        Inicializa el gestor de archivos versionados.

        Args:
            ruta_archivo (str): Ruta del archivo que se va a gestionar.

        Crea la estructura base de carpetas y archivos relacionados,
        pero no crea el archivo físico hasta llamar a `create()`.
        """

    def __init__(self, ruta_archivo):
        # Inicializa el gestor de archivos con la ruta del archivo a gestionar.
        self.ruta_archivo = ruta_archivo  # Almacena la ruta completa del archivo.
        self.nombre_archivo = os.path.basename(ruta_archivo)  # Obtiene el nombre del archivo a partir de la ruta.
        self.directorio_base = "lavacamu_data"  # Define el directorio base donde se almacenarán los datos.
        self.directorio_archivos = os.path.join(self.directorio_base,
                                                "archivos")  # Carpeta para los archivos originales.
        self.directorio_versiones_base = os.path.join(self.directorio_base,
                                                      "versiones")  # Carpeta base para las versiones.
        self.directorio_inodos = os.path.join(self.directorio_base, "inodos")  # Carpeta para los metadatos (inodos).
        self.directorio_logs = os.path.join(self.directorio_base, "logs")  # Carpeta para los registros de cambios.

        # Define las rutas específicas para el archivo actual.
        self.inodo_path = os.path.join(self.directorio_inodos,
                                       f"{self.nombre_archivo}.json")  # Ruta del archivo de inodo.
        self.versiones_dir = os.path.join(self.directorio_versiones_base,
                                          self.nombre_archivo)  # Carpeta de versiones del archivo.
        self.log_path = os.path.join(self.directorio_logs, f"{self.nombre_archivo}.log")  # Ruta del archivo de log.

        self.BLOQUE_TAM_MAX = 4096  # Define el tamaño máximo de cada bloque (4KB).

        # Inicializa las variables internas del gestor.
        self.inodo = None  # Estructura que almacena la información de versiones y bloques.
        self.current_version = -1  # Índice de la versión actual activa.

    def _asegurar_estructura(self):
        # Crea las carpetas necesarias para operar si no existen.
        for d in [self.directorio_base, self.directorio_archivos,
                  self.directorio_versiones_base, self.directorio_inodos,
                  self.directorio_logs, self.versiones_dir]:
            os.makedirs(d, exist_ok=True)  # Crea cada carpeta si no existe.

    def _cargar_o_crear_inodo(self):
        # Carga la información del inodo desde disco o crea uno nuevo si no existe.
        if os.path.exists(self.inodo_path):  # Verifica si el archivo de inodo existe.
            with open(self.inodo_path, "r", encoding="utf-8") as f:
                self.inodo = json.load(f)  # Carga el contenido del inodo desde el archivo JSON.
        else:
            # Crea un inodo inicial vacío si no existe.
            self.inodo = {
                "nombre": self.nombre_archivo,  # Nombre del archivo.
                "primer_bloque": "",  # Referencia al primer bloque (vacío inicialmente).
                "fat": {},  # Tabla de asignación de bloques (vacía inicialmente).
                "versiones": [],  # Lista de versiones del archivo (vacía inicialmente).
                "current_version": -1  # Índice de la versión actual (ninguna activa).
            }
            self._guardar_inodo()  # Guarda el inodo recién creado en disco.

    def _guardar_inodo(self):
        # Guarda la estructura del inodo en un archivo JSON en disco.
        with open(self.inodo_path, "w", encoding="utf-8") as f:
            json.dump(self.inodo, f, indent=4)  # Escribe el inodo en formato JSON con indentación.

    """
        Registra un mensaje en el log de cambios del archivo.

        Args:
            mensaje (str): Texto a registrar en el archivo de logs.
        """

    def _registrar_log(self, mensaje):
        # Obtiene la fecha y hora actual en formato "YYYY-MM-DD HH:MM:SS".
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Abre el archivo de log en modo de adición (append) con codificación UTF-8.
        with open(self.log_path, "a", encoding="utf-8") as f:
            # Escribe el mensaje en el archivo de log, precedido por el timestamp.
            f.write(f"[{timestamp}] {mensaje}\n")

    def _ruta_bloque(self, nombre_bloque):
        # Construye y devuelve la ruta completa de un bloque específico dentro del directorio de versiones.
        return os.path.join(self.versiones_dir, nombre_bloque)

    """
       Crea un nuevo bloque JSON vacío para almacenar fragmentos de datos.

       El nombre del bloque es incremental ('block_XXXX.json') dentro de la carpeta de versiones.

       Returns:
           str: Nombre del nuevo bloque creado.
    """

    def _crear_nuevo_bloque(self):
        # Lista todos los archivos en el directorio de versiones que comienzan con "block_" y terminan con ".json".
        bloques_existentes = [f for f in os.listdir(self.versiones_dir) if
                              f.startswith("block_") and f.endswith(".json")]
        if not bloques_existentes:
            # Si no hay bloques existentes, asigna el nombre del primer bloque.
            nuevo_nombre = "block_0001.json"
        else:
            # Ordena los bloques existentes alfabéticamente.
            bloques_existentes.sort()
            # Obtiene el último bloque y extrae su número.
            ultimo = bloques_existentes[-1]
            numero = int(ultimo.replace("block_", "").replace(".json", ""))
            # Genera el nombre del nuevo bloque incrementando el número.
            nuevo_nombre = f"block_{numero + 1:04d}.json"

        # Crea la estructura inicial del bloque con su nombre, contenido vacío, y tamaño máximo.
        bloque = {"nombre": nuevo_nombre, "contenido": "", "usado": 0, "max": self.BLOQUE_TAM_MAX, "paginas": []}
        # Guarda el bloque en disco.
        self._guardar_bloque(bloque)
        # Registra el bloque en la tabla de asignación de bloques (FAT) del inodo.
        self.inodo["fat"][nuevo_nombre] = {"next": None, "usado": 0}
        # Guarda el inodo actualizado en disco.
        self._guardar_inodo()
        # Devuelve el nombre del nuevo bloque creado.
        return nuevo_nombre

    """
    Guarda en disco el contenido actualizado de un bloque.

    Args:
        bloque (dict): Estructura del bloque a persistir.
    """

    def _guardar_bloque(self, bloque):
        # Abre el archivo correspondiente al bloque en modo escritura con codificación UTF-8.
        with open(self._ruta_bloque(bloque["nombre"]), "w", encoding="utf-8") as f:
            # Escribe la estructura del bloque en formato JSON con indentación.
            json.dump(bloque, f, indent=4)

    """
        Carga desde disco el contenido de un bloque específico.

        Args:
            nombre (str): Nombre del bloque a cargar.

        Returns:
            dict or None: Estructura del bloque, o None si no existe.
        """

    def _obtener_bloque(self, nombre):
        # Obtiene la ruta completa del bloque a partir de su nombre.
        ruta = self._ruta_bloque(nombre)
        # Verifica si el archivo del bloque existe en el sistema de archivos.
        if os.path.exists(ruta):
            # Si existe, abre el archivo en modo lectura y carga su contenido como un diccionario JSON.
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        # Si el archivo no existe, retorna None.
        return None

    """
       Crea un archivo vacío en modo binario y prepara su estructura de versionado.

       Si el archivo ya existe, no lo sobrescribe.
    """

    def create(self):
        # Verifica si ya hay un archivo abierto en el gestor.
        if self.inodo is not None:
            # Si hay un archivo abierto, muestra un mensaje de advertencia y no permite crear uno nuevo.
            print("⚠️ Ya tienes un archivo abierto. Debes cerrarlo primero antes de crear uno nuevo.")
            return
        # Asegura que la estructura de carpetas necesarias esté creada.
        self._asegurar_estructura()
        # Verifica si el archivo físico no existe en el sistema de archivos.
        if not os.path.exists(self.ruta_archivo):
            # Si no existe, crea un archivo vacío en modo binario.
            with open(self.ruta_archivo, "wb") as f:
                pass
            # Muestra un mensaje indicando que el archivo fue creado exitosamente.
            print(f"✅ Archivo '{self.nombre_archivo}' creado exitosamente y preparado para versionado.")
            # Carga o crea el inodo asociado al archivo.
            self._cargar_o_crear_inodo()
            # Registra en el log que el archivo fue creado.
            self._registrar_log("Archivo creado")
        else:
            # Si el archivo ya existe, muestra un mensaje de advertencia.
            print(f"⚠️ El archivo '{self.nombre_archivo}' ya existe.")

    """
        Abre un archivo existente, cargando su información de versiones e inodo.

        Si el archivo no existe, sugiere crear uno nuevo.
    """

    def open(self):
        # Verifica si ya hay un archivo abierto en el gestor.
        if self.inodo is not None:
            # Si hay un archivo abierto, muestra un mensaje de advertencia y no permite abrir otro.
            print("⚠️ Ya tienes un archivo abierto. Cierra el actual antes de abrir otro.")
            return

        # Asegura que la estructura de carpetas necesarias esté creada.
        self._asegurar_estructura()

        # Verifica si el archivo físico existe en el sistema de archivos.
        if os.path.exists(self.ruta_archivo):
            # Carga o crea el inodo asociado al archivo.
            self._cargar_o_crear_inodo()

            # Si no se encuentran versiones en el inodo, crea una versión inicial.
            if not self.inodo["versiones"]:
                print("📦 No se encontraron versiones. Creando versión inicial (v0)...")
                self._crear_version_inicial()

            # Actualiza la versión actual activa en el gestor.
            self.current_version = self.inodo["current_version"]
            # Muestra un mensaje indicando que el archivo fue abierto exitosamente.
            print(f"✅ Archivo '{self.nombre_archivo}' abierto exitosamente.")
        else:
            # Si el archivo no existe, muestra un mensaje sugiriendo crearlo primero.
            print(f"❌ Archivo '{self.nombre_archivo}' no encontrado. Usa 'create()' primero.")

    def _crear_version_inicial(self):
        """Crea automáticamente la versión inicial (v0) a partir del archivo físico."""
        try:
            # Abre el archivo físico en modo binario y lee su contenido.
            with open(self.ruta_archivo, "rb") as f:
                contenido = f.read()

            # Si el archivo tiene contenido, lo escribe como una nueva versión.
            if contenido:
                self.write(contenido)
                # Muestra un mensaje indicando que la versión inicial fue creada correctamente.
                print("🎯 Versión inicial (v0) creada correctamente.")
            else:
                # Si el archivo está vacío, muestra un mensaje de advertencia.
                print("⚠️ El archivo estaba vacío. No se creó versión inicial.")
        except Exception as e:
            # Si ocurre un error, muestra un mensaje con la descripción del error.
            print(f"❌ Error creando versión inicial: {e}")

    """
        Lee y reconstruye el contenido de la última versión guardada del archivo.

        Recupera el contenido binario original a partir de los bloques almacenados.
        Muestra el tamaño del contenido reconstruido.

        Raises:
            Exception: Si ocurre algún error en la descompresión o reconstrucción.
        """

    def read(self, guardar_como_archivo=False):
        """
        Lee la versión actual del archivo:
        - Reconstruye el contenido descomprimido.
        - Si `guardar_como_archivo=True`, lo guarda como archivo físico recuperado.
        """
        if self.inodo is None:
            print("⚠️ No hay archivo abierto. Usa 'open()' o 'create()' primero.")
            return
        if self.current_version == -1:
            print("⚠️ No existen versiones aún para leer.")
            return

        version = self.inodo["versiones"][self.current_version]
        contenido_total = ""

        for bloque_info in version["bloques"]:
            bloque = self._obtener_bloque(bloque_info["bloque"])
            if bloque:
                inicio = bloque_info["offset_inicio"]
                fin = bloque_info["offset_fin"]
                contenido_total += bloque["contenido"][inicio:fin]

        try:
            contenido_comprimido = base64.b64decode(contenido_total.encode("utf-8"))
            contenido_base64 = zlib.decompress(contenido_comprimido)
            binario = base64.b64decode(contenido_base64)

            print(f"📖 Contenido reconstruido exitosamente (tamaño: {len(binario)} bytes).")

            # Detectar tipo de archivo (opcional)
            tipo_mime, _ = mimetypes.guess_type(self.nombre_archivo)
            if tipo_mime:
                categoria = tipo_mime.split("/")[0]
                if categoria == "image":
                    print("🖼️ Tipo detectado: Imagen")
                elif categoria == "audio":
                    print("🎵 Tipo detectado: Audio")
                elif categoria == "video":
                    print("🎬 Tipo detectado: Video")
                elif categoria == "application":
                    print("📄 Tipo detectado: Documento")
                else:
                    print(f"📁 Tipo detectado: {categoria}")
            else:
                print("📁 Tipo de archivo desconocido.")

            if guardar_como_archivo:
                # Crear archivo recuperado
                nombre_recuperado = f"recuperado_{self.nombre_archivo}"
                with open(nombre_recuperado, "wb") as f:
                    f.write(binario)
                print(f"✅ Archivo recuperado como '{nombre_recuperado}'.")

        except Exception as e:
            print(f"❌ Error leyendo la versión: {e}")

    """
        Escribe nuevos datos como una nueva versión del archivo.

        Fragmenta y comprime los datos usando zlib y base64, almacena en bloques de 4KB, 
        y registra una nueva versión.

        Args:
            data (str or bytes): Contenido a escribir.
            level (int, optional): Nivel de compresión (1 a 9). Default = 9.

        Raises:
            Exception: Si ocurre error en la escritura o fragmentación de bloques.
        """

    def write(self, data, level=9):
        """
        Guarda datos en una nueva versión:
        - Si `data` es un texto, lo guarda como texto.
        - Si `data` es una ruta válida a un archivo, lo guarda como binario.
        - Fragmenta y acomoda en bloques de máximo 4096 bytes reales.
        """
        inicio = time.time()

        if self.inodo is None:
            print("⚠️ No hay archivo abierto. Usa 'open()' o 'create()' primero.")
            return

        if not isinstance(data, (str, bytes)):
            print("❌ El contenido debe ser tipo string, bytes, o ruta de archivo válida.")
            return

        # Auto detectar si es ruta de archivo
        if isinstance(data, str) and os.path.exists(data):
            print(f"📂 Detectado archivo: {data}")
            with open(data, "rb") as f:
                contenido = f.read()
        elif isinstance(data, str):
            contenido = data.encode("utf-8")
        else:
            contenido = data

        if len(contenido) == 0:
            print("⚠️ No se puede guardar contenido vacío.")
            return

        # Codificar y comprimir
        buffer = io.BytesIO()
        base64_bytes = base64.b64encode(contenido)
        compressed_bytes = zlib.compress(base64_bytes, level=level)
        buffer.write(base64.b64encode(compressed_bytes))
        buffer.seek(0)
        contenido_final = buffer.read().decode('utf-8')

        longitud_total = len(contenido_final)
        offset_inicio = 0

        bloques_existentes = {
            nombre: self._obtener_bloque(nombre)
            for nombre in os.listdir(self.versiones_dir)
            if nombre.startswith("block_")
        }
        bloques_utilizados = []
        acciones = []

        def guardar_fragmento_en_bloque(bloque, fragmento, offset_bloque, bytes_a_escribir):
            bloque["contenido"] += fragmento
            bloque["usado"] += bytes_a_escribir
            bloque["paginas"].append({
                "version_id": f"v{len(self.inodo['versiones'])}",
                "offset": offset_bloque,
                "longitud": bytes_a_escribir
            })
            self._guardar_bloque(bloque)

        with concurrent.futures.ThreadPoolExecutor() as executor, tqdm(
                total=longitud_total, desc="Guardando bloques", unit="B", unit_scale=True
        ) as barra:
            while offset_inicio < longitud_total:
                bloque_usado = next(
                    (b for b in bloques_existentes.values() if b and (b["max"] - b["usado"] > 0)),
                    None
                )

                if not bloque_usado:
                    nuevo_nombre = self._crear_nuevo_bloque()
                    bloque_usado = self._obtener_bloque(nuevo_nombre)
                    bloques_existentes[nuevo_nombre] = bloque_usado

                espacio_disponible = bloque_usado["max"] - bloque_usado["usado"]
                bytes_restantes = longitud_total - offset_inicio

                # Escribir lo que cabe en este bloque
                bytes_a_escribir = min(espacio_disponible, bytes_restantes)
                fragmento = contenido_final[offset_inicio: offset_inicio + bytes_a_escribir]
                offset_bloque = bloque_usado["usado"]

                acciones.append(executor.submit(
                    guardar_fragmento_en_bloque,
                    bloque_usado,
                    fragmento,
                    offset_bloque,
                    bytes_a_escribir
                ))

                bloques_utilizados.append({
                    "bloque": bloque_usado["nombre"],
                    "offset_inicio": offset_bloque,
                    "offset_fin": offset_bloque + bytes_a_escribir
                })

                barra.update(bytes_a_escribir)
                offset_inicio += bytes_a_escribir

            concurrent.futures.wait(acciones)

        version_metadata = {
            "id": f"v{len(self.inodo['versiones'])}",
            "bloques": bloques_utilizados,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        self.inodo["versiones"].append(version_metadata)
        self._actualizar_current_version(len(self.inodo["versiones"]) - 1)
        self._guardar_inodo()
        self._registrar_log(f"Nueva versión creada: {version_metadata['id']}")

        fin = time.time()
        print("\n🛠️ Nueva versión", version_metadata['id'], "guardada exitosamente.")
        print(f"⏱️ Tiempo total: {fin - inicio:.2f} segundos.")

    """
        Actualiza el índice de la versión actual en el inodo.

        Args:
            new_index (int): Índice de la nueva versión actual activa.
        """
    def _actualizar_current_version(self, new_index):
        self.inodo["current_version"] = new_index
        self.current_version = new_index
        self._guardar_inodo()

    """
        Cierra el archivo actual, limpiando las referencias en memoria.

        Registra el evento de cierre en el log de cambios.
        """
    def close(self):
        if self.ruta_archivo is None:
            print("⚠️ No hay archivo abierto actualmente.")
            return
        if self.ruta_archivo:
            print(f"🔒 Archivo '{self.nombre_archivo}' cerrado correctamente.")
            self._registrar_log("Archivo cerrado")
        self.ruta_archivo = None
        self.nombre_archivo = None
        self.inodo = None
        self.current_version = -1

    """
        Lista todas las versiones disponibles del archivo, mostrando:
        - ID de la versión
        - Tamaño en bytes
        - Número de bloques utilizados
        - Timestamp de creación

        Si no hay versiones, muestra advertencia.
        """

    def listar_versiones(self):
        """
        Lista todas las versiones disponibles del archivo, mostrando tamaño en disco y tamaño real estimado.
        """
        if not self.inodo or not self.inodo["versiones"]:
            print("⚠️ No hay versiones registradas.")
            return

        print(f"📜 Versiones disponibles para '{self.nombre_archivo}':\n")

        for i, version in enumerate(self.inodo["versiones"]):
            vid = version.get("id", "Sin ID")
            timestamp = version.get("timestamp", "Sin fecha")
            bloques = len(version.get("bloques", []))
            tamano_en_disco = sum(b["offset_fin"] - b["offset_inicio"] for b in version.get("bloques", []))

            # Reconstruir contenido para estimar tamaño real
            contenido_total = ""
            for bloque_info in version["bloques"]:
                bloque = self._obtener_bloque(bloque_info["bloque"])
                if bloque:
                    inicio = bloque_info["offset_inicio"]
                    fin = bloque_info["offset_fin"]
                    contenido_total += bloque["contenido"][inicio:fin]

            tamano_real = None

            if i == 0:
                # v0: es archivo puro, no codificado
                tamano_real = tamano_en_disco
            else:
                try:
                    contenido_comprimido = base64.b64decode(contenido_total.encode("utf-8"))
                    contenido_base64 = zlib.decompress(contenido_comprimido)
                    binario = base64.b64decode(contenido_base64)
                    tamano_real = len(binario)
                except Exception:
                    tamano_real = "❓"

            print(
                f"🔹 {i + 1}. ID: {vid} | Tamaño en disco: {tamano_en_disco} bytes | Estimado real: {tamano_real} bytes | Bloques: {bloques} | Creado: {timestamp}")

        print(f"\n🔄 Versión actual activa: {self.current_version}")

    """
        Muestra estadísticas de uso de memoria:
        - Bytes usados vs. capacidad máxima de cada bloque.
        - Porcentaje de ocupación por bloque.
        - Espacio total usado y libre.

        Útil para diagnosticar eficiencia de almacenamiento.
        """
    def mostrar_uso_memoria(self):
        """
        Muestra estadísticas de uso de memoria en los bloques del archivo y detecta inconsistencias.
        """
        if not self.inodo or not self.inodo["fat"]:
            print("⚠️ No hay bloques asignados.")
            return

        total_usado = 0
        total_max = 0

        print(f"\n\U0001F4CA Uso de memoria para el archivo '{self.nombre_archivo}':\n")

        for bloque_nombre in self.inodo["fat"]:
            bloque = self._obtener_bloque(bloque_nombre)
            if bloque:
                usados = len(bloque["contenido"])
                if usados > bloque["max"]:
                    print(f"⚠️  Inconsistencia detectada en {bloque_nombre}: {usados} > {bloque['max']} bytes.")
                    # Ajustar temporalmente
                    bloque["usado"] = bloque["max"]
                else:
                    bloque["usado"] = usados

                porcentaje = (bloque["usado"] / bloque["max"]) * 100 if bloque["max"] else 0
                total_usado += bloque["usado"]
                total_max += bloque["max"]

                print(f"🔹 {bloque_nombre}: {bloque['usado']} / {bloque['max']} bytes usados ({porcentaje:.2f}%)")

        print(f"\n\U0001F4E6 Total de bloques: {len(self.inodo['fat'])}")
        print(f"✅ Espacio total usado: {total_usado} bytes")
        print(f"\U0001F4A1 Espacio libre disponible: {total_max - total_usado} bytes\n")

    """
        Identifica y elimina bloques huérfanos no asociados a ninguna versión.

        Libera espacio de almacenamiento eliminando archivos de bloques
        no referenciados en las versiones activas.
        """
    def recolectar_bloques_huerfanos(self):
        """
        Elimina los bloques que no están referenciados por ninguna versión activa.
        """
        if not self.inodo:
            print("⚠️ No hay información de inodo cargada.")
            return

        print(f"🧹 Iniciando recolección de bloques huérfanos para '{self.nombre_archivo}'...")

        bloques_usados = set()
        for version in self.inodo["versiones"]:
            for b in version["bloques"]:
                bloques_usados.add(b["bloque"])

        bloques_en_disco = [f for f in os.listdir(self.versiones_dir) if f.startswith("block_")]

        eliminados = 0

        for bloque in bloques_en_disco:
            if bloque not in bloques_usados:
                try:
                    os.remove(self._ruta_bloque(bloque))
                    if bloque in self.inodo["fat"]:
                        del self.inodo["fat"][bloque]
                    eliminados += 1
                    print(f"🗑️ Eliminado bloque huérfano: {bloque}")
                except Exception as e:
                    print(f"❌ Error al eliminar bloque {bloque}: {e}")

        if eliminados > 0:
            self._guardar_inodo()
            self._registrar_log(f"Se eliminaron {eliminados} bloques huérfanos")
            print(f"✅ {eliminados} bloques huérfanos eliminados exitosamente.")
        else:
            print("✅ No se encontraron bloques huérfanos.")

    def rollback_backward(self):
        """
        Retrocede a la versión anterior disponible si es posible.
        """
        if not self.inodo or not self.inodo["versiones"]:
            print("⚠️ No hay versiones disponibles.")
            return

        if self.current_version > 0:
            self.current_version -= 1
            self.inodo["current_version"] = self.current_version
            self._guardar_inodo()
            print(f"⬅️ Retrocediste a la versión {self.inodo['versiones'][self.current_version]['id']}.")
        else:
            print("⚠️ Ya estás en la primera versión, no puedes retroceder más.")

    def rollback_forward(self):
        """
        Avanza a la siguiente versión disponible si existe.
        """
        if not self.inodo or not self.inodo["versiones"]:
            print("⚠️ No hay versiones disponibles.")
            return

        if self.current_version < len(self.inodo["versiones"]) - 1:
            self.current_version += 1
            self.inodo["current_version"] = self.current_version
            self._guardar_inodo()
            print(f"➡️ Avanzaste a la versión {self.inodo['versiones'][self.current_version]['id']}.")
        else:
            print("⚠️ Ya estás en la última versión, no puedes avanzar más.")

    def cambiar_a_version(self, version_id):
        """
        Cambia directamente a una versión específica por su ID (ej: 'v2', 'v5').
        """
        if not self.inodo or not self.inodo["versiones"]:
            print("⚠️ No hay versiones disponibles.")
            return

        encontrado = False
        for idx, version in enumerate(self.inodo["versiones"]):
            if version["id"] == version_id:
                self.current_version = idx
                self.inodo["current_version"] = idx
                self._guardar_inodo()
                print(f"🔄 Cambiaste a la versión {version_id}.")
                encontrado = True
                break

        if not encontrado:
            print(f"❌ No se encontró la versión {version_id}.")

    def reparar_inconsistencias(self):
        """Repara bloques cuyo 'usado' supera el tamaño máximo permitido."""
        if not self.inodo or not self.inodo["fat"]:
            print("⚠️ No hay bloques registrados para reparar.")
            return

        bloques_corregidos = 0

        for bloque_nombre in self.inodo["fat"]:
            bloque = self._obtener_bloque(bloque_nombre)
            if bloque:
                contenido_real = len(bloque["contenido"])
                if contenido_real > bloque["max"]:
                    print(f"⚙️ Reparando bloque {bloque_nombre}: {contenido_real} bytes -> {bloque['max']} bytes.")
                    bloque["contenido"] = bloque["contenido"][:bloque["max"]]  # Truncar al tamaño correcto
                    bloque["usado"] = bloque["max"]
                    self._guardar_bloque(bloque)
                    bloques_corregidos += 1
                elif bloque["usado"] != contenido_real:
                    print(f"🔧 Corrigiendo contador 'usado' en {bloque_nombre}: {bloque['usado']} -> {contenido_real}")
                    bloque["usado"] = contenido_real
                    self._guardar_bloque(bloque)
                    bloques_corregidos += 1

        if bloques_corregidos > 0:
            print(f"✅ Se repararon {bloques_corregidos} bloques inconsistentes.")
        else:
            print("✅ No se detectaron inconsistencias.")

        self._guardar_inodo()

    def optimizar_espacio(self):
        """
        🧹 Modo de optimización: reacomoda y compacta los bloques para mejorar el uso de espacio.
        Agrupa fragmentos dispersos en nuevos bloques llenos hasta 4KB.
        """
        if not self.inodo or not self.inodo["fat"]:
            print("⚠️ No hay bloques para optimizar.")
            return

        print("\n🛠️ Iniciando proceso de optimización de bloques...")
        bloques_actuales = [self._obtener_bloque(b) for b in self.inodo["fat"]]
        bloques_actuales = [b for b in bloques_actuales if b]

        # Crear buffer general de todos los datos existentes
        buffer_total = ""
        paginas_originales = []

        for bloque in bloques_actuales:
            contenido = bloque["contenido"]
            for pagina in bloque["paginas"]:
                offset = pagina["offset"]
                longitud = pagina["longitud"]
                data = contenido[offset:offset + longitud]
                buffer_total += data
                paginas_originales.append((pagina["version_id"], len(data)))

        # Limpiar todos los bloques antiguos
        for bloque in bloques_actuales:
            try:
                os.remove(self._ruta_bloque(bloque["nombre"]))
            except:
                pass
        self.inodo["fat"] = {}

        # Reinsertar datos compactados
        offset_total = 0
        nuevos_bloques = {}

        while offset_total < len(buffer_total):
            nuevo_nombre = self._crear_nuevo_bloque()
            bloque = self._obtener_bloque(nuevo_nombre)
            nuevos_bloques[nuevo_nombre] = bloque

            espacio_disponible = bloque["max"] - bloque["usado"]
            fragmento = buffer_total[offset_total:offset_total + espacio_disponible]

            bloque["contenido"] += fragmento
            bloque["usado"] += len(fragmento)
            self._guardar_bloque(bloque)
            offset_total += len(fragmento)

        # Ahora reconstruimos las referencias de las versiones
        nuevas_versiones = {}
        nuevo_offset_global = 0

        for version in self.inodo["versiones"]:
            nueva_bloques = []
            for pagina in version["bloques"]:
                longitud_pagina = pagina["offset_fin"] - pagina["offset_inicio"]
                # Reasignar a los nuevos bloques
                for nombre_bloque, bloque in nuevos_bloques.items():
                    if bloque["usado"] >= longitud_pagina:
                        nueva_bloques.append({
                            "bloque": nombre_bloque,
                            "offset_inicio": 0,
                            "offset_fin": longitud_pagina
                        })
                        bloque["usado"] -= longitud_pagina
                        break
            nuevas_versiones[version["id"]] = nueva_bloques

        for version in self.inodo["versiones"]:
            if version["id"] in nuevas_versiones:
                version["bloques"] = nuevas_versiones[version["id"]]

        self._guardar_inodo()
        self._registrar_log("Optimización de bloques ejecutada.")

        print("✅ Optimización de bloques completada con éxito.")

    def optimizar_bloques(self):
        """Optimiza la distribución de los bloques: compacta y elimina huecos."""
        if not self.inodo or not self.inodo["fat"]:
            print("⚠️ No hay bloques para optimizar.")
            return

        print("🧹 Iniciando optimización de bloques...")

        # Recolectamos todos los fragmentos usados de todas las versiones
        datos_totales = ""
        for version in self.inodo["versiones"]:
            for bloque_info in version["bloques"]:
                bloque = self._obtener_bloque(bloque_info["bloque"])
                if bloque:
                    datos_totales += bloque["contenido"][bloque_info["offset_inicio"]:bloque_info["offset_fin"]]

        # Borramos todos los bloques antiguos
        bloques_en_disco = [f for f in os.listdir(self.versiones_dir) if f.startswith("block_")]
        for bloque in bloques_en_disco:
            os.remove(self._ruta_bloque(bloque))
        self.inodo["fat"] = {}

        # Volvemos a crear los bloques con los datos combinados
        longitud_total = len(datos_totales)
        offset_inicio = 0
        bloques_utilizados = []

        while offset_inicio < longitud_total:
            nuevo_nombre = self._crear_nuevo_bloque()
            bloque_usado = self._obtener_bloque(nuevo_nombre)
            espacio_disponible = bloque_usado["max"]
            bytes_a_escribir = min(espacio_disponible, longitud_total - offset_inicio)
            fragmento = datos_totales[offset_inicio: offset_inicio + bytes_a_escribir]
            bloque_usado["contenido"] = fragmento
            bloque_usado["usado"] = len(fragmento)
            self._guardar_bloque(bloque_usado)

            bloques_utilizados.append({
                "bloque": bloque_usado["nombre"],
                "offset_inicio": 0,
                "offset_fin": len(fragmento)
            })

            offset_inicio += bytes_a_escribir

        # Actualizamos la versión actual
        nueva_version = {
            "id": f"v{len(self.inodo['versiones'])}_opt",
            "bloques": bloques_utilizados,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        self.inodo["versiones"].append(nueva_version)
        self._actualizar_current_version(len(self.inodo["versiones"]) - 1)
        self._guardar_inodo()

        print(f"✅ Optimización completada. Nueva versión '{nueva_version['id']}' creada.")

